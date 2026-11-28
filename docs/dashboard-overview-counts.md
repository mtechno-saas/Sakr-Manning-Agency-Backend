# Dashboard Overview — the cards count the loaded page, not the database

**For the frontend dev (Karim).** The Overview cards report the number of rows
the browser happened to have loaded, not the number of records in the
database. On production that is **49 seafarers instead of 625**.

---

## The five cards

| Card | Shows now | Truth | Where the truth lives |
|---|---|---|---|
| Total Seafarers | 49 | **625** | `GET /api/users/users/stats/` → `total_seafarers` (new) |
| Total CVs | 20 | **614** | `GET /api/cv-submissions/stats/` → `total` |
| Total Principals | 6 | 6 ✓ | `GET /api/companies/stats/` → `total_companies` |
| Open Positions | 17 | 17 ✓ | `GET /api/companies/stats/` → `open_positions.total` |
| New Registrations | 49 | ? | `GET /api/users/users/stats/` → `recent_seafarers_30d` (new) |

## Why each one is wrong

**Total Seafarers** — `Overview.jsx:137`

```js
totalSeafarers: seafarersOnly.length,
```

`seafarersOnly` is the users list the dashboard loaded. The users endpoint
returns **one page of 50 rows** (`GET /api/users/users/` → `results` has 50
entries, `count` is 630). 50 loaded − 1 admin = 49.

**Total CVs** — `Overview.jsx:138`

```js
totalCVs: cvStats?.total_applications ?? cvPagination.count ?? cvDocuments?.length ?? 0,
```

`cvStats` comes from `fetchDocumentStats()` → `GET /api/documents/stats/`,
which counts **uploaded CV documents** (`total_applications: 20`) — a
different table from the CV submissions the card is about (614 rows). The
CV submissions endpoint already reports the right number as `total`.

**New Registrations** — `Overview.jsx:144`

```js
recentRegistrations: recentSeafarers.length,
```

Same as Total Seafarers: it filters the loaded page by `created_at`, so it
can only ever see the 50 rows that were loaded.

---

## The fix

`Overview.jsx:129-146` — replace the counts that are derived from a loaded
array with the numbers the server reports:

```js
// before
totalSeafarers: seafarersOnly.length,
totalCVs: cvStats?.total_applications ?? cvPagination.count ?? cvDocuments?.length ?? 0,
recentRegistrations: recentSeafarers.length,

// after
totalSeafarers: userStats?.total_seafarers ?? seafarersOnly.length,
totalCVs: cvSubmissionStats?.total ?? cvStats?.total_applications ?? cvDocuments?.length ?? 0,
recentRegistrations: userStats?.recent_seafarers_30d ?? recentSeafarers.length,
```

where:

- `userStats` = `GET /api/users/users/stats/`
  (the dashboard already calls a users-stats endpoint for the Users page —
  check which one; the users list's own stats live at the URL above)
- `cvSubmissionStats` = `GET /api/cv-submissions/stats/` → `{ "total": 614 }`

Keep the `??` fallbacks so the cards still render if a stats call fails.

### The two new fields (backend, already live after the deploy)

`GET /api/users/users/stats/` now also returns:

```json
{
  "total_seafarers": 625,
  "recent_seafarers_30d": 618
}
```

`total_seafarers` = employees + crew (the same roles the Overview counts).
`recent_seafarers_30d` = those created in the last 30 days.

---

## Note on the users list

`GET /api/users/users/` returns 50 rows per page and the server **ignores
`page_size`** on that endpoint — asking for `?page_size=1000` still gives 50
rows (the `count` field is correct: 630). That is why the page-sized number
was so convincing: 50 rows, 49 seafarers, and a correct-looking total.

Two side notes for whoever picks this up:

- One page of users is **1.8 MB** of JSON. The list endpoint should not be
  asked for all 630 rows just to draw a number — use the stats endpoint.
- The server's `config/settings.py` (not tracked in git, so a
  `git reset --hard` does not touch it) is what actually configures the
  pagination. `saker/settings.py` in the repo says `PAGE_SIZE=50`,
  `PAGE_SIZE_QUERY_PARAM=page_size`, `MAX_PAGE_SIZE=1000`, but the running
  server does not honour `page_size`.
