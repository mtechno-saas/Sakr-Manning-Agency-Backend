# CV Submissions API — Full Endpoint Reference

**Base URL:** `/api/cv-submissions/`

**Authentication:** Bearer JWT token required on all endpoints.

The CV Submissions endpoint manages candidate job applications. It natively integrates with Seafarer Profiles and automatically synchronizes data from the CV to the candidate's Seafarer Profile, as well as tracking their assigned `ship`, `company`, and `job_position`.

---

### Permissions

| Role | Access Level |
|---|---|
| Admin / HR Manager | Full CRUD (Create, Read, Update, Delete) |
| Recruiter | View and update status |
| Employee | Can only read/create their own CVs |

---

### `GET /api/cv-submissions/` — List CV Submissions
Returns a list of CV Submissions. For Admin/HR Manager/Recruiter, returns all. For Employee, returns only their own. Uses a lightweight representation to improve performance.

**Response Example:**
```json
[
  {
    "id": 1,
    "user": 5,
    "user_name": "Ahmed Hassan",
    "company": 2,
    "company_name": "Maersk Line",
    "position": 3,
    "position_name": "Chief Officer",
    "experience_years": 5,
    "status": "Pending",
    "submitted_date": "2026-05-04T12:00:00Z",
    "generated_id": "123456789012",
    "salary": "5000",
    "coded_rank": [
      {
        "assigned_code": "CO.1",
        "rank_code": "CO",
        "rank_name": "Chief Officer"
      }
    ],
    "rank_code": "CO",
    "assigned_code": "CO.1",
    "job_position": 1,
    "job_position_details": {
      "id": 1,
      "job_position_name": "Chief Officer",
      "quantity": 2,
      "salary_min": "4500",
      "salary_max": "5500",
      "currency": "USD",
      "contract_duration_months": 6,
      "remarks": "Urgent"
    }
  }
]
```

---

### `GET /api/cv-submissions/{id}/` — Retrieve Full Submission Details
Returns the complete nested details of a CV Submission, including full seafarer profile data and company/ship information.

**Response Example:**
```json
{
  "id": 1,
  "user": 5,
  "user_name": "Ahmed Hassan",
  "user_email_display": "ahmed@example.com",
  "company": 2,
  "company_name": "Maersk Line",
  "ship": 1,
  "ship_name": "Ocean Voyager",
  "ship_details": {
    "id": 1,
    "ship_name": "Ocean Voyager",
    "imo_number": "1234567",
    "ship_type": "Container",
    "flag": "Panama",
    "status": "Active"
  },
  "position": 3,
  "position_name": "Chief Officer",
  "cv_file": "http://example.com/media/cvs/ahmed_hassan.pdf",
  "cover_letter": "I have 5 years of experience...",
  "experience_years": 5,
  "expected_salary": "5500.00",
  "availability_date": "2026-06-01",
  "status": "Approved",
  "submitted_date": "2026-05-04T12:00:00Z",
  "reviewed_by": 1,
  "reviewed_by_name_display": "Admin User",
  "reviewed_date": "2026-05-05",
  "notes": "Good candidate.",
  "rating": 5,
  "created_at": "2026-05-04T12:00:00Z",
  "updated_at": "2026-05-05T10:00:00Z",
  "generated_id": "123456789012",
  "salary_display": "5500",
  "coded_rank": [
    {
      "assigned_code": "CO.1",
      "rank_code": "CO",
      "rank_name": "Chief Officer"
    }
  ],
  "rank_code": "CO",
  "assigned_code": "CO.1",
  "certificates": [
    {
      "id": 1,
      "code": "STCW-1",
      "name": "Basic Safety Training"
    }
  ],
  "user_documents": {
    "passport": {
      "passport_no": "A1234567",
      "issue_date": "2020-01-01",
      "expiry_date": "2030-01-01",
      "issued_by": "Egypt",
      "place_of_issue": "Cairo",
      "file_url": "http://example.com/media/passports/ahmed.pdf",
      "download_url": "/api/cv-submissions/1/download-document/?type=passport"
    },
    "seaman_book": {
      "seaman_book_no": "SB123456"
    },
    "licenses": []
  },
  "job_position": 1,
  "job_position_details": {
    "id": 1,
    "job_position_name": "Chief Officer",
    "quantity": 2,
    "salary_min": "4500",
    "salary_max": "5500",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": "Urgent"
  },
  "seafarer_application": {
    "personal_details": {
      "first_name": "Ahmed",
      "last_name": "Hassan",
      "date_of_birth": "1990-01-01"
    },
    "education": [],
    "sea_service_details": [],
    "next_of_kin": [],
    "vaccinations": []
  },
  "company_details": {
    "id": 2,
    "company_name": "Maersk Line",
    "company_type": "Ship Owner",
    "country": "Denmark",
    "contact_person": "John Doe",
    "contact_email": "john@maersk.com",
    "status": "Active"
  }
}
```

