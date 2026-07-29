# AICFO — Business Requirements Document (BRD)

---

# Chapter 5 – Business Processes

---

## 5.0 Overview

This chapter defines the **core business processes** that AICFO supports. Each process is documented as a structured workflow specification that serves as the bridge between the business modules (Chapter 4) and the functional requirements (Chapter 6).

### Process Documentation Template

Every process follows this structure:

| Element | Description |
|:--------|:------------|
| **Process ID** | Unique identifier (BP-NNN) |
| **Business Objective** | Why this process exists — what business value it delivers |
| **Actors** | Which stakeholders participate |
| **Preconditions** | What must be true before the process can start |
| **Trigger** | What initiates the process |
| **Main Flow** | The happy-path step-by-step sequence |
| **Alternative Flows** | Valid variations of the main flow |
| **Exception Flows** | Error conditions and how they are handled |
| **Post Conditions** | What is true after the process completes successfully |
| **Business Rules** | Constraints and logic enforced during the process |
| **AI Behavior** | How the Virtual CFO participates in or drives this process |

### Process Index

| ID | Process Name | Module | Phase |
|:---|:-------------|:-------|:------|
| BP-001 | Record Income by Voice | AI + Finance | [MVP] |
| BP-002 | Record Expense by Voice | AI + Finance | [MVP] |
| BP-003 | Classify Asset vs Expense | AI + Finance | [MVP] |
| BP-004 | AI Clarification Dialogue | AI | [MVP] |
| BP-005 | Create Sales Invoice | Sales + Finance | [MVP] |
| BP-006 | Record Payment Receipt | Sales + Finance | [MVP] |
| BP-007 | Record Vendor Bill via OCR | AI + Purchase | [MVP] |
| BP-008 | Record Vendor Payment | Purchase + Finance | [MVP] |
| BP-009 | Morning Financial Briefing | AI + Analytics | [MVP] |
| BP-010 | Daily Closing Summary | AI + Analytics | [MVP] |
| BP-011 | Generate Financial Report | Analytics + Finance | [MVP] |
| BP-012 | AI CFO Advisory Query | AI | [MVP] |
| BP-013 | AI Correction & Learning | AI | [MVP] |
| BP-014 | Bank Reconciliation | Finance | [P2] |
| BP-015 | Customer Payment Reminder | Sales + Communication | [P2] |
| BP-016 | Employee Expense Claim | HR + Finance | [P3] |
| BP-017 | GST Return Preparation | Finance | [P3] |
| BP-018 | Monthly Payroll Processing | HR + Finance | [P3] |

---

## BP-001: Record Income by Voice

### Business Objective
Enable business owners to record sales/income transactions by speaking naturally, without understanding accounting terminology or navigating forms.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Preconditions
- User is authenticated and has selected an active business
- Business has a Chart of Accounts configured (at minimum, default COA)
- Microphone permission granted (for voice input) or text input available

### Trigger
Owner speaks or types a sales/income statement, e.g.:
- *"We sold 20 laptops to ABC Company. They paid ₹8 lakh by bank transfer."*
- *"Received ₹50,000 from Priya Enterprises for last month's invoice."*
- *"Revenue of ₹1,20,000 from consulting services to XYZ Corp."*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Speaks or types the transaction description |
| 2 | AI | Captures audio → sends to STT service (Whisper) → receives text transcript |
| 3 | AI | Sends transcript to NLP extraction engine with business context (COA, known customers, recent transactions) |
| 4 | AI | Extracts structured fields: **Intent** (Income/Sale), **Customer** (ABC Company), **Product/Service** (Laptops), **Quantity** (20), **Amount** (₹8,00,000), **Payment Status** (Paid), **Payment Channel** (Bank Transfer), **GST Rate** (18%), **GST Amount** (₹1,22,034) |
| 5 | AI | Assigns confidence scores to each extracted field |
| 6 | AI | Maps to accounting entries: Sales Account (Cr), Bank Account (Dr), GST Output Liability (Cr) |
| 7 | AI | Presents confirmation to Owner: *"Got it! Sale of 20 laptops to ABC Company for ₹8,00,000 paid via bank transfer. GST output liability: ₹1,22,034. Confirm or edit?"* |
| 8 | AI | Displays extracted field badges (Customer, Amount, GST, Channel, Status) |
| 9 | Owner | Reviews and says *"Confirm"* or taps Confirm button |
| 10 | System | Creates journal entry: Bank A/c Dr ₹8,00,000 / Sales A/c Cr ₹6,77,966 / GST Output Cr ₹1,22,034 |
| 11 | System | Updates customer ledger (ABC Company), bank balance, revenue totals, and GST liability |
| 12 | System | Logs entry in audit trail with source: VOICE, AI confidence scores, and user confirmation |
| 13 | AI | Responds: *"Sale recorded. Today's revenue is now ₹8,00,000. Anything else?"* |

