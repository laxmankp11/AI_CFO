import sqlite3
from google import genai
import os
from services.retry_utils import call_with_retry
from services.layer_knowledge import BusinessKnowledgeLayer

class BusinessExperienceLayer:
    def __init__(self, client: genai.Client):
        self.client = client

    def _fetch_financial_summary(self, db_path: str) -> str:
        """Fetches basic financial metrics and knowledge graph insights."""
        if not os.path.exists(db_path):
            return "No financial data available for this business yet."
        
        financial_str = ""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Cash Balance
            cursor.execute("""
                SELECT SUM(debit_amount) - SUM(credit_amount) as balance
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.code = '1000'
            """)
            cash_row = cursor.fetchone()
            cash_balance = cash_row[0] if cash_row and cash_row[0] else 0.0
            
            # Total Income
            cursor.execute("""
                SELECT SUM(credit_amount) - SUM(debit_amount) as revenue
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.type = 'Income'
            """)
            income_row = cursor.fetchone()
            revenue = income_row[0] if income_row and income_row[0] else 0.0
            
            # Total Expense
            cursor.execute("""
                SELECT SUM(debit_amount) - SUM(credit_amount) as expenses
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.type = 'Expense'
            """)
            expense_row = cursor.fetchone()
            expenses = expense_row[0] if expense_row and expense_row[0] else 0.0
            
            # Payables
            cursor.execute("""
                SELECT SUM(credit_amount) - SUM(debit_amount) as payables
                FROM journal_lines jl
                JOIN accounts a ON jl.account_id = a.id
                WHERE a.name LIKE '%Payable%'
            """)
            payable_row = cursor.fetchone()
            payables = payable_row[0] if payable_row and payable_row[0] else 0.0
            
            conn.close()
            
            financial_str = f"""
            FINANCIAL SUMMARY:
            - Current Cash Balance: ₹{cash_balance:,.2f}
            - Total Revenue: ₹{revenue:,.2f}
            - Total Expenses: ₹{expenses:,.2f}
            - Outstanding Payables: ₹{payables:,.2f}
            """
        except Exception as e:
            financial_str = f"Error retrieving financial data: {str(e)}"
            
        # Build Knowledge Graph for deep insights
        graph = BusinessKnowledgeLayer(db_path)
        graph.build_graph()
        graph_insights = graph.analyze_customer_risk()
        
        financial_str += f"\n\nKNOWLEDGE GRAPH INSIGHTS:\n{graph_insights}"
        
        return financial_str

    def narrate_recommendation(self, rec: dict, customer_memory: dict = None) -> str:
        """Takes a structured recommendation from the Recommendation Engine and turns it into CFO-level advice."""
        
        system_prompt = f"""
        You are an expert AI CFO.
        
        You have generated a structured recommendation for the business owner:
        Priority: {rec.get('priority')}
        Category: {rec.get('category')}
        Impact: {rec.get('impact')}
        Reason: {rec.get('reason')}
        Action: {rec.get('action')}
        
        Customer Memory Context (if applicable):
        {customer_memory if customer_memory else "None"}
        
        INSTRUCTIONS:
        1. Write a 2-3 sentence conversational explanation of this recommendation.
        2. Incorporate the Customer Memory (e.g. "Rahul has been a customer for X, but is now Y days late").
        3. Explain WHY this action (e.g. Call Rahul) is important for the impact (e.g. cash flow).
        4. Return ONLY plain text, no markdown, no HTML tags. Keep it punchy and professional.
        """

        def _call():
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=system_prompt,
            )
            return response.text

        return call_with_retry(_call)

    def provide_advice(self, transcript: str, user_context_str: str, db_path: str) -> str:
        """
        Analyzes the user's question. If it's a 'What-If' scenario, runs the ScenarioEngine.
        Otherwise, returns standard financial advice.
        """
        import json
        
        # 1. First LLM call: Intent classification and action extraction
        extraction_prompt = f"""
        Analyze the following query: "{transcript}"
        
        Is this a "What-If" scenario simulation? (e.g., "What if sales drop 20%", "What if I hire 2 developers")
        If YES, return a JSON array of actions.
        Available action types: "IncreaseSales", "DecreaseSales", "HireEmployee", "IncreaseMarketing"
        
        Example outputs:
        [{{\"type\": \"DecreaseSales\", \"value\": 20}}]
        [{{\"type\": \"HireEmployee\", \"salary\": 80000, \"count\": 2}}]
        
        If NO, return exactly "NO_SCENARIO".
        """
        
        def _extract():
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=extraction_prompt,
            )
            return response.text.strip().replace('```json', '').replace('```', '')

        extraction_result = call_with_retry(_extract)
        
        if extraction_result != "NO_SCENARIO":
            try:
                actions = json.loads(extraction_result)
                
                # Run Decision Engine
                from services.layer_intelligence import BusinessIntelligenceLayer
                from services.layer_decision import ForecastEngine, ScenarioEngine, DecisionEngine
                
                bi = BusinessIntelligenceLayer(db_path)
                forecast = ForecastEngine(bi)
                scenario = ScenarioEngine(forecast)
                decision_engine = DecisionEngine(scenario)
                
                # We simulate 3 months ahead for decision making
                decision_result = decision_engine.evaluate_decision(actions, months_ahead=3)
                sim_result = decision_result["simulation_data"]
                
                # 2. Second LLM call: Narrate the decision result
                sim_prompt = f"""
                You are an expert AI CFO.
                The user asked: "{transcript}"
                
                You ran a financial simulation and generated a structured decision.
                
                Decision: {decision_result['decision']}
                Confidence: {decision_result['confidence']}%
                Risk Level: {decision_result['risk']}
                Reason: {decision_result['reason']}
                Alternatives: {", ".join(decision_result['alternatives']) if decision_result['alternatives'] else "None"}
                
                Simulated Math Impact (after 3 months):
                Cash Impact: ₹{sim_result['delta']['cash']:,.2f}
                Profit Impact: ₹{sim_result['delta']['profit']:,.2f}
                
                INSTRUCTIONS:
                Write a concise, professional CFO response explaining the decision. 
                Crucially, append an "Explainability Block" at the end of your response to build trust.
                
                Structure your output as follows:
                <p>Hiring two developers is [Decision]. [Reason] Your cash will drop by [Cash Impact], but it remains above minimum reserve.</p>
                <div style="background: rgba(0,0,0,0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.9em;">
                    <strong>Explainability Report</strong>
                    <ul>
                        <li><strong>Why?</strong> [Reasoning for decision]</li>
                        <li><strong>Data Used:</strong> Current cash buffer vs simulated drop of [Cash Impact].</li>
                        <li><strong>Assumptions:</strong> Operating costs remain constant.</li>
                        <li><strong>Confidence:</strong> {decision_result['confidence']}%</li>
                        <li><strong>Alternatives:</strong> [Alternative]</li>
                    </ul>
                </div>
                
                Format using HTML (<strong>, <ul>, <p>, <div>). Do not use markdown.
                """
                
                def _narrate_sim():
                    return self.client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=sim_prompt,
                    ).text
                    
                return call_with_retry(_narrate_sim)
            except Exception as e:
                print(f"Scenario parsing error: {e}")
                
        # Standard Advice fallback
        financial_data = self._fetch_financial_summary(db_path)
        system_prompt = f"""
        You are an expert AI CFO providing strategic business advice.
        
        USER CONTEXT:
        {user_context_str}

        LIVE FINANCIAL DATA:
        {financial_data}
        
        INSTRUCTIONS:
        1. Analyze the user's question ("{transcript}").
        2. Give professional, objective advice based ONLY on the Live Financial Data.
        3. Format your response using HTML (<strong>, <ul>, etc.). Do NOT use markdown.
        4. Give a definitive conclusion.
        """

        def _call_std():
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=system_prompt,
            )
            return response.text

        return call_with_retry(_call_std)
