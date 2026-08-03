#!/usr/bin/env python3
"""
AI CFO Business Conversation Test Suite
Tests all 15 prompts against the live Multi-Agent architecture.
Run from ai_service/ directory.
"""
import sys
import os
import json
import time

# Ensure our modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Test Definitions ────────────────────────────────────────────
TESTS = [
    {
        "id": 1,
        "name": "Company Setup",
        "prompt": "We have started a new company called ABC Electronics Pvt. Ltd. We are located in Ahmedabad, Gujarat. Our GST number is 24ABCDE1234F1Z5. We mainly deal in laptops and computer accessories. Please configure my company.",
        "expected_behavior": "Should ask clarification (financial year, accounting method) OR route to an onboarding agent. Must NOT create a journal entry.",
        "pass_criteria": lambda r: r["status"] in ("clarification_needed", "report_generated"),
    },
    {
        "id": 2,
        "name": "Initial Capital",
        "prompt": "I invested ₹20,00,000 into the business through our HDFC Bank account.",
        "expected_behavior": "Should extract capital_injection. Debit Bank, Credit Owner's Equity.",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and r["data"].get("extraction", {}).get("intent") in ("capital_injection", "transfer", "income"),
    },
    {
        "id": 3,
        "name": "Purchase on Credit",
        "prompt": "Purchased 50 Dell laptops from Tech Distributors worth ₹18,00,000 plus GST on 45 days credit.",
        "expected_behavior": "Should create purchase entry with GST split, Accounts Payable, and entity extraction.",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and r["data"].get("extraction", {}).get("total_amount", 0) > 0,
    },
    {
        "id": 4,
        "name": "Mixed Payment",
        "prompt": "Bought office furniture worth ₹1,20,000. Paid ₹50,000 immediately and the remaining amount will be paid next month.",
        "expected_behavior": "Should create asset purchase with split payment (Cash + Payable).",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and len(r["data"].get("extraction", {}).get("line_items", [])) >= 2,
    },
    {
        "id": 5,
        "name": "Sales Invoice",
        "prompt": "Sell 10 Dell laptops to Rahul Technologies at ₹48,000 each plus GST. Give them 30 days credit.",
        "expected_behavior": "Should create sales_invoice intent with customer entity, operational_data items, and financial line_items.",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and r["data"].get("extraction", {}).get("intent") in ("sales_invoice", "income"),
    },
    {
        "id": 6,
        "name": "Partial Customer Payment",
        "prompt": "Rahul Technologies transferred ₹2,50,000 today against their outstanding invoice.",
        "expected_behavior": "Should create a payment_receipt with customer entity.",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and r["data"].get("extraction", {}).get("intent") in ("payment_receipt", "income", "transfer"),
    },
    {
        "id": 7,
        "name": "Ambiguous Expense",
        "prompt": "Paid Rajesh ₹25,000.",
        "expected_behavior": "Should ask clarification: Who is Rajesh? Employee, vendor, contractor, personal? No journal entry created.",
        "pass_criteria": lambda r: r["status"] == "clarification_needed",
    },
    {
        "id": 8,
        "name": "Business vs Personal",
        "prompt": "I purchased a MacBook for ₹1,80,000.",
        "expected_behavior": "Should ask clarification: business use? personal use? which funds?",
        "pass_criteria": lambda r: r["status"] == "clarification_needed",
    },
    {
        "id": 9,
        "name": "Vendor Payment",
        "prompt": "Pay Tech Distributors ₹5,00,000 from our ICICI Bank account towards the oldest outstanding invoices.",
        "expected_behavior": "Should create vendor_payment with entity Tech Distributors.",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and r["data"].get("extraction", {}).get("intent") in ("vendor_payment", "expense"),
    },
    {
        "id": 10,
        "name": "Fixed Asset & Loan",
        "prompt": "We purchased a company car worth ₹18,00,000. We paid ₹5,00,000 as down payment and financed the rest through Axis Bank.",
        "expected_behavior": "Should create asset_purchase with split: Debit Vehicle, Credit Bank (5L), Credit Loan (13L).",
        "pass_criteria": lambda r: r["status"] == "pending_confirmation" and len(r["data"].get("extraction", {}).get("line_items", [])) >= 3,
    },
    {
        "id": 11,
        "name": "Month-End Closing",
        "prompt": "Today is the last day of the month. Please complete all month-end activities and generate financial statements.",
        "expected_behavior": "Should route to reporting agent and generate a report, NOT create a journal entry.",
        "pass_criteria": lambda r: r["status"] == "report_generated",
    },
    {
        "id": 12,
        "name": "Business Question (Advisory)",
        "prompt": "Can I afford to purchase another delivery vehicle worth ₹12 lakh?",
        "expected_behavior": "Should route to advisory agent, analyze cash balance, and provide advice. NOT create a journal entry.",
        "pass_criteria": lambda r: r["status"] == "report_generated",
    },
    {
        "id": 13,
        "name": "AI Memory Query",
        "prompt": "How much have I paid Tech Distributors so far?",
        "expected_behavior": "Should route to reporting agent and query past transactions. NOT hallucinate.",
        "pass_criteria": lambda r: r["status"] == "report_generated",
    },
    {
        "id": 14,
        "name": "GST Intelligence",
        "prompt": "Generate this month's GST report and tell me how much tax I need to pay.",
        "expected_behavior": "Should route to reporting agent and generate GST summary.",
        "pass_criteria": lambda r: r["status"] == "report_generated",
    },
    {
        "id": 15,
        "name": "Executive Summary",
        "prompt": "Give me a complete overview of my business.",
        "expected_behavior": "Should route to reporting agent and generate executive summary with Revenue, Expenses, Profit, Cash, etc.",
        "pass_criteria": lambda r: r["status"] == "report_generated",
    },
]