### Alternative Flows

**AF-001: Text input instead of voice**
- Step 1 changes: Owner types the transaction in the chat input box
- Steps 2 changes: STT is skipped; text is sent directly to NLP extraction
- All subsequent steps remain the same

**AF-002: Customer not found in system**
- At Step 4, AI does not find "ABC Company" in existing customers
- AI asks: *"I don't have ABC Company in your customer list. Shall I create a new customer record?"*
- Owner confirms → System creates Customer with name "ABC Company" → Process continues from Step 6

**AF-003: Partial payment**
- Owner says: *"Sold goods worth ₹5 lakh to ABC Company. They paid ₹3 lakh, remaining on credit."*
- AI extracts: Total = ₹5,00,000, Paid = ₹3,00,000, Outstanding = ₹2,00,000
- System creates: invoice for full amount, payment receipt for ₹3,00,000, and accounts receivable entry for ₹2,00,000

### Exception Flows

**EF-001: Amount not understood**
- AI cannot extract amount from the utterance
- AI asks: *"I couldn't catch the amount. How much was the sale?"*
- Owner provides amount → Process resumes from Step 4

**EF-002: Confidence below threshold**
- Aggregate confidence < 0.85
- AI flags specific low-confidence fields: *"I'm not sure about the payment channel. Was this paid by bank, UPI, or cash?"*
- Owner clarifies → Process resumes from Step 5

**EF-003: STT failure**
- Speech-to-text returns empty or unintelligible text
- AI responds: *"I didn't catch that clearly. Could you say it again, or type it instead?"*

**EF-004: AI API unavailable**
- AI extraction service is down
- System shows: *"AI assistant is temporarily unavailable. You can enter this transaction manually."*
- Redirects to manual journal entry form

### Post Conditions
- ✅ Journal entry created and balanced (debits = credits)
- ✅ Customer ledger updated
- ✅ Bank/cash balance updated
- ✅ GST output liability updated
- ✅ Revenue dashboard updated in real-time
- ✅ Audit trail entry created with full AI extraction details
- ✅ Entry appears in transactions list and general ledger

### Business Rules
- BR-FIN-001: Journal MUST balance
- BR-SALE-002: GST Place of Supply rules enforced (CGST+SGST or IGST)
- BR-AI-002: AI MUST present extraction before posting
- BR-FIN-008: Amounts stored with 2-decimal precision

### AI Behavior
- AI uses business memory to improve accuracy: if owner frequently sells laptops to ABC Company, AI pre-fills with higher confidence
- AI applies correct GST rate based on product HSN code (if product exists in catalog) or default rate
- AI speaks the confirmation aloud via TTS if voice mode is active

---

## BP-002: Record Expense by Voice

### Business Objective
Enable instant expense recording through natural speech, capturing vendor, category, amount, payment method, and GST Input Tax Credit.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Preconditions
- User is authenticated with an active business
- Chart of Accounts includes expense categories

### Trigger
Owner speaks or types an expense statement:
- *"Paid ₹4,500 to Rajesh for electrical work."*
- *"Spent ₹22,000 on office rent, paid by UPI."*
- *"Bought stationery for ₹1,200, cash."*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Speaks or types the expense description |
| 2 | AI | Processes through STT → NLP extraction pipeline |
| 3 | AI | Extracts: **Intent** (Expense), **Vendor** (Rajesh), **Category** (Repairs & Maintenance), **Amount** (₹4,500), **Payment Channel** (not specified), **GST** (18% if vendor is registered, 0% if unregistered) |
| 4 | AI | Detects missing field: Payment Channel not specified |
| 5 | AI | Asks: *"Was this ₹4,500 paid by cash, UPI, or bank transfer?"* (→ triggers BP-004 Clarification) |
| 6 | Owner | Responds: *"Cash"* |
| 7 | AI | Completes extraction: Payment Channel = Cash |
| 8 | AI | Checks if vendor "Rajesh" has GSTIN on file. If no → GST ITC not claimable. If yes → ITC = ₹688 |
| 9 | AI | Presents confirmation: *"Expense of ₹4,500 to Rajesh for electrical work, paid cash. Category: Repairs & Maintenance. No GST credit (unregistered vendor). Confirm?"* |
| 10 | Owner | Confirms |
| 11 | System | Creates journal: Repairs & Maintenance A/c Dr ₹4,500 / Cash A/c Cr ₹4,500 |
| 12 | System | Updates vendor history, expense totals, and cash balance |

