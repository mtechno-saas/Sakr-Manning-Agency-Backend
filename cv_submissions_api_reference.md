# 📤 CV Submissions — API Reference

The CV Submissions section is the most data-rich module in the recruitment pipeline. It tracks the full evaluation and submission process of a seafarer to a specific client company for a target position.

---

## 1. Description
This section serves as a centralized hub for candidate evaluation. It combines the submission details (cover letter, availability, rating) with the candidate's full professional profile. It allows administrators to update the seafarer's name, email, ranks, certificates, and documents directly from the evaluation interface.

**Key Features:**
- **Evaluation Pipeline:** Track status from `Pending` through `Interviewed` to `Hired`.
- **Profile Synchronization:** Updating user info here (like salary or rank) automatically propagates to the main seafarer profile.
- **Document Hub:** Access and manage all travel documents and licenses within the submission context.
- **Coded Ranks:** Manage unique agency codes for assigned ranks (e.g., `DO-2.001`).

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/cv-submissions/` | List all submissions (lightweight) |
| `POST` | `/api/cv-submissions/` | Create a new submission |
| `GET` | `/api/cv-submissions/{id}/` | Full detail of one submission (includes docs/certs) |
| `PATCH` | `/api/cv-submissions/{id}/` | Update submission + linked user info |
| `GET` | `/api/cv-submissions/stats/` | Aggregate counts and percentages by status |
| `PATCH` | `/api/cv-submissions/{id}/update-status/` | Fast status-only update |
| `GET` | `/api/cv-submissions/{id}/download-document/?type=<type>` | Download linked seafarer documents |

---

## 3. Endpoint Details

### 3.1 List Submissions (`GET /api/cv-submissions/`)
**Description:** Returns a summarized list of submissions for the dashboard board view.
- **Response Body:**
```json
[
  {
    "id": 12,
    "user_name": "Ahmed Hassan",
    "company_name": "Sakr Shipping Co.",
    "position_name": "Chief Officer",
    "experience_years": 5,
    "status": "Under Review",
    "submitted_date": "2026-04-08T00:00:00Z",
    "salary": "4200",
    "coded_rank": [
      { "assigned_code": "DO-2.005", "rank_code": "DO-2", "rank_name": "Chief Officer" }
    ]
  }
]
```

### 3.2 Create Submission (`POST /api/cv-submissions/`)
**Description:** Initiates a new evaluation for a candidate.
- **Request Body:**
| Field | Type | Description |
|---|---|---|
| `user` | Integer | ID of the Seafarer (Required) |
| `job_position`| Integer | ID of the Job Order Position (Optional - Auto-fills company/rank) |
| `company` | Integer | ID of the target Company (Required if no job_position) |
| `position` | Mixed | Rank ID or Name (Required if no job_position) |
| `ship` | Integer | ID of the target Ship (Optional) |
| `status` | String | Initial status (Default: `Pending`) |

**Example Request:**
```json
{
  "user": 105,
  "job_position": 24,
  "cover_letter": "Strong candidate with 10 years experience on Tankers.",
  "status": "Under Review"
}
```

**Response (201):**
```json
{
  "id": 88,
  "user": 105,
  "user_name": "Mohamed Ali",
  "company": 3,
  "company_name": "Sakr Shipping",
  "position": 7,
  "position_name": "Chief Officer",
  "status": "Under Review",
  "created_at": "2026-05-15T21:26:00Z"
}
```

### 3.3 Full Update (`PATCH /api/cv-submissions/{id}/`)
**Description:** A powerful endpoint that updates the submission and the linked user profile.
- **Request Body (Combined Schema):**
| Field | Context | Description |
|---|---|---|
| `status` | Submission | `Pending` / `Under Review` / `Interviewed` / `Approved` etc. |
| `notes` | Submission | Admin internal notes |
| `rating` | Submission | 1–5 integer rating |
| `user_first_name`| User Profile | Updates the seafarer's first name |
| `salary` | User Profile | Updates the seafarer's base salary |
| `certificate_ids`| User Profile | Replaces all user STCW certificates |
| `passport_update`| User Profile | Updates passport details (number, expiry, etc.) |
| `licenses_update`| User Profile | List of `{id, document_name, ...}` to create/update licenses |

**Example Request:**
```json
{
  "status": "Approved",
  "rating": 5,
  "user_first_name": "Ahmed",
  "salary": "4500",
  "passport_update": {
    "passport_no": "A12345678",
    "expiry_date": "2030-01-14"
  }
}
```

### 3.4 Dashboard KPIs (`GET /api/cv-submissions/stats/`)
**Description:** Returns counts and percentages for the recruitment funnel.
- **Response Body:**
```json
{
  "total": 450,
  "under_review": 120,
  "under_review_percent": 27,
  "interviewed": 85,
  "interviewed_percent": 19,
  "pending": 200,
  "pending_percent": 44,
  "approved": 45,
  "approved_percent": 10
}
```

---

## 4. Data Modeling (Evaluation Context)

The `CVSubmission` model acts as a bridge between multiple data domains:

| Domain | Model Source | Purpose in Submission |
|---|---|---|
| **Identity** | `Users` | Name, Generated ID, Email |
| **Logistics** | `CVSubmission` | Availability, Expected Salary, Notes |
| **Compliance** | `Certificate` | STCW training verification |
| **Legal** | `PersonalDocument` | Passport and Seaman's Book validity |
| **Professional** | `UserRank` | Internal agency codes and seniority |

---

## 5. Permissions

- **Admin / HR Manager:** Full management, including data override on user profiles.
- **Recruiter:** Can view details, update status, add notes, and perform evaluations.
- **Employee (Seafarer):** Can view their own application status but cannot see internal notes or ratings.

---

> [!IMPORTANT]
> When downloading documents via `/api/cv-submissions/{id}/download-document/`, use the `type` query parameter: `passport`, `seaman_book`, `marlins`, or `crews`.
