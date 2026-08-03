import os
from google import genai
from pydantic import BaseModel
from models.extraction import TransactionExtraction
from services.scoring_service import ScoringService
import sqlite3
import re

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # If no key, we fallback to our smart regex mock in the caller
        if api_key and len(api_key) > 10:
            self.client = genai.Client(api_key=api_key)

    def extract_transaction_from_text(self, transcript: str, tenant_id: str, audio_base64: str = None, user_context: dict = None) -> dict:
        db_path = f"../backend/database/tenant{tenant_id}"
        
        active_coa = []
        active_vendors = []
        tenant_tax = {}
        global_taxes = []
        
        central_db_path = f"../backend/database/database.sqlite"
        if os.path.exists(central_db_path):
            try:
                conn = sqlite3.connect(central_db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT tax_code, country, regime, components FROM global_tax_rules")
                for row in cursor.fetchall():
                    global_taxes.append(f"- {row['tax_code']}: {row['regime']} ({row['country']}) -> {row['components']}")
                conn.close()
            except Exception as e:
                print(f"Error reading central DB: {e}")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT id, code, name, type FROM accounts")
                for row in cursor.fetchall():
                    active_coa.append(f"- {row['id']}: {row['name']} ({row['type']})")
                    
                cursor.execute("SELECT id, name FROM suppliers")
                for row in cursor.fetchall():
                    active_vendors.append(f"- {row['id']}: {row['name']}")
                    
                cursor.execute("SELECT * FROM tenant_tax_settings LIMIT 1")
                tenant_tax_row = cursor.fetchone()
                if tenant_tax_row:
                    tenant_tax = dict(tenant_tax_row)
                    
                conn.close()
            except Exception as e:
                print(f"Error reading tenant DB: {e}")

        mock_active_coa = "\n".join(active_coa) if active_coa else "- (No accounts found)"
        mock_active_vendors = "\n".join(active_vendors) if active_vendors else "- (No suppliers found)"
        mock_global_taxes = "\n".join(global_taxes) if global_taxes else "- (No global tax rules found)"

        import json
        user_context_str = json.dumps(user_context, indent=2) if user_context else "None provided"
        tenant_tax_str = json.dumps(tenant_tax, indent=2) if tenant_tax else "No specific tax settings configured"

        # Active Memory Injection
        from services.memory_engine import MemoryEngine
        memory_engine = MemoryEngine(db_path=db_path)
        active_memory_graph = memory_engine.enrich_context(transcript)
        
        user_context_str += f"\n\n{active_memory_graph}"

        from services.agent_router import AgentRouter
        from services.agents.expense_agent import ExpenseAgent
        from services.agents.reporting_agent import ReportingAgent
        from services.agents.advisory_agent import AdvisoryAgent
        
        router = AgentRouter(self.client)
        decision = router.route(transcript, user_context)
        print(f"Agent Router Decision: {decision.agent_type} - {decision.reasoning}")

        try:
            if decision.agent_type == "compound":
                # === COMPOUND WORKFLOW: Planning Agent → Orchestrator ===
                from services.agents.planning_agent import BusinessWorkflowPlanner
                from services.workflow_orchestrator import WorkflowOrchestrator
                from services.execution_validator import ExecutionValidator

                print("\n🔀 Compound prompt detected. Invoking Business Workflow Planner...")
                planner = BusinessWorkflowPlanner(self.client)
                plan = planner.plan(transcript, user_context)

                print(f"📋 Raw Execution Plan: {len(plan.steps)} steps | Compound: {plan.is_compound}")
                print(f"   Reasoning: {plan.reasoning}")

                if plan.is_compound and plan.steps:
                    # Validate and correct the execution plan
                    validator = ExecutionValidator()
                    validated_plan = validator.validate(plan)
                    
                    # Update plan steps with validator corrected steps
                    plan.steps = validated_plan.corrected_steps

                    orchestrator = WorkflowOrchestrator(self.client)
                    result = orchestrator.execute(
                        plan=plan,
                        user_context_str=user_context_str,
                        mock_active_coa=mock_active_coa,
                        mock_active_vendors=mock_active_vendors,
                        mock_global_taxes=mock_global_taxes,
                        tenant_tax_str=tenant_tax_str,
                        db_path=db_path,
                        tenant_id=tenant_id,
                        original_prompt=transcript,
                        validator_corrections=validated_plan.corrections,
                        audio_base64=audio_base64
                    )
                    return result
                else:
                    # Planner said it's not actually compound — fall through to ExpenseAgent
                    print("   Business Workflow Planner override: Not compound. Falling through to ExpenseAgent.")
                    agent = ExpenseAgent(self.client)
                    extraction = agent.process_transaction(
                        transcript=transcript,
                        user_context_str=user_context_str,
                        mock_active_coa=mock_active_coa,
                        mock_active_vendors=mock_active_vendors,
                        mock_global_taxes=mock_global_taxes,
                        tenant_tax_str=tenant_tax_str,
                        audio_base64=audio_base64
                    )

            elif decision.agent_type == "reporting":
                agent = ReportingAgent(self.client)
                report_html = agent.generate_report(transcript, user_context_str, db_path)
                return {
                    "status": "report_generated",
                    "data": {
                        "ai_extraction_id": "ext_reporting_123",
                        "transcript": transcript,
                        "ai_message": report_html
                    }
                }
            elif decision.agent_type == "advisory":
                agent = AdvisoryAgent(self.client)
                report_html = agent.provide_advice(transcript, user_context_str, db_path)
                return {
                    "status": "report_generated",
                    "data": {
                        "ai_extraction_id": "ext_advisory_123",
                        "transcript": transcript,
                        "ai_message": report_html
                    }
                }
            else:
                # Default to ExpenseAgent for expenses, sales, follow_ups, etc for MVP
                agent = ExpenseAgent(self.client)
                extraction = agent.process_transaction(
                    transcript=transcript,
                    user_context_str=user_context_str,
                    mock_active_coa=mock_active_coa,
                    mock_active_vendors=mock_active_vendors,
                    mock_global_taxes=mock_global_taxes,
                    tenant_tax_str=tenant_tax_str,
                    audio_base64=audio_base64
                )
        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise

        # Calculate Confidence based on Line Items
        aggregate_score = ScoringService.calculate_confidence(extraction)

        # Evaluate Clarification Status
        if extraction.clarification_needed and extraction.clarification_question:
            status = "clarification_needed"
            ai_message = extraction.clarification_question
        else:
            status = "pending_confirmation" if aggregate_score >= 0.85 else "clarification_needed"
            if status == "pending_confirmation":
                ai_message = "I have extracted the details. Confirm?"
            else:
                ai_message = extraction.clarification_question if extraction.clarification_question else "I couldn't fully understand the financial transaction. Could you provide more details like the amount, category, and what it was for?"

        
        return {
            "status": status,
            "data": {
                "ai_extraction_id": "ext_gemini_123",
                "transcript": transcript if transcript != "Mock decoded audio transcript" else "Audio processed by Gemini",
                "extraction": extraction.model_dump(),
                "confidence": {
                    "aggregate": aggregate_score
                },
                "ai_message": ai_message
            }
        }
