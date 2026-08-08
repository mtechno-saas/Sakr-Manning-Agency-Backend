# Admin Attachments API

Contract-scoped endpoints for admin-uploaded attachments. Replaces the old
`/api/documents/?user=<applicant>` pattern that mixed admin uploads into the
applicant's CV list.

All endpoints require a valid JWT bearer token. Admin and HR Manager roles
have full access; other roles are blocked by `ContractPermission`.

---

## Base URL

```
https://backend.sakrshipping.com
```

## Auth

```
Authorization: Bearer <access_token>
```

Get a token from `POST /api/login/`.

---

## Nested field

Every contract detail payload now includes an `admin_attachments` array,
sourced from the `Document.contract` FK (migration 0068).

```http
GET /api/contracts/{contract_id}/
```

```json
{
  "id": 20,
  "user": 55,
  "user_name": "ahmed morad abd el kader",
  "company": 3,
  "rank": 12,
  "sign_on_date": "2026-01-01",
  "sign_off_date": "2026-06-01",
  "status": "Active",
  "admin_attachments": [
    {
      "id": 67,
      "user": null,
      "contract": 20,
      "title": "Background check",
      "file": "/media/documents/background_check.pdf",
      "name": null,
      "email": null,
      "phone_number": null,
      "position": null,
      "position_id": null,
      "status": "Pending",
      "generated_id": "DOC-67-XYZ",
      "company": null,
      "company_name": null,
      "job_position": null,
      "job_position_name": null,
      "job_position_details": null,
      "created_at": "2026-08-08T14:30:00Z",
      "updated_at": "2026-08-08T14:30:00Z"
    }
  ],
  ...
}
```

---

## List attachments

```http
GET /api/contracts/{contract_id}/admin-attachments/
```

**Response 200 OK** — JSON array of attachment objects (same shape as
`admin_attachments` field above).

```bash
curl https://backend.sakrshipping.com/api/contracts/20/admin-attachments/ \
  -H "Authorization: Bearer $TOKEN"
```

Empty array if no attachments:

```json
[]
```

---

## Upload attachment

```http
POST /api/contracts/{contract_id}/admin-attachments/
Content-Type: multipart/form-data
```

**Body** (form fields, NOT JSON):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | yes | Human-readable label |
| `file`  | file   | yes | PDF or DOCX, validated server-side |

`user` and `contract` fields in the payload are **ignored** — the contract
is always taken from the URL, so the attachment can never be misrouted
into an applicant's profile.

**Response 201 Created** — full attachment object.

```bash
curl -X POST https://backend.sakrshipping.com/api/contracts/20/admin-attachments/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Background check" \
  -F "file=@./background_check.pdf"
```

**Response 400 Bad Request** — missing title or file:

```json
{ "detail": "Both 'title' and 'file' are required." }
```

**Response 404 Not Found** — contract doesn't exist (or caller can't see it).

---

## Get one attachment

```http
GET /api/contracts/{contract_id}/admin-attachments/{attachment_id}/
```

**Response 200 OK** — full attachment object.

```bash
curl https://backend.sakrshipping.com/api/contracts/20/admin-attachments/67/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response 404 Not Found** — either the contract doesn't exist, the
attachment doesn't exist, or the attachment belongs to a different contract
(intentional: scoping prevents cross-contract access).

---

## Update attachment (rename)

```http
PATCH /api/contracts/{contract_id}/admin-attachments/{attachment_id}/
Content-Type: application/json
```

**Body**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | yes | New title. No file swap — DELETE + re-POST for that. |

**Response 200 OK** — updated attachment object.

```bash
curl -X PATCH https://backend.sakrshipping.com/api/contracts/20/admin-attachments/67/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Renamed attachment"}'
```

**Response 400 Bad Request** — `title` field missing:

```json
{ "detail": "Only the 'title' field can be updated via PATCH." }
```

**Response 404 Not Found** — contract or attachment not found / not owned
by this contract.

---

## Delete attachment

```http
DELETE /api/contracts/{contract_id}/admin-attachments/{attachment_id}/
```

**Response 204 No Content** — success, no body.

```bash
curl -X DELETE https://backend.sakrshipping.com/api/contracts/20/admin-attachments/67/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response 404 Not Found** — contract or attachment not found / not owned
by this contract. The row is NOT deleted in that case (cross-contract
DELETE is rejected).

---

## Attachment object shape

The same object is returned by every endpoint that yields an attachment.
Mirrors `DocumentSerializer.Meta.fields`.

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `user` | int \| null | Always `null` for admin attachments |
| `contract` | int \| null | Always set for admin attachments |
| `title` | string | |
| `file` | string \| null | Relative URL under `/media/`, or `null` if not yet uploaded |
| `name` | string \| null | Legacy CV field, usually `null` for admin attachments |
| `email` | string \| null | Legacy CV field, usually `null` for admin attachments |
| `phone_number` | string \| null | Legacy CV field, usually `null` for admin attachments |
| `position` | string \| null | Legacy CV field, usually `null` for admin attachments |
| `position_id` | int \| null | Legacy CV field, usually `null` for admin attachments |
| `status` | string | "Pending" / "Active" / etc. |
| `generated_id` | string | Server-generated DOC-NNN-XXX code |
| `company` | int \| null | |
| `company_name` | string \| null | |
| `job_position` | int \| null | |
| `job_position_name` | string \| null | |
| `job_position_details` | object \| null | |
| `created_at` | ISO 8601 | |
| `updated_at` | ISO 8601 | |

---

## Error responses

All error responses use this shape:

```json
{ "detail": "Human-readable message" }
```

| Status | When |
|--------|------|
| 400 | Missing required field, validation error |
| 401 | No token / invalid token |
| 403 | Authenticated but not allowed (employee trying to access another contract) |
| 404 | Contract not found, attachment not found, or attachment belongs to a different contract |
| 500 | Server error (check `django_errors.log` on the server) |

---

## Migration / deployment notes

- Migration `0068_document_contract_alter_document_user.py` adds the
  nullable `Document.contract` FK and makes `Document.user` nullable.
  Already applied on production.
- No new migration ships with this change — it only adds endpoints.
- The `DocumentViewSet` endpoint `POST /api/documents/` still works for
  the legacy CV flow; it now also accepts a `contract` field for the
  same admin-attachment purpose. Prefer the new contract-scoped
  endpoints for admin uploads so the UI doesn't need a `userId` prop.
