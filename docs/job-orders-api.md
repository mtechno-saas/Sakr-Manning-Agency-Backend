# Job Orders — `assigned_crew`

`GET /api/companies/job-orders/` (and `GET /api/companies/job-orders/{id}/`) now include a flat `assigned_crew` field on every row.

## Shape

```json
{
  "id": 12,
  "reference_number": "JO-2026-042",
  "status": "Open",
  "company_name": "ABC Shipping",
  "ship_name": "MV Pacific",
  "total_open_vacancies": 1,
  "total_closed_vacancies": 2,
  "total_fully_filled_vacancies": 1,
  "positions": [ ... ],
  "assigned_crew": [
    {
      "contract_id": 17,
      "user_id": 42,
      "user_name": "John Smith",
      "user_email": "john@example.com",
      "ship_id": 8,
      "ship_name": "MV Pacific",
      "rank": "Master",
      "contract_status": "Active",
      "sign_on_date": "2026-08-01",
      "sign_off_date": null
    },
    {
      "contract_id": 18,
      "user_id": 55,
      "user_name": "Jane Doe",
      "user_email": "jane@example.com",
      "ship_id": 9,
      "ship_name": "MV Atlantic",
      "rank": "Chief Officer",
      "contract_status": "Signed",
      "sign_on_date": "2026-08-15",
      "sign_off_date": null
    }
  ]
}
```

## What "assigned" means

One row per `Contract` whose `job_position` belongs to this JobOrder. Every contract status is included — `Active`, `Signed`, `Draft`, `Pending Signature`, `Pending`, `Completed`, `Cancelled`. The frontend can filter by `contract_status` if it only wants filled positions.

`assigned_crew` is a flat list (not nested under `positions`) so a single table render covers it.

## Field-by-field

| Field | Source | Notes |
|---|---|---|
| `contract_id` | `Contract.id` | The database pk; useful for deep-linking |
| `user_id` | `Contract.user_id` | The crew member's `Users.id` |
| `user_name` | `Users.full_name` (`first_name` + `middle_name`) | Falls back to email, then username, then `user#<id>` |
| `user_email` | `Users.email` | |
| `ship_id` | `Contract.ship_id` | The ship on the **contract** (the vessel the crew member is on) — not necessarily the job order's ship |
| `ship_name` | `Contract.ship.ship_name` | |
| `rank` | `JobOrderPosition.rank.name` | Falls back to the contract's stored rank if the position has no rank |
| `contract_status` | `Contract.status` | |
| `sign_on_date` | `Contract.sign_on_date` (ISO 8601) | |
| `sign_off_date` | `Contract.sign_off_date` (ISO 8601) or `null` | |

## Performance

The viewset's `get_queryset` prefetches `positions__contracts__user`, `__ship`, and `__job_position__rank` so the field is computed with a constant number of queries regardless of how many crew are assigned.

## When `assigned_crew` is `[]`

The common case for a brand-new "Open" JobOrder — no contracts have been created against it yet. The frontend should render an empty state.

## Files touched

- `companies/serializers.py` — new `assigned_crew` `SerializerMethodField` and `_user_name` helper on `JobOrderSerializer`
- `companies/views.py` — viewset prefetch extended with `__ship` and `__job_position__rank`
- `companies/tests.py` — 7 new tests in `JobOrderAssignedCrewTests`