def get_gemini_key():
    """Read Gemini key from system settings DB."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "database", "database.sqlite")
    if not os.path.exists(db_path):
        print(f"ERROR: Central DB not found at {db_path}")
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key = 'gemini_api_key'")
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else None


def get_tenant_id():
    """Get the first tenant ID available."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "database", "database.sqlite")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tenants LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else "demo-tenant-id"


def run_test(test, gemini_service, tenant_id):
    """Run a single test against the GeminiService."""
    print(f"\n{'='*70}")
    print(f"  TEST {test['id']}: {test['name']}")
    print(f"  PROMPT: \"{test['prompt'][:80]}...\"")
    print(f"{'='*70}")

    try:
        start = time.time()
        result = gemini_service.extract_transaction_from_text(
            transcript=test["prompt"],
            tenant_id=tenant_id,
            audio_base64=None,
            user_context={"role": "Owner", "business_name": "ABC Electronics Pvt. Ltd."}
        )
        elapsed = time.time() - start

        status = result.get("status", "unknown")
        ai_message = result.get("data", {}).get("ai_message", "")
        extraction = result.get("data", {}).get("extraction", {})
        
        passed = test["pass_criteria"](result)

        print(f"  STATUS: {status}")
        print(f"  TIME: {elapsed:.1f}s")

        if extraction:
            print(f"  INTENT: {extraction.get('intent', 'N/A')}")
            print(f"  AMOUNT: {extraction.get('total_amount', 'N/A')}")
            print(f"  NARRATION: {extraction.get('narration', 'N/A')}")
            print(f"  CLARIFICATION: {extraction.get('clarification_needed', False)}")
            if extraction.get("clarification_question"):
                print(f"  QUESTION: {extraction.get('clarification_question')}")
            print(f"  LINE_ITEMS: {len(extraction.get('line_items', []))}")
            for li in extraction.get("line_items", []):
                print(f"    - {li.get('dc','?').upper():6s} {li.get('account_name','?'):30s} ₹{li.get('amount',0):>12,.2f}")
        elif ai_message:
            # Truncate HTML report for display
            clean = ai_message[:200].replace('\n', ' ')
            print(f"  AI REPORT (preview): {clean}...")

        verdict = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n  EXPECTED: {test['expected_behavior']}")
        print(f"  VERDICT: {verdict}")

        return {
            "id": test["id"],
            "name": test["name"],
            "passed": passed,
            "status": status,
            "time": round(elapsed, 1),
            "intent": extraction.get("intent") if extraction else None,
            "amount": extraction.get("total_amount") if extraction else None,
            "line_items_count": len(extraction.get("line_items", [])) if extraction else 0,
        }

    except Exception as e:
        print(f"  ❌ EXCEPTION: {e}")
        return {
            "id": test["id"],
            "name": test["name"],
            "passed": False,
            "status": "error",
            "time": 0,
            "error": str(e),
        }


def main():
    print("=" * 70)
    print("  AI CFO BUSINESS CONVERSATION TEST SUITE")
    print("  Testing 15 prompts against Multi-Agent Architecture")
    print("=" * 70)

    gemini_key = get_gemini_key()
    if not gemini_key or len(gemini_key) < 10:
        print("ERROR: No valid Gemini API key found in system_settings.")
        sys.exit(1)
    print(f"  Gemini Key: ...{gemini_key[-6:]}")

    tenant_id = get_tenant_id()
    print(f"  Tenant ID: {tenant_id}")

    from services.gemini_service import GeminiService
    service = GeminiService(api_key=gemini_key)

    results = []
    total = len(TESTS)
    for i, test in enumerate(TESTS):
        result = run_test(test, service, tenant_id)
        results.append(result)
        # Respect Gemini free-tier rate limit (5 RPM). Each test uses ~2 calls.
        if i < total - 1:
            print(f"\n  ⏳ Waiting 15s before next test to respect rate limits...")
            time.sleep(15)

    # ─── Summary ──────────────────────────────────────────────────
    print("\n\n")
    print("=" * 70)
    print("  FINAL REPORT")
    print("=" * 70)
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    print(f"  PASSED: {passed}/{len(results)}")
    print(f"  FAILED: {failed}/{len(results)}")
    print(f"  SCORE:  {passed/len(results)*100:.0f}%")
    print()
    for r in results:
        icon = "✅" if r["passed"] else "❌"
        print(f"  {icon} Test {r['id']:2d}: {r['name']:30s} | Status: {r['status']:25s} | Time: {r['time']}s")
    print("=" * 70)

    # Write results to JSON for artifact
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("  Results saved to test_results.json")


if __name__ == "__main__":
    main()