---

### `POST /api/cv-submissions/` — Create CV Submission
* **employee:** Auto-fills `request.user`.
* **admin/hr:** Can optionally specify `user`.

Modifying the write-only fields directly updates the linked User and their Seafarer application profile seamlessly.

**Request Example (JSON):**
```json
{
  "user_first_name": "Ahmed",
  "user_middle_name": "Ali",
  "user_email": "ahmed@example.com",
  "company_name_input": "Maersk Line",
  "position_name_input": "Chief Officer",
  "experience_years": 5,
  "expected_salary": "5500.00",
  "availability_date": "2026-06-01",
  "salary": "5500",
  "coded_rank_input": [
    {
      "rank_code": "CO",
      "rank_name": "Chief Officer",
      "assigned_code": "CO.1"
    }
  ],
  "passport_update": {
    "passport_no": "A1234567",
    "issue_date": "2020-01-01",
    "expiry_date": "2030-01-01",
    "issued_by": "Egypt",
    "place_of_issue": "Cairo"
  },
  "job_position": 1
}
```
*Note: You can also use `multipart/form-data` to include the `cv_file`.*

**Response Example:**
*Returns the full nested object just like `GET {id}`.*

---

### `PUT /api/cv-submissions/{id}/` — Replace CV Submission
Overwrites the CV Submission. Requires all mandatory fields.

**Request Example:**
```json
{
  "experience_years": 6,
  "expected_salary": "6000.00",
  "availability_date": "2026-07-01",
  "job_position": 1,
  "notes": "Updated candidate info."
}
```

**Response Example:**
*Returns the full nested object just like `GET {id}`.*

---

### `PATCH /api/cv-submissions/{id}/` — Update CV Submission
Partially update a CV Submission. You can selectively pass in the writable fields. Modifying these fields directly updates the linked User and their Seafarer application profile seamlessly.

**Request Example:**
```json
{
  "notes": "Candidate called today.",
  "status": "Interviewed",
  "licenses_update": [
    {
      "document_name": "DP Certificate",
      "document_number": "DP-123",
      "country_of_issue": "UK",
      "issue_date": "2022-01-01",
      "expiration_date": "2027-01-01"
    }
  ]
}
```

**Response Example:**
*Returns the full nested object just like `GET {id}`.*

---

### `DELETE /api/cv-submissions/{id}/` — Delete Submission
Permanently deletes the CV Submission.

**Response:**
* **Status:** `204 No Content`
* **Body:** None

---

### `PATCH /api/cv-submissions/{id}/update-status/` — Update Status
Dedicated endpoint for recruiters and admins to update a CV's status.
Automatically sets `reviewed_by` to the current user and `reviewed_date` to today if status is `Approved` or `Rejected`.

**Request Example:**
```json
{
  "status": "Approved"
}
```

**Response Example:**
*Returns the full nested object just like `GET {id}`.*

---

### `GET /api/cv-submissions/{id}/download-document/?type={doc_type}` — Download Document
Download a specific file attachment directly from the linked user's profile.
* **Valid `doc_type` values:** `passport`, `seaman_book`, `other_seaman_book`, `marlins`, `ces`.

---

### `POST /api/cv-submissions/upload/` — Direct CV Document Upload
* **Content-Type:** `multipart/form-data`
* **Body:** `cv_file` (required file), `position` (optional ID), `notes` (optional text).
Creates a `Pending` CV Submission immediately tied to the logged-in user.

---

### `GET /api/cv-submissions/stats/` — Dashboard Statistics
Returns aggregated counts for dashboard use. Admins see global counts, Employees see only their own.

**Response Example:**
```json
{
  "total": 10,
  "under_review": 2,
  "interviewed": 3,
  "pending": 4,
  "approved": 1,
  "under_review_percent": 20,
  "interviewed_percent": 30,
  "pending_percent": 40,
  "approved_percent": 10
}
```

