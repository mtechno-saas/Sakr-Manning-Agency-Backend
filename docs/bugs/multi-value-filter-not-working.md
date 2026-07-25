# Multi-Value Filter Not Working — `?company=2&company=10` Returns Only One Company's Ships

**Date:** 2026-07-23 (initial bug); 2026-07-23 (extended to Contracts)
**Affected endpoints:** `GET /api/ships/`, `GET /api/contracts/`
**Affected filter params:**
- **Ships:** `company`, `flag`, `ship_type`, `status`
- **Contracts:** `user`, `ship`, `company`, `rank`, `status`, `expiry_status`
- **Likely affected (not yet patched):** interviews, finance, users, companies, CV submissions — anywhere the same `getVal`/`NumberInFilter` pattern was used
**Severity:** Medium — user-facing filter UI silently drops selections

---

## Symptom

On the **Principals & Vessels** page, ticking multiple checkboxes in the **Principal** filter and clicking **Apply Filters** returns only the **last** company's ships, not the union of all selected companies.

| URL | Expected | Actual |
|---|---|---|
| `?company=2&company=10` | 3 ships (both companies) | 1 ship (only `company=10`) |
| `?company=10&company=2` | 3 ships (both companies) | 2 ships (only `company=2`) |

The "last value wins" pattern is the fingerprint of this bug.

### Same bug on the Contracts page

The **Contracts** page (`/contracts/`) had all filters broken — the multi-select User Name, Vessel Name, Contract Status, Principal, and Expiry Status filters all silently dropped to a single value. Even single-value filters looked broken because the comma-joining format the frontend sent (`?user=1,2`) was being parsed as one ID and rejected.

**Workaround while debugging:** typing in the text-search field at the top of the filter (e.g. "go" for AHMED GOMAA) was the only way to filter at all, because that goes through a separate `user_name` field with `icontains`, not the multi-select ID filter.

---

## Root Cause: Two Independent Bugs (one on each side)

The user-facing filter is built on a chain — frontend builds the URL, backend parses the URL, backend applies the filter. In this codebase, **both links of the chain were broken**, and the two bugs were cancelling each other in a confusing way.

### Bug 1 — Frontend: `getVal(v[0])` flattens arrays

**File:** `src/services/Dashboard/shipsApi.js`

```js
const getVal = (v) => (Array.isArray(v) ? v[0] : v);

if (filters.company) params.append("company", getVal(filters.company));
```

When `filters.company = [2, 10]` (a multi-select array), `getVal` silently discards everything except the **first element**. So the URL the browser actually sent was always `?company=2`, regardless of how many checkboxes the user ticked.

**Fix:** Replace with an `appendParam` helper that iterates the array:

```js
const appendParam = (key, value) => {
  if (value === undefined || value === null || value === "") return;
  if (Array.isArray(value)) {
    value.forEach((v) => {
      if (v !== undefined && v !== null && v !== "") params.append(key, v);
    });
  } else {
    params.append(key, value);
  }
};

appendParam("company", filters.company);
// → ?company=2&company=10  ✅
```

### Bug 2 — Frontend: `multiple: true` missing on filter fields

**File:** `src/components/dashboard/Content/Company.jsx`

```js
{
  key: "company",
  label: "Principal",
  type: "select",          // ← no `multiple` flag
  options: (referenceOptions?.companies || []),
},
```

`DataTableSidebar.handleCheckboxChange` has a single-value collapse branch:

```js
else if (newValues.length === 1 && !fields.find(f => f.key === fieldKey)?.multiple)
  newValues = newValues[0];
```

Without `multiple: true`, the first click converts the array `[2]` to a single value `2`. The second click reads the stale single value, and React's state propagation timing means subsequent clicks sometimes read pre-update state — the second click "wins" or the first click "wins" depending on timing, but the result is always one value, never the full array.

**Fix:** Add `multiple: true` to all multi-select fields:

```js
{ key: "company",  type: "select", multiple: true, ... }
{ key: "status",   type: "select", multiple: true, ... }
{ key: "ship_type", type: "select", multiple: true, ... }
```

With this flag, the state stays as an array from the very first click. The single-value collapse branch is bypassed entirely.

### Bug 3 — Backend: `BaseInFilter` only respects last value

**File:** `api/filters.py`

```python
company = NumberInFilter(field_name="company__id", lookup_expr="in")
```

`django_filters.BaseInFilter` is supposed to handle `?key=1&key=2` via `request.GET.getlist(...)`. In the version installed in this project, the parent `Filter.value()` only uses `request.GET.get(...)` — which returns the **last** value. So even with the correct URL, only the last ID was being applied server-side.

**Fix:** Use a method-based filter on the FilterSet that has direct access to `self.request`:

