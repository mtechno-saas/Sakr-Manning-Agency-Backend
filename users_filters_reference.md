# Users — Filter Reference

Complete reference for every query parameter supported by `GET /api/users/users/`. The endpoint is powered by `UsersFilter` in `api/filters.py` (django-filter).

---

## 1. Endpoint

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/users/users/` |
| **Auth** | `Authorization: Bearer <token>` (required) |
| **Permissions** | `Admin` / `HR Manager` / `Recruiter` see everyone; `Employee` sees only their own record |
| **Backend** | `api.views.UserViewSet` (DRF `ModelViewSet` with `UsersFilter`) |
| **Pagination** | `PageNumberPagination` (default page size 25) |

---

## 2. Pagination

Standard DRF envelope. `next` / `previous` are `null` on the first/last page.

| Query param | Default | Notes |
|---|---|---|
| `page` | `1` | 1-indexed |
| `page_size` | server default | Per-page count override |

**Response envelope:**

```json
{
  "count": 568,
  "next": "http://127.0.0.1:8000/api/users/users/?page=2",
  "previous": null,
  "results": [ /* UsersSerializer objects */ ]
}
```

---

## 3. Three input formats the backend accepts

Most list-style filters accept any of these. The backend uses `QueryArrayWidget` to split all three.

| Format | Example |
|---|---|
| Single value | `?user_status=ON_SITE` |
| Repeated keys | `?user_status=ON_SITE&user_status=VACATION` |
| Array notation | `?user_status[]=ON_SITE&user_status[]=VACATION` |
| CSV (single key) | `?user_status=ON_SITE,VACATION` |

> **`?user_status=ON_SITE&user_status=VACATION` vs `?user_status=ON_SITE,VACATION`**
> Both return identical results. The frontend uses repeated keys because that's what the
> multi-select component produces.

---

## 4. Case-sensitivity rules

| Lookup | Case-sensitive? | Example |
|---|---|---|
| `iexact` / `icontains` (free-text fields) | **No** | `?name=ahmed` matches `Ahmed` |
| `in` (used by `user_status`, `nationality`, `role`, `contract_status`, `ship_type`) | **Yes** | `?user_status=ON_SITE` matches `ON_SITE` only, not `On Site` |
| `IexactInFilter` (used by `marital_status`) | **No** | `?marital_status=SINGLE` matches `Single` |

> **Why `marital_status` is special:** the DB stores `'Single'` / `'Married'` (title case)
> but the frontend sends `'SINGLE'` / `'MARRIED'`. Plain `in` is case-sensitive and would
> return 0. `IexactInFilter` (a custom class in `api/filters.py`) does an OR of per-value
> `iexact` lookups instead.

---

## 5. Section: Personal Information

> Mirrors the "Filter Users" modal in the frontend.

### 5.1 `?name=` — First Name (multi-source)

Searches `first_name` + `middle_name` + `email`. Accepts comma-separated values; multi-word
values match `first_name=A` + `middle_name=B`.

```http
GET /api/users/users/?name=ahmed
GET /api/users/users/?name=ahmed,mohamed        # either term
GET /api/users/users/?name=ahmed ali            # first="ahmed" + middle="ali"
```

**Response (200):**
```json
{
  "count": 14,
  "next": null,
  "previous": null,
  "results": [
    { "id": 105, "first_name": "Ahmed", "middle_name": "Ali", "email": "ahmed.ali@example.com", ... }
  ]
}
```

---

### 5.2 `?age=` — Age (exact match)

```http
GET /api/users/users/?age=32
```

**Response (200):**
```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    { "id": 212, "age": 32, "first_name": "Mahmoud", ... }
  ]
}
```

> No range support yet. If you need "age between 25 and 40", `?age_from=25&age_to=40` is
> the next thing to add — say the word.

---

### 5.3 `?marital_status=` — Marital Status (multi-value, case-insensitive)

```http
GET /api/users/users/?marital_status=SINGLE                        # single value
GET /api/users/users/?marital_status=SINGLE,MARRIED                # CSV
GET /api/users/users/?marital_status=SINGLE&marital_status=MARRIED # repeated keys
GET /api/users/users/?marital_status[]=SINGLE&marital_status[]=MARRIED  # array notation
GET /api/users/users/?marital_status=Single                        # title case also works
```

**Response (200):**
```json
{
  "count": 568,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "marital_status": "Single", "first_name": "Mahmoud", ... },
    { "id": 2, "marital_status": "Married", "first_name": "Sara", ... }
  ]
}
```

> Values are case-insensitive on input. Output is whatever's in the DB (title case:
> `"Single"`, `"Married"`).

---

### 5.4 `?user_status=` — User Status (multi-value, case-sensitive)

```http
GET /api/users/users/?user_status=ON_SITE                          # one status
GET /api/users/users/?user_status=ON_SITE&user_status=VACATION     # two statuses
GET /api/users/users/?user_status=ON_SITE,VACATION,MEDICAL%20VACATION
```

**Response (200):**
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    { "id": 105, "user_status": "ON_SITE", "first_name": "Mohamed", ... }
  ]
}
```

