# Expiring Documents App — `expiring_documents/`

**Generated:** 2026-07-25
**App name:** `expiring_documents`
**Mount point:** `/api/expiring-documents/`
**Status:** New, replaces the previous function-based view in `api/views.py`

A focused Django app that aggregates every expiring or expired document across all users in a single endpoint. Pulls from two sources — the 9 expiry-date fields on the `Users` model, and the `PersonalDocument` table (30 document types) — and returns one unified, sorted, categorized list.

This document is the canonical reference for the app. If you're looking for the dashboard widget documentation (which uses this endpoint), see `docs/dashboard-needs-attention.md`.

---

## Table of Contents

1. [Why a separate app](#why-a-separate-app)
2. [App structure](#app-structure)
3. [Setup & install](#setup--install)
4. [The endpoint](#the-endpoint)
5. [Response shape](#response-shape)
6. [Categories](#categories)
7. [Query parameters](#query-parameters)
8. [Permissions](#permissions)
9. [Data sources](#data-sources)
10. [Examples](#examples)
11. [Testing](#testing)
12. [Migration from the old endpoint](#migration-from-the-old-endpoint)
13. [Future enhancements](#future-enhancements)

---

## Why a separate app

The previous implementation lived as a single function in `api/views.py:2598` with its URL in `api/urls.py:104`. That worked but had three problems:

1. **Mixed concerns.** The `api` app handles users, CVs, interviews, documents, etc. — 4,000+ lines of business logic. An aggregation function is a different kind of thing.
2. **Hard to test in isolation.** No `tests.py` for the old function; no way to run just the aggregation tests.
3. **Hard to extend.** When the team wants to add a scheduled job ("email admins every Monday with items expiring in 30 days"), it has nowhere natural to live.

A focused `expiring_documents` app solves all three: clean separation, its own test suite, and a home for future background tasks.

---

## App structure

```
E:\2-TECHNO AQUARE\expiring_documents\
├── __init__.py             # default_app_config = ExpiringDocumentsConfig
├── apps.py                 # ExpiringDocumentsConfig
├── models.py               # Empty (no DB models — pure aggregator)
├── serializers.py          # 3 serializers (item, counts, response wrapper)
├── views.py                # expiring_documents() function + 2 helpers
├── urls.py                 # /api/expiring-documents/
├── tests.py                # 4 smoke tests
└── migrations/
    └── __init__.py         # Empty — no migrations because no models
```

### File responsibilities

| File | Purpose |
|---|---|
| `__init__.py` | Default app config registration |
| `apps.py` | `ExpiringDocumentsConfig` class — registers the app with Django's app registry |
| `models.py` | Intentionally empty. The app doesn't add any tables; it only reads from `Users` and `PersonalDocument` |
| `serializers.py` | `ExpiringDocumentItemSerializer` (one row), `ExpiringDocumentsCountsSerializer` (counts by category), `ExpiringDocumentsResponseSerializer` (top-level wrapper) |
| `views.py` | The `expiring_documents()` function. ~250 lines including 2 helpers (`_categorize`, `_user_position`) and the field list `USER_EXPIRY_FIELDS` |
| `urls.py` | One URL pattern: `path("", views.expiring_documents, name="expiring-documents")` |
| `tests.py` | 4 smoke tests: auth required, role enforcement, response shape, expired item detection |
| `migrations/` | Empty package (no migrations because no models) |

### Dependencies on other apps

- `api.models.Users` — the 9 expiry fields and `user_ranks` reverse relation
- `api.models.PersonalDocument` — the 30 document types with their own `expiry_date`
- Django REST Framework — for `Response`, `status`, `@api_view`, `@permission_classes`
- Django ORM — `Q` objects, `prefetch_related`, `select_related`

That's it. No new third-party packages.

---

## Setup & install

### 1. Add to `INSTALLED_APPS`

In `saker/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'tickets_papers',
    'companies',
    'ships',
    'expiring_documents',  # <-- add this
    'core',
    # ... rest ...
]
```

### 2. Mount the URLs

In `saker/urls.py`:

```python
urlpatterns = [
    # ... existing patterns ...
    path("api/expiring-documents/", include("expiring_documents.urls")),
    # ... rest ...
]
```

### 3. No migration

The app has no models, so no migration is generated or required. Running `python manage.py makemigrations` after install will return "No changes detected."

### 4. Restart gunicorn

```bash
sudo systemctl restart gunicorn
```

### 5. Verify

```bash
curl -H "Authorization: Bearer <admin-token>" \
  "https://backend.sakrshipping.com/api/expiring-documents/?days=30" \
  | python -m json.tool | head -20
```

You should see a JSON payload with `counts`, `days_window`, `today`, `category_filter`, and `results`.

---

## The endpoint

### Request

```http
GET /api/expiring-documents/
GET /api/expiring-documents/?days=60
GET /api/expiring-documents/?category=critical
```

| Aspect | Value |
|---|---|
| Method | `GET` |
| URL | `/api/expiring-documents/` |
| Auth | Bearer JWT |
| Content-Type | `application/json` (response) |
| Cache | `expires 7d` (set on nginx for the underlying media — no app-level cache) |
| Pagination | None — single response with all matches |
| Idempotency | GET is naturally idempotent |
| Side effects | None (read-only) |

### Response codes

| Code | When | Body |
|---|---|---|
| `200` | Authenticated Admin/HR, valid params | Full payload |
| `400` | Invalid `days` (handled gracefully, defaults applied) | Always 200 actually — see `days` parameter note |
| `401` | No / bad token | `{ "detail": "Authentication credentials were not provided." }` |
| `403` | Logged in as Employee or Recruiter | `{ "error": "Only Admin and HR Manager can view expiring documents." }` |
| `500` | Server error | `{ "error": "...", "traceback": "..." }` (with `DEBUG=True`) |

---

## Response shape

```json
{
  "counts": {
    "expired": 2,
    "critical": 3,
    "warning": 5,
    "notice": 8,
    "active": 0,
    "total": 18
  },
  "days_window": 30,
  "today": "2026-07-20",
  "category_filter": "all",
  "results": [
    {
      "id": "user_42_coc_expiry_date",
      "type": "Certificate of Competency (COC)",
      "name": "Certificate of Competency (COC) - EAMS-12345",
      "number": "EAMS-12345",
      "user": "HISHAM HAMED HASSAN MOHAMED",
      "userId": 42,
      "userEmail": "hisham@example.com",
      "userPosition": "Able Seaman",
      "expiryDate": "2026-07-08",
      "daysToExpiry": -12,
      "category": "expired",
      "source": "user_profile"
    },
    {
      "id": "pd_87",
      "type": "Schengen Visa",
      "name": "Schengen Visa - V-998877",
      "number": "V-998877",
      "user": "ASLAM MOHAMED MOHAMED ABOURAGABR",
      "userId": 51,
      "userEmail": "aslam@example.com",
      "userPosition": "ABLE SEAFARER DECK",
      "expiryDate": "2026-08-12",
      "daysToExpiry": 17,
      "category": "warning",
      "source": "personal_document"
    }
  ]
}
```

### Top-level fields

| Field | Type | Description |
|---|---|---|
| `counts` | object | Counts of items per category, plus `total` |
| `counts.expired` | int | Items already past expiry date |
| `counts.critical` | int | Items expiring within 14 days (excluding expired) |
| `counts.warning` | int | Items expiring within 15–30 days |
| `counts.notice` | int | Items expiring within 31–90 days |
| `counts.active` | int | Items expiring in more than 90 days (only returned if `days >= 91`) |
| `counts.total` | int | Sum of all categories |
| `days_window` | int | The look-ahead window in days (echoed back from the request) |
| `today` | date | Server's current date in ISO 8601 (`YYYY-MM-DD`) |
| `category_filter` | string | Echoed from the request, or `"all"` if not provided |
| `results` | array | The list of expiring items, sorted by `daysToExpiry` ascending (most overdue first) |

### Per-item fields

| Field | Type | Source | Description |
|---|---|---|---|
| `id` | string | computed | Format: `user_<user_id>_<field>` or `pd_<doc_id>`. Stable across calls. |
| `type` | string | model | Human-readable doc type, e.g. `"Passport"`, `"Certificate of Competency (COC)"`, `"Schengen Visa"` |
| `name` | string | computed | `"{type} - {number}"` (e.g. `"Passport - P12345678"`) |
| `number` | string | model | Document number from the source. `"N/A"` if not set |
| `user` | string | computed | Full name (`first_name + middle_name`), falls back to email if empty |
| `userId` | int | model | Foreign key to the user |
| `userEmail` | string | model | The user's email (for follow-up notifications) |
| `userPosition` | string | computed | The user's most-recent rank name (e.g. `"Able Seaman"`, `"Master"`), `null` if no rank assigned |
| `expiryDate` | date | model | ISO 8601 (`YYYY-MM-DD`) |
| `daysToExpiry` | int | computed | Negative if expired, positive otherwise |
| `category` | string | computed | One of: `expired` / `critical` / `warning` / `notice` / `active` |
| `source` | string | computed | `user_profile` (from `Users` model) or `personal_document` (from `PersonalDocument` model) |

---

## Categories

The app buckets every item into one of 5 categories based on `daysToExpiry`:

| Category | Range | Color (UI) | Meaning |
|---|---|---|---|
| `expired` | `< 0` | red | Already past expiry date — renew immediately |
| `critical` | `0 – 14` days | red | Renew now |
| `warning` | `15 – 30` days | amber | Plan renewal |
| `notice` | `31 – 90` days | yellow | Heads up |
| `active` | `> 90` days | green | Not flagged by the default 30-day window; only appears when `days >= 91` |

These thresholds are defined in the `_categorize()` helper at the top of `views.py`. To change them, edit that single function and the rest of the app picks it up automatically.

---

## Query parameters

| Param | Type | Default | Range | Effect |
|---|---|---|---|---|
| `days` | int | `30` | `1 – 365` | Look-ahead window. Items with `expiry_date <= today + days` AND items already past `today` are included |
| `category` | string | *(all)* | `expired` / `critical` / `warning` / `notice` / `active` / `all` | Restrict results to one bucket |

### `days` parameter behavior

| Input | Result |
|---|---|
| not provided | `30` |
| `?days=` (empty) | `30` (defaults applied) |
| `?days=abc` (non-numeric) | `30` (defaults applied) |
| `?days=0` or negative | clamped up to `30` |
| `?days=400` | clamped down to `365` |
| `?days=60` | look 60 days ahead |

### `category` parameter behavior

| Input | Result |
|---|---|
| not provided | all categories included |
| `?category=` (empty) | all categories included |
| `?category=critical` | only items with `category == "critical"` |
| `?category=expired` | only items with `category == "expired"` |
| `?category=invalid` | 0 results (no error — see "Known quirks") |

The filter is **case-sensitive** — `?category=Critical` returns 0 results. Use lowercase only.

---

## Permissions

The endpoint uses a strict role-based check via `getattr(request.user, "role", None) in ("Admin", "HR Manager")`:

| Role | Access | Response on call |
|---|---|---|
| Anonymous | ❌ | `401 Unauthorized` |
| Employee | ❌ | `403 Forbidden` — `"Only Admin and HR Manager can view expiring documents."` |
| Recruiter | ❌ | `403 Forbidden` |
| Admin | ✅ | `200 OK` |
| HR Manager | ✅ | `200 OK` |
| Any other role (e.g. `Company Admin`, `Viewer`) | ❌ | `403 Forbidden` |

The check happens **after** authentication, so the error order is: bad/missing token → 401, valid token + wrong role → 403.

---

## Data sources

The app pulls from exactly two tables. The response `source` field tells you which one each item came from.

### Source: `user_profile` (from `Users` model)

| Backend field | Display type | Number field |
|---|---|---|
| `passport_expiry_date` | `Passport` | `passport_no` |
| `seaman_book_expiry_date` | `Seaman's Book` | `seaman_book_no` |
| `other_seaman_book_expiry_date` | `Other Seaman's Book` | `other_seaman_book_no` |
| `coc_expiry_date` | `Certificate of Competency (COC)` | `coc_certificate_number` |
| `goc_expiry_date` | `General Operator Certificate (GOC)` | `goc_certificate_number` |
| `health_expiry_date` | `Health Certificate` | `health_number` |
| `international_medical_expiry_date` | `International Medical` | `international_medical_number` |
| `yellow_fever_expiry_date` | `Yellow Fever Vaccination` | `yellow_fever_number` |
| `cholera_expiry_date` | `Cholera Vaccination` | *(no number field)* |

This is the **9 expiry-date fields** stored directly on the user profile. Each user has at most one of each field, so this returns at most 9 items per user.

### Source: `personal_document` (from `PersonalDocument` model)

A user can have **any number of PersonalDocument rows** — one per document. Common ones:
- Passport (separate from the `passport_no` on the user profile)
- Seaman's Book (separate from `seaman_book_no`)
- Schengen Visa, US Visa C1/D, US Visa B1/B2
- Bahamas Seaman's Book, Liberian Seaman's Book, UK Seaman's Book
- All 30 document types in `PersonalDocument.DOCUMENT_TYPE_CHOICES`

This is where the **appended expiry dates** live — things like visas and country-specific seaman books that don't have a fixed field on the user profile.

---

## Examples

### Basic call (defaults)

```bash
curl -H "Authorization: Bearer <admin-token>" \
  "https://backend.sakrshipping.com/api/expiring-documents/"
```

Returns all expired + expiring items within 30 days.

### Wider window

```bash
curl -H "Authorization: Bearer <admin-token>" \
  "https://backend.sakrshipping.com/api/expiring-documents/?days=90"
```

Returns everything expiring within 90 days, including the `notice` bucket.

### Only expired (already past)

```bash
curl -H "backend.sakrshipping.com/api/expiring-documents/?category=expired"
```

Returns only items where `expiry_date < today`. Useful for a "needs immediate action" list.

### Only critical (next 14 days)

```bash
curl -H "Authorization: Bearer <admin-token>" \
  "https://backend.sakrshipping.com/api/expiring-documents/?category=critical"
```

Returns items with `0 <= daysToExpiry <= 14`. Note: this excludes already-expired items. To get both, use `?category=expired` and `?category=critical` separately and merge.

### From the frontend

```js
import api from "@/services/Auth/api";

const { data } = await api.get("/expiring-documents/?days=30");
const { counts, results } = data;

// Show in the dashboard
results.forEach(item => {
  // item.user, item.type, item.daysToExpiry, item.category
});
```

---

## Testing

The app includes 4 smoke tests in `tests.py`. Run with:

```bash
cd /opt/sakr/Sakr-Manning-Agency-Backend-New
python manage.py test expiring_documents
```

Or with pytest if configured:

```bash
pytest expiring_documents/
```

### What's covered

| Test | Asserts |
|---|---|
| `test_endpoint_requires_auth` | Anonymous requests get 401 or 403 |
| `test_endpoint_rejects_employee_role` | User with `role="Employee"` gets 403 |
| `test_endpoint_returns_counts` | Response has `counts`, `results`, `days_window`, `today`, `category_filter` |
| `test_expired_passport_is_returned` | Setting `passport_expiry_date` to 5 days ago causes it to appear in the expired bucket |

### What's NOT covered (yet)

- The `category` parameter filtering
- The `userPosition` field accuracy for users with multiple ranks
- The 9 user-profile fields other than passport
- The 30 PersonalDocument types
- Pagination (not implemented; would be a future addition)
- 1–365 boundary enforcement on `days`
- 500 error path

These can be added incrementally. The current tests are enough to catch the most common regression: the endpoint being unreachable.

---

## Migration from the old endpoint

If you're upgrading from the previous version (where this lived in `api/views.py` and `api/urls.py`):

### What changed

| Before | After |
|---|---|
| Endpoint at `/api/users/expiring-documents/` | Endpoint at `/api/expiring-documents/` |
| View in `api/views.py:2598` | View in `expiring_documents/views.py` |
| URL in `api/urls.py:104` | URL in `expiring_documents/urls.py` |
| No serializers | 3 serializers in `expiring_documents/serializers.py` |
| No tests | 4 smoke tests in `expiring_documents/tests.py` |
| Single `name` field | `name` + new `userPosition` field (the user's most-recent rank) |

### What you need to do

1. **Pull the new code** — this includes the new `expiring_documents/` app and the changes to `saker/urls.py`, `saker/settings.py`, `api/views.py`, `api/urls.py`.

2. **Update the frontend URL**:
   - Find every occurrence of `/api/users/expiring-documents/` (or just `/users/expiring-documents/`) in the frontend code
   - Replace with `/api/expiring-documents/` (or just `/expiring-documents/`)
   - The response shape is the same, so no other code changes are needed

3. **Restart gunicorn** so the URL routing picks up the new app

4. **Verify the new URL works**:
   ```bash
   curl -H "Authorization: Bearer <admin-token>" \
     "https://backend.sakrshipping.com/api/expiring-documents/?days=30"
   ```

5. **Update your docs** — anywhere that referenced the old URL or file locations

The old URL `/api/users/expiring-documents/` will return **404** after this change. Plan a brief coordinated deploy if both frontend and backend need to update at the same time.

---

## Future enhancements

The app is intentionally minimal. These are the natural next steps if/when needed:

1. **Pagination** — the current response can be large for fleets with 5,000+ crew. Add `?page=1&page_size=50` using DRF's `PageNumberPagination`.
2. **Per-user endpoint** — add `/api/expiring-documents/by-user/<id>/` so the user-detail page can show just one user's expiring docs.
3. **Scheduled email job** — use the same logic in a Celery beat task to email admins every Monday with a summary. The view function is already structured to make this trivial.
4. **Slack/Teams webhook** — same idea, different transport.
5. **Filter by source** — add `?source=user_profile` or `?source=personal_document` to see only one table's items.
6. **Filter by user role** — let a Recruiter see only their assigned candidates' docs (more complex; requires per-user filtering).
7. **CSV export** — add a `?format=csv` to return a downloadable spreadsheet.
8. **Custom thresholds** — let each company configure when items become `critical` vs `warning` (e.g. for a 6-month vs 5-year visa).

None of these require a model change or migration — they all live in the view function.

---

## File locations reference

| File | Path |
|---|---|
| App folder | `E:\2-TECHNO AQUARE\expiring_documents\` |
| View function | `expiring_documents/views.py` |
| URL pattern | `expiring_documents/urls.py` |
| Serializers | `expiring_documents/serializers.py` |
| App config | `expiring_documents/apps.py` |
| Tests | `expiring_documents/tests.py` |
| URL mount | `saker/urls.py` (line 43 — `path("api/expiring-documents/", include("expiring_documents.urls"))`) |
| INSTALLED_APPS | `saker/settings.py` (added between `ships` and `core`) |

---

## Cross-references

- **Dashboard widget** that calls this endpoint: see `docs/dashboard-needs-attention.md` → "Expiring Documents" section
- **Related data models**: `Users` and `PersonalDocument` in `api/models.py`
- **Dashboard bug fix** that prompted this work: see `docs/bugs/bugs.pdf`
- **API contract** (full reference): see `docs/backend-documentation.md`
