# AICFO — Business Requirements Document (BRD)

---

# Chapter 14 – AI Decision Framework & Master Rules Library

---

## 14.0 Overview

This chapter defines the definitive **AI Decision Framework** and the **21 Master Scenarios** that elevate the AI from a simple text-to-journal parser into an experienced, autonomous Virtual CFO. These rules govern how the AI handles complex accounting logic including GST/VAT, asset depreciation, multi-tax sales, foreign customers, and month-end closing.

---

## 14.1 The AI Decision Framework

For every financial prompt, the AI CFO MUST process the input in the following exact order:

1. **Identify the intent:** (sale, purchase, expense, payment, depreciation, etc.).
2. **Identify the actor:** (who is performing or recording the transaction).
3. **Identify the financial entity:** (which company's books are affected).
4. **Identify counterparties:** (customer, supplier, employee, bank, tax authority).
5. **Extract financial details:** (amount, tax, payment method, dates, due dates, invoice references).
6. **Determine the accounting treatment:** using company policies and tax rules.
7. **Ask follow-up questions:** *only* if essential information is missing.
8. **Generate the business documents:** (invoice, bill, payment voucher, journal entry, etc.).
9. **Update ledgers and sub-ledgers:** (GL, AR, AP, Inventory, Assets, Taxes).
10. **Confirm the action:** with a concise summary of what was recorded.

Following this workflow ensures the AI behaves like an experienced accountant.

---

## 14.2 Master Business Scenarios (1-10)

### 1. GST/VAT - Local Purchase
- **User:** *"I purchased office furniture worth ₹50,000 from XYZ Furniture. GST is 18%. I paid using our HDFC Bank account."*
- **AI Action:** Detect purchase transaction. Split GST (CGST/SGST or IGST based on supplier location). Create purchase bill. Update Input GST ledger. Update Furniture asset. Update Bank. Generate journal entry.

### 2. GST Inclusive Purchase
- **User:** *"Purchased a printer for ₹23,600 including 18% GST and paid by bank."*
- **AI Action:** Calculate Base Amount, Calculate GST, Calculate Total. Create journal.

### 3. GST Not Mentioned
- **User:** *"Purchased office chairs worth ₹60,000 from Modern Furniture."*
- **AI Action:** Ask: *"Is GST included?"* or *"Do you have the supplier GST invoice?"*

### 4. GST Payment
- **User:** *"Paid GST liability of ₹85,000 through internet banking."*
- **AI Action:** Reduce GST Payable. Reduce Bank. Store GST payment reference.

### 5. GST Return
- **User:** *"Generate GST return for June."*
- **AI Action:** Calculate Output GST. Calculate Input GST. Calculate Net GST. Prepare GST report.

### 6. Invoice Generation
- **User:** *"Create an invoice for Rahul Traders for 20 Dell laptops at ₹45,000 each plus 18% GST."*
- **AI Action:** Create Customer (if new). Generate Invoice Number. Calculate GST & Total. Update Accounts Receivable. Reduce Inventory. Calculate Cost of Goods Sold. Create PDF. Offer to email the invoice.

### 7. Recurring Invoice
- **User:** *"Every month invoice ABC Retail ₹25,000 for software maintenance."*
- **AI Action:** Create recurring invoice. Schedule monthly generation.

### 8. Partial Customer Payment
- **User:** *"Rahul Traders paid ₹3 lakh against Invoice INV-1025."*
- **AI Action:** Find invoice. Reduce Accounts Receivable. Update payment status.

### 9. Credit Note
- **User:** *"Rahul returned two damaged laptops."*
- **AI Action:** Create Credit Note. Reverse GST. Increase Inventory (if applicable). Update Customer Balance.

### 10. Vendor Payment
- **User:** *"Pay Tech Distributors ₹2 lakh from HDFC Bank against the oldest outstanding bills."*
- **AI Action:** Find oldest unpaid bills. Allocate payment. Update Accounts Payable. Update Bank.

---

## 14.3 Master Business Scenarios (11-21)

### 11. Advance Payment to Vendor
- **User:** *"Pay ₹1 lakh advance to Bright Technologies for next month's order."*
- **AI Action:** Record Vendor Advance. Do NOT book inventory yet.

### 12. Vendor Bill
- **User:** *"Received a bill from Dell worth ₹8 lakh plus GST on 30 days credit."*
- **AI Action:** Create Purchase Bill. Create Accounts Payable. Update Input GST.

### 13. Fixed Asset Purchase
- **User:** *"Bought a CNC machine for ₹25 lakh. Paid ₹5 lakh now and financed the remaining amount through Axis Bank."*
- **AI Action:** Create Fixed Asset. Create Loan Liability. Reduce Bank. Generate Asset Register.

### 14. Asset Disposal
- **User:** *"Sold our old printer for ₹12,000."*
- **AI Action:** Remove Asset. Reverse Accumulated Depreciation. Calculate Profit/Loss on Disposal.

### 15. Monthly Depreciation
- **User:** *"Record depreciation for July."*
- **AI Action:** Find depreciable assets. Apply company depreciation policy. Create journal entries. Update accumulated depreciation.

### 16. Complex Sales
- **User:** *"Sold 10 laptops, 5 monitors and 20 keyboards to Rahul Technologies. They paid ₹5 lakh today and the remaining amount is due in 30 days."*
- **AI Action:** Create Sales Invoice. Calculate line-item taxes. Reduce inventory. Calculate Cost of Goods Sold. Record partial payment. Create Accounts Receivable for the balance.

### 17. Multi-Tax Sale
- **User:** *"Sold goods worth ₹4 lakh to a customer in another state with applicable GST."*
- **AI Action:** Detect interstate transaction. Apply IGST. Generate compliant invoice.

### 18. Foreign Customer
- **User:** *"Sold software services to a client in the USA for $10,000."*
- **AI Action:** Ask if needed: Exchange rate, Tax treatment, Payment terms. Then: Record export sale. Handle tax rules. Record Accounts Receivable.

### 19. Bank Reconciliation
- **User:** *"Import my HDFC bank statement and reconcile transactions."*
- **AI Action:** Match payments. Match receipts. Identify unmatched transactions. Suggest entries. Generate reconciliation report.

### 20. Month-End Closing
- **User:** *"Close the books for June."*
- **AI Action:** Record depreciation. Accrue unpaid expenses. Reverse prepaid expenses where applicable. Record inventory adjustments. Calculate taxes. Produce Trial Balance, P&L, Balance Sheet, and Cash Flow Statement.

### 21. Smart Follow-Up Example
- **User:** *"Bought office furniture."*
- **AI Action:** Instead of assuming details, AI asks: *"I can record this purchase, but I need a few details: What was the purchase amount? Which supplier did you buy it from? Was GST/VAT included? How was it paid (cash, bank, credit)? Should this be recorded as a fixed asset according to your company policy?"*

---
*End of Chapter 14*
