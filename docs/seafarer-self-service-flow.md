# Seafarer Self-Service Flow

End-to-end flow for onboarding a new seafarer via the Admin's CV upload, then letting the seafarer log in and manage their own profile.

Two perspectives are documented separately:
- **[Admin side](#admin-side-flow)** — what the Admin does to onboard a new seafarer
- **[Employee/Seafarer side](#employeeseafarer-side-flow)** — what the seafarer does to log in and manage their data

Implemented in commits `eab1d6f9` → `3728f2dd` → `4ef5d68c` → `4fdce549` → `0404052e` on `mtechno-saas/Sakr-Manning-Agency-Backend:server-updates`.

---

## TL;DR

| # | Who | What |
|---|---|---|
| 1 | **Admin** | `POST /ai/parse/` with `save_to_db=true` → backend creates `Users` (role=`Employee`, password=phone) + `CVSubmission` and **sends an OTP to the seafarer's email** (the address on file from the CV) via the configured email service |
| 2 | **Seafarer** | Receives the OTP in their email inbox, calls `POST /api/auth/verify-otp/` with `{phone, otp}` → marks the user as phone-verified, returns JWT |
| 3 | **Seafarer** | `POST /api/auth/phone-login/` with `{phone, phone}` → JWT (now allowed because they're verified) |
| 4 | **Seafarer** | `GET /api/me/` → see their own profile |
| 5 | **Seafarer** | `PATCH /api/me/` → update fields they care about (address, nationality, etc.) |

No email confirmation, no Twilio required. The phone number is the credential, and the system itself sends the OTP to the email address on file. The default email backend (`ConsoleEmailService`) logs the would-be email to the server console — swap in SMTP / SendGrid / Mailgun / Postmark / AWS SES for production by setting `EMAIL_SERVICE` in `saker/settings.py`.

> **Why email and not SMS?** The user explicitly chose email — seafarers get their OTP in their inbox (where they already receive job updates), the system doesn't need an SMS provider contract, and there's no per-message cost. The seafarer still authenticates with their phone (phone = password) — the email is just the delivery channel for the OTP.

---

## Endpoints (single source of truth)

| Method | URL | Auth | Used by |
|---|---|---|---|
| POST | `/ai/parse/` | **Admin only** (HR/Recruiter/Employee/Crew → 403, unauth → 401) | **Admin** |
| POST | `/api/auth/phone-login/` | AllowAny | **Seafarer** |
| GET | `/api/me/` | Any auth user | **Seafarer** (or anyone checking their own profile) |
| PATCH | `/api/me/` | Any auth user | **Seafarer** |
| POST | `/api/login/` (existing, unchanged) | AllowAny | **Admin / HR / Recruiter** (email + password) |

---

## Admin side flow

> **Who:** an `Admin` user (role=`Admin`, `is_staff=True`).
> **Goal:** onboard a new seafarer by uploading their CV. The system does the rest.

### Step A1 — Get an admin JWT

The Admin already has an account on the system (created by another Admin via `/api/users/users/`). They log in with email + password at the existing endpoint:

```bash
curl -X POST "https://backend.sakrshipping.com/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sakrshipping.com","password":"<their-password>"}'
# → 200 { "access": "eyJ...", "refresh": "eyJ..." }
```

Admin stores `access` as `$ADMIN_JWT` and uses it as `Authorization: Bearer $ADMIN_JWT` on subsequent calls.

### Step A2 — Upload the seafarer's CV

```bash
curl -X POST "https://backend.sakrshipping.com/ai/parse/" \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -F "file=@waiter.docx" \
  -F "save_to_db=true"
```

| Form field | Type | Notes |
|---|---|---|
| `file` | File | `.pdf` or `.docx`, max 20 MB |
| `save_to_db` | Text | `"true"` to persist; omit (or `"false"`) for parse-only |

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

> **Note:** the password is intentionally NOT in the response. Admin doesn't need to know it — the seafarer's phone number is the credential. If Admin wants to give the seafarer their credentials, they only need to share: "your phone number is your password" + the seafarer's own phone number.

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
| `password` | hashed via `set_password(phone_number)` | (hashed — unreadable) |

**What gets created in `CVSubmission`:**

| Field | Source | Example |
|---|---|---|
| `user` | the new `Users` row | `42` |
| `cv_file` | the uploaded file (stored in `cv_submissions/`) | (file) |
| `expected_salary` | parsed from `expected_salary` (`"730 $"` → `Decimal("730")`) | `730.00` |
| `availability_date` | parsed from `available_date` (`"25/7/2025"`) | `2025-07-25` |
| `status` | always `Pending` | `Pending` |

### Step A3 — Hand off to the seafarer

Admin's job is done. The seafarer now has:

- A `Users` row (id=`user_id` from the response), role=`Employee`, password = their phone number.
- A `CVSubmission` row (id=`cv_submission_id`) attached to that user.

Admin can communicate the seafarer's phone number to them through whatever channel they use (WhatsApp, in person, phone call, email — whatever). The seafarer does NOT need a separate setup email or invite link.

### What Admin can do later (via existing endpoints)

The Admin can keep managing the seafarer via the standard user-management endpoints:

| Action | Endpoint |
|---|---|
| List all seafarers | `GET /api/users/users/?role=Employee` |
| View a specific seafarer | `GET /api/users/users/42/` |
| Update seafarer's role, status, register_code, etc. | `PATCH /api/users/users/42/` |
| View the seafarer's CV submission | `GET /api/cv-submissions/99/` |
| Approve / reject the CV | `PATCH /api/cv-submissions/99/` (set `status` field) |

The Admin uses the same email + password login (`/api/login/`) and JWT for these calls.

---

## Employee/Seafarer side flow

> **Who:** the seafarer (role=`Employee`, default from the parser flow).
> **Goal:** verify their phone, log in for the first time, see their own data, update what's changed since the CV was uploaded.

### Step S0 — First-time phone verification (email OTP, one-time)

Before the seafarer can log in, they need to prove they own the email address on file (from the CV). This happens **once** — the seafarer is not asked to re-verify on subsequent logins.

The flow:

1. **Admin** uploads the CV via `POST /ai/parse/` with `save_to_db=true`.
2. Backend creates the `Users` row with `is_phone_verified=False`, then **generates a 6-digit numeric OTP**, stores it on the row (`otp_code` + `otp_expires_at`) with a 10-minute TTL, and **sends it to the seafarer's email** (the address in the CV's contact section) via the configured email service. The admin never sees the OTP in the API response.
3. **Seafarer** receives the OTP in their email inbox (in dev, the OTP is in the server log via `ConsoleEmailService`).
4. **Seafarer** hits `POST /api/auth/verify-otp/` with `{phone, otp}` (the phone is the lookup key, the OTP is what was emailed).
5. Backend checks the OTP matches and hasn't expired, marks the user as `is_phone_verified=True`, clears the OTP fields so a stale OTP can't be reused, and returns a JWT.
6. Seafarer is now verified. They can proceed to the normal login flow (S1 below).

**Endpoints:**

| Method | URL | Body | Returns |
|---|---|---|---|
| POST | `/api/auth/request-otp/` | `{phone}` | `200 {phone, ttl_minutes}` (regenerates a fresh OTP, idempotent — used to re-send if the seafarer lost the first one) |
| POST | `/api/auth/verify-otp/` | `{phone, otp}` | `200 {access, refresh, user}` (JWT, sets `is_phone_verified=True`, clears OTP) |

**Request OTP — example:**

```bash
curl -X POST "https://backend.sakrshipping.com/api/auth/request-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201090946284"}'
# → 200 { "phone": "00201090946284", "ttl_minutes": 10 }
# (OTP is sent to the seafarer's email — not in the response)
```

**Verify OTP — example:**

```bash
curl -X POST "https://backend.sakrshipping.com/api/auth/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201090946284","otp":"482917"}'
# → 200 { "access": "eyJ...", "refresh": "eyJ...", "user": {...} }
```

**Why a custom backend-generated OTP (no SMS provider out-of-the-box):**

- The user explicitly chose "backend system to do it" instead of an external SMS provider, so there's no third-party dep and no per-SMS cost.
- The user then chose **email** as the delivery channel — seafarers get the OTP in their inbox (where they already receive job updates) instead of having to wait for a text.
- The default `ConsoleEmailService` logs the would-be email to the server console — fine for dev/test, and any developer can read the OTP from the log.
- For production, plug in a real provider by setting `EMAIL_SERVICE = "your.module.YourEmailService"` in `saker/settings.py` (see `api/email.py` for the `EmailService` protocol). SMTP, SendGrid, Mailgun, Postmark, and AWS SES all work — point the env var at whichever module you implement.

**Model fields added to `Users`:**

| Field | Type | Default | Purpose |
|---|---|---|---|
| `is_phone_verified` | `BooleanField` | `False` | Gate for `phone-login` and the verify-otp flow |
| `otp_code` | `CharField(max_length=10)` | `null` | The current OTP (cleared after verify) |
| `otp_expires_at` | `DateTimeField` | `null` | OTP TTL; checked on verify-otp |

### Step S1 — Log in (phone = password, after phone is verified)

Once the seafarer is phone-verified (S0), they can log in by entering **their phone number in both fields** — phone and password are the same value. If the user isn't verified, this endpoint returns `403` with a hint to call `/api/auth/verify-otp/` first.

```bash
curl -X POST "https://backend.sakrshipping.com/api/auth/phone-login/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201090946284","password":"00201090946284"}'
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

The seafarer stores the `access` token in their app and uses it as `Authorization: Bearer <token>` on subsequent requests. (They can refresh it later via `POST /api/login/refresh/`.)

> **What if the seafarer doesn't have their phone number handy?** Their phone is also on file in the system (Admin uploaded the CV, so it's in the database). If they truly can't remember it, an Admin can look it up via `GET /api/users/users/?search=<name>` and tell them. There is no "forgot my phone" self-serve flow in this iteration.

### Step S2 — View their own profile

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

This is read-only — no side effects, safe to call any number of times.

### Step S3 — Update fields that changed since the CV was uploaded

The CV was a snapshot in time. The seafarer moves house, changes their phone, gains citizenship, etc. They use `PATCH /api/me/` to keep their profile current.

```bash
curl -X PATCH "https://backend.sakrshipping.com/api/me/" \
  -H "Authorization: Bearer $SEAFARER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Cairo - Maadi",
    "city": "Cairo",
    "country": "Egypt",
    "Nearest_Port": "Alexandria",
    "nationality": "Egyptian"
  }'
```

**Response 200** (returns the full updated profile).

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

### What the seafarer CANNOT do (in this iteration)

- ❌ Change their own password (would need a `POST /api/auth/change-password/` flow)
- ❌ Add new documents (passport, seaman book) — they'd use the existing role-scoped `DocumentViewSet` which is admin/HR/recruiter write
- ❌ See other seafarers' data — `/api/me/` is always scoped to the auth'd user
- ❌ Apply to job orders — the existing `SeafarerApplicationViewSet` exists, but isn't wired into `/api/me/` yet

---

## End-to-end example (admin + seafarer together)

```bash
# === ADMIN SIDE ===
# A1. Admin logs in (email + password)
ADMIN_JWT=$(curl -s -X POST "https://backend.sakrshipping.com/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sakrshipping.com","password":"<admin-pwd>"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# A2. Admin uploads the seafarer's CV
curl -X POST "https://backend.sakrshipping.com/ai/parse/" \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -F "file=@waiter.docx" -F "save_to_db=true"
# → 200, user_id=42, cv_submission_id=99
# (Admin tells the seafarer out-of-band: "Your phone number is your password")

# === SEAFARER SIDE ===
# S1. Seafarer logs in with their phone as both fields
SEAFARER_JWT=$(curl -s -X POST "https://backend.sakrshipping.com/api/auth/phone-login/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201090946284","password":"00201090946284"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# S2. Seafarer views their profile
curl "https://backend.sakrshipping.com/api/me/" \
  -H "Authorization: Bearer $SEAFARER_JWT"
# → 200, full profile

# S3. Seafarer updates their address after moving
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
| CV has no email | User is still created, but no initial OTP is dispatched. The seafarer can still log in via `/api/login/` (email + email-as-password fallback). They can also call `/api/auth/request-otp/` later — if their email is empty it will return the standard "OTP has been sent" no-leak response. |
| Seafarer tries to set `role: "Admin"` via `PATCH /api/me/` | Field is silently dropped; response is `200` with the rest applied, but `role` stays `Employee` |
| Seafarer tries to change `email` via `PATCH /api/me/` | Field is dropped; if it was the ONLY field, response is `400` |
| Same CV re-uploaded with a new phone | `Users` row is updated (existing user) and the password is reset to the new phone |
| Seafarer's `Users` row has `is_active=False` | `POST /api/auth/phone-login/` returns `403` |
| Two seafarers with the same phone | The second one **fails** — phone lookup is unique-by-DB, and saving the second would attempt `get_or_create` by email. Either way, the phone-as-password only works for the first seafarer to claim that phone. |
| Admin uploads a CV but the seafarer's CVSubmission was already `Approved` | The new CVSubmission is still created (status=`Pending`). Admin needs to manually merge/dedupe if the same seafarer is re-uploaded. |

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
- **No OTP / SMS provider.** Twilio / Vonage would add a vendor dep and a recurring cost. The OTP is delivered by **email** instead (which is essentially free and where seafarers already get job updates) — the `EmailService` interface is pluggable, and the default `ConsoleEmailService` logs the would-be email. See Step S0 for the full flow.
- **No password reset flow (yet).** The seafarer can't change their password from the UI in this iteration. If they need a new password, an Admin can call `set_password(...)` directly. A `POST /api/auth/change-password/` endpoint is a small follow-up if needed.
- **No `/api/me/cv-submissions/` or `/api/me/contracts/` aggregators (yet).** The seafarer can hit the existing role-scoped viewsets (`GET /api/cv-submissions/?user=me`, etc.) which already enforce row-level permissions. Dedicated `/api/me/` sub-resources are a follow-up.

---

## Files touched

- `ai_document/views.py` — `_save_parser_output` sets role=`Employee` + `set_password(phone)` + initial OTP dispatch via email
- `ai_document/views.py` — `ParseOnlyView.permission_classes = [IsAdmin]` (so /ai/parse/ stays admin-only)
- `api/views.py` — `PhoneLoginView` + `MeView` + `SEAFARER_EDITABLE_FIELDS` + `_serialize_user` + `RequestOTPView` + `VerifyOTPView` (email OTP)
- `api/email.py` — `EmailService` protocol + `ConsoleEmailService` default + `get_email_service()` + `generate_otp()` + `otp_default_ttl_minutes()` (pluggable, default logs to console)
- `api/urls.py` — wires `auth/phone-login/`, `auth/request-otp/`, `auth/verify-otp/`, `me/`
- `api/models.py` — 3 new fields on `Users` (`is_phone_verified`, `otp_code`, `otp_expires_at`)
- `api/migrations/0070_add_phone_verification_otp.py` — adds the 3 OTP fields
- `saker/settings.py` — `EMAIL_SERVICE` (env-overridable, default `api.email.ConsoleEmailService`) + `OTP_TTL_MINUTES` (default 10)
- `docs/seafarer-self-service-flow.md` — this file

## Tests

28 new tests in `api/tests.py`:

- `PhoneLoginTests` (6): correct creds, wrong pwd, unknown phone, missing fields, inactive user, unverified user → 403 with verify-otp hint
- `RequestOTPTests` (4): known phone regenerates OTP, unknown phone → 200 no leak, missing phone → 400, inactive user → 403
- `VerifyOTPTests` (6): correct OTP, wrong OTP, expired OTP, unknown phone, missing fields, already-verified idempotent
- `OTPEmailDispatchTests` (2): initial OTP stored and email dispatched; skipped when no email on CV
- `RequestOTPNoEmailTests` (1): user with no email gets the same no-leak 200 response as an unknown phone
- `RequestOTPEmailDispatchTests` (1): `/api/auth/request-otp/` dispatches to email, not phone
- `MeViewTests` (5): GET own profile, PATCH safe field, mixed safe/unsafe, pure-unsafe → 400, unauth → 401
- `SaveParserOutputSeafarerPasswordTests` (3): phone is password, email fallback when no phone, role=Employee default

Plus 6 `ParseOnlyViewAuthTest` tests for the Admin lockdown, and the existing 79 extractor tests.
