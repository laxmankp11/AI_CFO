# AICFO — Business Requirements Document (BRD)
## Version 1.0 | Draft

---

# Chapter 1 – Introduction

---

## 1.1 Purpose

This Business Requirements Document (BRD) defines the complete business requirements for **AICFO** — a voice-first, AI-powered Virtual CFO platform designed to automate bookkeeping, accounting, financial reporting, and business advisory for small and medium-sized businesses (SMBs) through natural conversational interaction.

The purpose of this document is to:

1. **Establish a shared understanding** of the product vision, capabilities, and boundaries among all stakeholders — including business owners, product designers, engineers, AI architects, and potential investors.
2. **Define every business capability** the platform must deliver, organized by functional modules (Finance, Sales, Purchase, Inventory, CRM, HR, AI, Communication, Analytics).
3. **Document the AI-specific behavioral requirements** that differentiate AICFO from traditional accounting software — including confidence scoring, human approval workflows, conversational intent extraction, and learning from corrections.
4. **Serve as the authoritative reference** for all downstream documents including the Software Architecture Document (SAD), Database Design, UI/UX Specifications, API Contracts, AI Prompt Engineering Guidelines, and QA Test Plans.
5. **Provide acceptance criteria** that clearly define when the MVP (Minimum Viable Product) and each subsequent release phase is considered complete and ready for production deployment.

> **Audience:** This document is intended for the founding team, product managers, software architects, frontend and backend developers, AI/ML engineers, QA engineers, UX designers, and potential investors or advisors evaluating the product.

---

## 1.2 Scope

### 1.2.1 In-Scope

AICFO is scoped as a **multi-tenant SaaS platform** accessible via web and mobile (iOS & Android) that provides the following capabilities:

| Scope Area | Description |
|:-----------|:------------|
| **Voice-First Transaction Entry** | Business owners dictate transactions in natural language (English and Hindi initially). The AI extracts structured financial data, asks clarifying questions when needed, and records entries into the accounting ledger with human confirmation. |
| **Automated Bookkeeping** | Double-entry journal creation, chart of accounts management, general ledger maintenance, bank reconciliation, and period-end closing — all triggered through voice/text conversation or automated rules. |
| **Indian Tax Compliance** | GST (CGST, SGST, IGST, GST ITC reconciliation, GSTR-1/3B filing assistance), TDS, TCS, and Income Tax estimation for businesses registered in India. |
| **Financial Reporting** | Profit & Loss Statement, Balance Sheet, Cash Flow Statement, Trial Balance, Aging Reports, and custom management reports — generated automatically from ledger data. |
| **Sales & Invoicing** | Customer management, quotation creation, sales order tracking, GST-compliant invoice generation (including e-invoicing), payment tracking, and credit note management. |
| **Purchase & Expense Management** | Vendor management, purchase order workflow, bill entry (manual and OCR-scanned), expense recording (voice and receipt photo), and vendor payment tracking. |
| **Inventory Management** | Product catalog, warehouse management, stock movement tracking, purchase-to-stock flow, sales-to-stock flow, and inter-warehouse transfers. |
| **CRM (Customer Relationship Management)** | Lead capture, opportunity pipeline, contact management, activity logging, and follow-up scheduling. |
| **HR & Payroll** | Employee records, attendance tracking, leave management, payroll calculation (with PF, ESI, TDS deductions), and reimbursement workflows. |
| **AI Virtual CFO** | Daily financial briefings, cash flow analysis, scenario-based advisory ("Can I afford to buy X?"), anomaly detection, and financial forecasting. |
| **Document Intelligence** | OCR-based invoice/receipt reading, email invoice extraction, and automated data entry from scanned documents. |
| **Communication** | Email, SMS, WhatsApp, and push notification channels for invoice delivery, payment reminders, and system alerts. |
| **Multi-Business & Multi-Branch** | A single user account can manage multiple businesses, each with isolated financial data, and each business can have multiple branches or cost centers. |
| **Audit Trail** | Every financial transaction, AI decision, and user action is logged with timestamps, actor identification, and before/after state snapshots for full auditability. |

### 1.2.2 Out of Scope (for Version 1.0)

The following capabilities are **not** part of the initial release but are acknowledged as future roadmap items:

