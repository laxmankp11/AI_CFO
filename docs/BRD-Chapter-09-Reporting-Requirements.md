# AICFO — Business Requirements Document (BRD)

---

# Chapter 9 – Reporting Requirements

---

## 9.0 Overview

Reporting in AICFO serves two distinct audiences:
1. **Business Owners:** Need high-level, visual, and actionable insights (Dashboards and Summaries).
2. **Accountants/Tax Consultants:** Need detailed, compliant, and exportable financial grids (Ledgers and Statutory Reports).

This chapter defines the standard reports the system MUST generate. All reports MUST be exportable to PDF (for sharing) and CSV/Excel (for further analysis).

---

## 9.1 Financial Reports

These reports are derived directly from the General Ledger and form the core of the accounting system.

| Report Name | Purpose & Audience | Key Data Columns / Elements | Filters & Grouping | Phase |
|:------------|:-------------------|:----------------------------|:-------------------|:------|
| **Trial Balance** | **Purpose:** Verify mathematical accuracy of double-entry books.<br>**Audience:** Accountant | Account Code, Account Name, Debit Balance, Credit Balance.<br>Totals at bottom MUST match. | **Filters:** Date as of (As of Date), Branch.<br>**Grouping:** By Account Group / Sub-group. | [MVP] |
| **Profit & Loss (Income Statement)** | **Purpose:** Show financial performance over a period.<br>**Audience:** Owner, Accountant | Revenue (Sales, Other Income), COGS (if inventory active), Gross Profit, Operating Expenses, Operating Profit, Taxes, Net Profit. | **Filters:** Date Range, Branch, Cost Center.<br>**Grouping:** Monthly comparative, YTD. | [MVP] |
| **Balance Sheet** | **Purpose:** Show financial position at a specific point in time.<br>**Audience:** Owner, Accountant | Assets (Current, Non-Current), Liabilities (Current, Non-Current), Equity (Capital, Retained Earnings). | **Filters:** As of Date, Branch.<br>**Grouping:** Standard Ind AS format. | [MVP] |
| **Cash Flow Statement** | **Purpose:** Show sources and uses of cash.<br>**Audience:** Owner, Accountant | Opening Balance, Operating Activities (Net Cash), Investing Activities, Financing Activities, Closing Balance. | **Filters:** Date Range.<br>**Grouping:** Indirect method standard format. | [P2] |
| **General Ledger Report** | **Purpose:** Detailed transaction history for a specific account.<br>**Audience:** Accountant | Date, Voucher No, Particulars (Contra Account), Narration, Debit Amount, Credit Amount, Running Balance. | **Filters:** Date Range, Account(s). | [MVP] |

---

## 9.2 Tax & Compliance Reports (India)

Reports specifically designed to aid in Indian statutory compliance (GST and TDS).

| Report Name | Purpose & Audience | Key Data Columns / Elements | Filters & Grouping | Phase |
|:------------|:-------------------|:----------------------------|:-------------------|:------|
| **GSTR-1 Summary (Outward Supplies)** | **Purpose:** Data for filing GSTR-1.<br>**Audience:** Accountant, Tax Consultant | B2B Sales (Invoice wise), B2C Large, B2C Small, Credit/Debit Notes, Export Invoices, HSN Summary. | **Filters:** Return Period (Month/Quarter).<br>**Export:** JSON format compatible with GST Offline Tool. | [P3] |
| **GSTR-3B Summary** | **Purpose:** Data for filing monthly tax payment return.<br>**Audience:** Accountant, Tax Consultant | Outward Taxable Supplies (Tax amount), Inward Supplies liable to RCM, Eligible ITC (IGST, CGST, SGST). | **Filters:** Return Period (Month). | [P3] |
| **GST ITC Register** | **Purpose:** Track input tax credit claimed.<br>**Audience:** Accountant | Date, Vendor Name, Vendor GSTIN, Bill No, Taxable Value, CGST, SGST, IGST, Total Tax. | **Filters:** Date Range, Vendor. | [P2] |
| **TDS Deduction Register** | **Purpose:** Track TDS deducted from vendors for Form 26Q filing.<br>**Audience:** Accountant, Tax Consultant | Date, Vendor PAN, Vendor Name, Section (e.g., 194C), Payment Amount, TDS %, TDS Amount, Challan Details (if paid). | **Filters:** Date Range (Quarterly), Section. | [P3] |
| **Fixed Asset Register** | **Purpose:** Track assets and depreciation for Income Tax compliance.<br>**Audience:** Accountant | Asset Name, Date of Purchase, Original Cost, Rate of Dep., Opening WDV, Dep. for the year, Closing WDV. | **Filters:** Financial Year, Asset Class. | [P2] |

