# Country Flags API

Endpoints for managing the canonical list of countries used as the
`Company.company_flag` choice and in other places that need a country
dropdown.

The frontend Settings → Dropdown Data → Nationalities/Flags tab is the
primary UI on top of this endpoint. The Add New Principal form's
Country Flag dropdown is currently a hardcoded list in the frontend
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

## List flags

```http
GET /api/core/flags/
```

**Response 200 OK** — JSON array of flag objects.

```bash
curl https://backend.sakrshipping.com/api/core/flags/ \
  -H "Authorization: Bearer $TOKEN"
```

```json
[
  { "id": 1, "name": "Afghanistan", "icon": null },
  { "id": 2, "name": "Albania", "icon": null },
  { "id": 3, "name": "Algeria", "icon": null },
  { "id": 208, "name": "rammatag", "icon": null }
]
```

Results are ordered by `name` (set by `core.Flag.Meta.ordering`).

Supports `?search=xxx` and pagination via DRF's standard
`?page=N&page_size=M` query parameters.

---

## Create flag

```http
POST /api/core/flags/
Content-Type: application/json
```

**Body**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Unique, max 100 chars |
| `icon` | file   | no  | Optional flag icon (image) |

**Response 201 Created** — full flag object.

```bash
curl -X POST https://backend.sakrshipping.com/api/core/flags/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "rammatag"}'
```

```json
{ "id": 208, "name": "rammatag", "icon": null }
```

**Response 400 Bad Request** — name is missing or already exists:

```json
{ "name": ["flag with this name already exists."] }
```

---

## Get one flag

```http
GET /api/core/flags/{id}/
```

**Response 200 OK** — full flag object.

```bash
curl https://backend.sakrshipping.com/api/core/flags/208/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response 404 Not Found** — flag with that ID doesn't exist.

---

## Update flag

```http
PATCH /api/core/flags/{id}/
Content-Type: application/json
```

**Body** (any subset):

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Must remain unique |
| `icon` | file   | Pass a new image to replace, or `null` to clear |

**Response 200 OK** — updated flag object.

```bash
curl -X PATCH https://backend.sakrshipping.com/api/core/flags/208/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Rammatag (renamed)"}'
```

---

## Delete flag

```http
DELETE /api/core/flags/{id}/
```

**Response 204 No Content** — success, no body.

```bash
curl -X DELETE https://backend.sakrshipping.com/api/core/flags/208/ \
  -H "Authorization: Bearer $TOKEN"
```

> **Warning**: deleting a flag that's referenced by a `Company.company_flag`
> row will leave the company pointing at a stale string. Prefer renaming
> or repurposing rather than deleting when in doubt.

---

## Flag object shape

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `name` | string | Unique, max 100 chars |
| `icon` | string \| null | URL to uploaded flag image, or `null` |

---

## Seeding / syncing the canonical country list

`core.Flag` was first seeded by migration `0004_populate_flags.py` with
~190 country names using a slightly different naming convention than
the frontend's hardcoded list in `fieldConfigs.js:130-156`.

A second command was added to keep the DB in sync with the canonical
frontend names:

```bash
python manage.py sync_country_flags            # apply
python manage.py sync_country_flags --dry-run  # show what would change
python manage.py sync_country_flags --backup   # write backups/flags_before_sync_<ts>.json
```

**What it does**:
1. Inserts any canonical names (e.g. `United States`, `Cape Verde`,
   `Taiwan`, `Vatican City`) that aren't in the DB yet.
2. Leaves the legacy parenthesised rows from migration 0004
   (`United States of America`, `Cabo Verde`, `Congo (Congo-Brazzaville)`,
   `Czechia (Czech Republic)`, `Myanmar (formerly Burma)`,
   `Palestine State`) in place so historical `Company.company_flag`
   values still resolve.

**Idempotent** — safe to re-run; on a fully-seeded DB it's a no-op.

---

## Error responses

All error responses use this shape:

```json
{ "detail": "Human-readable message" }
```
or, for field-level validation errors:
```json
{ "name": ["flag with this name already exists."] }
```

| Status | When |
|--------|------|
| 400 | Missing or duplicate name, invalid icon |
| 401 | No token / invalid token |
| 403 | Authenticated but not allowed (e.g. Employee trying to POST) |
| 404 | Flag not found |
| 500 | Server error |

---

## Frontend consistency note

The **Add New Principal** form's `Country Flag` dropdown
(`fieldConfigs.js:122-160`) is currently a hardcoded array of ~190
country names, NOT a runtime call to `/api/core/flags/`. So:

- New flags added via this endpoint WILL appear in Settings →
  Nationalities/Flags.
- They will NOT appear in the Add New Principal form's Country Flag
  dropdown until the frontend is updated to use the API.

The eventual fix is a 1-line change in `fieldConfigs.js`:

```jsx
options: refData.flags?.map(f => ({ value: f.name, label: f.name })) || []
```

Backend data is already prepared — the `sync_country_flags` command
keeps the DB list consistent with the frontend's historical naming.