> The DB stores `ON_SITE` / `VACATION` / `MEDICAL VACATION` in upper case, which matches
> the frontend's option values exactly. The filter is case-sensitive; do not send
> `"On Site"` (with a space) — it will return 0.

---

### 5.5 `?nationality=` — Nationality (multi-value)

```http
GET /api/users/users/?nationality=Egyptian
GET /api/users/users/?nationality=Egyptian&nationality=Syrian
GET /api/users/users/?nationality[]=Egyptian&nationality[]=Syrian
```

**Response (200):**
```json
{
  "count": 47,
  "next": null,
  "previous": null,
  "results": [
    { "id": 12, "nationality": "Egyptian", "first_name": "Ahmed", ... },
    { "id": 33, "nationality": "Syrian",   "first_name": "Omar",  ... }
  ]
}
```

---

### 5.6 `?nearest_port=` — Nearest Port (icontains)

```http
GET /api/users/users/?nearest_port=Alexandria
```

**Response (200):**
```json
{
  "count": 23,
  "next": null,
  "previous": null,
  "results": [
    { "id": 5, "Nearest_Port": "Alexandria, Egypt", "first_name": "Yusuf", ... }
  ]
}
```

---

### 5.7 `?language=` — Language (multi-source)

Searches four places:
- `LanguageProficiency.language` (M2M via `user.languages`)
- `UserLanguage.language` (M2M via `user.user_languages`)
- `User.english_language_level` (free-text, e.g. `"B2"`, `"Fluent"`)
- `User.other_language` (free-text)

```http
GET /api/users/users/?language=English
GET /api/users/users/?language=Arabic
GET /api/users/users/?language=B2                # matches english_language_level
```

**Response (200):**
```json
{
  "count": 89,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 105,
      "first_name": "Ahmed",
      "english_language_level": "B2",
      "other_language": "Arabic",
      "languages": [
        { "id": 1, "language": "English", "cefr_level": "B2" }
      ],
      ...
    }
  ]
}
```

---

### 5.8 `?has_language=` — has any language? (boolean)

`true` returns users with **at least one** language record (any of the four sources above).
`false` returns users with **no** language records at all.

```http
GET /api/users/users/?has_language=true
GET /api/users/users/?has_language=false
```

**Response (200, `?has_language=true`):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "Mahmoud",
      "english_language_level": "B2",
      "languages": [
        { "id": 1, "language": "English", "cefr_level": "B2" }
      ],
      ...
    }
  ]
}
```

**Response (200, `?has_language=false`):**
```json
{
  "count": 567,
  "next": null,
  "previous": null,
  "results": [
    { "id": 2, "first_name": "Sara", "english_language_level": null, "languages": [], ... }
  ]
}
```

> Note: the boolean is parsed by `forms.BooleanField`, so `true` / `false` / `True` /
> `False` all work. `1` / `0` are also accepted.

---

## 6. Section: Professional Details

### 6.1 `?rank_name=` — Rank / Position (multi-source)

Searches six places in one query:
- `User.codes` (M2M) → `codes__name`
- `UserRank.rank.name`
- `SeaService.rank` (free-text)
- `Contract.rank.name`
- `User.application_for_position` (legacy)
- `User.position` (synced from `Document.position`)

```http
GET /api/users/users/?rank_name=A.B
GET /api/users/users/?rank_name=Chief%20Officer
```

**Response (200):**
```json
{
  "count": 183,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "first_name": "Mahmoud", "position": "A.B", "codes": [...], ... }
  ]
}
```

---

### 6.2 `?assigned_code=` — Assigned Code

```http
GET /api/users/users/?assigned_code=ABC123
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    { "id": 105, "first_name": "Ahmed", "user_ranks": [{ "assigned_code": "ABC123", ... }] }
  ]
}
```

---

### 6.3 `?role=` — User Role (multi-value)

```http
GET /api/users/users/?role=Admin
GET /api/users/users/?role=Admin&role=HR%20Manager
```

**Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "role": "Admin", "first_name": "Mahmoud", ... },
    { "id": 2, "role": "HR Manager", "first_name": "Sara", ... }
  ]
}
```

