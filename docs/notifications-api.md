# Notifications

Automated email notifications for two key events:

1. **New Reminder** — when an admin/HR/Recruiter creates a `Reminder` for a crew member, an email is sent to the **shared admin inbox** (`crew@sakrshipping.com`).
2. **New Expiring Document** — when an admin uploads a new `PersonalDocument` (passport, seaman's book, etc.), an email is sent to the **shared admin inbox** as well.

The recipient is a **single shared inbox** (configurable via `NOTIFICATIONS_ADMIN_EMAIL`). The whole team sees every notification in one place. The actor (the user who triggered the write) is recorded in the email body ("Hi <actor>, you set ...") for traceability.

The crew member the reminder / document is for is **NOT** emailed — per product decision these are admin-only.

## Recipient

```python
# saker/settings.py
NOTIFICATIONS_ADMIN_EMAIL = "crew@sakrshipping.com"
# or override via env var:
#   NOTIFICATIONS_ADMIN_EMAIL=alerts@sakrshipping.com
```

If the setting is missing or empty, the service logs a warning and silently skips the send — the HTTP request that triggered the write is still successful.

## How it works

- A new `notifications` app holds the email-sending service, signals, and tests.
- `core/threadlocals.py` + `core/middleware.py::CurrentUserMiddleware` mirror `request.user` into a thread-local so signal handlers can populate the email body with "Hi <actor>, you set ...".
- `post_save` signals on `reminders.models.Reminder` and `api.models.PersonalDocument` call into `notifications.services` to send the email.
- All sends are best-effort: any exception is logged but never propagates back to the HTTP request, so a broken SMTP server cannot break the create flow.

## Email format

Plain text, multipart, sent via `django.core.mail.EmailMultiAlternatives` (HTML is optional and currently unused — text is the canonical body).

**From:** `Sakr Manning Agency <crew@sakrshipping.com>` (set by `DEFAULT_FROM_EMAIL`)
**To:** the value of `NOTIFICATIONS_ADMIN_EMAIL`

Sample reminder email:

```
Subject: New reminder set for John Smith on 2026-09-15

Hi Admin Root,

You set a new reminder.

  For:   John Smith
  Date:  2026-09-15
  Time:  14:00
  Note:  Call John about joining date
  ID:    42

— Sakr Manning Agency (automated notification)
```

Sample expiring-document email:

```
Subject: New expiring document recorded: Passport for John Smith

Hi Admin Root,

You recorded a new expiring document.

  Crew member:  John Smith
  Document:     Passport
  Number:       X1234567
  Issued:       2025-01-01
  Expires:      2027-01-01
  Country:      Egypt
  ID:           17

— Sakr Manning Agency (automated notification)
```

## What does NOT trigger an email

- **Updates to existing Reminders or PersonalDocuments** — only the initial `created=True` post_save fires. Editing an existing row is silent.
- **`NOTIFICATIONS_ADMIN_EMAIL` is empty / not set** — the service logs a warning and skips the send. The data write still succeeds.

## When email fails

Any exception inside the send path is caught and logged via `logger.exception(...)` at the `notifications` logger. The HTTP request that triggered the write is unaffected; the reminder / document is still saved, only the notification is dropped.

To diagnose in production:

```bash
tail -f /var/log/gunicorn/error.log | grep -i notifications
```

## Configuration

```python
# saker/settings.py
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "mtechsaas@gmail.com"
EMAIL_HOST_PASSWORD = "..."   # Google app password
DEFAULT_FROM_EMAIL = "Sakr Manning Agency <crew@sakrshipping.com>"

NOTIFICATIONS_ADMIN_EMAIL = "crew@sakrshipping.com"  # or via env var
```

For local development or tests:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# or
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
```

`locmem` is what the test suite uses — emails accumulate in `django.core.mail.outbox` for assertion.

## File map

| File | Purpose |
|---|---|
| `core/threadlocals.py` | `set_current_user` / `get_current_user` / `clear_current_user` |
| `core/middleware.py` | `CurrentUserMiddleware` — mirrors `request.user` into the thread-local |
| `saker/settings.py` | `MIDDLEWARE` wires `core.middleware.CurrentUserMiddleware` (after `AuthenticationMiddleware`); `INSTALLED_APPS` includes `notifications`; `NOTIFICATIONS_ADMIN_EMAIL` is the shared recipient |
| `notifications/services.py` | `send_reminder_notification`, `send_expiring_document_notification`, low-level `_send`; recipient resolved from `NOTIFICATIONS_ADMIN_EMAIL` |
| `notifications/signals.py` | `post_save` receivers for `Reminder` and `PersonalDocument` |
| `notifications/apps.py` | `ready()` imports `signals` so the receivers register |
| `notifications/tests.py` | 15 tests — all paths incl. e2e via DRF + locmem backend |

