# AICFO — Business Requirements Document (BRD)

---

# Chapter 6 – Functional Requirements

---

## 6.0 Overview

This chapter translates the broad business capabilities (Chapter 4) and business processes (Chapter 5) into specific, testable functional requirements. Each requirement defines *what* the system must do to support the business needs.

### Requirement Attributes

| Attribute | Description |
|:----------|:------------|
| **Req ID** | Unique identifier (e.g., FR-CORE-001) |
| **Description** | A clear statement of the system's required behavior |
| **Phase** | Release phase (MVP, P2, P3, P4) |
| **Acceptance Criteria** | Conditions that must be met for the requirement to be considered complete |

---

## 6.1 Core Business Requirements

| Req ID | Description | Phase | Acceptance Criteria |
|:-------|:------------|:------|:--------------------|
| **FR-CORE-001** | The system MUST allow a Super Admin to create a new Tenant Business profile with legal name, trade name, business type, PAN, GSTIN, address, and industry. | MVP | 1. Tenant is created with unique ID.<br>2. Tenant data is isolated from other tenants.<br>3. GSTIN format is validated. |
| **FR-CORE-002** | The system MUST allow a User to be associated with multiple Tenant Businesses. | MVP | 1. User logs in once.<br>2. User can select active business from a dropdown.<br>3. Switching business changes context immediately. |
| **FR-CORE-003** | The system MUST support Role-Based Access Control (RBAC) with predefined roles: Business Owner, Accountant, Employee, Tax Consultant, Support. | MVP | 1. Roles restrict UI visibility and API access as per Chapter 3 matrix.<br>2. Business Owner can invite new users and assign roles. |
| **FR-CORE-004** | The system MUST define Financial Years (e.g., Apr 1 - Mar 31) for each Tenant Business. | MVP | 1. System defaults to Indian FY.<br>2. Transactions outside active FY are blocked or routed to correct FY ledger. |
| **FR-CORE-005** | The system MUST log an immutable Audit Trail entry for every create, update, delete, and approve action affecting financial data or settings. | MVP | 1. Log contains: Timestamp, User ID (or AI), Action, Entity, Before/After state.<br>2. Logs cannot be edited or deleted by any user, including Super Admin. |
| **FR-CORE-006** | The system MUST allow the Business Owner or Accountant to lock a Financial Period (month or year). | MVP | 1. Locked periods prevent new journal entries or edits to existing entries dated within that period. |
| **FR-CORE-007** | The system MUST allow a User to authenticate via Email/Password and Mobile OTP. | MVP | 1. Passwords are encrypted.<br>2. OTPs expire after 5 minutes.<br>3. Session timeouts are enforced. |
| **FR-CORE-008** | The system MUST support multiple Branches per Business, each with its own optional GSTIN. | P2 | 1. Branches can be created and deactivated.<br>2. Transactions can be tagged to specific branches. |

---

## 6.2 Finance Requirements

| Req ID | Description | Phase | Acceptance Criteria |
|:-------|:------------|:------|:--------------------|
| **FR-FIN-001** | The system MUST provide a multi-level hierarchical Chart of Accounts (COA) for each business. | MVP | 1. Supports 5 core types: Assets, Liabilities, Equity, Income, Expenses.<br>2. Supports groups and sub-groups.<br>3. System provides default COA templates upon setup. |
| **FR-FIN-002** | The system MUST allow users to manually create double-entry Journal Vouchers. | MVP | 1. Form includes: Date, Narration, Debit line(s), Credit line(s).<br>2. Total debits MUST equal total credits to save. |
| **FR-FIN-003** | The system MUST generate a General Ledger showing chronological entries and running balance for any account. | MVP | 1. Ledger can be filtered by date range.<br>2. Closing balance is calculated accurately based on account type (Dr/Cr normal balance). |
| **FR-FIN-004** | The system MUST generate a Trial Balance report. | MVP | 1. Lists all active accounts with non-zero balances.<br>2. Total Debit column equals Total Credit column. |
| **FR-FIN-005** | The system MUST generate a Profit & Loss Statement and Balance Sheet. | MVP | 1. Reports are generated in real-time from ledger data.<br>2. Net Profit from P&L flows correctly into Retained Earnings on the Balance Sheet. |
| **FR-FIN-006** | The system MUST calculate GST Input Tax Credit (ITC) and Output Tax Liability based on transactional data. | MVP | 1. GST entries are posted to dedicated CGST/SGST/IGST Input and Output accounts.<br>2. GST summary matches ledger balances. |
| **FR-FIN-007** | The system MUST allow the entry of Opening Balances for accounts when starting mid-year. | MVP | 1. Imbalanced opening entries are posted against an 'Opening Balance Equity' account to ensure Trial Balance integrity. |
| **FR-FIN-008** | The system MUST support Bank Reconciliation by allowing users to match ledger entries against uploaded bank statement data. | P2 | 1. Uploads CSV/Excel bank statements.<br>2. Marks ledger entries as 'Reconciled'.<br>3. Generates Reconciliation Statement report. |
| **FR-FIN-009** | The system MUST maintain a Fixed Asset Register and generate automatic monthly depreciation entries. | P2 | 1. Calculates straight-line or WDV depreciation.<br>2. Posts Journal Entry automatically on the last day of the month. |

---

## 6.3 Sales Requirements

