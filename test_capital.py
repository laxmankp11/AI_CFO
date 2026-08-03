import sys
import os
import sqlite3
import json

workspace_dir = '/Users/apple/Documents/AICFO'
sys.path.append(os.path.join(workspace_dir, 'ai_service'))
from services.gemini_service import GeminiService

def test_capital_injection():
    try:
        conn = sqlite3.connect(os.path.join(workspace_dir, 'backend/database/database.sqlite'))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_settings WHERE key = 'gemini_api_key'")
        row = cursor.fetchone()
        
        cursor.execute("SELECT id FROM tenants LIMIT 1")
        tenant_row = cursor.fetchone()
        conn.close()
        
        if not row or not tenant_row:
            print("Missing DB config")
            return
            
        api_key = row[0]
        tenant_id = tenant_row[0]
        
        service = GeminiService(api_key=api_key)
        prompt = "I invested ₹20,00,000 into the business through our HDFC Bank account as initial capital."
        
        user_context = {
            "id": 2,
            "name": "Business Owner",
            "email": "info@see.com",
            "is_super_admin": False,
            "tenant_id": tenant_id
        }
        
        result = service.extract_transaction_from_text(prompt, tenant_id, user_context=user_context)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_capital_injection()
