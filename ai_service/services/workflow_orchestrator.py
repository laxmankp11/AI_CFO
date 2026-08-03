"""
Workflow Orchestrator - Executes compound execution plans step-by-step
with context propagation, error handling, and result aggregation.

Architecture:
    ExecutionPlan → Workflow Orchestrator → [Step1 → Step2 → Step3] → Aggregated Response

The Orchestrator iterates through steps in dependency order, passes context
(entity names, amounts, IDs) between steps, and handles failures gracefully.
"""

import json
import time
from google import genai
from services.agents.planning_agent import ExecutionPlan, WorkflowStep
from services.agents.expense_agent import ExpenseAgent
from services.agents.reporting_agent import ReportingAgent
from services.agents.advisory_agent import AdvisoryAgent
from services.scoring_service import ScoringService

# Enterprise Safety Components
from services.policy_engine import PolicyEngine
from services.rollback_manager import RollbackManager
from services.audit_engine import AuditEngine
from services.event_bus import event_bus, BusinessEvent


class StepResult:
    """Result of executing a single workflow step."""
    def __init__(self, step: WorkflowStep, status: str, data: dict = None, error: str = None):
        self.step = step
        self.status = status  # "completed", "failed", "skipped"
        self.data = data or {}
        self.error = error

    def to_dict(self) -> dict:
        return {
            "step_id": self.step.step_id,
            "agent_type": self.step.agent_type,
            "action": self.step.action,
            "description": self.step.description,
            "status": self.status,
            "data": self.data,
            "error": self.error
        }


