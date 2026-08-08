# Company Types API (Principal Types)

Endpoints for managing the canonical list of principal/company types
used as the `Company.company_type` choice and in the Add New Principal
form's Principal Type dropdown.

The frontend Settings → Dropdown Data → Principal Types tab is the
primary UI on top of this endpoint. The Add New Principal form's
Principal Type dropdown is currently a hardcoded list in the frontend
(see "Frontend consistency note" at the end).

---

## Base URL

```
https://backend.sakrshipping.com
```

## Auth

```
Authorization: Bearer <access_token>
```

Get a token from `POST /api/login/`. Admin or HR Manager role
required for write operations (POST/PATCH/DELETE).

---

## List company types

```http
GET /api/core/company-types/
```

**Response 200 OK** — JSON array of company type objects.

```bash
curl https://backend.sakrshipping.com/api/core/company-types/ \
  -H "Authorization: Bearer $TOKEN"
```

```json
[
  { "id": 1, "name": "BULK - CARGO" },
  { "id": 2, "name": "Vessel Owner" },
  { "id": 16, "name": "uuiiii" }
]
```

Results are ordered by `name` (set by `core.CompanyType.Meta.ordering`).

Supports `?search=xxx` and pagination via DRF's standard
`?page=N&page_size=M` query parameters.

---

## Create company type

```http
POST /api/core/company-types/
Content-Type: application/json
```

**Body**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Unique, max 100 chars |

**Response 201 Created** — full company type object.

```bash
curl -X POST https://backend.sakrshipping.com/api/core/company-types/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tanker Operators"}'
```

```json
{ "id": 17, "name": "Tanker Operators" }
```

**Response 400 Bad Request** — name is missing or already exists:

```json
{ "name": ["company type with this name already exists."] }
```

---

## Get one company type

```http
GET /api/core/company-types/{id}/
```

**Response 200 OK** — full company type object.

```bash
curl https://backend.sakrshipping.com/api/core/company-types/2/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response 404 Not Found** — company type with that ID doesn't exist.

---

## Update company type

```http
PATCH /api/core/company-types/{id}/
Content-Type: application/json
```

**Body**:

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Must remain unique |

**Response 200 OK** — updated company type object.

```bash
curl -X PATCH https://backend.sakrshipping.com/api/core/company-types/2/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Vessel Owner (renamed)"}'
```

> **Warning**: renaming a company type that's referenced by a
> `Company.company_type` row will leave the company pointing at a
> stale string. Prefer creating a new one with a different name
> rather than renaming.

---

## Delete company type

```http
DELETE /api/core/company-types/{id}/
```

**Response 204 No Content** — success, no body.

```bash
curl -X DELETE https://backend.sakrshipping.com/api/core/company-types/16/ \
  -H "Authorization: Bearer $TOKEN"
```

> **Warning**: deleting a company type referenced by `Company.company_type`
> will leave the company pointing at a stale string. The DRF default
> is to allow the delete (no DB-level FK enforcement here). Prefer
> renaming or repurposing rather than deleting when in doubt.

---

## Company type object shape

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `name` | string | Unique, max 100 chars |

---

## Seeding / syncing the canonical company type list

There is no seed migration for `core.CompanyType` — production starts
at 0 entries and grows only as admins add new types via Settings.

The Add New Principal form's Principal Type dropdown is a hardcoded
array of 11 values in `fieldConfigs.js:84-96`:

```js
[
  "Cargo Manning Principals",
  "Cruise & Hospitality Manning Principals",
  "Fishing Fleet Manning Principals",
  "Full Crew Management Principals",
  "General Crew Manning Principals",
  "Offshore & Oil/Gas Manning Principals",
  "Vessel Owner",
  "Shipping Manning Principals",
  "Specialized Marine Manning Principals",
  "Temporary / Contract Manning Agencies",
  "Other",
]
```

A sync command was added to seed the DB with this canonical list:

```bash
python manage.py sync_company_types            # apply
python manage.py sync_company_types --dry-run  # show what would change
python manage.py sync_company_types --backup   # write backups/company_types_before_sync_<ts>.json
```

**What it does**:
1. Inserts the 11 canonical names that aren't in the DB yet.
2. Leaves any custom names you've added (e.g. "BULK - CARGO",
   "uuiiii") in place.

**Idempotent** — safe to re-run; on a fully-seeded DB it's a no-op.

---

## Error responses

```json
{ "detail": "Human-readable message" }
```
or, for field-level validation errors:
```json
{ "name": ["company type with this name already exists."] }
```

| Status | When |
|--------|------|
| 400 | Missing or duplicate name |
| 401 | No token / invalid token |
| 403 | Authenticated but not allowed |
| 404 | Company type not found |
| 500 | Server error |

---

## Frontend consistency note

The **Add New Principal** form's `Principal Type` dropdown
(`fieldConfigs.js:77-101`) is currently a hardcoded array of 11
type names, NOT a runtime call to `/api/core/company-types/`. So:

- New types added via this endpoint WILL appear in Settings →
  Principal Types.
- They will NOT appear in the Add New Principal form's Principal
  Type dropdown until the frontend is updated to use the API.

The eventual fix is a 1-line change in `fieldConfigs.js`:

```jsx
options: refData.companyTypes?.map(t => ({ value: t.name, label: t.name })) || []
```
