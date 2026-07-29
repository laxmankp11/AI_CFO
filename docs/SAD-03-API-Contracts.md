# Software Architecture Design (SAD)

---

# Part 3: API Contracts (Frontend ↔ Backend)

---

## 3.0 Overview

The AICFO Core Backend (Laravel) exposes a RESTful JSON API. This API serves both the Flutter Mobile App (Owner interface) and the Next.js Web App (Accountant interface).

### Global API Standards
- **Base URL:** `https://api.aicfo.com/v1`
- **Authentication:** Bearer Token (JWT / Laravel Sanctum) sent in `Authorization: Bearer <token>` header.
- **Tenant Context:** Passed via custom header `X-Tenant-ID: <uuid>` on every request.
- **Content-Type:** `application/json` (except for direct file uploads).

---

## 3.1 Core Workflow: Voice Transaction Submission

This is the primary endpoint for the voice-first experience. It routes data from the client, through Laravel, to the Python AI service, and returns the draft extraction.

### `POST /transactions/voice`

**Purpose:** Submits an audio recording (or raw text fallback) to be processed by the Virtual CFO.

**Request Payload:**
```json
{
  "input_type": "audio", // or "text"
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...", // Required if audio
  "text": null, // Required if text
  "client_timestamp": "2026-07-24T10:15:00Z"
}
```

**Response (Success - High Confidence Draft):**
```json
{
  "status": "success",
  "data": {
    "ai_extraction_id": "ext_8f7b2319-...",
    "transcript": "Paid 4500 to Rajesh for electrical work, cash.",
    "state": "pending_confirmation",
    "extraction": {
      "intent": "expense",
      "amount": 4500.00,
      "currency": "INR",
      "entity": {
        "id": "ven_12345",
        "name": "Rajesh (Electrician)",
        "is_new": false
      },
      "category": {
        "id": "acc_67890",
        "name": "Repairs & Maintenance"
      },
      "payment_channel": "Cash",
      "gst_itc_eligible": false,
      "gst_amount": 0.00
    },
    "confidence": {
      "aggregate": 0.92,
      "amount": 1.0,
      "entity": 0.95,
      "category": 0.92,
      "channel": 1.0
    },
    "ai_message": "Expense of ₹4,500 to Rajesh for Repairs & Maintenance, paid in cash. Confirm?"
  }
}
```

**Response (Requires Clarification):**
```json
{
  "status": "clarification_needed",
  "data": {
    "ai_extraction_id": "ext_8f7b2319-...",
    "transcript": "Paid 4500 for electrical work.",
    "missing_fields": ["entity", "payment_channel"],
    "ai_message": "Who did you pay the ₹4,500 to?",
    "quick_replies": []
  }
}
```

---

## 3.2 Core Workflow: Transaction Confirmation

Once the user reviews the draft extraction on the mobile app, they must confirm it or supply corrections.

### `POST /transactions/{ai_extraction_id}/confirm`

**Purpose:** Approves a draft AI extraction, causing Laravel to execute the accounting logic and post the final Journal Entry to the database. Also logs any manual corrections made by the user to the `correction_logs` table for ML feedback.

**Request Payload:**
```json
{
  "is_approved": true,
  "corrections": [
    {
      "field": "category.id",
      "original_value": "acc_67890", // Originally 'Repairs & Maintenance'
      "corrected_value": "acc_54321" // User changed to 'Office Supplies'
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "journal_entry_id": "je_9a8b7c6d-...",
    "status": "posted",
    "ai_message": "Got it. I've recorded the expense under Office Supplies.",
    "impact_summary": {
      "cash_balance": -4500.00,
      "expense_total_month": 125000.00
    }
  }
}
```

---

## 3.3 Dashboard & Reporting Endpoints

Used heavily by both Mobile and Web apps to fetch real-time financial data.

### `GET /dashboard/summary`

**Purpose:** Fetches the data required for the "Morning Briefing" (BP-009) and the mobile home screen widgets.

**Query Parameters:** `?date=2026-07-24`

**Response:**
```json
{
  "status": "success",
  "data": {
    "bank_balance": 1240000.00,
    "cash_balance": 15000.00,
    "revenue_mtd": 845000.00,
    "expenses_mtd": 220000.00,
    "net_profit_mtd": 625000.00,
    "gst_liability_mtd": 152100.00,
    "action_items": [
      {
        "type": "overdue_invoice",
        "entity_name": "ABC Company",
        "amount": 480000.00,
        "days_overdue": 12
      }
    ],
    "ai_briefing_text": "Good morning. Yesterday your revenue was ₹84,500..."
  }
}
```

### `GET /reports/profit-and-loss`

**Purpose:** Fetches the Income Statement. Used heavily by the Next.js web app for grid rendering.

**Query Parameters:** `?start_date=2026-04-01&end_date=2026-07-24&branch_id=all`

**Response Schema:** Returns standard P&L hierarchical JSON (Revenue array, COGS array, Expenses array, with totals).

---

## 3.4 Entity Management Endpoints

Standard CRUD operations for managing business entities.

- `GET /entities/customers` (List customers, supports pagination & search)
- `POST /entities/customers` (Create a new customer manually)
- `GET /entities/vendors` 
- `POST /entities/vendors` 
- `GET /invoices` (List sales invoices)
- `GET /invoices/{id}/pdf` (Download generated PDF invoice)
