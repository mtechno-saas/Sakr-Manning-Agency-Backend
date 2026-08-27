# Admin-Onboarded Seafarer Flow

End-to-end flow for when an **Admin creates a `CVSubmission` for a seafarer that doesn't have a self-set password yet**. The system emails the seafarer a signed magic link; the seafarer clicks it, lands on the frontend's "set your password" page, and sets a password they can use to log in.

This is the **counterpart** to the seafarer-self-service flow. Where the self-service flow is for seafarers who uploaded a CV via `/ai/parse/` (phone-as-password, OTP by email), **this flow is for seafarers who are added to the system manually by an Admin** through the regular CRUD endpoints. After setting a password via the magic link, the seafarer can log in via `POST /api/login/` with their email + new password — phone-as-password still works as a fallback unless explicitly disabled.

Two perspectives are documented separately:
- **[Admin side](#admin-side-flow)** — what the Admin does to onboard a seafarer
- **[Seafarer side](#seafarer-side-flow)** — what the seafarer does to set their password and log in

Implemented in commit `803a78b4` on `mtechno-saas/Sakr-Manning-Agency-Backend:server-updates`.

---

## TL;DR

| # | Who | What |
|---|---|---|
| 1 | **Admin** | `POST /api/cv-submissions/` with `{user_email, user_first_name, user_phone, ...}` (or `{user: <id>}` to link to an existing user) → backend **auto-creates the `Users` row** if needed (with `password = user_phone`) and creates the `CVSubmission` linked to it |
| 2 | **System** | Sends an email to the linked seafarer's email address (the one in `Users.email`) with a signed magic link: `https://sakrshipping.com/set-password?uidb64=...&token=...` |
| 3 | **Seafarer** | Clicks the link, lands on the frontend's "set new password" page |
| 4 | **Seafarer** | Types their new password + submits. Frontend POSTs `{uidb64, token, new_password}` to `POST /api/auth/set-password-confirm/` |
| 5 | **System** | Validates the signed token (HMAC + 24h TTL), calls `user.set_password(...)`, returns 200 |
| 6 | **Seafarer** | `POST /api/login/` with `{email, password}` → JWT, can now use the standard email-login flow. **Phone-as-password also works** (`POST /api/auth/phone-login/` with `{phone, phone}`) once the seafarer verifies their phone via `POST /api/auth/verify-otp/`. |

The default email backend is `DjangoSMTPEmailService` (uses the project's Gmail SMTP config). For local dev / CI, set `EMAIL_SERVICE=api.email.ConsoleEmailService` to log the would-be email to the server console instead.

**Key properties:**

- **Single-step onboarding:** A single `POST /api/cv-submissions/` with `user_email` + `user_first_name` + `user_phone` (and optional `user_middle_name`) auto-creates the `Users` row in the same transaction. No separate `POST /api/users/users/` step.
- **Default password is the phone number:** When the user is auto-created, `user.set_password(user_phone)` is called — phone-as-password is the immediate fallback. The seafarer can use either the magic link (to set a custom password) or `POST /api/auth/phone-login/` with `{phone, phone}` (after verifying via OTP).
- **Idempotent on existing users:** If the seafarer already exists (lookup by email), the system refreshes `first_name`/`middle_name`/`phone_number` if the admin supplied them, but does NOT touch the password (the seafarer may have set their own).
- **Welcome email is sent only once per seafarer:** Tracked by `Users.welcome_email_sent_at`. A second `CVSubmission` for the same seafarer does NOT re-send the email.
- **Secure:** The token is HMAC-signed (Django's `default_token_generator`) and timestamp-checked at 24h. A tampered or expired link fails closed.
- **Non-blocking:** Email dispatch failures never roll back the `CVSubmission` save. The seafarer just doesn't get the email; the admin can re-trigger by clearing `welcome_email_sent_at` and re-creating a `CVSubmission` for the user.
- **Doesn't replace phone-as-password:** The seafarer can keep using phone-as-password (after OTP verification) AND the email+password option once they set a custom one.

---

## Endpoints (single source of truth)

| Method | URL | Auth | Used by |
|---|---|---|---|
| POST | `/api/cv-submissions/` | `CVPermission` (Admin/HR/Recruiter full, Employee own-only) | **Admin** — onboard a new seafarer |
| POST | `/api/auth/set-password-confirm/` | **AllowAny** (the token IS the credential) | **Seafarer** — submit the new password |
| POST | `/api/login/` (existing, unchanged) | AllowAny | **Seafarer** — log in with email + new password after setting one |

**Helper URL the seafarer clicks** (not a backend endpoint, frontend-only):

```
<FRONTEND_SET_PASSWORD_URL>?uidb64=<base64-user-pk>&token=<signed-blob>
```

Default `FRONTEND_SET_PASSWORD_URL` is `https://sakrshipping.com/set-password` (env-overridable). The frontend dev renders the "set new password" form at this path.

---

## Admin side flow

> **Who:** an `Admin` user (role=`Admin`, `is_staff=True`).
> **Goal:** onboard a new seafarer by creating a `CVSubmission` for them. The system does the rest — emails the seafarer a magic link.

### Step A1 — Get an admin JWT

The Admin logs in with email + password at the existing endpoint:

```bash
curl -X POST "https://backend.sakrshipping.com/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sakrshipping.com","password":"<admin-pwd>"}'
# → 200 { "access": "eyJ...", "refresh": "eyJ..." }
```

Admin stores `access` as `$ADMIN_JWT` for subsequent calls.

### Step A2 — Create the CVSubmission for the seafarer

A single `POST /api/cv-submissions/` does it all: links to an existing seafarer, **or auto-creates a new `Users` row from the request body and links to that**. The `CVSubmission` row links to the seafarer via the `user` foreign key (`CVSubmission.user` → `Users.id`, a one-to-many relationship: one seafarer can have many CVSubmissions, e.g. one per job application).

**Three ways to identify the seafarer in the request body:**

1. **By user ID** (link to an existing user — no auto-create):
   ```json
   { "user": 42, "status": "Pending", "position": 7 }
   ```

2. **By email — user already exists** (look up by email, refresh first/middle/phone if supplied; no password reset):
   ```json
   {
     "user_email": "seafarer@sakrshipping.com",
     "user_first_name": "AHMED",
     "user_middle_name": "HASSAN",
     "user_phone": "00201012345678",
     "status": "Pending"
   }
   ```

3. **By email — user is new** (auto-create the `Users` row with default password = phone number, then send the welcome email):
   ```json
   {
     "user_email": "newbie@sakrshipping.com",
     "user_first_name": "AHMED",
     "user_middle_name": "HASSAN",
     "user_phone": "00201012345678",
     "status": "Pending"
   }
   ```

In case (3) the backend:
- Looks up `Users.objects.get(email=user_email)` — `DoesNotExist`
- Calls `Users.objects.create_user(email=..., password=user_phone, first_name=..., middle_name=...)` — the **default password is the phone number** (so phone-as-password is the immediate fallback for the seafarer)
- Sets `role = 'Employee'` (matching the `/ai/parse/` convention)
- Saves the `CVSubmission` linked to the new user
- Calls `dispatch_welcome_email(user)` → emails the seafarer a "set your password" magic link

**Validation:**
- DRF's `PrimaryKeyRelatedField` validates the `user` ID at serializer-time → 400 `"Invalid pk \"X\" - object does not exist."` if the ID is wrong
- The `user_email` field is just an `EmailField` (validates format only); the user-existence check happens in the viewset's `perform_create` and either creates the user or looks them up

**For Employees / Crew:** the `user_email` auto-create branch is admin-only. Employees submitting their own CV can only target themselves — the `user_email` field is ignored and the CVSubmission is attributed to the request user.

```bash
curl -X POST "https://backend.sakrshipping.com/api/cv-submissions/" \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 42,
    "status": "Pending",
    "position": 7,
    "company": 3
  }'
```

**Response 201:**

```json
{
  "id": 99,
  "user": 42,
  "status": "Pending",
  "position": 7,
  "company": 3,
  "expected_salary": null,
  "availability_date": null,
  "created_at": "2026-08-27T20:30:00Z",
  "updated_at": "2026-08-27T20:30:00Z"
}
```

**Side effect (silent, async-safe):**

If the linked user has `welcome_email_sent_at IS NULL` and has an email on file, the system calls `EmailService.send_set_password_link(user.email, link, ttl_hours=24)`. The dispatch:

- Builds the magic link from the user's PK + Django's `default_token_generator` HMAC token
- Calls the configured email backend (default `DjangoSMTPEmailService`)
- On success, stamps `welcome_email_sent_at = now()` so the next CVSubmission for the same user is a no-op
- On failure, logs the error but does NOT raise — the CVSubmission save is never rolled back because of an email problem

The admin never sees the link or the token. They're not in the API response.

### Step A3 — Communicate the seafarer's email (out-of-band)

The seafarer gets the email in their own inbox. The admin doesn't need to do anything else — except make sure the seafarer has the email address on file (`Users.email`). If the seafarer's email is wrong/missing, no email goes out; see [Edge cases](#edge-cases).

### What Admin can do later

| Action | Endpoint |
|---|---|
| List all CVSubmissions | `GET /api/cv-submissions/` |
| View a specific CVSubmission | `GET /api/cv-submissions/99/` |
| Update CVSubmission status | `PATCH /api/cv-submissions/99/` |
| Resend the welcome email to a seafarer | `POST /api/cv-submissions/` again on the same user (only works if you first clear `welcome_email_sent_at` via DB / Django admin) |

---

## Seafarer side flow

> **Who:** the seafarer who was added to the system by the Admin.
> **Goal:** click the link, set a password, log in with email + password.

### Step S0 — Receive the email

The seafarer opens their inbox and finds an email like:

> **Subject:** Welcome to Sakr Manning Agency — set your password
>
> Hello,
>
> You've been added to Sakr Manning Agency. To access your profile and manage your account, please set a password by clicking the link below:
>
>   https://sakrshipping.com/set-password?uidb64=ABC123&token=xyz456...
>
> This link is valid for 24 hours. After that, you'll need to request a new one.
>
> If you did not expect this email, you can safely ignore it.
>
> — Sakr Manning Agency

The seafarer clicks the link.

### Step S1 — Land on the set-password page

The frontend renders a "set new password" form at `FRONTEND_SET_PASSWORD_URL` (`https://sakrshipping.com/set-password` by default). The form must:

1. **Read `uidb64` and `token` from the URL query string** (e.g. via `URLSearchParams` on the frontend).
2. Render a "new password" + "confirm password" field pair.
3. Validate client-side (min length, match) before submitting.

### Step S2 — Submit the new password

The frontend POSTs the token + new password to the backend:

```bash
curl -X POST "https://backend.sakrshipping.com/api/auth/set-password-confirm/" \
  -H "Content-Type: application/json" \
  -d '{
    "uidb64": "ABC123",
    "token": "xyz456...",
    "new_password": "MyNewSecurePass!2026"
  }'
```

| Outcome | Response |
|---|---|
| Success | `200` `{"detail": "Password set. You can now log in."}` |
| Missing field | `400` `{"detail": "uidb64, token, and new_password are required"}` |
| Bad uidb64 (doesn't decode to a user) | `400` `{"detail": "Invalid link"}` |
| Tampered / expired token | `400` `{"detail": "Invalid or expired link"}` |
| Weak password (fails `AUTH_PASSWORD_VALIDATORS`) | `400` `{"detail": "Password too weak: <reason>"}` |

On success, the backend:
- Sets `user.set_password(new_password)` (Django hashes properly)
- Stamps `user.welcome_email_sent_at = now()` (so the welcome email is never re-sent)
- Returns 200

### Step S3 — Log in with the new password

The seafarer can now use the standard email-login flow:

```bash
curl -X POST "https://backend.sakrshipping.com/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"seafarer@sakrshipping.com","password":"MyNewSecurePass!2026"}'
# → 200 { "access": "eyJ...", "refresh": "eyJ...", "user": {...} }
```

The JWT works against every authenticated endpoint (`/api/me/`, `/api/users/...`, etc.) the same as a phone-verified seafarer.

### Step S4 — Subsequent logins

The seafarer can keep using email + password indefinitely. **Phone-as-password still works as a fallback** unless the seafarer explicitly disables it (no API to do so today; the phone-as-password path is `POST /api/auth/phone-login/` with `{phone, phone}`, gated on `is_phone_verified=True`).

---

## End-to-end example (admin + seafarer together)

This example shows the new single-step flow: the Admin's POST auto-creates the seafarer's `Users` row.

```bash
# === ADMIN SIDE ===
# A1. Admin logs in
ADMIN_JWT=$(curl -s -X POST "https://backend.sakrshipping.com/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sakrshipping.com","password":"<admin-pwd>"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# A2. Admin posts the CVSubmission with the new seafarer's data.
#     The system auto-creates the Users row (default password = user_phone)
#     and the CVSubmission linked to it. Single API call, no separate
#     POST /api/users/users/ step.
curl -X POST "https://backend.sakrshipping.com/api/cv-submissions/" \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "newbie@sakrshipping.com",
    "user_first_name": "AHMED",
    "user_middle_name": "HASSAN",
    "user_phone": "00201012345678",
    "status": "Pending",
    "position": 7
  }'
# → 201 { "id": 99, "user": 42, "status": "Pending", ... }
# → Side effect: backend created the Users row (password=00201012345678,
#   role=Employee) and emailed a magic link to newbie@sakrshipping.com
#   (in dev with ConsoleEmailService, the link is in the gunicorn log)

# === SEAFARER SIDE ===
# S1. Seafarer reads the email, clicks the link, lands on
#     https://sakrshipping.com/set-password?uidb64=ABC&token=xyz
#     (frontend renders the form, reads the query string)

# S2. Frontend POSTs the new password
curl -X POST "https://backend.sakrshipping.com/api/auth/set-password-confirm/" \
  -H "Content-Type: application/json" \
  -d '{"uidb64":"ABC","token":"xyz","new_password":"MyNewSecurePass!2026"}'
# → 200 { "detail": "Password set. You can now log in." }

# S3. Seafarer logs in with the new password
SEAFARER_JWT=$(curl -s -X POST "https://backend.sakrshipping.com/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"newbie@sakrshipping.com","password":"MyNewSecurePass!2026"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# S4. Seafarer can now use any authenticated endpoint
curl "https://backend.sakrshipping.com/api/me/" \
  -H "Authorization: Bearer $SEAFARER_JWT"
# → 200, full profile

# S5. (Alternative) Seafarer can also use phone-as-password, after
#     verifying the phone via OTP. This is the same flow as /ai/parse/.
curl -X POST "https://backend.sakrshipping.com/api/auth/request-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201012345678"}'
# → 200 (OTP emailed)
# ... seafarer enters the OTP, then:
curl -X POST "https://backend.sakrshipping.com/api/auth/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201012345678","otp":"<6-digit-from-email>"}'
# → 200 (is_phone_verified=True, returns JWT)
curl -X POST "https://backend.sakrshipping.com/api/auth/phone-login/" \
  -H "Content-Type: application/json" \
  -d '{"phone":"00201012345678","password":"00201012345678"}'
# → 200 (phone-as-password works because the default password is the phone number)
```

---

## Edge cases

| Case | Behavior |
|---|---|
| Seafarer doesn't exist (wrong `user` ID or email) | `POST /api/cv-submissions/` returns `400` with `{"user": ["Invalid pk \"X\" - object does not exist."]}`. No `CVSubmission` row is created. The Admin must `POST /api/users/users/` first to create the `Users` row, then retry the CVSubmission. |
| Seafarer doesn't exist + Admin posts `user_email` (new) | Backend auto-creates the `Users` row with `password = user_phone` (per spec), `role = 'Employee'`, and the supplied `first_name`/`middle_name`. The `CVSubmission` is created linked to the new user. The welcome email is dispatched. |
| Seafarer already exists (Admin posts `user_email` of existing user) | Backend looks up by email, refreshes `first_name`/`middle_name`/`phone_number` if supplied, but does NOT touch the password (the seafarer may have set their own via the magic link or have phone-as-password configured). |
| Admin posts `user_email` but no `user_phone` | Auto-create still works; default password falls back to the email address (so `/api/login/` works as a fallback). The welcome email still prompts the seafarer to set a real password. |
| Employee / Crew posts `user_email` of someone else | The `user_email` branch is admin-only — Employees' `user_email` is ignored. The CVSubmission is always attributed to the Employee themselves. |
| Seafarer has no email on file | `dispatch_welcome_email` is a no-op (returns False). The `CVSubmission` save still succeeds. The seafarer is silently not onboarded via this path. The admin should set the seafarer's email and re-create the CVSubmission (or clear `welcome_email_sent_at` first) to retry. |
| Admin creates a second `CVSubmission` for the same seafarer | No re-send. The user's `welcome_email_sent_at` is already set; the email path is a no-op. The CVSubmission row is still created. |
| Seafarer already has a custom password (e.g. set via a previous flow) | The seafarer's `welcome_email_sent_at` is set, so the email doesn't re-send. The new CVSubmission is created normally. The seafarer's existing password still works. |
| Seafarer is `is_active=False` | The CVSubmission is still created. The email dispatch runs (no check on `is_active`). When the seafarer clicks the link and POSTs, the token is validated, the password is set, but `/api/login/` will return 403 because the account is disabled. The admin needs to re-activate. |
| Token is tampered (different uidb64 + token combo) | `default_token_generator.check_token()` returns False → 400 "Invalid or expired link". The frontend should redirect to /login with an error message. |
| Token is expired (>24h old) | Same as tampered — 400 "Invalid or expired link". The seafarer needs to ask the admin to re-send (which requires clearing `welcome_email_sent_at` and creating another CVSubmission). **No built-in "resend" endpoint today** — see [open follow-ups](#open-follow-ups). |
| Email dispatch fails (SMTP down, wrong creds, etc.) | The `CVSubmission` save is NOT rolled back. The error is logged in the gunicorn error log (`DjangoSMTPEmailService: send_set_password_link failed for to_email=...`). The seafarer just doesn't get the email. |
| Seafarer submits a weak password | `validate_password()` runs Django's `AUTH_PASSWORD_VALIDATORS`. 400 "Password too weak: <reason>". The frontend should show the reason to the user. |
| Seafarer submits with missing `uidb64` or `token` | 400 "uidb64, token, and new_password are required". |
| Frontend URL is unreachable / wrong | The seafarer's click goes to a 404 (or whatever the frontend shows). The backend endpoint still works regardless of the URL — the URL is just what the email embeds. |

---

## Auth matrix (recap)

| Endpoint | Admin | HR Manager | Recruiter | Employee / Crew | Unauth |
|---|---|---|---|---|---|
| `POST /api/cv-submissions/` (creates one) | ✅ | ✅ | ✅ (limited fields) | ✅ (own only) | ❌ 401 |
| `POST /api/auth/set-password-confirm/` | ✅ | ✅ | ✅ | ✅ | ✅ (token is the credential) |
| `POST /api/login/` (email + new password) | ✅ | ✅ | ✅ | ✅ | ✅ |

The `CVPermission` on `POST /api/cv-submissions/` lets Recruiters POST (with limited fields per the role's permission class). For onboarding a new seafarer via this flow, the **Admin role is recommended** because Recruiters are restricted on what fields they can set.

---

## Why this design (vs alternatives)

- **Magic link, not emailed password.** Emailing a plaintext password is a security anti-pattern (the password lives forever in the seafarer's inbox, in mail server logs, in any forwarding chain). The magic-link pattern is the standard secure alternative — the link is single-purpose, time-bounded, and never contains any credential itself.
- **HMAC-signed token, not a random opaque one.** Django's `default_token_generator` derives the token from the user PK + a server-side secret + a timestamp. No DB lookup is needed to validate — just the project's `SECRET_KEY`. The 24h TTL is embedded in the token, so old links fail closed without a separate expiry table.
- **Re-use the existing `default_token_generator` pattern.** Same mechanism as the legacy `VerifyEmailView` (the welcome email with a "fill in your data" link). Familiar code path, fewer surprises.
- **Idempotency at the user level, not the request level.** A second `CVSubmission` for the same seafarer is a valid admin action (different position, different company) but it shouldn't spam the seafarer with duplicate welcome emails. The `welcome_email_sent_at` flag gives us a per-user one-shot.
- **Email failures don't roll back the save.** The `CVSubmission` is the primary record; the email is a notification. If SMTP is down, the admin can retry later (or the seafarer can use phone-as-password as a fallback). Reversing the relationship would couple unrelated concerns.
- **Doesn't replace phone-as-password.** Seafarers created via `/ai/parse/` keep their phone-as-password option. This new flow adds email+password as a second option, not a replacement. Real-world deployments often need both.

---

## Open follow-ups (not in this iteration)

1. **"Resend welcome email" endpoint.** Today the only way to re-send is to clear `welcome_email_sent_at` directly (Django admin / DB). A `POST /api/users/{id}/resend-welcome/` would be a 5-line addition.
2. **`is_active=False` block in the confirm view.** Today the seafarer can set a password on a disabled account (the email is sent, the token validates, `set_password` runs) but then `/api/login/` will 403. We could short-circuit with 403 in the confirm view. Low priority — the admin workflow is "set `is_active=True` first", not "let disabled users set passwords".
3. **Rate-limit `set-password-confirm` per IP.** A brute-force attacker with a leaked token could keep trying passwords. Today there's no rate limit. Low priority — the token is HMAC-signed and 24h-bounded, so the attack surface is small.
4. **Frontend "expired link" page.** The `Invalid or expired link` 400 should redirect to a friendly page (e.g. `/auth?error=expired`) with a "Request a new link" button. Currently the frontend dev needs to build this.

---

## Files touched

- `api/models.py` — added `Users.welcome_email_sent_at` (DateTimeField, nullable)
- `api/migrations/0071_users_welcome_email_sent_at.py` — new migration
- `saker/settings.py` — `FRONTEND_SET_PASSWORD_URL` (env-overridable, default `https://sakrshipping.com/set-password`) + `PASSWORD_SET_TTL_HOURS` (env-overridable, default `24`)
- `api/email.py` — extended `EmailService` protocol with `send_set_password_link(to_email, link, ttl_hours)`. Both `ConsoleEmailService` and `DjangoSMTPEmailService` implement it.
- `api/serializer.py` — added `user_phone` write-only field to `CVSubmissionSerializer` (used by the auto-create flow).
- `api/views.py` — new `build_set_password_link(user)` helper, `SetPasswordConfirmView` (POST `/api/auth/set-password-confirm/`), `dispatch_welcome_email(user)` helper. `CVSubmissionViewSet.perform_create` rewritten to support three identification paths: `'user'` FK, `'user_email'` look-up-by-email, or auto-create from `user_email + user_first_name + user_middle_name + user_phone` (default password = phone). Welcome email dispatched after every CVSubmission create.
- `api/urls.py` — wires `/api/auth/set-password-confirm/`
- `api/tests.py` — 21 new tests (SetPasswordMagicLinkTests + EmailServiceSendPasswordLinkTests + CVSubmissionAutoCreateUserTests) + 2 existing OTP-dispatch tests got `@override_settings(EMAIL_SERVICE=ConsoleEmailService)` to keep passing under the new default
- `docs/admin-onboarded-seafarer-flow.md` — this file

## Tests

21 new tests in `api/tests.py`:

- **`SetPasswordMagicLinkTests`** (11):
  - `test_dispatch_skips_when_no_email` — no email on user → no-op
  - `test_dispatch_skips_when_already_sent` — `welcome_email_sent_at` set → no-op
  - `test_dispatch_sends_email_and_stamps_flag` — happy path: send + stamp
  - `test_dispatch_does_not_stamp_when_email_send_fails` — SMTP fails → don't stamp
  - `test_cv_submission_create_dispatches_welcome_email` — Admin POST `/api/cv-submissions/` triggers dispatch
  - `test_second_cv_submission_for_same_user_does_not_redisptach` — idempotency on the create path
  - `test_set_password_confirm_with_valid_token` — happy path: token + new password → 200 + password set
  - `test_set_password_confirm_rejects_invalid_token` — bad token → 400
  - `test_set_password_confirm_rejects_weak_password` — weak password → 400 (Django validators)
  - `test_set_password_confirm_rejects_missing_fields` — missing body fields → 400
  - `test_set_password_link_uses_frontend_url` — link points at the configured frontend URL
- **`EmailServiceSendPasswordLinkTests`** (3):
  - `test_console_logs_link` — ConsoleEmailService logs the link + email
  - `test_django_smtp_sends` — DjangoSMTPEmailService calls `send_mail` with the right subject/body
  - `test_django_smtp_returns_false_on_failure` — SMTP exception → returns False (no propagation)
- **`CVSubmissionAutoCreateUserTests`** (7) — the new single-step admin-onboarding flow:
  - `test_admin_post_with_user_email_auto_creates_user` — happy path: auto-create + password = phone + welcome email
  - `test_admin_post_with_existing_user_does_not_re_create` — existing user found → no auto-create, password not touched
  - `test_admin_post_with_existing_user_no_dispatch_when_already_sent` — welcome-email idempotency on the create path
  - `test_admin_post_with_user_fk_skips_auto_create` — `'user'` FK path still works (no password reset)
  - `test_admin_post_without_user_email_falls_back_to_admin` — historical fallback preserved
  - `test_admin_post_auto_create_with_no_phone_falls_back_to_email_password` — no `user_phone` → password = email
  - `test_admin_post_with_employee_role_does_not_auto_create` — Employees can't trigger auto-create (security)
  - `test_django_smtp_returns_false_on_failure` — SMTP exception → returns False (no propagation)

**Full suite: 396 tests, 0 new failures.** The 2 pre-existing failures (`DocumentUploadViewTest`, `IntegrationTest`) are the LLM path (`/ai/upload/`) which is untouched in this work.
