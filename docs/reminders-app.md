# Reminders App — `reminders/`

**Generated:** 2026-07-25
**App name:** `reminders`
**Mount point:** `/api/reminders/`
**Status:** New, replaces the previous implementation in `interviews/`

A focused Django app for per-user reminders. The admin picks a crew member from a dropdown, writes the reminder text, sets a date and time, and the reminder appears in that user's view of the Interviews section. Other users can only see their own reminders.

This document is the canonical reference for the app.

---

## Table of Contents

1. [Why a separate app](#why-a-separate-app)
2. [App structure](#app-structure)
3. [Setup & install](#setup--install)
4. [The model](#the-model)
5. [The endpoints](#the-endpoints)
6. [CRUD reference](#crud-reference)
7. [Custom actions](#custom-actions)
8. [Request / response shape](#request--response-shape)
9. [Permissions](#permissions)
10. [Examples](#examples)
11. [Testing](#testing)
12. [Migration from the old endpoint](#migration-from-the-old-endpoint)
13. [Future enhancements](#future-enhancements)
14. [File locations reference](#file-locations-reference)

---

## Why a separate app

The previous Reminder implementation lived in the `interviews` app:
- `interviews/models.py:Reminder`
- `interviews/serializers.py:ReminderSerializer`
- `interviews/views.py:ReminderViewSet`
- `interviews/urls.py` (router registered at `r'reminders'`)
- Migrations: `interviews/migrations/0002_reminder.py`

That worked, but the Interviews app is already large (interviews + document + CV submission logic). Reminders aren't really about interviews — they're about a user (any user, not just interview candidates). Two problems with the old setup:

1. **Wrong home.** Reminders are user-scoped, not interview-scoped. A reminder can be for any crew member for any reason, not just interview-related.
2. **Awkward URL.** `/api/interviews/reminders/` implies reminders belong to the interviews domain. `/api/reminders/` is cleaner.

This new app fixes both: the reminder is its own resource, and the URL is its own namespace.

---

## App structure

```
E:\2-TECHNO AQUARE\reminders\
├── __init__.py
├── apps.py                  # RemindersConfig
├── models.py                # Reminder (single model)
├── serializers.py           # ReminderSerializer
├── views.py                 # ReminderViewSet (CRUD + 4 custom actions)
├── urls.py                  # /api/reminders/ (DefaultRouter)
├── admin.py                 # Django admin registration
├── tests.py                 # 9 smoke tests
└── migrations/
    ├── __init__.py
    └── 0001_initial.py      # creates the `reminders_reminder` table
```

### File responsibilities

| File | Purpose |
|---|---|
| `models.py` | The single `Reminder` model: user, text, date, time, is_completed, timestamps |
| `serializers.py` | `ReminderSerializer` with read-only computed fields (`user_name`, `user_email`, `is_overdue`) and validation |
| `views.py` | `ReminderViewSet` (ModelViewSet) with role-based queryset scoping and 4 custom actions (`upcoming`, `overdue`, `mark_done`, `mark_pending`) |
| `urls.py` | DefaultRouter registration — exposes the full CRUD + the custom actions as named routes |
| `admin.py` | Django admin: list view with filters, search, date hierarchy |
| `tests.py` | 9 smoke tests: auth, role scoping, CRUD, validation, custom actions |
| `migrations/0001_initial.py` | Creates the `reminders_reminder` table |

### Dependencies on other apps

- `django.contrib.auth` — for `settings.AUTH_USER_MODEL` (the `Users` model in this project)
- Django REST Framework — for `ModelViewSet`, `DefaultRouter`, etc.
- `django.utils.timezone` — for the `is_overdue` calculation and the `upcoming` filter

No new third-party packages. No dependency on `interviews` or `companies` (a reminder is a self-contained user-scoped thing).

---

## Setup & install

### 1. Add to `INSTALLED_APPS`

In `saker/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'expiring_documents',
    'reminders',  # <-- add this
    # ... rest ...
]
```

### 2. Mount the URLs

In `saker/urls.py`:

```python
urlpatterns = [
    # ... existing patterns ...
    path("api/reminders/", include("reminders.urls")),
    # ... rest ...
]
```

### 3. Apply the migration

```bash
python manage.py migrate reminders
```

Expected:
```
Running migrations:
  Applying reminders.0001_initial... OK
```

### 4. (Optional) Register the admin

Already done in `reminders/admin.py`. Visit `https://backend.sakrshipping.com/admin/reminders/reminder/` to manage reminders via the Django admin (you'll need a superuser login).

### 5. Restart gunicorn

```bash
sudo systemctl restart gunicorn
```

### 6. Verify

```bash
curl -H "Authorization: Bearer <admin-token>" \
  "https://backend.sakrshipping.com/api/reminders/" \
  | python -m json.tool
```

---

## The model

```python
class Reminder(models.Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='reminders')
    text = TextField(help_text='Reminder message / details')
    reminder_date = DateField()
    reminder_time = TimeField()
    is_completed = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Field reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | int (auto) | auto | Primary key |
| `user` | FK to `Users` | ✅ yes | Who the reminder is for. The form's "Crew Member" dropdown |
| `text` | text | ✅ yes | The reminder message body |
| `reminder_date` | date (`YYYY-MM-DD`) | ✅ yes | When the reminder fires |
| `reminder_time` | time (`HH:MM:SS`) | ✅ yes | What time on that date |
| `is_completed` | bool | no (default `false`) | Mark `true` when the user acts on the reminder |
| `created_at` | datetime | auto | Server timestamp on create |
| `updated_at` | datetime | auto | Server timestamp on every save |

### Database table

- Table name: `reminders_reminder`
- Ordering: `reminder_date ASC, reminder_time ASC` (soonest first)

### Reverse relation

Each `Users` row has a `.reminders` reverse manager. So to get all reminders for a user:

```python
user.reminders.all()
```

---

## The endpoints

All endpoints require Bearer JWT auth.

### CRUD

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/reminders/` | List reminders visible to the caller |
| POST | `/api/reminders/` | Create a new reminder |
| GET | `/api/reminders/{id}/` | Retrieve one reminder |
| PUT | `/api/reminders/{id}/` | Full update (all required fields) |
| PATCH | `/api/reminders/{id}/` | Partial update (any subset) |
| DELETE | `/api/reminders/{id}/` | Delete the reminder |

### Custom actions

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/reminders/upcoming/` | Reminders for today or later, not yet completed |
| GET | `/api/reminders/overdue/` | Past-due, not yet completed |
| POST | `/api/reminders/{id}/mark_done/` | Flip `is_completed` to `true` |
| POST | `/api/reminders/{id}/mark_pending/` | Flip `is_completed` back to `false` |

---

## CRUD reference

### List — `GET /api/reminders/`

- Returns paginated list (DRF default pagination)
- Scoped by role (see [Permissions](#permissions)):
  - **Admin / HR Manager / Recruiter**: all reminders
  - **Other users**: only their own

### Create — `POST /api/reminders/`

**Required:** `user`, `text`, `reminder_date`, `reminder_time`
**Optional:** `is_completed` (default `false`)

**Body example:**
```json
{
  "user": 42,
  "text": "Renew Schengen visa before trip",
  "reminder_date": "2026-08-15",
  "reminder_time": "10:00:00"
}
```

**The `user` field accepts both `int` and `string-int`** so the frontend can submit a `<select>` value as-is:

| Input | Result |
|---|---|
| `{"user": 42}` | ✅ accepted, resolved to `Users.objects.get(pk=42)` |
| `{"user": "42"}` | ✅ accepted, coerced to int, then `Users.objects.get(pk=42)` |
| `{"user": "not-a-number"}` | ❌ 400, "Invalid pk \"not-a-number\"" |
| `{"user": 99999}` | ❌ 400, pk does not exist |

This is implemented via a small custom field class, `UserFlexiblePrimaryKeyRelatedField` in `serializers.py`. The field is read as an integer on output (the standard FK representation), but tolerates a string on input — common when the form value comes from `<option value="42">`.

**Response 201:**
```json
{
  "id": 17,
  "user": 42,
  "user_name": "HISHAM HASSAN MOHAMED",
  "user_email": "hisham@example.com",
  "text": "Renew Schengen visa before trip",
  "reminder_date": "2026-08-15",
  "reminder_time": "10:00:00",
  "is_completed": false,
  "is_overdue": false,
  "created_at": "2026-07-25T10:00:00Z",
  "updated_at": "2026-07-25T10:00:00Z"
}
```

**Errors:**
- `400` if any required field is missing
- `401` if no / bad token
- `403` if not Admin/HR/Recruiter AND trying to set `user` to someone else (the `perform_create` method forces `user=request.user` for non-privileged callers)

### Retrieve — `GET /api/reminders/{id}/`

Returns the full reminder object. Users can only retrieve their own reminders; admins retrieve any.

### Update — `PUT /api/reminders/{id}/` and `PATCH /api/reminders/{id}/`

**PATCH example** (most common — change one field):
```json
{ "is_completed": true }
```

**PUT** requires all fields.

### Delete — `DELETE /api/reminders/{id}/`

Returns `204 No Content` on success.

---

## Custom actions

### `GET /api/reminders/upcoming/`

Reminders for today or later, `is_completed = false`, ordered by `reminder_date ASC, reminder_time ASC`.

Use case: a "Today & Upcoming" widget on the dashboard.

```bash
curl -H "Authorization: Bearer <token>" \
  https://backend.sakrshipping.com/api/reminders/upcoming/
```

Returns an array (not paginated — these are usually few in number).

### `GET /api/reminders/overdue/`

Past-due, `is_completed = false`, ordered by `reminder_date DESC, remider_time DESC` (most overdue first).

Use case: an "Overdue" badge with a count + a list of items.

### `POST /api/reminders/{id}/mark_done/`

Quick action: marks the reminder as completed. Returns the updated reminder object.

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  https://backend.sakrshipping.com/api/reminders/17/mark_done/
```

### `POST /api/reminders/{id}/mark_pending/`

Opposite of `mark_done` — flips `is_completed` back to `false`. Useful when a user dismissed a reminder by mistake.

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  https://backend.sakrshipping.com/api/reminders/17/mark_pending/
```

---

## Request / response shape

### Response item

```json
{
  "id": 17,
  "user": 42,
  "user_name": "HISHAM HASSAN MOHAMED",
  "user_email": "hisham@example.com",
  "text": "Renew Schengen visa before trip",
  "reminder_date": "2026-08-15",
  "reminder_time": "10:00:00",
  "is_completed": false,
  "is_overdue": false,
  "created_at": "2026-07-25T10:00:00Z",
  "updated_at": "2026-07-25T10:00:00Z"
}
```

### Field reference

| Field | Type | Source | Description |
|---|---|---|---|
| `id` | int | model | Primary key |
| `user` | int | model | FK to `Users.id` |
| `user_name` | string | computed | Full name (`first_name middle_name`), fallback to email/username |
| `user_email` | string | model | `user.email` |
| `text` | string | model | The reminder body |
| `reminder_date` | date | model | `YYYY-MM-DD` |
| `reminder_time` | time | model | `HH:MM:SS` |
| `is_completed` | bool | model | Server-managed boolean |
| `is_overdue` | bool | computed | `true` if `!is_completed && (date+time < now)` |
| `created_at` | datetime | model | Auto-set on create |
| `updated_at` | datetime | model | Auto-set on every save |

### List response (paginated)

```json
{
  "count": 12,
  "next": "https://backend.sakrshipping.com/api/reminders/?page=2",
  "previous": null,
  "results": [ ...items... ]
}
```

---

## Permissions

| Role | GET list | GET detail | POST | PATCH | DELETE |
|---|---|---|---|---|---|
| Anonymous | ❌ 401 | ❌ 401 | ❌ 401 | ❌ 401 | ❌ 401 |
| Employee | ✅ (own only) | ✅ (own only) | ✅ (forces user=self) | ✅ (own only) | ✅ (own only) |
| Recruiter | ✅ all | ✅ all | ✅ all | ✅ all | ✅ all |
| HR Manager | ✅ all | ✅ all | ✅ all | ✅ all | ✅ all |
| Admin | ✅ all | ✅ all | ✅ all | ✅ all | ✅ all |

### Scoping logic

The `get_queryset` method in `ReminderViewSet`:

```python
def get_queryset(self):
    user = self.request.user
    qs = Reminder.objects.select_related('user').all()
    privileged = getattr(user, 'role', None) in ('Admin', 'HR Manager', 'Recruiter')
    if not privileged:
        qs = qs.filter(user=user)
    return qs
```

Non-privileged users can only see and operate on their own reminders. They get a `404 Not Found` if they try to access someone else's reminder by ID (because the queryset filter excludes it).

### Create-time enforcement

```python
def perform_create(self, serializer):
    user = self.request.user
    privileged = getattr(user, 'role', None) in ('Admin', 'HR Manager', 'Recruiter')
    if privileged and 'user' in serializer.validated_data:
        serializer.save()
    else:
        serializer.save(user=user)  # Force ownership to self
```

A non-privileged user sending `{"user": <other_id>, ...}` will get their own ID substituted. This is a defensive layer on top of the queryset filter.

---

## Examples

### From the frontend (form submit)

```js
import api from "@/services/Auth/api";

// POST a new reminder
const response = await api.post("/reminders/", {
  user: selectedCrewMemberId,
  text: "Submit medical form",
  reminder_date: "2026-08-15",
  reminder_time: "10:00:00",
});
// response.data has the created reminder
```

### Mark done

```js
await api.post(`/reminders/${id}/mark_done/`);
```

### Get the user's upcoming list

```js
const { data } = await api.get("/reminders/upcoming/");
// data is an array of reminders for today or later, not yet completed
data.forEach(r => {
  // r.text, r.reminder_date, r.reminder_time, r.user_name
});
```

### Filter on the client

If the frontend wants only critical reminders, it can use the standard CRUD with a custom query:

```bash
# No backend filter — do it client-side
GET /api/reminders/upcoming/  # returns all upcoming
# Frontend filters to is_overdue === true
```

Or, for a different design, add a `category` filter to the backend (not implemented yet; tracked in "Future enhancements").

---

## Testing

The app includes 9 smoke tests in `tests.py`. Run with:

```bash
cd /opt/sakr/Sakr-Manning-Agency-Backend-New
python manage.py test reminders
```

Or with pytest:

```bash
pytest reminders/
```

### What's covered

| Test | Asserts |
|---|---|
| `test_anonymous_request_blocked` | No token → 401 or 403 |
| `test_employee_sees_only_own` | Employee can only see their own reminders |
| `test_admin_sees_all` | Admin can see all reminders |
| `test_create_reminder` | POST with all required fields returns 201 with the right data |
| `test_create_missing_required_field_fails` | POST with missing user/date/time returns 400 with errors per field |
| `test_patch_partial_update` | PATCH with one field updates only that field |
| `test_delete` | DELETE returns 204 and removes the row |
| `test_upcoming_action` | The `upcoming` action filters by date and `is_completed` |
| `test_mark_done` | The `mark_done` action sets `is_completed = true` |

### What's NOT covered (yet)

- The `overdue` and `mark_pending` actions
- The `is_overdue` computed field
- Cross-user access (admin vs employee permission boundaries)
- Date format edge cases (timezone, DST)
- Bulk operations

Add tests as needed; the current set covers the most common regressions.

---

## Migration from the old endpoint

If you're upgrading from the previous implementation (where Reminder was inside the `interviews` app):

### What changed

| Before | After |
|---|---|
| `interviews/models.py:Reminder` | `reminders/models.py:Reminder` |
| `interviews/serializers.py:ReminderSerializer` | `reminders/serializers.py:ReminderSerializer` |
| `interviews/views.py:ReminderViewSet` | `reminders/views.py:ReminderViewSet` |
| `interviews/urls.py` (router `r'reminders'`) | `reminders/urls.py` (DefaultRouter at `''`) |
| URL: `/api/interviews/reminders/` | URL: `/api/reminders/` |
| Migrations: `interviews/0002_reminder.py` | Migrations: `reminders/0001_initial.py` |
| Tables: `interviews_reminder` | Tables: `reminders_reminder` |
| No admin | Django admin registered |
| No tests | 9 smoke tests |
| Only `upcoming` action | 4 custom actions: `upcoming`, `overdue`, `mark_done`, `mark_pending` |
| `user_name` from `get_full_name()` | `user_name` from `first_name + middle_name` |

### What you need to do

1. **Pull the new code** (the `reminders/` app + the changes to `saker/`, `interviews/`).

2. **Apply the migration**:
   ```bash
   python manage.py migrate
   ```
   This will create the `reminders_reminder` table. It will NOT touch the old `interviews_reminder` table — that data is preserved.

3. **(Optional) Migrate old data to the new table**:
   ```sql
   INSERT INTO reminders_reminder (user_id, text, reminder_date, reminder_time, is_completed, created_at, updated_at)
   SELECT user_id, text, reminder_date, reminder_time, is_completed, created_at, updated_at
   FROM interviews_reminder;
   ```
   Then drop the old table if you're sure:
   ```sql
   DROP TABLE interviews_reminder;
   ```

4. **Update the frontend URL**:
   - Find every occurrence of `/api/interviews/reminders/` (or just `/interviews/reminders/`) in the frontend code
   - Replace with `/api/reminders/` (or `/reminders/`)
   - The response shape is mostly the same, but you now have `is_overdue` and a more reliable `user_name`

5. **Restart gunicorn** so the new URL routing takes effect

6. **Verify the new URL works**:
   ```bash
   curl -H "Authorization: Bearer <admin-token>" \
     "https://backend.sakrshipping.com/api/reminders/"
   ```

The old URL `/api/interviews/reminders/` will return **404** after this change.

---

## Future enhancements

Natural next steps if/when needed:

1. **Per-user notification** — when a reminder's date+time arrives, send an email or push notification to the user. Use Celery beat or a cron job.
2. **Recurring reminders** — add a `recurrence` field (daily/weekly/monthly) so the reminder auto-creates the next instance when marked done.
3. **Categories** — let the admin tag reminders as `medical`, `document`, `interview`, `payment`, etc., so the user can filter.
4. **Frontend "is_overdue" indicator** — the field is already in the response; just style it in the UI.
5. **Webhook on `mark_done`** — fire a Django signal to notify downstream systems.
6. **Attachment support** — let the admin attach a PDF (e.g. a form to fill out) to the reminder. Would need a new `attachment` field and a `FileField`.
7. **Bulk import** — admins often want to bulk-create reminders for a batch of crew (e.g. all visas expiring in Q4). A `POST /api/reminders/bulk/` with an array of payloads would do it.
8. **Calendar view** — add `?from=YYYY-MM-DD&to=YYYY-MM-DD` filtering for date-range queries, which makes a month-view calendar trivially renderable.
9. **Soft delete** — `is_deleted` + `deleted_at` instead of hard DELETE, so admins can recover.

None of these require breaking changes to the current API.

---

## File locations reference

| File | Path |
|---|---|
| App folder | `E:\2-TECHNO AQUARE\reminders\` |
| Model | `reminders/models.py` |
| Serializer | `reminders/serializers.py` |
| View | `reminders/views.py` |
| URL config | `reminders/urls.py` |
| Admin | `reminders/admin.py` |
| App config | `reminders/apps.py` |
| Tests | `reminders/tests.py` |
| Initial migration | `reminders/migrations/0001_initial.py` |
| URL mount | `saker/urls.py` (line 44 — `path("api/reminders/", include("reminders.urls"))`) |
| INSTALLED_APPS | `saker/settings.py` (added between `expiring_documents` and `core`) |
| Database table | `reminders_reminder` |

---

## Cross-references

- **Dashboard widget** that shows the "Add Reminder" modal: see the frontend's `src/components/dashboard/Components/Modal/ReminderModal.jsx` *(verify path)*
- **Hook that fetches reminders**: see `src/hooks/dashboard/useDocumentExpiry.js` (or a new `useReminders` hook if the team has split it)
- **Related data model**: `api.models.Users`
- **API contract** (full reference): see `docs/backend-documentation.md`
- **Older, now-moved implementation**: see `docs/dashboard-needs-attention.md` (the Reminders section there is now superseded)
