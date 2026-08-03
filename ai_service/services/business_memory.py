from services.layer_knowledge import BusinessKnowledgeLayer
from datetime import datetime

class BusinessMemory:
    """
    Business Memory Layer: Interprets nodes and edges from the Knowledge Graph
    to store/calculate historical behavioral profiles (Customer Memory, Vendor Memory).
    """
    
    def __init__(self, graph: BusinessKnowledgeLayer):
        self.graph = graph
        self.customer_memory = {}
        
    def build_memories(self):
        """Processes the graph to extract behavioral metrics."""
        if not self.graph or self.graph.graph.number_of_nodes() == 0:
            return
            
        customers = [n for n, attr in self.graph.graph.nodes(data=True) if attr.get('type') == 'Customer']
        
        for cust_id in customers:
            name = self.graph.graph.nodes[cust_id].get('name')
            invoices = [v for u, v, d in self.graph.graph.out_edges(cust_id, data=True) if d.get('relation') == 'HAS_INVOICE']
            
            total_ltv = 0.0
            total_delay_days = 0
            delay_count = 0
            
            for inv_id in invoices:
                inv_node = self.graph.graph.nodes[inv_id]
                due_date_str = inv_node.get('due_date')
                if not due_date_str:
                    continue
                    
                # Get payments for this invoice
                payments = [u for u, v, d in self.graph.graph.in_edges(inv_id, data=True) if d.get('relation') == 'PAYS']
                
                for pay_id in payments:
                    pay_node = self.graph.graph.nodes[pay_id]
                    amount = pay_node.get('amount', 0.0)
                    total_ltv += amount
                    
                    pay_date_str = pay_node.get('date')
                    if pay_date_str:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                        pay_date = datetime.strptime(pay_date_str, "%Y-%m-%d")
                        diff = (pay_date - due_date).days
                        
                        # Even if paid early (negative), we track it, but usually we care about delay
                        total_delay_days += max(0, diff) 
                        delay_count += 1
                        
            avg_delay = (total_delay_days / delay_count) if delay_count > 0 else 0
            
            self.customer_memory[cust_id] = {
                "name": name,
                "lifetime_value": total_ltv,
                "average_payment_delay": avg_delay,
                "risk_profile": "High" if avg_delay > 15 else ("Moderate" if avg_delay > 5 else "Low")
            }
            
    def get_customer_memory(self, cust_id: str) -> dict:
        return self.customer_memory.get(cust_id, {})
        
    def get_all_customer_memories(self) -> dict:
        return self.customer_memory
