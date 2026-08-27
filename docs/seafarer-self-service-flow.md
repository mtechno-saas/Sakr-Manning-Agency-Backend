# Seafarer Self-Service Flow

End-to-end flow for onboarding a new seafarer via the Admin's CV upload, then letting the seafarer log in and manage their own profile.

Implemented in commits `eab1d6f9` → `3728f2dd` → `4ef5d68c` → `4fdce549` → `0404052e` on `mtechno-saas/Sakr-Manning-Agency-Backend:server-updates`.

---

## TL;DR

1. **Admin** uploads a seafarer CV via `POST /ai/parse/` with `save_to_db=true`.
2. Backend deterministically parses the CV, creates a `Users` row (role=`Employee`, password = phone number) and a `CVSubmission` row.
3. **Seafarer** logs in at `POST /api/auth/phone-login/` using `{phone, phone}` — the phone number is both username and password.
4. **Seafarer** calls `GET /api/me/` to see their own profile, `PATCH /api/me/` to update fields.

No email confirmation, no OTP, no Twilio. The phone number is the credential.

---

## Endpoints

| Method | URL | Auth | Purpose |
|---|---|---|---|
| POST | `/ai/parse/` | **Admin only** | Upload CV, parse, optionally save to `Users` + `CVSubmission` |
| POST | `/api/auth/phone-login/` | AllowAny | Seafarer login with phone + phone-as-password, returns JWT |
| GET | `/api/me/` | Any auth user | Read own profile |
| PATCH | `/api/me/` | Any auth user | Edit own profile (whitelisted fields only) |

Email/password login at `POST /api/login/` is unchanged — that's still how Admin / HR / Recruiter log in.

---

## Step 1 — Admin uploads the CV

`POST /ai/parse/`

| Form field | Type | Notes |
|---|---|---|
| `file` | File | `.pdf` or `.docx`, max 20 MB |
| `save_to_db` | Text | `"true"` to persist; omit (or `"false"`) for parse-only |

```bash
curl -X POST "https://backend.sakrshipping.com/ai/parse/" \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -F "file=@waiter.docx" \
  -F "save_to_db=true"
```

What the backend does:

1. `DocumentProcessor` extracts text + tables from the file (no LLM).
2. `SakrTemplateExtractor` deterministically parses the 12 sections.
3. `_save_parser_output` writes two rows in a single transaction:
   - `Users` (or updates if email already exists) with role = `Employee`, `set_password(phone)`
   - `CVSubmission` linked to that user

**Response 200:**

```json
{
  "success": true,
  "extractor": "sakr_template",
  "confidence": 0.95,
  "data": { "0_application_meta": {...}, "1_personal_details": {...}, ... },
  "warnings": [],
  "file_name": "waiter.docx",
  "saved": true,
  "user_id": 42,
  "cv_submission_id": 99
}
```

> **Note:** the password is intentionally NOT in the response. Admin doesn't need to know it — the seafarer's phone number is the credential.

**What gets created in `Users`:**

| Field | Source | Example |
|---|---|---|
| `email` | `contact_details.e_mail` (lowercased) | `mohashehata1995@gmail.com` |
| `first_name` / `middle_name` | split from `personal_details.full_name` | `MOHAMED` / `SHEHATA RAMADAN ABDEL BASSET` |
| `phone_number` | `contact_details.mobile_tel` | `00201090946284` |
| `nationality`, `Place_Of_Birth`, `Nearest_Port` | `personal_details` | `Egyptian`, `Qena, Egypt`, `Luxor` |
| `Height_Cm`, `Weight_Kg` | `personal_details` (ints) | `173`, `67` |
| `date_of_birth` | `personal_details.date_of_birth` parsed `DD/MM/YYYY` etc. | `1995-02-28` |
| `marital_status` | `personal_details.marital_status` | `Single` / `Married` |
| `register_code` | `0_application_meta.register_code` | `DR-6.104` |
| `register_date` | `0_application_meta.register_date` parsed | `2025-07-10` |
| `application_for_position` | `0_application_meta.application_for_position_as` if it matches a known choice; else blank | `Waiter` |
| `other_position` | `0_application_meta.other_position` (always set) | `Bar Attendent Lounge` |
| `address` | `contact_details.home_address_city` (truncated to 100 chars) | `Qena - Qena - Sheikh Younis` |
| `role` | always `Employee` | `Employee` |
| `password` | hashed via `set_password(phone_number)` | (hashed) |

