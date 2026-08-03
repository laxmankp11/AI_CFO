from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict

class ExplainabilityTrace(BaseModel):
    rule_code: str = Field(description="The unique code of the policy rule applied (e.g., AR-008).")
    description: str = Field(description="Human-readable explanation of why this rule triggered.")
    decision: str = Field(description="The outcome of the rule (e.g., 'Approved', 'Rejected', 'Capitalized').")

class ExtractedEntity(BaseModel):
    id: Optional[str] = Field(None, description="UUID of the existing entity if matched exactly from context.")
    name: str = Field(description="Name of the vendor, customer, or employee.")
    is_new: bool = Field(description="True if no exact match was found in the provided context list.")

class LineItem(BaseModel):
    account_id: Optional[str] = Field(None, description="UUID of the matched Chart of Account.")
    account_name: str = Field(description="Name of the account (e.g. Rent Expense, CGST Payable).")
    amount: float = Field(description="Monetary amount for this line item.")
    dc: Literal["debit", "credit"] = Field(description="Whether this line is a debit or a credit.")
    description: Optional[str] = Field(None, description="Line item narration or description.")

class InvoiceItem(BaseModel):
    item_name: str = Field(description="Name or description of the product/service sold.")
    quantity: float = Field(description="Quantity of the item.")
    unit_price: float = Field(description="Price per single unit before tax.")

class OperationalData(BaseModel):
    invoice_items: Optional[list[InvoiceItem]] = Field(None, description="Line items for sales or purchase invoices.")
    invoice_number: Optional[str] = Field(None, description="Explicit invoice number if mentioned by the user.")

class TransactionExtraction(BaseModel):
    module: Literal["finance", "sales", "purchases", "inventory"] = Field("finance", description="Which business module this transaction belongs to.")
    clarification_needed: bool = Field(False, description="Set to true if you are missing critical accounting information.")
    clarification_question: Optional[str] = Field(None, description="The specific question you want to ask the user to clarify (e.g., 'Is GST included in this?').")
    
    approval_required: bool = Field(False, description="Set to true if transaction requires manual approval.")
    approval_reasons: list[str] = Field(default_factory=list, description="Reasons why approval is required.")

    
    intent: Literal["expense", "income", "asset_purchase", "transfer", "payment_receipt", "vendor_payment", "capital_injection", "sales_invoice", "unknown"] = Field(
        description="The primary accounting intent of this transaction."
    )
    total_amount: Optional[float] = Field(None, description="The total monetary amount. Must be positive.")
    entity: Optional[ExtractedEntity] = Field(None, description="The customer or vendor involved, if applicable.")
    
    operational_data: Optional[OperationalData] = Field(None, description="Business document details like item quantities and rates.")
    line_items: list[LineItem] = Field(default_factory=list, description="The double-entry bookkeeping lines.")
    explainability_traces: list[ExplainabilityTrace] = Field(default_factory=list, description="Traces of AI decisions and policies applied.")
    
    payment_channel: Optional[Literal["cash", "bank_transfer", "upi", "credit_card"]] = Field(
        None, description="How the transaction was paid or received."
    )
    narration: Optional[str] = Field(
        None, description="A detailed, human-readable summary of the entire transaction (e.g., 'Investment of 10000 by John Doe deposited in ICICI bank')."
    )
