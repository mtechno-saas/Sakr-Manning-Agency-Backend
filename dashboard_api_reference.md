# 🏠 Dashboard — API Reference

The Dashboard section provides a high-level overview of the agency's operations through aggregated statistics, Key Performance Indicators (KPIs), and a unified global search. This data is intended to power the admin dashboard widgets.

---

## 1. Description
The Dashboard is not a single resource but a collection of specialized statistics endpoints. It allows administrators (Admin and HR Managers) to monitor the entire seafarer lifecycle—from initial application to contract signing and financial tracking—at a glance.

**Key Features:**
- **KPI Cards:** Real-time counts for users, applications, and contracts.
- **Urgent Actions:** Identification of expiring contracts and upcoming interviews.
- **Operational Health:** Tracking open positions and active companies.
- **Global Search:** Instant lookup across seafarers, ships, companies, and submissions.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users/stats/` | Seafarer and role distribution stats |
| `GET` | `/api/cv-submissions/stats/` | Application pipeline metrics |
| `GET` | `/api/interviews/stats/` | Scheduled interview overview |
| `GET` | `/api/contracts/stats/` | Contract validity and urgency alerts |
| `GET` | `/api/companies/stats/` | Partner companies and job demand |
| `GET` | `/api/documents/stats/` | "Quick Apply" application tracking |
| `GET` | `/api/finance-records/stats/` | Payroll and record status overview |
| `GET` | `/api/global-search/?q=<query>` | Unified search across the system |

---

## 3. Endpoint Details

### 3.1 Seafarer Stats (`/api/users/stats/`)
**Description:** High-level counts of registered users and their roles.
- **Permissions:** `Admin`, `HR Manager`
- **Response Body:**
```json
{
  "total_users": 1250,
  "admins": 5,
  "hr_managers": 12,
  "recruiters": 8,
  "employees": 1225,
  "active_users": 1180
}
```

### 3.2 CV Submission Stats (`/api/cv-submissions/stats/`)
**Description:** Pipeline metrics for seafarer applications.
- **Permissions:** `Admin`, `HR Manager`, `Recruiter`
- **Response Body:**
```json
{
  "total": 450,
  "under_review": 120,
  "interviewed": 85,
  "pending": 200,
  "approved": 45,
  "under_review_percent": 27,
  "interviewed_percent": 19,
  "pending_percent": 44,
  "approved_percent": 10
}
```

### 3.3 Interview Overview (`/api/interviews/stats/`)
**Description:** Monitoring the recruitment schedule.
- **Permissions:** `Admin`, `HR Manager`, `Recruiter` (Employees see their own)
- **Response Body:**
```json
{
  "today_interviews": 15,
  "this_week": 42,
  "pending_confirmation": 8
}
```

### 3.4 Contract Alerts (`/api/contracts/stats/`)
**Description:** Critical monitoring of contract end dates for crew changes.
- **Permissions:** `Admin`, `HR Manager`, `Recruiter`
- **Response Body:**
```json
{
  "signed_contracts": 320,
  "pending_signature": 15,
  "drafts": 10,
  "critical": 5,      // Expiring within 7 days
  "warning": 12,      // Expiring within 30 days
  "notice": 25        // Expiring within 60 days
}
```

### 3.5 Global Search (`/api/global-search/?q=...`)
**Description:** Searches across five major entities simultaneously.
- **Permissions:** `Authenticated`
- **Query Params:** `q` (string, min 2 chars)
- **Response Body:**
```json
{
  "users": [ { "id": 1, "name": "John Doe", "email": "...", "phone": "...", "role": "..." } ],
  "ships": [ ... ],
  "companies": [ ... ],
  "cvs": [ ... ],
  "contracts": [ ... ]
}
```

---

## 4. Data Modeling (Dashboard Context)

The Dashboard aggregates data from the following core models:

| Model | Dashboard Role | Key Fields Used |
|---|---|---|
| `Users` | Seafarer Pipeline | `role`, `is_active`, `user_status` |
| `CVSubmission` | Recruitment Funnel | `status`, `created_at` |
| `Interview` | Schedule Management | `scheduled_date`, `status` |
| `Contract` | Crew Retention | `sign_off_date`, `status` |
| `Company` | Business Demand | `status`, `open_positions` |
| `Document` | New Applicants | `status` (for Quick Appliers) |
| `FinanceRecord` | Payroll Health | `status` |

---

## 5. Permissions

Access to dashboard data is strictly role-based:

- **Admin / HR Manager:** Full access to all statistics across all seafarers and companies.
- **Recruiter:** Access to recruitment-related stats (`CVSubmissions`, `Interviews`, `Contracts`, `Companies`).
- **Employee (Seafarer):** Can only access statistics filtered for their own records (e.g., their own upcoming interviews or contract status).
- **Public:** No access to any dashboard endpoints.

---

> [!TIP]
> Use the `/api/contracts/stats/` endpoint to drive a "Critical Expirations" widget on the main dashboard to ensure crew changes are scheduled on time.