**What gets created in `CVSubmission`:**

| Field | Source | Example |
|---|---|---|
| `user` | the new `Users` row | `42` |
| `cv_file` | the uploaded file (stored in `cv_submissions/`) | (file) |
| `expected_salary` | parsed from `expected_salary` (`"730 $"` → `Decimal("730")`) | `730.00` |
| `availability_date` | parsed from `available_date` (`"25/7/2025"`) | `2025-07-25` |
| `status` | always `Pending` | `Pending` |

---

## Step 2 — Seafarer logs in

`POST /api/auth/phone-login/`

```json
{ "phone": "00201090946284", "password": "00201090946284" }
```

| Outcome | Response |
|---|---|
| Success | `200` + `{access, refresh, user: {...}}` (JWT) |
| Phone not in DB | `401` `No account found for that phone number` |
| Wrong password | `401` `Invalid phone or password` |
| Both fields empty | `400` `phone and password are required` |
| Account disabled | `403` `Account is disabled` |

**Success response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 42,
    "email": "mohashehata1995@gmail.com",
    "first_name": "MOHAMED",
    "phone_number": "00201090946284",
    "role": "Employee"
  }
}
```

The seafarer saves the `access` token and uses it as `Authorization: Bearer <token>` on subsequent requests.

---

## Step 3 — Seafarer views their profile

`GET /api/me/`

```bash
curl "https://backend.sakrshipping.com/api/me/" \
  -H "Authorization: Bearer $SEAFARER_JWT"
```

**Response 200:**

```json
{
  "id": 42,
  "email": "mohashehata1995@gmail.com",
  "first_name": "MOHAMED",
  "middle_name": "SHEHATA RAMADAN ABDEL BASSET",
  "phone_number": "00201090946284",
  "address": "Qena - Qena - Sheikh Younis",
  "city": null,
  "country": null,
  "nationality": "Egyptian",
  "Place_Of_Birth": "Qena, Egypt",
  "Nearest_Port": "Luxor",
  "Height_Cm": 173,
  "Weight_Kg": 67,
  "marital_status": "Single",
  "smoker": false,
  "us_visa_status": "",
  "schengen_visa_status": "",
  "blood_type": "",
  "register_code": "DR-6.104",
  "register_date": "2025-07-10",
  "available_date": "2025-07-25",
  "role": "Employee",
  "user_status": "ON_SITE"
}
```

---

## Step 4 — Seafarer updates their profile

`PATCH /api/me/`

```json
{
  "address": "Cairo - Maadi",
  "city": "Cairo",
  "country": "Egypt",
  "Nearest_Port": "Alexandria"
}
```

| Outcome | Response |
|---|---|
| All fields accepted | `200` + updated profile |
| Some fields dropped (role, is_staff, email, password, …) | `200` + updated profile (dangerous fields silently ignored) |
| ALL fields are non-editable | `400` + `{detail: "No editable fields in the request..."}` |

**Whitelisted editable fields** (everything else is dropped):

```
first_name, middle_name, phone_number, address, city, country,
nationality, Place_Of_Birth, Nearest_Port, Height_Cm, Weight_Kg,
marital_status, smoker, us_visa_status, schengen_visa_status, blood_type
```

**Deliberately NOT editable by the seafarer (intentional safety net):**

- `role` — would let the seafarer escalate to Admin
- `is_staff`, `is_superuser` — Django permission flags
- `email` — unique key, would let the seafarer hijack another account if they typed a different email
- `password` — the seafarer doesn't know it; they use the phone-as-password flow
- `register_code`, `register_date`, `available_date` — admin-managed
- `user_status` — admin-managed (the 5-state enum)

---

## End-to-end example

```bash
# 1. Admin uploads the CV
curl -X POST "https://backend.sakrshipping.com/ai/parse/" \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -F "file=@waiter.docx" -F "save_to_db=true"
# → 200, user_id=42, cv_submission_id=99

# 2. Seafarer logs in
curl -X POST "https://backend.sakrshipping.com/api/auth/phone-login/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201090946284","password":"00201090946284"}'
# → 200, {access: "eyJ...", refresh: "eyJ...", user: {...}}

