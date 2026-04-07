# Admin Panel — Section Breakdown
> Based on actual database models in the Sakr Manning Agency backend

---

## 1. 🏠 Dashboard
**Purpose:** High-level overview / KPIs at a glance

| Widget | Data Source |
|---|---|
| Total registered seafarers | `Users` model (total count) |
| Active / On Site seafarers | `Users.user_status = ON_SITE` |
| Seafarers on Vacation | `Users.user_status = VACATION` |
| Seafarers on Medical Leave | `Users.user_status = MEDICAL VACATION` |
| Blacklisted seafarers | `Users.is_blacklisted = True` |
| Total CVs submitted | `CVSubmission` model (count) |
| Pending CV reviews | `CVSubmission.status = Pending` |
| Upcoming interviews | `Interview.status = Scheduled` (upcoming dates) |
| Total companies | `Company` model (count) |
| Open job positions | `Company.open_positions` sum OR `JobOrder.status = Open` |
| Documents expiring soon | `UserLicense.expiration_date` within 30–60 days |
| Recent registrations | Latest `Users` by `created_at` |

---

## 2. 📋 CVs
**Purpose:** Manage CV/profile documents uploaded for each seafarer

| What to Show | Data Source |
|---|---|
| List of all CV documents | `Document` model (PDF/DOCX files linked to users) |
| Seafarer name + position | `Document.user` → `Users.first_name`, `Document.position` |
| Document status | `Document.status` (Pending / Active / Blacklist) |
| Upload date | `Document.created_at` |
| Download/view file | `Document.file` (PDF or DOCX) |
| Linked user profile | `Document.user` → full `Users` record |

> **Also relevant:** `Users.file` and `Users.title` — these are synced from documents and hold the latest file per user.

---

## 3. 👥 Management
**Purpose:** Manage companies, ships, job orders, and rank/crew assignments

### Sub-sections:

#### 🏢 Companies
| Field | Source |
|---|---|
| Company name & type | `Company.company_name`, `Company.company_type` |
| Status | `Company.status` (Active / Inactive / Prospect) |
| Contact email | `Company.contact_email` |
| Hourly rate | `Company.hourly_rate` |
| Open positions | `Company.open_positions` |
| Linked ships | `Ship.company` → all ships for this company |

#### 🚢 Ships
| Field | Source |
|---|---|
| Ship name & IMO | `Ship.ship_name`, `Ship.imo_number` |
| Type & Flag | `Ship.ship_type` (→ `VesselType`), `Ship.flag` (→ `Flag`) |
| Crew members | `Ship.crew` (ManyToMany → `Users`) |
| Technical details | `gross_tonnage`, `deadweight`, `engine_type`, `engine_power_kw` |
| Status | `Ship.status` |

#### 📋 Job Orders
| Field | Source |
|---|---|
| Reference number | `JobOrder.reference_number` |
| Company & Ship | `JobOrder.company`, `JobOrder.ship` |
| Request date / target join | `JobOrder.request_date`, `JobOrder.target_joining_date` |
| Status | `JobOrder.status` (Pending / Open / In Progress / Fulfilled / Cancelled) |
| Positions required | `JobOrderPosition` → rank, quantity, salary range, contract duration |

#### 🏅 Rank Codes
| Field | Source |
|---|---|
| All available ranks | `Rank` model (code + name) |
| Users per rank | `UserRank.user` grouped by `rank` |

---

## 4. 📤 CV Submissions
**Purpose:** Track the full application/submission pipeline per seafarer + company.
Uses `CVSubmission` model. Detail endpoint uses `CVSubmissionSerializer`.

**Base URL:** `/api/cv-submissions/`

---

### 4.1 Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/cv-submissions/` | List all submissions (lightweight) |
| `POST` | `/api/cv-submissions/` | Create a new submission |
| `GET` | `/api/cv-submissions/{id}/` | Full detail of one submission |
| `PATCH` | `/api/cv-submissions/{id}/` | Partial update — all write fields below |
| `GET` | `/api/cv-submissions/stats/` | Aggregate counts by status |
| `PATCH` | `/api/cv-submissions/{id}/update-status/` | Quick status update only |
| `GET` | `/api/cv-submissions/{id}/download-document/?type=<type>` | Download a user file attachment |

---

### 4.2 Response Fields (Read)

