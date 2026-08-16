# Reports endpoint

The Reports page on the frontend posts a filter spec to this endpoint and renders the returned sections. There is no DB-side "saved report" model — each request is self-contained and idempotent.

## Endpoint

`POST /api/reports/generate/`

Auth: any authenticated user. (Add a custom permission class if the team later wants server-side role gating.)

## Request body

```json
{
  "job_orders": { ... optional filters ... },
  "companies":  { ... optional filters ... },
  "ships":      { ... optional filters ... },
  "users":      { ... optional filters ... }
}
```

Each top-level block is optional. A block that is present but empty (`{}`) returns all rows for that entity. A block that is omitted entirely is not included in the response.

## Response (200 OK)

```json
{
  "generated_at": "2026-08-16T23:10:00+00:00",
  "limit_per_section": 500,
  "sections": {
    "job_orders": {
      "total_records": 12,
      "rows": [ ...JobOrder rows... ]
    },
    "companies": {
      "total_records": 5,
      "rows": [ ...Company rows... ]
    },
    "ships": {
      "total_records": 8,
      "rows": [ ...Ship rows... ]
    },
    "users": {
      "total_records": 25,
      "rows": [ ...User rows... ]
    }
  }
}
```

Each section's `rows` is the same shape as the corresponding list endpoint's rows (uses the existing serializers: `JobOrderSerializer`, `CompanySerializer`, `ShipSerializer`, `UsersSerializer`).

## Filter dimensions

### `job_orders`

| Field | Type | Notes |
|---|---|---|
| `company_ids` | list of int | Job orders whose `company_id` is in this list |
| `ship_ids` | list of int | Job orders whose `ship_id` is in this list |
| `statuses` | list of str | One or more of `Open`, `Close`, `Full Filled` |
| `rank_ids` | list of int | Job orders that have at least one `JobOrderPosition` with one of these ranks |
| `request_date_from` | `YYYY-MM-DD` | `JobOrder.request_date >= this` |
| `request_date_to` | `YYYY-MM-DD` | `JobOrder.request_date <= this` |
| `target_join_date_from` | `YYYY-MM-DD` | `JobOrder.target_joining_date >= this` |
| `target_join_date_to` | `YYYY-MM-DD` | `JobOrder.target_joining_date <= this` |

### `companies`

| Field | Type | Notes |
|---|---|---|
| `company_type_ids` | list of int | FK to `core.CompanyType` |
| `country_ids` | list of int | FK to `core.Flag` (the `company_flag` on the company) |
| `statuses` | list of str | One or more of `Active`, `Inactive`, `Prospect` |

### `ships`

| Field | Type | Notes |
|---|---|---|
| `company_ids` | list of int | Ships under these companies |
| `ship_type_ids` | list of int | FK to `core.VesselType` |
| `flag_ids` | list of int | FK to `core.Flag` |
| `year_built_from` | int | `year_built >= this` |
| `year_built_to` | int | `year_built <= this` |

### `users`

| Field | Type | Notes |
|---|---|---|
| `roles` | list of str | One or more of `Admin`, `HR Manager`, `Recruiter`, `Employee` |
| `user_statuses` | list of str | The effective 5-state status. Accepts `ON_SITE`, `ON_BOARD`, `VACATION`, `MEDICAL_VACATION` / `MEDICAL VACATION` (both forms accepted; we normalize), `NEW_APPLICANT`. Logic mirrors `?user_status=` on the users list endpoint. |
| `rank_ids` | list of int | Users that have a `UserRank` row pointing at any of these ranks |
| `nationalities` | list of str | Case-insensitive contains-match on `Users.nationality` (OR'd across the list) |
| `is_blacklisted` | bool | `true` / `false` (null = no filter) |

## Semantics

- **AND within a section**: all provided filters AND together.
- **OR within a multi-value field**: e.g. `company_ids=[1,2]` matches companies 1 OR 2.
- **Sections are independent**: filtering `job_orders.company_ids` does not affect the `companies` section. Each section is a self-contained filtered list.
- **No cross-entity JOIN**: a job order row doesn't expand into the assigned crew; if the frontend wants that, it follows up with `/api/companies/job-orders/{id}/` which already exposes `assigned_crew`.

## Limits

- `limit_per_section: 500` — the most rows any one section can return in a single request. The frontend can refine its filters for more, or follow up with the list endpoint with pagination for deeper drill-down.

## Error responses

- 400 with a clear field-level message for any invalid filter value (e.g. an unsupported status, a malformed date).
- 401/403 if the request isn't authenticated (or the user is blocked, etc.).

## Files

- `reports/views.py` — `ReportsGenerateView` (POST).
- `reports/serializers.py` — per-entity filter validation.
- `reports/services.py` — `generate_report()` and the four `_xxx_qs` queryset builders.
- `reports/urls.py` — routes under `/api/reports/`.
- `reports/tests.py` — 33 tests across 7 test classes.
- `saker/urls.py` — `path("api/reports/", include("reports.urls"))`.
- `saker/settings.py` — `'reports'` added to `INSTALLED_APPS`.
