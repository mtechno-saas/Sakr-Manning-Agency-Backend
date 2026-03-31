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
**Purpose:** Track application/submission pipeline per seafarer + company

| What to Show | Data Source |
|---|---|
| Applicant name | `CVSubmission.user` → `Users.first_name` |
| Applied position | `CVSubmission.position` → `Rank.name` |
| Target company | `CVSubmission.company` → `Company.company_name` |
| Submission status | `CVSubmission.status` (Pending → Under Review → Shortlisted → Hired / Rejected) |
| Submission date | `CVSubmission.submitted_date` |
| Experience years | `CVSubmission.experience_years` |
| Expected salary | `CVSubmission.expected_salary` |
| Cover letter | `CVSubmission.cover_letter` |
| CV file | `CVSubmission.cv_file` |
| Reviewed by / date | `CVSubmission.reviewed_by`, `CVSubmission.reviewed_date` |
| Rating | `CVSubmission.rating` |
| Notes | `CVSubmission.notes` |

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
