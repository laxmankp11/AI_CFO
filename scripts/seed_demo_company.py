import sqlite3
import uuid
import random
from datetime import datetime, timedelta
import os
import sys

workspace_dir = '/Users/apple/Documents/AICFO'

def seed_demo_company(db_path: str):
    """
    Populates a realistic, complete 3-year history for ABC Electronics Pvt Ltd into the target SQLite tenant DB.
    """
    print(f"Seeding Demo Company 'ABC Electronics Pvt Ltd' into {db_path}...")
    
    # If file doesn't exist, create it and copy schema from existing DB if available
    source_db = os.path.join(workspace_dir, 'backend/database/tenant8cb504bc-6c3f-409f-903a-b9afd63730f3')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure tables exist
    if os.path.exists(source_db) and db_path != source_db:
        src_conn = sqlite3.connect(source_db)
        schema = src_conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL;").fetchall()
        for stmt in schema:
            try:
                cursor.execute(stmt[0])
            except Exception as e:
                pass
        src_conn.close()
    
    # Clear existing data to ensure clean seed
    for table in ['journal_lines', 'journal_entries', 'payments', 'invoices', 'purchase_payments', 'purchase_bills', 'customers', 'suppliers', 'accounts']:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except:
            pass
            
    conn.commit()

    # 1. Accounts Setup
    accounts_def = [
        ('1000', 'Cash & Bank Account', 'Asset'),
        ('1100', 'Accounts Receivable', 'Asset'),
        ('1200', 'Inventory Asset', 'Asset'),
        ('2000', 'Accounts Payable', 'Liability'),
        ('2100', 'GST Payable', 'Liability'),
        ('3000', 'Owner Equity', 'Equity'),
        ('4000', 'Sales Revenue', 'Revenue'),
        ('5000', 'Cost of Goods Sold', 'Expense'),
        ('6000', 'Operating & Rent Expense', 'Expense'),
        ('6100', 'Payroll & Salaries Expense', 'Expense')
    ]
    
    acct_map = {}
    for code, name, acct_type in accounts_def:
        aid = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO accounts (id, code, name, type, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (aid, code, name, acct_type))
        acct_map[code] = aid

    # Initial Capital Injection (3 years ago)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 3)
    
    initial_cap = 2500000.0  # ₹25 Lakhs starting capital
    je_cap_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO journal_entries (id, entry_date, narration) VALUES (?, ?, ?)",
                   (je_cap_id, start_date.strftime('%Y-%m-%d'), "Initial Capital Contribution"))
    cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                   (str(uuid.uuid4()), je_cap_id, acct_map['1000'], initial_cap, 0))
    cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                   (str(uuid.uuid4()), je_cap_id, acct_map['3000'], 0, initial_cap))

    # 2. Customers Setup
    customers_data = [
        {"name": "Rahul Technologies", "vip": True, "overdue_amount": 420000},
        {"name": "Acme Corp", "vip": True, "overdue_amount": 0},
        {"name": "Global Solutions", "vip": False, "overdue_amount": 0},
        {"name": "City Electronics", "vip": False, "overdue_amount": 0},
        {"name": "Tech Hub", "vip": True, "overdue_amount": 0},
        {"name": "Apex Retailers", "vip": False, "overdue_amount": 0},
        {"name": "Matrix Systems", "vip": False, "overdue_amount": 0},
        {"name": "Infotech Services", "vip": False, "overdue_amount": 0}
    ]
    
    cust_map = {}
    for c in customers_data:
        cid = str(uuid.uuid4())
        cursor.execute("INSERT INTO customers (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                       (cid, c['name'], start_date.strftime('%Y-%m-%d %H:%M:%S'), start_date.strftime('%Y-%m-%d %H:%M:%S')))
        c['id'] = cid
        cust_map[c['name']] = c

    # 3. Suppliers Setup
    suppliers_data = ["Dell India Pvt Ltd", "HP Enterprise", "Samsung Electronics", "Logitech India", "RealEstate Properties"]
    supp_map = {}
    for sname in suppliers_data:
        sid = str(uuid.uuid4())
        cursor.execute("INSERT INTO suppliers (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                       (sid, sname, start_date.strftime('%Y-%m-%d %H:%M:%S'), start_date.strftime('%Y-%m-%d %H:%M:%S')))
        supp_map[sname] = sid

    # 4. Generate 3 Years of Recurring Transactions & Invoices
    curr_date = start_date
    inv_seq = 1001
    
    while curr_date <= end_date:
        # A. Monthly Fixed Expenses (Rent & Payroll on 1st of every month)
        if curr_date.day == 1:
            # Rent ₹85,000
            rent_je = str(uuid.uuid4())
            cursor.execute("INSERT INTO journal_entries (id, entry_date, narration) VALUES (?, ?, ?)",
                           (rent_je, curr_date.strftime('%Y-%m-%d'), "Monthly Office Rent Payment"))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), rent_je, acct_map['6000'], 85000, 0))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), rent_je, acct_map['1000'], 0, 85000))
                           
            # Payroll ₹2,18,000
            pay_je = str(uuid.uuid4())
            cursor.execute("INSERT INTO journal_entries (id, entry_date, narration) VALUES (?, ?, ?)",
                           (pay_je, curr_date.strftime('%Y-%m-%d'), "Monthly Salaries Payment"))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), pay_je, acct_map['6100'], 218000, 0))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), pay_je, acct_map['1000'], 0, 218000))

        # B. Revenue & Invoices (Generate 3-5 invoices per month)
        if random.random() < 0.15: # ~4-5 times a month
            c = random.choice(customers_data)
            amount = round(random.uniform(75000, 350000), 2)
            
            # Special case for Rahul Technologies overdue invoice if near current date
            if c['name'] == 'Rahul Technologies' and (end_date - curr_date).days < 35 and (end_date - curr_date).days > 15:
                amount = 420000.0
                status = 'Overdue'
                due_date = curr_date + timedelta(days=15)
                is_paid = False
            else:
                due_date = curr_date + timedelta(days=30)
                if (end_date - due_date).days > 0:
                    status = 'Paid'
                    is_paid = True
                else:
                    status = 'Sent'
                    is_paid = False
                    
            inv_id = str(uuid.uuid4())
            inv_num = f"INV-ABC-{inv_seq}"
            inv_seq += 1
            
            cursor.execute("""
                INSERT INTO invoices (id, customer_id, invoice_number, description, total_amount, status, issue_date, due_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (inv_id, c['id'], inv_num, "IT Hardware & Components", amount, status, curr_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), curr_date.strftime('%Y-%m-%d %H:%M:%S'), curr_date.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Invoice Journal Entry (AR Debit, Sales Credit)
            je_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO journal_entries (id, entry_date, narration) VALUES (?, ?, ?)",
                           (je_id, curr_date.strftime('%Y-%m-%d'), f"Invoice {inv_num} issued to {c['name']}"))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), je_id, acct_map['1100'], amount, 0))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), je_id, acct_map['4000'], 0, amount))
                           
            # Payment Entry if Paid
            if is_paid:
                pay_date = curr_date + timedelta(days=random.randint(5, 25))
                if pay_date <= end_date:
                    pay_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO payments (id, invoice_id, amount, payment_date, payment_method, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (pay_id, inv_id, amount, pay_date.strftime('%Y-%m-%d'), 'Bank Transfer', pay_date.strftime('%Y-%m-%d %H:%M:%S'), pay_date.strftime('%Y-%m-%d %H:%M:%S')))
                    
                    je_pay = str(uuid.uuid4())
                    cursor.execute("INSERT INTO journal_entries (id, entry_date, narration) VALUES (?, ?, ?)",
                                   (je_pay, pay_date.strftime('%Y-%m-%d'), f"Payment received for {inv_num}"))
                    cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                                   (str(uuid.uuid4()), je_pay, acct_map['1000'], amount, 0))
                    cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                                   (str(uuid.uuid4()), je_pay, acct_map['1100'], 0, amount))

        curr_date += timedelta(days=1)

    # 5. Final Top-up to set realistic current cash balance (~₹24.8 Lakhs)
    cursor.execute("""
        SELECT SUM(debit_amount) - SUM(credit_amount) 
        FROM journal_lines jl
        JOIN accounts a ON jl.account_id = a.id
        WHERE a.code = '1000'
    """)
    current_cash = cursor.fetchone()[0] or 0.0
    
    target_cash = 2480000.0  # ₹24,80,000 as requested
    diff = target_cash - current_cash
    
    if diff != 0:
        topup_je = str(uuid.uuid4())
        cursor.execute("INSERT INTO journal_entries (id, entry_date, narration) VALUES (?, ?, ?)",
                       (topup_je, end_date.strftime('%Y-%m-%d'), "Opening Balance Cash Adjust"))
        if diff > 0:
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), topup_je, acct_map['1000'], diff, 0))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), topup_je, acct_map['3000'], 0, diff))
        else:
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), topup_je, acct_map['3000'], abs(diff), 0))
            cursor.execute("INSERT INTO journal_lines (id, journal_entry_id, account_id, debit_amount, credit_amount) VALUES (?, ?, ?, ?, ?)",
                           (str(uuid.uuid4()), topup_je, acct_map['1000'], 0, abs(diff)))

    conn.commit()
    conn.close()
    print(f"Successfully seeded ABC Electronics Pvt Ltd into {db_path}!")

if __name__ == "__main__":
    db_paths = [
        os.path.join(workspace_dir, 'backend/database/tenant1.sqlite'),
        os.path.join(workspace_dir, 'backend/database/tenant1'),
        os.path.join(workspace_dir, 'backend/database/tenant8cb504bc-6c3f-409f-903a-b9afd63730f3.sqlite'),
        os.path.join(workspace_dir, 'backend/database/tenant8cb504bc-6c3f-409f-903a-b9afd63730f3'),
        os.path.join(workspace_dir, 'backend/database/tenant7cd53b25-e10a-40c0-9be4-a45925f0fa2c')
    ]
    
    for path in db_paths:
        try:
            seed_demo_company(path)
        except Exception as e:
            print(f"Skipping {path}: {e}")
