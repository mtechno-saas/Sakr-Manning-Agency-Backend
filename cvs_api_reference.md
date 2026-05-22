# 📋 CVs (Quick Applications) — API Reference

The CVs section (internally referred to as **Documents**) manages the triage of "Quick Applications." This is the entry point for seafarers who upload their CV files without yet having a full account profile.

---

## 1. Description
This section is designed for the initial intake of candidates. Administrators can review uploaded PDF/DOCX files, verify basic contact information, and either approve the applicant (which promotes them to a full User profile) or blacklist them.

**Key Features:**
- **Triaging:** Manage applications in `Pending`, `Active`, or `Blacklist` states.
- **Auto-Promotion:** Approval (`Active`) automatically generates a 12-digit User ID, creates a full profile, and initiates a CV Submission.
- **Public Intake:** The `POST` endpoint is open to allow unregistered applicants to submit their CVs.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/documents/` | List all quick applications |
| `POST` | `/api/documents/` | Submit a new quick application (Public) |
| `GET` | `/api/documents/{id}/` | Retrieve detailed application info |
| `PATCH` | `/api/documents/{id}/` | Update application details |
| `DELETE` | `/api/documents/{id}/` | Remove an application record |
| `POST` | `/api/documents/{id}/set_status/` | Update status and trigger profile creation |
| `GET` | `/api/documents/stats/` | KPIs for quick applications |
| `GET` | `/api/documents/{id}/download/` | View/Download the uploaded CV file |

---

## 3. Endpoint Details

### 3.1 List Applications (`GET /api/documents/`)
**Description:** Returns a list of all documents/applications. Supports filtering by status.
- **Permissions:** `Admin`, `HR Manager`, `Recruiter`
- **Response Body:**
```json
[
  {
    "id": 105,
    "name": "Ahmed Mansour",
    "email": "ahmed.m@example.com",
    "phone_number": "+20123456789",
    "position": "Chief Officer",
    "status": "Pending",
    "file": "http://domain.com/media/documents/ahmed_cv.pdf",
    "created_at": "2026-05-10T14:30:00Z"
  }
]
```

### 3.2 Quick Apply (`POST /api/documents/`)
**Description:** Public endpoint for new seafarers to upload their CV.
- **Permissions:** `AllowAny` (Public)
- **Request Body (Multipart/Form-Data):**
| Field | Type | Description |
|---|---|---|
| `file` | File | The PDF or DOCX CV file (Required) |
| `name` | String | Full name of the applicant |
| `email` | String | Contact email |
| `phone_number`| String | Contact phone |
| `position` | String | Target position name (e.g., "Master") |
| `job_position`| Integer| ID of a specific Job Order Position (Optional) |

### 3.3 Set Status (`POST /api/documents/{id}/set_status/`)
**Description:** The primary workflow trigger. Setting status to `Active` performs several background actions.
- **Permissions:** `Admin`, `HR Manager`, `Recruiter`
- **Request Body:**
```json
{
  "status": "Active" // Options: Pending, Active, Blacklist
}
```
**Side Effects of "Active":**
1. Generates a unique 12-digit `generated_id` for the user.
2. Syncs `name`, `email`, and `position` to the main `Users` profile.
3. Creates a `CVSubmission` record linked to the provided position.
4. Assigns the corresponding `UserRank`.
5. Sends a welcome and email verification link to the applicant.

---

## 4. Data Modeling

### Document Model
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Unique identifier |
| `title` | String | Automatically set to the filename if not provided |
| `file` | FileField | Path to the uploaded PDF/DOCX |
| `name` | String | Applicant's name |
| `email` | String | Applicant's email |
| `position` | String | Human-readable rank name |
| `position_id` | Integer | ID from the `Rank` model |
| `status` | Choice | `Pending`, `Active`, `Blacklist` |
| `user` | FK | Links to the `Users` model (auto-created) |

---

## 5. Permissions

- **Public (Anonymous):** Can only `POST` to `/api/documents/` to apply.
- **Employee (Seafarer):** Can view and download their own document.
- **Recruiter:** Can view all applications and update statuses.
- **Admin / HR Manager:** Full management capabilities including deletion.

---

> [!IMPORTANT]
> The `POST` endpoint handles automatic user creation. If an applicant uses an email that already exists in the system, the document is automatically linked to the existing user account instead of creating a duplicate.
