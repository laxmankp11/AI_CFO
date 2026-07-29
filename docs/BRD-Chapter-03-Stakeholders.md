# AICFO — Business Requirements Document (BRD)

---

# Chapter 3 – Stakeholders

---

## 3.0 Overview

AICFO serves multiple stakeholder types, each with distinct responsibilities, permissions, goals, and pain points. This chapter defines every stakeholder role in detail because these profiles directly drive:

- **Permission design** — who can see, create, edit, approve, and delete what
- **AI behavior** — who the AI speaks to, what it reveals, and whose approval it seeks
- **Workflow routing** — which approvals, notifications, and escalations involve which roles
- **UI/UX design** — different stakeholders see different dashboards, reports, and interaction modes

### Core Hierarchy
**AI Business OS (Platform)**
│
├── **Super Admin** (Platform Owner)
│
├── **Tenant / Business**
│     │
│     ├── **Business Owner** (Tenant Admin)
│     ├── **Accountant**
│     ├── **Manager** (Department level)
│     ├── **Employee**
│     └── **Auditor** (optional)
│
└── **External Users**
      ├── **Customer** (To whom the business sells)
      ├── **Supplier (Vendor)** (From whom the business buys)
      └── **Tax Consultant / CA**

---

## 3.1 Super Admin (Platform Owner)

### Persona Description
This is the SaaS platform operator (your company, not your customer's company). The Super Admin manages the entire AICFO infrastructure, billing, and AI models across all tenants.

### Responsibilities
- **Platform Management:** Create, suspend, delete, activate, and verify businesses (Tenants).
- **Subscription Management:** Manage plans, billing, renewals, coupons, trial accounts, and feature limits.
- **AI Management:** Configure AI providers, select AI models, manage prompt templates, monitor AI costs, usage limits, and confidence thresholds.
- **User Management (Cross-Tenant):** Reset passwords, lock/unlock accounts, force logout.
- **Monitoring:** Track active users, AI requests, API usage, storage usage, revenue, and errors.
- **Support:** Impersonate business (with strict audit logging), view logs, and resolve issues.
- **Security:** Define MFA policies, password policies, IP restrictions, and monitor audit logs.
- **Integrations:** Manage global API keys for Payment gateways, Email, SMS, OCR, and AI providers.
- **Analytics:** View platform-wide metrics (Total Businesses, Monthly Revenue, Churn, AI Cost, Storage, API Calls).

---

## 3.2 Business Owner (Tenant Admin)

### Persona Description
This is your paying customer. They own one company (Tenant) and can manage only their company's data.

### Responsibilities
- **Company Management:** Manage company profile, GST/VAT details, financial year, branches, and bank accounts.
- **User Management:** Create employees, assign roles, and set permissions.
- **Customers & Suppliers:** Create, edit, and delete Customers and Suppliers (Vendors), including payment terms.
- **Products:** Manage products, categories, pricing, and tax rates.
- **Finance & Accounting:** Manage sales, purchases, expenses, payroll, taxes, and journal entries.
- **AI Interaction:** Talk to the AI Virtual CFO, approve AI entries, and review AI advisory suggestions.
- **Reports:** View Profit & Loss, Balance Sheet, Cash Flow, and custom dashboards.
- **Billing:** Manage the subscription and billing specifically for their own tenant account.

---

## 3.3 Accountant

### Persona Description
A finance user working inside one specific business (Tenant). They focus on accounting accuracy and compliance.

### Responsibilities
- **Core Accounting:** Review AI entries, approve journals, file taxes, generate reports, and close the books.
- **Restrictions:** They *cannot* change the SaaS subscription, delete the company, or alter global platform settings.

---

## 3.4 Manager

### Persona Description
Department-level leaders within a Business (e.g., Sales Manager, Warehouse Manager, HR Manager, Finance Manager).

### Responsibilities
- Manage operations specific to their department.
- Approve employee requests (e.g., expenses, leaves) within their department.
- Access limited, department-specific reporting.

---

## 3.5 Employee

### Persona Description
Operational users within a Business who perform assigned tasks.

### Responsibilities
- **Self-Service:** Upload receipts, create expense claims, view payslips, apply for leave, and clock in/out.
- **Restrictions:** They can only view and perform tasks explicitly assigned to them. They have no access to company-wide financial reports.

---

## 3.6 Customer

### Persona Description
Your customer's customer (the entity to whom the Business sells).

### Responsibilities
- **Interactions:** View invoices, pay invoices via payment links, and download receipts from a secure portal or email link.

---

## 3.7 Supplier (Vendor)

### Persona Description
The entity from whom the Business buys (Standard accounting meaning of "Vendor").

### Responsibilities
- **Interactions:** Receive purchase orders, view payment status, and optionally upload invoices into a vendor portal.

---

## 3.8 Role-Based Access Control (RBAC) Summary Matrix

The following matrix summarizes the permission scopes across all primary stakeholders:

| Feature | Super Admin | Business Owner | Accountant | Manager | Employee |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Platform Settings** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Create Business (Tenant)** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Subscription (SaaS)** | ✅ | View Own | ❌ | ❌ | ❌ |
| **Company Settings** | ❌ | ✅ | View | ❌ | ❌ |
| **Users** | Cross-Tenant | Own Business | Limited | Team | Self |
| **Accounting** | View | Full | Full | Limited | Limited |
| **AI Configuration** | Platform | Business Preferences | ❌ | ❌ | ❌ |
| **Reports** | Platform | Own Business | Finance | Department | Assigned |

---

*End of Chapter 3 – Stakeholders*

*Next: Chapter 4 – Business Modules*