```python
class ShipFilter(django_filters.FilterSet):
    company = django_filters.CharFilter(method="filter_company")
    ...

    def filter_company(self, queryset, name, value):
        # `name` here is the field_name, which can resolve to the DB
        # lookup ('company__id') rather than the URL param ('company').
        # Hardcode the URL param name to be safe.
        all_values = self.request.GET.getlist("company")
        if not all_values:
            return queryset
        ids = [int(v) for v in all_values if str(v).strip().isdigit()]
        if not ids:
            return queryset.none()
        return queryset.filter(company__id__in=ids)
```

---

## Verification

### Backend test (via curl or Postman)

```bash
TOKEN="eyJhbGciOi..."   # your access token
URL="https://backend.sakrshipping.com/api/ships/"

# Should return count=3
curl -s "$URL?company=2&company=10" -H "Authorization: Bearer $TOKEN"
```

Run four quick checks:

| Request | Expected `count` |
|---|---|
| `?` (no filter) | 14 (all ships) |
| `?company=2` | 2 (3 SEAS only) |
| `?company=2&company=10` | 3 (both) ✅ |
| `?company=10&company=2` | 3 (both, order-independent) ✅ |

If `count=3` on the last two, backend is done.

### Frontend test (in browser)

1. `npm run build` in `Sakr-Manning-Agency-Frontend/`
2. Deploy the new `dist/`
3. Hard refresh browser (`Ctrl+Shift+R`)
4. Tick two principals, click **Apply Filters**
5. Open DevTools → Network → click the `ships/` request
6. Confirm URL is `?company=2&company=10&page=1` (both IDs present)
7. Confirm response is `count: 3`

If the URL still has only one `company=` value, the frontend bundle didn't pick up the change — verify the deployed JS contains `appendParam` (not `getVal`).

---

## Deployment Checklist

- [ ] Backend: `git pull` or `rsync api/filters.py` to server
- [ ] Backend: `sudo systemctl restart sakr-backend.service`
- [ ] Backend: run the four curl checks above
- [ ] Frontend: `npm run build` in frontend repo
- [ ] Frontend: deploy new `dist/` to hosting (nginx / S3 / Vercel / etc.)
- [ ] Frontend: hard refresh browser, re-test the multi-select

---

## Lessons Learned

1. **Multi-layer bugs mask each other.** The frontend was sending one value, the backend was parsing the last value. Both bugs "worked together" to produce a consistent (wrong) result. Without testing each layer in isolation, the fix at either side alone would not have worked.

2. **`getVal(v[0])` is a footgun in any API client.** When the source is an array, never silently fall back to `v[0]`. Either iterate, or be explicit about the single-value assumption.

3. **`django_filters.BaseInFilter` is unreliable across versions.** In some installs it correctly calls `getlist()`; in others it inherits the parent's `get()`. When in doubt, write a method-based filter and use `self.request.GET.getlist(...)` directly.

4. **Always test multi-value endpoints with both Postman AND a UI that has the multi-select.** Postman hides frontend bugs. The UI hides backend bugs. You need both.

5. **The `multiple: true` flag is essential for any filter field that uses checkboxes in `DataTableSidebar`.** Without it, the state collapses to a single value after the first click and stays that way — even on subsequent clicks.

6. **`type: "multi-select"` in the filter field definition is NOT enough on its own.** The `DataTableSidebar` checks `field.multiple`, not `field.type`. Both must be set: `type: "multi-select", multiple: true`. Easy to miss.

7. **Comma-joined query strings (`?user=1,2,3`) are NOT compatible with `NumberInFilter`.** Even if the backend were fixed, this URL format would be parsed as one ID `"1,2,3"` and fail validation. The frontend must always use repeated keys (`?user=1&user=2&user=3`).

---

## Related Bugs (Same Pattern, Other Pages)

The same `getVal(v[0])` footgun exists in **at least 4 other API clients** in the frontend. They have not been audited/patched yet — they will exhibit the same "last value wins" bug when their multi-select filters are used. Plan to do a one-pass sweep:

| File | Status | Notes |
|---|---|---|
| `src/services/Dashboard/shipsApi.js` | ✅ Patched | `getVal` → `appendParam` |
| `src/services/Dashboard/documentsApi.js` | ✅ Patched | `appendFilter` rewritten, no more comma-joining |
| `src/services/Dashboard/usersApi.js` | ✅ Already correct | Had proper `appendParam` from the start — no change needed |
| `src/services/Dashboard/companiesApi.js` | ⚠️ Not patched | Has the same `getVal` pattern |
| `src/services/Dashboard/financeApi.js` | ⚠️ Not patched | Has the same `getVal` pattern |
| `src/services/Dashboard/interviewsApi.js` | ⚠️ Not patched | Has the same `getVal` pattern |

