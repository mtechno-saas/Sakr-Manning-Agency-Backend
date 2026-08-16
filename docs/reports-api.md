# Reports endpoint

The Reports page on the frontend posts a filter spec to this endpoint and renders the returned sections. There is no DB-side "saved report" model — each request is self-contained and idempotent.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` / `GET` | `/api/reports/generate/` | Run a filter spec, get rows back. Same shape for both. |
| `GET` | `/api/reports/dropdown-options/` | One-shot list of every filter dropdown option, populated from the database. The Reports page calls this once on load. |

Auth on both: any authenticated user.

### `GET /api/reports/dropdown-options/`

Returns the lists the Reports page uses to populate its filter dropdowns. The frontend fetches this once when the page loads, then uses the returned `id`s or `name`s as filter values.

```json
{
  "generated_at": "2026-08-17T00:00:00+00:00",
  "options": {
    "companies":      [{ "id": 1, "name": "Maersk Line" }, ...],
    "ships":          [{ "id": 5, "name": "MV Pacific" }, ...],
    "ship_types":     [{ "id": 7, "name": "Tanker" }, ...],
    "flags":          [{ "id": 11, "name": "Panama" }, ...],
    "company_types":  [{ "id": 3, "name": "Ship Owner" }, ...],
    "ranks":          [{ "id": 42, "name": "Master", "code": "MAS-1" }, ...]
  },
  "enum_options": {
    "job_order_statuses": ["Open", "Close", "Full Filled"],
    "company_statuses":   ["Active", "Inactive", "Prospect"],
    "ship_statuses":      ["Active", "Under Maintenance", "Inactive"],
    "user_roles":         ["Admin", "HR Manager", "Recruiter", "Employee"],
    "user_statuses":      ["ON_SITE", "ON_BOARD", "VACATION", "MEDICAL_VACATION", "NEW_APPLICANT"]
  }
}
```

Each list is capped at 1000 entries (more than any sane UI shows). Ranks include both `name` and `code` so the dropdown can render "Master (MAS-1)".

---

## `POST` / `GET /api/reports/generate/`

Both methods produce the **same response shape**. Use POST for the full Reports page (large multi-select spec), use GET for ad-hoc Postman debugging or for bookmarkable / cacheable URLs with smaller filter specs.

## ID-or-name filtering

For every feature that has a numeric id **and** a human name, the filter accepts BOTH forms:

| IDs form | Names form | Match |
|---|---|---|
| `company_ids: [1, 2]` | `company_names: ["Maersk"]` | company 1 OR 2 OR whose name contains "Maersk" |
| `ship_ids: [5]` | `ship_names: ["Atlas"]` | ship 5 OR whose name contains "Atlas" |
| `company_type_ids: [3]` | `company_type_names: ["Owner"]` | type 3 OR whose name contains "Owner" |
| `country_ids: [10]` | `country_names: ["Egypt"]` | flag 10 OR whose name contains "Egypt" |
| `ship_type_ids: [7]` | `ship_type_names: ["Tanker"]` | type 7 OR whose name contains "Tanker" |
| `flag_ids: [11]` | `flag_names: ["Panama"]` | flag 11 OR whose name contains "Panama" |
| `rank_ids: [42]` | `rank_names: ["Master"]` or `["MAS-1"]` | rank 42 OR whose name/code contains the value |

Name matching is **case-insensitive contains** (so "alpha" matches both "Alpha Shipping" and "Alphaline"). Rank names also match against `Rank.code` (so "MAS-1" matches rank "Master" / code "MAS-1").

If you pass BOTH `_ids` and `_names` for the same feature in one request, they OR together. The frontend can pick whichever form is easier to display in its multi-select UI.

Empty / whitespace-only name strings are accepted by the serializer and silently ignored at the service layer.

## Request body

```json
{
  "job_orders":    { ... optional filters ... },
  "job_positions": { ... optional filters ... },
  "companies":     { ... optional filters ... },
  "ships":         { ... optional filters ... },
  "users":         { ... optional filters ... }
}
```

Each top-level block is optional. A block that is present but empty (`{}`) returns all rows for that entity. A block that is omitted entirely is not included in the response.

## GET query grammar

For GET, the same nested spec is flattened into the URL using dotted keys `<section>.<field>`. Multi-value fields accept BOTH:

- Repeated params: `?job_orders.company_names=Maersk&job_orders.company_names=MSC`
- Comma-separated: `?job_orders.company_names=Maersk,MSC`
- Mixed: `?job_orders.company_names=Maersk&job_orders.company_names=MSC,Egypt`

The two are equivalent — the service concatenates the values into a single list.

### Example

```
GET /api/reports/generate/
  ?job_orders.company_names=Maersk,MSC
  &job_orders.statuses=Open
  &job_orders.statuses=Close
  &job_orders.rank_names=Master
  &job_orders.target_join_date_from=2026-09-01
  &job_orders.target_join_date_to=2026-12-31
  &companies.company_type_names=Ship Owner
  &companies.statuses=Active
