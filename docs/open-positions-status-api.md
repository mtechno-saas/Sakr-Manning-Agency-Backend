# Open Positions Status API

`GET /api/companies/open-positions-status/` — flat report listing
one row per vacant `JobOrderPosition`, with the principal
(company), position title (rank), remaining vacancies, and the
parent job order's status / dates. Drives the Open Positions
Status UI.

---

## Base URL

```
https://backend.sakrshipping.com
```

## Auth

```
Authorization: Bearer <access_token>
```

Any authenticated user.

---

## Method

| Method | Path |
|--------|------|
| `GET` | `/api/companies/open-positions-status/` |

## Query params (all optional)

| Name | Default | Notes |
|------|---------|-------|
| `status` | `Pending`, `Open`, `Hold`, `In Progress`, `Active` | Restrict to one of: `Pending`, `Open`, `Hold`, `In Progress`, `Active`, `Fulfilled`, `Cancelled`, `Closed`. |
| `principal` | (all) | Numeric company id; only that principal's rows. |
| `position_title` | (all) | Case-insensitive contains-match on rank name. |

## Response 200 OK

```json
{
  "total_records": 2,
  "report_date": "2026-08-11",
  "results": [
    {
      "reference_number": "JO-2026-001",
      "principal": "Maersk Line",
      "position_title": "Master / Captain",
      "vacancies": 3,
      "status": "Open",
      "job_order_number": 1,
      "request_date": "2026-01-15",
      "target_join_date": "2026-03-01"
    },
    {
      "reference_number": "JO-2026-001",
      "principal": "Maersk Line",
      "position_title": "Chief Officer",
      "vacancies": 1,
      "status": "Open",
      "job_order_number": 1,
      "request_date": "2026-01-15",
      "target_join_date": "2026-03-01"
    }
  ]
}
```

### Field map

| Field | Source | Notes |
|-------|--------|-------|
| `reference_number` | `JobOrder.reference_number` | e.g. `"JO-2024-001"` |
| `principal` | `JobOrder.company.company_name` | The principal's display name |
| `position_title` | `JobOrderPosition.rank.name` | The rank for this position |
| `vacancies` | `quantity - filled_slots` | Remaining slots, **only rows with `vacancies > 0` are returned** |
| `status` | `JobOrder.status` | Parent job order's status |
| `job_order_number` | `JobOrder.id` (numeric PK) | Distinct from the human-readable `reference_number` |
| `request_date` | `JobOrder.request_date` | ISO 8601 (`YYYY-MM-DD`) |
| `target_join_date` | `JobOrder.target_joining_date` | ISO 8601 (`YYYY-MM-DD`) |

### Top-level

| Field | Notes |
|-------|-------|
| `total_records` | `len(results)`, i.e. the number of *vacant* positions in the filtered set |
| `report_date` | Today's local date — captures the moment the report was generated |
| `results` | Array of position rows as above |

## Examples

```bash
# Default — all currently open positions
curl 'https://backend.sakrshipping.com/api/companies/open-positions-status/' \
  -H "Authorization: Bearer $TOKEN"

# Only one company
curl '.../api/companies/open-positions-status/?principal=3' \
  -H "Authorization: Bearer $TOKEN"

# Only a specific rank
curl '.../api/companies/open-positions-status/?position_title=chief' \
  -H "Authorization: Bearer $TOKEN"

# Include closed/cancelled orders
curl '.../api/companies/open-positions-status/?status=Closed' \
  -H "Authorization: Bearer $TOKEN"
```

## What's NOT included

- **Salary range** (covered by `GET /api/companies/job-positions/`)
- **Vessel name** (covered by `GET /api/companies/job-orders/`)
- **Assigned crew** (covered by `GET /api/companies/job-positions/`)
- **Historical changes** (this is a current-state snapshot, not a log)

## Error responses

```json
{ "error": "Invalid status 'Bogus'. Allowed: ['Pending', 'Open', 'Hold', 'In Progress', 'Active', 'Fulfilled', 'Cancelled', 'Closed']" }
```

| Status | When |
|--------|------|
| 400 | Invalid `status` value |
| 401 | No token / invalid token |
| 500 | Server error |
