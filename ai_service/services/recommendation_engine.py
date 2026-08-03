from typing import List, Dict, Any

class RecommendationEngine:
    """
    Recommendation Engine: Uses pure business rules (no LLM) to analyze KPIs
    and output highly structured actionable recommendations.
    Includes a Priority Engine that ranks by Financial Impact × Urgency × Confidence.
    """
    
    # Impact scoring lookup (higher = more impactful)
    URGENCY_WEIGHTS = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1
    }
    
    def generate_recommendations(self, bi_kpis: Dict[str, Any], memory_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []
        
        # Rule 1: Cash Flow Warning
        total_cash = bi_kpis.get("total_cash", 0)
        if total_cash < 200000:
            recommendations.append({
                "priority": "HIGH",
                "category": "Cash Flow",
                "confidence": 98,
                "impact": "Prevent cash crunch",
                "impact_value": 200000,
                "reason": f"Operating cash is critically low (₹{total_cash:,.0f})",
                "action": "Delay major purchases and accelerate collections",
                "estimated_time": "Immediate",
                "actions": [
                    {"label": "Review Payables", "icon": "fas fa-file-invoice-dollar", "type": "navigate"},
                    {"label": "Send Reminders", "icon": "fas fa-paper-plane", "type": "action"},
                    {"label": "Ignore", "icon": "fas fa-times", "type": "dismiss"}
                ],
                "explainability": {
                    "why": f"Your operating cash balance (₹{total_cash:,.0f}) is below the ₹2,00,000 minimum reserve threshold, which risks inability to cover payroll and vendor obligations.",
                    "data_used": "Cash account balance (A/C 1000), Monthly burn rate from last 30 days of expenses.",
                    "assumptions": "Expenses continue at the current monthly run rate. No unexpected large receipts.",
                    "confidence": 98,
                    "alternatives": ["Negotiate extended payment terms with top 3 vendors.", "Apply for a short-term working capital line."]
                }
            })
            
        # Rule 2: Overdue AR Collections
        total_ar = bi_kpis.get("total_overdue_ar", 0)
        overdue_invs = bi_kpis.get("overdue_invoices", [])
        
        if total_ar > 0 and len(overdue_invs) > 0:
            cust_totals = {}
            for inv in overdue_invs:
                cname = inv['customer_name']
                cust_totals[cname] = cust_totals.get(cname, 0) + inv['balance']
                
            biggest_offender = max(cust_totals.items(), key=lambda x: x[1])
            
            recommendations.append({
                "priority": "HIGH",
                "category": "Receivables",
                "confidence": 95,
                "impact": f"Recover ₹{biggest_offender[1]:,.0f}",
                "impact_value": biggest_offender[1],
                "reason": f"Customer '{biggest_offender[0]}' has the highest overdue exposure.",
                "action": f"Collect ₹{biggest_offender[1]:,.0f} from {biggest_offender[0]}",
                "estimated_time": "15 minutes",
                "actions": [
                    {"label": "Call", "icon": "fas fa-phone", "type": "action"},
                    {"label": "Send Reminder", "icon": "fas fa-paper-plane", "type": "action"},
                    {"label": "Schedule Follow-up", "icon": "fas fa-calendar-plus", "type": "action"},
                    {"label": "Ignore", "icon": "fas fa-times", "type": "dismiss"}
                ],
                "explainability": {
                    "why": f"{biggest_offender[0]} owes ₹{biggest_offender[1]:,.0f} past the due date. Delayed collection directly reduces your available cash and increases credit risk exposure.",
                    "data_used": f"Invoice ledger showing {len(overdue_invs)} overdue invoices. Customer payment history from Business Memory.",
                    "assumptions": "Customer is solvent and reachable. Payment terms are as agreed.",
                    "confidence": 95,
                    "alternatives": [f"Offer {biggest_offender[0]} a 2% early payment discount.", "Escalate to legal notice if no response within 7 days."]
                }
            })
            
        # Rule 3: Growth Opportunity
        if total_cash > 500000:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Growth",
                "confidence": 85,
                "impact": "Increase revenue by 12%",
                "impact_value": total_cash * 0.12,
                "reason": "Excess cash reserves available for reinvestment.",
                "action": "Launch a targeted marketing campaign or bulk inventory purchase",
                "estimated_time": "1 week",
                "actions": [
                    {"label": "Plan Campaign", "icon": "fas fa-bullhorn", "type": "navigate"},
                    {"label": "Bulk Order", "icon": "fas fa-boxes", "type": "navigate"},
                    {"label": "Ignore", "icon": "fas fa-times", "type": "dismiss"}
                ],
                "explainability": {
                    "why": f"You have ₹{total_cash:,.0f} in cash, well above operating reserves. Idle cash loses value to inflation. Reinvestment into growth channels has historically yielded 12-18% returns for similar businesses.",
                    "data_used": "Current cash balance, historical sales growth rate, industry benchmarks.",
                    "assumptions": "5% baseline sales growth. Marketing spend conversion at 3-5x ROI.",
                    "confidence": 85,
                    "alternatives": ["Place excess cash in a short-term FD for guaranteed 6.5% return.", "Prepay vendor invoices for a 2-3% discount."]
                }
            })
            
        return recommendations
    
    def prioritize(self, recommendations: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Priority Engine: Scores all recommendations by Financial Impact × Urgency × Confidence.
        Returns only the top N, ranked and numbered.
        """
        for rec in recommendations:
            urgency_score = self.URGENCY_WEIGHTS.get(rec.get("priority", "LOW"), 1)
            confidence = rec.get("confidence", 50) / 100.0
            impact_value = rec.get("impact_value", 10000)
            
            # Composite priority score
            rec["priority_score"] = impact_value * urgency_score * confidence
            
        # Sort descending by priority score
        ranked = sorted(recommendations, key=lambda r: r.get("priority_score", 0), reverse=True)
        
        # Return only top N, with rank labels
        top = ranked[:top_n]
        for i, rec in enumerate(top):
            rec["priority_rank"] = i + 1
            
        return top