### Alternative Flows

**AF-001: All fields present in single utterance**
- Owner says: *"Spent ₹22,000 on office rent, paid by UPI"*
- AI extracts all fields without clarification. Steps 4–6 skipped.

**AF-002: Vendor with GSTIN**
- Vendor has GSTIN in the system
- AI calculates and claims GST ITC: *"GST credit of ₹688 claimed on this expense."*
- Journal includes: Expense A/c Dr ₹3,814 / GST Input Credit Dr ₹686 / Cash Cr ₹4,500

### Exception Flows

**EF-001: Category unclear**
- Owner says: *"I spent 20,000"* — no category provided
- AI asks: *"What was the ₹20,000 for?"*
- Owner: *"Marketing"*
- AI classifies under Marketing & Advertising expense

### Post Conditions
- ✅ Expense journal entry created
- ✅ Cash/bank balance reduced
- ✅ GST ITC claimed (if applicable)
- ✅ Vendor ledger updated
- ✅ Expense dashboard updated

### Business Rules
- BR-PUR-001: GST ITC only for registered vendors
- BR-FIN-001: Journal must balance
- BR-AI-001: Entries below 0.85 confidence require confirmation

### AI Behavior
- AI learns category patterns: if "Rajesh" is always categorized as Repairs, future entries auto-classify with higher confidence
- AI detects TDS applicability: if cumulative payments to Rajesh exceed ₹30,000/year, AI alerts about Section 194C TDS requirement

---

## BP-003: Classify Asset vs Expense

### Business Objective
Ensure high-value purchases are correctly classified as Capital Assets (with depreciation) rather than one-time expenses, protecting P&L accuracy and tax compliance.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Preconditions
- A purchase transaction has been spoken or typed
- Purchase amount exceeds the asset threshold (default: ₹50,000)
- Item type matches potential asset categories (equipment, furniture, vehicles, machinery, IT hardware)

### Trigger
AI detects a high-value purchase during transaction extraction (BP-001 or BP-002):
- *"Bought a laptop for office for ₹65,000"*
- *"Purchased office furniture worth ₹1,20,000"*
- *"Bought a delivery van for ₹8,50,000"*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | AI | During extraction, detects: amount ≥ ₹50,000 AND item matches asset keywords (laptop, computer, furniture, machine, vehicle, printer, AC, etc.) |
| 2 | AI | Pauses normal expense flow and asks: *"This purchase of ₹65,000 could be a long-term business asset. Is this for business use as a capital asset, or is it a regular expense?"* |
| 3 | AI | Presents options: **"Yes, Business Asset (Depreciate)"** / **"No, Regular Expense"** |
| 4 | Owner | Selects "Yes, Business Asset" |
| 5 | AI | Determines asset category and depreciation parameters: Category = IT Equipment, Useful Life = 3 years (per Income Tax Act), Method = Straight-Line, Annual Depreciation = ₹21,667 |
| 6 | AI | Calculates GST ITC: ₹9,915 (18% reverse-calculated from ₹65,000 inclusive) |
| 7 | AI | Presents: *"Classified as Capital Asset (IT Equipment). Depreciation: ₹21,667/year over 3 years. GST credit of ₹9,915 claimed. Confirm?"* |
| 8 | Owner | Confirms |
| 9 | System | Creates journal: IT Equipment Asset A/c Dr ₹55,085 / GST Input Credit Dr ₹9,915 / Bank/Cash Cr ₹65,000 |
| 10 | System | Adds to Fixed Asset Register with depreciation schedule |
| 11 | System | Schedules automatic monthly depreciation entries: Depreciation Expense Dr / Accumulated Depreciation Cr |

### Alternative Flows

**AF-001: Owner classifies as expense**
- Owner selects "No, Regular Expense" at Step 4
- AI records as normal expense: Office Equipment Expense A/c Dr / Bank Cr
- No depreciation schedule created

**AF-002: Owner unsure**
- Owner says: *"I'm not sure"*
- AI explains: *"If this laptop will be used for business for more than a year, it's typically classified as a capital asset. This means the cost is spread over its useful life as depreciation, which gives you a tax deduction each year. If it's a one-time consumable purchase, it's an expense. What would you like to do?"*

### Post Conditions
- ✅ Asset recorded in Fixed Asset Register OR expense recorded in ledger
- ✅ GST ITC claimed
- ✅ Depreciation schedule created (if asset)
- ✅ Balance Sheet updated (if asset) OR P&L updated (if expense)

