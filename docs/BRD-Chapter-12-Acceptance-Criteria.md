# AICFO — Business Requirements Document (BRD)

---

# Chapter 12 – Acceptance Criteria

---

## 12.0 Overview

Acceptance Criteria define the specific, measurable conditions that must be met for the AICFO Phase 1 MVP to be considered "Done" and ready for production launch. These criteria serve as the foundation for the QA test plan and User Acceptance Testing (UAT).

---

## 12.1 Functional Acceptance Criteria (MVP Scope)

The MVP is accepted functionally when the following end-to-end workflows execute flawlessly without unhandled errors:

| ID | Criterion | Validation Method |
|:---|:----------|:------------------|
| **AC-FUN-001** | **Business Setup:** A new user can register, create a business profile, set the financial year, and view the default Chart of Accounts. | Manual UAT / Automated E2E |
| **AC-FUN-002** | **Voice Income Entry:** A user can speak a sales transaction; the system extracts Customer, Amount, and Payment Channel, creates a balanced Journal Entry, and updates the dashboard. | Manual UAT |
| **AC-FUN-003** | **Voice Expense Entry:** A user can speak an expense; the system extracts Vendor, Amount, Category, identifies GST ITC eligibility (if vendor GSTIN is present), and creates a balanced Journal Entry. | Manual UAT |
| **AC-FUN-004** | **Clarification Flow:** If a user says "Paid ₹5,000 for rent", the system MUST successfully ask for the missing Payment Channel, receive the answer, and complete the entry. | Manual UAT |
| **AC-FUN-005** | **Sales Invoicing:** A user can generate a GST-compliant sales invoice (CGST/SGST or IGST based on states), and the system automatically posts the corresponding receivable journal entry. | Manual UAT / Automated E2E |
| **AC-FUN-006** | **Receipt/Payment:** A user can record a payment received against a specific invoice, and the invoice status updates to 'Paid'. | Manual UAT |
| **AC-FUN-007** | **Reporting:** The system can generate a Trial Balance, P&L, and Balance Sheet that balance perfectly (Assets = Liabilities + Equity) based on the test transactions entered. | Automated E2E |

---

## 12.2 AI Accuracy & Performance Criteria

AI behavior is probabilistic, so acceptance is based on statistical accuracy against a known baseline dataset (the AI Conversation Catalog in Chapter 13).

| ID | Criterion | Validation Method |
|:---|:----------|:------------------|
| **AC-AI-001** | **Extraction Accuracy:** When tested against a suite of 100 standard business utterances from Chapter 13, the NLP engine MUST correctly extract the Intent, Amount, Entity (Customer/Vendor), and Account Category with **≥ 92% accuracy**. | Automated Batch Prompt Testing |
| **AC-AI-002** | **Fallback Gracefulness:** When fed 20 completely nonsensical or off-topic utterances (e.g., "What is the weather?"), the AI MUST gracefully reject 100% of them without attempting to create a journal entry. | Automated Batch Prompt Testing |
| **AC-AI-003** | **Voice Latency (End-to-End):** The time from the end of speech input to the rendering of the confirmation UI MUST be **< 3.0 seconds** in 90% of test cases over a standard broadband connection. | Performance Profiling |
| **AC-AI-004** | **Math Guardrail:** When tested with 10 complex scenario questions (e.g., "If I spend X, what is my remaining cash?"), the AI MUST NOT perform internal math, but must correctly format the result provided by the backend SQL engine in 100% of cases. | Manual UAT / Log Inspection |

---

## 12.3 Security & Isolation Criteria

| ID | Criterion | Validation Method |
|:---|:----------|:------------------|
| **AC-SEC-001** | **Tenant Data Leakage:** A test script authenticating as User A in Tenant A MUST NOT be able to query, view, or modify any records belonging to Tenant B through any API endpoint or GraphQL query. | Automated Penetration Testing |
| **AC-SEC-002** | **Audit Immutability:** Any attempt to directly UPDATE or DELETE a record in the `audit_logs` table using application database credentials MUST fail (enforced by DB triggers/permissions). | DBA Validation |
| **AC-SEC-003** | **Encryption:** All database volumes and S3 storage buckets MUST have encryption-at-rest enabled prior to production deployment. | Infrastructure Audit |

---

## 12.4 Compliance Criteria

| ID | Criterion | Validation Method |
|:---|:----------|:------------------|
| **AC-COM-001** | **GST Rounding:** GST amounts calculated by the system MUST match standard manual GST calculations within ±₹1.00 (to account for standard rounding rules) across 50 test invoices. | Automated Unit Tests |
| **AC-COM-002** | **Place of Supply:** Cross-state invoices MUST strictly apply IGST. Intra-state invoices MUST strictly apply CGST and SGST equally. | Automated Unit Tests |
| **AC-COM-003** | **Data Localization:** Production database and application servers MUST be deployed in an AWS/Cloud region geographically located in India (e.g., ap-south-1). | Infrastructure Audit |

---

*End of Chapter 12 – Acceptance Criteria*

*Next: Chapter 13 – AI Conversation Catalog (The Final Chapter)*
