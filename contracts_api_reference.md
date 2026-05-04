# Contracts API — Full Endpoint Reference

**Base URL:** `/api/contracts/`

**Authentication:** Bearer JWT token required on all endpoints.

The contracts endpoint integrates directly with CV Submissions and Job Order Positions, allowing you to instantly generate a contract pre-filled with the employee's details and the salary from the job position they applied for.

---

### Permissions

| Role | Access Level |
|---|---|
| Admin / HR Manager | Full CRUD (Create, Read, Update, Delete) |
| Recruiter | Read-only |
| Employee | Can only read their own contracts |

---

### `POST /api/contracts/` — Generate Contract (from CV Submission)

Allows you to instantly generate an employment contract by pointing to an approved CV Submission. It auto-fills the user, company, rank, and salary details based on the exact Job Position they applied for.

**Data Model Inputs:**
| Field | Source / Type | Required? | Description |
|---|---|---|---|
| `cv_submission` | `int` | **Yes** | The ID of the CV Submission. Auto-fills `user`, `company`, `rank`, and `job_position`. |
| `ship_name` | `string` | **Yes** | The name of the Ship they are joining (alternatively, you can pass `ship` as an int ID). |
| `sign_on_date` | `date` | **Yes** | Date they board the ship (Format: YYYY-MM-DD). |
| `salary` | `decimal` | Optional | **Auto-fills** with `salary_max` from the Job Order Position if not provided. |
| `currency` | `string` | Optional | **Auto-fills** from the Job Order Position, otherwise defaults to `USD`. |
| `sign_off_date` | `date` | Optional | Scheduled disembarkation date. |
| `repatriation_terms` | `string` | Optional | Notes on flight/travel coverage. |
| `leave_pay_terms` | `string` | Optional | Notes on paid leave. |
| `status` | `string` | Optional | Defaults to `Draft` (Active, Completed, Pending, Signed, Pending Signature, Draft, Cancelled). |

**Request:**
```json
{
  "cv_submission": 45,
  "ship_name": "Ocean Voyager",
  "sign_on_date": "2026-06-01",
  "repatriation_terms": "Company covers return flight to home country",
  "leave_pay_terms": "30 days paid leave per contract cycle",
  "status": "Draft"
}
```
> *Note: We did not send `salary` or `currency` — the backend will grab those directly from the job position they applied for!*

**Success Response (201 Created):**
```json
{
  "id": 12,
  "user": 7,
  "user_name": "Mohamed Ahmed",
  "user_email": "mohamed.ahmed@email.com",
  "generated_id": "492817364051",
  
  "ship": 3,
  "ship_name": "MV Ocean Star",
  "company": 2,
  "company_name": "Sakr Shipping",
  
  "rank": 7,
  "rank_name": "2nd. Officer",
  "assigned_code": "DO-3.002",
  
  "job_position": 4,
  "job_position_details": {
    "id": 4,
    "quantity": 2,
    "salary_min": "2500.00",
    "salary_max": "3500.00",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": "Must have tanker experience"
  },
  
  "sign_on_date": "2026-06-01",
  "sign_off_date": null,
  "salary": "3500.00",
  "currency": "USD",
  "status": "Draft",
  
  "signed_file": null,
  "signed_at": null,
  "created_at": "2026-05-01T11:45:00Z",
  "updated_at": "2026-05-01T11:45:00Z",

  "certificates": [
    {
      "id": 1,
      "code": "GMDSS",
      "name": "G.M.D.S.S"
    }
  ],
  "coded_rank": [
    {
      "assigned_code": "DO-3.002",
      "rank_code": "DO-3.000",
      "rank_name": "2nd. Officer"
    }
  ],
  "user_documents": {
    "passport": {
      "passport_no": "A12345678",
      "issue_date": "2022-01-15",
      "expiry_date": "2032-01-14",
      "issued_by": "Egypt",
      "place_of_issue": "Cairo",
      "file_url": "http://api.backend.soon.it/media/documents/passports/passport_123.pdf"
    },
    "seaman_book": {
      "seaman_book_no": "SB9876543",
      "issue_date": "2023-05-10",
      "expiry_date": "2028-05-09",
      "issued_by": "Maritime Authority",
      "place_of_issue": "Alexandria",
      "file_url": "http://api.backend.soon.it/media/documents/seaman/sb_123.pdf"
    },
    "other_seaman_book": {
      "seaman_book_no": null,
      "issue_date": null,
      "expiry_date": null,
      "issued_by": "",
      "place_of_issue": "",
      "file_url": null
    },
    "coc": {
      "certificate_name": "Officer in Charge of Navigational Watch",
      "certificate_number": "COC-456",
      "issue_date": "2021-08-20",
      "expiry_date": "2026-08-19",
      "issued_by": "EAMS",
      "issued_at": "Alexandria"
    },
    "goc": {
      "certificate_number": "GOC-789",
      "issue_date": "2022-11-05",
      "expiry_date": "2027-11-04",
      "issued_by": "EAMS",
      "issued_at": "Alexandria"
    },
    "health_certificate": {
      "flag_state": "Panama",
      "number": "MED-111",
      "issue_date": "2025-01-10",
      "expiry_date": "2027-01-09",
      "issued_by": "Approved Clinic",
      "issued_at": "Cairo",
      "international_medical_number": "INT-222",
      "international_medical_issue_date": "2025-01-15",
      "international_medical_expiry_date": "2027-01-14"
    },
    "licenses": [
      {
        "id": 1,
        "document_name": "Panama License",
        "document_number": "PAN-333",
        "country_of_issue": "Panama",
        "issue_date": "2024-03-01",
        "expiration_date": "2029-02-28",
        "file_url": "http://api.backend.soon.it/media/documents/licenses/panama_lic.pdf"
      }
    ]
  }
}
```

---

### `PATCH /api/contracts/{id}/` — Edit a Contract

Use this to update fields (e.g. changing status to "Signed" or adjusting salary). All fields are optional.

**Request:**
```json
{
  "salary": "4000.00",
  "status": "Pending Signature",
  "sign_off_date": "2026-12-15"
}
```

**Response (200):** Full contract object with updated fields.

---

### `GET /api/contracts/` — List all Contracts
Returns a paginated list of all contracts. Employee sees only their own contracts.

---

### `GET /api/contracts/{id}/` — Get Contract Details
Returns the same rich response as the `POST` endpoint, containing all user documentation.

---

### `GET /api/contracts/stats/` — Contract Statistics
Returns statistics for dashboard (Signed, Pending Signature, Drafts, expiring soon).

**Response (200):**
```json
{
  "signed_contracts": 12,
  "pending_signature": 5,
  "drafts": 3,
  "critical": 2,
  "warning": 4,
  "notice": 6
}
```

---

### `DELETE /api/contracts/{id}/` — Delete a Contract

**Response:** `204 No Content`

---

## Quick Reference — All Endpoints

| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/contracts/` | Admin/HR | List all contracts |
| `POST` | `/api/contracts/` | Admin/HR | Generate/create contract |
| `GET` | `/api/contracts/{id}/` | Admin/HR | Contract detail |
| `PATCH` | `/api/contracts/{id}/` | Admin/HR | Update a contract |
| `DELETE` | `/api/contracts/{id}/` | Admin/HR | Delete a contract |
| `GET` | `/api/contracts/stats/` | Admin/HR | Dashboard statistics |
