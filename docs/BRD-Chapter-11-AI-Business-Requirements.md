# AICFO — Business Requirements Document (BRD)

---

# Chapter 11 – AI Business Requirements

---

## 11.0 Overview

Traditional software BRDs focus on deterministic workflows (if X happens, do Y). AICFO, being an AI Business Operating System, relies on probabilistic models (Large Language Models) to extract intents, classify transactions, and provide advisory. 

This chapter defines the **behavioral boundaries, prompt governance, and reasoning constraints** the AI must adhere to. These requirements ensure the AI acts as a reliable, compliant, and trustworthy financial assistant rather than a generic chatbot.

---

## 11.1 System Persona & Tone

The AI MUST consistently adopt the persona of a **Virtual Chief Financial Officer (Virtual CFO)**.

| Attribute | Requirement | Example |
|:----------|:------------|:--------|
| **Professional yet Approachable** | The AI MUST use clear, non-academic language. It MUST avoid dense accounting jargon when speaking to the Business Owner. | *Instead of:* "Credit accounts receivable."<br>*Use:* "I've recorded that ABC Company still owes you ₹50,000." |
| **Objective & Data-Driven** | The AI MUST NOT use emotional or subjective language when discussing financials. | *Instead of:* "Your marketing spend is terrible."<br>*Use:* "Marketing spend is up 40%, but revenue only grew 5%." |
| **Subservient but Proactive** | The AI serves the owner but MUST proactively highlight risks. | "I've recorded that payment. However, notice your bank balance will drop below your upcoming rent requirement." |
| **Identity Transparency** | The AI MUST never pretend to be a human. | "As your AI assistant, I recommend..." |

---

## 11.2 Context Boundaries (RAG Strategy)

When answering queries or processing transactions, the AI's reasoning is bounded by the context provided to it. To ensure strict multi-tenant security and prevent hallucination, the system MUST implement the following Retrieval-Augmented Generation (RAG) constraints:

| Requirement ID | Description |
|:---------------|:------------|
| **AI-CTX-001** | **Tenant Isolation:** The context window for any AI request MUST ONLY contain data (ledgers, master data, history) belonging to the currently authenticated `tenant_id`. |
| **AI-CTX-002** | **Master Data Pre-loading:** During a transaction extraction request, the prompt MUST be injected with the business's active Chart of Accounts, active Vendors, and active Customers to force the LLM to map to existing entities rather than hallucinating new ones. |
| **AI-CTX-003** | **Historical Precedent:** For expense extraction, the prompt MUST include the last 5 transactions with the identified vendor (if any) to encourage consistent categorization (e.g., if "AWS" is always mapped to "Software Subscriptions"). |
| **AI-CTX-004** | **Time Awareness:** Every prompt MUST include the current date and time in the user's timezone (IST) so relative terms like "yesterday", "last month", and "today" are parsed correctly. |
| **BR-AI-001** | **Identity Resolution:** Before creating a financial transaction, the AI MUST identify the acting party using a defined priority (explicit name > logged-in user role/identity > business context). The LLM MUST receive session context (user name, role, permissions, business profile) with every prompt to correctly interpret terms like "I", "my", or "our". If an accountant says "I invested", it should flag for clarification rather than assume they are the investor. |

---

## 11.3 Confidence Scoring & Escalation Matrix

Every field extracted by the NLP engine MUST be assigned a Confidence Score (0.0 to 1.0). The **Aggregate Transaction Confidence** is the lowest score among the mandatory fields (Intent, Amount, Account, Date).

The system MUST enforce the following escalation matrix based on the Aggregate Confidence:

| Aggregate Score | AI Action | Human Intervention Required |
|:----------------|:----------|:----------------------------|
| **≥ 0.95** (Very High) | Auto-Post to Ledger | None. (Only available in Phase 2+ after user explicitly enables auto-posting). |
| **0.85 – 0.94** (High) | Draft Entry + Prompt Confirmation | **Business Owner** taps "Confirm" or says "Yes". |
| **0.70 – 0.84** (Medium) | Draft Entry + Ask Clarification | AI asks up to 3 clarification questions. If unresolved, routes to **Accountant** for review. |
| **< 0.70** (Low) | Reject Extraction | AI apologizes and asks the user to repeat or rephrase the transaction. No draft entry is created. |

*Note: In Phase 1 (MVP), ALL transactions, regardless of score, cap out at the "High" tier and require Business Owner confirmation.*

---

## 11.4 Clarification Dialogue Rules

When the AI lacks sufficient information or confidence (Score 0.70 - 0.84), it MUST trigger a clarification dialogue (as defined in BP-004).

| Requirement ID | Description |
|:---------------|:------------|
| **AI-CLR-001** | **Max Questions Limit:** The AI MUST NOT ask more than 3 consecutive clarification questions for a single transaction. If unresolved after 3 turns, it MUST save as "Draft - Needs Review". |
| **AI-CLR-002** | **Single Question Focus:** The AI MUST ask for only ONE missing piece of information at a time. (e.g., Ask for Amount, then ask for Vendor — do not ask for both simultaneously). |
| **AI-CLR-003** | **Quick Replies:** Where the missing field has a limited set of valid options (e.g., Payment Channel: Cash, Bank, UPI), the AI MUST provide UI buttons for those options alongside the voice/text prompt. |

---

## 11.5 Learning & Memory Management

AICFO becomes more valuable over time because it "learns" the specific patterns of the business. 

| Requirement ID | Description |
|:---------------|:------------|
| **AI-MEM-001** | **Correction Logging:** Every time a user edits a Draft Entry generated by the AI (e.g., changing the Category from 'Office Expense' to 'Repairs'), the system MUST log a `TrainingPair` (Utterance + Original Output + Corrected Output). |
| **AI-MEM-002** | **Pattern Adaptation:** The AI prompt generation MUST prioritize the user's historical `TrainingPairs` over standard accounting defaults for that specific business. |
| **AI-MEM-003** | **Memory Forgetting:** If a user explicitly corrects a previously learned pattern (e.g., changes the default categorization of "AWS"), the system MUST deprecate the older pattern to prevent the AI from repeatedly making the outdated suggestion. |
| **AI-MEM-004** | **Memory Portability:** The "learned memory" (custom entity mappings, categorization rules) belongs to the Business Owner and MUST be exportable or deletable upon request. |

---

## 11.6 Anti-Hallucination Guardrails

Financial data requires absolute precision. LLMs are prone to hallucinating numbers if not strictly constrained.

| Requirement ID | Description |
|:---------------|:------------|
| **AI-GRD-001** | **No Synthetic Math:** The AI MUST NOT perform mathematical aggregations (Sums, Averages, Percentages) internally within the LLM. All math MUST be executed by standard SQL/Backend logic, and the exact result provided to the LLM to format into a sentence. |
| **AI-GRD-002** | **Strict Output Formatting:** Transaction extraction MUST utilize "Structured Outputs" (e.g., OpenAI JSON Schema mode) to ensure the LLM returns exactly the fields required by the database schema, with strict type checking (e.g., `amount` must be a Float, not a String). |
| **AI-GRD-003** | **Advisory Disclaimers:** Whenever the AI provides predictive advice ("You will run out of cash in 3 months") or tax advice, it MUST append a predefined disclaimer: *"Note: This is an AI-generated analysis. Please verify with your accountant before making major financial decisions."* |

---

*End of Chapter 11 – AI Business Requirements*

*Next: Chapter 12 – Acceptance Criteria*
