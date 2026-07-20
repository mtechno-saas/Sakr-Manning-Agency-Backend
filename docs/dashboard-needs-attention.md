# Dashboard — "Needs Attention" Section

**Generated:** 2026-07-20
**Page:** Main dashboard (`/dashboard`)
**Purpose:** Surface pending documents that require admin/HR action

This document covers the **"Needs Attention"** widget on the main dashboard — the card that lists all pending documents so the logged-in admin/HR can quickly triage them.

---

## Section: Dashboard / Needs Attention

### Where it lives

- **Frontend route:** `/dashboard` (main page after login)
- **Component:** `src/components/dashboard/Components/Cards/StatCard.jsx` *(or whichever card component renders the list — see frontend codebase to confirm)*
- **Backend app:** `api` (the same app that handles users, CVs, and interviews)
- **Model:** `api.models.Document`
- **ViewSet:** `api.views.DocumentViewSet`
- **Serializer:** `api.serializers.DocumentSerializer`

### What the user sees

A card on the dashboard listing the count of pending documents and the most recent ones. Clicking a row opens the document detail (or downloads the file). The card auto-refreshes when the user clicks the refresh icon, or after a successful action elsewhere in the dashboard.

### What it shows

- Total count of documents with `status == "Pending"`
- List of recent pending documents (typically top 5–10)
- For each item: title, file name, uploader name, upload date, quick-action buttons (View / Approve / Reject)

---

## Endpoint 1: List pending documents

### Request

```http
GET https://backend.sakrshipping.com/api/documents/?page=1&status=Pending
Authorization: Bearer <jwt>
```

### Query parameters

| Param | Type | Required | Effect |
|---|---|---|---|
| `page` | int | No (default 1) | Page number for pagination |
| `status` | string (multi) | No (default: all) | One or more of `Pending`, `Approved`, `Rejected`. **Repeat the param for multiple**: `?status=Pending&status=Approved` |
| `name` | string | No | Substring match on `name` (case-insensitive) |
| `email` | string | No | Substring match on `email` (case-insensitive) |
| `position` | string | No | Substring match on `position` (case-insensitive) |
| `search` | string | No | Substring match on `name` **OR** `email` (whichever) |
| `page_size` | int | No | Override default page size |

### Response 200

```json
{
  "count": 27,
  "next": "https://backend.sakrshipping.com/api/documents/?page=2&status=Pending",
  "previous": null,
  "results": [
    {
      "id": 28,
      "name": "Capt. Sherif AbdelAleem",
      "email": "sherif.abdelaleem@example.com",
      "title": "CV — Sherif AbdelAleem",
      "position": "Chief Officer / Chief Mate",
      "status": "Pending",
      "file": "https://backend.sakrshipping.com/media/documents/cv_sherif_abdelaleem.pdf",
      "company": 12,
      "company_name": "Maersk Line Egypt",
      "job_position": 87,
      "user": 42,
      "created_at": "2026-07-19T14:23:00Z",
      "updated_at": "2026-07-19T14:23:00Z"
    }
  ]
}
```

### Field reference

| Field | Type | Notes |
|---|---|---|
| `id` | int | Document primary key — use for any "open detail" link |
| `name` | string | Uploader's display name (sometimes parsed from filename if missing) |
| `email` | string | Uploader's email — used for search and notifications |
| `title` | string | Document title (e.g. "CV — John Doe" or "Application — Master") |
| `position` | string (choice) | One of ~60+ maritime rank values, see model for the full list |
| `status` | string (choice) | `Pending` / `Approved` / `Rejected` |
| `file` | URL string | Absolute URL to the uploaded file (PDF or DOCX) |
| `company` | int (FK) | Optional link to the company the application is for |
| `company_name` | string (computed) | Resolved company name (read-only) |
| `job_position` | int (FK) | Optional link to a specific `JobOrderPosition` |
| `user` | int (FK) | The user who uploaded the document |
| `created_at` | datetime | Upload time |
| `updated_at` | datetime | Last change (e.g. status change) |

### Permissions

| Role | GET | POST | PUT/PATCH | DELETE |
|---|---|---|---|---|
| Anonymous | ❌ 401 | ✅ allowed (any user can upload) | ❌ 401 | ❌ 401 |
| Employee | ✅ (own only) | ✅ (for self) | ❌ 403 | ❌ 403 |
| Admin | ✅ all | ✅ | ✅ | ✅ |
| HR Manager | ✅ all | ✅ | ✅ | ✅ |
| Recruiter | ✅ all | ✅ | ✅ | ✅ |