### Business Rules
- BR-FIN-005: Depreciation entries are system-generated per asset register schedule
- Asset threshold is configurable per business (default ₹50,000)
- Depreciation rates follow Income Tax Act Section 32 (IT equipment: 40% WDV or 3-year SLM)

### AI Behavior
- AI remembers classification decisions: if owner always classifies laptops as assets, future laptop purchases auto-suggest "Asset" with higher confidence
- AI uses Income Tax Act depreciation rates as defaults but allows override

---

## BP-004: AI Clarification Dialogue

### Business Objective
Systematically resolve ambiguous or incomplete transaction inputs through conversational follow-up questions, ensuring every recorded entry is accurate and complete.

### Actors
- **Primary:** Business Owner or Employee
- **Secondary:** AICFO Virtual CFO (AI)

### Preconditions
- User has provided a transaction input (voice or text)
- AI extraction has identified one or more fields with missing data or confidence < 0.85

### Trigger
AI's NLP extraction produces incomplete or low-confidence results during any transaction recording process.

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | AI | Identifies missing or uncertain fields from the extraction |
| 2 | AI | Prioritizes questions: most critical missing field first (Amount > Type > Category > Payment Channel > Entity) |
| 3 | AI | Asks the first clarification question with quick-response buttons where applicable |
| 4 | User | Responds via voice, text, or button tap |
| 5 | AI | Incorporates the answer into the extraction |
| 6 | AI | Checks if all required fields are now present and above confidence threshold |
| 7a | (If complete) | AI presents the full extraction for confirmation → returns to parent process |
| 7b | (If still incomplete) | AI asks the next clarification question → returns to Step 4 |

### Clarification Question Templates

| Missing Field | Question Template | Quick Options |
|:--------------|:------------------|:--------------|
| Amount | *"How much was this transaction?"* | — (free text) |
| Payment Channel | *"Was this paid by cash, UPI, or bank transfer?"* | Cash / UPI / Bank Transfer |
| Category | *"What was this expense for?"* | — (free text, AI suggests from history) |
| Vendor/Customer | *"Who was this payment to?"* or *"Who was this received from?"* | — (free text, AI suggests matches) |
| Date | *"When did this happen? Today, or a different date?"* | Today / Yesterday / Other |
| Asset vs Expense | *"Is this a long-term business asset or a regular expense?"* | Business Asset / Expense |
| GST Applicability | *"Does this vendor charge GST? Do you have their GSTIN?"* | Yes / No / Not Sure |
| TDS Applicability | *"This payment may require TDS deduction. Shall I apply TDS at [rate]%?"* | Yes / No |

### Business Rules
- Maximum 3 clarification questions per transaction. If still incomplete after 3 questions, AI creates a draft entry flagged for manual review.
- AI MUST NOT ask questions whose answers can be inferred from context (e.g., if vendor is already known, don't ask for vendor again).
- Quick-response buttons MUST be provided where options are limited and known.

### AI Behavior
- AI learns from clarification patterns: if the owner always says "Bank" when asked about payment channel, AI increases confidence for "Bank" on future extractions
- AI presents the most likely answer as the first option in quick-response buttons

---

## BP-005: Create Sales Invoice

### Business Objective
Generate GST-compliant sales invoices with correct tax breakdowns, sequential numbering, and multi-channel delivery (PDF, email, WhatsApp).

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI), Customer (recipient)

### Preconditions
- Customer exists in the system (or is created during process)
- Products/services exist in catalog (or are added as one-time line items)

### Trigger
- Owner says: *"Create an invoice for ABC Company for 10 laptops at ₹50,000 each"*
- Owner navigates to Sales → New Invoice in the UI
- Conversion from Quotation or Sales Order

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Initiates invoice creation (voice, text, or UI) |
| 2 | AI/System | Determines customer: existing or new |
| 3 | AI/System | Populates line items: product, HSN/SAC, quantity, rate, discount |
| 4 | System | Calculates tax based on Place of Supply: Customer's state vs Business's state → CGST+SGST (same state) or IGST (different state) |
| 5 | System | Applies correct GST rate per product HSN code |
| 6 | System | Calculates totals: Subtotal + Tax = Grand Total |
| 7 | System | Assigns sequential invoice number (e.g., INV-2026-0143) |
| 8 | AI | Presents invoice summary for confirmation |
| 9 | Owner | Reviews and confirms |
| 10 | System | Creates journal: Accounts Receivable Dr / Sales Cr / GST Output Cr |
| 11 | System | Generates PDF invoice with QR code (if e-invoicing enabled) |
| 12 | System | Offers delivery options: Email, WhatsApp, Download PDF |
| 13 | Owner | Selects delivery method(s) |
| 14 | System | Sends invoice to customer via selected channel(s) |
| 15 | System | If inventory-tracked items: deducts stock quantities |

