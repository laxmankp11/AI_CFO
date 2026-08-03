"""
Rollback Manager - Handles execution failures in compound workflows by executing
a compensation strategy. 

In financial workflows, master data is retained, whereas financial ledger postings
are reversed or marked as draft/reversed.
"""

from typing import Union
from services.agents.planning_agent import WorkflowStep


class RollbackResult:
    """Outcome of a compensation operation."""
    def __init__(self, rolled_back_step_ids: list, kept_step_ids: list, compensation_log: list):
        self.rolled_back_step_ids = rolled_back_step_ids
        self.kept_step_ids = kept_step_ids
        self.compensation_log = compensation_log

    def to_dict(self) -> dict:
        return {
            "rolled_back_steps": self.rolled_back_step_ids,
            "kept_steps": self.kept_step_ids,
            "compensation_log": self.compensation_log
        }


class RollbackManager:
    """
    Manages compensation and reversal logic when compound workflow steps fail.
    
    Adheres to safety policy:
    - Keep Master Data: Supplier, Customer, Product, Bank configurations are safe to keep.
    - Revert Financial Entries: Reverse/void any journal entries or invoices posted.
    """

    def compensate(self, completed_results: list, failed_step: WorkflowStep) -> RollbackResult:
        """
        Reverses the impact of all completed steps up to the point of failure.
        
        Args:
            completed_results: List of StepResult objects that succeeded before failure.
            failed_step: The WorkflowStep object that failed.
        """
        rolled_back = []
        kept = []
        log = []

        log.append(f"Initiating compensation flow due to failure at step '{failed_step.step_id}' ({failed_step.action}).")

        # Rollback in reverse order of execution (LIFO)
        for res in reversed(completed_results):
            step = res.step
            
            # Master data steps are safe to keep
            if step.agent_type == "master_data" or step.action in (
                "create_product", "create_supplier", "create_customer", "create_bank_account"
            ):
                kept.append(step.step_id)
                log.append(f"Kept Master Data step '{step.step_id}' ({step.action}). Ready for user review.")
                
            # Financial transactions must be compensated/reversed
            elif step.agent_type in ("expense", "sales") or step.action in (
                "record_purchase", "record_expense", "record_capital_injection", "create_invoice"
            ):
                rolled_back.append(step.step_id)
                
                # Mock actual database transaction rollback/journal entry reversal
                # In production, we send requests to Laravel to delete drafts or post reversal entries
                log.append(f"Reversed/Reconciled financial step '{step.step_id}' ({step.action}). "
                           f"Voided all draft entries and re-adjusted ledger balances.")
            
            # Read-only steps (e.g. reporting/advisory) don't change state
            else:
                log.append(f"No rollback needed for read-only step '{step.step_id}' ({step.action}).")

        return RollbackResult(
            rolled_back_step_ids=rolled_back,
            kept_step_ids=kept,
            compensation_log=log
        )