| Out-of-Scope Item | Rationale |
|:-------------------|:----------|
| 3D Animated Avatar | UX enhancement, not core value. Deferred to Phase 4+. |
| Autonomous Bookkeeping (Zero Human Review) | Requires proven AI accuracy over time. Phase 5. |
| Direct Bank Account Integration (Open Banking APIs) | Regulatory and partnership complexity. Phase 3+. |
| Multi-Currency Accounting | Adds significant complexity. Phase 3. |
| Manufacturing / Bill of Materials (BOM) | Industry-specific module. Phase 4+. |
| Point-of-Sale (POS) Integration | Separate product vertical. Future consideration. |
| Statutory Audit / CA Collaboration Portal | Phase 3+. |
| White-Labeling / Reseller Model | Post product-market-fit. |
| Desktop Application (Windows/Mac native) | Web + Mobile covers primary use cases. |
| Regional Language Voice Support beyond English & Hindi | Phase 4+ (Tamil, Telugu, Kannada, Marathi, etc.). |

---

## 1.3 Objectives

### Business Objectives

| # | Objective | Measurable Target |
|:--|:----------|:------------------|
| BO-1 | **Eliminate bookkeeping friction** for SMB owners who lack accounting knowledge | 80% of daily transactions entered via voice/text without manual form-filling |
| BO-2 | **Reduce dependency on external accountants** for day-to-day bookkeeping | Business owners can independently run daily books and generate monthly reports |
| BO-3 | **Ensure Indian tax compliance** with minimal manual effort | GST, TDS, and TCS calculations are automatic with >99% accuracy on standard transactions |
| BO-4 | **Provide real-time financial visibility** to business owners | Dashboard reflects current P&L, cash position, and receivables/payables within 5 seconds of any transaction |
| BO-5 | **Build trust in AI-assisted accounting** through transparency and control | Every AI-generated entry includes confidence score, explanation, and one-click correction |

### Product Objectives

| # | Objective | Measurable Target |
|:--|:----------|:------------------|
| PO-1 | **Ship a functional MVP** within 3 months of development start | Core modules (Voice Entry, Ledger, GST, P&L, Dashboard) operational |
| PO-2 | **Achieve >90% extraction accuracy** on common business transaction patterns | Measured against the AI Conversation Catalog (Chapter 13) |
| PO-3 | **Support 100 concurrent businesses** on a single deployment | Infrastructure load-tested before public beta |
| PO-4 | **Deliver sub-2-second AI response time** for voice-to-ledger extraction | Measured end-to-end from speech completion to confirmation display |
| PO-5 | **Zero data leakage** between tenant businesses | Verified through automated security tests on every release |

### Technical Objectives

| # | Objective | Measurable Target |
|:--|:----------|:------------------|
| TO-1 | **API-first architecture** enabling web, mobile, and future integrations | 100% of business logic accessible via documented REST/GraphQL APIs |
| TO-2 | **Modular AI engine** allowing model swaps without application changes | AI service abstracted behind a standard interface; swappable between OpenAI, Anthropic, or self-hosted models |
| TO-3 | **Complete audit trail** for regulatory compliance | Every state change logged with actor, timestamp, and diff |
| TO-4 | **Automated test coverage** on financial calculation logic | >95% unit test coverage on accounting engine, GST calculations, and AI extraction |
| TO-5 | **CI/CD pipeline** with staging environment | Every merge to main automatically deployed to staging for review |

---

## 1.4 Business Goals

AICFO aims to become the **AI-native accounting platform of choice for Indian SMBs** — businesses that currently use spreadsheets, paper ledgers, or basic Tally installations but find traditional accounting software intimidating, time-consuming, or expensive.

### Short-Term Goals (0–6 months)
1. Launch MVP with voice-first bookkeeping, GST compliance, and financial reporting.
2. Onboard 50–100 pilot businesses for feedback and AI accuracy calibration.
3. Establish AI accuracy baselines and correction-learning loops.

### Medium-Term Goals (6–18 months)
1. Expand to full Sales, Purchase, Inventory, CRM, and HR modules.
2. Introduce bank reconciliation, e-invoicing, and WhatsApp integration.
3. Reach 1,000+ active businesses.
4. Achieve AI confidence levels that allow semi-autonomous bookkeeping (auto-post for high-confidence entries, human review for low-confidence entries).

### Long-Term Vision (18–36 months)
1. Evolve AICFO from an accounting tool into an **AI Business Operating System** — where business owners interact with a single conversational AI that handles bookkeeping, invoicing, inventory, payroll, CRM, tax filing, and strategic financial advisory.
2. Support multiple Indian languages (Hindi, Tamil, Telugu, Marathi, Kannada, Bengali, Gujarati).
3. Expand to other emerging markets with similar SMB pain points (Southeast Asia, Africa, Latin America).
4. Explore autonomous bookkeeping with confidence-scored auto-posting and anomaly detection.
5. Position for Series A funding with proven unit economics and retention metrics.