The backend side of those endpoints likely has the same `NumberInFilter` problem too, so when the frontend is fixed the corresponding `FilterSet` classes will need the same `_ids_for` method treatment as `ShipFilter` and `ContractFilter`.

### Quick grep to find all instances

```bash
grep -rn "getVal" src/services/Dashboard/
grep -rn "NumberInFilter" api/filters.py
```

The `getVal` grep returns every API client with the same footgun. The `NumberInFilter` grep returns every backend filter that needs the same `filter_X` method rewrite.

### Backend filter status

| Filter class | Status | Notes |
|---|---|---|
| `ShipFilter` (Ships) | ✅ Patched | `filter_company` method with hardcoded URL param name |
| `ContractFilter` (Contracts) | ✅ Patched | `_ids_for` helper + 4 method filters (user, ship, company, rank) |
| `UsersFilter` (Users) | ✅ Patched | `_strings_for` helper + 9 method filters covering all multi-value fields |
| Other filters (interviews, finance, etc.) | ⚠️ Unaudited | Same `_ids_for` treatment will be needed |

---

## Contracts Page — Specific Fix Details

The Contracts page had **all** filters broken, not just the multi-select ones. Three things had to change:

### 1. Backend `ContractFilter` rewrite

**File:** `api/filters.py`

Replaced four `NumberInFilter` declarations with method-based filters that all share a `_ids_for()` helper:

```python
class ContractFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(method="filter_user")
    ship = django_filters.CharFilter(method="filter_ship")
    company = django_filters.CharFilter(method="filter_company_id")
    rank = django_filters.CharFilter(method="filter_rank_id")
    status = django_filters.AllValuesMultipleFilter(field_name="status")  # was already OK

    def _ids_for(self, param_name):
        raw = self.request.GET.getlist(param_name)
        if not raw:
            return None
        ids = [int(v) for v in raw if str(v).strip().isdigit()]
        if not ids:
            return []
        return ids

    def filter_user(self, queryset, name, value):
        ids = self._ids_for("user")
        if ids is None: return queryset
        if not ids: return queryset.none()
        return queryset.filter(user__id__in=ids)

    def filter_ship(self, queryset, name, value):
        ids = self._ids_for("ship")
        if ids is None: return queryset
        if not ids: return queryset.none()
        return queryset.filter(ship__id__in=ids)

    def filter_company_id(self, queryset, name, value):
        ids = self._ids_for("company")
        if ids is None: return queryset
        if not ids: return queryset.none()
        return queryset.filter(company__id__in=ids)

    def filter_rank_id(self, queryset, name, value):
        ids = self._ids_for("rank")
        if ids is None: return queryset
        if not ids: return queryset.none()
        return queryset.filter(rank__id__in=ids)
```

`status` and `expiry_status` were already using `AllValuesMultipleFilter` so they don't need this treatment.

### 2. Frontend API client `appendFilter` rewrite

**File:** `src/services/Dashboard/documentsApi.js`

The old helper was inconsistent: for `status` and `expiry_status` it correctly repeated keys, but for every other array filter it **comma-joined** the values — which `NumberInFilter` would have failed on even if it worked. The new helper always repeats keys:

```js
const appendFilter = (key, value) => {
  if (value === undefined || value === null || value === "") return;
  if (Array.isArray(value)) {
    value.forEach((v) => {
      if (v !== undefined && v !== null && v !== "") params.append(key, v);
    });
  } else {
    params.append(key, value);
  }
};
```

### 3. Frontend filter fields `multiple: true` flag

**File:** `src/components/dashboard/Content/Documents.jsx`

Every `multi-select` field in `filterFields` got `multiple: true` added:

```js
{ key: "user",         type: "multi-select", multiple: true, ... }
{ key: "ship",         type: "multi-select", multiple: true, ... }
{ key: "status",       type: "multi-select", multiple: true, ... }
{ key: "company",      type: "multi-select", multiple: true, ... }
{ key: "expiry_status",type: "multi-select", multiple: true, ... }
```

### Verification (Contracts)

Postman:

| Request | Expected behavior |
|---|---|
| `?user=1&user=2` | All contracts for both user IDs (not 0 results from `1,2` parsing) |
| `?status=Active&status=Expired` | All Active OR Expired contracts |
| `?user=1,2` (old format) | Returns 0 — confirms the comma format is rejected, so the frontend must be sending repeated keys |

Browser: tick two seafarers in the Contracts page filter, click Apply, and the table should narrow to the union.

---

## Users Page — Specific Fix Details

The Users page (`/users/users/`) had **~12 broken multi-select filters** out of ~30 total filters. The page has a much larger surface area than Ships or Contracts (multiple sections: Personal Info, Professional Details, Assignment & Vessels, Contract Details, Documentation, Status).

### Multi-select filters that needed `multiple: true` (frontend)

In `src/components/dashboard/Content/Users.jsx`, every `type: "multi-select"` field needed `multiple: true` added:

