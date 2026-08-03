import sqlite3
import re
from typing import Dict, List, Any

class MemoryEngine:
    """
    Active Memory & Knowledge Graph Engine.
    Instead of passing passive lists, this engine actively fetches relationship sub-graphs
    based on entities detected in the prompt (e.g. Customer -> Invoices -> Payments).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def enrich_context(self, prompt: str) -> str:
        """Analyze the prompt, fetch relevant sub-graphs, and return an enriched context string."""
        if not self.db_path or self.db_path == ":memory:" or not self.db_path.endswith(".sqlite"):
            return "Active Memory: No persistent database connected."

        # Extremely simple entity extraction: words starting with capital letters
        words = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        potential_entities = list(set([w for w in words if len(w) > 2]))

        if not potential_entities:
            return "Active Memory: No explicit entities detected."

        knowledge_graph_lines = []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. Check Customers
            for entity in potential_entities:
                cursor.execute("SELECT * FROM customers WHERE name LIKE ? LIMIT 1", (f"%{entity}%",))
                customer = cursor.fetchone()
                if customer:
                    c_id = customer['id']
                    c_name = customer['name']
                    
                    # Fetch Invoices for this customer
                    cursor.execute("SELECT invoice_number, total_amount, status FROM invoices WHERE customer_id = ? AND status != 'Paid' LIMIT 5", (c_id,))
                    invoices = cursor.fetchall()
                    
                    if invoices:
                        inv_details = ", ".join([f"{row['invoice_number']} (₹{row['total_amount']:,.2f} - {row['status']})" for row in invoices])
                        knowledge_graph_lines.append(f"➔ CUSTOMER MATCH: '{c_name}' has pending invoices: {inv_details}")
                    else:
                        knowledge_graph_lines.append(f"➔ CUSTOMER MATCH: '{c_name}' has no pending invoices.")

            # 2. Check Suppliers
            for entity in potential_entities:
                cursor.execute("SELECT * FROM suppliers WHERE name LIKE ? LIMIT 1", (f"%{entity}%",))
                supplier = cursor.fetchone()
                if supplier:
                    s_id = supplier['id']
                    s_name = supplier['name']
                    
                    # Fetch Bills for this supplier
                    # (Assuming purchase_bills table exists with similar structure)
                    try:
                        cursor.execute("SELECT bill_number, total_amount, status FROM purchase_bills WHERE supplier_id = ? AND status != 'Paid' LIMIT 5", (s_id,))
                        bills = cursor.fetchall()
                        if bills:
                            bill_details = ", ".join([f"{row['bill_number']} (₹{row['total_amount']:,.2f} - {row['status']})" for row in bills])
                            knowledge_graph_lines.append(f"➔ SUPPLIER MATCH: '{s_name}' has pending bills: {bill_details}")
                        else:
                            knowledge_graph_lines.append(f"➔ SUPPLIER MATCH: '{s_name}' has no pending bills.")
                    except sqlite3.OperationalError:
                        knowledge_graph_lines.append(f"➔ SUPPLIER MATCH: '{s_name}'.")

            conn.close()
        except Exception as e:
            print(f"Memory Engine Error: {e}")
            return f"Active Memory: Error retrieving graph - {e}"

        if not knowledge_graph_lines:
            return "Active Memory: Entities detected, but no historical relationships found in database."

        graph_str = "\n".join(knowledge_graph_lines)
        return f"ACTIVE KNOWLEDGE GRAPH (Relationships Pre-Fetched):\n{graph_str}\n\nIMPORTANT: Use these pre-fetched relationships to accurately map IDs and resolve vague references (e.g., 'Pay Rahul' refers to the invoices listed above)."
