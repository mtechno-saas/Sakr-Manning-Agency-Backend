# Backend API Documentation — Sakr Manning Agency

**Generated:** 2026-07-18
**Base URL:** `https://backend.sakrshipping.com`
**Auth:** JWT Bearer token (except where noted)
**Framework:** Django 5.2 + Django REST Framework 3.16.1 + SimpleJWT 5.5.1

This document covers every endpoint that is **new** or **updated** in the current build. Endpoints that exist but have not changed are listed in the index but not re-documented in full.

---

## Table of Contents

1. [Quick Reference — All Endpoints](#quick-reference)
2. [Authentication](#authentication)
3. [Companies App](#companies-app)
   - [GET    /api/companies/](#get-apicompanies)
   - [POST   /api/companies/](#post-apicompanies)
   - [GET    /api/companies/{id}/](#get-apicompaniesid)
   - [PUT    /api/companies/{id}/](#put-apicompaniesid)
   - [PATCH  /api/companies/{id}/](#patch-apicompaniesid)
   - [DELETE /api/companies/{id}/](#delete-apicompaniesid)
   - [GET    /api/companies/stats/](#get-apicompaniesstats)
   - [GET    /api/companies/job-orders/...](#job-orders)
   - [CRUD   /api/companies/job-positions/...](#job-positions)
4. [Interviews App](#interviews-app)
   - [GET    /api/interviews/](#get-apiinterviews)
   - [POST   /api/interviews/](#post-apiinterviews)
   - [GET    /api/interviews/{id}/](#get-apiinterviewsid)
   - [PUT    /api/interviews/{id}/](#put-apiinterviewsid)
   - [PATCH  /api/interviews/{id}/](#patch-apiinterviewsid)
   - [DELETE /api/interviews/{id}/](#delete-apiinterviewsid)
   - [GET    /api/interviews/status/](#get-apiinterviewsstatus)
   - [CRUD   /api/reminders/](#interview-reminders)  *(now in its own `reminders` app)*
5. [Common Error Responses](#errors)
6. [Migrations Index](#migrations)

---

## Quick Reference <a id="quick-reference"></a>

| Section | Method | Path | Auth | Notes |
|---|---|---|---|---|
| Companies | GET | `/api/companies/` | Bearer | List + filter |
| Companies | POST | `/api/companies/` | Bearer | Create |
| Companies | GET | `/api/companies/{id}/` | Bearer | Retrieve |
| Companies | PUT | `/api/companies/{id}/` | Bearer | Full update |
| Companies | PATCH | `/api/companies/{id}/` | Bearer | Partial update |
| Companies | DELETE | `/api/companies/{id}/` | Bearer | CASCADE → JobOrders |
| Companies | GET | `/api/companies/stats/` | Bearer | Aggregated stats |
| Companies | GET/POST/PUT/PATCH/DELETE | `/api/companies/job-orders/{id}/` | Public GET / Auth write | Job orders |
| Companies | GET/POST/PUT/PATCH/DELETE | `/api/companies/job-positions/{id}/` | Public GET / Auth write | Job positions |
| Companies | POST | `/api/companies/job-positions/apply/` | Bearer | Employee quick-apply |
| Interviews | GET | `/api/interviews/` | Bearer | List |
| Interviews | POST | `/api/interviews/` | Bearer | Create |
| Interviews | GET | `/api/interviews/{id}/` | Bearer | Retrieve |
| Interviews | PUT | `/api/interviews/{id}/` | Bearer | Full update |
| Interviews | PATCH | `/api/interviews/{id}/` | Bearer | Partial update |
| Interviews | DELETE | `/api/interviews/{id}/` | Bearer | Delete |
| Interviews | GET | `/api/interviews/status/` | Bearer | Counts by status |
| **Interviews** | **GET/POST/PUT/PATCH/DELETE** | **`/api/reminders/{id}/`** | **Bearer** | **🆕 New endpoint** |
| **Interviews** | **GET** | **`/api/reminders/upcoming/`** | **Bearer** | **🆕 New endpoint** |

🆕 = added in this build · ✏️ = updated in this build (new fields, behavior, or format)

---

## Authentication <a id="authentication"></a>

All endpoints require a JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Get a token from `POST /api/login/` with `{ "username": "...", "password": "..." }`. Refresh with `POST /api/login/refresh/`.

The token contains the user's `role` claim. Backend permission checks use the following role values:

- `Admin`
- `HR Manager`
- `Recruiter`
- `Employee`

---

## Companies App <a id="companies-app"></a>

**Model:** `companies.Company`
**Serializer:** `companies.serializers.CompanySerializer`
**ViewSet:** `companies.views.CompanyViewSet`
**Filter:** `companies.filters.CompanyFilter`
**Default permission:** `IsAuthenticated`

### ✏️ `GET /api/companies/` <a id="get-apicompanies"></a>

List companies with optional filters.

**Section:** Companies / List

**Permissions:** `IsAuthenticated` (any role)

**Query parameters:**

| Param | Type | Effect |
|---|---|---|
| `name` | string | Substring match on `company_name` (case-insensitive) |
| `company_type` | string | Exact match (case-insensitive) |
| `status` | string | Exact match. One of `Active` / `Inactive` / `Prospect` |

**Request body:** none

**Response 200:**
```json
[
  {
    "id": 2,
    "company_name": "Maersk Line Egypt",
    "company_type": "Owner",
    "company_type_name": "Owner",
    "company_flag": "Egypt",
    "company_flag_id": 3,
    "company_flag_name": "Egypt",
    "open_positions": 12,
    "status": "Active",
    "contact_email": "ops@maersk.com",
    "contact_phone": "+201234567890",
    "owner": "Capt. Hassan",
    "website": "https://maersk.com",
    "hourly_rate": "45.00",
    "contact_person": "Capt. Hassan Mohamed",
    "alt_phone": "+20 100 123 4567",
    "address": "12 El Horreya St, Alexandria, Egypt",
    "notes": "Preferred vendor. WhatsApp only.",
    "created_at": "2024-03-15T10:00:00Z",
    "updated_at": "2025-07-01T14:22:00Z",
    "ships": [ /* see /api/companies/{id}/ for shape */ ],
    "open_position_names": [
      { "id": 4, "name": "Chief Officer", "count": 2 }
    ]
  }
]
```

**Errors:** `401`

---

### ✏️ `POST /api/companies/` <a id="post-apicompanies"></a>

Create a new company.

**Section:** Companies / Create

**Permissions:** `IsAuthenticated`. ⚠️ **No role check** — any authenticated user can create. See "Known Issues" section in `missing-fields-audit.md`.

**Required fields:** `company_name`, `contact_email`
**Optional:** all other fields

**Request body:**
```json
{
  "company_name": "New Shipping Co",
  "contact_email": "info@newship.com",
  "company_type": "Owner",
  "company_flag": "Egypt",
  "status": "Active",
  "website": "newship.com",
  "hourly_rate": "30.00",
  "contact_person": "Capt. John",
  "alt_phone": "+20 100 000 0000",
  "address": "Port Said, Egypt",
  "notes": "Verified by IT 2026-07"
}
```

**Behaviour notes:**
- `company_flag` accepts int id (`3`), string id (`"3"`), or name (`"Egypt"`). If name is unknown, the Flag is **auto-created** and linked.
- `company_type` accepts id or name. **Does not** auto-create.
- `website` auto-prefixes `https://` if no scheme is present.

**Response 201:** full company object (see GET shape above)

**Errors:**
- `400` — validation error (e.g. duplicate `company_name`, missing `contact_email`)
- `401` — no/bad token

---

### ✏️ `GET /api/companies/{id}/` <a id="get-apicompaniesid"></a>

Retrieve one company with all related data.

**Section:** Companies / Detail

**Permissions:** `IsAuthenticated`

**Response 200:**
```json
{
  "id": 2,
  "company_name": "Maersk Line Egypt",
  "company_type": "Owner",
  "company_type_name": "Owner",
  "company_flag": "Egypt",
  "company_flag_id": 3,
  "company_flag_name": "Egypt",
  "open_positions": 12,
  "status": "Active",
  "contact_email": "ops@maersk.com",
  "contact_phone": "+201234567890",
  "owner": "Capt. Hassan",
  "website": "https://maersk.com",
  "hourly_rate": "45.00",
  "contact_person": "Capt. Hassan Mohamed",
  "alt_phone": "+20 100 123 4567",
  "address": "12 El Horreya St, Alexandria, Egypt",
  "notes": "Preferred vendor. WhatsApp only.",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2025-07-01T14:22:00Z",
  "ships": [
    {
      "id": 12,
      "ship_name": "Maersk Horizon",
      "imo_number": "9876543",
      "ship_type": "Container",
      "flag": "Panama",
      "status": "Active",
      "official_no": "EG-1234",
      "call_sign": "HZN",
      "year_built": 2018
    }
  ],
  "open_position_names": [
    { "id": 4, "name": "Chief Officer", "count": 2 },
    { "id": 7, "name": "Bosun",         "count": 1 }
  ]
}
```

**Errors:** `401`, `404`

**Field notes:**
- `open_positions` is a **computed** value: `SUM(max(0, quantity - filled_contracts))` across all open JobOrderPositions under this company. Not the model field of the same name.
- `ships` is computed from the reverse `Company.ships` relation.
- `company_flag` and `company_type` are string-typed (as of this build). Old `company_flag` int id is still accepted on input.
- `contact_person`, `alt_phone`, `address`, `notes` are the 4 fields added in migration `0013`.

---

### ✏️ `PUT /api/companies/{id}/` <a id="put-apicompaniesid"></a>

Full replace. **All required fields must be present** or DRF returns 400.

**Section:** Companies / Update

**Permissions:** `IsAuthenticated`. ⚠️ **No role check.**

**Required fields:** `company_name`, `contact_email`

**Request body:** same shape as POST, with all required fields.

**Response 200:** full company object
**Errors:** `400` (missing/invalid required field), `401`, `404`

> 💡 **Tip:** use `PATCH` for edit forms — it accepts partial payloads and only sends the changed fields.

---

### ✏️ `PATCH /api/companies/{id}/` <a id="patch-apicompaniesid"></a>

Partial update. Any subset of fields.

**Section:** Companies / Update

**Permissions:** `IsAuthenticated`. ⚠️ **No role check.**

**Request body:** any subset, e.g. just the new fields:
```json
{
  "contact_person": "Capt. Hassan Mohamed",
  "alt_phone": "+20 100 123 4567",
  "address": "12 El Horreya St, Alexandria, Egypt",
  "notes": "Preferred vendor. WhatsApp only."
}
```

**Response 200:** full company object (with updated fields)
**Errors:** `400`, `401`, `404`

---

### ✏️ `DELETE /api/companies/{id}/` <a id="delete-apicompaniesid"></a>

Delete a company.

**Section:** Companies / Delete

**Permissions:** `IsAuthenticated`. ⚠️ **No role check.** ⚠️ **Cascades to all related `JobOrder` records** (FK has `on_delete=CASCADE`).

**Response 204:** No content
**Errors:** `401`, `404`

> ⚠️ Recommend a hard-confirm dialog in the frontend before calling this.

---

### `GET /api/companies/stats/` <a id="get-apicompaniesstats"></a>

Aggregated statistics for the dashboard.

**Section:** Companies / Stats

**Permissions:** `IsAuthenticated`

**Response 200:**
```json
{
  "total_companies": 27,
  "by_status": { "Active": 22, "Inactive": 3, "Prospect": 2 },
  "by_type":   { "Owner": 12, "Manager": 9, "Charterer": 6 },
  "open_positions": {
    "total": 41,
    "companies_with_openings": 9
  },
  "recent_companies": [
    { "id": 31, "company_name": "Globex", "company_type": "Owner", "status": "Prospect", "created_at": "2026-07-15T10:00:00Z" }
  ]
}
```

---

### Job Orders <a id="job-orders"></a>

Nested at `/api/companies/job-orders/{id}/` and `/api/companies/job-positions/{id}/` (via `JobOrderViewSet`).

**Permissions:** Custom `PublicJobOrderPermission`:
- `GET`, `HEAD`, `OPTIONS` — anyone (including unauthenticated)
- `POST`, `PUT`, `PATCH`, `DELETE` — authenticated user **without** `role == "Employee"` (Admin / HR Manager / Recruiter only)

These endpoints are unchanged in this build — see `companies/views.py` and `companies/serializers.py` for the `JobOrderSerializer` and `JobOrderPositionSerializer` source.

---

### ✏️ Job Positions <a id="job-positions"></a>

Nested at `/api/companies/job-positions/{id}/`.

**Permissions:** Same as Job Orders — `PublicJobOrderPermission`. Employee role **cannot** write.

**Model:** `JobOrderPosition` (with `created_at` and `updated_at` added in this build — migration `0014`)

**Available methods:**

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/companies/job-positions/` | List + filter |
| POST | `/api/companies/job-positions/` | Create (single OR bulk array) |
| GET | `/api/companies/job-positions/{id}/` | Retrieve |
| PUT | `/api/companies/job-positions/{id}/` | Full update |
| PATCH | `/api/companies/job-positions/{id}/` | Partial update |
| DELETE | `/api/companies/job-positions/{id}/` | Delete |
| POST | `/api/companies/job-positions/apply/` | Employee quick-apply |

**Fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | int | auto | Primary key |
| `job_order` | FK | ✅ yes | Parent job order |
| `rank` | FK / string | ✅ yes | Accepts id (e.g. `4`) or name (e.g. `"Chief Officer"`) |
| `quantity` | PositiveIntegerField | ⬜ optional | Default `1` |
| `salary_min` | Decimal | ⬜ optional | |
| `salary_max` | Decimal | ⬜ optional | |
| `currency` | CharField | ⬜ optional | Default `"USD"` |
| `contract_duration_months` | PositiveIntegerField | ⬜ optional | Default `6` |
| `remarks` | TextField | ⬜ optional | |
| `created_at` | DateTime | read-only | ✏️ **Added in this build** |
| `updated_at` | DateTime | read-only | ✏️ **Added in this build** |
| `rank_name` | string | read-only | Computed |
| `status` | string | read-only | Inherited from `job_order.status` |
| `company_name` | string | read-only | Computed |
| `ship_name` | string | read-only | Computed |
| `filled_slots` | int | read-only | Computed |
| `remaining_slots` | int | read-only | Computed |
| `assigned_to` | array | read-only | Computed |

**Sample PATCH:**
```http
PATCH /api/companies/job-positions/42/
Authorization: Bearer <token>
Content-Type: application/json

{
  "quantity": 5,
  "salary_max": "5000.00"
}
```

**Sample Response 200:**
```json
{
  "id": 42,
  "job_order": 7,
  "rank": 4,
  "rank_name": "Chief Officer",
  "quantity": 5,
  "salary_min": "3000.00",
  "salary_max": "5000.00",
  "currency": "USD",
  "contract_duration_months": 6,
  "remarks": "Urgent hire",
  "status": "Open",
  "company_name": "Maersk Line Egypt",
  "ship_name": "Maersk Horizon",
  "filled_slots": 0,
  "remaining_slots": 5,
  "assigned_to": [],
  "created_at": "2026-07-14T10:16:00Z",
  "updated_at": "2026-07-18T11:30:00Z"
}
```

**Sample bulk create:**
```http
POST /api/companies/job-positions/
Content-Type: application/json

[
  { "job_order": 1, "rank": "Chief Officer", "quantity": 1, "salary_min": "3000", "salary_max": "4500", "currency": "USD" },
  { "job_order": 1, "rank": "Bosun",         "quantity": 2, "salary_min": "1800", "salary_max": "2200", "currency": "USD" }
]
```

Returns `201 Created` with the array.

**Quick apply** (any authenticated user):
```http
POST /api/companies/job-positions/apply/
Content-Type: application/json

{
  "position_ids": [1, 2, 3]
}
```
or
```json
{
  "position_names": ["Chief Officer", "Bosun"]
}
```
or
```json
{
  "position_ids": [1],
  "position_names": ["Bosun"]
}
```

**Response 201:**
```json
{
  "applied": [
    { "document_id": 88, "position_id": 1, "rank_name": "Chief Officer", "company_name": "Maersk Line Egypt", "status": "Pending" }
  ],
  "skipped": [],
  "total_applied": 1,
  "total_skipped": 0
}
```

---

## Interviews App <a id="interviews-app"></a>

**Model:** `api.models.Interview` (re-exported) / `interviews.models.Interview`
**Serializer:** `interviews.serializers.InterviewSerializer`
**ViewSet:** `interviews.views.InterviewViewSet`
**Default permission:** `IsAuthenticated`

### ✏️ `GET /api/interviews/` <a id="get-apiinterviews"></a>

List interviews.

**Section:** Interviews / List

**Permissions:** `IsAuthenticated`

**Response 200:**
```json
[
  {
    "id": 23,
    "candidate": 42,
    "candidate_details": { "id": 42, "first_name": "Hassan", "last_name": "Mohamed", "email": "hassan@example.com" },
    "candidate_email": "hassan@example.com",
    "interviewer": 7,
    "interviewer_details": { "id": 7, "first_name": "Sara", "last_name": "Ali", "email": "sara@example.com" },
    "interviewer_email": "sara@example.com",
    "principal": 12,
    "position": "Chief Officer",
    "type": "Video",
    "duration_minutes": 30,
    "location": "Zoom",
    "date": "2026-07-20T14:30:00Z",
    "status": "Scheduled",
    "result": "Pending",
    "feedback": "",
    "notes": "First round screening",
    "link": "https://zoom.us/j/123",
    "created_at": "2026-07-14T11:00:00Z",
    "updated_at": "2026-07-18T11:00:00Z"
  }
]
```

---

### ✏️ `POST /api/interviews/` <a id="post-apiinterviews"></a>

Create a new interview.

**Section:** Interviews / Create

**Permissions:** `IsAuthenticated`

**Required fields:** `candidate`, `interviewer`, `date`
**Default for `status`:** `"Pending Confirmation"` if omitted

**Request body:**
```json
{
  "candidate": 42,
  "interviewer": 7,
  "principal": 12,
  "position": "Chief Officer",
  "type": "Video",
  "duration_minutes": 30,
  "location": "Zoom",
  "date": "2026-07-20T14:30:00Z",
  "status": "Scheduled",
  "result": "Pending",
  "feedback": "",
  "link": "https://zoom.us/j/123",
  "notes": "First round screening"
}
```

**Response 201:** full interview object
**Errors:** `400`, `401`

---

### ✏️ `GET /api/interviews/{id}/` <a id="get-apiinterviewsid"></a>

Retrieve one interview.

**Section:** Interviews / Detail

**Permissions:** `IsAuthenticated`

**Response 200:** full interview object (see list shape)
**Errors:** `401`, `404`

---

### ✏️ `PUT /api/interviews/{id}/` <a id="put-apiinterviewsid"></a>

Full replace. Required fields must be present.

**Section:** Interviews / Update

**Permissions:** `IsAuthenticated`

**Required fields:** `candidate`, `interviewer`, `date`

**Request body:** same as POST with all required fields
**Response 200:** full interview object
**Errors:** `400`, `401`, `404`

---

### ✏️ `PATCH /api/interviews/{id}/` <a id="patch-apiinterviewsid"></a>

Partial update.

**Section:** Interviews / Update

**Permissions:** `IsAuthenticated`

**Request body:** any subset
```json
{ "result": "Pass", "feedback": "Strong communicator. Recommend hire." }
```

**Response 200:** full interview object
**Errors:** `400`, `401`, `404`

---

### ✏️ `DELETE /api/interviews/{id}/` <a id="delete-apiinterviewsid"></a>

Delete an interview.

**Section:** Interviews / Delete

**Permissions:** `IsAuthenticated`

**Response 204:** No content
**Errors:** `401`, `404`

---

### `GET /api/interviews/status/` <a id="get-apiinterviewsstatus"></a>

Counts by status. Role-aware — admins see all, others see only their own.

**Section:** Interviews / Stats

**Permissions:** `IsAuthenticated`. For non-Admin/HR/Recruiter users, scoped to `candidate=request.user`.

**Response 200:**
```json
{
  "scheduled": 12,
  "completed": 28,
  "cancelled": 3,
  "rescheduled": 1,
  "no_show": 2,
  "total": 46
}
```

---

### Reminders <a id="interview-reminders"></a> *(own `reminders` app since 2026-07-25)*

**New endpoint in this build.** Resource: `Reminder` model added in migration `0002_reminder.py`.

**Serializer:** `interviews.serializers.ReminderSerializer`
**ViewSet:** `interviews.views.ReminderViewSet`
**Default permission:** `IsAuthenticated`
**Role-based scoping:** Admin / HR Manager / Recruiter see all reminders. Other authenticated users see only their own (`user == request.user`).

> **Note (2026-07-25):** This endpoint was moved from `/api/interviews/reminders/` to `/api/reminders/`. The full app reference is in `docs/reminders-app.md`.

#### 🆕 `GET /api/reminders/`

**Section:** Reminders / List

**Permissions:** `IsAuthenticated`. Returns only the user's own reminders unless they're Admin/HR/Recruiter (in which case all).

**Response 200:**
```json
[
  {
    "id": 7,
    "user": 42,
    "user_name": "Capt. Hassan Mohamed",
    "user_email": "hassan@example.com",
    "text": "Call Capt. Hassan about medicals",
    "reminder_date": "2026-07-20",
    "reminder_time": "14:30:00",
    "is_completed": false,
    "created_at": "2026-07-14T11:00:00Z",
    "updated_at": "2026-07-14T11:00:00Z"
  }
]
```

---

#### 🆕 `POST /api/reminders/`

**Section:** Reminders / Create

**Permissions:** `IsAuthenticated`

**Required fields:** `user`, `text`, `reminder_date`, `reminder_time`

**Request body:**
```json
{
  "user": 42,
  "text": "Call Capt. Hassan about medicals",
  "reminder_date": "2026-07-20",
  "reminder_time": "14:30:00"
}
```

**Response 201:** full reminder object
**Errors:** `400` (validation), `401`

---

#### 🆕 `GET /api/reminders/{id}/`

**Section:** Reminders / Detail

**Permissions:** `IsAuthenticated`. Non-admin/HR/Recruiter users can only retrieve their own reminders.

**Response 200:** full reminder object
**Errors:** `401`, `404` (or `403` if not the owner and not privileged)

---

#### 🆕 `PUT /api/reminders/{id}/`

**Section:** Reminders / Update

**Permissions:** `IsAuthenticated`. Required fields must be present.

**Response 200:** full reminder object
**Errors:** `400`, `401`, `403`, `404`

---

#### 🆕 `PATCH /api/reminders/{id}/`

**Section:** Reminders / Update

**Permissions:** `IsAuthenticated`

**Request body:** any subset
```json
{ "is_completed": true }
```

**Response 200:** full reminder object
**Errors:** `400`, `401`, `403`, `404`

---

#### 🆕 `DELETE /api/reminders/{id}/`

**Section:** Reminders / Delete

**Permissions:** `IsAuthenticated`. Non-admin users can only delete their own.

**Response 204:** No content
**Errors:** `401`, `403`, `404`

---

#### 🆕 `GET /api/reminders/upcoming/`

**Section:** Reminders / Upcoming

**Permissions:** `IsAuthenticated`. Returns only the user's own upcoming reminders unless they're Admin/HR/Recruiter.

**Behavior:** Returns reminders where `reminder_date >= today` AND `is_completed = false`, ordered by `reminder_date`, `reminder_time`.

**Response 200:** array of reminder objects (same shape as list response)

---

## Common Error Responses <a id="errors"></a>

| Code | When | Body shape |
|---|---|---|
| `400` | Validation error | `{ "field_name": ["error message"] }` |
| `401` | No / bad / expired token | `{ "detail": "Authentication credentials were not provided." }` |
| `403` | Authenticated but forbidden by permission | `{ "detail": "You do not have permission to perform this action." }` |
| `404` | Resource not found | `{ "detail": "Not found." }` |
| `405` | Wrong HTTP method | `{ "detail": "Method \"...\" not allowed." }` |
| `500` | Server error | `{ "error": "...", "traceback": "..." }` (debug only) |

**Validation error example:**
```json
{
  "company_name": ["company with this company name already exists."],
  "contact_email": ["Enter a valid email address."]
}
```

---

## Migrations Index <a id="migrations"></a>

The following migrations were added or referenced in this build. Run all of them on the production server with:

```bash
python manage.py migrate companies
python manage.py migrate interviews
```

| App | Migration | Effect |
|---|---|---|
| `companies` | `0013_company_address_contact_person_alt_phone_notes.py` | Adds 4 fields to `Company` |
| `companies` | `0014_joborderposition_created_at_and_more.py` | Adds `created_at` / `updated_at` to `JobOrderPosition` |
| `interviews` | `0002_reminder.py` | Creates `Reminder` table |
| `interviews` | `0003_interview_more_fields.py` | Adds 7 fields + FK to Company on `Interview` |

---

## Field Type Reference

| Type | DRF serializer | Example JSON |
|---|---|---|
| `string` (short) | `CharField` | `"Maersk"` |
| `string` (long) | `TextField` | `"Long description..."` |
| `string` (slug) | `SlugRelatedField` | `"Owner"` |
| `integer` | `IntegerField` | `42` |
| `integer` (positive) | `PositiveIntegerField` | `5` |
| `decimal` | `DecimalField` | `"45.00"` |
| `date` | `DateField` | `"2026-07-20"` |
| `time` | `TimeField` | `"14:30:00"` |
| `datetime` | `DateTimeField` | `"2026-07-20T14:30:00Z"` |
| `boolean` | `BooleanField` | `true` |
| `FK` (write as id) | `PrimaryKeyRelatedField` (default) | `7` |
| `FK` (write as name) | `SlugRelatedField` | `"Chief Officer"` |
| `email` | `EmailField` | `"ops@maersk.com"` |
| `URL` | `URLField` | `"https://maersk.com"` |

**Date format convention:**
- Date only: `YYYY-MM-DD`
- Time only: `HH:MM:SS` (or `HH:MM`)
- DateTime: ISO 8601 with timezone, e.g. `2026-07-20T14:30:00Z`

---

## Permission Matrix

| Endpoint | Anonymous | Employee | HR / Recruiter | Admin |
|---|---|---|---|---|
| `GET /api/companies/...` | ❌ 401 | ✅ | ✅ | ✅ |
| `POST /api/companies/...` | ❌ 401 | ⚠️ Allowed (no role check) | ✅ | ✅ |
| `GET /api/companies/job-orders/...` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/companies/job-orders/...` | ❌ 401 | ❌ 403 | ✅ | ✅ |
| `GET /api/companies/job-positions/...` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/companies/job-positions/...` | ❌ 401 | ❌ 403 | ✅ | ✅ |
| `GET /api/interviews/...` | ❌ 401 | ✅ | ✅ | ✅ |
| `POST /api/interviews/...` | ❌ 401 | ✅ | ✅ | ✅ |
| `GET /api/reminders/...` | ❌ 401 | ✅ (own only) | ✅ (all) | ✅ (all) |
| `POST /api/reminders/...` | ❌ 401 | ✅ | ✅ | ✅ |

> ⚠️ Note: Companies POST/PUT/PATCH/DELETE currently allows any authenticated user. Recommended to add a role check (e.g. `IsAdminOrHR`).

---

## Changelog

- **2026-07-18** — Documented in this build
  - ✏️ `Company` — added 4 fields (address, contact_person, alt_phone, notes)
  - ✏️ `Company.company_flag` — now serialized as string name (was int FK id)
  - ✏️ `JobOrderPosition` — added `created_at`, `updated_at`
  - ✏️ `Interview` — added 7 fields (principal, position, type, duration_minutes, location, result, feedback) + 2 computed (candidate_email, interviewer_email)
  - 🆕 `Reminder` model + `/api/reminders/*` endpoints
  - 🆕 `/api/reminders/upcoming/` custom action
