# Missing Fields Audit — Sakr Companies API

**Generated:** 2026-07-14
**Scope:** Fields requested by the frontend that were not present in the backend response, and the migrations created to add them.

---

## Endpoint: `GET / PATCH /api/companies/{id}/`

### Fields Added

| # | Field Name | API Key | Type | Required | Max Length | UI Label | Example |
|---|---|---|---|---|---|---|---|
| 1 | Postal address | `address` | `string` (long) | No | unlimited | Address | `"12 El Horreya St, Alexandria, Egypt"` |
| 2 | Primary contact name | `contact_person` | `string` | No | 200 | Contact Person | `"Capt. Hassan Mohamed"` |
| 3 | Alternative phone | `alt_phone` | `string` | No | 50 | Alt Phone | `"+20 100 123 4567"` |
| 4 | Internal notes | `notes` | `string` (long) | No | unlimited | Notes | `"Preferred vendor. WhatsApp only."` |

**Migration:** `companies/migrations/0013_company_address_contact_person_alt_phone_notes.py`
**Model file:** `companies/models.py` (Company class, after `owner`)
**Serializer:** `companies/serializers.py` (no change — auto-included via `fields = '__all__'`)

### Frontend Mapping Required

Frontend must:
- Add 4 new inputs in the **Company form** bound to the API keys above
- Display the values in the **Company detail/list views**
- All four are optional — send `null` or omit the key on POST/PATCH

### Sample Response (after migration applied)

```json
{
  "id": 7,
  "company_name": "Maersk Line Egypt",
  "contact_person": "Capt. Hassan Mohamed",
  "alt_phone": "+20 100 123 4567",
  "address": "12 El Horreya St, Alexandria, Egypt",
  "notes": "Preferred vendor. WhatsApp only.",
  "company_type": "Owner",
  "status": "Active",
  "contact_email": "ops@maersk.com",
  "contact_phone": "+201234567890",
  "owner": "Capt. Hassan",
  "website": "https://maersk.com",
  "company_flag": 3,
  "company_flag_name": "Egypt",
  "hourly_rate": "45.00",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2025-07-01T14:22:00Z",
  "ships": [...],
  "open_positions": 12,
  "open_position_names": [...]
}
```

---

## Endpoint: `GET / PATCH /api/companies/job-positions/{id}/`

### Fields Added

| # | Field Name | API Key | Type | Required | Auto-managed | UI Label | Format |
|---|---|---|---|---|---|---|---|
| 1 | Creation timestamp | `created_at` | `datetime` (ISO 8601) | auto | yes (server) | Created | `"2026-07-14T10:16:00Z"` |
| 2 | Last-update timestamp | `updated_at` | `datetime` (ISO 8601) | auto | yes (server) | Updated | `"2026-07-14T10:16:00Z"` |

**Migration:** `companies/migrations/0014_joborderposition_created_at_and_more.py`
**Model file:** `companies/models.py` (JobOrderPosition class, after `remarks`)
**Serializer:** `companies/serializers.py` (no change — auto-included via `fields = '__all__'`)

### Frontend Mapping Required

Frontend must:
- Add a **"Created"** column in the job-positions table/list mapped to `created_at`
- (Optional) Add an **"Updated"** column mapped to `updated_at`
- **Do NOT send** these fields in POST/PATCH — they are read-only on the API. The server auto-fills them on create and update respectively.
- Existing rows were backfilled with the migration timestamp; new rows will get the real creation time automatically.

### Sample Response (after migration applied)

```json
{
  "id": 42,
  "job_order": 7,
  "rank": 4,
  "rank_name": "Chief Officer",
  "quantity": 1,
  "salary_min": "3000.00",
  "salary_max": "4500.00",
  "currency": "USD",
  "contract_duration_months": 6,
  "remarks": "Urgent hire",
  "status": "Open",
  "company_name": "Maersk Line Egypt",
  "ship_name": "Maersk Horizon",
  "filled_slots": 0,
  "remaining_slots": 1,
  "assigned_to": [],
  "created_at": "2026-07-14T10:16:00Z",
  "updated_at": "2026-07-14T10:16:00Z"
}
```

---

## Summary

| Endpoint | New Fields | Migration | Status |
|---|---|---|---|
| `/api/companies/{id}/` | `address`, `contact_person`, `alt_phone`, `notes` | `0013_company_address_contact_person_alt_phone_notes.py` | Code added — pending `python manage.py migrate companies` |
| `/api/companies/job-positions/{id}/` | `created_at`, `updated_at` | `0014_joborderposition_created_at_and_more.py` | Code added — pending `python manage.py migrate companies` |

## Apply the Migrations

```powershell
cd E:\2-TECHNO AQUARE
.\venv\Scripts\activate
python manage.py migrate companies
```

Expected output:
```
Running migrations:
  Applying companies.0013_company_address_contact_person_alt_phone_notes... OK
  Applying companies.0014_joborderposition_created_at_and_more... OK
```

## Handoff Notes for Frontend

