from typing import Dict, Any, List

class FinancialModel:
    """
    The Mathematical Heart of the AI Platform.
    Holds baseline inputs (current cash, monthly revenue run-rate) and 
    calculates P&L, Cash Flow, and Ratios based on applied modifiers.
    """
    
    def __init__(self, current_cash: float, current_monthly_revenue: float, current_monthly_expenses: float):
        self.baseline_cash = current_cash
        self.baseline_revenue = current_monthly_revenue
        self.baseline_expenses = current_monthly_expenses
        self.tax_rate = 0.18 # GST
        
    def run_projection(self, months: int = 1, modifiers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Projects financials forward by `months`. 
        `modifiers` allow What-If engines to alter the run-rate dynamically.
        """
        if modifiers is None:
            modifiers = []
            
        proj_revenue = self.baseline_revenue
        proj_expenses = self.baseline_expenses
        
        # Apply modifiers (e.g. from ScenarioEngine)
        for mod in modifiers:
            if mod["type"] == "IncreaseSales":
                # Value is percentage (e.g. 20 for 20%)
                proj_revenue *= (1 + (mod["value"] / 100.0))
            elif mod["type"] == "DecreaseSales":
                proj_revenue *= (1 - (mod["value"] / 100.0))
            elif mod["type"] == "HireEmployee":
                # Add salary * count to monthly expenses
                proj_expenses += (mod["salary"] * mod.get("count", 1))
            elif mod["type"] == "IncreaseMarketing":
                proj_expenses += mod["amount"]
                
        # Calculate 1-month snapshot
        proj_profit = proj_revenue - proj_expenses
        proj_gst = proj_revenue * self.tax_rate
        
        # Simple Cash Flow: Assume all revenue collected and expenses paid
        proj_cash = self.baseline_cash + (proj_profit * months) - (proj_gst * months)
        
        # Calculate Risk purely mathematically
        risk = "Low"
        if proj_cash < 0:
            risk = "Critical"
        elif proj_cash < (proj_expenses * 1.5): # Less than 1.5 months operating runway
            risk = "High"
        elif proj_cash < (proj_expenses * 3):
            risk = "Medium"
            
        return {
            "projected_revenue": proj_revenue * months,
            "projected_expenses": proj_expenses * months,
            "projected_profit": proj_profit * months,
            "projected_gst": proj_gst * months,
            "projected_cash": proj_cash,
            "risk_level": risk
        }
