# Notifications

Automated email notifications for two key events:

1. **New Reminder** — when an admin/HR/Recruiter creates a `Reminder` for a crew member, an email is sent to the **admin who set it** (i.e. the request user) as a receipt / paper trail.
2. **New Expiring Document** — when an admin uploads a new `PersonalDocument` (passport, seaman's book, etc.), an email is sent to the **admin who uploaded it** as a receipt.

The crew member is NOT emailed in either case — per product decision these are admin-only notifications.

## How it works

- A new `notifications` app holds the email-sending service, signals, and tests.
- `core/threadlocals.py` + `core/middleware.py::CurrentUserMiddleware` mirror `request.user` into a thread-local so signal handlers can ask "who triggered this write?" without re-plumbing the request through every call site.
- `post_save` signals on `reminders.models.Reminder` and `api.models.PersonalDocument` call into `notifications.services` to send the email.
- All sends are best-effort: any exception is logged but never propagates back to the HTTP request, so a broken SMTP server cannot break the create flow.

## Email format

Plain text, multipart, sent via `django.core.mail.EmailMultiAlternatives` (HTML is optional and currently unused — text is the canonical body).

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
- **No admin user on the request** (e.g. an anonymous user, a Celery worker, a management command) — the thread-local actor is `None`, so the signal handler returns early and logs `no actor email; skipping ...`.
- **Admin user has no email address** — same: early return, no crash.

## When email fails

Any exception inside the send path is caught and logged via `logger.exception(...)` at the `notifications` logger. The HTTP request that triggered the write is unaffected; the reminder / document is still saved, only the notification is dropped.

To diagnose in production:

```bash
# tail the gunicorn / django log
tail -f /var/log/gunicorn/error.log | grep -i notifications
```

## Configuration

The standard Django email settings in `saker/settings.py` apply:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "mtechsaas@gmail.com"
EMAIL_HOST_PASSWORD = "..."   # Google app password
DEFAULT_FROM_EMAIL = "Sakr Manning Agency <crew@sakrshipping.com>"
```

For local development or tests, set:

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
| `saker/settings.py` | `MIDDLEWARE` wires `core.middleware.CurrentUserMiddleware` (after `AuthenticationMiddleware`); `INSTALLED_APPS` includes `notifications` |
| `notifications/services.py` | `send_reminder_notification`, `send_expiring_document_notification`, low-level `_send` |
| `notifications/signals.py` | `post_save` receivers for `Reminder` and `PersonalDocument` |
| `notifications/apps.py` | `ready()` imports `signals` so the receivers register |
| `notifications/tests.py` | 13 tests — all paths incl. e2e via DRF + locmem backend |