---

## 1.5 Definitions & Glossary

| Term | Definition |
|:-----|:-----------|
| **AICFO** | The product name. Stands for "AI Chief Financial Officer." |
| **SMB** | Small and Medium-sized Business. The primary target user segment. Typically businesses with 1–50 employees and annual revenue under ₹50 crore. |
| **Virtual CFO** | The AI persona that greets users, provides financial briefings, processes spoken transactions, asks clarifying questions, and offers financial advisory. Not a human CFO. |
| **Voice-First** | A design philosophy where the primary input method is spoken natural language, with text input as a secondary alternative. The system is optimized for voice interaction. |
| **Double-Entry Bookkeeping** | An accounting method where every financial transaction affects at least two accounts — a debit and a credit — ensuring the accounting equation (Assets = Liabilities + Equity) always balances. |
| **Chart of Accounts (COA)** | A structured list of all accounts (Assets, Liabilities, Equity, Income, Expenses) used by a business to classify and record financial transactions. |
| **Journal Entry** | A record of a financial transaction in the accounting system, specifying the accounts debited and credited, amounts, date, narration, and supporting references. |
| **General Ledger** | The master record of all journal entries, organized by account. The source of truth for all financial reports. |
| **Trial Balance** | A report listing all accounts and their debit/credit balances at a point in time. If double-entry is correct, total debits equal total credits. |
| **GST** | Goods and Services Tax. India's indirect tax system with components: CGST (Central), SGST (State), IGST (Inter-state), and Cess. |
| **GSTIN** | GST Identification Number. A 15-digit alphanumeric code assigned to every registered GST taxpayer. |
| **ITC** | Input Tax Credit. The GST paid on purchases (inputs) that can be offset against GST collected on sales (output). |
| **GSTR-1** | Monthly/quarterly GST return for outward supplies (sales). |
| **GSTR-3B** | Monthly summary GST return for tax payment. |
| **TDS** | Tax Deducted at Source. The payer deducts tax before paying the payee, as mandated by the Income Tax Act. |
| **TCS** | Tax Collected at Source. The seller collects tax from the buyer at the time of sale for specified goods. |
| **e-Invoice** | Electronically generated invoice registered on the GST Network's Invoice Registration Portal (IRP), mandatory for businesses above ₹5 crore turnover. |
| **Multi-Tenant** | A software architecture where a single instance of the application serves multiple businesses (tenants), with complete data isolation between them. |
| **Confidence Score** | A numerical value (0.0 to 1.0) assigned by the AI to each extracted data field, indicating how certain the AI is about the extraction. Used to determine whether to auto-post or request human confirmation. |
| **STT** | Speech-to-Text. Converting spoken audio into written text. |
| **TTS** | Text-to-Speech. Converting written text into spoken audio output. |
| **NLP** | Natural Language Processing. AI techniques for understanding, interpreting, and generating human language. |
| **OCR** | Optical Character Recognition. Extracting text and structured data from images or scanned documents. |
| **RAG** | Retrieval-Augmented Generation. An AI technique where the model retrieves relevant context (e.g., past transactions, business memory) before generating a response. |
| **P&L** | Profit and Loss Statement (also called Income Statement). Shows revenue, expenses, and net profit/loss over a period. |
| **Balance Sheet** | Financial statement showing Assets, Liabilities, and Equity at a specific point in time. |
| **Cash Flow Statement** | Financial statement showing cash inflows and outflows from Operating, Investing, and Financing activities. |
| **Depreciation** | The systematic allocation of the cost of a tangible asset over its useful life. Methods include Straight-Line (SLM) and Written Down Value (WDV). |
| **Financial Year (FY)** | The 12-month period used for accounting and tax purposes. In India, the standard FY is April 1 to March 31. |
| **Assessment Year (AY)** | The year following the Financial Year, in which income earned during the FY is assessed and taxed. |
| **HSN Code** | Harmonized System of Nomenclature. A standardized international code for classifying goods for GST purposes. |
| **SAC Code** | Services Accounting Code. Used to classify services under GST. |
| **Reconciliation** | The process of matching two sets of records (e.g., bank statement vs. accounting ledger) to ensure they agree. |
| **Aging Report** | A report categorizing outstanding receivables or payables by the length of time they have been overdue (e.g., 0–30 days, 31–60 days, 61–90 days, 90+ days). |

