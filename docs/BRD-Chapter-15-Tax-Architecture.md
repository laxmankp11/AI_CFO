# AICFO — Business Requirements Document (BRD)

---

# Chapter 15 – Tax Architecture & Compliance Engine

---

## 15.0 Overview

To support global scalability while giving individual businesses strict compliance control, the AICFO Tax Architecture is split into two distinct tiers:
1. **Level 1: Super Admin (Platform Configuration)** - Owns the global rules and statutory definitions.
2. **Level 2: Tenant (Business Configuration)** - Owns company-specific registrations, defaults, and product rules.

This separation ensures that when statutory tax laws change, the platform updates once, and every applicable tenant benefits automatically without touching application code.

---

## 15.1 Level 1: Super Admin (Platform Configuration)

The Super Admin manages the definitive global tax rules, validations, and rates shared across all tenants.

### 15.1.1 Tax Masters
Defines the tax regimes supported by the platform:
- GST (India)
- VAT (UK, UAE)
- Sales Tax (USA)
- SST (Malaysia)
- GST (Australia)

### 15.1.2 Tax Types
Components that make up a tax calculation:
- CGST, SGST, IGST, UTGST, CESS, TCS, TDS, Withholding Tax.

### 15.1.3 Tax Rates
Preconfigured standard rates mapped to regimes.
- **Example (India GST):** 0%, 5%, 12%, 18%, 28%
- **Example (UK VAT):** 0%, 5%, 20%

### 15.1.4 Tax Calculation Engine
Core platform mathematical rules governing:
- Inclusive Tax vs. Exclusive Tax
- Reverse Charge Mechanism
- Zero Rated, Exempt, Export, Import

### 15.1.5 Validation Rules & Templates
- **Templates:** GST Invoice, VAT Invoice, Tax Invoice, Retail Invoice, Credit Note, Debit Note.
- **Validation:** GST Number format, VAT Number validation, TIN validation, PAN validation.

---

## 15.2 Level 2: Tenant (Business Configuration)

Every company configures its own tax settings to dictate how the global engine applies to them.

### 15.2.1 Company Tax Information
- Company Name, GST Number, PAN, TAN, VAT Number, Business Type.
- **Branch GST:** Ability to map multiple GSTINs to different state branches (e.g., Mumbai GST vs. Delhi GST).

### 15.2.2 Default Settings
- **GST Enabled:** Yes / No
- **Default Rate:** e.g., 18%
- **Tax Inclusive:** Yes / No
- **Invoice Settings:** Invoice Prefix (e.g., INV-2026-), GST Invoice (Auto), E-Invoice (Yes/No), E-Way Bill (Yes/No).

### 15.2.3 Granular Overrides
- **Product Tax:** Laptop (18%), Book (0%), Food (5%), Medicine (12%).
- **Customer Tax:** GST Registered?, GST Number, Place of Supply, Reverse Charge, Default Tax Rate.
- **Supplier Tax:** Supplier GST, Input Tax Credit Eligible, TDS Applicable, Reverse Charge.

### 15.2.4 AI Preferences
- Always ask before applying GST
- Automatically calculate GST
- Validate GST Number automatically
- Auto-detect Place of Supply

---

## 15.3 The AI Tax Rule Engine

Instead of hardcoding tax logic (if/else), the system uses a configurable rule engine. 

### 15.3.1 AI Tax Rules
Rules are evaluated based on condition priority.
- **Rule Name:** Same State Sale
  - **Condition:** Customer.State == Company.State
  - **Action:** Apply CGST + SGST
  - **Priority:** 100
- **Rule Name:** Interstate Sale
  - **Condition:** Customer.State != Company.State
  - **Action:** Apply IGST
  - **Priority:** 90

### 15.3.2 AI Prompt Workflow
When a user says: *"Create an invoice for Rahul Traders for 10 laptops at ₹50,000 each."*, the AI internally follows this sequence:
1. Identify the tenant and load its tax configuration.
2. Check whether GST/VAT is enabled for the company.
3. Retrieve the company's GST registration and branch details.
4. Load the customer's tax profile and place of supply.
5. Determine whether the transaction is intrastate, interstate, export, or exempt.
6. Apply the appropriate tax rule from the platform's rule engine.
7. Calculate taxes and generate a compliant invoice.
8. Create the accounting entries and update GST input/output ledgers.
9. Validate whether additional compliance (e-invoicing/e-way bills) is required based on tenant settings.

---

## 15.4 Settings Menu Structure

### Super Admin Settings
```
Tax Management
├── Countries
├── Tax Masters
├── Tax Types
├── Tax Rates
├── Tax Rules Engine
├── GST Rules
├── VAT Rules
├── Invoice Templates
├── Validation Rules
├── AI Tax Rules
├── E-Invoice Providers
├── E-Way Bill Providers
└── Tax APIs
```

### Tenant Settings
```
Tax & Compliance
├── Company Tax Details
├── GST Registration
├── Branch GST
├── Default Tax
├── Product Taxes
├── Customer Taxes
├── Supplier Taxes
├── Invoice Settings
├── Return Settings
├── Tax Preferences
├── AI Tax Settings
└── Connected Tax Portals
```

---
*End of Chapter 15*
