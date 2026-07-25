# Applicants Page — `/api/documents/` *(unfiltered)*

**Generated:** 2026-07-21
**Page:** Sidebar → **Applicants**
**Endpoint:** `GET /api/documents/?page=1`

The **Applicants** page on the dashboard is a separate page from the "Needs Attention" widget. It lists **all** uploaded documents regardless of status — not just `Pending`. This is the canonical "applicants list" the HR team browses.

---

## Endpoint

```http
GET https://backend.sakrshipping.com/api/documents/?page=1
Authorization: Bearer <token>
```

> **No `status` filter.** The Applicants page is meant to show every document. Filtering by `status=Pending` here would hide approved/rejected candidates and break the page.

---

## Why this is separate from "Needs Attention"

| Widget / Page | URL | Purpose |
|---|---|---|
| **Needs Attention** (dashboard card) | `/api/documents/?page=1&status=Pending` | Surface only pending items for the admin/HR to triage |
| **Applicants** (sidebar page) | `/api/documents/?page=1` | Show all candidates, any status, with their full state |

Both use the same `DocumentViewSet` and `DocumentSerializer` — only the query string differs.

---

## Query parameters

| Param | Type | Effect |
|---|---|---|
| `page` | int | Page number (default 1) |
| `page_size` | int | Override default page size |
| `status` | *(do not set)* | Would filter the list — wrong for this page |
| `name` | string | Substring match on `name` (case-insensitive) |
| `email` | string | Substring match on `email` (case-insensitive) |
| `position` | string | Substring match on `position` (case-insensitive) |
| `search` | string | Substring match on `name` OR `email` |

If the user needs to filter by status on this page, that should be a client-side filter on the response, not a server-side `status` query param.

---

## Sample response

```json
{
  "count": 247,
  "next": "https://backend.sakrshipping.com/api/documents/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Capt. Sherif AbdelAleem",
      "email": "sherif.abdelaleem@example.com",
      "title": "CV — Sherif AbdelAleem",
      "position": "Chief Officer / Chief Mate",
      "status": "Pending",
      "file": "https://backend.sakrshipping.com/media/documents/cv_sherif.pdf",
      "company": 12,
      "company_name": "Maersk Line Egypt",
      "user": 42,
      "created_at": "2026-07-19T14:23:00Z",
      "updated_at": "2026-07-19T14:23:00Z"
    },
    {
      "id": 2,
      "name": "Hassan Mohamed",
      "email": "hassan@example.com",
      "title": "CV — Hassan",
      "position": "Master",
      "status": "Approved",
      "..."
    }
  ]
}
```

Note the `status` field varies across items — this is **all** documents, not a status-filtered list.

---

## Field reference

| Field | Type | Notes |
|---|---|---|
| `id` | int | Document primary key |
| `name` | string | Uploader's display name |
| `email` | string | Uploader's email |
| `title` | string | Document title |
| `position` | string (choice) | Maritime rank (Master, Chief Officer, etc.) |
| `status` | string (choice) | `Pending` / `Approved` / `Rejected` (varies across results) |
| `file` | URL | Absolute URL to the uploaded PDF/DOCX |
| `company` | int (FK) | Optional link to the company |
| `company_name` | string (computed) | Resolved company name (read-only) |
| `user` | int (FK) | The uploader's user id |
| `created_at` | datetime | Upload time |
| `updated_at` | datetime | Last change |

For the full record (including `cover_letter`, `reviewed_by`, `notes`, etc. — fields the lightweight list doesn't include), use `GET /api/documents/{id}/`.

---

## Where it lives

- **Frontend route:** `/dashboard` → **Applicants** sidebar item (NOT the "Needs Attention" card)
- **Backend view:** `api.views.DocumentViewSet` (same viewset as Needs Attention)
- **Backend URL:** `/api/documents/` (router-registered)

---

## Frontend implementation note

Make sure the Applicants page's API call does **not** include `?status=...`. If the codebase has a shared `getDocuments()` service, check whether it hardcodes `?status=Pending` — if so, the Applicants page would inherit the wrong filter and show only pending items.

The fix is either:
1. A separate `getAllDocuments()` service that omits the `status` param, or
2. Pass `{ status: undefined }` (or omit the key) in the request config

### Common frontend bug to look for
```js
// BAD — inherited from the Needs Attention service
const response = await api.get("/documents/", { params: { status: "Pending" } });
//                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//                                  This would silently filter the Applicants page

// GOOD
const response = await api.get("/documents/");
// or
const response = await api.get("/documents/", { params: { page, page_size } });
```

---

## Permissions

Same as the DocumentViewSet:

| Role | GET | POST | PATCH | DELETE |
|---|---|---|---|---|
| Anonymous | ❌ 401 | ✅ (AllowAny) | ❌ 401 | ❌ 401 |
| Employee | ✅ (own only) | ✅ (for self) | ❌ 403 | ❌ 403 |
| Admin | ✅ all | ✅ | ✅ | ✅ |
| HR Manager | ✅ all | ✅ | ✅ | ✅ |
| Recruiter | ✅ all | ✅ | ✅ | ❌ 403 |

⚠️ The `create` action is `AllowAny` in the current code — anyone (even unauthenticated) can POST a document. This is intentional for the public "Apply Now" form on the landing page, but worth reviewing if the form is internal-only.

---

## Cross-references

- **Related widget** (status-filtered): see `dashboard-needs-attention.md` → "Needs Attention" section
- **Expiring docs from the same model:** `/api/expiring-documents/`
- **CV submissions (different model):** `/api/cv-submissions/`

---

## File locations

- **Backend model:** `api/models.py:905` (`class Document`)
- **Backend viewset:** `api/views.py:1364` (`class DocumentViewSet`)
- **Backend URL:** `api/urls.py:57` (`router.register(r'documents', DocumentViewSet, basename="document")`)
- **Frontend page:** `src/components/dashboard/Content/Applicants.jsx` *(verify exact path in code)*
- **Shared service (potential bug):** `src/services/Dashboard/documentsApi.js` or similar — check if it accepts a `status` param