```js
// Personal Information
{ key: "marital_status", type: "multi-select", multiple: true, ... }
{ key: "user_status",    type: "multi-select", multiple: true, ... }
{ key: "nationality",    type: "multi-select", multiple: true, ... }

// Professional Details
{ key: "rank_name",      type: "multi-select", multiple: true, ... }
{ key: "role",           type: "multi-select", multiple: true, ... }
{ key: "position",       type: "multi-select", multiple: true, ... }

// Assignment & Vessels
{ key: "company_name",   type: "multi-select", multiple: true, ... }
{ key: "ship_name",      type: "multi-select", multiple: true, ... }
{ key: "company_type",   type: "multi-select", multiple: true, ... }
{ key: "ship_type",      type: "multi-select", multiple: true, ... }

// Contract Details
{ key: "contract_status", type: "multi-select", multiple: true, ... }

// Documentation
{ key: "document_type",   type: "multi-select", multiple: true, ... }
```

### Backend `UsersFilter` rewrite

In `api/filters.py`, the `UsersFilter` was the biggest FilterSet. Two patterns needed fixing:

**Pattern A — was using `CharInFilter` (broken in this django-filter version):**
- `user_status` — was `CharInFilter(field_name="user_status", lookup_expr="in")`
- `nationality` — was `CharInFilter(field_name="nationality", lookup_expr="in")`
- `role` — was `CharInFilter(field_name="role", lookup_expr="in")`
- `contract_status` — was `CharInFilter(field_name="contracts__status", lookup_expr="in")`

**Pattern B — was a single-value `CharFilter` but the frontend sends an array:**
- `marital_status` — was `CharFilter(field_name="marital_status", lookup_expr="iexact")` (single value)
- `company_type` — was `CharFilter(field_name="contracts__company__company_type__name", lookup_expr="icontains")`
- `ship_type` — was `CharFilter(field_name="contracts__ship__ship_type__name", lookup_expr="icontains")`
- `document_type` — was `CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")`

**Pattern C — was single-ID `NumberFilter` but the frontend can send an array:**
- `company` — was `NumberFilter(field_name="contracts__company__id", lookup_expr="exact")`
- `ship` — was `NumberFilter(field_name="contracts__ship__id", lookup_expr="exact")`

All of these were rewritten as method-based filters that share a `_strings_for` helper (or inline ID-parsing for the ID filters):

```python
def _strings_for(self, param_name):
    """Pull repeated ?key=1&key=2 values from the request as strings."""
    raw = self.request.GET.getlist(param_name)
    if not raw:
        return None
    cleaned = [v.strip() for v in raw if v is not None and str(v).strip() != ""]
    return cleaned if cleaned else []

def filter_user_status(self, queryset, name, value):
    vals = self._strings_for("user_status")
    if vals is None: return queryset
    if not vals: return queryset.none()
    return queryset.filter(user_status__in=vals)
# ...same pattern for marital_status, nationality, role, contract_status,
#    company_type, ship_type, document_type...
```

For the ID filters (`company`, `ship`):

```python
def filter_company(self, queryset, name, value):
    ids = [int(v) for v in self.request.GET.getlist("company") if str(v).strip().isdigit()]
    if not ids:
        return queryset
    return queryset.filter(contracts__company__id__in=ids).distinct()
```

The `.distinct()` is important when filtering across a M2M-style relationship (a user with multiple contracts) — otherwise the same user appears N times.

### Text-search fields were left alone

These still use `CharFilter(field_name=..., lookup_expr="icontains")` and accept a single string:
- `name` (custom method, splits on commas)
- `age` (number)
- `nearest_port` (icontains)
- `language` (custom method)
- `rank_name` (icontains via `codes__name`)
- `assigned_code` (icontains)
- `company_name` (icontains via `contracts__company__company_name`)
- `ship_name` (icontains via `contracts__ship__ship_name`)
- `job_position_name` (icontains)
- `course_name` (icontains)
- `passport_no`, `seaman_book_no`, `medical_no` (icontains)
- `document_status` (iexact), `document_title` (icontains)
- `position` (custom method)

These are typed as `text` in the frontend (not `multi-select`), so they only ever receive a single string. No change needed.

### Verification (Users)

Postman:

| Request | Expected |
|---|---|
| `?user_status=ON_SITE&user_status=VACATION` | Users with either status (not just the last value) |
| `?nationality=Egypt&nationality=Albania` | Users from either country |
| `?marital_status=SINGLE&marital_status=MARRIED` | Users who are single OR married |
| `?contract_status=Active&contract_status=Expired` | Users with Active OR Expired contracts |
| `?role=Employee&role=Crew` | Users with either role |

Browser: tick two nationalities, two user statuses, two contract statuses, etc., and the table should narrow to the union.