⚠️ The `create` action is `AllowAny` in the current code — anyone, even unauthenticated users, can POST a document. This is a known issue for a public-facing form (the Apply Now button on the landing page) but it does mean unauthenticated users can upload. **Review whether this is intentional.**

### Pagination

Default page size is set in `REST_FRAMEWORK['PAGE_SIZE']` (likely 10 or 25). To get the full list without paging:

```bash
GET /api/documents/?status=Pending&page_size=1000
```

Or use the `next` URL until `next` is `null`.

---

## Endpoint 2: Search for a specific document (per-item detail)

The dashboard calls this **once per item** in the "Needs Attention" list, to fetch the full record for each pending document.

### Request

```http
GET https://backend.sakrshipping.com/api/documents/?search=28
Authorization: Bearer <jwt>
```

### What `search` does

`search` performs a case-insensitive substring match on **either** `name` **or** `email`. So:

- `?search=28` matches every document whose uploader name OR email contains "28"
- `?search=abdelaleem` matches every document with "abdelaleem" in name or email
- `?search=user28@example.com` matches that exact email if it exists

⚠️ The `search` param does **not** look up by document id. If "28" was meant as a document id, the right call is:

```bash
GET /api/documents/28/
```

### When to use which

| Intent | URL |
|---|---|
| Lookup by name or email fragment | `?search=<substring>` |
| Lookup by document id (the number 28 in your example) | `/api/documents/28/` |
| Lookup by uploader user id | `?user=42` |

If the frontend is calling `?search=28` to get a specific document, that's probably wrong. It would return a list of all documents whose uploader's name or email contains "28" (could be dozens), and the dashboard would render the wrong one. **The frontend should use `/api/documents/{id}/` for per-item lookups.**

### Response 200 (for `?search=28`)

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 28,
      "name": "Capt. user28",
      "email": "user28@example.com",
      ...
    },
    {
      "id": 41,
      "name": "John 28-Smith",
      "email": "j.smith@example.com",
      ...
    },
    {
      "id": 89,
      "name": "Crew Member 281",
      "email": "crew281@example.com",
      ...
    }
  ]
}
```

### Response 200 (for `/api/documents/28/`)

```json
{
  "id": 28,
  "name": "Capt. Sherif AbdelAleem",
  "email": "sherif.abdelaleem@example.com",
  "title": "CV — Sherif AbdelAleem",
  "position": "Chief Officer / Chief Mate",
  "status": "Pending",
  "file": "https://backend.sakrshipping.com/media/documents/cv_sherif_abdelaleem.pdf",
  ...
}
```

---

## How the dashboard uses these endpoints

### The full flow

```
1. Dashboard mounts
   └─→ GET /api/documents/?page=1&status=Pending
       Returns: { count: 27, results: [...10 items] }

2. For each item in results:
   └─→ GET /api/documents/?search=<something>
       (Currently looks up by name/email fragment — see warning above)
       Should be: GET /api/documents/{id}/

3. User clicks a row
   └─→ Open detail panel / modal
   └─→ GET /api/documents/{id}/

4. User clicks "Approve" or "Reject"
   └─→ PATCH /api/documents/{id}/  with { "status": "Approved" }
   └─→ Dashboard re-fetches list to update count