> The DB stores `"HR Manager"` with a literal space. URL-encode it as `%20` in the query
> string. The lookup is case-sensitive — do not send `"admin"` in lowercase.

---

### 6.4 `?position=` — General Position

Multi-source: `codes.name` + `application_for_position` + `position`.

```http
GET /api/users/users/?position=Chief%20Officer
```

**Response (200):**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    { "id": 5, "first_name": "Omar", "position": "Chief Officer", ... }
  ]
}
```

---

### 6.5 `?course_name=` — Marine Course

```http
GET /api/users/users/?course_name=STCW
```

**Response (200):**
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    { "id": 3, "first_name": "Yusuf", "courses": [{ "course_name": "STCW Basic Safety", ... }] }
  ]
}
```

---

## 7. Section: Assignment & Vessels

### 7.1 `?company=` — Company (ID or name)

```http
GET /api/users/users/?company=5                # numeric id
GET /api/users/users/?company=ROMALEX%20MARINE # name (icontains)
GET /api/users/users/?company=ROMALEX          # partial
```

**Response (200):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 105,
      "first_name": "Ahmed",
      "contracts": [
        { "company": { "id": 5, "company_name": "ROMALEX MARINE", ... } }
      ]
    }
  ]
}
```

---

### 7.2 `?company_name=` — Company Name (multi-source)

Searches both `Company.company_name` (via `Contract.company`) and `SeaService.company_name` (free-text).

```http
GET /api/users/users/?company_name=ROMALEX%20MARINE
GET /api/users/users/?company_name=ROMALEX
```

**Response (200):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "first_name": "Mahmoud", ... },
    { "id": 2, "first_name": "Sara",   ... }
  ]
}
```

> This is the filter that returned 0 users before the `SeaService.company_name` source
> was added — `ROMALEX MARINE` doesn't exist in the `Company` table, only in the
> free-text `SeaService.company_name` column. The fix is the OR'd Q expression in
> `filter_by_company_name`.

---

### 7.3 `?ship=` — Ship (ID or name)

```http
GET /api/users/users/?ship=5                # numeric id
GET /api/users/users/?ship=Northern%20Star  # name (icontains)
GET /api/users/users/?ship=Northern         # partial
GET /api/users/users/?ship=1234             # numeric, won't match names containing "1234"
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 212,
      "first_name": "Hassan",
      "contracts": [{ "ship": { "id": 5, "ship_name": "Northern Star", ... } }]
    }
  ]
}
```

---

### 7.4 `?ship_name=` — Ship Name (icontains)

Direct FK traversal. Same effect as `?ship=<name>` but always uses icontains.

```http
GET /api/users/users/?ship_name=Star
```

**Response (200):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [ /* 2 users with ship_name icontains "Star" */ ]
}
```

---

### 7.5 `?company_type=` — Company Type

```http
GET /api/users/users/?company_type=Owner
```

**Response (200):**
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [ /* users whose contracts.company.company_type.name contains "Owner" */ ]
}
```

---

### 7.6 `?ship_type=` — Ship Type (multi-value)

```http
GET /api/users/users/?ship_type=Bulk%20Carrier
GET /api/users/users/?ship_type=Bulk%20Carrier&ship_type=Tanker
```

**Response (200):**
```json
{
  "count": 14,
  "next": null,
  "previous": null,
  "results": [ /* users with that ship type on at least one contract */ ]
}
```

---

### 7.7 `?job_position_name=` — Job Position (rank on contract)

```http
GET /api/users/users/?job_position_name=Chief%20Officer
```

**Response (200):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [ /* users with that rank on any contract */ ]
}
```

---

## 8. Section: Contract Details

### 8.1 `?contract_status=` — Contract Status (multi-value)

**Valid values (case-sensitive):** `Pending`, `Draft`, `Signed`, `Active`, `Completed`, `Terminated`

```http
GET /api/users/users/?contract_status=Active
GET /api/users/users/?contract_status=Active&contract_status=Signed
GET /api/users/users/?contract_status=Pending
GET /api/users/users/?contract_status=Pending&contract_status=Active
```

**Response (200, `?contract_status=Pending`):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 4,
      "first_name": "Mahmoud",
      "contracts": [
        { "id": 1, "status": "Pending", "sign_on_date": "2026-06-01", "sign_off_date": null, ... }
      ]
    }
  ]
}
```

