# Software Architecture Design (SAD)

---

# Part 4: AI Service Architecture (Python Microservice)

---

## 4.0 Overview

The AI Service is a standalone microservice built with **Python 3.12** and **FastAPI**. It is strictly internal; it only accepts traffic from the Laravel API Gateway. Its sole purpose is to convert unstructured inputs (audio, text, images) into highly structured, validated JSON that adheres to rigid accounting constraints.

---

## 4.0.1 Enterprise Multi-Agent & Orchestration Architecture

To support compound, multi-step business prompts (e.g. Master Data Setup + Purchases + Sales + Accounting Posting in a single utterance), the AI system employs a **Planning Agent & Workflow Orchestrator** pattern:

```
                                  AI CFO
                                    │
                              Intent Router
                                    │
                             Planning Agent
                                    │
                           Workflow Orchestrator
                                    │
       ┌─────────────┬─────────────┼─────────────┬─────────────┐
       │             │             │             │             │
 Product Agent Customer Agent Purchase Agent Sales Agent Reporting Agent
       │             │             │             │             │
       └─────────────┴─────────────┼─────────────┴─────────────┘
                                    │
                             Accounting Engine
                                    │
                            Double Entry Ledger
                                    │
                             Reporting Engine
```

### Architectural Layer Responsibilities:
1. **Intent Router**: Determines overall context and delegates complex compound requests to the Planning Agent.
2. **Planning Agent**: Decomposes multi-intent prompts into an ordered, dependency-aware DAG (Directed Acyclic Graph) of execution steps.
3. **Workflow Orchestrator**: Manages stateful execution, validation, atomic rollback, and audit logging across step boundaries.
4. **Domain Agents (Product, Customer, Purchase, Sales, Reporting)**: Specialized worker agents with strict single-responsibility boundaries.
5. **Accounting & Reporting Engine**: Enforces rigid double-entry validation ($\text{Debits} = \text{Credits}$) and immutability.

---

## 4.1 Microservice Boundaries

- **Input:** Receives authenticated requests from Laravel containing Base64 Audio, Text, or Image URIs, along with the `tenant_id`.
- **Database Access:** It connects to a Read-Only replica of the PostgreSQL database to fetch RAG context (Entities, COA, Rules). **It cannot perform INSERT or UPDATE operations on the ledger.**
- **Output:** Returns a strictly typed JSON object back to Laravel.

---

## 4.2 The RAG Pipeline (Retrieval-Augmented Generation)

When a voice transaction arrives, the Python service executes a fast RAG pipeline before calling the LLM. This prevents hallucination by grounding the LLM in the tenant's actual data.

### Pipeline Steps:

1. **Audio to Text (STT):**
   - Transmits Base64 audio to OpenAI Whisper API (or local Whisper instance).
   - Receives raw text transcript (e.g., "Paid 4500 to Rajesh for repairs").

2. **Context Retrieval (Cache/DB):**
   - Queries the DB/Redis for the active `tenant_id`:
     - **Active COA:** List of expense and income accounts.
     - **Active Entities:** Recent Vendors and Customers.
     - **Correction Memory:** Queries the `correction_logs` table for recent corrections matching keywords in the transcript (e.g., "Rajesh").

3. **Prompt Construction:**
   - Assembles the System Prompt combining the Persona (Virtual CFO), Anti-Hallucination rules, and the retrieved tenant context.

---

## 4.3 LLM Structured Outputs

To guarantee the LLM returns JSON that Laravel can parse without error, we utilize **OpenAI Structured Outputs** (JSON Schema).

### The JSON Schema Definition (Pydantic Model)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class ExtractedEntity(BaseModel):
    id: Optional[str] = Field(description="UUID of the existing entity if matched exactly.")
    name: str = Field(description="Name of the vendor or customer.")
    is_new: bool = Field(description="True if no exact match was found in the provided context list.")

class TransactionExtraction(BaseModel):
    intent: Literal["expense", "income", "asset_purchase", "transfer"]
    amount: float = Field(description="The total monetary amount. Must be positive.")
    entity: Optional[ExtractedEntity]
    category_id: Optional[str] = Field(description="UUID of the matched Chart of Account category.")
    payment_channel: Optional[Literal["cash", "bank_transfer", "upi", "credit_card"]]
```

The FastAPI service passes this Pydantic model directly to the OpenAI API, forcing the LLM to adhere to this exact schema.

---

## 4.4 Confidence Scoring Algorithm

The LLM does not reliably return confidence scores natively. The Python service calculates the **Aggregate Confidence Score** using a custom algorithm.

### Scoring Factors:
1. **Entity Match (Weight 0.3):**
   - Exact UUID match from context list = 1.0
   - Fuzzy match = 0.8
   - `is_new = true` = 0.6
2. **Category Match (Weight 0.3):**
   - Exact UUID match from COA = 1.0
   - No category extracted = 0.0
3. **Amount Extraction (Weight 0.3):**
   - Explicitly stated and parsed = 1.0
   - Implicit or calculated = 0.7
   - Missing = 0.0
4. **Channel Extraction (Weight 0.1):**
   - Present = 1.0
   - Missing = 0.0

**Calculation:**
`Aggregate = (Entity * 0.3) + (Category * 0.3) + (Amount * 0.3) + (Channel * 0.1)`

### Clarification Trigger:
If `Aggregate < 0.85`, the Python service identifies the lowest-scoring factor and generates a clarification question (e.g., "How was the amount paid?") and returns `status: clarification_needed` to Laravel.

---

## 4.5 API Endpoints (Internal)

These endpoints are called by Laravel, not the frontend.

- `POST /internal/v1/extract/transaction` (Takes audio/text, returns extraction)
- `POST /internal/v1/extract/receipt` (Takes image URI, calls Google Vision OCR, then NLP)
- `POST /internal/v1/advisory/query` (Takes a business question and raw DB metrics, returns a formatted advisory response)

---

*End of Software Architecture Design (SAD)*
