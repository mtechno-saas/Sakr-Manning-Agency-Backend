# Ranks API (Job Positions)

Endpoints for managing the canonical list of maritime ranks used
across the application: `User.user_ranks`, `SeaService.rank`,
`Document.position`, and the "Add New Rank" UI in Settings →
Dropdown Data → Job Positions (Ranks).

The frontend Settings → Dropdown Data → Job Positions (Ranks) tab
is the primary UI on top of this endpoint. The rank dropdowns in
form steps are dynamic (read from `/api/ranks/`), unlike the
Country Flag and Principal Type dropdowns which are still
hardcoded in the frontend.

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

## List ranks

```http
GET /api/ranks/
```

**Response 200 OK** — JSON array of rank objects.

```bash
curl https://backend.sakrshipping.com/api/ranks/ \
  -H "Authorization: Bearer $TOKEN"
```

```json
[
  { "id": 1, "code": "DO-1.000", "name": "Master / Captain" },
  { "id": 2, "code": "CUS-394F43", "name": "A/B" },
  { "id": 78, "code": "TR0.000", "name": "trac..." }
]
```

Results are ordered by `code` (set in Django admin; the API itself
returns rows in their default order).

Supports `?search=xxx` and pagination via DRF's standard
`?page=N&page_size=M` query parameters.

---

## Create rank

```http
POST /api/ranks/
Content-Type: application/json
```

**Body**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `code` | string | yes | Unique, max 780 chars (e.g. `MST`, `CUS-XXXXXX`, `TR0.000`) |
| `name` | string | yes | Max 780 chars, e.g. `Master / Captain` |

**Response 201 Created** — full rank object.

```bash
curl -X POST https://backend.sakrshipping.com/api/ranks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Dynamic Positioning Operator", "code": "DPO-1.000"}'
```

```json
{ "id": 79, "code": "DPO-1.000", "name": "Dynamic Positioning Operator" }
```

**Response 400 Bad Request** — code is missing/duplicate, or name is missing.

---

## Get one rank

```http
GET /api/ranks/{id}/
```

**Response 200 OK** — full rank object.

```bash
curl https://backend.sakrshipping.com/api/ranks/1/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response 404 Not Found** — rank with that ID doesn't exist.

---

## Update rank

```http
PATCH /api/ranks/{id}/
Content-Type: application/json
```

**Body** (any subset):

| Field | Type | Notes |
|-------|------|-------|
| `code` | string | Must remain unique |
| `name` | string | |

**Response 200 OK** — updated rank object.

```bash
curl -X PATCH https://backend.sakrshipping.com/api/ranks/79/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Dynamic Positioning Operator (DPO)"}'
```

> **Warning**: `Rank.code` is referenced by `UserRank.assigned_code` and
> other places. Renaming a code that's in use may break lookups.

---

## Delete rank

```http
DELETE /api/ranks/{id}/
```

**Response 204 No Content** — success, no body.

```bash
curl -X DELETE https://backend.sakrshipping.com/api/ranks/79/ \
  -H "Authorization: Bearer $TOKEN"
```

> **Warning**: deleting a rank referenced by `UserRank`, `SeaService`,
> or `Document.position` will cascade-delete those rows (`on_delete=
> CASCADE` on the FK). This is a destructive operation — prefer
> renaming or repurposing when in doubt.

---

## Rank object shape

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `code` | string | Unique, max 780 chars |
| `name` | string | Max 780 chars |

---

## Seeding / syncing the canonical rank list

The frontend form's rank dropdown is dynamic — it reads from
`/api/ranks/`. So unlike flags and principal types, no frontend
list needs to be mirrored.

However, the `Document.position` field is a CharField with a
hardcoded `POSITION_CHOICES` list of 81 rank names (`api/models.py:952`).
When a user picks a position in the admin attachments section, they
pick from those 81 names. But the dynamic Rank table only has 64.
The other 17 don't exist in the table, which means:
- A Document with `position = "Staff Captain"` has no matching `Rank`
  row, so any code that joins Document.position to Rank.name returns
  nothing.
- The Settings → Job Positions (Ranks) tab shows the dynamic list
  (64 rows), so an admin can't see the hardcoded-only names.

A sync command was added to bring the dynamic Rank table in line
with the model's hardcoded list:

```bash
python manage.py sync_ranks            # apply
python manage.py sync_ranks --dry-run  # show what would change
python manage.py sync_ranks --backup   # write before-state to backups/ranks_before_sync_<ts>.json
```

**What it does**:
1. Inserts any name from `Document.POSITION_CHOICES` that isn't
   already in the `Rank` table.
2. Auto-generates a `code` like `SYNC-NNN` for the new rows (no
   existing code patterns to follow; the production codes are
   a mix of `DO-`, `CUS-`, `DR-`, `TR-` formats).
3. Leaves all existing rows alone.

**Idempotent** — safe to re-run; on a fully-seeded DB it's a no-op.

---

## Error responses

```json
{ "detail": "Human-readable message" }
```
or, for field-level validation errors:
```json
{ "code": ["rank with this code already exists."] }
```

| Status | When |
|--------|------|
| 400 | Missing or duplicate code, missing name |
| 401 | No token / invalid token |
| 403 | Authenticated but not allowed |
| 404 | Rank not found |
| 500 | Server error |
