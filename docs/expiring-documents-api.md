# Expiring Documents API

Aggregator endpoint that lists, creates, and updates all expiring or
expired documents across all users. Combines two source tables:

- 9 expiry-date fields on the `Users` model
- Every `PersonalDocument` row

Read endpoint, plus a convenience write layer that auto-routes to
the right source based on the row's `id` format.

---

## Base URL

```
https://backend.sakrshipping.com
```

## Auth

```
Authorization: Bearer <access_token>
```

Admin or HR Manager role required. Employee and Recruiter return 403.

---

## Methods at a glance

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/expiring-documents/` | List all expiring/expired items |
| `POST` | `/api/expiring-documents/` | Upload a new personal document |
| `PATCH` | `/api/expiring-documents/{id}/` | Update expiry on an existing item |
| `DELETE` | `/api/expiring-documents/{id}/` | Delete a personal document (`pd_<id>` only) |

The `id` in the PATCH/DELETE URL is the same one returned by GET, and
encodes which source table to update:

| `id` pattern | `GET` | `PATCH` | `DELETE` |
|--------------|------|---------|----------|
| `user_<user_id>_<field>` | ✓ | ✓ | ✗ (400) |
| `pd_<doc_id>` | ✓ | ✓ | ✓ |

DELETE on a `user_<id>_<field>` returns 400 — you cannot "delete" a
user-profile field, only clear it. Use PATCH with
`{"expiry_date": null}` to clear.

---

## List — `GET /api/expiring-documents/`

**Query params:**

| Name | Default | Notes |
|------|---------|-------|
| `days` | `30` | Look-ahead window (1–365). Includes items already expired PLUS items expiring in the next N days. |
| `category` | `all` | One of: `expired`, `critical`, `warning`, `notice`, `active`, `all` |

**Response 200 OK:**

```json
{
  "counts": {
    "expired": 3,
    "critical": 7,
    "warning": 12,
    "notice": 28,
    "active": 187,
    "total": 237
  },
  "days_window": 30,
  "today": "2026-08-11",
  "category_filter": "all",
  "results": [
    {
      "id": "user_42_passport_expiry_date",
      "type": "Passport",
      "name": "Passport - ABC123",
      "number": "ABC123",
      "user": "John Smith",
      "userId": 42,
      "userEmail": "john@example.com",
      "userPosition": "Able Seaman",
      "expiryDate": "2026-08-20",
      "daysToExpiry": 9,
      "category": "critical",
      "source": "user_profile"
    },
    {
      "id": "pd_87",
      "type": "Australian Visa Crew",
      "name": "Australian Visa Crew - V-998877",
      "number": "V-998877",
      "user": "Jane Doe",
      "userId": 42,
      "userEmail": "jane@example.com",
      "userPosition": "Master",
      "expiryDate": "2026-09-15",
      "daysToExpiry": 35,
      "category": "notice",
      "source": "personal_document"
    }
  ]
}
```

**Category thresholds:**

| Bucket | `daysToExpiry` |
|--------|---------------|
| `expired` | `< 0` |
| `critical` | `0 – 14` |
| `warning` | `15 – 30` |
| `notice` | `31 – 90` |
| `active` | `> 90` |

**9 expiry fields on Users:**

| Field | Type label | Number field |
|-------|-----------|--------------|
| `passport_expiry_date` | Passport | `passport_no` |
| `seaman_book_expiry_date` | Seaman's Book | `seaman_book_no` |
| `other_seaman_book_expiry_date` | Other Seaman's Book | `other_seaman_book_no` |
| `coc_expiry_date` | Certificate of Competency (COC) | `coc_certificate_number` |
| `goc_expiry_date` | General Operator Certificate (GOC) | `goc_certificate_number` |
| `health_expiry_date` | Health Certificate | `health_number` |
| `international_medical_expiry_date` | International Medical | `international_medical_number` |
| `yellow_fever_expiry_date` | Yellow Fever Vaccination | `yellow_fever_number` |
| `cholera_expiry_date` | Cholera Vaccination | (none) |

---

## Upload — `POST /api/expiring-documents/`

Creates a new `PersonalDocument` row. Multipart form data, same body
as `POST /api/personal-documents/`.

**Required fields:**

| Field | Type | Notes |
|-------|------|-------|
| `user` | int | FK to Users |
| `document_type` | string | Must be one of `PersonalDocument.DOCUMENT_TYPE_CHOICES` (e.g. `"Australian Visa Crew"`) |
| `expiry_date` | date | `YYYY-MM-DD` |
| `file` | file | PDF / DOCX / DOC / JPG / JPEG / PNG |

**Optional fields:** `document_number`, `issue_date`, `issuing_country`, `issued_by`, `place_of_issue`

**Response 201 Created** — full PersonalDocument object.

```bash
curl -X POST 'https://backend.sakrshipping.com/api/expiring-documents/' \
  -H "Authorization: Bearer $TOKEN" \
  -F "user=42" \
  -F "document_type=Australian Visa Crew" \
  -F "document_number=V-998877" \
  -F "expiry_date=2027-01-15" \
  -F "issuing_country=Australia" \
  -F "issued_by=Department of Home Affairs" \
  -F "file=@./visa.pdf"
```

The new row will appear in subsequent GET responses with id
`pd_<new_id>`.

---

## Update — `PATCH /api/expiring-documents/{id}/`

Auto-routes to either `Users` (via the new `admin_attachments`
field) or `PersonalDocument` based on the `id` prefix.

### A. Update a user-profile expiry (`user_<id>_<field>`)

```bash
curl -X PATCH 'https://backend.sakrshipping.com/api/expiring-documents/user_42_passport_expiry_date/' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expiry_date": "2027-01-15"}'
```

The body can be `{"expiry_date": "..."}` (alias) or the canonical
field name (`{"passport_expiry_date": "..."}`).

**Response 200 OK:**
```json
{
  "id": "user_42_passport_expiry_date",
  "source": "user_profile",
  "field": "passport_expiry_date",
  "userId": 42,
  "value": "2027-01-15"
}
```

**400 Bad Request** — unknown field or no value supplied.

### B. Update a personal document (`pd_<id>`)

```bash
curl -X PATCH 'https://backend.sakrshipping.com/api/expiring-documents/pd_87/' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expiry_date": "2027-12-31", "document_number": "V-NEW"}'
```

Any subset of `PersonalDocument` fields. The response is the full
updated row.

**404 Not Found** — user/document doesn't exist.

---

## Delete — `DELETE /api/expiring-documents/{id}/`

Hard-deletes a `PersonalDocument` row. Use it when a visa/PAN/other
personal doc was uploaded by mistake and needs to disappear from
the expiring list.

### A. Delete a personal document (`pd_<id>`)

```bash
curl -X DELETE 'https://backend.sakrshipping.com/api/expiring-documents/pd_87/' \
  -H "Authorization: Bearer $TOKEN"
```

**Response 204 No Content** — row deleted, no body.

### B. `user_<id>_<field>` is rejected (400)

```json
{
  "error": "Cannot DELETE a user_profile row. To clear an expiry date on a user field, use PATCH with {\"expiry_date\": null}."
}
```

---

## Error responses

```json
{ "error": "Only Admin and HR Manager can access this." }
```

| Status | When |
|--------|------|
| 400 | Unknown field, missing value, invalid `id` format |
| 401 | No token / invalid token |
| 403 | Authenticated but role is Employee or Recruiter |
| 404 | User or document not found |
| 500 | Server error |
