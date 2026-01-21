
## Allowed Vaccine Choices

The `name` field **must be one of the following values**:

```
QUARANTINE LETTER
RUBELLA IMMUNITY
TESSERA SANITARIA
TUBERCULOSIS_LAB_SCREEN
TYPHOID_VACCINATION
VARICELLA_IMMUNIZATION
YELLOW_FEVER_IMMUNIZATION
CHICKENPOX_IMMUNITY_SCREENING
COLOR_VISION_CERTIFICATE
COVID_SARS_VACCINATION
COVID_FORM
FOODHANDLER_EXAMS
HEALTH_QUESTIONNAIRE
HEPATITIS_A_IMMUNIZATION
HEPATITIS_B_IMMUNIZATION
ITALIAN_MEDICAL_PRE_EMBARK
MEASLES_IMMUNITY
MEDICAL_CERT_SEAFARERS
MMR_BOOSTER_2
MMR_VACC_IMMUNIZATION
MUMPS_IMMUNITY
PERTUSSIS_IMMUNIZATION
```

---

## Vaccination Object Schema

| Field       | Type     | Description                         |
| ----------- | -------- | ----------------------------------- |
| id          | integer  | Vaccination ID                      |
| user        | integer  | Owner user ID (auto-assigned)       |
| name        | string   | Vaccine type (from allowed choices) |
| number      | string   | Certificate / document number       |
| issue_date  | date     | Issue date                          |
| expiry_date | date     | Expiry date                         |
| issued_by   | string   | Issuing authority                   |
| issued_at   | string   | Place of issue                      |
| disease     | string   | Related disease                     |
| first_date  | date     | First dose date                     |
| last_date   | date     | Last / booster dose date            |
| remarks     | string   | Additional notes                    |
| document    | file     | PDF document (nullable)             |
| created_at  | datetime | Record creation timestamp           |
| updated_at  | datetime | Last update timestamp               |

---

## 1. List Vaccinations

Returns **only vaccinations belonging to the logged-in user**.

### Endpoint

```
GET /vaccinations/
```

### Response `200 OK`

```json
[
  {
    "id": 1,
    "name": "YELLOW_FEVER_IMMUNIZATION",
    "number": "YF-2024-001",
    "issue_date": "2026-01-10",
    "expiry_date": "2030-01-10",
    "issued_by": "Ministry of Health",
    "issued_at": "Cairo",
    "disease": "Yellow Fever",
    "first_date": "2024-05-01",
    "last_date": "2024-05-01",
    "remarks": "Travel requirement",
    "document": null,
    "created_at": "2026-01-21T16:14:44.525941Z",
    "updated_at": "2026-01-21T16:14:44.525984Z",
    "user": 46
  }
]
```

---

## 2. Create Vaccination

Creates a vaccination **linked automatically to the authenticated user**.

### Endpoint

```
POST /vaccinations/
```

### Body

Use **form-data** (required for file upload).

| Field       | Type              | Required |
| ----------- | ----------------- | -------- |
| name        | string            | yes      |
| number      | string            | no       |
| issue_date  | date (YYYY-MM-DD) | no       |
| expiry_date | date              | no       |
| issued_by   | string            | no       |
| issued_at   | string            | no       |
| disease     | string            | no       |
| first_date  | date              | no       |
| last_date   | date              | no       |
| remarks     | string            | no       |
| document    | PDF file          | no       |

### Example

```
name=YELLOW_FEVER_IMMUNIZATION
number=YF-2024-001
issue_date=2026-01-10
expiry_date=2030-01-10
issued_by=Ministry of Health
issued_at=Cairo
disease=Yellow Fever
first_date=2024-05-01
last_date=2024-05-01
```

### Response `201 Created`

```json
{
  "id": 1,
  "name": "YELLOW_FEVER_IMMUNIZATION",
  "user": 46
}
```

---

## 3. Retrieve Vaccination

Retrieve a **single vaccination owned by the user**.

### Endpoint

```
GET /vaccinations/{id}/
```

### Responses

* `200 OK` – success
* `404 Not Found` – not owned or does not exist

---

## 4. Update Vaccination (Partial)

### Endpoint

```
PATCH /vaccinations/{id}/
```

### Body (JSON or form-data)

```json
{
  "remarks": "Updated notes"
}
```

### Response

```
200 OK
```

---

## 5. Update Vaccination (Full Replace)

⚠️ Requires **all fields**.

### Endpoint

```
PUT /vaccinations/{id}/
```

---

## 6. Delete Vaccination

Deletes a vaccination **owned by the user**.

### Endpoint

```
DELETE /vaccinations/{id}/
```

### Response

```
204 No Content
```

---

## Error Responses

### Invalid Vaccine Name

```
400 Bad Request
```

```json
{
  "name": ["Invalid vaccine choice"]
}
```

### Invalid File Type

```
400 Bad Request
```

```json
{
  "document": ["Only PDF files are allowed"]
}
```

### Unauthorized

```
401 Unauthorized
```

---

## Behavior Guarantees

* User can only access **their own records**
* Vaccinations are **automatically linked** to the Users table
* No `permissions.py` used
* Only valid vaccine choices accepted
* Only PDF files allowed

---

## Version

**v1.1**
