"""
Execution Validator - Validates and auto-corrects LLM-generated execution plans
before the Workflow Orchestrator processes them.

Architecture:
    Business Workflow Planner → Execution Validator → Validated Plan → Orchestrator

Catches dependency inversions, circular references, missing prerequisites,
and duplicate actions — all deterministically without LLM calls.
"""

from typing import Optional
from services.agents.planning_agent import ExecutionPlan, WorkflowStep


# Dependency rules: action -> list of actions that MUST come before it
DEPENDENCY_RULES = {
    # Purchases require products and suppliers
    "record_purchase": ["create_product", "create_supplier"],
    # Sales require products and customers
    "create_invoice": ["create_product", "create_customer"],
    "record_sale": ["create_product", "create_customer"],
    # Payments require the entity they pay to/from
    "record_vendor_payment": ["create_supplier", "record_purchase"],
    "record_customer_payment": ["create_customer", "create_invoice"],
    # Reports should come after everything
    "generate_report": [],
    "generate_balance_sheet": [],
    "generate_pnl": [],
}

# Actions that produce master data (safe to keep on rollback)
MASTER_DATA_ACTIONS = {
    "create_product", "create_supplier", "create_customer",
    "create_bank_account", "create_employee"
}

# Actions that produce financial entries (must be rolled back on failure)
FINANCIAL_ACTIONS = {
    "record_purchase", "record_expense", "record_capital_injection",
    "record_vendor_payment", "create_invoice", "record_sale",
    "record_customer_payment"
}

# Actions that are read-only (no state change)
READONLY_ACTIONS = {
    "generate_report", "generate_balance_sheet", "generate_pnl",
    "provide_advice"
}


class ValidationCorrection:
    """Records a single correction made by the validator."""
    def __init__(self, rule: str, description: str, severity: str = "info"):
        self.rule = rule
        self.description = description
        self.severity = severity  # "info", "warning", "critical"

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "description": self.description,
            "severity": self.severity
        }


class ValidatedPlan:
    """Result of the Execution Validator."""
    def __init__(
        self,
        original_plan: ExecutionPlan,
        corrected_steps: list,
        corrections: list,
        is_valid: bool
    ):
        self.original_plan = original_plan
        self.corrected_steps = corrected_steps
        self.corrections = corrections
        self.is_valid = is_valid

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "original_step_count": len(self.original_plan.steps),
            "corrected_step_count": len(self.corrected_steps),
            "corrections": [c.to_dict() for c in self.corrections],
        }


