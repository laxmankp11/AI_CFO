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

        system_prompt = f"""
        You are an expert Virtual CFO. Your job is to extract accounting details from the user's transcript and generate a proper double-entry journal (Debits and Credits must balance).
        
        IMPORTANT RAG CONTEXT:
        Active Chart of Accounts:
        {mock_active_coa}
        
        Active Vendors/Customers:
        {mock_active_vendors}
        
        GLOBAL TAX ENGINE (Level 1):
        {mock_global_taxes}
        
        TENANT TAX CONFIGURATION (Level 2):
        {tenant_tax_str}
        
        Strictly use the provided UUIDs if you find a match. Do not do internal math.
        If the transaction is an owner investment or capital injection, categorize it under an Equity account.

        CLARIFICATION ENGINE (CRITICAL RULES):
        You MUST ask for clarification (set clarification_needed=true and provide clarification_question) if any of the following are true:
        1. If the user mentions purchasing something over ₹50,000 but does NOT explicitly mention GST or "inclusive of tax", you MUST ask "Is GST included in this amount or do you have a supplier tax invoice?".
        2. If Role="Accountant" and they say "I invested", this is ambiguous. You MUST ask "Who invested the capital?".
        3. If Role="Manager" and they say "I invested", ask for clarification on who contributed the capital.
        4. If it's a vendor payment but you cannot figure out which vendor it is.

        MULTI-LINE TAX SPLITS:
        If the user explicitly states "including 18% GST" (or similar), or the transaction clearly implies GST according to the Tax Engine rules:
        - Generate one LineItem for the Gross Amount (e.g., Bank/Cash).
        - Generate one LineItem for the Base Amount (e.g., Expense/Asset).
        - Generate LineItems for CGST/SGST/IGST as applicable based on the rules.

        OPERATIONS MANAGER (MODULES):
        - By default, module is 'finance'.
        - If the user asks to "create an invoice", "generate an invoice", or "bill a customer" for products/services:
          1. Set module = 'sales'
          2. Set intent = 'sales_invoice'
          3. Populate `operational_data` with the items sold (item_name, quantity, unit_price).
          4. You MUST STILL generate the financial `line_items` for this invoice (e.g., Debit Accounts Receivable, Credit Sales Revenue).
        """

        # Build the contents array
        parts = [{"text": system_prompt}]
        if audio_base64:
            import base64
            # We assume it's webm as sent by our frontend
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

        # Call real Gemini API with Structured Outputs (json_schema)
        try:
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[
                    {"role": "user", "parts": parts}
                ],
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': TransactionExtraction,
                },
            )
            
            # response.text is guaranteed to be a JSON string matching the Pydantic schema
            import json
            extraction_dict = json.loads(response.text)
            extraction = TransactionExtraction(**extraction_dict)
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise

        # Evaluate Clarification Status
        if extraction.clarification_needed and extraction.clarification_question:
            status = "clarification_needed"
            ai_message = extraction.clarification_question
        else:
            # Calculate Confidence based on Line Items
            aggregate_score = ScoringService.calculate_confidence(extraction)
            status = "pending_confirmation" if aggregate_score >= 0.85 else "clarification_needed"
            ai_message = "I have extracted the details. Confirm?" if status == "pending_confirmation" else "I need a bit more detail to record this properly."

        
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
