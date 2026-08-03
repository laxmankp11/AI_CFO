import sqlite3
import os
import networkx as nx
from typing import Dict, Any

class BusinessKnowledgeLayer:
    """
    Builds an in-memory knowledge graph of business entities (Customers, Invoices, Payments)
    to perform relational queries that a standard SQL query cannot easily surface 
    (e.g. cascaded risk, payment behavior patterns).
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.DiGraph()
        
    def build_graph(self) -> None:
        """Reads the SQLite database and populates the NetworkX graph."""
        if not os.path.exists(self.db_path):
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 1. Load Customers
            cursor.execute("SELECT id, name FROM customers")
            for row in cursor.fetchall():
                node_id = f"Customer_{row['id']}"
                self.graph.add_node(node_id, type="Customer", name=row['name'], db_id=row['id'])
                
            # 2. Load Invoices
            cursor.execute("SELECT id, customer_id, invoice_number, total_amount, status, issue_date, due_date FROM invoices")
            for row in cursor.fetchall():
                inv_id = f"Invoice_{row['id']}"
                cust_id = f"Customer_{row['customer_id']}"
                
                self.graph.add_node(inv_id, 
                                    type="Invoice", 
                                    number=row['invoice_number'], 
                                    amount=float(row['total_amount']),
                                    status=row['status'],
                                    due_date=row['due_date'])
                
                # Edge: Customer HAS_INVOICE Invoice
                if self.graph.has_node(cust_id):
                    self.graph.add_edge(cust_id, inv_id, relation="HAS_INVOICE")
                    
            # 3. Load Payments
            cursor.execute("SELECT id, invoice_id, amount, payment_date FROM payments")
            for row in cursor.fetchall():
                pay_id = f"Payment_{row['id']}"
                inv_id = f"Invoice_{row['invoice_id']}"
                
                self.graph.add_node(pay_id,
                                    type="Payment",
                                    amount=float(row['amount']),
                                    date=row['payment_date'])
                
                # Edge: Payment PAYS Invoice
                if self.graph.has_node(inv_id):
                    self.graph.add_edge(pay_id, inv_id, relation="PAYS")
                    
            conn.close()
        except sqlite3.Error as e:
            print(f"Error building Knowledge Graph: {e}")
            
    def analyze_customer_risk(self) -> str:
        """
        Analyzes the graph to find total overdue amounts per customer.
        Returns a formatted summary string.
        """
        if self.graph.number_of_nodes() == 0:
            return "Knowledge Graph is empty. No relationship data available."
            
        insights = []
        
        # Find all customers
        customers = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'Customer']
        
        for cust_id in customers:
            cust_name = self.graph.nodes[cust_id].get('name', 'Unknown')
            
            # Find their invoices
            invoices = [v for u, v, d in self.graph.out_edges(cust_id, data=True) if d.get('relation') == 'HAS_INVOICE']
            
            total_outstanding = 0.0
            overdue_count = 0
            
            for inv_id in invoices:
                inv_data = self.graph.nodes[inv_id]
                
                if inv_data.get('status') in ['Sent', 'Overdue', 'Draft']: # Assuming Drafts aren't paid
                    # Calculate how much is paid
                    payments = [u for u, v, d in self.graph.in_edges(inv_id, data=True) if d.get('relation') == 'PAYS']
                    total_paid = sum(self.graph.nodes[p].get('amount', 0.0) for p in payments)
                    
                    balance = inv_data.get('amount', 0.0) - total_paid
                    
                    if balance > 0:
                        total_outstanding += balance
                        if inv_data.get('status') == 'Overdue':
                            overdue_count += 1
                            
            if total_outstanding > 0:
                risk_level = "HIGH" if overdue_count > 0 else "MODERATE"
                insights.append(f"- {cust_name}: ₹{total_outstanding:,.2f} outstanding ({overdue_count} overdue invoices) -> Risk: {risk_level}")
                
        if not insights:
            return "No outstanding customer risk detected in the Knowledge Graph."
            
        return "\n".join(insights)