### Post Conditions
- ✅ Invoice created with unique sequential number
- ✅ GST liability (output) recorded
- ✅ Accounts receivable updated for customer
- ✅ Revenue recorded in P&L
- ✅ Inventory reduced (if applicable)
- ✅ Invoice delivered to customer
- ✅ Audit trail entry logged

### Business Rules
- BR-SALE-001: Sequential invoice numbering within FY
- BR-SALE-002: Place of Supply rules for GST
- BR-SALE-003: Posted invoice cannot be edited (use Credit Note)

---

## BP-006: Record Payment Receipt

### Business Objective
Record money received from customers, automatically match it to outstanding invoices, and update accounts receivable.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Trigger
- *"ABC Company paid ₹3,50,000 by bank transfer"*
- *"Received ₹50,000 from Priya via UPI"*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Speaks or types payment receipt details |
| 2 | AI | Extracts: Customer, Amount, Payment Channel |
| 3 | AI | Queries open invoices for this customer |
| 4a | (Single match) | AI auto-matches to the open invoice closest in amount |
| 4b | (Multiple invoices) | AI presents list: *"ABC Company has 3 open invoices: INV-0140 (₹2,00,000), INV-0142 (₹3,50,000), INV-0145 (₹1,30,000). Which invoice is this payment for?"* |
| 4c | (No open invoices) | AI records as Advance from Customer |
| 5 | Owner | Confirms match or selects invoice(s) |
| 6 | System | Creates journal: Bank/Cash Dr / Accounts Receivable Cr |
| 7 | System | Marks invoice as Paid (or Partially Paid) |
| 8 | AI | *"Payment recorded. ABC Company has ₹1,30,000 remaining outstanding."* |

### Post Conditions
- ✅ Bank/cash balance increased
- ✅ Accounts receivable decreased
- ✅ Invoice status updated
- ✅ Customer ledger updated

### Business Rules
- BR-SALE-004: Payment matched to invoice(s). Unmatched = advance.
- Partial payments are supported: invoice shows Partially Paid status

---

## BP-007: Record Vendor Bill via OCR

### Business Objective
Allow business owners to photograph vendor bills/invoices and have AICFO automatically extract all fields and create purchase entries.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI), OCR Engine

### Trigger
Owner takes a photo of a vendor invoice/bill or uploads a PDF.

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Photographs bill using mobile camera or uploads PDF/image |
| 2 | System | Sends image to OCR engine (Google Vision / AWS Textract) |
| 3 | OCR Engine | Extracts raw text from image |
| 4 | AI | Processes raw text through NLP to extract structured fields: Vendor Name, Vendor GSTIN, Bill Number, Bill Date, Line Items (description, HSN, qty, rate), Tax Breakdown (CGST, SGST, IGST), Total Amount |
| 5 | AI | Matches vendor to existing vendor records (fuzzy name matching + GSTIN lookup) |
| 6 | AI | Classifies expense category based on line item descriptions |
| 7 | AI | Calculates GST ITC eligibility: Is vendor GSTIN valid? Is this a blocked ITC category? |
| 8 | AI | Presents extracted data with highlighted confidence: *"I read this bill from WeWork India (GSTIN: 27AAACW9988H1Z2). Amount: ₹28,000. GST: ₹4,271 (eligible for ITC). Category: Office Rent. Confirm or edit?"* |
| 9 | Owner | Reviews and confirms (can edit any field) |
| 10 | System | Creates purchase journal entry with GST ITC |
| 11 | System | Stores original image linked to the journal entry for audit |

### Alternative Flows

**AF-001: Poor image quality**
- OCR confidence is low due to blurry/dark image
- AI: *"I'm having trouble reading this bill. Can you take another photo with better lighting?"*

**AF-002: New vendor**
- Vendor not found in system
- AI creates new vendor record from extracted GSTIN and name

### Post Conditions
- ✅ Purchase bill recorded with all fields
- ✅ GST ITC claimed (if eligible)
- ✅ Vendor ledger updated
- ✅ Original document image stored and linked
- ✅ Expense dashboard updated

---

## BP-008: Record Vendor Payment

