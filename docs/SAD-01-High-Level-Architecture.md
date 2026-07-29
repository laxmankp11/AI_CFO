# Software Architecture Design (SAD)

---

# Part 1: High-Level System Architecture

---

## 1.0 Architectural Assumptions
Based on the approved Business Requirements Document (BRD) and best practices for the chosen tech stack (Laravel + Python + Next.js + Flutter), this architecture proceeds with the following foundational decisions:

1. **Multi-Tenancy:** Single shared PostgreSQL database utilizing a strict `tenant_id` column on all tenant-specific tables, enforced via Row-Level Security (RLS) or global ORM scopes in Laravel to guarantee data isolation.
2. **API Paradigm:** Standard RESTful JSON APIs using Laravel API Resources for frontend-backend communication.
3. **AI Communication:** Synchronous REST API communication between Laravel and the Python AI Microservice for real-time Voice-to-Text and NLP extractions, with Redis queues reserved for background tasks (e.g., OCR processing, batch reports).

---

## 1.1 Context Diagram (C4 Level 1)

The Context Diagram provides a macro view of the AICFO system, illustrating the users and external systems it interacts with.

```mermaid
C4Context
    title System Context diagram for AICFO

    Person(owner, "Business Owner", "Uses mobile app to record voice transactions and view dashboards.")
    Person(accountant, "Accountant", "Uses web app for detailed ledger review, reconciliation, and tax prep.")
    
    System(aicfo, "AICFO Platform", "Voice-first AI accounting system providing automated bookkeeping and Virtual CFO advisory.")

    System_Ext(openai, "OpenAI APIs", "Whisper STT, GPT-4o NLP, and TTS services.")
    System_Ext(vision, "Google Cloud Vision", "OCR for vendor bills and receipts.")
    System_Ext(gstn, "GSTN / ClearTax", "GSTIN validation and E-Invoicing.")
    System_Ext(comm, "Communication APIs", "Resend (Email), Twilio (SMS), WhatsApp API.")
    System_Ext(payment, "Payment Gateway", "Razorpay/Stripe for subscription and invoice payments.")
    System_Ext(bank, "Open Banking API", "Sahamati/Setu for automated bank feeds.")

    Rel(owner, aicfo, "Speaks transactions, views reports", "Mobile App")
    Rel(accountant, aicfo, "Manages ledgers, exports reports", "Web Browser")
    
    Rel(aicfo, openai, "Sends audio/prompts, receives text/JSON", "HTTPS")
    Rel(aicfo, vision, "Sends images, receives raw text", "HTTPS")
    Rel(aicfo, gstn, "Validates GSTINs, fetches IRNs", "HTTPS")
    Rel(aicfo, comm, "Triggers notifications and invoices", "HTTPS")
    Rel(aicfo, payment, "Creates payment links, receives webhooks", "HTTPS")
    Rel(aicfo, bank, "Fetches daily bank statements", "HTTPS")
```

---

## 1.2 Container Diagram (C4 Level 2)

The Container Diagram zooms into the `AICFO Platform` to show the distinct deployable units (containers) that make up the system, their responsibilities, and how they communicate.