---

## 9.3 Operational Reports (Sales, Purchase, Inventory)

Reports designed to help the owner manage day-to-day cash flow and operations.

| Report Name | Purpose & Audience | Key Data Columns / Elements | Filters & Grouping | Phase |
|:------------|:-------------------|:----------------------------|:-------------------|:------|
| **Accounts Receivable (A/R) Aging** | **Purpose:** Track who owes money and for how long.<br>**Audience:** Owner | Customer Name, Total Outstanding, Current, 1-30 Days Overdue, 31-60 Days, 61-90 Days, >90 Days. | **Filters:** As of Date.<br>**Grouping:** By Customer Group / Salesperson. | [MVP] |
| **Accounts Payable (A/P) Aging** | **Purpose:** Track who the business owes money to.<br>**Audience:** Owner | Vendor Name, Total Outstanding, Current, 1-30 Days Overdue, 31-60 Days, 61-90 Days, >90 Days. | **Filters:** As of Date. | [MVP] |
| **Customer Statement of Account** | **Purpose:** Share transaction history with a customer.<br>**Audience:** Customer, Owner | Date, Transaction Type (Invoice, Payment, Credit Note), Reference No, Debit, Credit, Running Balance. | **Filters:** Date Range, Customer. | [P2] |
| **Sales by Item/Category** | **Purpose:** Identify best-selling products or services.<br>**Audience:** Owner | Item Name, Quantity Sold, Average Selling Price, Total Revenue, % of Total Revenue. | **Filters:** Date Range.<br>**Grouping:** By Category. | [MVP] |
| **Expense Analysis** | **Purpose:** Identify areas of high spending.<br>**Audience:** Owner | Expense Category, Total Amount, % of Total Expenses, Comparison vs Previous Period. | **Filters:** Date Range, Branch.<br>**Grouping:** By Expense Sub-group. | [MVP] |
| **Inventory Stock Summary** | **Purpose:** Current stock levels and valuation.<br>**Audience:** Owner | Item Name, SKU, Current Quantity, UOM, Unit Cost, Total Value, Reorder Level. | **Filters:** Warehouse, Category. | [P2] |

---

## 9.4 AI & System Reports

Reports unique to AICFO that track the performance of the AI engine and system usage.

| Report Name | Purpose & Audience | Key Data Columns / Elements | Filters & Grouping | Phase |
|:------------|:-------------------|:----------------------------|:-------------------|:------|
| **AI Confidence & Correction Log** | **Purpose:** Monitor how accurately the AI is performing for this business.<br>**Audience:** Owner, Admin | Date, Original Utterance, AI Extracted Category, Owner Corrected Category, Initial Confidence Score. | **Filters:** Date Range, Correction Type (Category, Vendor, Amount). | [P2] |
| **Audit Log Report** | **Purpose:** Security and compliance tracking of who did what.<br>**Audience:** Owner, Auditor | Timestamp, Actor (User/AI), Action (Create/Update/Delete/Approve), Entity Type (Invoice, Journal), IP Address. | **Filters:** Date Range, User, Entity Type. | [MVP] |

---

*End of Chapter 9 – Reporting Requirements*

*Next: Chapter 10 – Integrations*