### Business Objective
Record outgoing payments to vendors, match to outstanding bills, and handle TDS deduction where applicable.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Trigger
- *"Paid ₹1,20,000 to Sharma Traders by bank transfer"*
- *"Pay Rajesh ₹15,000, cash"*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Speaks or types payment details |
| 2 | AI | Extracts: Vendor, Amount, Payment Channel |
| 3 | AI | Checks TDS applicability based on payment type, vendor category, and cumulative payments for the year |
| 4a | (TDS applicable) | AI: *"TDS of ₹1,500 (10% under Section 194C) should be deducted. Net payment: ₹13,500. Apply TDS?"* |
| 4b | (TDS not applicable) | Process continues without TDS |
| 5 | AI | Matches payment to outstanding vendor bills |
| 6 | Owner | Confirms |
| 7 | System | Creates journal: Vendor Payable Dr / TDS Payable Cr (if applicable) / Bank/Cash Cr |
| 8 | System | Updates vendor ledger and bank balance |

### Post Conditions
- ✅ Vendor balance reduced
- ✅ Bank/cash balance reduced
- ✅ TDS liability recorded (if applicable)
- ✅ Bill status updated to Paid

---

## BP-009: Morning Financial Briefing

### Business Objective
Provide the business owner with a spoken, proactive financial summary every morning — eliminating the need to navigate dashboards or wait for accountant reports.

### Actors
- **Primary:** AICFO Virtual CFO (AI)
- **Secondary:** Business Owner (listener)

### Trigger
- Owner opens the AICFO app in the morning (auto-triggered)
- Owner says: *"Good morning"* or *"What's my status?"*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | AI | Detects first app open of the day (or responds to greeting) |
| 2 | AI | Queries previous day's data: revenue, expenses, net profit, bank balance, GST liability changes, and overdue invoices |
| 3 | AI | Composes natural language briefing |
| 4 | AI | Delivers briefing via text (chat bubble) and voice (TTS): |
| | | *"Good morning, Laxman. Yesterday your revenue was ₹84,500. You spent ₹22,000. Your net profit was ₹62,500. Bank balance stands at ₹12,40,000. GST payable increased by ₹3,960. You have 3 unpaid invoices totaling ₹4,80,000 — one from ABC Company is 12 days overdue. What happened in your business today?"* |
| 5 | Owner | Begins daily transaction recording or asks follow-up questions |

### AI Behavior
- Briefing content adapts based on what's most important: if cash is low, emphasize that; if a large payment is overdue, highlight it
- Tone is warm and professional — Virtual CFO persona
- If no transactions happened yesterday, AI says: *"No transactions recorded yesterday. Would you like to catch up on anything?"*

---

## BP-010: Daily Closing Summary

### Business Objective
Provide an end-of-day financial wrap-up showing the day's financial activity, enabling the owner to "close the day" mentally and catch any missed transactions.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Trigger
- Owner says: *"Daily closing"* or *"Show me today's summary"*
- Scheduled notification at a configured time (e.g., 7:00 PM)

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner/System | Triggers daily closing |
| 2 | AI | Aggregates today's transactions: total income, total expenses, asset purchases, payments made, payments received |
| 3 | AI | Calculates: net cash impact, updated bank balance, month-to-date profit |
| 4 | AI | Identifies potential missing entries: *"You recorded 4 transactions today. Yesterday you had 7. Is there anything else to record?"* |
| 5 | AI | Delivers summary via chat and TTS |
| 6 | Owner | Confirms day is complete or adds missing transactions |

### Post Conditions
- ✅ Owner has reviewed the day's financial activity
- ✅ Any missing transactions have been recorded
- ✅ Daily summary logged in system for historical reference

---

## BP-011: Generate Financial Report

### Business Objective
Generate accurate, real-time financial statements (P&L, Balance Sheet, Trial Balance) on demand through voice or UI navigation.

### Actors
- **Primary:** Business Owner or Accountant
- **Secondary:** AICFO Virtual CFO (AI)

### Trigger
- *"Show me this month's profit and loss"*
- *"Generate Balance Sheet as of today"*
- Navigation to Reports section in UI

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | User | Requests report by voice, text, or UI |
| 2 | AI | Identifies report type and parameters (date range, comparison period) |
| 3 | System | Queries general ledger and computes report data in real-time |
| 4 | System | Renders report in interactive table format with drill-down capability |
| 5 | AI | (If voice) Speaks a summary: *"This month's revenue is ₹12,40,000, expenses are ₹3,80,000. Net profit: ₹8,60,000 — that's a 69% profit margin."* |
| 6 | User | Can drill down (click any line item to see underlying transactions), compare periods, or export to PDF/Excel |

### Business Rules
- BR-ANA-002: Report values MUST match ledger data exactly
- Reports are generated in real-time from the ledger — never from cached or pre-aggregated data (ensures accuracy)

---

## BP-012: AI CFO Advisory Query

### Business Objective
Enable business owners to ask strategic financial questions and receive data-driven advice based on their actual financial position.

