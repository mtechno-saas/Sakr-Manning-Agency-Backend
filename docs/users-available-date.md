# `available_date` — what it is, where it lives, what `GET /api/users/users/42/` returns

**Date:** 2026-07-27
**Branch:** `server-updates`

This document is a complete map of the `available_date` field on the **Users** model and on the **CVSubmission** aliases, with file:line references for every place it's defined, exposed, validated, and consumed.

---

## TL;DR

`available_date` is a single optional `DateField` on the `Users` model. It represents the date from which the seafarer is available to start a new contract. It is **not** a `DateTimeField`, it has no auto-stamp logic, and the backend exposes it both directly (on the user detail endpoint) and as a write-only alias on the CV submission detail endpoint.

| Endpoint | Field | Where it comes from | Read / Write |
| --- | --- | --- | --- |
| `GET /api/users/users/{id}/` | `available_date` | `Users.available_date` (model column) | read + write |
| `GET /api/cv-submissions/` (list) | `available_date` | alias of `CVSubmission.availability_date` (read-only) | read-only |
| `GET /api/cv-submissions/{id}/` (detail) | `available_date` | write-only alias of `Users.available_date` (i.e. it writes to the linked **user**, not the submission) | write-only |
| `POST /api/users/register/` | `available_date` | `Users.available_date` | write-only |