```mermaid
C4Container
    title Container diagram for AICFO Platform

    Person(owner, "Business Owner", "Uses mobile app")
    Person(accountant, "Accountant", "Uses web app")

    System_Boundary(c1, "AICFO Platform") {
        Container(mobile_app, "Mobile App", "Flutter", "Provides voice-first interface, offline caching, and executive dashboards.")
        Container(web_app, "Web App", "Next.js, React", "Provides detailed data grids, complex reporting, and manual entry forms.")
        
        Container(api_gateway, "Core Backend API", "Laravel 11, PHP", "Handles authentication, RBAC, business logic, accounting rules, and API routing.")
        
        Container(ai_service, "AI Microservice", "Python, FastAPI", "Handles RAG prompt construction, strict JSON extraction from LLMs, and confidence scoring.")
        
        ContainerDb(database, "Primary Database", "PostgreSQL 16", "Stores multi-tenant financial data, audit logs, and system config.")
        ContainerDb(cache, "Cache & Queue", "Redis", "Caches RAG context, handles async jobs (emails, webhooks).")
        Container(storage, "Object Storage", "AWS S3", "Stores uploaded receipts, generated PDFs, and audio backups.")
    }

    System_Ext(openai, "OpenAI APIs", "LLM & Voice Services")
    System_Ext(vision, "Google Cloud Vision", "OCR Engine")

    Rel(owner, mobile_app, "Interacts via Voice/Touch")
    Rel(accountant, web_app, "Interacts via Web")

    Rel(mobile_app, api_gateway, "Makes REST API calls", "HTTPS/JSON")
    Rel(web_app, api_gateway, "Makes REST API calls", "HTTPS/JSON")

    Rel(api_gateway, database, "Reads/Writes financial data", "SQL")
    Rel(api_gateway, cache, "Publishes jobs, reads cache", "Redis Protocol")
    Rel(api_gateway, storage, "Uploads/Downloads files", "HTTPS/S3 API")

    Rel(api_gateway, ai_service, "Forwards voice transcripts & extraction requests", "Internal HTTPS/REST")
    
    Rel(ai_service, database, "Reads RAG context (Read-Only)", "SQL")
    Rel(ai_service, openai, "Requests STT, NLP extraction", "HTTPS")
    Rel(ai_service, vision, "Requests OCR processing", "HTTPS")
```

---

## 1.3 Container Responsibilities

### 1. Flutter Mobile App (Frontend)
- **Primary Interface:** The main tool for Business Owners.
- **Key Features:** One-tap voice recording, instant transaction confirmations, highly visual KPI dashboards.
- **Offline Capability:** Queues voice notes locally if the network drops, syncing to the API Gateway when restored.

### 2. Next.js Web App (Frontend)
- **Primary Interface:** The main tool for Accountants and Tax Consultants.
- **Key Features:** Dense data grids (Ag-Grid or similar), manual journal entry forms, advanced filtering, and PDF/Excel report exports.

### 3. Laravel Core Backend (API Gateway & Logic)
- **The Source of Truth:** Enforces the "Fundamental Accounting Rules" and "Compliance Rules" defined in Chapter 7.
- **Responsibilities:**
  - JWT Authentication and Role-Based Access Control (RBAC).
  - Enforcing PostgreSQL Row-Level Security (`tenant_id`).
  - Double-entry journaling logic.
  - Generating PDFs for invoices and reports.
  - Acting as the gateway: It receives voice audio from Flutter, forwards it to the Python AI service, waits for the structured JSON response, applies accounting logic, and returns the result to Flutter.

### 4. Python FastAPI AI Service
- **The Brain:** Completely isolated from financial write operations to prevent hallucination-induced data corruption.
- **Responsibilities:**
  - Interfacing with OpenAI (Whisper, GPT-4o).
  - Executing Retrieval-Augmented Generation (RAG) by fetching active Chart of Accounts and Vendor lists from PostgreSQL to inject into prompts.
  - Calculating the "Confidence Score" for each extraction.
  - Interfacing with OCR engines (Google Vision) for receipt parsing.
  - **Constraint:** This service only has READ access to the database (to fetch context) and MUST return its findings to Laravel via API. It cannot INSERT journal entries directly.

### 5. PostgreSQL Database
- **Structure:** A single, robust relational database.
- **Why Postgres?** Excellent support for JSONB (crucial for storing flexible AI extraction metadata alongside rigid journal lines) and robust Row-Level Security features to ensure tenant isolation.

### 6. Redis (Cache & Queue)
- **Caching:** Stores frequently accessed RAG context (e.g., active COA list) to reduce database load during rapid AI prompt generation.
- **Queues:** Handles async tasks triggered by Laravel (e.g., sending email invoices, processing scheduled payment reminders, webhooks).