### Actors
- **Primary:** Business Owner
- **Secondary:** AICFO Virtual CFO (AI)

### Trigger
- *"Can I buy a new machine for ₹2,50,000?"*
- *"Can I afford to hire another employee at ₹40,000/month?"*
- *"Should I offer 30-day credit to this new customer?"*

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner | Asks a financial scenario question |
| 2 | AI | Identifies question type: Capital Purchase / Hiring / Credit Policy / General |
| 3 | AI | Retrieves current financial position: bank balance, monthly revenue trend, monthly expense trend, outstanding receivables/payables, upcoming obligations (GST, TDS, rent, salaries) |
| 4 | AI | Performs scenario analysis: "If you spend ₹2,50,000 on this machine..." → calculates remaining cash, impact on monthly cash flow, cash runway in months, GST ITC benefit, depreciation tax benefit |
| 5 | AI | Generates recommendation with data: |
| | | *"Based on your current bank balance of ₹12,40,000 and average monthly operating expenses of ₹2,80,000:*
| | | *✅ Yes, you can make this purchase. Your cash reserve would reduce to ₹9,90,000, giving you 3.5 months of operating runway (above the recommended minimum of 2 months).*
| | | *You'll also claim ₹38,136 in GST Input Tax Credit and ₹50,000/year in depreciation deductions.*
| | | *One caution: you have ₹4,80,000 in outstanding receivables. If collections are delayed, your effective runway drops to 2.8 months."* |
| 6 | AI | Appends disclaimer: *"This is AI-generated analysis based on your financial data. Please consult a financial advisor for major decisions."* |

### Business Rules
- BR-AI-005: Advisory MUST include AI-generated disclaimer
- Advisory uses only the owner's actual financial data — no assumptions about future revenue growth

---

## BP-013: AI Correction & Learning

### Business Objective
When users correct AI-generated entries, capture the correction as structured training data so the AI improves accuracy over time for that specific business.

### Actors
- **Primary:** Business Owner or Accountant
- **Secondary:** AICFO AI Engine

### Trigger
User edits an AI-generated transaction entry (changes account, category, vendor, amount, or any other field).

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | User | Edits an AI-generated entry (e.g., changes category from "Office Supplies" to "Repairs & Maintenance") |
| 2 | System | Detects that the edit changes a field that was AI-extracted |
| 3 | System | Logs correction record: Original AI Output (field, value, confidence) → User Correction (field, new value) → Context (original utterance, business, timestamp) |
| 4 | System | Updates the journal entry with the corrected values |
| 5 | AI (background) | Stores correction in per-business learning store |
| 6 | AI (future) | On next similar transaction, uses corrections to adjust extraction: "Last time 'electrical work' was classified as Repairs & Maintenance, not Office Supplies" → applies higher confidence to Repairs & Maintenance |

### Business Rules
- BR-AI-003: Both original AI output and correction MUST be preserved
- BR-AI-004: Learning is per-tenant only — corrections from Business A do not affect Business B
- Correction patterns are aggregated for platform-wide model improvement (anonymized)

---

## BP-014: Bank Reconciliation [P2]

### Business Objective
Match bank statement transactions with accounting ledger entries to identify discrepancies, unrecorded transactions, and reconciliation differences.

### Actors
- **Primary:** Accountant
- **Secondary:** AICFO AI Engine

### Trigger
Accountant uploads a bank statement (CSV/Excel/PDF) or connects bank feed.

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Accountant | Uploads bank statement file |
| 2 | System | Parses bank statement: extracts date, description, reference, debit, credit, balance |
| 3 | AI | Auto-matches bank transactions with ledger entries using: amount match, date proximity (±3 days), reference number match, and description similarity |
| 4 | System | Presents results in 3 categories: **Matched** (green), **Unmatched in Bank** (entries in bank but not in books), **Unmatched in Books** (entries in books but not in bank) |
| 5 | Accountant | Reviews matches — confirms correct matches, manually matches remaining entries |
| 6 | AI | For unmatched bank entries, suggests: *"This ₹5,000 debit on July 15 looks like an ATM withdrawal. Create a cash withdrawal entry?"* |
| 7 | Accountant | Approves AI suggestions or creates manual entries |
| 8 | System | Generates Bank Reconciliation Statement showing: Book Balance + Adjustments = Bank Balance |

### Post Conditions
- ✅ All bank transactions matched or explained
- ✅ Missing ledger entries created
- ✅ Reconciliation statement generated
- ✅ Reconciliation status tracked per bank account per month

---

## BP-015: Customer Payment Reminder [P2]

### Business Objective
Automatically send polite payment reminders to customers with overdue invoices, reducing the owner's manual follow-up effort.