#### Core Submission Fields
| Field | Description |
|---|---|
| `id` | CV submission ID |
| `user` | FK to user (ID) |
| `user_name` | `first_name + middle_name` display |
| `user_email_display` | User's email (read-only display) |
| `company` / `company_name` | FK + company name display |
| `position` / `position_name` | FK + rank name display |
| `cv_file` | Uploaded CV file URL |
| `cover_letter` | Text cover letter |
| `experience_years` | Integer |
| `expected_salary` | Decimal |
| `availability_date` | Date |
| `status` | `Pending` / `Under Review` / `Interviewed` / `Shortlisted` / `Approved` / `Rejected` / `Hired` |
| `submitted_date` | DateTime |
| `reviewed_by` / `reviewed_by_name_display` / `reviewed_date` | Reviewer info |
| `notes` | Admin notes |
| `rating` | Integer (1–5) |
| `created_at` / `updated_at` | Timestamps |
| `generated_id` | User's 12-digit ID (set after Document approval) |
| `salary_display` | User's salary (read-only) |

#### Rank & Codes
| Field | Description |
|---|---|
| `coded_rank` | List of `{assigned_code, rank_code, rank_name}` from user's `UserRank` records |

#### Certificates
| Field | Description |
|---|---|
| `certificates` | List of `{id, code, name}` — STCW certs assigned to the user |

#### User Documents (read-only grouped block)
Returned under `user_documents`:

| Key | Contents |
|---|---|
| `passport` | `passport_no, issue_date, expiry_date, issued_by, place_of_issue, file_url, download_url` |
| `seaman_book` | `seaman_book_no, issue_date, expiry_date, issued_by, place_of_issue, file_url, download_url` |
| `other_seaman_book` | Same structure as seaman_book |
| `coc` | `certificate_name, certificate_number, issue_date, expiry_date, issued_by, issued_at` |
| `goc` | `certificate_number, issue_date, expiry_date, issued_by, issued_at` |
| `health_certificate` | `flag_state, number, issue_date, expiry_date, issued_by, issued_at, international_medical_*` |
| `licenses` | List of `{id, document_name, document_number, country_of_issue, issue_date, expiration_date, file_url, download_url}` |

---

### 4.3 Write Fields (PATCH)

All fields are optional (partial update).

#### Submission Fields
| Field | Type | Description |
|---|---|---|
| `status` | string | Change submission status |
| `experience_years` | int | Years of experience |
| `expected_salary` | decimal | Expected salary |
| `availability_date` | date | `YYYY-MM-DD` or `DD-MM-YYYY` |
| `cover_letter` | string | Cover letter text |
| `notes` | string | Admin notes |
| `rating` | int | 1–5 rating |
| `company` | int | FK to Company |
| `position` | int | FK to Rank |
| `reviewed_by` | int | FK to User (reviewer) |
| `reviewed_date` | date | Review date |

#### User Info Write Fields
| Field | Type | Description |
|---|---|---|
| `user_first_name` | string | Updates `user.first_name` |
| `user_middle_name` | string | Updates `user.middle_name` |
| `user_email` | email | Updates `user.email` |
| `salary` | string | Updates `user.salary` |
| `company_name_input` | string | Renames the linked Company |
| `position_name_input` | string | Renames the linked Rank |
| `reviewed_by_name` | string | Updates reviewer's first name |

#### Ranks & Codes
| Field | Type | Description |
|---|---|---|
| `coded_rank_input` | list | `[{rank_code, rank_name, assigned_code}]` — **replaces all** user ranks |
| `assigned_code_updates` | list | `[{user_rank_id, assigned_code}]` — updates `assigned_code` on specific existing ranks **without replacing others** |

> ℹ️ Get `user_rank_id` from `coded_rank[].id` in the GET response.

#### Certificates
| Field | Type | Description |
|---|---|---|
| `certificate_ids` | list[int] | List of Certificate IDs — **replaces all** user STCW certificates |

#### Document Sections (PATCH)
| Field | Type | Accepted Keys |
|---|---|---|
| `passport_update` | dict | `passport_no, issue_date, expiry_date, issued_by, place_of_issue` |
| `seaman_book_update` | dict | `seaman_book_no, issue_date, expiry_date, issued_by, place_of_issue` |
| `other_seaman_book_update` | dict | Same keys as `seaman_book_update` |
| `coc_update` | dict | `certificate_name, certificate_number, issue_date, expiry_date, issued_by, issued_at` |
| `goc_update` | dict | `certificate_number, issue_date, expiry_date, issued_by, issued_at` |
| `licenses_update` | list | See table below |

