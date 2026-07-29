# AICFO — Business Requirements Document (BRD)

---

# Chapter 8 – Non-Functional Requirements

---

## 8.0 Overview

Non-Functional Requirements (NFRs) define system attributes such as performance, security, reliability, and usability. While functional requirements dictate *what* the system does, non-functional requirements dictate *how well* it does it. For an AI-driven financial application like AICFO, performance (especially AI latency) and security are as critical as the core accounting logic.

---

## 8.1 Performance Requirements

| Req ID | Description | Target / Metric |
|:-------|:------------|:----------------|
| **NFR-PER-001** | **AI Response Latency (Voice to Text to Logic):** The time from when a user finishes speaking a transaction to when the system presents the confirmation screen MUST be under a strict limit to maintain conversational flow. | **Target: < 2.5 seconds (P90)**<br>Max: 4.0 seconds (P99) |
| **NFR-PER-002** | **Dashboard Load Time:** The executive dashboard MUST load and render fully upon user login or refresh. | **Target: < 1.5 seconds (P90)**<br>Max: 3.0 seconds (P99) |
| **NFR-PER-003** | **Report Generation Time:** Standard financial reports (P&L, Balance Sheet, Trial Balance) for a standard date range (e.g., current FY) MUST generate quickly on demand. | **Target: < 3.0 seconds (P90)**<br>Max: 5.0 seconds (P99) |
| **NFR-PER-004** | **OCR Processing Time:** Extracting data from an uploaded receipt or invoice (PDF/Image) MUST complete and present the extraction preview within a reasonable timeframe. | **Target: < 5.0 seconds (P90)**<br>Max: 10.0 seconds (P99) |
| **NFR-PER-005** | **API Response Time:** All non-AI REST API endpoints MUST respond rapidly under normal load. | **Target: < 200 milliseconds (P95)** |

---

## 8.2 Scalability Requirements

| Req ID | Description | Target / Metric |
|:-------|:------------|:----------------|
| **NFR-SCA-001** | **Tenant Scalability (Phase 1 MVP):** The architecture MUST support a specified number of active businesses on a single infrastructure deployment without performance degradation. | **Initial Target: 100 concurrent businesses** |
| **NFR-SCA-002** | **Tenant Scalability (Phase 2+):** The architecture MUST scale horizontally to support significant growth. | **Target: 10,000+ businesses** (via containerization and read-replicas) |
| **NFR-SCA-003** | **Transaction Volume:** The system MUST handle the expected monthly transaction volume per business efficiently. | **Target:** Support up to **10,000 journal entries per month per business** without query timeouts on reports. |
| **NFR-SCA-004** | **AI Concurrency:** The AI microservice MUST handle concurrent requests during peak hours (e.g., end-of-day daily closings). | **Target: 50 concurrent AI extractions per second** |

---

## 8.3 Security & Privacy Requirements

| Req ID | Description | Implementation / Metric |
|:-------|:------------|:------------------------|
| **NFR-SEC-001** | **Data Isolation (Multi-Tenancy):** Complete logical separation of data between tenant businesses. A bug or API manipulation MUST NOT allow Tenant A to see Tenant B's data. | Implemented via **Row-Level Security (RLS)** in PostgreSQL and strict `tenant_id` scoping in the ORM layer. |
| **NFR-SEC-002** | **Data Encryption in Transit:** All communication between clients (Web/Mobile) and servers MUST be encrypted. | **TLS 1.2 or higher (HTTPS/WSS)** enforced universally. HSTS enabled. |
| **NFR-SEC-003** | **Data Encryption at Rest:** Sensitive data stored in the database and file storage MUST be encrypted on the disk. | **AES-256 encryption** for database volumes and cloud storage buckets (e.g., AWS S3 KMS). |
| **NFR-SEC-004** | **PII & Sensitive Field Encryption:** Highly sensitive fields (e.g., Employee Bank Account numbers, API Keys for payment gateways) MUST be encrypted at the application level before database insertion. | Application-level symmetric encryption. |
| **NFR-SEC-005** | **Password Security:** Passwords MUST NOT be stored in plain text. | Hashed using **bcrypt or Argon2** with unique salts. |
| **NFR-SEC-006** | **AI Prompt Security:** The system MUST sanitize user inputs to prevent Prompt Injection attacks aimed at exposing backend instructions or overriding business rules. | Input sanitization and bounded system prompts. |
| **NFR-SEC-007** | **Data Localization (India):** To comply with expected Indian regulatory preferences for financial data, primary servers and databases MUST be located within India. | Infrastructure hosted in **AWS Mumbai (ap-south-1)** or equivalent Indian data center. |

---

## 8.4 Availability & Reliability Requirements

| Req ID | Description | Target / Metric |
|:-------|:------------|:----------------|
| **NFR-REL-001** | **System Uptime (SLA):** The core application and database MUST be highly available. | **Target: 99.9% uptime** (approx. 43 minutes allowed downtime per month). |
| **NFR-REL-002** | **AI Degradation Fallback:** If third-party AI APIs (OpenAI/Anthropic) experience outages, the core accounting system MUST remain usable. | The system MUST seamlessly fallback to manual data entry forms. "AI Unavailable" banners are displayed, but the app does not crash. |
| **NFR-REL-003** | **Data Backup Frequency:** Financial data MUST be backed up frequently to prevent data loss in disaster scenarios. | **Continuous incremental backups** (e.g., WAL archiving) with **daily full snapshots**. |
| **NFR-REL-004** | **Recovery Point Objective (RPO):** Maximum acceptable amount of data loss in a disaster scenario. | **Target: < 15 minutes** |
| **NFR-REL-005** | **Recovery Time Objective (RTO):** Maximum acceptable time to restore the system from backup after a critical failure. | **Target: < 4 hours** |

---

## 8.5 Usability Requirements

| Req ID | Description | Target / Metric |
|:-------|:------------|:----------------|
| **NFR-USA-001** | **Mobile-First Responsiveness:** The web application MUST be fully usable on mobile browsers, as many SMB owners manage businesses from their phones. | 100% of owner-facing features accessible and readable on screens ≥ 375px wide. |
| **NFR-USA-002** | **Voice Interface Discoverability:** The microphone activation button MUST be the most prominent action on the mobile UI. | Placed in the bottom-center tab bar or floating action button. |
| **NFR-USA-003** | **Offline Voice Capture:** The mobile app MUST allow users to record voice transaction notes even when internet connectivity drops. | Notes are queued locally and automatically processed when connection is restored. |
| **NFR-USA-004** | **Accounting Jargon Minimization:** The UI MUST prioritize plain language over technical accounting terms where possible (e.g., "Money In" instead of "Debit Cash", "Money Out" instead of "Credit Cash"). | Enforced in UI copy reviews. Technical terms remain available for the 'Accountant' view. |
| **NFR-USA-005** | **Accessibility:** The application SHOULD comply with basic accessibility standards for color contrast and screen reader compatibility. | WCAG 2.1 AA (Target). |

---

*End of Chapter 8 – Non-Functional Requirements*

*This completes Sprint 2 of the BRD. Next up: Sprint 3 (Reports, Integrations, AI Specifics).*
