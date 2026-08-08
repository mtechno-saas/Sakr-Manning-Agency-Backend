# Vessel Types API

Endpoints for managing the canonical list of vessel types used as
the `Ship.ship_type` choice and in the Seafarer Application form's
vessel type dropdown.

The frontend Settings → Dropdown Data → Vessel Types tab is the
primary UI on top of this endpoint. The Add/Edit Ship form's vessel
type dropdown is already dynamic (it reads from `useReferenceData()
.vesselTypes`), unlike the Country Flag dropdown which is still
hardcoded.

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

## List vessel types

```http
GET /api/core/vessel-types/
```

**Response 200 OK** — JSON array of vessel type objects.

```bash
curl https://backend.sakrshipping.com/api/core/vessel-types/ \
  -H "Authorization: Bearer $TOKEN"
```

```json
[
  { "id": 1, "name": "Container Ships" },
  { "id": 2, "name": "Bulk Carriers" },
  { "id": 11, "name": "Bulk Carrier" },
  { "id": 13, "name": "General Cargo Ship" }
]
```

Results are ordered by `name` (set by `core.VesselType.Meta.ordering`).

Supports `?search=xxx` and pagination via DRF's standard
`?page=N&page_size=M` query parameters.

---

## Create vessel type

```http
POST /api/core/vessel-types/
Content-Type: application/json
```

**Body**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Unique, max 100 chars |

**Response 201 Created** — full vessel type object.

```bash
curl -X POST https://backend.sakrshipping.com/api/core/vessel-types/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "LNG Carrier"}'
```

```json
{ "id": 13, "name": "LNG Carrier" }
```

**Response 400 Bad Request** — name is missing or already exists:

```json
{ "name": ["vessel type with this name already exists."] }
```

---

## Get one vessel type

```http
GET /api/core/vessel-types/{id}/
```

**Response 200 OK** — full vessel type object.

```bash
curl https://backend.sakrshipping.com/api/core/vessel-types/13/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response 404 Not Found** — vessel type with that ID doesn't exist.

---

## Update vessel type

```http
PATCH /api/core/vessel-types/{id}/
Content-Type: application/json
```

**Body**:

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Must remain unique |

**Response 200 OK** — updated vessel type object.

```bash
curl -X PATCH https://backend.sakrshipping.com/api/core/vessel-types/13/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "LNG Carrier (renamed)"}'
```

> **Warning**: renaming a vessel type that's referenced by a `Ship.ship_type`
> row will leave the ship pointing at a stale string. Prefer leaving
> the original or creating a new one with a different name.

---

## Delete vessel type

```http
DELETE /api/core/vessel-types/{id}/
```

**Response 204 No Content** — success, no body.

```bash
curl -X DELETE https://backend.sakrshipping.com/api/core/vessel-types/13/ \
  -H "Authorization: Bearer $TOKEN"
```

> **Warning**: deleting a vessel type referenced by `Ship.ship_type` will
> leave the ship pointing at a stale string. The DRF default behavior is
> to allow the delete (no DB-level FK enforcement here). Prefer renaming
> or repurposing rather than deleting when in doubt.

---

## Vessel type object shape

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `name` | string | Unique, max 100 chars |

---

## Seeding / syncing the canonical vessel type list

`core.VesselType` was first seeded by migration `0005_populate_vessel_types.py`
with 10 types (`Container Ships`, `Bulk Carriers`, `Tankers`, `Ro-Ro Ships`,
`Passenger Ships`, `Fishing Vessels`, `Recreational`,
`Offshore Support Vessels`, `Icebreakers`, `Tugboats`).

The current production state has 32 types — a mix of seeded and
manually-added entries. Naming is inconsistent (`Container Ships`
plural vs `Container Ship` singular; both `Tanker` and `Oil Tanker`
exist). The frontend form's `ship_type` dropdown reads dynamically,
so no broken UX, but the duplicate names show up in the Settings list.

A sync command was added to insert the canonical vessel type list
**without** removing existing rows (so historical `Ship.ship_type`
references stay valid):

```bash
python manage.py sync_vessel_types            # apply
python manage.py sync_vessel_types --dry-run  # show what would change
python manage.py sync_vessel_types --backup   # write backups/vessel_types_before_sync_<ts>.json
```

**What it does**:
1. Inserts any canonical names that aren't in the DB yet.
2. Does NOT delete or rename existing rows (would break FK references).

**Idempotent** — safe to re-run; on a fully-seeded DB it's a no-op.

---

## Error responses

```json
{ "detail": "Human-readable message" }
```
or, for field-level validation errors:
```json
{ "name": ["vessel type with this name already exists."] }
```

| Status | When |
|--------|------|
| 400 | Missing or duplicate name |
| 401 | No token / invalid token |
| 403 | Authenticated but not allowed |
| 404 | Vessel type not found |
| 500 | Server error |
