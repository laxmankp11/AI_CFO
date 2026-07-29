import sys
import os
import sqlite3
import json
import asyncio

# Setup paths to import AI service
workspace_dir = '/Users/apple/Documents/AICFO'
sys.path.append(os.path.join(workspace_dir, 'ai_service'))
from services.gemini_service import GeminiService

def test_sales_invoice_extraction():
    print("--- 1. Testing AI Extraction ---")
    
    # 1. Get the GEMINI API KEY from the central database
    try:
        conn = sqlite3.connect(os.path.join(workspace_dir, 'backend/database/database.sqlite'))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_settings WHERE key = 'gemini_api_key'")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("❌ GEMINI API KEY not found in system_settings!")
            return False
            
        api_key = row[0]
        print("✅ Retrieved Gemini API Key.")
    except Exception as e:
        print(f"❌ Failed to read database: {e}")
        return False
        
    # 2. Find the tenant ID
    try:
        conn = sqlite3.connect(os.path.join(workspace_dir, 'backend/database/database.sqlite'))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tenants LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("❌ No tenant found in the database!")
            return False
            
        tenant_id = row[0]
        print(f"✅ Found Tenant ID: {tenant_id}")
    except Exception as e:
        print(f"❌ Failed to find tenant: {e}")
        return False

    # 3. Initialize GeminiService
    service = GeminiService(api_key=api_key)
    
    # 4. Run the test prompt
    prompt = "Create an invoice for Reliance Industries for 5 Enterprise Laptops at ₹85,000 each plus 18% GST."
    print(f"\nPrompt: '{prompt}'")
    
    user_context = {
        "id": 2,
        "name": "Business Owner",
        "email": "info@see.com",
        "is_super_admin": False,
        "tenant_id": tenant_id
    }
    
    print("Calling Gemini API...")
    try:
        result = service.extract_transaction_from_text(prompt, tenant_id, user_context=user_context)
        print("\n✅ AI Extraction Successful! Result:")
        print(json.dumps(result, indent=2))
        
        # Verify the extraction
        assert result['data']['extraction']['module'] == 'sales', "Module should be sales"
        assert result['data']['extraction']['intent'] == 'sales_invoice', "Intent should be sales_invoice"
        assert 'Reliance' in result['data']['extraction']['entity']['name'], "Customer name should be extracted"
        assert len(result['data']['extraction']['operational_data']['invoice_items']) == 1, "Should have 1 invoice item"
        assert result['data']['extraction']['operational_data']['invoice_items'][0]['quantity'] == 5, "Quantity should be 5"
        
        print("\n✅ All AI Assertions Passed! Operations Manager logic is working flawlessly.")
        return True
    except Exception as e:
        print(f"\n❌ AI Extraction Failed or Assertions Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sales_invoice_extraction()
