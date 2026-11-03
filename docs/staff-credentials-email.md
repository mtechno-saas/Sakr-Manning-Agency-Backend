# Staff credentials — random password, emailed to the user

**When:** an admin promotes an applicant to a staff role (Admin / HR Manager /
Recruiter), or creates a staff account directly from the dashboard's add-user form.

**What happens:**

1. A random **8-digit** password is generated (`secrets.randbelow` — cryptographically
   unpredictable).
2. It becomes the account's password.
3. It is emailed to the account holder.

The plaintext password is transmitted by email only. It is never returned in an API
response, never written to a log line, and never stored anywhere but the bcrypt hash on
the user row.

**Replaces:** the shared hard-coded password `admin123!`, which was handed to every staff
account without one. That value was in the repository's git history and gave nobody
per-person accountability.

---

## Rules

| Situation | Password | Email |
|---|---|---|
| Account has **no** usable password | generated 8-digit random | sent |
| Account **already has** a password | kept as-is | **not sent** |
| An explicit `password` in the request | that one is used | **not sent** |
| Promotion to a **non-staff** role | none is set | not sent |
| The email **fails** | still generated and set | reported as failed |

The account always ends up usable — a mail failure never rolls the promotion back.

> An account created from the dashboard's add-user form has **no password at all**: that
> form has no password field. That is why the password has to be provisioned at the moment
> of the promotion.

---

## Response fields

On the response of the request that performed the promotion (or created the account):

```json
{
  "staff_credentials_sent": true,
  "staff_credentials_email": "amro@sakrshipping.com",
  "staff_credentials_role": "HR Manager",
  "staff_credentials_email_service": "api.email.DjangoSMTPEmailService"
}
```

The bulk-edit action returns the same information:

```json
{
  "message": "Successfully updated 1 users",
  "staff_credentials_emailed": 1,
  "staff_credentials_sent": true,
  "staff_credentials_email_service": "api.email.DjangoSMTPEmailService"
}
```

### Read `staff_credentials_email_service` carefully

| Value | Meaning |
|---|---|
| `api.email.DjangoSMTPEmailService` | **Real email.** Sent via Gmail SMTP. |
| `api.email.ConsoleEmailService` | **Not delivered.** The message was only written to the server log — but the backend still reports success, because that backend cannot fail. |

`staff_credentials_sent` is `true` in the console case too, so the service name is the
only way to tell. The backend also logs a warning when the console backend is active.

---

## Verify the email path BEFORE relying on it

`EMAIL_SERVICE` defaults to `DjangoSMTPEmailService`, but the production `.env` can
override it to the console backend — in which case nothing is ever delivered.

### 1. Which backend is active?

```bash
cd /opt/sakr/Sakr-Manning-Agency-Backend
venv/bin/python3 manage.py shell -c "
from api.email import get_email_service
svc = get_email_service()
print('service :', type(svc).__module__ + '.' + type(svc).__name__)
"
```

If it prints `api.email.ConsoleEmailService`, the emails only go to the server log.
Fix it by setting the real backend in the production `.env`:

```
EMAIL_SERVICE=api.email.DjangoSMTPEmailService
```

and restarting gunicorn.

### 2. Does SMTP actually deliver?

```bash
venv/bin/python3 manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
print('backend:', settings.EMAIL_BACKEND, '| host:', settings.EMAIL_HOST, '| from:', settings.DEFAULT_FROM_EMAIL)
try:
    send_mail('Sakr test', 'Email delivery is working.', settings.DEFAULT_FROM_EMAIL, ['crew@sakrshipping.com'], fail_silently=False)
    print('SMTP OK')
except Exception as e:
    print('SMTP FAILED:', type(e).__name__, e)
"
```

A Gmail App Password is used (`EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` in
`saker/settings.py`). Free Gmail accounts are capped at **~500 sends/day** — if the agency
starts hitting that, move to SendGrid / SES.

### 3. Past failures

The SMTP failures are swallowed by the email service (it returns `False` and logs the
exception). Look for them in the gunicorn error log:

```bash
grep -iE 'send_mail|SMTP|AuthenticationFailed|staff_credentials' /var/log/gunicorn/error.log | tail -30
```

---

## Rotating the accounts that still carry the old shared password

Accounts created **before** this change keep whatever password they had. To rotate one,
PATCH it with an explicit password (the API accepts a `password` field on the user
endpoint):

```bash
curl -s -X PATCH "https://backend.sakrshipping.com/api/users/users/73/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "<new-strong-password>"}'
```

An explicit password is used as-is and **no email is sent** — the admin knows the value.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No email arrives | `EMAIL_SERVICE` is the console backend | set it to `DjangoSMTPEmailService` in `.env`, restart gunicorn |
| No email arrives | Gmail rejected it / daily cap reached | check `/var/log/gunicorn/error.log` |
| `staff_credentials_sent: false` | the email service returned False or raised | check the gunicorn error log; set an explicit password by hand |
| Person cannot log in after the promotion | the promotion email failed **and** nobody set a password | PATCH the user with an explicit password (above) |
| Old password still works after promoting | the account already had a password, so it was deliberately kept | PATCH an explicit password if the old one must be retired |