# 3. Seafarer views their profile
curl "https://backend.sakrshipping.com/api/me/" \
  -H "Authorization: Bearer $SEAFARER_JWT"
# → 200, full profile

# 4. Seafarer moves to a new address
curl -X PATCH "https://backend.sakrshipping.com/api/me/" \
  -H "Authorization: Bearer $SEAFARER_JWT" \
  -H "Content-Type: application/json" \
  -d '{"address":"Cairo - Maadi","city":"Cairo","country":"Egypt"}'
# → 200, updated profile
```

---

## Edge cases

| Case | Behavior |
|---|---|
| CV has no phone number | Password falls back to `email` (the standard email-login flow still works) |
| Seafarer tries to set `role: "Admin"` via `PATCH /api/me/` | Field is silently dropped; response is `200` with the rest applied, but `role` stays `Employee` |
| Seafarer tries to change `email` via `PATCH /api/me/` | Field is dropped; if it was the ONLY field, response is `400` |
| Same CV re-uploaded with a new phone | `Users` row is updated (existing user) and the password is reset to the new phone |
| Seafarer's `Users` row has `is_active=False` | `POST /api/auth/phone-login/` returns `403` |
| Two seafarers with the same phone | The second one **fails** — phone lookup is unique-by-DB, and saving the second would attempt `get_or_create` by email. Either way, the phone-as-password only works for the first seafarer to claim that phone. |

---

## Auth matrix (recap)

| Endpoint | Admin | HR Manager | Recruiter | Employee / Crew | Unauth |
|---|---|---|---|---|---|
| `POST /ai/parse/` (save_to_db=true) | ✅ | ❌ 403 | ❌ 403 | ❌ 403 | ❌ 401 |
| `POST /api/auth/phone-login/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET / PATCH /api/me/` | ✅ (own profile) | ✅ (own) | ✅ (own) | ✅ (own) | ❌ 401 |
| `POST /api/login/` (email + password) | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GET /api/users/users/` | ✅ all | ✅ all | view-only | own only | ❌ 401 |

---

## Why this design (vs alternatives)

- **No email confirmation flow.** The CV is uploaded by an Admin, so we already trust the data. Adding a "verify your email" step would require the seafarer to remember a token from an email they may not check, for a CV they didn't submit. Skip it.
- **No OTP / SMS provider.** Twilio / Vonage would add a vendor dep and a recurring cost for every login. The phone-as-password approach is "what you have IS what you log in with" — zero infrastructure.
- **No password reset flow (yet).** The seafarer can't change their password from the UI in this iteration. If they need a new password, an Admin can call `set_password(...)` directly. A `POST /api/auth/change-password/` endpoint is a small follow-up if needed.
- **No `/api/me/cv-submissions/` or `/api/me/contracts/` aggregators (yet).** The seafarer can hit the existing role-scoped viewsets (`GET /api/cv-submissions/?user=me`, etc.) which already enforce row-level permissions. Dedicated `/api/me/` sub-resources are a follow-up.

---

## Files touched

- `ai_document/views.py` — `_save_parser_output` sets role=`Employee` + `set_password(phone)`
- `api/views.py` — new `PhoneLoginView` + `MeView` + `SEAFARER_EDITABLE_FIELDS` + `_serialize_user`
- `api/urls.py` — wires `auth/phone-login/` and `me/`
- `ai_document/views.py` — `ParseOnlyView.permission_classes = [IsAdmin]` (so /ai/parse/ stays admin-only)
- `docs/seafarer-self-service-flow.md` — this file

## Tests

14 new tests in `api/tests.py`:

- `PhoneLoginTests` (5): correct creds, wrong pwd, unknown phone, missing fields, inactive user
- `MeViewTests` (5): GET own profile, PATCH safe field, mixed safe/unsafe, pure-unsafe → 400, unauth → 401
- `SaveParserOutputSeafarerPasswordTests` (3): phone is password, email fallback when no phone, role=Employee default

Plus 6 `ParseOnlyViewAuthTest` tests for the Admin lockdown, and the existing 79 extractor tests.

**Full suite: 238 tests, 2 pre-existing failures (DocumentUploadViewTest, IntegrationTest — LLM path, untouched in this work).**