### Actors
- **Primary:** AICFO System (automated)
- **Secondary:** Business Owner (configures), Customer (recipient)

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | System | Daily scheduled job scans all open invoices |
| 2 | System | Identifies invoices past due date |
| 3 | System | Applies reminder schedule: Day 1, Day 7, Day 15, Day 30 after due date |
| 4 | System | Generates reminder message using template (customizable) |
| 5 | System | Sends via configured channel (email, SMS, WhatsApp) |
| 6 | System | Logs reminder in communication history |
| 7 | AI | Notifies owner: *"Sent payment reminder to ABC Company for ₹4,80,000 (15 days overdue)"* |

---

## BP-016: Employee Expense Claim [P3]

### Business Objective
Allow employees to submit expense claims with receipt photos and voice descriptions, routed to the business owner for approval.

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Employee | Opens AICFO app → speaks: *"Spent ₹800 on cab for client meeting"* or photographs receipt |
| 2 | AI | Extracts: Amount (₹800), Category (Travel/Conveyance), Purpose (Client meeting) |
| 3 | System | Creates expense claim (status: Pending Approval) |
| 4 | System | Sends push notification to Business Owner: *"Rahul submitted ₹800 expense claim for cab fare"* |
| 5 | Owner | Reviews and approves/rejects with optional comment |
| 6 | System | If approved: Creates journal entry (Travel Expense Dr / Reimbursement Payable Cr) |
| 7 | System | Adds to next payroll cycle or processes as ad-hoc reimbursement |

---

## BP-017: GST Return Preparation [P3]

### Business Objective
Automatically compile GST return data (GSTR-1 and GSTR-3B) from the ledger, reducing preparation time from days to minutes.

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Accountant/Owner | Requests: *"Prepare GST return for July"* |
| 2 | System | Aggregates all sales invoices for the month → GSTR-1 data (B2B, B2C, exports, credit notes) |
| 3 | System | Aggregates all purchase entries with ITC → GSTR-3B data (output tax, input credit, net payable) |
| 4 | AI | Cross-checks: validates GSTIN format on all invoices, flags missing HSN codes, identifies ITC ineligible entries |
| 5 | AI | Presents summary: *"GSTR-1: 45 B2B invoices (₹32,00,000), 120 B2C invoices (₹8,50,000). GSTR-3B: Output tax ₹7,29,000, Input credit ₹2,15,000, Net payable ₹5,14,000"* |
| 6 | System | Generates data in GST portal-compatible format (JSON/Excel) for filing |
| 7 | Tax Consultant | Downloads and files on GST portal |

### Post Conditions
- ✅ GSTR-1 and GSTR-3B data compiled
- ✅ Discrepancies flagged for review
- ✅ Export file generated for portal upload

---

## BP-018: Monthly Payroll Processing [P3]

### Business Objective
Calculate monthly salaries for all employees including statutory deductions (PF, ESI, TDS, Professional Tax), generate payslips, and create accounting entries.

### Main Flow

| Step | Actor | Action |
|:-----|:------|:-------|
| 1 | Owner/Accountant | Initiates: *"Process payroll for July"* or navigates to HR → Payroll |
| 2 | System | For each employee, calculates: Gross Salary (basic + HRA + allowances) |
| 3 | System | Calculates deductions: PF Employee (12% of basic), ESI Employee (0.75%), TDS (based on projected annual income and slab), Professional Tax (per state rules), LOP deduction (if applicable) |
| 4 | System | Calculates employer contributions: PF Employer (12%), ESI Employer (3.25%) |
| 5 | System | Computes Net Pay = Gross – Deductions |
| 6 | AI | Presents payroll summary: *"July payroll for 5 employees: Total gross ₹2,50,000. Total deductions ₹42,000. Total net pay ₹2,08,000. Employer PF+ESI: ₹38,125."* |
| 7 | Owner | Reviews and approves |
| 8 | System | Creates journal entries: Salary Expense Dr / PF Payable Cr / ESI Payable Cr / TDS Payable Cr / PT Payable Cr / Bank Cr |
| 9 | System | Generates individual payslips (PDF) |
| 10 | System | Sends payslips to employees via email |
| 11 | System | Updates PF/ESI/TDS liability registers for challan generation |

### Post Conditions
- ✅ Payroll calculated for all active employees
- ✅ Net pay amounts ready for bank transfer
- ✅ Statutory deductions recorded as liabilities
- ✅ Payslips generated and distributed
- ✅ Expense entries posted to P&L

---

*End of Chapter 5 – Business Processes*

*Next: Chapter 6 – Functional Requirements*