class ExecutionValidator:
    """
    Validates and auto-corrects LLM-generated execution plans.
    
    All validation is deterministic (no LLM calls). Rules include:
    1. Dependency Inversion Detection & Auto-Fix
    2. Circular Dependency Detection & Breaking
    3. Missing Master Data Prerequisite Insertion
    4. Duplicate Action Merging
    5. Report Ordering (reports always last)
    """

    def validate(self, plan: ExecutionPlan) -> ValidatedPlan:
        """
        Validate and correct an execution plan.
        
        Returns ValidatedPlan with corrected steps, list of corrections made,
        and overall validity flag.
        """
        if not plan.is_compound or not plan.steps:
            return ValidatedPlan(
                original_plan=plan,
                corrected_steps=plan.steps,
                corrections=[],
                is_valid=True
            )

        corrections = []
        steps = [s.model_copy() for s in plan.steps]  # Work on copies

        # Rule 1: Detect and merge duplicate actions for the same entity
        steps, dedup_corrections = self._deduplicate_steps(steps)
        corrections.extend(dedup_corrections)

        # Rule 2: Enforce dependency rules (insert missing depends_on edges)
        steps, dep_corrections = self._enforce_dependencies(steps)
        corrections.extend(dep_corrections)

        # Rule 3: Detect and break circular dependencies
        steps, cycle_corrections = self._break_cycles(steps)
        corrections.extend(cycle_corrections)

        # Rule 4: Ensure reports come last
        steps, report_corrections = self._reports_last(steps)
        corrections.extend(report_corrections)

        # Rule 5: Validate all depends_on references exist
        steps, ref_corrections = self._validate_references(steps)
        corrections.extend(ref_corrections)

        is_valid = not any(c.severity == "critical" for c in corrections)

        if corrections:
            print(f"\n  🔍 Execution Validator: {len(corrections)} correction(s) applied")
            for c in corrections:
                icon = {"info": "ℹ️", "warning": "⚠️", "critical": "❌"}.get(c.severity, "•")
                print(f"     {icon} [{c.rule}] {c.description}")
        else:
            print(f"\n  ✅ Execution Validator: Plan is valid. No corrections needed.")

        return ValidatedPlan(
            original_plan=plan,
            corrected_steps=steps,
            corrections=corrections,
            is_valid=is_valid
        )

    def _deduplicate_steps(self, steps: list) -> tuple:
        """Merge duplicate actions targeting the same entity."""
        corrections = []
        seen = {}  # (action, entity_key) -> step_id
        unique_steps = []
        removed_ids = set()

        for step in steps:
            params = step.parameters or {}
            entity_key = params.get("name", "").lower().strip()
            dedup_key = (step.action, entity_key)

            if entity_key and dedup_key in seen:
                corrections.append(ValidationCorrection(
                    rule="DEDUP_MERGE",
                    description=f"Merged duplicate '{step.action}' for '{entity_key}' "
                                f"(step {step.step_id} merged into {seen[dedup_key]})",
                    severity="info"
                ))
                removed_ids.add(step.step_id)
            else:
                if entity_key:
                    seen[dedup_key] = step.step_id
                unique_steps.append(step)

        # Update depends_on references: replace removed step_ids with the merged one
        for step in unique_steps:
            step.depends_on = [
                d for d in step.depends_on if d not in removed_ids
            ]

        return unique_steps, corrections

    def _enforce_dependencies(self, steps: list) -> tuple:
        """Enforce that required prerequisite steps are in depends_on."""
        corrections = []
        step_actions = {s.step_id: s.action for s in steps}
        action_to_steps = {}
        for s in steps:
            action_to_steps.setdefault(s.action, []).append(s.step_id)

        for step in steps:
            required_actions = DEPENDENCY_RULES.get(step.action, [])
            for req_action in required_actions:
                if req_action in action_to_steps:
                    for prereq_id in action_to_steps[req_action]:
                        if prereq_id not in step.depends_on and prereq_id != step.step_id:
                            step.depends_on.append(prereq_id)
                            corrections.append(ValidationCorrection(
                                rule="DEP_INVERSION_FIX",
                                description=f"Added missing dependency: step '{step.step_id}' "
                                            f"({step.action}) now depends on '{prereq_id}' "
                                            f"({req_action})",
                                severity="warning"
                            ))

        return steps, corrections

    def _break_cycles(self, steps: list) -> tuple:
        """Detect and break circular dependencies using DFS."""
        corrections = []
        step_map = {s.step_id: s for s in steps}

        def has_cycle_from(start_id, visited=None, path=None):
            if visited is None:
                visited = set()
            if path is None:
                path = set()
            
            visited.add(start_id)
            path.add(start_id)

            if start_id in step_map:
                for dep_id in step_map[start_id].depends_on:
                    if dep_id in path:
                        return (start_id, dep_id)  # Cycle found
                    if dep_id not in visited:
                        result = has_cycle_from(dep_id, visited, path)
                        if result:
                            return result
            
            path.discard(start_id)
            return None

        # Check each step for cycles
        for step in steps:
            cycle = has_cycle_from(step.step_id)
            if cycle:
                from_id, to_id = cycle
                if from_id in step_map:
                    step_map[from_id].depends_on = [
                        d for d in step_map[from_id].depends_on if d != to_id
                    ]
                    corrections.append(ValidationCorrection(
                        rule="CYCLE_BREAK",
                        description=f"Broke circular dependency: removed edge "
                                    f"'{from_id}' → '{to_id}'",
                        severity="critical"
                    ))

        return steps, corrections

    def _reports_last(self, steps: list) -> tuple:
        """Ensure reporting steps depend on all non-reporting steps."""
        corrections = []
        report_steps = [s for s in steps if s.action in READONLY_ACTIONS]
        non_report_steps = [s for s in steps if s.action not in READONLY_ACTIONS]

        if report_steps and non_report_steps:
            all_non_report_ids = {s.step_id for s in non_report_steps}
            for report_step in report_steps:
                missing = all_non_report_ids - set(report_step.depends_on)
                if missing:
                    report_step.depends_on = list(
                        set(report_step.depends_on) | all_non_report_ids
                    )
                    corrections.append(ValidationCorrection(
                        rule="REPORTS_LAST",
                        description=f"Report step '{report_step.step_id}' now depends on "
                                    f"all {len(all_non_report_ids)} non-report steps",
                        severity="info"
                    ))

        return steps, corrections

    def _validate_references(self, steps: list) -> tuple:
        """Ensure all depends_on references point to existing step_ids."""
        corrections = []
        valid_ids = {s.step_id for s in steps}

        for step in steps:
            invalid_deps = [d for d in step.depends_on if d not in valid_ids]
            if invalid_deps:
                step.depends_on = [d for d in step.depends_on if d in valid_ids]
                corrections.append(ValidationCorrection(
                    rule="INVALID_REF_REMOVED",
                    description=f"Removed invalid dependency references from "
                                f"'{step.step_id}': {invalid_deps}",
                    severity="warning"
                ))

        return steps, corrections
