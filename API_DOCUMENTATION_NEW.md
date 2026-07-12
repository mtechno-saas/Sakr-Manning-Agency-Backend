# Sakr Manning Agency Backend — Full API Documentation

> **Source:** `E:\2-TECHNO AQUARE` (branch: `server-updates`)
> **Stack:** Django 5 + Django REST Framework + SimpleJWT + LangChain (Groq / Gemini)
> **Base URL (local):** `http://localhost:8000`
> **Base URL (prod):** `https://api.sakrshipping.com` (configure via `ALLOWED_HOSTS`)
> **Auth:** Bearer JWT (access + refresh) obtained from `/api/login/` or `/api/auth/google/`

---

## Table of contents

1. [Authentication & global conventions](#1-authentication--global-conventions)
2. [Role & permission model](#2-role--permission-model)
3. [Core reference data](#3-core-reference-data) — `core/`
4. [User & account management](#4-user--account-management) — `api/`
5. [Seafarer application (aggregated profile)](#5-seafarer-application-aggregated-profile)
6. [Profile sub-resources](#6-profile-sub-resources) — languages, declarations, NOK, personal docs, refs, sea service
7. [Quick-applier document workflow](#7-quick-applier-document-workflow)
8. [CV Submissions](#8-cv-submissions)
9. [Contracts / Documents Management](#9-contracts--documents-management)
10. [Interviews](#10-interviews)
11. [Companies & Job Orders](#11-companies--job-orders)
12. [Ships & crew assignment](#12-ships--crew-assignment)
13. [Tickets & traveling papers](#13-tickets--traveling-papers)
14. [Licenses (COC / GOC / STCW)](#14-licenses-coc--goc--stcw)
15. [Vaccinations & medical](#15-vaccinations--medical)
16. [Marine courses](#16-marine-courses)
17. [Finance records](#17-finance-records)
18. [Logistics (flights, visas, joining instructions)](#18-logistics-flights-visas-joining-instructions)
19. [Compliance (audits, incidents)](#19-compliance-audits-incidents)
20. [AI document processor (LangChain RAG)](#20-ai-document-processor-langchain-rag)
21. [AI chat agent (search & conversation)](#21-ai-chat-agent-search--conversation)
22. [Contract generation (DOCX)](#22-contract-generation-docx)
23. [Global search](#23-global-search)
24. [Choice / dropdown endpoints](#24-choice--dropdown-endpoints)

---

## 1. Authentication & global conventions

| Item | Value |
|---|---|
| Auth scheme | `Authorization: Bearer <access_token>` header |
| Token type | JWT (Simple JWT) |
| Token lifetime | Access: 60 min · Refresh: 1 day (configurable in `settings.py`) |
| CORS | Open to `*` in dev; `CORS_ALLOWED_ORIGINS` in prod |
| File uploads | `multipart/form-data` (`MultiPartParser` + `FormParser` + `JSONParser` per viewset) |
| Date format | `YYYY-MM-DD` (some endpoints also accept `DD/MM/YYYY` and `DD-MM-YYYY`) |
| Time zone | `Asia/Riyadh` (server config) |
| Default user-role for self-registration | `Employee` |
| Default user-role for new applicants via Quick-Applier | `Employee` (password unusable until set) |

### 1.1 `POST /api/login/`

**Permission:** `AllowAny`

**Request body**
```json
{ "email": "user@sakrshipping.com", "password": "plaintext" }
```

**Response 200**
```json
{ "access": "<jwt_access>", "refresh": "<jwt_refresh>" }
```

**Response 401** — invalid credentials.

### 1.2 `POST /api/login/refresh/`

**Permission:** `AllowAny`

**Request body**
```json
{ "refresh": "<jwt_refresh>" }
```

**Response 200** `{ "access": "<new_access>" }`

### 1.3 `POST /api/register/`

**Permission:** `AllowAny` · **View:** `RegisterView` (creates `Users` w/ `role=Employee`)

**Request body** (subset of user fields)
```json
{
  "email": "new.user@example.com",
  "first_name": "John",
  "middle_name": "Smith",
  "password": "chooseapassword",
  "password2": "chooseapassword",
  "phone_number": "+20123456789"
}
```

**Response 201** — full `UserSerializer` payload (see §4.1).

### 1.4 `POST /api/logout/`

**Permission:** `IsAuthenticated`

Clears the `online_user_<id>` cache key. **No body.**

**Response 200** `{ "message": "Successfully logged out" }`

### 1.5 `POST /api/auth/google/`

**Permission:** `AllowAny` · **View:** `GoogleAuthView`

**Request body**
```json
{ "id_token": "<Google ID token from frontend>" }
```

**Response 200**
```json
{
  "access":  "<jwt_access>",
  "refresh": "<jwt_refresh>",
  "user": { "id": 12, "email": "...", "first_name": "...", "middle_name": "...", "role": "Employee" }
}
```

**Errors**
- `400` — invalid / unverified token
- `403` — account deactivated
- `503` — OAuth not configured on server

### 1.6 `GET /api/verify-email/<uidb64>/<token>/`

**Permission:** `AllowAny` · **View:** `VerifyEmailView`

Verifies the email link sent to newly-approved applicants. On success redirects to `https://test.sakrshipping.com/form`; on failure redirects to `https://test.sakrshipping.com/auth?error=invalid_token`. **No body / JSON response.**

---

## 2. Role & permission model

The system recognises five user roles (defined in `api/permissions.py`):

| Role | Read all | Write all | Bulk ops | User mgmt |
|---|---|---|---|---|
| **Admin** | ✅ | ✅ | ✅ | ✅ |
| **HR Manager** | ✅ | ✅ non-Admin records | ✅ | non-Admin users |
| **Recruiter** | ✅ | limited (no delete) | ❌ | view only |
| **Employee** | own only | own only | ❌ | own only |
| **Crew** | own only | own only | ❌ | own only |

**Special permission classes** (see `api/permissions.py`):

- `IsAdmin` — `role == "Admin"`
- `IsHRManager` — `role in {Admin, HR Manager}`
- `IsRecruiter` — `role in {Admin, HR Manager, Recruiter}`
- `IsEmployee` — any authenticated user
- `IsHROrReadOnly` — HR/Admin can write, others read-only
- `IsOwnerOrHR` — object-level: Admin/HR sees all, others see their own
- `CVPermission`, `InterviewPermission`, `FinancePermission`, `CompanyPermission`, `ContractPermission`, `JobOrderPermission`, `UserPermission` — composite object-level rules
- `IsShipManagerOrAdmin` (`ships/permissions.py`) — `Admin` or `groups ∈ {Ship Manager, Admin}`
- `IsOwner` (`vaccinations/permissions.py`) — only the vaccination owner

**Forbidden combinations enforced in code**
- HR Manager **cannot** create/edit `Admin` users.
- Recruiter **cannot** delete or edit `Declaration`, `NextOfKin` records (read-only).

---

## 3. Core reference data

Base path: `/api/core/` (and `api/flags/`, `api/vessel-types/`, `api/company-types/`).

### 3.1 `Flag` resource

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/core/flags/` | `IsAuthenticated` | list |
| POST | `/api/core/flags/` | `IsAuthenticated` | create |
| GET | `/api/core/flags/{id}/` | `IsAuthenticated` | detail |
| PUT/PATCH | `/api/core/flags/{id}/` | `IsAuthenticated` | update |
| DELETE | `/api/core/flags/{id}/` | `IsAuthenticated` | delete |

**Model fields** (`Flag`): `id`, `name` (unique), `icon` (image, optional)

### 3.2 `VesselType` resource

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/core/vessel-types/` | `IsAuthenticated` | list |
| POST | `/api/core/vessel-types/` | `IsAuthenticated` | create |
| GET / PUT / PATCH / DELETE | `/api/core/vessel-types/{id}/` | `IsAuthenticated` | CRUD |

**Model fields:** `id`, `name` (unique)

### 3.3 `CompanyType` resource

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET / POST | `/api/core/company-types/` | `IsAuthenticated` | CRUD via router |
| GET / PUT / PATCH / DELETE | `/api/core/company-types/{id}/` | `IsAuthenticated` | detail |

**Model fields:** `id`, `name` (unique)

---

## 4. User & account management

Base path: `/api/users/` and `/api/`. **View:** `UserViewSet` (also `RegisterView`, `LogoutView`, function-based helpers).

### 4.1 `UserSerializer` response shape (paginated list / detail)

```json
{
  "id": 12,
  "email": "john.doe@example.com",
  "first_name": "John",
  "middle_name": "Smith",
  "profile_image": "https://.../users/avatar.jpg",
  "role": "Employee",
  "is_online": false,
  "is_active": true,
  "is_blacklisted": false,
  "is_staff": false,
  "is_superuser": false,
  "user_status": "ON_SITE",
  "application_for_position": "Master / Captain",
  "other_position": null,
  "available_date": "2026-08-01",
  "register_date": "2026-01-15",
  "last_updated_date": "2026-07-10T10:00:00Z",
  "register_code": "REG-123",
  "nationality": "Egyptian",
  "Place_Of_Birth": "Alexandria",
  "Nearest_Port": "Alexandria",
  "Height_Cm": 178,
  "Weight_Kg": 75,
  "age": 32,
  "date_of_birth": "1994-06-18",
  "marital_status": "MARRIED",
  "blood_type": "O+",
  "smoker": false,
  "us_visa_status": "C1/D valid",
  "schengen_visa_status": "Valid",
  "college_or_school": "Arab Academy",
  "address": "123 Nile St",
  "country": "Egypt",
  "city": "Alexandria",
  "phone_number": "+20123456789",
  "tel_number": "+2031234567",
  "generated_id": "123456",

  "passport_no": "A1234567",
  "passport_issue_date": "2022-01-01",
  "passport_expiry_date": "2032-01-01",
  "passport_issued_by": "MOI Egypt",
  "passport_place_of_issue": "Alexandria",
  "passport_attachment": "/media/passports/...",

  "seaman_book_no": "SB-001",
  "seaman_book_issue_date": "2021-05-01",
  "seaman_book_expiry_date": "2031-05-01",
  "seaman_book_issued_by": "...",
  "seaman_book_place_of_issue": "...",
  "seaman_book_attachment": "/media/seaman_books/...",

  "other_seaman_book_no": "...",
  "other_seaman_book_attachment": "/media/other_seaman_books/...",

  "e_reg_no": "...", "license_no": "...",
  "coc_certificate_name": "Master",
  "coc_certificate_number": "COC-001",
  "coc_issue_date": "2020-01-01",
  "coc_expiry_date": "2030-01-01",
  "coc_issued_by": "EAMS",
  "coc_issued_at": "Alex.",
  "goc_certificate_number": "GOC-001",
  "goc_issue_date": "...", "goc_expiry_date": "...",
  "goc_issued_by": "NTRA", "goc_issued_at": "Cairo",

  "next_of_kin_full_name": "Jane Doe",
  "next_of_kin_relationship": "Wife",
  "next_of_kin_address_country": "Egypt",
  "next_of_kin_phone": "+20100000000",
  "next_of_kin_phone2": null,
  "next_of_kin_email": "jane@example.com",

  "health_flag_state": "Egypt", "health_number": "...",
  "health_issue_date": "...", "health_expiry_date": "...",
  "health_issued_by": "...", "health_issued_at": "...",
  "international_medical_number": "...",
  "international_medical_issue_date": "...",
  "international_medical_expiry_date": "...",
  "yellow_fever_number": "...",
  "yellow_fever_issue_date": "...",
  "yellow_fever_expiry_date": "...",
  "cholera_number": "...",
  "cholera_issue_date": "...",
  "cholera_expiry_date": "...",

  "covid_vaccine_name": "Pfizer",
  "covid_first_dose": "2021-08-01",
  "covid_second_dose": "2021-09-01",
  "covid_other_doses_or_remarks": "Booster 2022",

  "overall_size": "L", "shirt_size": "L", "trouser_size": "32",
  "shoes_size": "42",
  "english_language_level": "Good",
  "other_language": "Arabic",
  "other_language_level": "Native",
  "disease_history": "...",
  "accident_history": "...",
  "psychiatric_treatment_history": "...",
  "addiction_history": "...",
  "declaration_consent": true,
  "declaration_date": "2026-01-15",
  "declaration_place": "Alexandria",
  "initial_assessment_comments": "...",
  "responsible_person_name": "...",
  "assessment_date": "2026-01-20",

  "salary": "3500",
  "marlins_test_result": "85%",
  "marlins_test_issued_date": "2025-01-01",
  "marlins_test_issued_at": "Alexandria",
  "marlins_test_issued_by": "Marlins Test Center",
  "marlins_test_attachment": "/media/marlins_tests/...",

  "ces_test_result": "Pass",
  "ces_test_issued_date": "2025-01-01",
  "ces_test_issued_at": "Alexandria",
  "ces_test_issued_by": "CES Center",
  "ces_test_attachment": "/media/ces_tests/...",

  "title": null, "file": null, "position": null,
  "certificates": [1, 2, 3],
  "codes": [4, 5],
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-07-10T10:00:00Z"
}
```

### 4.2 Standard user CRUD (`UserViewSet`)

Base path: `/api/users/`

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/users/` | Auth + `UserPermission` | list (Admin/HR/Recruiter see all; Employee sees self) |
| POST | `/api/users/` | Auth + `UserPermission` | create (HR can't create Admin) |
| GET | `/api/users/{id}/` | Auth + `UserPermission` | detail (own profile if Employee) |
| PUT / PATCH | `/api/users/{id}/` | Auth + `UserPermission` | update |
| DELETE | `/api/users/{id}/` | Admin only | delete |

**Query params supported by `UsersFilter`:** `role`, `is_active`, `is_blacklisted`, `nationality`, `user_status`, `company`, `search`, `position` etc. (see `api/filters.py`).

### 4.3 `POST /api/users/bulk-delete/`

**Permission:** Admin or HR Manager only (`UserViewSet.bulk_delete`)

**Request body**
```json
{ "ids": [12, 13, 14] }
```

**Response 200** `{ "message": "Successfully deleted 3 users" }`

### 4.4 `POST /api/users/bulk-edit/`

**Permission:** Admin or HR Manager only (`UserViewSet.bulk_edit`)

**Request body**
```json
{
  "ids": [12, 13],
  "data": {
    "user_status": "ON_SITE",
    "role": "Crew",
    "is_active": true,
    "is_blacklisted": false,
    "rank": "Master"
  }
}
```

**Response 200** `{ "message": "Successfully updated 2 users" }`

> Only the whitelisted fields above are honoured. `rank` is resolved via `assign_rank_by_position` logic.

### 4.5 `GET /api/users/me/`

**Permission:** Authenticated

Returns the `UserMeSerializer` (a slim user view) for the calling user.

### 4.6 `GET /api/users/stats/`

**Permission:** Admin or HR Manager only

**Response 200**
```json
{
  "total_users": 234,
  "admins": 2,
  "hr_managers": 3,
  "recruiters": 5,
  "employees": 198,
  "crew": 26,
  "active_users": 220
}
```

### 4.7 `GET /api/users/{id}/full-profile/`

**Permission:** Authenticated (own profile or HR+)

Returns the user record + embedded `contracts` array (`ContractListSerializer`).

### 4.8 `GET /api/users/{id}/download-full-profile-pdf/`

**Permission:** `AllowAny` (intended for direct `<a href>` in the browser)

**Response 200** — `application/pdf` (generated by `api/pdf_generator.py`)

### 4.9 User document downloads (all `AllowAny` for browser direct-link)

| Path | Returns |
|---|---|
| `GET /api/users/{id}/download-passport/` | `user.passport_attachment` |
| `GET /api/users/{id}/download-seaman-book/` | `user.seaman_book_attachment` |
| `GET /api/users/{id}/download-other-seaman-book/` | `user.other_seaman_book_attachment` |
| `GET /api/users/{id}/download-marlins/` | `user.marlins_test_attachment` |
| `GET /api/users/{id}/download-ces/` | `user.ces_test_attachment` |
| `GET /api/users/{id}/download-personal-document/{doc_id}/` | `PersonalDocument.file` |
| `GET /api/users/{id}/download-license/{license_id}/` | `UserLicense.document_file` |
| `GET /api/users/{id}/download-vaccination/{vaccination_id}/` | `Vaccination.document` |
| `GET /api/users/{id}/download-course/{course_id}/` | `Course.document` |
| `GET /api/users/{id}/download-sea-service/{service_id}/` | `SeaService.file` |
| `GET /api/users/{id}/download-document/?type=<type>&doc_id=<id>` | Universal dispatcher (see below) |

**`download-document` `type` values** (singleton, no `doc_id`): `passport`, `seaman_book`, `other_seaman_book`, `marlins`, `ces`, `profile_image`, `file`, `coc`, `goc`, `health_certificate`
**`type` values (related, `doc_id` required):** `license`, `sea_service`, `course`, `vaccination`, `personal_document`

### 4.10 Standalone user-list endpoints (`api/urls.py`)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/all/` | `IsAuthenticated`, role in `{Admin, HR Manager, Recruiter}` | wrapper around `Users.objects.all()` → `{ "users": [...] }` |
| POST | `/api/create/` | Admin/HR (HR can't create Admin) | `multipart/form-data` allowed; `UserSerializer` |
| GET | `/api/filter/?...` | Admin/HR/Recruiter | uses `UsersFilter` |
| GET | `/api/users/{pk}/` | function-based `user_detail` (own or HR+) | GET/PUT/DELETE |
| DELETE | `/api/users/{pk}/` | Admin only | function-based |
| POST | `/api/users/{user_id}/assign-rank/{rank_id}/` | Admin/HR | creates `UserRank` |
| POST | `/api/users/{user_id}/assign-by-position/` | Admin/HR | auto-creates `Rank` + `UserRank` with auto `assigned_code` (see §24) |

**`assign-by-position` request body**
```json
{ "position": "Master" }   // or a rank ID as a string of digits
```
**Response 201**
```json
{
  "message": "Rank 'Master' successfully assigned to John Smith.",
  "rank_created_in_db": false,
  "user_rank": {
    "id": 99, "user": 12, "rank": 7, "assigned_code": "MST.001",
    "rank_name": "Master", "rank_code": "MST"
  }
}
```

### 4.11 User-specific certificate & rank helpers

| Method | Path | Permission | Body | Notes |
|---|---|---|---|---|
| GET | `/api/users/{user_id}/certificates/` | own or HR+ | – | `{ user_id, user_name, certificates: [...] }` |
| GET | `/api/users/{user_id}/ranks/` | own or HR+ | – | `{ user_id, user_name, ranks: [...] }` |
| POST | `/api/users/{user_id}/certificates/add/` | Admin/HR | `{ "certificate_id": 1 }` | 201 |
| POST | `/api/users/{user_id}/ranks/add/` | Admin/HR | `{ "rank_id": 7 }` | 201 (409 if duplicate) |
| DELETE | `/api/users/{user_id}/certificates/{certificate_id}/remove/` | Admin/HR | – | 200 |
| DELETE | `/api/users/{user_id}/ranks/{rank_id}/remove/` | Admin/HR | – | 200 |

---

## 5. Seafarer application (aggregated profile)

Base path: `/api/seafarer-application/` · **View:** `SeafarerApplicationViewSet` (uses `SeafarerApplicationSerializer`).

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/seafarer-application/` | Auth (Employee sees only self) | list (slim) |
| POST | `/api/seafarer-application/` | Auth | create (typically called only for new users) |
| GET | `/api/seafarer-application/{id}/` | Auth (own or HR+) | full aggregated profile |
| PUT / PATCH | `/api/seafarer-application/{id}/` | Auth | update |
| DELETE | `/api/seafarer-application/{id}/` | **Admin only** | delete |

**Response shape** — the full `Users` payload (same as §4.1) plus embedded sub-resources (`sea_services`, `user_documents`, `certificates`, `next_of_kins`, `personal_documents`, `declarations`, `user_languages`, `interviews`, `contracts`, etc.). Designed as the one-shot "complete profile" payload used by the front-end's applicant view.

---

## 6. Profile sub-resources

### 6.1 `LanguageProficiency` (own only)

Path: `/api/my-languages/` · **View:** `LanguageProficiencyViewSet` · **Permission:** `IsAuthenticated`, queryset forced to `user=request.user`.

| Method | Path | Notes |
|---|---|---|
| GET / POST | `/api/my-languages/` | list / create (auto-binds to `request.user`) |
| GET / PUT / PATCH / DELETE | `/api/my-languages/{id}/` | CRUD |

**Fields:** `id`, `user`, `language`, `proficiency` (`Elementary|Intermediate|Advanced|Native`), `created_at`, `updated_at`

### 6.2 `UserLanguage` (rich language record)

Path: `/api/user-languages/` · **View:** `UserLanguageViewSet` · **Permission:** `IsAuthenticated`; roles limited to `Admin`, `HR Manager`, `Employee`.

| Method | Path | Notes |
|---|---|---|
| GET / POST | `/api/user-languages/` | Admin/HR see all, Employee sees own |
| GET / PUT / PATCH / DELETE | `/api/user-languages/{id}/` | object-level: own or HR+ |

**Fields:** `id`, `user`, `language`, `general_remarks`, `speaking_level`, `writing_level`, `reading_level`, `cefr_level` (A1–C2), `cefr_description`, `attachment`, `created_at`, `updated_at`

### 6.3 `PersonalDocument` (travel / ID docs)

Path: `/api/personal-documents/` · **View:** `PersonalDocumentViewSet` · **Permission:** `IsAuthenticated`; Admin/HR/Recruiter see all, Employee sees own.

| Method | Path |
|---|---|
| GET / POST | `/api/personal-documents/` |
| GET / PUT / PATCH / DELETE | `/api/personal-documents/{id}/` |

**Fields:** `id`, `user`, `document_type` (see §24), `document_number`, `issue_date`, `expiry_date`, `issuing_country`, `issued_by`, `place_of_issue`, `file`, `created_at`, `updated_at`

### 6.4 `NextOfKin` (emergency contact)

Path: `/api/next-of-kin/` · **View:** `NextOfKinViewSet`

| Method | Path | Permission |
|---|---|---|
| GET / POST | `/api/next-of-kin/` | Admin/HR/Recruiter see all, Employee sees own |
| PUT / PATCH | `/api/next-of-kin/{id}/` | Employee: own only · Recruiter: read-only (403) |
| DELETE | `/api/next-of-kin/{id}/` | Recruiter: 403 · Employee: own only |

**Fields:** `id`, `user`, `full_name`, `relationship` (Father/Mother/Brother/Sister/Wife/Husband/Son/Daughter/Uncle/Aunt/Friend/Other), `address_country`, `phone`, `phone2`, `email`, `created_at`, `updated_at`

### 6.5 `Declaration` (health declaration)

Two URLs (back-compat):
- `/api/declarations/` (ViewSet primary)
- `/api/users/declarations/` and `/api/users/declarations/{id}/` (ViewSet proxy for the front-end)

**View:** `DeclarationViewSet` · **Permission:** `IsAuthenticated`

| Method | Path | Permission |
|---|---|---|
| GET / POST | `/api/declarations/` | Admin/HR/Recruiter: all · Employee: own |
| GET / PUT / PATCH / DELETE | `/api/declarations/{id}/` | Employee: own only · Recruiter: 403 on writes |

**Fields:** `id`, `user`, `has_disease`, `disease_details`, `has_accident`, `accident_details`, `has_psychiatric_treatment`, `psychiatric_treatment_details`, `has_addiction`, `addiction_details`, `consent_given`, `declaration_place`, `declaration_date`, `signature`, `created_at`, `updated_at`

> Saving a `Declaration` syncs back to the parent `Users.disease_history`, `accident_history`, `psychiatric_treatment_history`, `addiction_history`, `declaration_place`, `declaration_date`, `declaration_consent`.

### 6.6 `Reference`

Path: `/api/references/` · **View:** `ReferenceViewSet` · **Permission:** `IsAuthenticated`

| Method | Path | Notes |
|---|---|---|
| GET | `/api/references/?user={id}` | filtered by query param, else only own |
| POST | `/api/references/` | `user` in body or defaults to `request.user` |
| GET / PUT / PATCH / DELETE | `/api/references/{id}/` | CRUD |

**Fields:** `id`, `user`, `company_name`, `position`, `name`, `tel`, `email`

### 6.7 `SeaService`

Path: `/api/sea-services/` · **View:** `SeaServiceViewSet` · **Permission:** `IsAuthenticated`

| Method | Path | Notes |
|---|---|---|
| GET | `/api/sea-services/?user={id}` | filtered by query param |
| POST | `/api/sea-services/` | `user` in body (or defaults to `request.user` for Employees) |
| GET / PUT / PATCH / DELETE | `/api/sea-services/{id}/` | CRUD |

**Fields:** `id`, `user`, `company_name`, `rank`, `vessel_name_imo`, `vessel_name`, `imo_number`, `flag`, `signed_on`, `signed_off`, `period`, `vessel_type`, `dwt`, `grt`, `engine_type`, `bh`, `kw`, `file` (PDF/DOCX/image), `reason_for_sign_off`

### 6.8 `Certificate` (catalog of certificate types)

Path: `/api/certificates/` · **View:** `CertificateViewSet` · **Permission:** `IsAuthenticated + IsHROrReadOnly` (HR/Admin can edit)

| Method | Path | Notes |
|---|---|---|
| GET / POST | `/api/certificates/` | |
| GET / PUT / PATCH / DELETE | `/api/certificates/{id}/` | |

> Compat alias: `/api/users/certificates/` & `/api/users/certificates/{id}/`

### 6.9 `Rank` (position catalog)

Path: `/api/ranks/` · **View:** `RankViewSet` · **Permission:** `IsAuthenticated`

| Method | Path | Notes |
|---|---|---|
| GET / POST | `/api/ranks/` | |
| GET / PUT / PATCH / DELETE | `/api/ranks/{id}/` | |
| GET | `/api/ranks/all/` | flat unpaginated list `[ {id, code, name}, ... ]` for dropdowns |

**Fields:** `id`, `code`, `name`, `assigned_code` (auto-generated, e.g. `MST.001`)

---

## 7. Quick-applier document workflow

The system has two layers for incoming applications:

1. `api.Document` — fast, internal-only record the front-end uses for the "Quick Applier" pipeline (admin uploads, drag-and-drop CVs).
2. `ai_document.Applicant` — extracted JSON store, plus the AI processor that converts documents into structured data.

### 7.1 `Document` resource (Quick Applier)

Path: `/api/documents/` · **View:** `DocumentViewSet` · **Permission:** `IsAuthenticated` (create is `AllowAny`).

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/documents/?status=...&name=...&email=...&position=...&search=...` | `IsAuthenticated` | filterable |
| POST | `/api/documents/` | `AllowAny` (no auth required) | `multipart/form-data` |
| GET / PUT / PATCH / DELETE | `/api/documents/{id}/` | `IsAuthenticated` | |
| POST | `/api/documents/{id}/set_status/` | Admin/HR/Recruiter | see below |
| GET | `/api/documents/stats/` | `IsAuthenticated` | counts |
| GET | `/api/documents/{id}/download/` | `IsAuthenticated` | streams the file |

**`POST /api/documents/` fields** (`multipart/form-data`)
- Required: `file` (PDF/DOCX), `title`
- Optional: `name`, `email`, `phone_number`, `position` (rank name), `position_id`, `user` (existing user id)
- `status` defaults to `Pending`

**`POST /api/documents/{id}/set_status/` body**
```json
{ "status": "Active" }   // Pending | Active | Blacklist
```
On `Active`:
- If the user has no `generated_id`, a random 6-digit one is generated.
- User profile fields (name, email, phone, title, file, position) are synced from the document.
- A `CVSubmission` is created/updated automatically with `status='Approved'`.
- A verification email is sent (Django `send_mail`).

**`GET /api/documents/stats/`** response
```json
{
  "total_applications": 88,
  "pending_applications": 23,
  "active_applications": 60,
  "blacklist_applications": 5
}
```

### 7.2 `Document` model fields (used by serializer)
`id`, `user`, `title`, `file` (PDF/DOCX), `company`, `job_position`, `name`, `email`, `phone_number`, `position` (free-text rank name), `position_id`, `status` (Pending/Active/Blacklist), `created_at`, `updated_at`

### 7.3 Document download proxy on CV Submissions

`GET /api/cv-submissions/{id}/download-document/?type=<type>&doc_id=<id>` — returns the same file types as §4.9 but resolved through the CV's linked user. `AllowAny`.

### 7.4 CV download

`GET /api/cv-submissions/{id}/download-cv/` — streams `CVSubmission.cv_file` (AllowAny).

---

## 8. CV Submissions

Path: `/api/cv-submissions/` · **View:** `CVSubmissionViewSet` · **Permission:** `IsAuthenticated + CVPermission`

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/cv-submissions/` | Admin/HR/Recruiter: all · Employee: own | uses `CVSubmissionFilter` |
| POST | `/api/cv-submissions/` | `CVPermission` | Admin/HR/Recruiter: any · Employee: only own |
| GET | `/api/cv-submissions/{id}/` | `CVPermission` (object) | |
| PUT / PATCH | `/api/cv-submissions/{id}/` | `CVPermission` (object) | |
| DELETE | `/api/cv-submissions/{id}/` | `CVPermission` (object) | removes from ship crew if linked |
| GET | `/api/cv-submissions/stats/` | `IsAuthenticated` | |
| POST | `/api/cv-submissions/upload/` | `IsAuthenticated` | multipart upload (see below) |
| PATCH | `/api/cv-submissions/{id}/update-status/` | Admin/HR/Recruiter | |
| GET | `/api/cv-submissions/{id}/download-cv/` | `AllowAny` | |
| GET | `/api/cv-submissions/{id}/download-document/?type=...&doc_id=...` | `AllowAny` | |

**`POST /api/cv-submissions/upload/`** (`multipart/form-data`)
- Required: `cv_file` (PDF/Word)
- Optional: `position` (rank id), `notes`

**`PATCH /api/cv-submissions/{id}/update-status/`** body
```json
{ "status": "Approved" }   // Pending|Under Review|Interviewed|Shortlisted|Approved|Rejected|Hired
```
On `Approved` / `Rejected` the reviewer and review date are stamped.

**`CVSubmissionFilter` query params (sample):** `status`, `position`, `company`, `ship`, `date_from`, `date_to`, `search`

**`stats` response**
```json
{
  "total": 88,
  "under_review": 20, "interviewed": 12, "pending": 30, "approved": 26,
  "under_review_percent": 23, "interviewed_percent": 14,
  "pending_percent": 34,  "approved_percent": 30
}
```

**Model fields:** `id`, `user`, `company`, `ship`, `position` (Rank FK), `job_position` (JobOrderPosition FK), `cv_file`, `cover_letter`, `experience_years`, `expected_salary`, `availability_date`, `status`, `submitted_date`, `reviewed_by`, `reviewed_date`, `notes`, `rating`, `created_at`, `updated_at`

---

## 9. Contracts / Documents Management

Path: `/api/contracts/` · **View:** `ContractViewSet` · **Permission:** `IsAuthenticated + ContractPermission`

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/contracts/` | Admin/HR/Recruiter: all · Employee: own | uses `ContractFilter` |
| POST | `/api/contracts/` | Admin/HR | |
| GET | `/api/contracts/{id}/` | `ContractPermission` (object) | full `ContractSerializer` |
| PUT / PATCH | `/api/contracts/{id}/` | `ContractPermission` (object) | |
| DELETE | `/api/contracts/{id}/` | `ContractPermission` (object) | restores `job_position.quantity` and `company.open_positions` if linked |
| GET | `/api/contracts/stats/` | `IsAuthenticated` | |
| GET | `/api/contracts/status/` | `IsAuthenticated` | counts per status |

> Each day the viewset bulk-moves any `Active/Signed/Pending Signature/Pending` contract whose `sign_off_date` is in the past to `Draft` (rate-limited to 1× per day via cache).

**`stats` response** (Admin/HR/Recruiter)
```json
{
  "signed_contracts": 30, "pending_signature": 8, "drafts": 5,
  "critical": 3,        // expires within 7 days
  "warning": 7,         // 8–30 days
  "notice": 12          // 31–60 days
}
```

**`status` response** (per status count): `active`, `completed`, `pending`, `signed`, `pending_signature`, `draft`, `cancelled`

**Model fields (`Contract`):** `id`, `user`, `ship`, `company`, `rank`, `job_position`, `sign_on_date`, `sign_off_date`, `salary`, `currency` (USD/EUR/GBP/EGP), `repatriation_terms`, `leave_pay_terms`, `status`, `signed_file`, `signed_at`, `created_at`, `updated_at`

---

## 10. Interviews

Two parallel surfaces (legacy and new):

### 10.1 Primary ViewSet (mounted at `/api/`)

Path: `/api/interviews/` · **View:** `InterviewViewSet` · **Permission:** `IsAuthenticated + InterviewPermission`

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/interviews/` | Admin/HR/Recruiter: all · Employee: own | |
| POST | `/api/interviews/` | Admin/HR/Recruiter | |
| GET | `/api/interviews/{id}/` | `InterviewPermission` (object) | |
| PUT / PATCH | `/api/interviews/{id}/` | `InterviewPermission` (object) | |
| DELETE | `/api/interviews/{id}/` | `InterviewPermission` (object) | |
| GET | `/api/interviews/stats/` | `IsAuthenticated` | |
| GET | `/api/interviews/calendar/?month=&year=` | `IsAuthenticated` | returns `InterviewCalendarSerializer` |
| GET | `/api/interviews/status/` | `IsAuthenticated` | counts |

**`stats` response**
```json
{ "today_interviews": 4, "this_week": 12, "pending_confirmation": 3 }
```

**`status` response**
```json
{ "scheduled": 8, "completed": 14, "cancelled": 2, "rescheduled": 1, "no_show": 1, "total": 26 }
```

### 10.2 Legacy app (`/api/interviews/` from `interviews` app)

`GET /api/interviews/status/` — duplicate of the above (function-based `interview_status`).

**Model fields (`Interview`):** `candidate` (FK Users), `interviewer` (FK Users), `company`, `position` (Rank), `scheduled_date`, `scheduled_time`, `duration_minutes`, `interview_type` (Phone/Video/In-Person/Technical), `location`, `meeting_link`, `interviewer_name`, `interviewer_email`, `status` (Scheduled/Completed/Cancelled/Rescheduled/No Show), `result` (Pending/Passed/Failed/On Hold), `notes`, `feedback`, `created_by`, `created_at`, `updated_at`

---

## 11. Companies & Job Orders

Base path: `/api/companies/`

### 11.1 `CompanyViewSet` (companies app)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/companies/` | `IsAuthenticated` | list w/ filter (`CompanyFilter`) |
| POST | `/api/companies/` | Admin (HR/Recruiter: PUT/PATCH only) | |
| GET | `/api/companies/{id}/` | `IsAuthenticated` | detail (ships + open_positions embedded) |
| PUT / PATCH | `/api/companies/{id}/` | Admin (HR/Recruiter allowed) | |
| DELETE | `/api/companies/{id}/` | Admin | |
| GET | `/api/companies/stats/` | `IsAuthenticated` | aggregate stats |

**`POST /api/companies/` and `PUT/PATCH /api/companies/{id}/` request body**
```json
{
  "company_name":  "MSC Mediterranean",
  "company_type":  "Ship Owner",
  "company_flag":  "Panama",
  "open_positions": 0,
  "status":        "Active",
  "contact_email": "info@msc.example",
  "contact_phone": "+507 800 1234",
  "owner":         "Gianluigi Aponte",
  "website":       "msc.com",
  "hourly_rate":   12.50
}
```

> **Field formats**
> - `company_type` — **string** (the `CompanyType.name`). Must match an existing name in the `core.CompanyType` table (e.g. `Ship Owner`, `Ship Manager`, `Crewing Agency`, `Training Center`, `Other`). Numeric IDs are **not** accepted on this endpoint.
> - `company_flag` — string (the `Flag.name`, e.g. `Panama`) **or** integer ID. If a string is sent and the name doesn't exist, a new `Flag` row is created automatically.
> - `website` — bare hostnames are auto-prefixed with `https://`.

**`stats` response**
```json
{
  "total_companies": 32,
  "by_status":      { "Active": 25, "Inactive": 5, "Prospect": 2 },
  "by_type":        { "Ship Owner": 20, "Ship Manager": 8, "Crewing Agency": 4 },
  "open_positions": { "total": 78, "companies_with_openings": 14 },
  "recent_companies": [ { "id": 99, "company_name": "MSC Mediterranean", "company_type": "Ship Owner", "status": "Active", "created_at": "2026-07-10T10:00:00Z" } ]
}
```

**Detail response shape** (excerpt — `company_type` is the string name, not an ID)
```json
{
  "id": 99,
  "company_name": "MSC Mediterranean",
  "company_type": "Ship Owner",
  "company_type_name": "Ship Owner",
  "company_flag": 7,
  "company_flag_name": "Panama",
  "open_positions": 0,
  "status": "Active",
  "contact_email": "info@msc.example",
  "contact_phone": "+507 800 1234",
  "owner": "Gianluigi Aponte",
  "website": "https://msc.com",
  "hourly_rate": "12.50",
  "ships": [ { "id": 1, "ship_name": "...", "imo_number": "..." } ],
  "open_position_names": [ { "id": 3, "name": "Chief Officer", "count": 2 } ],
  "created_at": "2026-07-10T10:00:00Z",
  "updated_at": "2026-07-10T10:00:00Z"
}
```

**Model fields:** `id`, `company_name` (unique), **`company_type` (string, FK→`core.CompanyType.name` via `SlugRelatedField`)** *(Ship Owner / Ship Manager / Crewing Agency / Training Center / Other)*, `open_positions`, `status` (Active/Inactive/Prospect), `contact_email`, `contact_phone`, `owner`, `website`, **`company_flag` (integer FK to `core.Flag`)** *(string names also accepted on write)*, `hourly_rate`, `created_at`, `updated_at`

> ⚠️ **Note:** There is also a `Company` model in `api.models` (separate, used for legacy data) with fields `name`, `email`, `phone`, `address`, `country`, `contact_person`, etc. The `companies` app's Company is the source of truth for the front-end.

### 11.2 `JobOrderViewSet` (`/api/companies/job-orders/`)

| Method | Path | Permission (`PublicJobOrderPermission`) | Notes |
|---|---|---|---|
| GET | `/api/companies/job-orders/` | Public (anyone) | list w/ filter |
| POST | `/api/companies/job-orders/` | Admin/HR/Recruiter | |
| GET / PUT / PATCH / DELETE | `/api/companies/job-orders/{id}/` | GET public, writes Admin/HR/Recruiter | |

**Model fields:** `id`, `company`, `ship`, `reference_number` (unique, e.g. `JO-2024-001`), `request_date`, `target_joining_date`, `vessel_type_override`, `trading_area`, `status` (Pending/Open/Active/In Progress/Fulfilled/Cancelled), `notes`, `created_at`, `updated_at`, plus nested `positions` array.

### 11.3 `JobOrderPositionViewSet` (`/api/companies/job-positions/`)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/companies/job-positions/` | Public | list |
| POST | `/api/companies/job-positions/` | Admin/HR/Recruiter | **single object OR array (bulk create)** |
| GET / PUT / PATCH / DELETE | `/api/companies/job-positions/{id}/` | GET public, writes Admin/HR/Recruiter | |
| POST | `/api/companies/job-positions/apply/` | **Employee** or higher | Quick-Apply (see below) |

**Single create** body
```json
{ "job_order": 1, "rank": "2nd. Officer", "quantity": 2 }
```
`rank` may be an integer ID or a string name (case-insensitive).

**Bulk create** body (an array)
```json
[
  { "job_order": 1, "rank": "2nd. Officer", "quantity": 2 },
  { "job_order": 1, "rank": "Bosun",       "quantity": 1 }
]
```

**`POST /api/companies/job-positions/apply/`** (Employee Quick-Apply)

Body — IDs, names, or both:
```json
{
  "position_ids":   [1, 2, 3],
  "position_names": ["Bosun", "Chief Cook"]
}
```

Behaviour: For each matching open `JobOrderPosition`, creates a `Document` (status `Pending`) linked to the calling user, the company, and the position. Skips duplicates (already `Pending`/`Active`).

**Response 201**
```json
{
  "applied": [ { "document_id": 412, "position_id": 1, "rank_name": "Master", "company_name": "MSC", "status": "Pending" } ],
  "skipped": [],
  "total_applied": 1, "total_skipped": 0
}
```

**Model fields:** `id`, `job_order`, `rank` (FK `api.Rank`), `quantity`, `salary_min`, `salary_max`, `currency` (default `USD`), `contract_duration_months` (default `6`), `remarks`. The serializer additionally exposes `rank_name`, `company_name`, `ship_name`, `status` (read-only), `filled_slots`, `remaining_slots`, `assigned_to`.

---

## 12. Ships & crew assignment

Path: `/api/ships/` · **View:** `ShipViewSet` · **Permission:** `IsShipManagerOrAdmin` (Admin, superuser, or `Ship Manager` group)

| Method | Path | Permission |
|---|---|---|
| GET / POST | `/api/ships/` | GET public to authenticated; POST Admin/Ship Manager |
| GET / PUT / PATCH / DELETE | `/api/ships/{id}/` | GET public; writes Admin/Ship Manager |
| POST | `/api/ships/{id}/assign-user/` | Admin/Ship Manager |
| POST | `/api/ships/{id}/unassign-user/` | Admin/Ship Manager |

**`assign-user` body** `{ "user_id": 12 }` → adds to crew, also stamps `CVSubmission.ship` and `Contract.ship` for the user's latest records.

**`unassign-user` body** `{ "user_id": 12 }`

**`ShipFilter` query params:** `ship_name`, `imo_number`, `ship_type`, `flag`, `company`, `status`, `year_built__gte/lte`, `gross_tonnage__gte/lte`, etc.

**Model fields:** `id`, `ship_name`, `imo_number` (unique), `company` (FK), `crew` (M2M Users), `ship_type` (FK VesselType), `flag` (FK Flag), `official_no`, `call_sign`, `mmsi_no`, `port_of_registry`, `gross_tonnage`, `deadweight`, `year_built`, `builder`, `engine_type`, `engine_power_kw`, `status` (Active/Under Maintenance/Inactive), `created_at`, `updated_at`. Serializer also exposes `crew` (nested), `crew_ids` (write-only), `flag_name`, `ship_type_name`, `jobs_order_count`, `job_orders` (nested list with positions).

---

## 13. Tickets & traveling papers

Path: `/api/tickets-papers/`

### 13.1 `TicketViewSet` (`/api/tickets-papers/tickets/`)

| Method | Path | Permission |
|---|---|---|
| GET / POST | `/api/tickets-papers/tickets/?user_id={id}` | `IsAuthenticated` (effectively open) |
| GET / PUT / PATCH / DELETE | `/api/tickets-papers/tickets/{id}/` | |

**Fields:** `id`, `user`, `ticket_number`, `file`, `file_url` (read-only absolute URL), `created_at`

### 13.2 `TravelingPaperViewSet` (`/api/tickets-papers/traveling-papers/`)

Same shape. **Fields:** `id`, `user`, `title`, `issued_date`, `file`, `file_url`, `created_at`

> Neither viewset enforces strict role-based permissions — write access is currently open to any authenticated caller.

---

## 14. Licenses (COC / GOC / STCW)

Path: `/api/my-licenses/` · **View:** `UserLicenseViewSet` · **Permission:** `IsAuthenticated`

| Method | Path | Permission |
|---|---|---|
| GET | `/api/my-licenses/?user={id}` | Admin/HR: all · others: own |
| POST | `/api/my-licenses/` | Auth (Admin/HR can assign for any user) |
| GET / PUT / PATCH / DELETE | `/api/my-licenses/{id}/` | Auth |
| GET | `/api/my-licenses/{id}/download/` | Auth |

**Fields:** `id`, `user`, `document_name` (see `DOCUMENT_NAME_CHOICES` in `licenses/models.py` — Master, Chief Officer, Chief Engineer, GMDSS, COC, GOC, Able Seaman, etc.), `document_number`, `country_of_issue`, `issue_date`, `expiration_date`, `document_file` (PDF/JPG/PNG), `download_url`, `created_at`, `updated_at`

---

## 15. Vaccinations & medical

Path: `/api/vaccinations/` · **View:** `VaccinationViewSet` · **Permission:** `IsAuthenticated + IsOwner` (object-level: only the owner can edit/delete)

| Method | Path |
|---|---|
| GET | `/api/vaccinations/` (always scoped to `request.user`) |
| POST | `/api/vaccinations/` (auto-binds to `request.user`) |
| GET / PUT / PATCH / DELETE | `/api/vaccinations/{id}/` |

**Fields:** `id`, `user`, `name` (see `VACCINE_CHOICES` — Yellow Fever, COVID, Medical Certificate For Seafarers, Hepatitis A/B, etc.), `number`, `issue_date`, `expiry_date`, `issued_by`, `issued_at`, `disease`, `first_date`, `last_date`, `remarks`, `document` (PDF/JPG/PNG), `download_url`, `created_at`, `updated_at`

---

## 16. Marine courses

Path: `/api/courses/` · **View:** `CourseViewSet` + `download_course_document` function view

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/courses/` | `IsAuthenticated` (scoped to own) | |
| POST | `/api/courses/` | `IsAuthenticated` (auto-binds to `request.user`) | multipart |
| GET / PUT / PATCH / DELETE | `/api/courses/{id}/` | `IsAuthenticated` | |
| GET | `/api/courses/{course_id}/download/` | `IsAuthenticated` | streams `course.document` as `application/pdf` |

**Fields:** `id`, `user`, `course_name`, `course_number`, `issue_date`, `expiry_date`, `issued_by`, `issued_at`, `country_of_issue`, `document`, `download_url`

---

## 17. Finance records

Two parallel surfaces: `/api/finance-records/` (primary, from `api` app) and `/api/finance/finance-records/` (legacy, from `finance` app). Both expose the same `FinanceRecordSerializer`.

### 17.1 Primary ViewSet (`/api/finance-records/`)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/api/finance-records/` | Admin/HR: all · others: own | uses `FinanceRecordFilter` |
| POST | `/api/finance-records/` | Admin/HR | |
| GET / PUT / PATCH / DELETE | `/api/finance-records/{id}/` | `FinancePermission` (object) | |
| GET | `/api/finance-records/stats/` | Admin/HR | counts |
| GET | `/api/finance-records/export/` | Admin/HR | returns full JSON dump |

### 17.2 Legacy ViewSet (`/api/finance/finance-records/`)

| Method | Path | Notes |
|---|---|---|
| GET / POST | `/api/finance/finance-records/` | |
| GET / PUT / PATCH / DELETE | `/api/finance/finance-records/{id}/` | |
| POST | `/api/finance/finance-records/calculate/` | dry-run (see below) |
| GET | `/api/finance/finance-records/status/` | counts per status |

**`POST .../calculate/` body**
```json
{ "user": 1, "company": 2, "start_date": "2025-09-01", "end_date": "2025-09-10" }
```
**Response 200**
```json
{ "total_days": 10, "daily_rate": 80.00, "total_money": 800.00 }
```
(Computed as `(end - start + 1) × (company.hourly_rate × 8)`.)

**`stats` response**
```json
{ "total_records": 45, "pending": 10, "approved": 5, "paid": 30 }
```

**`status` response**
```json
{ "pending": 10, "paid": 30, "overdue": 3, "cancelled": 2, "total": 45 }
```

**Model fields:** `id`, `user`, `company`, `status` (Pending/Paid/Overdue/Cancelled), `start_date`, `end_date`, `created_at`, `updated_at`. Serializer also exposes `total_days`, `daily_rate`, `total_money` (computed).

---

## 18. Logistics (flights, visas, joining instructions)

Path: `/api/logistics/`

### 18.1 `FlightBookingViewSet` (`/api/logistics/flights/`)

**Permission:** none beyond `IsAuthenticated` (effectively open to all auth users).

**Fields:** `id`, `user`, `contract`, `airline`, `flight_number`, `departure_airport`, `arrival_airport`, `departure_time`, `arrival_time`, `pnr`, `ticket_number`, `cost`, `currency` (default `USD`), `ticket_file`, `status` (Requested/Booked/Cancelled/Completed), `created_at`, `updated_at`

### 18.2 `VisaApplicationViewSet` (`/api/logistics/visas/`)

**Fields:** `id`, `user`, `contract`, `country`, `visa_type` (Schengen/US C1/D/Transit/Arrival/Other), `submission_date`, `appointment_date`, `expiry_date`, `cost`, `status` (Not Started/Documents Collected/Submitted/Appointment Scheduled/Approved/Rejected), `remarks`, `document_file`

### 18.3 `JoiningInstructionViewSet` (`/api/logistics/joining-instructions/`)

**Fields:** `id`, `user`, `contract`, `issue_date`, `port_agent_name`, `port_agent_contact`, `embarkation_port`, `embarkation_date`, `additional_guidelines`, `is_sent_to_crew`

All three support `GET/POST/PUT/PATCH/DELETE` and filter via `FlightBookingFilter` / `VisaApplicationFilter` / `filterset_fields = ['user']`.

---

## 19. Compliance (audits, incidents)

Path: `/api/compliance/`

### 19.1 `AuditViewSet` (`/api/compliance/audits/`)

| Method | Path | Notes |
|---|---|---|
| GET / POST | `/api/compliance/audits/` | uses `AuditFilter` |
| GET / PUT / PATCH / DELETE | `/api/compliance/audits/{id}/` | |

**Fields:** `id`, `audit_type` (MLC/ISO/PSC/Internal/Client), `company`, `ship`, `audit_date`, `auditor_name`, `organization`, `status` (Scheduled/In Progress/Passed/Authorized with Conditions/Failed), `findings_count`, `report_file`, `remarks`, `created_at`

> No `permission_classes` set — effectively open to authenticated users.

### 19.2 `IncidentReportViewSet` (`/api/compliance/incidents/`)

**Fields:** `id`, `title`, `incident_type` (Accident/Near Miss/Grievance/Disciplinary/Pollution/Security), `severity` (Low/Medium/High/Critical), `user`, `ship`, `date_occurred`, `location`, `description`, `immediate_action_taken`, `root_cause_analysis`, `corrective_action`, `preventive_action`, `is_closed`, `closed_date`, `created_at`, plus read-only `user_email`, `ship_name`

---

## 20. AI document processor (LangChain RAG)

Path: `/ai/...` · **Views:** all `AllowAny` (designed to be called from the public CV-upload page).

### 20.1 `POST /ai/upload/`

**View:** `DocumentUploadView` · **Permission:** `AllowAny`

Uploads a CV/PDF/DOCX, runs it through the LangChain → Groq/Gemini pipeline, and saves structured data into **both** `ai_document.Applicant` and `api.Users`.

**Request** — `multipart/form-data`
- Required: `file` (PDF/DOCX)
- Optional: `save_to_db` (default `true`), `groq_api_key`, `api_keys_config` (JSON string)

**Response 201** — full `Applicant` record (id, user, user_name, user_email_display, status, seafarer_application object, etc.). `206 Partial Content` is returned if `User` creation failed but `Applicant` succeeded. `400` is returned for invalid (non-maritime) documents.

**Response shape (sample — `applicant_id: 412`)**:
```json
{
  "id": 412,
  "user": 12,
  "user_name": "John Smith",
  "user_email_display": "john.doe@example.com",
  "status": "Pending",
  "submitted_date": "2026-07-10",
  "notes": "Auto-created from AI Extraction",
  "seafarer_application": { "1_personal_details": { ... }, "2_education": { ... }, "...": "..." },
  "doubted_fields": [],
  "user_documents": {
    "passport":   { "passport_no": "..." },
    "seaman_book":{ "...": "..." },
    "coc":        { "...": "..." },
    "goc":        { "...": "..." },
    "health_certificate": { "...": "..." },
    "licenses":   []
  },
  "_upload_meta": {
    "success": true, "message": "Data saved successfully to both databases",
    "parsing_quality": "high", "page_count": 4, "word_count": 820,
    "user_creation_status": "success", "user_error": null,
    "api_keys_status": { "groq": [{ "key": "...", "status": "live", "reset_time": null }] }
  }
}
```

### 20.2 `POST /ai/save-applicant/`

**View:** `SaveApplicantView` · **Permission:** `AllowAny`

Accepts AI-reviewed structured JSON from the front-end and saves it. Used when a human reviews/edits the AI extraction before committing.

**Request**
```json
{
  "structured_data": { "1_personal_details": { ... }, "2_education": { ... }, "...": "..." },
  "file_name": "manual_upload.pdf"
}
```

**Response 201** (or `206` if `User` creation failed).

### 20.3 `GET /ai/applicants/`

**View:** `ApplicantListView` · **Permission:** `AllowAny`

**Response 200**
```json
{
  "success": true,
  "count": 18,
  "applicants": [
    { "id": 412, "name": "John Smith", "email": "...", "nationality": "...", "created_at": "2026-07-10T..." }
  ]
}
```

### 20.4 `GET /ai/applicants/{applicant_id}/`

**View:** `ApplicantDetailView` · **Permission:** `AllowAny`

Returns the full `ApplicantToUsersSerializer` payload for the applicant (large nested object containing all extracted sections).

### 20.5 `POST /ai/convert/`

**View:** `ConvertApplicantToUserView` · **Permission:** `AllowAny`

**Request** `{ "applicant_id": 412 }`

**Response 200**
```json
{ "success": true, "message": "Applicant converted to user successfully",
  "data": { "applicant_id": 412, "user_id": 12, "user_email": "...", "created_at": "...",
            "applicant_data": { ... } } }
```

### 20.6 `POST /ai/batch-convert/`

**View:** `BatchConvertApplicantsView` · **Permission:** `AllowAny`

**Request**
```json
{ "applicant_ids": [412, 413], "convert_all": false }
```
If `convert_all: true`, ignores `applicant_ids` and converts every applicant.

**Response 200**
```json
{ "success": true, "message": "Batch conversion completed. 12 successful, 1 failed.",
  "data": { "total_applicants": 13, "successful_conversions": 12, "failed_conversions": 1,
            "errors": ["Applicant 7: Email is required"],
            "converted_users": [ { "applicant_id": 412, "user_id": 12, "user_email": "..." } ] } }
```

### 20.7 `GET /ai/sync-status/`

**View:** `SyncStatusView` · **Permission:** `AllowAny`

**Response 200**
```json
{ "success": true, "data": { "total_applicants": 18, "total_users": 234, "applicants_with_email": 17, "users_with_email": 220, "unsynced_applicants": 1, "unsynced_emails": ["foo@bar.com"], "sync_percentage": 94.12 } }
```

### 20.8 `POST /ai/check-quota/`

**View:** `CheckQuotaView` · **Permission:** `AllowAny`

**Request**
```json
{ "api_keys_config": "{\"groq\":[{\"key\":\"gsk_...\",\"status\":\"live\"}]}" }
```

**Response 200**
```json
{ "success": true, "limit": "100000", "remaining": "84123", "provider": "groq" }
```

---

## 21. AI chat agent (search & conversation)

Path: `/ai-agents/...` · All endpoints `AllowAny` except `UserSessionsView`.

### 21.1 `POST /ai-agents/chat/`

**View:** `ChatSearchView` · **Permission:** `AllowAny`

Main AI search/chat endpoint. Maintains conversation context (last 10 messages), supports `general`, `news`, `research`, `fact_check`, `conversational`, and `database` search types. The `database` mode uses `sql_agent.process_database_question` to translate natural-language questions to SQL via the configured LLM.

**Request**
```json
{
  "message":      "Show me all ships under Panama flag",
  "session_id":   "uuid-optional",
  "search_type":  "database",
  "groq_api_key": "gsk_...",
  "api_keys_config": "{\"groq\":[{\"key\":\"gsk_...\",\"status\":\"live\"}]}"
}
```

**Response 200**
```json
{ "session_id": "...", "message": "Show me all ships under Panama flag",
  "response": "...", "search_type": "database", "response_time": 1.42,
  "message_count": 2, "timestamp": "2026-07-10T10:00:00Z",
  "api_keys_status": { ... }, "status": "success" }
```

### 21.2 `GET /ai-agents/chat/history/{session_id}/`

**View:** `ChatHistoryView` · **Permission:** `AllowAny`

**Response 200**
```json
{ "session_id": "...", "title": "Ships under Panama flag", "created_at": "...",
  "total_messages": 4, "messages": [ { "role": "user", "content": "...", "timestamp": "...", "search_type": "database", "response_time": null } ] }
```

### 21.3 `GET /ai-agents/chat/sessions/`

**View:** `UserSessionsView` · **Permission:** `IsAuthenticated`

Returns up to 50 most-recent active chat sessions for the calling user.

**Response 200**
```json
{ "sessions": [ { "session_id": "...", "title": "...", "created_at": "...", "updated_at": "...", "total_messages": 12, "last_activity": "..." } ], "total_count": 5 }
```

### 21.4 `GET /ai-agents/capabilities/`

**View:** `SearchCapabilitiesView` · **Permission:** `AllowAny`

Static description of available chat features, search types, and tools.

---

## 22. Contract generation (DOCX)

Path: `/api/contracts-gen/...` · **View:** `GenerateContractView` (function-based) · **Permission:** implicit (no `permission_classes` defined; effectively open).

### 22.1 `POST /api/contracts-gen/generate/{user_id}/`

Fills the `A NEW APPLICATION - Copy (5).docx` template with the user's data and returns the generated file URL.

**Request body** — none (data is pulled from `Users`).

**Response 200**
```json
{ "message": "Contract generated successfully",
  "file_url": "/media/contracts/generated/Contract_12_ab12cd34.docx",
  "file_path": "/var/www/media/contracts/generated/Contract_12_ab12cd34.docx" }
```

### 22.2 `GET /api/contracts-gen/list/`

**View:** `ListGeneratedContractsView` · **Permission:** implicit (open)

**Response 200**
```json
[ { "filename": "Contract_12_ab12cd34.docx", "created_at": "2026-07-10 10:00:00", "url": "/media/contracts/generated/Contract_12_ab12cd34.docx" } ]
```

---

## 23. Global search

### 23.1 `GET /api/global-search/?q=<query>`

**View:** `GlobalSearchView` · **Permission:** `IsAuthenticated`

Minimum query length: 2 characters. Searches across Users, Ships, Companies, CV Submissions, and Contracts (top 10 each).

**Response 200**
```json
{
  "users":     [ { "id": 1, "name": "John Smith", "email": "...", "phone": "...", "role": "Employee" } ],
  "ships":     [ { "id": 5, "ship_name": "MSC Oscar", "imo_number": "...", "...": "..." } ],
  "companies": [ { "id": 3, "company_name": "...", "...": "..." } ],
  "cvs":       [ { "id": 99, "...": "..." } ],
  "contracts": [ { "id": 17, "...": "..." } ]
}
```

---

## 24. Choice / dropdown endpoints

These all require authentication and return `[{ "value": ..., "label": ... }]` style lists for populating front-end dropdowns.

| Method | Path | Returns |
|---|---|---|
| GET | `/api/positions/` | List of all `Rank` records as `[{value: id, label: name, code: code}]`; falls back to hardcoded `Document.POSITION_CHOICES` if `Rank` table empty |
| GET | `/api/flags/` | All `Flag` records; falls back to ~190 hardcoded country list |
| GET | `/api/vessel-types/` | All `VesselType` records |
| GET | `/api/company-types/` | All `CompanyType` records |
| GET | `/api/coc-choices/` | `Users.COC_CERTIFICATE_CHOICES` (Master / Chief Mate / Chief Officer / …) |
| GET | `/api/document-types/` | `PersonalDocument.DOCUMENT_TYPE_CHOICES` (~30 travel doc types — Passport, Schengen Visa, US C1/D, etc.) |
| GET | `/api/ranks/all/` | Flat list `[{id, code, name}]` for position dropdowns |

---

## 25. Media serving

All uploaded files are served from `/media/...` via Django's `static` helper in `saker/urls.py`:

```python
urlpatterns += [ re_path(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT }) ]
```

So a file uploaded to `passports/12345_passport.pdf` is reachable at `https://<host>/media/passports/12345_passport.pdf`.

---

## 26. URL inventory (cheat sheet)

| Mount | URL prefix |
|---|---|
| Admin | `/admin/` |
| Auth | `/api/login/`, `/api/login/refresh/`, `/api/register/`, `/api/logout/`, `/api/auth/google/`, `/api/verify-email/<uid>/<token>/` |
| Users | `/api/users/`, `/api/users/{id}/`, `/api/users/me/`, `/api/users/stats/`, `/api/users/bulk-delete/`, `/api/users/bulk-edit/`, `/api/users/{id}/full-profile/`, `/api/users/{id}/download-*/` |
| Profile sub-resources | `/api/my-languages/`, `/api/user-languages/`, `/api/personal-documents/`, `/api/next-of-kin/`, `/api/declarations/`, `/api/users/declarations/`, `/api/users/certificates/`, `/api/certificates/`, `/api/ranks/`, `/api/references/`, `/api/sea-services/` |
| Quick Applier | `/api/documents/`, `/api/documents/{id}/set_status/`, `/api/documents/{id}/download/`, `/api/documents/stats/` |
| CV Submissions | `/api/cv-submissions/`, `/api/cv-submissions/{id}/upload/`, `/api/cv-submissions/{id}/update-status/`, `/api/cv-submissions/{id}/download-cv/`, `/api/cv-submissions/{id}/download-document/`, `/api/cv-submissions/stats/` |
| Seafarer App | `/api/seafarer-application/`, `/api/seafarer-application/{id}/` |
| Contracts | `/api/contracts/`, `/api/contracts/stats/`, `/api/contracts/status/`, `/api/contracts-gen/generate/{user_id}/`, `/api/contracts-gen/list/` |
| Interviews | `/api/interviews/`, `/api/interviews/{id}/`, `/api/interviews/stats/`, `/api/interviews/calendar/`, `/api/interviews/status/` |
| Companies | `/api/companies/`, `/api/companies/stats/`, `/api/companies/job-orders/`, `/api/companies/job-positions/`, `/api/companies/job-positions/apply/` |
| Ships | `/api/ships/`, `/api/ships/{id}/assign-user/`, `/api/ships/{id}/unassign-user/` |
| Tickets & papers | `/api/tickets-papers/tickets/`, `/api/tickets-papers/traveling-papers/` |
| Licenses | `/api/my-licenses/`, `/api/my-licenses/{id}/download/` |
| Vaccinations | `/api/vaccinations/` |
| Courses | `/api/courses/`, `/api/courses/{course_id}/download/` |
| Finance | `/api/finance-records/`, `/api/finance-records/stats/`, `/api/finance-records/export/`, `/api/finance/finance-records/`, `/api/finance/finance-records/calculate/`, `/api/finance/finance-records/status/` |
| Logistics | `/api/logistics/flights/`, `/api/logistics/visas/`, `/api/logistics/joining-instructions/` |
| Compliance | `/api/compliance/audits/`, `/api/compliance/incidents/` |
| Core | `/api/core/flags/`, `/api/core/vessel-types/`, `/api/core/company-types/`, `/api/flags/`, `/api/vessel-types/`, `/api/company-types/` |
| Choices | `/api/positions/`, `/api/coc-choices/`, `/api/document-types/`, `/api/ranks/all/` |
| AI document | `/ai/upload/`, `/ai/save-applicant/`, `/ai/applicants/`, `/ai/applicants/{id}/`, `/ai/convert/`, `/ai/batch-convert/`, `/ai/sync-status/`, `/ai/check-quota/` |
| AI chat | `/ai-agents/chat/`, `/ai-agents/chat/history/{session_id}/`, `/ai-agents/chat/sessions/`, `/ai-agents/capabilities/` |
| Search | `/api/global-search/` |
| Media | `/media/...` (served by Django in dev) |

---

## 27. Cross-cutting notes / gotchas

- **Two `Users` serializers exist**: `UserSerializer` (`api/serializers.py`, used internally) and `UsersSerializer` (`api/serializer.py`, the big one used by `UserViewSet`). The `UsersSerializer` payload is the one described in §4.1.
- **Two `Company` models**: `api.models.Company` (legacy, no migration) and `companies.models.Company` (the active one). Make sure to use the `companies` app's table for new code.
- **Two `Interview` models**: `api.models.Interview` (primary) and `interviews.models.Interview` (legacy duplicate). Always use the `api` one.
- **Document upload (`/api/documents/`)** auto-creates a `Users` record with `role=Employee` and an unusable password if the email is not already registered. This is the "Quick Applier" funnel.
- **Document approval flow**: `Document.status = Active` triggers `User.generated_id` generation, syncs name/email/phone/position, creates/updates a `CVSubmission(status='Approved')`, creates a `UserRank`, and sends a verification email.
- **Contract auto-expiry**: A daily cached job bulk-flips expired `Active/Signed/Pending Signature/Pending` contracts to `Draft` based on `sign_off_date < today`.
- **`assign_rank_by_position`** auto-generates `assigned_code` like `MST.001`, `EO-1.001`, etc., using a hardcoded `POSITION_CODE_MAP` in `api/views.py`. The 6-character prefix is `rank.code` (split on `.`), and the trailing number increments per prefix.
- **Seafarer application serializer** (`SeafarerApplicationSerializer`) is the master aggregated profile — used by the front-end's "applicant details" screen. It contains the entire `Users` record + every related sub-resource in one payload.
- **AI document processing** requires either a `GROQ_API_KEY` env var or a `groq_api_key`/`api_keys_config` form field on the upload. The quota check (`/ai/check-quota/`) reads the headers from a 1-token test request to Groq.
- **All `AllowAny` download endpoints** are documented in the relevant sections. They exist because the front-end uses plain `<a href>` links that don't carry auth headers. Treat these as public — do not put non-public data behind them.
- **Rate limiting**: not configured at the view level. The contract-expiry job is the only rate-limited piece (1× per day via `cache.set`).
- **CORS**: open (`*`) in dev. In production, set `CORS_ALLOWED_ORIGINS` in `saker/settings.py`.

---

*Last regenerated from source on the current branch (`server-updates`).* If a route is missing, it likely lives behind a feature flag or in commented code; ping the backend owner before adding it to the front-end.