| Req ID | Description | Phase | Acceptance Criteria |
|:-------|:------------|:------|:--------------------|
| **FR-SALE-001** | The system MUST maintain a Customer directory. | MVP | 1. Stores Name, GSTIN, Address, Contact Info.<br>2. Prevents deletion of customers with linked transactions (soft archive only). |
| **FR-SALE-002** | The system MUST allow generation of GST-compliant Sales Invoices. | MVP | 1. Auto-generates sequential invoice numbers.<br>2. Calculates CGST/SGST or IGST based on Place of Supply (Business State vs Customer State).<br>3. Generates PDF output. |
| **FR-SALE-003** | The system MUST automatically create corresponding Journal Entries when a Sales Invoice is finalized. | MVP | 1. Dr Accounts Receivable.<br>2. Cr Sales Revenue.<br>3. Cr GST Output Tax. |
| **FR-SALE-004** | The system MUST allow recording of Payment Receipts against specific Invoices. | MVP | 1. Updates invoice status to 'Partially Paid' or 'Paid'.<br>2. Creates Journal Entry (Dr Bank/Cash, Cr Accounts Receivable). |
| **FR-SALE-005** | The system MUST generate an Accounts Receivable Aging report. | MVP | 1. Groups outstanding invoices by age (0-30, 31-60, 61-90, >90 days). |
| **FR-SALE-006** | The system MUST allow creation of Credit Notes linked to specific Sales Invoices. | P2 | 1. Cannot exceed original invoice amount.<br>2. Creates reversing Journal Entries for revenue and GST output. |
| **FR-SALE-007** | The system MUST generate E-Invoices (IRN and QR Code) via GSTN portal integration. | P3 | 1. Sends payload to IRP.<br>2. Receives and embeds IRN and QR code on the invoice PDF. |

---

## 6.4 Purchase Requirements

| Req ID | Description | Phase | Acceptance Criteria |
|:-------|:------------|:------|:--------------------|
| **FR-PUR-001** | The system MUST maintain a Vendor (Supplier) directory. | MVP | 1. Stores Name, GSTIN, PAN, Address.<br>2. Tracks TDS applicability. |
| **FR-PUR-002** | The system MUST allow recording of Vendor Bills (Purchase Invoices). | MVP | 1. Captures vendor invoice number and date.<br>2. Calculates GST ITC based on line items and vendor GSTIN. |
| **FR-PUR-003** | The system MUST automatically create corresponding Journal Entries when a Vendor Bill is finalized. | MVP | 1. Dr Expense/Asset.<br>2. Dr GST Input Tax.<br>3. Cr Accounts Payable. |
| **FR-PUR-004** | The system MUST allow recording of Vendor Payments and application to specific bills. | MVP | 1. Creates Journal Entry (Dr Accounts Payable, Cr Bank/Cash). |
| **FR-PUR-005** | The system MUST calculate and record Tax Deducted at Source (TDS) on vendor payments when applicable thresholds are met. | P3 | 1. Applies correct section rate (e.g., 194C, 194J).<br>2. Creates Journal Entry (Cr TDS Payable). |
| **FR-PUR-006** | The system MUST generate an Accounts Payable Aging report. | MVP | 1. Groups outstanding bills by age. |

---

## 6.5 Inventory Requirements

| Req ID | Description | Phase | Acceptance Criteria |
|:-------|:------------|:------|:--------------------|
| **FR-INV-001** | The system MUST maintain a Product/Service catalog. | P2 | 1. Stores Name, SKU, Type (Good/Service), Selling Price, Purchase Price, HSN/SAC code, Default GST rate. |
| **FR-INV-002** | The system MUST track stock quantities across multiple Warehouses. | P2 | 1. Auto-decreases stock on Sales Invoice.<br>2. Auto-increases stock on Purchase Bill. |
| **FR-INV-003** | The system MUST calculate inventory valuation. | P2 | 1. Supports FIFO or Weighted Average Cost.<br>2. Calculates Cost of Goods Sold (COGS) dynamically for P&L. |
| **FR-INV-004** | The system MUST support manual Stock Adjustments. | P2 | 1. Allows quantity corrections with reason.<br>2. Creates Journal Entry for inventory write-off if value decreases. |

---

## 6.6 HR & Payroll Requirements

| Req ID | Description | Phase | Acceptance Criteria |
|:-------|:------------|:------|:--------------------|
| **FR-HR-001** | The system MUST maintain Employee profiles. | P3 | 1. Stores personal details, PAN, salary structure, bank details. |
| **FR-HR-002** | The system MUST allow employees to submit Expense Reimbursement claims. | P3 | 1. Supports receipt upload.<br>2. Routes to Manager/Owner for approval. |
| **FR-HR-003** | The system MUST process monthly Payroll. | P3 | 1. Calculates Gross Pay.<br>2. Calculates statutory deductions (PF, ESI, TDS, PT).<br>3. Calculates Net Pay.<br>4. Generates bulk Journal Entry for salary expenses and liabilities. |
| **FR-HR-004** | The system MUST generate individual employee Payslips (PDF). | P3 | 1. Details earnings, deductions, net pay, and YTD figures. |

---

*Note: Requirements for the **AI Engine**, **Communication**, and **Analytics** modules are covered in their respective dedicated chapters (Chapter 7, 9, 11) to allow for deeper exploration of prompts, templates, and visualization logic.*

---

*End of Chapter 6 – Functional Requirements*

*Next: Chapter 7 – Business Rules & Logic*