> **Frontend dropdown vs. DB — known mismatch (as of this writing):**
> The frontend `Filter Users` modal only offers `Draft` / `Signed` / `Active` /
> `Completed` / `Terminated` (`Sakr-Manning-Agency-Frontend/src/components/dashboard/Content/Users.jsx`),
> but the backend `Contract.status` field also accepts `Pending`. A user who picks
> `Active` from the dropdown will get 0 results if the only matching contracts are
> `Pending`. **Fix:** add `Pending` to the frontend dropdown options, OR normalise
> existing DB records to the standard set.

---

### 8.1.1 `?contract_status=` case-sensitivity cheat sheet

| Query | Matches DB row with `status = "Active"`? | Matches DB row with `status = "active"`? |
|---|---|---|
| `?contract_status=Active` | yes | no |
| `?contract_status=active` | no | yes |
| `?contract_status=ACTIVE` | no | no |
| `?contract_status=Active,Pending` | yes (OR'd) | no |

> The lookup is `IN (...)` under the hood, which is case-sensitive in MySQL/PostgreSQL.
> The values must match the DB row exactly.

---

### 8.2 `?signed_on_from=` / `?signed_on_to=` — Sign-on Date Range

```http
GET /api/users/users/?signed_on_from=2024-01-01
GET /api/users/users/?signed_on_to=2024-12-31
GET /api/users/users/?signed_on_from=2024-01-01&signed_on_to=2024-12-31
```

**Response (200):**
```json
{
  "count": 41,
  "next": null,
  "previous": null,
  "results": [ /* users with at least one contract whose sign_on_date is in range */ ]
}
```

---

### 8.3 `?signed_off_from=` / `?signed_off_to=` — Sign-off Date Range

```http
GET /api/users/users/?signed_off_from=2023-06-01
GET /api/users/users/?signed_off_to=2023-12-31
GET /api/users/users/?signed_off_from=2023-06-01&signed_off_to=2023-12-31
```

**Response (200):**
```json
{
  "count": 17,
  "next": null,
  "previous": null,
  "results": [ /* users with at least one contract whose sign_off_date is in range */ ]
}
```

---

## 9. Section: Documentation

### 9.1 `?passport_no=` — Passport Number

```http
GET /api/users/users/?passport_no=A1234567
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "first_name": "Mahmoud", "passport_no": "A1234567", ... }
  ]
}
```

---

### 9.2 `?passport_type=` — Passport Document Type

```http
GET /api/users/users/?passport_type=Passport
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [ /* users whose personal_documents contains type icontains "Passport" */ ]
}
```

---

### 9.3 `?passport_expiry_from=` / `?passport_expiry_to=` — Passport Expiry

```http
GET /api/users/users/?passport_expiry_from=2025-01-01
GET /api/users/users/?passport_expiry_to=2026-12-31
GET /api/users/users/?passport_expiry_from=2025-01-01&passport_expiry_to=2026-12-31
```

**Response (200):**
```json
{
  "count": 312,
  "next": null,
  "previous": null,
  "results": [ /* users with passport_expiry_date in range */ ]
}
```

---

### 9.4 `?seaman_book_no=` — Seaman Book Number

```http
GET /api/users/users/?seaman_book_no=SB-987654
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "first_name": "Mahmoud", "seaman_book_no": "SB-987654", ... }
  ]
}
```

---

### 9.5 `?seaman_book_type=` — Seaman Book Document Type

```http
GET /api/users/users/?seaman_book_type=Seaman%20Book
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [ /* users whose personal_documents contains type icontains "Seaman Book" */ ]
}
```

---

### 9.6 `?seaman_book_expiry_from=` / `?seaman_book_expiry_to=` — Seaman Book Expiry

```http
GET /api/users/users/?seaman_book_expiry_from=2025-01-01
GET /api/users/users/?seaman_book_expiry_to=2026-12-31
```

**Response (200):**
```json
{
  "count": 280,
  "next": null,
  "previous": null,
  "results": [ /* users with seaman_book_expiry_date in range */ ]
}
```

---

### 9.7 `?medical_no=` — Medical Number (multi-source)

Searches four separate number fields on the User model — none of them are on
`PersonalDocument` (that table only holds travel/ID docs: Passport, Seaman's
Book, Visa, etc.):

| Source field | Doc type |
|---|---|
| `User.health_number` | General health certificate |
| `User.international_medical_number` | International Medical Certificate |
| `User.yellow_fever_number` | Yellow fever vaccination |
| `User.cholera_number` | Cholera vaccination |

A user matches if **any** of the four contains the value (icontains).

```http
GET /api/users/users/?medical_no=02734
GET /api/users/users/?medical_no=H-12345
GET /api/users/users/?medical_no=YF
```

**Response (200, `?medical_no=02734`):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "Ahmed",
      "health_number": null,
      "international_medical_number": "02734",
      "yellow_fever_number": null,
      "cholera_number": null,
      ...
    }
  ]
}
```

> **Data state (as of this writing):** of 568 users, 1 has
> `international_medical_number` set, 0 have the other three. Once seafarers
> start getting `health_number` / `yellow_fever_number` / `cholera_number`
> populated, this single filter will find all of them without code changes.

---

### 9.8 `?medical_expiry_from=` / `?medical_expiry_to=` — Medical Expiry (multi-source)

Same multi-source idea, but for the **expiry date** of each medical cert. The
`from` / `to` direction is inferred from the filter name (`_from` → `gte`,
`_to` → `lte`). A user matches if **any** of the four expiry dates falls in
the range.

| Source field | Doc type |
|---|---|
| `User.health_expiry_date` | General health certificate |
| `User.international_medical_expiry_date` | International Medical Certificate |
| `User.yellow_fever_expiry_date` | Yellow fever vaccination |
| `User.cholera_expiry_date` | Cholera vaccination |

```http
GET /api/users/users/?medical_expiry_from=2020-01-01
GET /api/users/users/?medical_expiry_to=2030-12-31
GET /api/users/users/?medical_expiry_from=2025-01-01&medical_expiry_to=2026-12-31
```

**Response (200, `?medical_expiry_from=2020-01-01`):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "Ahmed",
      "international_medical_expiry_date": "2023-08-04",
      "health_expiry_date": null,
      "yellow_fever_expiry_date": null,
      "cholera_expiry_date": null,
      ...
    }
  ]
}
```