class WorkflowOrchestrator:
    """
    Executes an ExecutionPlan step-by-step with:
    1. Dependency-ordered execution
    2. Context propagation between steps
    3. Error handling with graceful degradation
    4. Result aggregation into a unified compound response
    """

    def __init__(self, client: genai.Client):
        self.client = client
        self.expense_agent = ExpenseAgent(client)
        self.reporting_agent = ReportingAgent(client)
        self.advisory_agent = AdvisoryAgent(client)
        
        # Enterprise components
        self.policy_engine = PolicyEngine()
        self.rollback_manager = RollbackManager()
        self.audit_engine = AuditEngine()

    def execute(
        self,
        plan: ExecutionPlan,
        user_context_str: str,
        mock_active_coa: str,
        mock_active_vendors: str,
        mock_global_taxes: str,
        tenant_tax_str: str,
        db_path: str,
        tenant_id: str = "unknown",
        original_prompt: str = "",
        validator_corrections: list = None,
        audio_base64: str = None
    ) -> dict:
        """
        Execute a compound execution plan step-by-step with safety guards.
        
        Returns a unified compound response with all step results.
        """
        # Create initial audit log entry
        audit_record = self.audit_engine.create_record(
            tenant_id=tenant_id,
            original_prompt=original_prompt,
            detected_intent="compound",
            planner_output=plan.model_dump(),
            validator_corrections=validator_corrections or []
        )
        audit_id = audit_record["audit_id"]

        results: list[StepResult] = []
        completed_step_ids: set = set()
        step_context: dict = {}  # Accumulated context from completed steps
        rollback_info = None
        workflow_state = "Executing"
        start_time = time.time()
        llm_time_ms = 0

        # Sort steps by dependency order (topological sort)
        ordered_steps = self._topological_sort(plan.steps)

        print(f"\n{'='*70}")
        print(f"  WORKFLOW ORCHESTRATOR: Executing {len(ordered_steps)} steps")
        print(f"{'='*70}")

        for step in ordered_steps:
            # Check if all dependencies are satisfied
            unmet_deps = [dep for dep in step.depends_on if dep not in completed_step_ids]
            if unmet_deps:
                # Check if any dependency failed
                failed_deps = [dep for dep in unmet_deps 
                              if any(r.step.step_id == dep and r.status == "failed" for r in results)]
                if failed_deps:
                    result = StepResult(
                        step=step,
                        status="skipped",
                        error=f"Skipped because dependency step(s) {failed_deps} failed."
                    )
                    results.append(result)
                    print(f"  ⏭️  Step {step.step_id} ({step.action}): SKIPPED (dependency failed)")
                    continue

            print(f"\n  ▶️  Step {step.step_id}: {step.description}")
            print(f"     Agent: {step.agent_type} | Action: {step.action}")

            step_failed = False
            error_msg = ""
            try:
                step_start_time = time.time()
                step_result = self._execute_step(
                    step=step,
                    step_context=step_context,
                    user_context_str=user_context_str,
                    mock_active_coa=mock_active_coa,
                    mock_active_vendors=mock_active_vendors,
                    mock_global_taxes=mock_global_taxes,
                    tenant_tax_str=tenant_tax_str,
                    db_path=db_path,
                    tenant_id=tenant_id,
                    audio_base64=audio_base64
                )
                if step.agent_type in ("expense", "sales"):
                    llm_time_ms += int((time.time() - step_start_time) * 1000)
                
                results.append(step_result)
                
                if step_result.status in ("failed", "waiting_approval"):
                    error_msg = step_result.error or "Unknown failure"
                    is_critical = step.agent_type in ("expense", "sales", "master_data")
                    if is_critical or step_result.status == "waiting_approval":
                        step_failed = True
                    else:
                        print(f"     ⚠️ Non-critical failure in {step.action}. Treating as warning.")
                        step_result.status = "completed_with_warning"
                        completed_step_ids.add(step.step_id)
                else:
                    completed_step_ids.add(step.step_id)

                    if step_result.status == "completed" and step_result.data:
                        step_context[step.step_id] = {
                            "action": step.action,
                            "description": step.description,
                            "result_summary": step_result.data.get("summary", step.description),
                            "parameters": step.parameters
                        }
                        
                    event_bus.publish(BusinessEvent(
                        tenant_id=tenant_id,
                        event_type="WorkflowStepCompleted" if step_result.status == "completed" else "WorkflowStepWarning",
                        data=step_result.to_dict()
                    ))

                    status_icon = "✅" if step_result.status == "completed" else "⚠️"
                    print(f"     {status_icon} Result: {step_result.status}")

            except Exception as e:
                step_failed = True
                error_msg = str(e)
                result = StepResult(step=step, status="failed", error=error_msg)
                results.append(result)
                print(f"     ❌ FAILED: {error_msg}")
                event_bus.publish(BusinessEvent(
                    tenant_id=tenant_id,
                    event_type="WorkflowStepFailed",
                    data=result.to_dict()
                ))

            if step_failed:
                # Trigger Rollback/Compensation
                print(f"\n  ⚠️  Failure or Approval required. Triggering Rollback/Compensation strategy...")
                completed_results = [r for r in results if r.status == "completed"]
                rollback_res = self.rollback_manager.compensate(completed_results, step)
                rollback_status = "full" if rollback_res.rolled_back_step_ids else "none"
                
                self.audit_engine.update_rollback(
                    tenant_id=tenant_id,
                    audit_id=audit_id,
                    status=rollback_status,
                    details=rollback_res.to_dict()
                )
                rollback_info = rollback_res.to_dict()
                
                # Halt execution of subsequent steps
                workflow_state = "WaitingApproval" if step_result.status == "waiting_approval" else "RolledBack"
                print(f"  🛑 Workflow execution halted. State: {workflow_state}")
                break

            # Brief delay between steps to respect API rate limits
            if step != ordered_steps[-1]:
                time.sleep(1)

        # Aggregate results and update final audit record
        agg_result = self._aggregate_results(plan, results, step_context)
        if rollback_info:
            agg_result["data"]["rollback"] = rollback_info

        # Calculate final overall confidence
        step_confidences = [
            r.data.get("confidence", 0.0) 
            for r in results 
            if r.status == "completed" and "confidence" in r.data
        ]
        overall_conf = round(sum(step_confidences) / len(step_confidences), 2) if step_confidences else 0.0

        # Update step results in Audit log
        execution_duration_ms = int((time.time() - start_time) * 1000)
        
        # Adjust final workflow state if completed with warnings
        if workflow_state == "Executing":
            if any(r.status == "completed_with_warning" for r in results):
                workflow_state = "CompletedWithWarning"
            elif any(r.status == "skipped" for r in results):
                workflow_state = "CompletedWithWarning"
            else:
                workflow_state = "Completed"

        self.audit_engine.update_step_results(
            tenant_id=tenant_id,
            audit_id=audit_id,
            step_results=[r.to_dict() for r in results],
            overall_confidence=overall_conf,
            workflow_state=workflow_state,
            execution_duration_ms=execution_duration_ms,
            llm_time_ms=llm_time_ms
        )
        
        # Append audit details to final response
        agg_result["data"]["audit_id"] = audit_id
        agg_result["data"]["overall_confidence"] = overall_conf
        
        event_bus.publish(BusinessEvent(
            tenant_id=tenant_id,
            event_type="WorkflowExecutionFinished",
            data={
                "audit_id": audit_id,
                "workflow_state": workflow_state,
                "overall_confidence": overall_conf,
                "summary": agg_result["data"].get("summary")
            }
        ))
        
        return agg_result

    def _execute_step(
        self,
        step: WorkflowStep,
        step_context: dict,
        user_context_str: str,
        mock_active_coa: str,
        mock_active_vendors: str,
        mock_global_taxes: str,
        tenant_tax_str: str,
        db_path: str,
        tenant_id: str,
        audio_base64: str = None
    ) -> StepResult:
        """
        Execute a single workflow step by dispatching to the appropriate agent.
        """

        if step.agent_type == "master_data":
            # Master data creation steps are handled deterministically (no LLM needed)
            return self._handle_master_data_step(step, step_context)

        elif step.agent_type in ("expense", "sales"):
            # Build enriched context from prior steps
            enriched_context = self._build_enriched_context(step, step_context, user_context_str)

            extraction = self.expense_agent.process_transaction(
                transcript=step.prompt_fragment,
                user_context_str=enriched_context,
                mock_active_coa=mock_active_coa,
                mock_active_vendors=mock_active_vendors,
                mock_global_taxes=mock_global_taxes,
                tenant_tax_str=tenant_tax_str,
                audio_base64=audio_base64
            )

            # Evaluate extraction against Policy Engine
            policy_result = self.policy_engine.evaluate(extraction)
            adjusted_extraction = policy_result.adjusted_extraction

            # Calculate confidence score
            confidence = ScoringService.calculate_confidence(adjusted_extraction)
            
            # Confidence Gate routing decision
            gate_decision = ScoringService.gate_decision(confidence)

            # Idempotency Check
            if adjusted_extraction.total_amount and adjusted_extraction.entity:
                is_duplicate = self.audit_engine.check_recent_duplicate(
                    tenant_id=tenant_id,
                    amount=adjusted_extraction.total_amount,
                    entity_name=adjusted_extraction.entity.name
                )
                if is_duplicate:
                    event_bus.publish(BusinessEvent(
                        tenant_id=tenant_id,
                        event_type="DuplicateTransactionDetected",
                        data={"amount": adjusted_extraction.total_amount, "entity": adjusted_extraction.entity.name}
                    ))
                    return StepResult(
                        step=step,
                        status="waiting_approval",
                        error=f"Idempotency Guard: Duplicate transaction detected for '{adjusted_extraction.entity.name}' with amount ₹{adjusted_extraction.total_amount:,.2f} in the last 5 minutes.",
                        data={
                            "extraction": adjusted_extraction.model_dump(),
                            "confidence": confidence,
                            "gate_decision": "requires_approval",
                            "applied_policies": policy_result.applied_policies,
                            "policy_overrides": policy_result.overrides
                        }
                    )

            if adjusted_extraction.approval_required:
                error_msg = " | ".join(adjusted_extraction.approval_reasons)
                event_bus.publish(BusinessEvent(
                    tenant_id=tenant_id,
                    event_type="ApprovalRequired",
                    data={"reasons": adjusted_extraction.approval_reasons, "amount": adjusted_extraction.total_amount}
                ))
                return StepResult(
                    step=step,
                    status="waiting_approval",
                    error=f"Policy Gate Blocked: {error_msg}",
                    data={
                        "extraction": adjusted_extraction.model_dump(),
                        "confidence": confidence,
                        "gate_decision": "requires_approval",
                        "applied_policies": policy_result.applied_policies,
                        "policy_overrides": policy_result.overrides
                    }
                )

            # If confidence is too low or policy requires clarification, trigger failure/rollback
            if gate_decision == "requires_clarification" or adjusted_extraction.clarification_needed:
                error_msg = adjusted_extraction.clarification_question or "Confidence threshold not met."
                return StepResult(
                    step=step,
                    status="failed",
                    error=f"Confidence Gate Blocked: {error_msg}",
                    data={
                        "extraction": adjusted_extraction.model_dump(),
                        "confidence": confidence,
                        "gate_decision": gate_decision,
                        "applied_policies": policy_result.applied_policies,
                        "policy_overrides": policy_result.overrides
                    }
                )

            return StepResult(
                step=step,
                status="completed",
                data={
                    "extraction": adjusted_extraction.model_dump(),
                    "confidence": confidence,
                    "gate_decision": gate_decision,
                    "applied_policies": policy_result.applied_policies,
                    "policy_overrides": policy_result.overrides,
                    "summary": adjusted_extraction.narration or step.description
                }
            )

        elif step.agent_type == "reporting":
            report_html = self.reporting_agent.generate_report(
                step.prompt_fragment, user_context_str, db_path
            )
            return StepResult(
                step=step,
                status="completed",
                data={
                    "report": report_html,
                    "summary": f"Generated report: {step.description}"
                }
            )

        elif step.agent_type == "advisory":
            advice_html = self.advisory_agent.provide_advice(
                step.prompt_fragment, user_context_str, db_path
            )
            return StepResult(
                step=step,
                status="completed",
                data={
                    "advice": advice_html,
                    "summary": f"Advisory response: {step.description}"
                }
            )

        else:
            return StepResult(
                step=step,
                status="completed",
                data={"summary": f"Acknowledged: {step.description}"}
            )

    def _handle_master_data_step(self, step: WorkflowStep, step_context: dict) -> StepResult:
        """
        Handle master data creation steps deterministically (no LLM call needed).
        These are simple CRUD operations that the backend API will execute.
        """
        params = step.parameters or {}

        if step.action == "create_product":
            return StepResult(
                step=step,
                status="completed",
                data={
                    "type": "master_data_creation",
                    "entity_type": "product",
                    "details": params,
                    "summary": f"Product '{params.get('name', 'Unknown')}' ready for creation. "
                               f"Cost: ₹{params.get('cost_price', 'N/A')}, "
                               f"Selling: ₹{params.get('selling_price', 'N/A')}, "
                               f"GST: {params.get('gst_rate', '18')}%"
                }
            )

        elif step.action == "create_supplier":
            return StepResult(
                step=step,
                status="completed",
                data={
                    "type": "master_data_creation",
                    "entity_type": "supplier",
                    "details": params,
                    "summary": f"Supplier '{params.get('name', 'Unknown')}' ready for registration."
                }
            )

        elif step.action == "create_customer":
            return StepResult(
                step=step,
                status="completed",
                data={
                    "type": "master_data_creation",
                    "entity_type": "customer",
                    "details": params,
                    "summary": f"Customer '{params.get('name', 'Unknown')}' ready for registration."
                }
            )

        elif step.action == "create_bank_account":
            return StepResult(
                step=step,
                status="completed",
                data={
                    "type": "master_data_creation",
                    "entity_type": "bank_account",
                    "details": params,
                    "summary": f"Bank Account '{params.get('name', 'Unknown')}' ready for setup."
                }
            )

        else:
            return StepResult(
                step=step,
                status="completed",
                data={
                    "type": "master_data_creation",
                    "details": params,
                    "summary": f"Master data step completed: {step.description}"
                }
            )

    def _build_enriched_context(self, step: WorkflowStep, step_context: dict, user_context_str: str) -> str:
        """
        Build enriched user context that includes results from prior completed steps.
        This enables context propagation between dependent steps.
        """
        prior_context_lines = []
        for dep_id in step.depends_on:
            if dep_id in step_context:
                dep_data = step_context[dep_id]
                prior_context_lines.append(
                    f"- Prior Step '{dep_id}' ({dep_data['action']}): {dep_data['result_summary']}"
                )

        if prior_context_lines:
            prior_str = "\n".join(prior_context_lines)
            return f"""{user_context_str}

PRIOR WORKFLOW CONTEXT (Results from earlier steps in this compound workflow):
{prior_str}

IMPORTANT: Use the entity names and amounts from the prior steps above. Do NOT ask for clarification about entities that were created in prior steps."""
        
        return user_context_str

    def _topological_sort(self, steps: list[WorkflowStep]) -> list[WorkflowStep]:
        """
        Sort steps in dependency order using Kahn's algorithm.
        Steps with no dependencies come first.
        """
        step_map = {s.step_id: s for s in steps}
        in_degree = {s.step_id: len(s.depends_on) for s in steps}
        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        ordered = []

        while queue:
            current = queue.pop(0)
            if current in step_map:
                ordered.append(step_map[current])

            # Reduce in-degree for dependent steps
            for s in steps:
                if current in s.depends_on:
                    in_degree[s.step_id] -= 1
                    if in_degree[s.step_id] == 0:
                        queue.append(s.step_id)

        # If some steps weren't visited (circular deps), append them anyway
        for s in steps:
            if s not in ordered:
                ordered.append(s)

        return ordered

    def _aggregate_results(self, plan: ExecutionPlan, results: list[StepResult], step_context: dict) -> dict:
        """
        Aggregate all step results into a unified compound response.
        """
        completed = [r for r in results if r.status == "completed"]
        failed = [r for r in results if r.status == "failed"]
        skipped = [r for r in results if r.status == "skipped"]

        # Collect all extractions from transaction steps
        extractions = []
        master_data_items = []
        reports = []

        for r in completed:
            if r.data.get("extraction"):
                extractions.append(r.data["extraction"])
            if r.data.get("type") == "master_data_creation":
                master_data_items.append(r.data)
            if r.data.get("report"):
                reports.append(r.data["report"])

        # Determine overall status
        if failed:
            overall_status = "partial_completion"
        elif skipped:
            overall_status = "partial_completion"
        else:
            overall_status = "workflow_completed"

        # Build summary message
        summary_parts = []
        summary_parts.append(f"Workflow executed {len(completed)}/{len(results)} steps successfully.")
        if master_data_items:
            summary_parts.append(f"Created {len(master_data_items)} master data record(s).")
        if extractions:
            summary_parts.append(f"Processed {len(extractions)} financial transaction(s).")
        if reports:
            summary_parts.append(f"Generated {len(reports)} report(s).")
        if failed:
            summary_parts.append(f"⚠️ {len(failed)} step(s) failed.")
        if skipped:
            summary_parts.append(f"⏭️ {len(skipped)} step(s) skipped due to dependencies.")

        return {
            "status": overall_status,
            "data": {
                "workflow_type": "compound",
                "plan_reasoning": plan.reasoning,
                "total_steps": len(results),
                "completed_steps": len(completed),
                "failed_steps": len(failed),
                "skipped_steps": len(skipped),
                "summary": " ".join(summary_parts),
                "steps": [r.to_dict() for r in results],
                "master_data": master_data_items,
                "extractions": extractions,
                "reports": reports
            }
        }
