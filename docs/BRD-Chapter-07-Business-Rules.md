# AICFO — Business Requirements Document (BRD)

---

# Chapter 7 – Business Rules

---

## 7.0 Overview

Business rules define the strict constraints, logic, and conditions that the AICFO system MUST enforce at all times, regardless of how data enters the system (via AI voice, manual entry, OCR, or API). If a transaction or action violates a business rule, the system MUST reject it or route it to a human for intervention.

This chapter categorizes rules into three domains:
1. **Fundamental Accounting Rules** (Universal constraints)
2. **Indian Compliance & Tax Rules** (GST, TDS, Legal)
3. **AI & Automation Rules** (Confidence thresholds, auto-posting logic)

---

## 7.1 Fundamental Accounting Rules

These rules ensure the integrity of the financial data. They are non-negotiable and cannot be overridden by any user, including the Super Admin.

| Rule ID | Rule Description | System Enforcement |
|:--------|:-----------------|:-------------------|
| **RULE-ACC-001** | **The Accounting Equation:** Total Assets MUST always equal Total Liabilities + Total Equity. | Implicitly enforced by double-entry bookkeeping (RULE-ACC-002). Verified dynamically during Balance Sheet generation. |
| **RULE-ACC-002** | **Double-Entry Balance:** Every Journal Entry MUST have at least one debit line and at least one credit line. The sum of all debit amounts MUST exactly equal the sum of all credit amounts. | Database transaction level. The system MUST throw an error and rollback if an imbalanced entry is attempted. |
| **RULE-ACC-003** | **Immutability of Posted Entries:** Once a Journal Entry is posted to the ledger, its core financial data (Account, Amount, Date, Dr/Cr) MUST NOT be altered or deleted. | To correct an error, the system MUST create a new reversing journal entry linked to the original, preserving the audit trail. |
| **RULE-ACC-004** | **Period Locking:** No user (including Business Owner) can create, reverse, or modify transactions dated within a 'Locked' financial period. | Application layer check against the `period_locks` table. Only a user with 'Accountant' role can unlock a period, which is logged in the audit trail. |
| **RULE-ACC-005** | **No Negative Cash/Bank Balances (Configurable):** By default, Cash and Bank accounts MUST NOT have a credit (negative) balance unless explicitly allowed (e.g., overdraft facility). | The system issues a warning if a transaction causes a cash/bank account to go negative. The Business Owner can configure this from Warning to Hard Block. |
| **RULE-ACC-006** | **Rounding Precision:** All monetary amounts MUST be stored and calculated to exactly 2 decimal places (paisa). | Half-round up strategy applied consistently (e.g., ₹10.455 becomes ₹10.46). |
| **RULE-ACC-007** | **Continuous Financial Years:** Financial years MUST NOT overlap and MUST NOT have gaps between them. | Validation applied during Financial Year creation. |

---

## 7.2 Indian Compliance & Tax Rules

These rules enforce compliance with Indian taxation laws (GST and Income Tax Act).

| Rule ID | Rule Description | System Enforcement |
|:--------|:-----------------|:-------------------|
| **RULE-TAX-001** | **GST Place of Supply (Sales):** If the Customer's billing state is the SAME as the Business's registered state, the system MUST apply CGST + SGST (split equally). If the states differ, the system MUST apply IGST. | Applied automatically during Sales Invoice creation based on Customer master data and Business profile. |
| **RULE-TAX-002** | **GST Input Tax Credit (ITC) Eligibility:** The system MUST NOT claim ITC on purchase bills if the Vendor does not have a valid, system-verified GSTIN. | If vendor GSTIN is blank or invalid, GST amounts paid are added to the expense/asset cost, not to the GST Input Account. |
| **RULE-TAX-003** | **Valid GSTIN Format:** Any GSTIN entered (for Business, Customer, or Vendor) MUST pass the standard Indian GSTIN regex validation (15 alphanumeric characters, specific structure). | Form validation on UI and API level. |
| **RULE-TAX-004** | **Mandatory HSN/SAC:** Every line item on a Sales Invoice MUST have a valid 4, 6, or 8-digit HSN (goods) or SAC (services) code. | Prevent invoice finalization if HSN/SAC is missing. |
| **RULE-TAX-005** | **E-Invoicing Threshold:** If the Business profile is marked as 'E-Invoicing Applicable', the system MUST NOT allow printing/sending of an invoice without generating an IRN from the IRP portal. | Block PDF generation and email/WhatsApp dispatch until IRN is successfully fetched. |
| **RULE-TAX-006** | **TDS Deduction Thresholds:** The system MUST track cumulative payments to vendors within a Financial Year. If a payment crosses a TDS threshold (e.g., ₹30k single / ₹1L aggregate for 194C), the system MUST prompt for TDS deduction. | AI/UI alerts user during Vendor Payment creation. Can be manually overridden with a logged reason. |

---

## 7.3 AI & Automation Rules

These rules govern how the Virtual CFO AI operates, ensuring trust, transparency, and data isolation.

| Rule ID | Rule Description | System Enforcement |
|:--------|:-----------------|:-------------------|
| **RULE-AI-001** | **Confidence Threshold for Auto-Posting:** The AI MUST NOT automatically post any journal entry to the ledger if its aggregate extraction confidence score is below 0.95 (configurable per business). | Entries < 0.95 are saved as 'Draft' and routed to the Business Owner (if > 0.85) or Accountant (if < 0.85) for confirmation. |
| **RULE-AI-002** | **Mandatory Human Confirmation (MVP):** Regardless of confidence score, during Phase 1 (MVP), ALL AI-generated transactions MUST require human confirmation before posting. | Hardcoded restriction in MVP. Auto-posting unlocks in Phase 2 based on continuous accuracy metrics. |
| **RULE-AI-003** | **Missing Master Data Handling (BR-AI-003):** If a required master record is missing (Bank, Customer, Supplier, Product, Employee, Warehouse):<br>1. Check if a matching master exists (case-insensitive & alias matching).<br>2. If no match exists, propose creating the master using already available/inferred details.<br>3. Ask only for mandatory fields that cannot be inferred.<br>4. Do NOT block transactions for optional missing details (such as account numbers, phone numbers, or IFSC codes).<br>5. Complete the transaction after user confirms master creation. | Enforced in AI Agent Clarification Engine & Master Data Wizard. |
| **RULE-AI-004** | **Strict Data Isolation (Multi-Tenancy):** The AI context window for any given user query MUST ONLY contain data belonging to that user's active Tenant Business. | API payload generation strictly filtered by `tenant_id`. |
| **RULE-AI-005** | **AI Hallucination Prevention (Retrieval bounds):** When asked about factual business data (e.g., "What is my bank balance?"), the AI MUST rely *exclusively* on the data retrieved from the database via SQL/API, and MUST NOT generate synthetic numbers. | Enforced via Prompt Engineering constraints and temperature settings (T=0 for factual queries). |
| **RULE-AI-006** | **Correction Logging:** When a user modifies an AI-drafted transaction, the system MUST record the original AI extraction and the user's correction to create a training pair. | Trigger on 'Save' of a draft AI transaction where `is_modified = true`. |

---

*End of Chapter 7 – Business Rules*

*Next: Chapter 8 – Non-Functional Requirements*