> **Combining `_from` and `_to`:** the two filters are AND'd. So
> `?medical_expiry_from=2020-01-01&medical_expiry_to=2026-12-31` matches a
> user only if at least one of their four medical expiry dates falls in
> `[2020-01-01, 2026-12-31]`. Different expiry dates in different fields
> don't combine to create a "wide" match — each user is checked
> independently.

---

### 9.9 `?document_type=` — General Document Type

```http
GET /api/users/users/?document_type=Certificate
```

**Response (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "first_name": "Mahmoud", "personal_documents": [{ "document_type": "Certificate", ... }] }
  ]
}
```

---

## 10. Section: Status

### 10.1 `?is_blacklisted=` — Blacklisted Only (boolean)

```http
GET /api/users/users/?is_blacklisted=true
GET /api/users/users/?is_blacklisted=false
GET /api/users/users/?is_blacklisted=1
```

**Response (200, `?is_blacklisted=true`):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    { "id": 412, "first_name": "Omar", "is_blacklisted": true, ... }
  ]
}
```

---

## 11. Combining filters

All filters are AND-combined. Within a single filter, multi-value inputs are OR-combined.

```http
# Married, on vacation, Egyptian, has any English skill
GET /api/users/users/\
  ?marital_status=MARRIED\
  &user_status=VACATION\
  &nationality=Egyptian\
  &language=English
```

**Response (200):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 17,
      "first_name": "Mahmoud",
      "marital_status": "Married",
      "user_status": "VACATION",
      "nationality": "Egyptian",
      "english_language_level": "C1",
      ...
    }
  ]
}
```

---

## 12. Quick curl / PowerShell reference

**bash:**
```bash
curl "http://127.0.0.1:8000/api/users/users/?user_status=ON_SITE&user_status=VACATION" \
  -H "Authorization: Bearer $token"
```

**PowerShell (line-continuation with backtick):**
```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl "http://127.0.0.1:8000/api/users/users/?user_status=ON_SITE&user_status=VACATION" `
  -H "Authorization: Bearer $token"
```

**PowerShell (single line):**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/users/?user_status=ON_SITE" -Headers @{ Authorization = "Bearer $token" } | Select-Object -ExpandProperty count
```

---

## 13. Implementation reference

| File | What lives there |
|---|---|
| `api/filters.py` | `UsersFilter` + the three custom filter classes (`CharInFilter`, `NumberInFilter`, `IexactInFilter`) |
| `api/views.py` | `UserViewSet` (line 206) — wires `UsersFilter` to the viewset and applies role-based `get_queryset` |
| `api/urls.py` | `router.register(r'users', UserViewSet)` — produces `/api/users/users/` |
| `api/serializers.py` | `UserSerializer` (line 68) — full payload returned in `results` |

If you change a filter, update the row in the table above AND this section so the next
person doesn't have to re-derive the map from the code.