```

### Performance note (N+1)

The current flow does **1 list query + N search queries** (one per item). For 10 items, that's 11 requests. This is the classic N+1 problem. Better:

- ✅ Fetch the full payload in the list (already does — `?page_size=1000` if needed)
- ✅ Use `/api/documents/{id}/` for direct lookup, not `?search=`
- ✅ Or include the full record in a single list response and skip per-item fetches

---

## Known issues & gotchas

1. **Wrong detail endpoint** — `?search=28` is being used to fetch a specific document. This is a frontend bug; should be `/api/documents/28/`. May show the wrong document if multiple match the substring.

2. **Search uses name/email, not id** — no way to look up "document 28" via the search param. Add `id` to the search OR fix the frontend to use the detail endpoint.

3. **`create` is `AllowAny`** — unauthenticated users can POST documents. The `Apply Now` form on the landing page likely relies on this. If the form is internal-only, change `permission_classes` to `IsAuthenticated`.

4. **No role check on the list endpoint** — employees can see other employees' documents if the `get_queryset` doesn't filter. Verify it does.

5. **Status filter is multi-value** — `?status=Pending&status=Approved` returns both. The `?status=Pending` alone filters to just `Pending`. If the UI sends a single value, that's correct. If it builds an array, make sure to repeat the param, not pass JSON.

6. **Pagination is not enforced client-side** — the dashboard might assume "all results are here" when there are 27 total but only 10 returned. Always check `next` URL.

7. **Document files are at `/media/documents/...`** — requires nginx `location /media/` block to serve. **Make sure this is configured on production** (see `docs/bugs/` for the bug fix).

8. **Position choices are hardcoded** — there are ~60 maritime rank values in the model. Adding a new rank requires a model change + migration. There's no `get_positions` endpoint for this; the choices are statically defined.

---

## Related endpoints

| Endpoint | Use case |
|---|---|
| `GET /api/documents/?page=1&status=Pending` | List (this widget) |
| `GET /api/documents/{id}/` | Per-item detail (preferred over `?search=`) |
| `GET /api/documents/?search=<fragment>` | Search by name/email |
| `POST /api/documents/` | Upload (AllowAny — review!) |
| `PATCH /api/documents/{id}/` | Approve / Reject |
| `DELETE /api/documents/{id}/` | Remove |
| `GET /api/documents/?user=42` | All docs for a user |

---

## File locations

- **Backend model:** `api/models.py:905` (`class Document`)
- **Backend serializer:** `api/serializers.py:195` and `api/serializer.py:2538`
- **Backend view:** `api/views.py:1364` (`class DocumentViewSet`)
- **Backend URL:** `api/urls.py:57` (`router.register(r'documents', DocumentViewSet, basename="document")`)
- **Frontend card component:** `src/components/dashboard/Components/Cards/StatCard.jsx` *(verify in code)*

---

## Summary

The **"Needs Attention"** widget is straightforward:
- It calls `/api/documents/?page=1&status=Pending` to get the list
- It shows the count and a few recent items
- For each item, it should call `/api/documents/{id}/` for the full record (currently uses `?search=` which is buggy)

The main thing to fix is the per-item detail call. The current `?search=28` returns a paginated list of every uploader whose name/email contains "28", not the document with id 28.

---

## Expiring Documents — Aggregated Endpoint

A single endpoint that surfaces every expiring or expired document across all users. Combines the 9 expiry date fields stored on the `Users` model with the `PersonalDocument` table into one unified response.

This endpoint fills the gap left by `useDocumentExpiry.js`, which only checked `PersonalDocument` and ignored the 9 user-profile expiry fields.

### Endpoint

```
GET /api/users/expiring-documents/
```

### Auth

- **Bearer JWT required** (`IsAuthenticated`)
- **Role required:** `Admin` or `HR Manager` (returns `403 Forbidden` for everyone else)

### Query parameters

| Param | Type | Default | Effect |
|---|---|---|---|
| `days` | int | `30` | Look-ahead window in days (1–365) |
| `category` | string | *(none)* | Filter: `expired` / `critical` / `warning` / `notice` / `active` / `all` |

### Categories

| Category | Range | Meaning |
|---|---|---|
| `expired` | `daysToExpiry < 0` | Already past expiry date |
| `critical` | `0–14 days` | Renew immediately |
| `warning` | `15–30 days` | Plan renewal |
| `notice` | `31–90 days` | Heads up |
| `active` | `> 90 days` | Not flagged by this endpoint (only appears if you widen `days`) |

### Request examples

```bash
# All expired + expiring within 30 days (default)
GET /api/users/expiring-documents/

# Next 60 days
GET /api/users/expiring-documents/?days=60

# Only critical (next 14 days)
GET /api/users/expiring-documents/?category=critical

# Only already-expired
GET /api/users/expiring-documents/?category=expired
```

### Response 200

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
      "id": "user_42_passport_expiry_date",
      "type": "Passport",
      "name": "Passport - P12345678",
      "number": "P12345678",
      "user": "Mahmoud Ali",
      "userId": 42,
      "userEmail": "mahmoud@example.com",
      "expiryDate": "2026-07-22",
      "daysToExpiry": 2,
      "category": "critical",
      "source": "user_profile"
    },
    {
      "id": "pd_87",
      "type": "Schengen Visa",
      "name": "Schengen Visa - V-998877",
      "number": "V-998877",
      "user": "Sara Khaled",
      "userId": 51,
      "userEmail": "sara@example.com",
      "expiryDate": "2026-06-15",
      "daysToExpiry": -35,
      "category": "expired",
      "source": "personal_document"
    }
  ]
}
```

### Field reference

