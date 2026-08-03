import sqlite3
from google import genai
import os
from services.retry_utils import call_with_retry

class ReportingAgent:
    def __init__(self, client: genai.Client):
        self.client = client

    def _fetch_financial_summary(self, db_path: str) -> str:
        """Fetches basic financial metrics from the database."""
        if not os.path.exists(db_path):
            return "No financial data available for this business yet."
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Cash Balance (Sum of debits - Sum of credits for account code 1000)
            cursor.execute("""
                SELECT SUM(debit_amount) - SUM(credit_amount) as balance
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.code = '1000'
            """)
            cash_row = cursor.fetchone()
            cash_balance = cash_row[0] if cash_row and cash_row[0] else 0.0
            
            # Total Income (Sum of credits - Sum of debits for Income accounts)
            cursor.execute("""
                SELECT SUM(credit_amount) - SUM(debit_amount) as revenue
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.type = 'Income'
            """)
            income_row = cursor.fetchone()
            revenue = income_row[0] if income_row and income_row[0] else 0.0
            
            # Total Expense (Sum of debits - Sum of credits for Expense accounts)
            cursor.execute("""
                SELECT SUM(debit_amount) - SUM(credit_amount) as expenses
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.type = 'Expense'
            """)
            expense_row = cursor.fetchone()
            expenses = expense_row[0] if expense_row and expense_row[0] else 0.0
            
            conn.close()
            
            return f"""
            FINANCIAL SUMMARY:
            - Current Cash Balance: ₹{cash_balance:,.2f}
            - Total Revenue: ₹{revenue:,.2f}
            - Total Expenses: ₹{expenses:,.2f}
            - Net Profit: ₹{(revenue - expenses):,.2f}
            """
        except Exception as e:
            return f"Error retrieving financial data: {str(e)}"

    def generate_report(self, transcript: str, user_context_str: str, db_path: str) -> str:
        financial_data = self._fetch_financial_summary(db_path)
        
        system_prompt = f"""
        You are an expert AI CFO and Financial Analyst. Your job is to answer the user's business intelligence or reporting query.
        
        USER CONTEXT:
        {user_context_str}

        LIVE FINANCIAL DATA:
        {financial_data}
        
        INSTRUCTIONS:
        1. Answer the user's query ("{transcript}") directly using the Live Financial Data provided.
        2. Format your response beautifully using HTML. Use bolding (<strong>), bullet points (<ul><li>), and highlighting for numbers to make it look like an Executive Summary. 
        3. Do NOT use markdown. Return ONLY raw HTML that can be injected into a <div>.
        4. If the user asks for data that is not present in the LIVE FINANCIAL DATA, politely explain that you only have access to the high-level summary at the moment.
        """

        def _call():
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=system_prompt,
            )
            return response.text

        return call_with_retry(_call)