Two completely different fields share the same JSON key, which is the source of most of the confusion around it. See [§ 5 — the CVSubmission alias trap](#5-the-cvsubmission-alias-trap) below.

---

## 1. Model definition

**File:** `E:\2-TECHNO AQUARE\api\models.py:433`

```python
433  available_date = models.DateField(blank=True, null=True, help_text="Date of availability")
```

- `DateField` — date only, no time component.
- `null=True, blank=True` — fully optional; the column is nullable in the DB and the field is not required at the form layer.
- `help_text="Date of availability"` — surfaced as the field's label in the Django admin and the OpenAPI schema.
- Added in migration `0040_users_application_for_position_users_available_date_and_more.py:55–61` (alongside `application_for_position` and `other_position`).

---

## 2. Where it's exposed in the API

### 2.1 The user detail endpoint — `GET /api/users/users/{id}/`

This is the endpoint you asked about. It uses `UsersSerializer` at `api/serializer.py:1841`. The field is exposed with **no rename and no special handling** — it just falls through to the model field.

**File:** `api/serializer.py:1894–1908` (`UsersSerializer.Meta.fields`)

```python
1894  class Meta:
1895      model = Users
1896      fields = [
1897          'id', 'email', 'first_name', 'middle_name', 'password','country', 'city',
1898          'profile_image', 'age', 'blood_type', 'smoker', 'us_visa_status',
...
1905          'phone_number', 'tel_number', 'created_at', 'updated_at', 'role', "register_code",
1906          'register_date',
1907          'last_updated_date',
1908          'application_for_position', 'other_position', 'available_date',  ← here
...
```

So the live response for `GET https://backend.sakrshipping.com/api/users/users/42/` looks like:

```json
{
  "id": 42,
  "email": "hugh@example.com",
  "first_name": "Hugh",
  "middle_name": "",
  "available_date": "2026-08-15",
  "application_for_position": "Master",
  "other_position": null,
  ...
}
```

Two important notes:

1. **The endpoint requires auth.** `GET /api/users/users/42/` returns `401 {"detail":"Authentication credentials were not provided."}` to an unauthenticated request — confirmed by hitting the live URL.
2. **Date format is ISO `YYYY-MM-DD`.** Because the field is a plain `DateField` with no custom serializer wrapping, DRF's default `DateField.to_representation` emits ISO. `null` if not set.

### 2.2 The user registration endpoint — `POST /api/users/register/`

**File:** `api/serializer.py:2465` (`RegisterSerializer.Meta.fields`)

```python
2465  'application_for_position', 'other_position', 'available_date',
```

The registration serializer uses the same `Users.available_date` model field (no rename). It's exposed **write-only** here, so the field is accepted on the way in but not echoed back on the response.

### 2.3 The alternate user serializer module — `api/serializers.py:83`

There's a **second** `serializers.py` file (note the lowercase `s`) inside `api/`, separate from the one above. It defines its own `Users`-related serializer that uses `FlexibleDateField` and **validates that the date is not in the past**:

**File:** `api/serializers.py:83`

```python
83   available_date = FlexibleDateField(required=False, allow_null=True)
```

**File:** `api/serializers.py:132–135` (the validator)

```python
132  # Validate available date
133  if 'available_date' in attrs and attrs['available_date']:
134      if attrs['available_date'] < today:
135          raise serializers.ValidationError({"available_date": "Available date cannot be in the past"})
```

The `FlexibleDateField` accepts multiple input formats (`YYYY-MM-DD`, `DD-MM-YYYY`, `MM/DD/YYYY`, etc.) and is disambiguated by checking whether the first numeric part is greater than 12.

---

## 3. Where the value is consumed

### 3.1 CV / Seafarer PDF generator

**File:** `api/pdf_generator.py:146–149`

```python
146  ['Height (cm):', _safe(user_data.get('Height_Cm')), 'Weight (kg):', _safe(user_data.get('Weight_Kg'))],
147  ['Rank Code:', _safe(user_data.get('rank_code')), 'Assigned Code:', _safe(user_data.get('assigned_code'))],
148  ['Salary:', _safe(user_data.get('salary')), 'Available Date:', _safe(user_data.get('available_date'))],
149  ]
```

Rendered as the right-hand column in the personal-info table of every generated CV PDF, beside Salary. Uses `_safe(...)` so a `None` is just blank instead of crashing.

### 3.2 Seafarer application CSV importer

**File:** `api/seafarer_application_serializers.py:122–125, 444`

```python
122  if 'available_date' in header:
123      instance.available_date = self._parse_date(header.get('available_date'))
124  elif 'expected_salary_available_date' in header:
125      instance.available_date = self._parse_date(header.get('expected_salary_available_date'))
```

The CSV importer reads the column under either of those two header names and writes it to `Users.available_date`. So if you import seafarer applications from a spreadsheet, either header works.

---

## 4. Validation behaviour summary

| Validation rule | Where | Effect |
| --- | --- | --- |
| `null=True, blank=True` (model) | `api/models.py:433` | Field is optional everywhere. |
| ISO date format expected | `api/serializer.py:1841` (default `DateField`) | Send `YYYY-MM-DD`. |
| `FlexibleDateField` accepts multiple formats | `api/serializers.py:83` | `DD-MM-YYYY`, `MM/DD/YYYY`, `YYYY/MM/DD` all work — the second `serializers.py` module. |
| Cannot be in the past | `api/serializers.py:132–135` | Rejects with `400 {"available_date": "Available date cannot be in the past"}` (only on the serializer that has the validator, not on the main `UsersSerializer`). |

---

## 5. The CVSubmission alias trap

The same JSON key `available_date` is also used as an **alias** on the CV submission endpoints, but it points to a **completely different model field**. This is the single most common source of confusion.

### 5.1 List endpoint — `GET /api/cv-submissions/`

**File:** `api/serializer.py:354` (`CVSubmissionListSerializer`)

```python
354  available_date = serializers.DateField(source='availability_date', read_only=True, default=None)
```

- `source='availability_date'` — **this alias points to `CVSubmission.availability_date`** (`api/models.py:799`), NOT `Users.available_date`.
- `read_only=True` — the field is display-only in the list response.

So the list response can have **two different `available_date` values** depending on which one the client reads:

| Path | What `available_date` returns |
| --- | --- |
| `GET /api/users/users/42/` | The user's own availability date (column on `Users`). |
| `GET /api/cv-submissions/?user=42` | The CV submission's availability date (column on `CVSubmission`). |

If the user submitted multiple CVs with different availability dates, each row can have its own `available_date` that's different from the user's profile-level `available_date`.

### 5.2 Detail endpoint — `GET /api/cv-submissions/{id}/` / `PATCH /api/cv-submissions/{id}/`

**File:** `api/serializer.py:510` (`CVSubmissionSerializer`)

```python
510  available_date = FlexibleDateField(write_only=True, required=False, allow_null=True)
```

- `write_only=True` — never appears in the response.
- It is **popped** out of `validated_data` in the serializer's `create()` / `update()` (line 657: `available_date = validated_data.pop('available_date', None)`) and then written to the **linked user's** `Users.available_date`, not the submission's `availability_date` column.

**File:** `api/serializer.py:678–679`

```python
678  if available_date is not None:
679      user.available_date = available_date
```

So if you `PATCH /api/cv-submissions/123/` with `{"available_date": "2026-09-01"}`, it overwrites `Users.available_date` on the submission's linked user, **not** `CVSubmission.availability_date` (which has its own `availability_date` field at line 507). Two separate fields, two separate columns, same JSON key on different endpoints.

### 5.3 `to_representation` override — yet another twist

**File:** `api/serializer.py:547–550`

```python
547  def to_representation(self, instance):
548      ret = super().to_representation(instance)
549      ret['salary'] = instance.user.salary if instance.user else None
550      ret['available_date'] = instance.user.available_date if instance.user else None
```

Even though `available_date` is declared `write_only=True` in the detail serializer, `to_representation` manually **re-injects** `instance.user.available_date` into the response. So the detail endpoint ALSO returns the user's profile `available_date` in the `available_date` key — alongside the submission's own `availability_date`. Same key, same aliasing behavior, applied at a different layer.

---

## 6. How to actually test it

Quick cURL recipes (the live API requires a JWT — replace `$TOKEN` with a real one):

```bash
# Read a user's available_date
curl -H "Authorization: Bearer $TOKEN" \
     https://backend.sakrshipping.com/api/users/users/42/

# Update a user's available_date
curl -X PATCH \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"available_date": "2026-08-15"}' \
     https://backend.sakrshipping.com/api/users/users/42/

# Same key, different field, on the CV detail endpoint
curl -X PATCH \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"available_date": "2026-09-01"}' \
     https://backend.sakrshipping.com/api/cv-submissions/123/
#  ↑ this writes to Users.available_date, NOT CVSubmission.availability_date
```

The unauthenticated probe (`GET /api/users/users/42/` with no token) returns `401 {"detail":"Authentication credentials were not provided."}` — confirmed.

---

## 7. Field index — every file:line that touches this field

| Concern | File:line |
| --- | --- |
| Model definition | `api/models.py:433` |
| Migration that added it | `api/migrations/0040_users_application_for_position_users_available_date_and_more.py:55–61` |
| User detail serializer (read + write) | `api/serializer.py:1908` (in `Meta.fields`) |
| User registration serializer (write-only) | `api/serializer.py:2465` |
| Alternate user serializer (with past-date validation) | `api/serializers.py:83, 132–135` |
| CV submission LIST alias (read-only, `source='availability_date'`) | `api/serializer.py:354` |
| CV submission DETAIL alias (write-only, writes to `Users.available_date`) | `api/serializer.py:510, 657, 678–679` |
| CV detail `to_representation` (re-injects user's `available_date` into the response) | `api/serializer.py:550` |
| CV detail `fields` list | `api/serializer.py:529` |
| PDF generator (rendered as "Available Date:") | `api/pdf_generator.py:148` |
| Seafarer application CSV import (header `available_date` or `expected_salary_available_date`) | `api/seafarer_application_serializers.py:122–125, 444` |

---

## 8. Gotchas / things to be careful about

1. **Two model columns, one JSON key.** `Users.available_date` and `CVSubmission.availability_date` are both surfaced under the JSON key `available_date` on different endpoints. If you `PATCH /api/cv-submissions/{id}/` with `available_date`, you change the **user's** value, not the submission's. The submission's own value lives under the JSON key `availability_date`.
2. **No auto-stamp.** Unlike `reviewed_date` (which I patched in commit `57d860b` to auto-stamp when `reviewed_by` is set), `available_date` is never auto-set. It only changes if a client explicitly sends it.
3. **Date only, no time.** The field is `DateField`, not `DateTimeField`. The OpenAPI schema reflects this — don't send `T00:00:00Z` or it might get rejected depending on which serializer you're hitting.
4. **Two `serializers.py` modules exist** in the `api/` package: `api/serializer.py` (the big one) and `api/serializers.py` (the small one). Both define `available_date`, but only the small one validates that the date is not in the past. If you ever need past dates to be allowed, the small file is the one to patch.
5. **No tests** for `available_date` round-trip — none of the existing test files (`api/tests.py` doesn't exist on the current branch; only the `reminders/tests.py` and `expiring_documents/tests.py` were created in this session) cover the field. Worth adding a regression test alongside the `reviewed_date` one if you decide to write one.
