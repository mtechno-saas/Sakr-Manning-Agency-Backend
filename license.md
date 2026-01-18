Perfect! I’ll rewrite the **full UserLicense API documentation in GitHub Markdown style**, ready for a README.md or GitHub wiki. It will be clean, structured, and easy to copy-paste.

---

# 🗂 UserLicense API Documentation

Base URL (local development):

```
http://127.0.0.1:8000/api/my-licenses/
```

**Authentication:** JWT Bearer token required for all endpoints

```
Authorization: Bearer <access_token>
```

---

## 1️⃣ List All User Licenses

**Endpoint:**

```
GET /api/my-licenses/
```

**Description:** Retrieve all licenses uploaded by the authenticated user.

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Response Example:**

```json
[
  {
    "id": 4,
    "user": 46,
    "document_name": "Master (Reg. II/2 Par. 1-2)",
    "document_number": "DL-123456",
    "country_of_issue": "Egypt",
    "issue_date": "2026-01-10",
    "expiration_date": "2030-01-10",
    "document_file": "http://127.0.0.1:8000/media/user_46/licenses/YourFileName.pdf",
    "created_at": "2026-01-18T08:50:00.123456Z",
    "updated_at": "2026-01-18T08:50:00.123456Z"
  }
]
```

---

## 2️⃣ Create a New License

**Endpoint:**

```
POST /api/my-licenses/
```

**Description:** Upload a new license for the authenticated user.

**Headers:**

```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body (form-data in Postman):**

| Key              | Value / Type                                       |
| ---------------- | -------------------------------------------------- |
| document_name    | Master (Reg. II/2 Par. 1-2) *(must match choices)* |
| document_number  | DL-123456                                          |
| country_of_issue | Egypt                                              |
| issue_date       | 2026-01-10                                         |
| expiration_date  | 2030-01-10                                         |
| document_file    | <Select PDF file>                                  |

**Response Example:**

```json
{
  "id": 4,
  "user": 46,
  "document_name": "Master (Reg. II/2 Par. 1-2)",
  "document_number": "DL-123456",
  "country_of_issue": "Egypt",
  "issue_date": "2026-01-10",
  "expiration_date": "2030-01-10",
  "document_file": "http://127.0.0.1:8000/media/user_46/licenses/YourFileName.pdf",
  "created_at": "2026-01-18T08:50:00.123456Z",
  "updated_at": "2026-01-18T08:50:00.123456Z"
}
```

---

## 3️⃣ Retrieve a Single License

**Endpoint:**

```
GET /api/my-licenses/<id>/
```

**Description:** Get details of a specific license belonging to the authenticated user.

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Response Example:**

```json
{
  "id": 4,
  "user": 46,
  "document_name": "Master (Reg. II/2 Par. 1-2)",
  "document_number": "DL-123456",
  "country_of_issue": "Egypt",
  "issue_date": "2026-01-10",
  "expiration_date": "2030-01-10",
  "document_file": "http://127.0.0.1:8000/media/user_46/licenses/YourFileName.pdf",
  "created_at": "2026-01-18T08:50:00.123456Z",
  "updated_at": "2026-01-18T08:50:00.123456Z"
}
```

---

## 4️⃣ Update a License

**Endpoint:**

```
PATCH /api/my-licenses/<id>/
```

**Description:** Update specific fields of a license.

**Headers:**

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body Example:**

```json
{
  "document_name": "Master (Reg. II/2 Par. 1-2) Endorsement",
  "document_number": "DL-654321"
}
```

**Response Example:**

```json
{
  "id": 4,
  "user": 46,
  "document_name": "Master (Reg. II/2 Par. 1-2) Endorsement",
  "document_number": "DL-654321",
  "country_of_issue": "Egypt",
  "issue_date": "2026-01-10",
  "expiration_date": "2030-01-10",
  "document_file": "http://127.0.0.1:8000/media/user_46/licenses/YourFileName.pdf",
  "created_at": "2026-01-18T08:50:00.123456Z",
  "updated_at": "2026-01-18T08:55:00.654321Z"
}
```

---

## 5️⃣ Delete a License

**Endpoint:**

```
DELETE /api/my-licenses/<id>/
```

**Description:** Delete a specific license.

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

## 6️⃣ Download License PDF

**Endpoint:**

```
GET /api/my-licenses/<id>/download/
```

**Description:** Download the PDF file of the license.

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Example URL:**

```
GET http://127.0.0.1:8000/api/my-licenses/4/download/
```

**Response:**

* Postman will download the PDF file directly.

---

## 7️⃣ Notes & Tips

* **Document Names:** Must exactly match one of the choices defined in `DOCUMENT_NAME_CHOICES`.
* **File Uploads:** Always use `multipart/form-data` in Postman.
* **Security:** Users can only access their own licenses.
* **Date Format:** `YYYY-MM-DD` for `issue_date` and `expiration_date`.

---

✅ This is **ready to be used as a README.md** or a GitHub Wiki page.

---

If you want, I can also **make a Postman collection JSON** with all these endpoints prefilled so you can **import it directly into Postman and start testing** immediately.

Do you want me to create that Postman collection?
