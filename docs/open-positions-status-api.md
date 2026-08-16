# Open Positions Status

`GET /api/companies/open-positions-status/` — one row per still-vacant `JobOrderPosition`. Used by the Open Positions Status UI.

## Response shape (200 OK)

```json
{
  "total_records": 2,
  "report_date": "2026-08-16",
  "results": [
    {
      "reference_number": "JO-2026-001",
      "principal": "Maersk Line",
      "position_title": "Master",
      "position": "Master",
      "count": 3,
      "vacancies": 3,
      "salary": {
        "min": "4500.00",
        "max": "8000.00",
        "currency": "USD"
      },
      "remarks": "Must have GMDSS cert",
      "status": "Open",
      "job_order_number": 1,
      "request_date": "2026-01-15",
      "target_join_date": "2026-03-01"
    }
  ]
}
```

## Field-by-field

| Field | Source | Notes |
|---|---|---|
| `reference_number` | `JobOrder.reference_number` | The job order's reference, e.g. `JO-2026-001` |
| `principal` | `JobOrder.company.company_name` | The company that issued the job order |
| `position_title` | `JobOrderPosition.rank.name` | The rank title |
| `position` | `JobOrderPosition.rank.name` | Alias of `position_title` (same value) |
| `count` | `JobOrderPosition.quantity` | Total slots requested for this position |
| `vacancies` | `quantity - filled_slots` (max 0) | Remaining unfilled slots |
| `salary.min` | `JobOrderPosition.salary_min` (string) | `null` when not set on the position |
| `salary.max` | `JobOrderPosition.salary_max` (string) | `null` when not set on the position |
| `salary.currency` | `JobOrderPosition.currency` | e.g. `USD`, `EUR` |
| `remarks` | `JobOrderPosition.remarks` | `""` (empty string, not `null`) when blank |
| `status` | `JobOrder.status` | One of `Open` / `Close` / `Full Filled` |
| `job_order_number` | `JobOrder.id` | The job order's database pk |
| `request_date` | `JobOrder.request_date` (ISO 8601) | |
| `target_join_date` | `JobOrder.target_joining_date` (ISO 8601) | |

## Filtering

Optional query params:

- `?status=Open` — change the default filter (default: only `Open` job orders). Allowed: `Open`, `Close`, `Full Filled`. Invalid values return 400.
- `?principal=12` — filter by company id.
- `?position_title=Master` — case-insensitive contains-match on the rank name.
- `?company_name=Maersk` — case-insensitive contains-match on the company name.
- `?vessel_name=Atlas` — case-insensitive contains-match on the ship's name (the vessel the job order is for).
- `?salary_min=5000` — only positions with `salary_min >= 5000`. Decimal value. Invalid → 400.
- `?salary_max=10000` — only positions with `salary_max <= 10000`. Decimal value. Invalid → 400.
- `?request_date_from=2026-01-01` & `?request_date_to=2026-12-31` — date range on the job order's `request_date`. Format `YYYY-MM-DD`. Invalid → 400.
- `?target_join_date_from=2026-01-01` & `?target_join_date_to=2026-12-31` — date range on the job order's `target_joining_date`. Format `YYYY-MM-DD`. Invalid → 400.

All filters can be combined. An empty result set is `{"total_records": 0, "results": []}` with status 200, not 404.

## Default behavior

- Excludes `Close` and `Full Filled` job orders by default — only `Open` ones show up.
- Skips fully-filled positions even if the parent job order is still nominally open (so a `quantity=3, filled=3` position won't appear).

## Sorting

Results are ordered by `request_date` ASC, then `reference_number` ASC, then `rank.name` ASC.

## Files

- `companies/views.py` — `CompanyViewSet.open_positions_status` action.
- `companies/tests.py` — `OpenPositionsStatusEndpointTests` (19 tests).