| Field | Type | Source | Notes |
|---|---|---|---|
| `id` | string | computed | Format: `user_<user_id>_<field>` or `pd_<doc_id>` |
| `type` | string | model | Human-readable doc type (e.g. "Passport", "COC") |
| `name` | string | computed | `<type> - <number>` |
| `number` | string | model | Document number (passport no, certificate no, etc.) or `N/A` |
| `user` | string | computed | Full name from `first_name last_name`, fallback to email |
| `userId` | int | model | FK to the user |
| `userEmail` | string | model | For follow-up emails |
| `expiryDate` | date | model | ISO 8601 (`YYYY-MM-DD`) |
| `daysToExpiry` | int | computed | Negative if expired |
| `category` | string | computed | One of the 5 categories above |
| `source` | string | computed | `user_profile` (from `Users` model) or `personal_document` (from `PersonalDocument` model) |

### Data sources covered

| User profile field (source: `user_profile`) | Document type |
|---|---|
| `passport_expiry_date` | Passport |
| `seaman_book_expiry_date` | Seaman's Book |
| `other_seaman_book_expiry_date` | Other Seaman's Book |
| `coc_expiry_date` | Certificate of Competency (COC) |
| `goc_expiry_date` | General Operator Certificate (GOC) |
| `health_expiry_date` | Health Certificate |
| `international_medical_expiry_date` | International Medical |
| `yellow_fever_expiry_date` | Yellow Fever Vaccination |
| `cholera_expiry_date` | Cholera Vaccination |

| PersonalDocument type (source: `personal_document`) | Notes |
|---|---|
| Passport, Seaman's Book, Schengen Visa, US Visa, etc. — **all 30 document types** in the `PersonalDocument.DOCUMENT_TYPE_CHOICES` | A user can have multiple rows of the same type, each with its own expiry |

### Errors

| Status | Body | When |
|---|---|---|
| `401` | `{ "detail": "Authentication credentials were not provided." }` | No / bad token |
| `403` | `{ "error": "Only Admin and HR Manager can view expiring documents." }` | Logged in as Employee / Recruiter |
| `500` | `{ "error": "...", "traceback": "..." }` | Server error (with traceback in debug mode) |

### How the dashboard uses this

The `useDocumentExpiry` hook can be simplified to call this one endpoint instead of aggregating 4. Recommended frontend refactor:

```js
// Before (4 parallel calls + manual aggregation)
const [personal, license, vaccine, contract] = await Promise.allSettled([...]);

// After (1 call)
const { data } = await api.get("/users/expiring-documents/?days=30");
// data.counts, data.results — both ready to render
```

### Backend locations

- **View function:** `api/views.py:2598` (`def expiring_documents`)
- **URL pattern:** `api/urls.py:104` (`path('expiring-documents/', expiring_documents, name='expiring-documents')`)
- **Full URL (after both mounts in `saker/urls.py` resolve):** `/api/users/expiring-documents/`
- **Why the inner path doesn't have a `users/` prefix:** `saker/urls.py` mounts `api/urls.py` at `path("api/users/", ...)` first, so any `users/...` inside `api/urls.py` would resolve to `/api/users/users/...` (double). The cleaner inner path `expiring-documents/` produces the correct full URL `/api/users/expiring-documents/`.

### Migration / deploy steps

No migration needed — pure view + URL change. To deploy:

```bash
ssh root@srv1080138
sudo systemctl restart gunicorn
# or, if using --reload workers:
sudo touch /opt/sakr/Sakr-Manning-Agency-Backend-New/saker/wsgi.py
```

### Verify

```bash
curl -H "Authorization: Bearer <admin-token>" \
  "https://backend.sakrshipping.com/api/users/expiring-documents/?days=30" \
  | python -m json.tool
```

Should return the full payload with `counts`, `days_window`, and `results` sorted by `daysToExpiry` ascending (most overdue first).

---

## All dashboard widget endpoints (summary)

| Widget | Endpoint | Method | Notes |
|---|---|---|---|
| Needs Attention — list | `/api/documents/?page=1&status=Pending` | GET | Paginated list of pending uploads |
| Needs Attention — per item | `/api/documents/{id}/` | GET | Full document (use id, not `?search=`) |
| **Expiring Documents** | **`/api/users/expiring-documents/`** | **GET** | **Single source for all 9 user-profile + 30 personal-doc types** |
| Expiring Documents (legacy) | `/users/personal-documents/`, `/my-licenses/`, `/vaccinations/`, `/contracts/` | GET × 4 | What `useDocumentExpiry` uses today — can be replaced by the new endpoint |
| Document stats | `/api/documents/?status=Pending&page_size=1` (count) | GET | For the "X items need attention" badge |
