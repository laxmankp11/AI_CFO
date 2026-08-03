"""
Policy Engine - Enforces configurable business and accounting rules on agent
extractions, ensuring compliance with organizational policies.

Policies include asset capitalization thresholds, tax verification triggers,
and credit terms mapping.
"""

import os
import json
from models.extraction import TransactionExtraction, ExplainabilityTrace


class PolicyResult:
    """Result of evaluating extraction against policies."""
    def __init__(
        self,
        original_extraction: TransactionExtraction,
        adjusted_extraction: TransactionExtraction,
        applied_policies: list,
        overrides: dict
    ):
        self.original_extraction = original_extraction
        self.adjusted_extraction = adjusted_extraction
        self.applied_policies = applied_policies
        self.overrides = overrides


class PolicyEngine:
    """
    Enforces business policies on extracted accounting data.
    
    Prevents the LLM from deciding accounting treatment (such as expense vs. asset capitalization).
    """

    def __init__(self, policy_config_path: str = "policies/default_policies.json"):
        self.policy_config_path = policy_config_path
        self.policies = self._load_policies()

    def evaluate(self, extraction: TransactionExtraction) -> PolicyResult:
        """
        Evaluate a transaction extraction against configured policies.
        
        Modifies and returns the extraction if policies warrant adjustments.
        """
        adjusted = extraction.model_copy(deep=True)
        applied_policies = []
        overrides = {}

        # 1. Asset capitalization threshold check (Rule: ASSET_THRESHOLD)
        asset_threshold = self.policies.get("ASSET_THRESHOLD", 20000.0)
        if adjusted.intent == "expense" and adjusted.total_amount:
            # If expense amount exceeds threshold, auto-promote to asset_purchase
            if adjusted.total_amount >= asset_threshold:
                adjusted.intent = "asset_purchase"
                applied_policies.append("ASSET_THRESHOLD")
                
                trace_reason = f"Amount ₹{adjusted.total_amount:,.2f} meets or exceeds asset capitalization threshold of ₹{asset_threshold:,.2f}."
                overrides["intent"] = {
                    "original": "expense",
                    "new": "asset_purchase",
                    "reason": trace_reason
                }
                
                adjusted.explainability_traces.append(ExplainabilityTrace(
                    rule_code="CAP-001",
                    description=trace_reason,
                    decision="Capitalized"
                ))
                
                # Check line items and reclassify expense account to asset account names if appropriate
                for item in adjusted.line_items:
                    if item.dc == "debit" and "expense" in item.account_name.lower():
                        old_name = item.account_name
                        item.account_name = item.account_name.replace("Expense", "Asset").replace("expense", "asset")
                        overrides[f"line_item_{item.account_name}"] = {
                            "original": old_name,
                            "new": item.account_name,
                            "reason": "Reclassified debit account to Asset due to capitalization threshold."
                        }

        # 2. Tax verification trigger (Rule: GST_TRIGGER)
        gst_trigger = self.policies.get("GST_TRIGGER", 50000.0)
        if adjusted.total_amount and adjusted.total_amount >= gst_trigger:
            has_tax = any(
                "tax" in (item.account_name or "").lower() or 
                "gst" in (item.account_name or "").lower() or
                "cgst" in (item.account_name or "").lower() or
                "sgst" in (item.account_name or "").lower()
                for item in adjusted.line_items
            )
            if not has_tax and not adjusted.clarification_needed:
                adjusted.clarification_needed = True
                
                trace_reason = f"Verification required for transactions >= ₹{gst_trigger:,.2f} without tax details."
                
                adjusted.clarification_question = (
                    f"This transaction is ₹{adjusted.total_amount:,.2f} which is above our ₹{gst_trigger:,.2f} "
                    f"tax verification limit. Is GST included in this amount, and do you have a tax invoice?"
                )
                applied_policies.append("GST_TRIGGER")
                overrides["clarification_needed"] = {
                    "original": False,
                    "new": True,
                    "reason": trace_reason
                }
                
                adjusted.explainability_traces.append(ExplainabilityTrace(
                    rule_code="TAX-001",
                    description=trace_reason,
                    decision="Clarification Requested"
                ))

        # 3. High Value Approval Gate (Rule: APPROVAL_THRESHOLD)
        approval_threshold = self.policies.get("APPROVAL_THRESHOLD", 1000000.0)
        if adjusted.total_amount and adjusted.total_amount >= approval_threshold:
            trace_reason = f"High value transaction >= ₹{approval_threshold:,.2f}"
            adjusted.approval_required = True
            adjusted.approval_reasons.append(f"Transaction amount ₹{adjusted.total_amount:,.2f} requires approval (Threshold: ₹{approval_threshold:,.2f}).")
            applied_policies.append("APPROVAL_THRESHOLD")
            overrides["approval_required"] = {
                "original": False,
                "new": True,
                "reason": trace_reason
            }
            
            adjusted.explainability_traces.append(ExplainabilityTrace(
                rule_code="AR-008",
                description=f"Transaction exceeds approval threshold. Rule AR-008 requires approval for >= ₹{approval_threshold:,.2f}.",
                decision="Requires Approval"
            ))

        # 4. Default payment term mapping
        default_credit_days = self.policies.get("CREDIT_TERMS_DEFAULT", 30)
        # Note: In a real system, we'd check/update terms if needed.
        # But this shows how the engine handles general business configuration validation.

        return PolicyResult(
            original_extraction=extraction,
            adjusted_extraction=adjusted,
            applied_policies=applied_policies,
            overrides=overrides
        )

    def _load_policies(self) -> dict:
        """Load configuration or fallback to hardcoded defaults."""
        defaults = {
          "ASSET_THRESHOLD": 20000.0,
          "GST_TRIGGER": 50000.0,
          "APPROVAL_THRESHOLD": 1000000.0,
          "INVENTORY_METHOD": "FIFO",
          "DEPRECIATION_METHOD": "WDV",
          "CREDIT_TERMS_DEFAULT": 30
        }
        
        if os.path.exists(self.policy_config_path):
            try:
                with open(self.policy_config_path, "r") as f:
                    config = json.load(f)
                    return {k: v.get("value", defaults[k]) for k, v in config.items() if k in defaults}
            except Exception as e:
                print(f"Error reading policies file {self.policy_config_path}: {e}. Using defaults.")
        
        return defaults