**`licenses_update` entry behavior:**

| Entry | Action |
|---|---|
| `{document_name, document_number, ...}` (no `id`) | ✅ **Create** new license |
| `{id, ...fields...}` | ✅ **Update** existing license |
| `{id, "_delete": true}` | ✅ **Delete** license |

---

### 4.4 Download Endpoints

| Document | Endpoint |
|---|---|
| Passport | `GET /api/cv-submissions/{id}/download-document/?type=passport` |
| Seaman Book | `GET /api/cv-submissions/{id}/download-document/?type=seaman_book` |
| Other Seaman Book | `GET /api/cv-submissions/{id}/download-document/?type=other_seaman_book` |
| Marlins Test | `GET /api/cv-submissions/{id}/download-document/?type=marlins` |
| CES Test | `GET /api/cv-submissions/{id}/download-document/?type=ces` |
| License file | `GET /api/licenses/{license_id}/download/` |

> Files are returned as downloadable attachments. Returns `404` if no file is uploaded for that type.

---

### 4.5 Assign Ranks (separate user endpoints)

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/users/{user_id}/ranks/` | List all ranks for a user (includes `assigned_code`) |
| `POST` | `/api/users/{user_id}/ranks/add/` | Add one rank (`{rank_id}`) — `assigned_code` auto-generated |
| `POST` | `/api/users/{user_id}/assign-rank/{rank_id}/` | Shortcut — add rank by URL |
| `DELETE` | `/api/users/{user_id}/ranks/{rank_id}/remove/` | Remove a specific rank |

> `assigned_code` is **auto-generated** as `{rank_prefix}.001`, `.002`, etc. (e.g. `DO-2.005`).
> It can be manually overridden via `assigned_code_updates` on PATCH `/api/cv-submissions/{id}/`.

---

### 4.6 `assigned_code` Flow

```
1. Admin calls POST /api/users/{user_id}/ranks/add/  →  UserRank created
                                                         ↓
2. UserRank.save() fires                             →  assigned_code auto-set (e.g. "DO-2.005")
                                                         ↓
3. GET /api/cv-submissions/{id}/                     →  coded_rank[] includes assigned_code
                                                         ↓
