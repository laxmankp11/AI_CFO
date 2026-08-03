import json
from google import genai
from models.extraction import TransactionExtraction
from services.retry_utils import call_with_retry

class ExpenseAgent:
    def __init__(self, client: genai.Client):
        self.client = client

    def process_transaction(self, transcript: str, user_context_str: str, mock_active_coa: str, mock_active_vendors: str, mock_global_taxes: str, tenant_tax_str: str, audio_base64: str = None) -> TransactionExtraction:
        system_prompt = f"""
        You are an expert Transaction Agent. Your job is to extract ALL types of financial transactions from the user's transcript and generate a proper double-entry journal (Debits and Credits must balance).
        
        USER CONTEXT (Role, Preferences, and Previous Clarification Extraction State):
        {user_context_str}

        IMPORTANT RAG CONTEXT:
        Active Chart of Accounts:
        {mock_active_coa}
        
        Active Vendors/Customers:
        {mock_active_vendors}
        
        GLOBAL TAX ENGINE (Level 1):
        {mock_global_taxes}
        
        TENANT TAX CONFIGURATION (Level 2):
        {tenant_tax_str}
        
        RULES:
        1. Strictly use the provided UUIDs if you find a match. Do not do internal math.
        2. If the transaction is an owner investment or capital injection, categorize it under an Equity account. Intent = 'capital_injection'.
        3. By default, module is 'finance'.

        TRANSACTION TYPE HANDLING:
        
        EXPENSES & ASSET PURCHASES:
        - Intent: 'expense', 'asset_purchase', or 'capital_injection'
        - Create proper debit/credit entries (Debit: Asset/Expense, Credit: Cash/Bank/Payable)
        - For MIXED PAYMENTS (e.g. "paid 50k now, rest next month"): Create 3+ line items:
          * Debit the asset/expense for the FULL amount
          * Credit Cash/Bank for the amount paid NOW
          * Credit Accounts Payable for the REMAINING amount
        - For LOAN-FINANCED purchases (e.g. "paid 5L down, financed rest through bank"):
          * Debit the asset for the FULL amount
          * Credit Cash/Bank for the down payment
          * Credit Loan Payable for the financed portion

        SALES INVOICES:
        - If the user mentions SELLING products/services to a customer:
          * Set module = 'sales', intent = 'sales_invoice'
          * Populate `operational_data` with items sold (item_name, quantity, unit_price)
          * Generate line_items: Debit Accounts Receivable, Credit Sales Revenue
          * If GST applies, add CGST/SGST/IGST line items

        CUSTOMER PAYMENT RECEIPTS:
        - If a customer is paying against an outstanding invoice:
          * Set intent = 'payment_receipt'
          * Generate line_items: Debit Cash/Bank, Credit Accounts Receivable

        VENDOR PAYMENTS:
        - If paying a vendor/supplier against outstanding bills:
          * Set intent = 'vendor_payment'
          * Generate line_items: Debit Accounts Payable, Credit Cash/Bank

        NARRATION:
        Always provide a highly detailed, comprehensive human-readable narration of the entire transaction in the `narration` field.
        For example, if the user says "I invested 10000 in business deposited in ICICI bank", the narration should be exactly "Investment of ₹10,000 by [owner name/role] deposited in ICICI Bank".

        CONVERSATIONAL MEMORY (CRITICAL):
        If the user is answering a previous clarification question (e.g., saying "yes", "included", or providing a missing name/number), you MUST look at the `previous_extraction` inside the USER CONTEXT.
        You must MERGE their new answer with the data from the `previous_extraction` to generate the final completed transaction. Do NOT treat their short answer as a brand new isolated transaction, and do NOT reject it as an unknown intent.

        CLARIFICATION ENGINE (CRITICAL RULES):
        You MUST ask for clarification (set clarification_needed=true and provide clarification_question) if any of the following are true:
        1. If the user mentions purchasing something over ₹50,000 but does NOT explicitly mention GST or "inclusive of tax" or "plus GST", you MUST ask "Is GST included in this amount or do you have a supplier tax invoice?".
        2. If Role="Accountant" and they say "I invested", this is ambiguous. You MUST ask "Who invested the capital?".
        3. If Role="Manager" and they say "I invested", ask for clarification on who contributed the capital.
        4. If the user says "Paid [Person Name] [Amount]" without specifying who that person is (employee, vendor, contractor, personal), you MUST ask "Who is [Person Name]? Are they an employee, vendor, contractor, or is this a personal payment?"
        5. If the user says "I purchased [expensive item]" without clarifying business vs personal use, you MUST ask "Is this for business use or personal use? Was this paid with company funds or personal funds?"
        6. MISSING MASTER DATA & BANK ACCOUNTS (BR-AI-003): If the user mentions a specific Bank (like HDFC, SBI, ICICI, etc.) or Master Record (Customer/Supplier) that is NOT present in the Active Chart of Accounts context, do NOT block the transaction or demand optional details like account numbers or IFSC upfront. Ask conversationally: "I noticed that your company doesn't have an [Entity/Bank Name] account configured yet. Would you like me to create it? I can set it up as Bank Name: [Bank Name], Account Type: Current Account, Ledger Group: Bank Accounts. You can add optional details like account numbers later in Settings."
        7. If the intent is entirely unknown, set clarification_needed=true.

        MULTI-LINE TAX SPLITS:
        If the user explicitly states "plus GST", "including 18% GST" (or similar), or the transaction clearly implies GST:
        - Generate one LineItem for the Gross Amount (e.g., Bank/Cash).
        - Generate one LineItem for the Base Amount (e.g., Expense/Asset).
        - Generate LineItems for CGST/SGST/IGST as applicable based on the rules.
        """

        parts = [{"text": system_prompt}]
        if audio_base64:
            parts.append({
                "inline_data": {
                    "mime_type": "audio/webm",
                    "data": audio_base64
                }
            })
            parts.append({"text": "\n\nPlease extract the transaction details from the audio provided."})
            if transcript and transcript != "Mock decoded audio transcript":
                parts.append({"text": f"\n\nHere is a transcribed version if helpful: {transcript}"})
        else:
            parts.append({"text": "\n\nTranscript:\n" + transcript})

        def _call():
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[
                    {"role": "user", "parts": parts}
                ],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': TransactionExtraction,
                },
            )
            extraction_dict = json.loads(response.text)
            return TransactionExtraction(**extraction_dict)

        return call_with_retry(_call)
