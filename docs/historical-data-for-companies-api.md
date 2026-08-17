# Historical Data for Companies

A single endpoint that returns every analysis section (summary / time-series / top-N rankings / status breakdowns / per-company timeline) in one response. Powers the frontend's "Historical data for companies" page.

## Endpoint

`GET /api/historical-data-for-companies/`

Auth: `IsAuthenticated`.

## Query params

| Name | Type | Default | Notes |
|---|---|---|---|
| `date_from` | `YYYY-MM-DD` | 12 months back | Inclusive. Contracts whose `sign_on_date < date_from` are excluded. |
| `date_to` | `YYYY-MM-DD` | today | Inclusive. Contracts whose `sign_on_date > date_to` are excluded. |
| `granularity` | `month` \| `quarter` \| `year` | `month` | Bucket size for the time-series charts. |
| `company_ids` | int, repeated | none | Restrict the analysis to these company ids. |
| `company_names` | str, repeated or comma-separated | none | Restrict by `Company.company_name` (case-insensitive contains). |
| `top_n` | int 1-100 | `10` | Cap each top-N list. |
| `include_timeline` | `true` / `1` / `yes` | `false` | Include the per-company timeline (off by default — can be heavy). |

Invalid values return 400 with a clear error message.

## Response shape (200 OK)

```json
{
  "generated_at": "2026-08-17T...",
  "filters": {
    "date_from": "2026-01-01",
    "date_to": "2026-04-30",
    "granularity": "month",
    "company_ids": [],
    "company_names": [],
    "top_n": 10
  },
  "summary": { ... },
  "time_series": { ... },
  "top_n": { ... },
  "breakdowns": { ... },
  "per_company_timeline": [ ... ]   // only if include_timeline=true
}
```

### `summary`

One-line totals for the date range.

| Field | Source |
|---|---|
| `companies_total` | count of companies matching the company filter (not date-filtered) |
| `companies_active` | count of those whose `status="Active"` |
| `job_orders` | JOs with `request_date` in [date_from, date_to] |
| `contracts` | contracts with `sign_on_date` in range |
| `crew_placed` | distinct users with at least one contract in range |
| `open_positions` | sum of `quantity - filled_slots` over positions in range, only counting positions where `quantity - filled > 0` |
| `date_from` / `date_to` | the applied range |
| `granularity` | the applied bucket size |

### `time_series`

Two time-bucketed arrays for the charts.

```json
{
  "granularity": "month",
  "contracts_over_time": [
    { "period": "2026-01", "signed": 5, "active_signed": 4, "ended": 1 },
    { "period": "2026-02", "signed": 3, "active_signed": 2, "ended": 0 },
    ...
  ],
  "job_orders_over_time": [
    { "period": "2026-01", "created": 2 },
    { "period": "2026-02", "created": 0 },
    ...
  ]
}
```

The period list is the full date range with zero-fill (so the chart has no gaps). Period labels:
- month: `YYYY-MM` (e.g. `2026-01`)
- quarter: `YYYY-QN` (e.g. `2026-Q1`)
- year: `YYYY` (e.g. `2026`)

### `top_n`

Four ranked lists, each capped at `top_n` entries.

| List | Sorted by | Each row has |
|---|---|---|
| `top_companies_by_contracts` | total contract count | `company_id`, `company_name`, `count` |
| `top_companies_by_crew_placed` | distinct users placed | `company_id`, `company_name`, `crew_count` |
| `top_companies_by_total_salary` | sum of `Contract.salary` (string) | `company_id`, `company_name`, `total_salary` |
| `top_ranks_by_demand` | count of `JobOrderPosition` rows | `rank_id`, `rank_name`, `rank_code`, `demand` |

### `breakdowns`

Status / type / country / rank distributions, scoped to the company filter and (for time-bound ones) the date range.

```json
{
  "by_company_status":   { "Active": 12, "Inactive": 3, "Prospect": 1 },
  "by_company_type":     { "Ship Owner": 8, "Ship Manager": 5, ... },
  "by_country":          { "Egypt": 4, "Panama": 3, ... },
  "by_contract_status":  { "Active": 8, "Signed": 2, "Completed": 1, ... },
  "by_rank":             { "Master": 3, "Chief Officer": 2, ... }
}
```

`by_company_status`, `by_company_type`, `by_country` are **not** date-filtered (companies exist regardless of range). `by_contract_status` and `by_rank` are date-filtered.

### `per_company_timeline` (opt-in)

A per-company chronological list of every job order and every contract in the date range, capped at 50 companies (most-requested first).

```json
[
  {
    "company_id": 1,
    "company_name": "Maersk Line",
    "events": [
      { "type": "job_order", "id": 17, "reference_number": "JO-2026-042",
        "request_date": "2026-01-15", "target_joining_date": "2026-03-01",
        "status": "Open" },
      { "type": "contract", "id": 88, "user_id": 42, "rank_id": 5,
        "sign_on_date": "2026-01-20", "sign_off_date": null,
        "status": "Active", "salary": "4500.00" },
      ...
    ]
  }
]
```

Each `events` list is sorted ascending by date (events missing a date are pushed to the end).

## Example requests

### All analyses, last 12 months, default granularity

```
GET /api/historical-data-for-companies/
```

### A specific quarter, by quarter

```
GET /api/historical-data-for-companies/
  ?date_from=2026-01-01
  &date_to=2026-03-31
  &granularity=quarter
```

### Top 20 companies, scoped to one company, with timeline

```
GET /api/historical-data-for-companies/
  ?top_n=20
  &company_names=Maersk
  &include_timeline=true
```

### A specific year

```
GET /api/historical-data-for-companies/
  ?date_from=2026-01-01
  &date_to=2026-12-31
  &granularity=month
```

## Files

- `historical_data_companies/views.py` — `HistoricalDataForCompaniesView` (GET, full query-param validation).
- `historical_data_companies/services.py` — `build_historical_report()` plus the per-section builders (`_build_summary`, `_build_time_series`, `_build_top_n`, `_build_breakdowns`, `_build_per_company_timeline`).
- `historical_data_companies/urls.py` — routes under `/api/historical-data-for-companies/`.
- `historical_data_companies/tests.py` — 24 tests across 7 test classes.
- `saker/urls.py` — `path("api/historical-data-for-companies/", include(...))`.
- `saker/settings.py` — `'historical_data_companies'` added to `INSTALLED_APPS`.