4. PATCH with assigned_code_updates                  →  update specific rank's code without replacing others
```

---



## 5. 🎤 Interviews
**Purpose:** Schedule and track interview sessions

| What to Show | Data Source |
|---|---|
| Candidate | `Interview.candidate` → `Users.first_name` |
| Interviewer | `Interview.interviewer` (from `interviews` app) OR `Interview.interviewer_name/email` (from `api` app) |
| Date & Time | `Interview.date` / `Interview.scheduled_date` + `scheduled_time` |
| Type | `Interview.interview_type` (Phone / Video / In-Person / Technical) |
| Status | `Interview.status` (Scheduled / Completed / Cancelled / Rescheduled / No Show) |
| Result | `Interview.result` (Pending / Passed / Failed / On Hold) |
| Company | `Interview.company` → `Company.company_name` |
| Position applied for | `Interview.position` → `Rank.name` |
| Meeting link | `Interview.meeting_link` |
| Notes / Feedback | `Interview.notes`, `Interview.feedback` |

> ⚠️ There are **two Interview models**: one in `api/models.py` (more detailed) and one in `interviews/models.py` (simpler). The admin should likely consolidate on the one in `api/models.py`.

---

## 6. 📁 Documents
**Purpose:** Manage all personal documents, licenses, and certificates per seafarer

### Sub-sections:

#### 🪪 Personal Documents
| Field | Source |
|---|---|
| Document type | `PersonalDocument.document_type` (Passport, Seaman's Book, etc.) |
| Document number | `PersonalDocument.document_number` |
| Issue / Expiry dates | `PersonalDocument.issue_date`, `PersonalDocument.expiry_date` |
| Issuing country / authority | `PersonalDocument.issuing_country`, `PersonalDocument.issued_by` |
| File attachment | `PersonalDocument.file` |

#### 🏅 Licenses / Certificates of Competency
| Field | Source |
|---|---|
| License name | `UserLicense.document_name` (COC, GOC, Engineer cert, etc.) |
| Document number | `UserLicense.document_number` |
| Country of issue | `UserLicense.country_of_issue` |
| Issue / Expiry dates | `UserLicense.issue_date`, `UserLicense.expiration_date` |
| File | `UserLicense.document_file` |

#### 📜 Training Certificates (STCW)
| Field | Source |
|---|---|
| Certificate type | `Users.certificates` (ManyToMany → `Certificate` model) with 50+ STCW choices |

#### 🔵 Passports & Seaman Books (stored inline on Users)
| Field | Source |
|---|---|
| Passport | `Users.passport_no`, `passport_issue_date`, `passport_expiry_date`, `passport_issued_by`, `passport_attachment` |
| Seaman Book | `Users.seaman_book_no`, `seaman_book_issue_date`, `seaman_book_expiry_date`, `seaman_book_attachment` |
| Other Seaman Book | `Users.other_seaman_book_*` fields |

---

## 7. 👤 Users
**Purpose:** Full seafarer profile management

This is the most data-rich section. Each user record spans:

### 👤 Personal Info
- `first_name`, `middle_name`, `email`, `profile_image`
- `age`, `date_of_birth`, `blood_type`, `smoker`
- `nationality`, `Place_Of_Birth`, `marital_status`
- `address`, `phone_number`, `tel_number`, `country`, `city`
- `Nearest_Port`

### 🎯 Position & Status
- `application_for_position`, `available_date`
- `user_status` (ON_SITE / VACATION / MEDICAL VACATION)
- `role` (Admin / HR Manager / Recruiter / Employee)
- `register_code`, `register_date`, `generated_id`
- `is_blacklisted`, `blacklist_reason`

### 🎓 Professional
- `codes` (ManyToMany → `Rank` ranks held)
- `certificates` (ManyToMany → `Certificate` STCW certs)
- `marlins_test_result`, `ces_test_result` + dates/attachments
- `salary`
- Sea service history → `SeaService` related records

### 📏 Physical Info
- `Height_Cm`, `Weight_Kg`
- `overall_size`, `shirt_size`, `trouser_size`, `shoes_size`

### 🌍 Languages
- `LanguageProficiency` / `UserLanguage` related records (language, level, CEFR)
- `english_language_level`, `other_language`, `other_language_level`

### 🏥 Health & Vaccinations
- `health_flag_state`, `health_number`, `health_issue_date`, `health_expiry_date`
- `international_medical_number/issue/expiry`
- `yellow_fever_*`, `cholera_*`
- `covid_vaccine_name`, `covid_first_dose`, `covid_second_dose`

### 🛂 Visa Info
- `us_visa_status`, `schengen_visa_status`
- `passport_no`, `passport_expiry_date`
- `seaman_book_no`, `seaman_book_expiry_date`

### 👨‍👩‍👧 Next of Kin
- `NextOfKin` related records: `full_name`, `relationship`, `phone`, `email`

### 📝 Declaration / Health History
- `Declaration` related records: disease, accident, psychiatric, addiction history
- `consent_given`, `declaration_date`

### 📊 Performance
- `PerformanceAppraisal` records: rating (1–5), vessel, date, evaluator
- `BlacklistRecord` history

### 📄 References
- `Reference` records: company name, position, contact info

### ⚙️ COC / GOC (on Users model directly)
- `coc_certificate_name`, `coc_certificate_number`, `coc_issue_date`, `coc_expiry_date`
- `goc_certificate_number`, `goc_issue_date`, `goc_expiry_date`

---

## 8. 💰 Finance
**Purpose:** Track financial records / payroll per seafarer

| What to Show | Data Source |
|---|---|
| Seafarer name | `FinanceRecord.user` → `Users.first_name` |
| Company | `FinanceRecord.company` → `Company.company_name` |
| Status | `FinanceRecord.status` (Pending / Paid / Overdue / Cancelled) |
| Period (start–end date) | `FinanceRecord.start_date`, `FinanceRecord.end_date` |
| Total days worked | Computed: `(end_date - start_date).days + 1` |
| Daily rate | Computed: `Company.hourly_rate × 8` |
| Total payout | Computed: `total_days × daily_rate` |

> ⚠️ The `Finance` module is **relatively thin** right now. You may want to expand it with: salary advance records, contract salary from `Contract.salary`, and currency from `Contract.currency`.

---

## 9. 🤖 AI Assistant
**Purpose:** AI-powered assistant for the admin

Based on the `ai_agents` and `ai_document` directories, this section would provide:
- Natural language search over seafarer profiles
- Document generation (contracts, reference letters)
- Intelligent recommendations for job-seafarer matching