```

is equivalent to the POST body:

```json
{
  "job_orders": {
    "company_names": ["Maersk", "MSC"],
    "statuses": ["Open", "Close"],
    "rank_names": ["Master"],
    "target_join_date_from": "2026-09-01",
    "target_join_date_to": "2026-12-31"
  },
  "companies": {
    "company_type_names": ["Ship Owner"],
    "statuses": ["Active"]
  }
}
```

### "Give me everything"

A GET with no query parameters returns all 4 sections (each with up to 500 rows) — convenient for "I just want to see what's in the DB" debugging.

A POST with `{}` (empty body) returns an **empty `sections` object** — by design, since the POST body is explicit about which sections are wanted. To get all 4 sections via POST, send `{"job_orders": {}, "companies": {}, "ships": {}, "users": {}}`.

### Scalar fields via GET

Date / int / bool fields take a single value, not a list:

```
?job_orders.request_date_from=2026-09-01
?ships.year_built_from=2010
?users.is_blacklisted=true
```

If you pass multiple values for a scalar (e.g. `?is_blacklisted=true&is_blacklisted=false`), the last non-empty value wins.

## Response (200 OK)

```json
{
  "generated_at": "2026-08-16T23:10:00+00:00",
  "limit_per_section": 500,
  "sections": {
    "job_orders":    { "total_records": 12, "rows": [ ... ] },
    "job_positions": { "total_records": 7,  "rows": [ ... ] },
    "companies":     { "total_records": 5,  "rows": [ ... ] },
    "ships":         { "total_records": 8,  "rows": [ ... ] },
    "users":         { "total_records": 25, "rows": [ ... ] }
  }
}
```

Each `rows` array uses the existing list-endpoint serializer. `job_positions.rows` uses `JobOrderPositionSerializer` (flat position-level view).

## Per-entity filter dimensions

### `job_orders`

| Field | Type | Notes |
|---|---|---|
| `company_ids` / `company_names` | list | Job orders whose company matches either form |
| `ship_ids` / `ship_names` | list | Job orders whose ship matches either form |
| `statuses` | list of str | `Open`, `Close`, `Full Filled` |
| `rank_ids` / `rank_names` | list | Job orders with at least one position with one of these ranks (name matches `Rank.name` or `Rank.code`) |
| `request_date_from` / `to` | `YYYY-MM-DD` | Range on `JobOrder.request_date` |
| `target_join_date_from` / `to` | `YYYY-MM-DD` | Range on `JobOrder.target_joining_date` |

### `job_positions`

Filter at the **position** level (not the parent JO). Each row in the response is a `JobOrderPosition`, so you get a flat list of every position matching the criteria across all job orders.

| Field | Type | Notes |
|---|---|---|
| `position_ids` | list of int | Direct PK lookup |
| `position_rank_names` | list of str | Case-insensitive contains on `Rank.name` OR `Rank.code` |
| `position_company_ids` / `position_company_names` | list | Filter by the parent job order's company |
| `position_ship_ids` / `position_ship_names` | list | Filter by the parent job order's ship |
| `position_statuses` | list of str | The status of the PARENT job order. So `position_statuses=["Open"]` returns positions under Open job orders. |

**Example** — "every open Motorman slot in the system":

```
POST /api/reports/generate/
{
  "job_positions": {
    "position_rank_names": ["Motorman"],
    "position_statuses": ["Open"]
  }
}
```

Response: a flat list of every Motorman position under an Open job order. Compare to `job_orders.rank_names=["Motorman"]` which returns the PARENT job order (and all its positions in the nested array).

### `companies`

| Field | Type | Notes |
|---|---|---|
| `company_type_ids` / `company_type_names` | list | FK to `core.CompanyType` |
| `country_ids` / `country_names` | list | FK to `core.Flag` (the `company_flag`) |
| `statuses` | list of str | `Active`, `Inactive`, `Prospect` |

### `ships`

| Field | Type | Notes |
|---|---|---|
| `company_ids` / `company_names` | list | |
| `ship_type_ids` / `ship_type_names` | list | FK to `core.VesselType` |
| `flag_ids` / `flag_names` | list | FK to `core.Flag` |
| `year_built_from` / `to` | int | |

### `users`

| Field | Type | Notes |
|---|---|---|
| `roles` | list of str | `Admin`, `HR Manager`, `Recruiter`, `Employee` |
| `user_statuses` | list of str | The effective 5-state status. Accepts `MEDICAL_VACATION` or `MEDICAL VACATION` (normalized). |
| `rank_ids` / `rank_names` | list | Users with a `UserRank` row pointing at one of these (name matches `Rank.name` or `Rank.code`) |
| `nationalities` | list of str | Case-insensitive contains-match on `Users.nationality` (OR'd) |
| `is_blacklisted` | bool | `true` / `false` (omit = no filter) |

## Semantics

- **AND within a section**: all provided filters AND together.
- **OR within a multi-value field**: e.g. `company_ids=[1,2]` matches 1 OR 2.
- **OR across `_ids` and `_names` for the same feature**: pass `company_ids=[1]` and `company_names=["Maersk"]` and you get companies 1 OR any whose name contains "Maersk".
- **Sections are independent**: filtering `job_orders.company_ids` does not affect the `companies` section.
- **No cross-entity JOIN**: a job order row doesn't expand into the assigned crew; if the frontend wants that, it follows up with `/api/companies/job-orders/{id}/` which already exposes `assigned_crew`.

## Limits

`limit_per_section: 500` — the most rows any one section can return in a single request. The frontend can refine its filters for more, or follow up with the list endpoint with pagination for deeper drill-down.

## Error responses

- 400 with a clear field-level message for any invalid filter value (e.g. an unsupported status, a malformed date).
- 401/403 if the request isn't authenticated.

## Files

- `reports/views.py` — `ReportsGenerateView` (POST/GET), `ReportsDropdownOptionsView` (GET).
- `reports/serializers.py` — per-entity filter validation (`JobOrder`, `JobPosition`, `Company`, `Ship`, `User`); `_NormalisedStatusField`.
- `reports/services.py` — `generate_report()` and the five `_xxx_qs` queryset builders; `_or_id_name` helper for the id/name merge.
- `reports/urls.py` — routes under `/api/reports/`.
- `reports/tests.py` — 75 tests across 13 test classes.
- `saker/urls.py` — `path("api/reports/", include("reports.urls"))`.
- `saker/settings.py` — `'reports'` added to `INSTALLED_APPS`.