---

## 1.6 References

| # | Reference | Description |
|:--|:----------|:------------|
| R-1 | [OpenAI API Reference](https://platform.openai.com/docs/api-reference) | Audio transcription (Whisper), chat completions, structured outputs, TTS, and Realtime API documentation. |
| R-2 | [OpenAI Responses API](https://platform.openai.com/docs/guides/responses) | The recommended API for building AI assistants (replaces deprecated Assistants API). |
| R-3 | [Anthropic Claude API](https://docs.anthropic.com/) | Alternative LLM provider for NLP extraction and advisory reasoning. |
| R-4 | [GST Council India](https://gstcouncil.gov.in/) | Official GST rules, rates, return filing formats, and compliance requirements. |
| R-5 | [GSTN e-Invoice Portal](https://einvoice1.gst.gov.in/) | e-Invoice registration, IRN generation, and API specifications. |
| R-6 | [Indian Accounting Standards (Ind AS)](https://www.mca.gov.in/content/mca/global/en/acts-rules/acs/indian-accounting-standards.html) | Financial reporting standards applicable to Indian companies. |
| R-7 | [Income Tax Act, 1961](https://incometaxindia.gov.in/) | TDS/TCS rules, depreciation rates (Section 32), and assessment procedures. |
| R-8 | [Indian Companies Act, 2013](https://www.mca.gov.in/) | Requirements for financial statement preparation, audit, and filing. |
| R-9 | [AICFO Product Vision & Tech Stack](file:///Users/apple/.gemini/antigravity-ide/brain/e4119e58-9fbc-465a-8ecb-197337db9d51/brd_strategy_and_tech_stack.md) | The approved BRD strategy and technology stack recommendation. |
| R-10 | [Tally Prime](https://tallysolutions.com/) | Incumbent accounting software dominant in India. Competitive reference. |
| R-11 | [Zoho Books](https://www.zoho.com/books/) | Cloud accounting software with GST compliance. Competitive reference. |
| R-12 | [QuickBooks India](https://quickbooks.intuit.com/in/) | International cloud accounting platform with India localization. Competitive reference. |
| R-13 | [Khatabook](https://khatabook.com/) | Mobile-first digital ledger app targeting micro-businesses in India. Competitive reference for voice/simplicity positioning. |

---

## 1.7 Assumptions

The following assumptions underpin this BRD. If any assumption proves incorrect, the affected requirements must be re-evaluated.

### Business Assumptions

| # | Assumption |
|:--|:-----------|
| A-1 | The primary target market is **Indian SMBs** (sole proprietorships, partnerships, and private limited companies) with annual turnover between ₹10 lakh and ₹50 crore. |
| A-2 | Target users are **business owners or managers**, not trained accountants. They understand their business operations but lack formal accounting knowledge. |
| A-3 | Users are comfortable speaking in **English or Hindi** (or a mix — "Hinglish") for voice interactions. Regional language support is a future enhancement. |
| A-4 | Most target users already own a **smartphone** (Android or iOS) and have access to **reliable mobile internet** (4G/5G). |
| A-5 | Users will accept a **brief AI training period** (first 2–4 weeks) where the AI requires more confirmations and corrections before it learns their business patterns. |
| A-6 | Indian **GST rates and rules** will remain broadly stable. If significant changes occur (e.g., new return formats), the system will require an update within the compliance window. |

### Technical Assumptions

| # | Assumption |
|:--|:-----------|
| A-7 | **OpenAI and/or Anthropic APIs** will remain available, performant, and reasonably priced. The architecture includes an abstraction layer to switch providers if needed. |
| A-8 | **Web Speech API** (browser-based STT) is available in modern browsers (Chrome, Edge, Safari) as a fallback. Primary STT is server-side Whisper. |
| A-9 | **PostgreSQL** is the primary database. The schema design assumes PostgreSQL-specific features (JSONB columns, row-level security, trigram indexes). |
| A-10 | The development team has access to **macOS or Linux** development environments with Docker support. |
| A-11 | **Third-party integrations** (payment gateways, SMS providers, WhatsApp Business API) will provide stable, documented APIs with reasonable SLAs. |
| A-12 | The **founding team** can handle initial customer support and onboarding for the first 100 pilot businesses without dedicated support staff. |

---

## 1.8 Constraints

### Regulatory Constraints

| # | Constraint | Impact |
|:--|:-----------|:-------|
| C-1 | **GST compliance** is mandatory. All invoices must include GSTIN, HSN/SAC codes, and correct tax breakdowns. GSTR-1 and GSTR-3B data must be exportable in the prescribed format. | Financial module design must enforce GST rules at the data entry level, not just at report generation. |
| C-2 | **e-Invoicing** is mandatory for businesses with turnover > ₹5 crore. The system must integrate with the GSTN IRP for Invoice Registration Number (IRN) generation. | Requires API integration with the GST e-Invoice portal. Phase 2 feature. |
| C-3 | **TDS compliance** requires correct tax deduction at source for payments above prescribed thresholds (e.g., rent > ₹2,40,000/year, professional fees > ₹30,000/year). | Purchase and payment modules must include TDS applicability checks and deduction tracking. |
| C-4 | **Data localization**: Financial data for Indian businesses must be stored on servers located in India (or at minimum, must comply with RBI and SEBI data localization guidelines if applicable). | Infrastructure must use India-region data centers (AWS Mumbai, DigitalOcean Bangalore). |

### Technical Constraints

| # | Constraint | Impact |
|:--|:-----------|:-------|
| C-5 | **AI latency**: Voice-to-ledger round trip (STT → NLP extraction → response) must complete within **2 seconds** for a satisfactory user experience. | Requires efficient prompt engineering, response caching for common patterns, and low-latency API calls. |
| C-6 | **AI accuracy vs. autonomy trade-off**: The AI must never silently record a transaction it is uncertain about. Below a defined confidence threshold (initially 0.85), the system must request human confirmation. | Confidence scoring logic must be robust. False confidence is worse than asking too many questions. |
| C-7 | **Offline capability**: Mobile app must allow **voice note recording** when offline, with automatic processing and sync when connectivity is restored. Full offline accounting is not required for MVP. | Mobile app needs local storage for queued voice notes and a sync engine. |
| C-8 | **Browser compatibility**: Web application must function on Chrome (latest 2 versions), Safari (latest 2 versions), Edge (latest 2 versions), and Firefox (latest 2 versions). | Frontend must avoid vendor-specific APIs without polyfills. |

### Business Constraints

| # | Constraint | Impact |
|:--|:-----------|:-------|
| C-9 | **Founding team size**: Initial development team is small (1–3 developers). Technology choices must maximize individual productivity and minimize operational overhead. | Preference for managed services over self-hosted infrastructure. Laravel + managed PostgreSQL + managed Redis. |
| C-10 | **Budget**: Pre-revenue startup with bootstrapped or early-stage funding. AI API costs (OpenAI/Anthropic) are a significant variable cost that scales with user activity. | Must implement token usage tracking, prompt optimization, caching of repeated patterns, and tiered pricing to manage AI costs. |
| C-11 | **Time-to-MVP**: Target 3 months from development start to functional MVP. Feature scope for MVP must be ruthlessly prioritized. | Only Phase 1 modules (Voice Entry, Finance Core, GST, Dashboard, Basic Reports) are in MVP scope. |
| C-12 | **Competitive landscape**: Tally, Zoho Books, and Khatabook are established players. AICFO must differentiate on **voice-first UX** and **AI intelligence**, not on feature parity with mature ERPs. | Avoid feature-creep. Focus on doing voice-first bookkeeping exceptionally well before expanding modules. |

---

## 1.9 Document Conventions

Throughout this BRD, the following conventions are used:

| Convention | Meaning |
|:-----------|:--------|
| **MUST** | A mandatory requirement. The system cannot ship without it. |
| **SHOULD** | A strongly recommended requirement. Omission requires documented justification. |
| **MAY** | An optional requirement. Included if time and resources permit. |
| **BR-XXX-NNN** | Business Requirement ID. `XXX` = module code (FIN, SALE, AI, etc.), `NNN` = sequential number. |
| **[MVP]** | This requirement is in scope for the Minimum Viable Product (Phase 1, 3-month target). |
| **[P2]**, **[P3]**, etc. | This requirement is deferred to Phase 2, Phase 3, etc. |
| *Italicized text* | Example user utterances or AI responses. |
| `Monospace text` | Technical identifiers, API endpoints, database column names, or configuration values. |

---

*End of Chapter 1 – Introduction*

*Next: Chapter 2 – Business Overview*
