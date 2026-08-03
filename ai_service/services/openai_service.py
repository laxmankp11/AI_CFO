import os
from openai import OpenAI
from pydantic import BaseModel
from models.extraction import TransactionExtraction
from services.scoring_service import ScoringService

class OpenAIService:
    def __init__(self):
        # In a real app, this would use a real key from os.environ
        # We will mock the response for demonstration if no key is provided
        api_key = os.getenv("OPENAI_API_KEY", "mock-key")
        self.is_mock = api_key == "mock-key"
        if not self.is_mock:
            self.client = OpenAI(api_key=api_key)

    def extract_transaction_from_text(self, transcript: str, tenant_id: str, audio_base64: str = None, user_context: dict = None) -> dict:
        """
        Executes the RAG pipeline and calls OpenAI structured outputs.
        """
        import sqlite3
        
        db_path = f"../backend/database/tenant{tenant_id}"
        
        active_coa = []
        active_vendors = []
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Fetch accounts
                cursor.execute("SELECT id, code, name, type FROM accounts")
                for row in cursor.fetchall():
                    active_coa.append(f"- {row['id']}: {row['name']} ({row['type']})")
                    
                # Fetch suppliers
                cursor.execute("SELECT id, name FROM suppliers")
                for row in cursor.fetchall():
                    active_vendors.append(f"- {row['id']}: {row['name']}")
                    
                conn.close()
            except Exception as e:
                print(f"Error reading tenant DB: {e}")
        else:
            print(f"Warning: DB {db_path} not found")

        mock_active_coa = "\n".join(active_coa) if active_coa else "- (No accounts found)"
        mock_active_vendors = "\n".join(active_vendors) if active_vendors else "- (No suppliers found)"

        user_context_str = str(user_context) if user_context else "None"

        system_prompt = f"""
        You are an expert Virtual CFO. Extract accounting details from the user's transcript.
        
        USER CONTEXT (Role, Preferences, and Previous Clarification Extraction State):
        {user_context_str}

        IMPORTANT RAG CONTEXT:
        Active Chart of Accounts:
        {mock_active_coa}
        
        Active Vendors/Customers:
        {mock_active_vendors}
        
        Strictly use the provided UUIDs if you find a match. Do not do internal math.
        
        CLARIFICATION ENGINE (CRITICAL RULES):
        1. If the intent is entirely unknown or you cannot determine what financial transaction the user is trying to record (e.g., they ask to "add a new accountant" or just say hello), set clarification_needed=true and ask a helpful question in clarification_question like "It seems you want to do something outside of recording a transaction. I am currently designed to record financial transactions, could you provide details for a journal entry, invoice, or bill instead?"
        """

        if self.is_mock:
            import re
            
            # Simple Regex Mock Parser for Demo Purposes
            
            # Extract amount
            amount_match = re.search(r'\b\d+\b', transcript)
            amount = float(amount_match.group()) if amount_match else 4500.0
            
            # Extract name (e.g. "to ankita")
            name_match = re.search(r'to\s+([a-zA-Z]+)', transcript, re.IGNORECASE)
            vend_name = name_match.group(1).capitalize() if name_match else "Rajesh"
            
            # Check if extracted name exists in our RAG context
            vend_id = None
            is_new = True
            for v in active_vendors:
                if vend_name.lower() in v.lower():
                    vend_id = v.split(':')[0].replace('- ', '')
                    vend_name = v.split(':')[1].strip()
                    is_new = False
                    break
                    
            if is_new:
                # Mock a fake UUID for the new entity
                vend_id = "new-uuid-" + vend_name.lower()

            # Determine intent
            intent = "expense"
            if re.search(r'\b(received|sold)\b', transcript, re.IGNORECASE):
                intent = "income"

            # Filter accounts by intent type to get a realistic match
            target_type = "Expense" if intent == "expense" else "Revenue"
            matching_accounts = [acc for acc in active_coa if f"({target_type})" in acc]
            
            if matching_accounts:
                first_account = matching_accounts[0]
            else:
                first_account = active_coa[0] if active_coa else "- uuid-rent: Rent Expense (Expense)"
                
            acc_id = first_account.split(':')[0].replace('- ', '')
            acc_name = first_account.split(':')[1].strip()

            import json
            extraction = TransactionExtraction(
                intent=intent,
                amount=amount,
                entity={"id": vend_id, "name": vend_name, "is_new": is_new},
                category={"id": acc_id, "name": acc_name},
                payment_channel="cash",
                gst_itc_eligible=False
            )
        else:
            # Call real OpenAI API with Structured Outputs (json_schema)
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript}
                ],
                response_format=TransactionExtraction,
            )
            extraction = response.choices[0].message.parsed
            
        # Calculate Confidence
        aggregate_score = ScoringService.calculate_confidence(extraction)
        
        status = "pending_confirmation" if aggregate_score >= 0.85 else "clarification_needed"
        if status == "pending_confirmation":
            ai_message = "I have extracted the details. Confirm?"
        else:
            # Note: openai schema extraction obj might not have clarification_question if not in schema.
            # Assuming it is in TransactionExtraction schema:
            ai_message = getattr(extraction, 'clarification_question', None)
            if not ai_message:
                ai_message = "I couldn't fully understand the financial transaction. Could you provide more details like the amount, category, and what it was for?"
        return {
            "status": status,
            "data": {
                "ai_extraction_id": "ext_mock_123",
                "transcript": transcript,
                "extraction": extraction.model_dump(),
                "confidence": {
                    "aggregate": aggregate_score
                },
                "ai_message": ai_message
            }
        }