1. All new fields are optional — none are required on POST or PATCH.
2. `address` and `notes` are unbounded text — use `<textarea>` inputs in the form.
3. `contact_person` and `alt_phone` are short strings — use single-line `<input type="text">`.
4. `created_at` and `updated_at` are read-only — never include them in POST/PATCH payloads.

---

## Endpoint: `POST / GET / PATCH / DELETE /api/interviews/reminders/`

**New endpoint added.** The original interview endpoint is `/api/interviews/`. A `Reminder` resource has been added to the same app, exposed under `/api/interviews/reminders/`.

### Fields Added (new model `Reminder`)

| # | Field Name | API Key | Type | Required | UI Label | Example |
|---|---|---|---|---|---|---|
| 1 | Crew member (user) | `user` | `integer` (FK to `Users`) | Yes | Crew Member Name | `42` |
| 2 | Reminder message | `text` | `string` (long) | Yes | Reminder | `"Call Capt. Hassan about medicals"` |
| 3 | Reminder date | `reminder_date` | `date` (YYYY-MM-DD) | Yes | Date | `"2026-07-20"` |
| 4 | Reminder time | `reminder_time` | `time` (HH:MM:SS) | Yes | Time | `"14:30:00"` |
| 5 | Completion flag | `is_completed` | `boolean` | No (default `false`) | — | `false` |
| 6 | Created at | `created_at` | `datetime` (ISO 8601) | auto (server) | — | `"2026-07-14T11:00:00Z"` |
| 7 | Updated at | `updated_at` | `datetime` (ISO 8601) | auto (server) | — | `"2026-07-14T11:00:00Z"` |

Plus a read-only computed field:

| Field | Type | Source | Purpose |
|---|---|---|---|
| `user_name` | `string` | `user.get_full_name()` | Display name of the assigned crew member |
| `user_email` | `string` | `user.email` | Email of the assigned crew member |

**Migration:** `interviews/migrations/0002_reminder.py`
**Model file:** `interviews/models.py` (new `Reminder` class)
**Serializer file:** `interviews/serializers.py` (new `ReminderSerializer`)
**View file:** `interviews/views.py` (new `ReminderViewSet`)
**URL file:** `interviews/urls.py` (router register `r'reminders'`)

### Available HTTP Methods

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/api/interviews/reminders/` | List all visible reminders | Bearer JWT |
| POST | `/api/interviews/reminders/` | Create a new reminder | Bearer JWT |
| GET | `/api/interviews/reminders/{id}/` | Retrieve one reminder | Bearer JWT |
| PUT | `/api/interviews/reminders/{id}/` | Full update | Bearer JWT |
| PATCH | `/api/interviews/reminders/{id}/` | Partial update | Bearer JWT |
| DELETE | `/api/interviews/reminders/{id}/` | Delete a reminder | Bearer JWT |
| GET | `/api/interviews/reminders/upcoming/` | List upcoming, not-completed reminders (custom action) | Bearer JWT |

### Authorization Rules

- **Admin / HR Manager / Recruiter** — sees and manages every reminder
- **Any other authenticated user** — sees only their own reminders (`user == request.user`)

### Sample Request (POST)

```http
POST /api/interviews/reminders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user": 42,
  "text": "Call Capt. Hassan about medicals",
  "reminder_date": "2026-07-20",
  "reminder_time": "14:30:00"
}
```

### Sample Response (GET single)

```json
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
```

### Frontend Mapping Required

Frontend must:
- Add 4 inputs in the **Add Reminder** modal mapped to `user`, `text`, `reminder_date`, `reminder_time` (the screenshot you sent already does this)
- Send the user as the integer `id` (not the name string)
- Send dates as `YYYY-MM-DD`, times as `HH:MM:SS` (or `HH:MM`)
- Use `/api/interviews/reminders/` for create, list, and delete
- Use `/api/interviews/reminders/upcoming/` if you want a "today and later" feed
- Optionally display `is_completed` with a checkbox to mark reminders done (PATCH `{"is_completed": true}`)

---

## Summary

| Endpoint | New Fields / Resource | Migration | Status |
|---|---|---|---|
| `/api/companies/{id}/` | `address`, `contact_person`, `alt_phone`, `notes` | `0013_company_address_contact_person_alt_phone_notes.py` | Code added — pending `python manage.py migrate companies` |
| `/api/companies/job-positions/{id}/` | `created_at`, `updated_at` | `0014_joborderposition_created_at_and_more.py` | Code added — pending `python manage.py migrate companies` |
| `/api/interviews/reminders/` *(new endpoint)* | `user`, `text`, `reminder_date`, `reminder_time`, `is_completed`, `created_at`, `updated_at` | `0002_reminder.py` | Code added — pending `python manage.py migrate interviews` |

## Apply All Migrations

```powershell
cd E:\2-TECHNO AQUARE
.\venv\Scripts\activate
python manage.py migrate companies
python manage.py migrate interviews
```

Expected output:
```
Running migrations:
  Applying companies.0013_company_address_contact_person_alt_phone_notes... OK
  Applying companies.0014_joborderposition_created_at_and_more... OK
  Applying interviews.0002_reminder... OK
```
