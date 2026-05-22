# Companies API — Full Endpoint Reference

**Base URL:** `/api/companies/`

**Authentication:** Bearer JWT token required on all endpoints.

### Permissions

| Endpoint Group | Admin / HR / Recruiter | Employee |
|---|---|---|
| Companies | Full CRUD | Full CRUD |
| Job Orders | Full CRUD | Read-only (browse) |
| Job Positions | Full CRUD | Read-only + Quick Apply |

> [!IMPORTANT]
> The frontend should use `/api/companies/job-orders/` instead of the old `/api/companies/vacancies/` (which no longer exists).

---

## 1. Companies

### Model

```python
class Company(models.Model):
    company_name     = CharField(max_length=200, unique=True)
    company_type     = CharField(max_length=100, choices=COMPANY_TYPES)
    open_positions   = PositiveIntegerField(default=0)
    status           = CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    contact_email    = EmailField()
    website          = URLField(blank=True, null=True)
    company_flag     = CharField(max_length=100, choices=Flag.FLAG_CHOICES, blank=True, null=True)
    hourly_rate      = DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at       = DateTimeField(auto_now_add=True)
    updated_at       = DateTimeField(auto_now=True)
```

**`company_type` choices:**
`Shipping Manning Companies`, `Cargo Manning Companies`, `Cruise & Hospitality Manning Companies`, `Offshore & Oil/Gas Manning Companies`, `Fishing Fleet Manning Companies`, `General Crew Manning Companies`, `Specialized Marine Manning Companies`, `Temporary / Contract Manning Agencies`, `Full Crew Management Companies`, `Other`

**`status` choices:** `Active`, `Inactive`, `Prospect`

---

### `GET /api/companies/` — List all companies

**Filters (query params):**
| Param | Type | Description |
|---|---|---|
| `name` | string | Company name (case-insensitive contains) |
| `company_type` | string | Exact match (case-insensitive) |
| `status` | string | Exact match (case-insensitive) |

**Request:**
```
GET /api/companies/?status=Active&name=sakr
Authorization: Bearer eyJ...
```

**Response (200):**
```json
[
  {
    "id": 1,
    "company_name": "Sakr Shipping",
    "company_type": "Shipping Manning Companies",
    "open_positions": 5,
    "status": "Active",
    "contact_email": "info@sakrshipping.com",
    "contact_phone": "+20 123 456 789",
    "owner": "Capt. Ahmed Sakr",
    "website": "https://sakrshipping.com",
    "company_flag": "Egypt",
    "hourly_rate": "25.00",
    "ships": [
      {
        "id": 1,
        "ship_name": "MV Ocean Star",
        "imo_number": "1234567",
        "ship_type": "Container",
        "flag": "Panama",
        "status": "Active",
        "official_no": "ON-999",
        "call_sign": "C5XYZ",
        "year_built": 2015
      }
    ],
    "created_at": "2026-04-01T10:00:00Z",
    "updated_at": "2026-04-20T14:30:00Z"
  }
]
```

---

### `POST /api/companies/` — Create a company

**Request:**
```json
{
  "company_name": "Sakr Shipping",
  "company_type": "Shipping Manning Companies",
  "open_positions": 5,
  "status": "Active",
  "contact_email": "info@sakrshipping.com",
  "contact_phone": "+20 123 456 789",
  "owner": "Capt. Ahmed Sakr",
  "website": "https://sakrshipping.com",
  "company_flag": "Egypt",
  "hourly_rate": "25.00"
}
```

> `website` and `company_flag` are optional (nullable/blank).

**Response (201):**
```json
{
  "id": 1,
  "company_name": "Sakr Shipping",
  "company_type": "Shipping Manning Companies",
  "open_positions": 5,
  "status": "Active",
  "contact_email": "info@sakrshipping.com",
  "website": "https://sakrshipping.com",
  "company_flag": "Egypt",
  "hourly_rate": "25.00",
  "ships": [],
  "created_at": "2026-04-01T10:00:00Z",
  "updated_at": "2026-04-01T10:00:00Z"
}
```

**Error (400) — Duplicate name:**
```json
{
  "company_name": ["company with this company name already exists."]
}
```

---

### `GET /api/companies/{id}/` — Get company detail

**Request:**
```
GET /api/companies/1/
Authorization: Bearer eyJ...
```

**Response (200):**
```json
{
  "id": 1,
  "company_name": "Sakr Shipping",
  "company_type": "Shipping Manning Companies",
  "open_positions": 5,
  "status": "Active",
  "contact_email": "info@sakrshipping.com",
  "contact_phone": "+20 123 456 789",
  "owner": "Capt. Ahmed Sakr",
  "website": "https://sakrshipping.com",
  "company_flag": "Egypt",
  "hourly_rate": "25.00",
  "ships": [
    {
      "id": 1,
      "ship_name": "MV Ocean Star",
      "imo_number": "1234567",
      "ship_type": "Container",
      "flag": "Panama",
      "status": "Active",
      "official_no": "ON-999",
      "call_sign": "C5XYZ",
      "year_built": 2015
    }
  ],
  "created_at": "2026-04-01T10:00:00Z",
  "updated_at": "2026-04-20T14:30:00Z"
}
```

---

### `PATCH /api/companies/{id}/` — Update a company

**Request:**
```json
{
  "status": "Inactive",
  "open_positions": 0
}
```

**Response (200):** Full company object with updated fields.

---

### `DELETE /api/companies/{id}/` — Delete a company

**Response:** `204 No Content`

---

### `GET /api/companies/stats/` — Company statistics

**Request:**
```
GET /api/companies/stats/
Authorization: Bearer eyJ...
```

**Response (200):**
```json
{
  "total_companies": 25,
  "by_status": {
    "Active": 18,
    "Inactive": 5,
    "Prospect": 2
  },
  "by_type": {
    "Shipping Manning Companies": 10,
    "Cargo Manning Companies": 5,
    "Cruise & Hospitality Manning Companies": 3,
    "Other": 7
  },
  "open_positions": {
    "total": 42,
    "companies_with_openings": 12
  },
  "recent_companies": [
    {
      "id": 25,
      "company_name": "New Marine Co",
      "company_type": "General Crew Manning Companies",
      "status": "Prospect",
      "created_at": "2026-04-25T09:00:00Z"
    }
  ]
}
```

---

## 2. Job Orders (replaces `/vacancies/`)

### Model

```python
class JobOrder(models.Model):
    company               = ForeignKey(Company, on_delete=CASCADE, related_name='job_orders')
    ship                  = ForeignKey('ships.Ship', on_delete=SET_NULL, null=True, blank=True)
    reference_number      = CharField(max_length=50, unique=True)    # e.g. "JO-2024-001"
    request_date          = DateField()
    target_joining_date   = DateField()
    vessel_type_override  = CharField(max_length=100, blank=True)
    trading_area          = CharField(max_length=100, blank=True)
    status                = CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    notes                 = TextField(blank=True)
    created_at            = DateTimeField(auto_now_add=True)
    updated_at            = DateTimeField(auto_now=True)
```

**`status` choices:** `Pending`, `Open`, `In Progress`, `Fulfilled`, `Cancelled`

---

### `GET /api/companies/job-orders/` — List all job orders

**Filters (query params):**
| Param | Type | Description |
|---|---|---|
| `company` | int | Company ID |
| `ship` | int | Ship ID |
| `status` | string | Exact match (case-insensitive) |
| `reference_number` | string | Contains (case-insensitive) |
| `request_date_from` | date | Request date >= value |
| `request_date_to` | date | Request date <= value |

**Request:**
```
GET /api/companies/job-orders/?status=Open&company=3
Authorization: Bearer eyJ...
```

**Response (200):**
```json
[
  {
    "id": 1,
    "company": 3,
    "company_name": "Sakr Shipping",
    "ship": 5,
    "ship_name": "MV Ocean Star",
    "reference_number": "JO-2026-001",
    "request_date": "2026-04-15",
    "target_joining_date": "2026-06-01",
    "vessel_type_override": "",
    "trading_area": "Mediterranean",
    "status": "Open",
    "notes": "Urgent replacement needed",
    "positions": [
      {
        "id": 1,
        "job_order": 1,
        "rank": 7,
        "rank_name": "2nd. Officer",
        "quantity": 2,
        "salary_min": "2500.00",
        "salary_max": "3500.00",
        "currency": "USD",
        "contract_duration_months": 6,
        "remarks": "Must have tanker experience"
      },
      {
        "id": 2,
        "job_order": 1,
        "rank": 12,
        "rank_name": "Bosun",
        "quantity": 1,
        "salary_min": "1800.00",
        "salary_max": "2200.00",
        "currency": "USD",
        "contract_duration_months": 6,
        "remarks": ""
      }
    ],
    "created_at": "2026-04-15T08:00:00Z",
    "updated_at": "2026-04-20T10:30:00Z"
  }
]
```

---

### `POST /api/companies/job-orders/` — Create a job order

**Request:**
```json
{
  "company": 3,
  "ship": 5,
  "reference_number": "JO-2026-001",
  "request_date": "2026-04-15",
  "target_joining_date": "2026-06-01",
  "vessel_type_override": "",
  "trading_area": "Mediterranean",
  "status": "Pending",
  "notes": "Urgent replacement needed"
}
```

> `ship`, `vessel_type_override`, `trading_area`, and `notes` are optional.

**Response (201):**
```json
{
  "id": 1,
  "company": 3,
  "company_name": "Sakr Shipping",
  "ship": 5,
  "ship_name": "MV Ocean Star",
  "reference_number": "JO-2026-001",
  "request_date": "2026-04-15",
  "target_joining_date": "2026-06-01",
  "vessel_type_override": "",
  "trading_area": "Mediterranean",
  "status": "Pending",
  "notes": "Urgent replacement needed",
  "positions": [],
  "created_at": "2026-04-15T08:00:00Z",
  "updated_at": "2026-04-15T08:00:00Z"
}
```

**Error (400) — Duplicate reference:**
```json
{
  "reference_number": ["job order with this reference number already exists."]
}
```

**Error (400) — Missing required fields:**
```json
{
  "company": ["This field is required."],
  "reference_number": ["This field is required."],
  "request_date": ["This field is required."],
  "target_joining_date": ["This field is required."]
}
```

---

### `GET /api/companies/job-orders/{id}/` — Get job order detail

**Request:**
```
GET /api/companies/job-orders/1/
Authorization: Bearer eyJ...
```

**Response (200):** Same as list item (including nested `positions` array).

---

### `PATCH /api/companies/job-orders/{id}/` — Update a job order

**Request:**
```json
{
  "status": "In Progress",
  "notes": "Interviews scheduled for May"
}
```

**Response (200):** Full job order object with updated fields.

---

### `DELETE /api/companies/job-orders/{id}/` — Delete a job order

**Response:** `204 No Content`

> ⚠️ Deleting a job order will cascade-delete all its positions.

---

## 3. Job Order Positions

### Model

```python
class JobOrderPosition(models.Model):
    job_order                = ForeignKey(JobOrder, on_delete=CASCADE, related_name='positions')
    rank                     = ForeignKey('api.Rank', on_delete=SET_NULL, null=True)
    quantity                 = PositiveIntegerField(default=1)
    salary_min               = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max               = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency                 = CharField(max_length=10, default='USD')
    contract_duration_months = PositiveIntegerField(default=6)
    remarks                  = TextField(blank=True)
```

---

### `GET /api/companies/job-positions/` — List all positions

**Filters (query params):**
| Param | Type | Description |
|---|---|---|
| `job_order` | int | Job Order ID |
| `rank` | int | Rank ID |

**Request:**
```
GET /api/companies/job-positions/?job_order=1
Authorization: Bearer eyJ...
```

**Response (200):**
```json
[
  {
    "id": 1,
    "job_order": 1,
    "rank": 7,
    "rank_name": "2nd. Officer",
    "quantity": 2,
    "salary_min": "2500.00",
    "salary_max": "3500.00",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": "Must have tanker experience"
  }
]
```

---

### `POST /api/companies/job-positions/` — Add position(s) to a job order

> [!TIP]
> - The `rank` field accepts **both** an integer ID **or** a string name (case-insensitive).
> - You can send a **single object** or an **array** to create multiple positions at once.

#### Single Position

**Request:**
```json
{
  "job_order": 1,
  "rank": "2nd. Officer",
  "quantity": 2,
  "salary_min": "2500.00",
  "salary_max": "3500.00",
  "currency": "USD",
  "contract_duration_months": 6,
  "remarks": "Must have tanker experience"
}
```

**Response (201):**
```json
{
  "id": 1,
  "job_order": 1,
  "rank": 7,
  "rank_name": "2nd. Officer",
  "quantity": 2,
  "salary_min": "2500.00",
  "salary_max": "3500.00",
  "currency": "USD",
  "contract_duration_months": 6,
  "remarks": "Must have tanker experience"
}
```

#### Bulk Create (multiple positions at once)

**Request (array):**
```json
[
  {
    "job_order": 1,
    "rank": "2nd. Officer",
    "quantity": 2,
    "salary_min": "2500.00",
    "salary_max": "3500.00",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": "Must have tanker experience"
  },
  {
    "job_order": 1,
    "rank": "Bosun",
    "quantity": 1,
    "salary_min": "1800.00",
    "salary_max": "2200.00"
  },
  {
    "job_order": 1,
    "rank": "Chief Cook",
    "quantity": 1
  }
]
```

> `salary_min`, `salary_max`, `currency`, `contract_duration_months`, and `remarks` are optional on each item.

**Response (201) — array of created positions:**
```json
[
  {
    "id": 1,
    "job_order": 1,
    "rank": 7,
    "rank_name": "2nd. Officer",
    "quantity": 2,
    "salary_min": "2500.00",
    "salary_max": "3500.00",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": "Must have tanker experience"
  },
  {
    "id": 2,
    "job_order": 1,
    "rank": 12,
    "rank_name": "Bosun",
    "quantity": 1,
    "salary_min": "1800.00",
    "salary_max": "2200.00",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": ""
  },
  {
    "id": 3,
    "job_order": 1,
    "rank": 15,
    "rank_name": "Chief Cook",
    "quantity": 1,
    "salary_min": null,
    "salary_max": null,
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": ""
  }
]
```

#### Error Responses

**Error (400) — Missing required fields:**
```json
{
  "job_order": ["This field is required."],
  "rank": ["This field is required."]
}
```

**Error (400) — Invalid rank name:**
```json
{
  "rank": "Rank \"Invalid Name\" not found. Use a valid rank name or ID."
}
```

---

### `POST /api/companies/job-positions/apply/` — Quick Apply (Employee)

Allows an Employee to apply to one or more open job positions. This creates a `Document` record with status `Pending` for each position, effectively saving the application to the "2. 📋 CVs" section first. When an Admin changes the document status to `Active`, the system automatically creates the formal `CVSubmission` in "4. 📤 CV Submissions".

> [!IMPORTANT]
> This is the **only write endpoint** available to Employees on job positions.

**Request (by IDs):**
```json
{
  "position_ids": [1, 2, 3]
}
```

**Request (by rank names):**
```json
{
  "position_names": ["2nd. Officer", "Bosun", "Chief Cook"]
}
```

**Request (mixed — both at once):**
```json
{
  "position_ids": [1],
  "position_names": ["Bosun", "Chief Cook"]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `position_ids` | int[] | One or both | List of `JobOrderPosition` IDs to apply to |
| `position_names` | string[] | One or both | List of rank names to match against open positions |

> At least one of `position_ids` or `position_names` must be provided. Both can be used together.

**Success Response (201) — Document applications created:**
```json
{
  "applied": [
    {
      "document_id": 45,
      "position_id": 1,
      "rank_name": "2nd. Officer",
      "company_name": "Sakr Shipping",
      "status": "Pending"
    },
    {
      "document_id": 46,
      "position_id": 3,
      "rank_name": "Chief Cook",
      "company_name": "Sakr Shipping",
      "status": "Pending"
    }
  ],
  "skipped": [
    {
      "position_id": 2,
      "rank_name": "Bosun",
      "company_name": "Sakr Shipping",
      "reason": "Already applied (Pending or Active)"
    }
  ],
  "total_applied": 2,
  "total_skipped": 1
}
```

> Duplicate applications are automatically detected and skipped (checks for existing Pending or Active Documents for the same user + same rank + same company).

**Error (400) — Missing or invalid position_ids:**
```json
{
  "error": "position_ids is required and must be a list of JobOrderPosition IDs."
}
```

**Error (404) — No valid positions found:**
```json
{
  "error": "No valid positions found for the given IDs."
}
```

---

### `GET /api/companies/job-positions/{id}/` — Get position detail

**Response (200):** Same as list item.

---

### `PATCH /api/companies/job-positions/{id}/` — Update a position

> `rank` can also be updated using a name string or ID.

**Request:**
```json
{
  "quantity": 3,
  "salary_max": "4000.00",
  "rank": "Chief Officer"
}
```

**Response (200):** Full position object with updated fields.

---

### `DELETE /api/companies/job-positions/{id}/` — Delete a position

**Response:** `204 No Content`

> Permission: Admin / HR / Recruiter only.

---

---

## 2. 📋 CVs (/api/documents/)

The CVs section (internally called `Documents`) is the entry point for all applications. When a candidate uses "Quick Apply" or uploads their CV directly, a record is created here with a `Pending` status.

### `GET /api/documents/` — List Applications
**Permissions:** Admin / HR / Recruiter see all. Employees see only their own.

**Success Response (200):**
```json
[
  {
    "id": 88,
    "user": 5,
    "title": "Application for 2nd. Officer at Sakr Shipping",
    "name": "Ahmed Salem",
    "email": null,
    "phone_number": null,
    "position": "2nd. Officer",
    "status": "Pending",
    "file": "http://api.backend.soon.it/media/documents/ahmed_cv.pdf",
    "company": 2,
    "company_name": "Sakr Shipping",
    "job_position": 12,
    "job_position_name": "2nd. Officer",
    "job_position_details": {
      "id": 12,
      "quantity": 3,
      "salary_min": "4000.00",
      "salary_max": "5000.00",
      "currency": "USD",
      "contract_duration_months": 6,
      "remarks": "Must have offshore experience"
    },
    "created_at": "2026-05-01T14:00:00Z",
    "updated_at": "2026-05-01T14:00:00Z"
  }
]
```

### `POST /api/documents/` — Direct CV Upload
Allows uploading a CV and linking it directly to a job position. The backend will automatically fill in the company and rank details.

**Request (Multipart Form-Data):**
* `file`: (The PDF/DOCX file)
* `job_position`: `12`
* `name`: `"Ahmed Salem"` (Optional)

**Success Response (201):** Returns the full document object as shown above.

---

## 3. 📤 CV Submissions (/api/cv-submissions/)

Once a `Document` application's status is changed to **Active** (via `/api/documents/{id}/set_status/`), it is automatically promoted to a **CV Submission**. This is where HR manages the candidate's journey (Reviewing, Interviewing, etc.).

### `GET /api/cv-submissions/` — List Submissions
**Permissions:** Admin / HR / Recruiter see all. Employees see only their own.

**Success Response (200):**
```json
[
  {
    "id": 45,
    "user": 5,
    "user_name": "Ahmed Salem",
    "company": 2,
    "company_name": "Sakr Shipping",
    "position": 7,
    "position_name": "2nd. Officer",
    "status": "Approved",
    "experience_years": 5,
    "submitted_date": "2026-05-01",
    "job_position": 12,
    "job_position_details": {
      "id": 12,
      "quantity": 3,
      "salary_min": "4000.00",
      "salary_max": "5000.00",
      "currency": "USD"
    }
  }
]
```

---

## 4. Contracts

The contracts endpoint integrates directly with CV Submissions and Job Order Positions, allowing you to instantly generate a contract pre-filled with the employee's details and the salary from the job position they applied for.

### `POST /api/contracts/` — Generate Contract (from CV Submission)

**Permissions:** Admin / HR Manager only

Allows you to instantly generate an employment contract by pointing to an approved CV Submission. It auto-fills the user, company, rank, and salary details based on the exact Job Position they applied for.

**Request:**
```json
{
  "cv_submission_id": 45,
  "ship": 3,
  "sign_on_date": "2026-06-01",
  "repatriation_terms": "Company covers return flight to home country",
  "leave_pay_terms": "30 days paid leave per contract cycle",
  "status": "Draft"
}
```
> *Note: We did not send `salary` or `currency` — the backend will grab those directly from the job position they applied for!*

**Success Response (201 Created):**
```json
{
  "id": 12,
  "user": 7,
  "user_name": "Mohamed Ahmed",
  "user_email": "mohamed.ahmed@email.com",
  "generated_id": "492817364051",
  
  "ship": 3,
  "ship_name": "MV Ocean Star",
  "company": 2,
  "company_name": "Sakr Shipping",
  
  "rank": 7,
  "rank_name": "2nd. Officer",
  "assigned_code": "DO-3.002",
  
  "job_position": 4,
  "job_position_details": {
    "id": 4,
    "quantity": 2,
    "salary_min": "2500.00",
    "salary_max": "3500.00",
    "currency": "USD",
    "contract_duration_months": 6,
    "remarks": "Must have tanker experience"
  },
  
  "sign_on_date": "2026-06-01",
  "sign_off_date": null,
  "salary": "3500.00",
  "currency": "USD",
  "status": "Draft",
  
  "signed_file": null,
  "signed_at": null,
  "created_at": "2026-05-01T11:45:00Z",
  "updated_at": "2026-05-01T11:45:00Z",

  "certificates": [
    {
      "id": 1,
      "code": "GMDSS",
      "name": "G.M.D.S.S"
    }
  ],
  "coded_rank": [
    {
      "assigned_code": "DO-3.002",
      "rank_code": "DO-3.000",
      "rank_name": "2nd. Officer"
    }
  ],
  "user_documents": {
    "passport": {
      "passport_no": "A12345678",
      "issue_date": "2022-01-15",
      "expiry_date": "2032-01-14",
      "issued_by": "Egypt",
      "place_of_issue": "Cairo",
      "file_url": "http://api.backend.soon.it/media/documents/passports/passport_123.pdf"
    },
    "seaman_book": {
      "seaman_book_no": "SB9876543",
      "issue_date": "2023-05-10",
      "expiry_date": "2028-05-09",
      "issued_by": "Maritime Authority",
      "place_of_issue": "Alexandria",
      "file_url": "http://api.backend.soon.it/media/documents/seaman/sb_123.pdf"
    },
    "other_seaman_book": {
      "seaman_book_no": null,
      "issue_date": null,
      "expiry_date": null,
      "issued_by": "",
      "place_of_issue": "",
      "file_url": null
    },
    "coc": {
      "certificate_name": "Officer in Charge of Navigational Watch",
      "certificate_number": "COC-456",
      "issue_date": "2021-08-20",
      "expiry_date": "2026-08-19",
      "issued_by": "EAMS",
      "issued_at": "Alexandria"
    },
    "goc": {
      "certificate_number": "GOC-789",
      "issue_date": "2022-11-05",
      "expiry_date": "2027-11-04",
      "issued_by": "EAMS",
      "issued_at": "Alexandria"
    },
    "health_certificate": {
      "flag_state": "Panama",
      "number": "MED-111",
      "issue_date": "2025-01-10",
      "expiry_date": "2027-01-09",
      "issued_by": "Approved Clinic",
      "issued_at": "Cairo",
      "international_medical_number": "INT-222",
      "international_medical_issue_date": "2025-01-15",
      "international_medical_expiry_date": "2027-01-14"
    },
    "licenses": [
      {
        "id": 1,
        "document_name": "Panama License",
        "document_number": "PAN-333",
        "country_of_issue": "Panama",
        "issue_date": "2024-03-01",
        "expiration_date": "2029-02-28",
        "file_url": "http://api.backend.soon.it/media/documents/licenses/panama_lic.pdf"
      }
    ]
  }
}
```

---

### `PATCH /api/contracts/{id}/` — Edit a Contract

Use this to update fields (e.g. changing status to "Signed" or adjusting salary). All fields are optional.

**Request:**
```json
{
  "salary": "4000.00",
  "status": "Pending Signature",
  "sign_off_date": "2026-12-15"
}
```

**Response (200):** Full contract object with updated fields.

---

### `DELETE /api/contracts/{id}/` — Delete a Contract

**Response:** `204 No Content`

---

## Quick Reference — All Endpoints

### Companies
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/companies/` | All | List all companies |
| `POST` | `/api/companies/` | All | Create a company |
| `GET` | `/api/companies/{id}/` | All | Company detail |
| `PATCH` | `/api/companies/{id}/` | All | Update a company |
| `DELETE` | `/api/companies/{id}/` | All | Delete a company |
| `GET` | `/api/companies/stats/` | All | Dashboard statistics |

### Job Orders (replaces vacancies)
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/companies/job-orders/` | All | List/browse job orders |
| `POST` | `/api/companies/job-orders/` | Admin/HR/Recruiter | Create a job order |
| `GET` | `/api/companies/job-orders/{id}/` | All | Job order detail |
| `PATCH` | `/api/companies/job-orders/{id}/` | Admin/HR/Recruiter | Update a job order |
| `DELETE` | `/api/companies/job-orders/{id}/` | Admin/HR/Recruiter | Delete a job order |

### Job Order Positions
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/companies/job-positions/` | All | List/browse positions |
| `POST` | `/api/companies/job-positions/` | Admin/HR/Recruiter | Add position(s) |
| `GET` | `/api/companies/job-positions/{id}/` | All | Position detail |
| `PATCH` | `/api/companies/job-positions/{id}/` | Admin/HR/Recruiter | Update a position |
| `DELETE` | `/api/companies/job-positions/{id}/` | Admin/HR/Recruiter | Delete a position |
| `POST` | `/api/companies/job-positions/apply/` | **Employee** | Quick apply to positions |

### Contracts
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/contracts/` | Admin/HR | List all contracts |
| `POST` | `/api/contracts/` | Admin/HR | Generate/create contract |
| `GET` | `/api/contracts/{id}/` | Admin/HR | Contract detail |
| `PATCH` | `/api/contracts/{id}/` | Admin/HR | Update a contract |
| `DELETE` | `/api/contracts/{id}/` | Admin/HR | Delete a contract |

### 📋 CVs & Applications
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/documents/` | All | List pending applications |
| `POST` | `/api/documents/` | All | Direct CV upload |
| `POST` | `/api/documents/{id}/set_status/` | Admin/HR | Approve (Active) or Reject |

### 📤 CV Submissions
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| `GET` | `/api/cv-submissions/` | All | List approved submissions |
| `GET` | `/api/cv-submissions/{id}/` | All | Submission details & documents |

---

## Source Files

- **Models:** [companies/models.py](file:///run/media/storm/New%20Volume/1-TECHNO%20SQUARE/SAKR%20PROJECT/companies/models.py)
- **Serializers:** [companies/serializers.py](file:///run/media/storm/New%20Volume/1-TECHNO%20SQUARE/SAKR%20PROJECT/companies/serializers.py)
- **Views:** [companies/views.py](file:///run/media/storm/New%20Volume/1-TECHNO%20SQUARE/SAKR%20PROJECT/companies/views.py)
- **URLs:** [companies/urls.py](file:///run/media/storm/New%20Volume/1-TECHNO%20SQUARE/SAKR%20PROJECT/companies/urls.py)
- **Filters:** [api/filters.py](file:///run/media/storm/New%20Volume/1-TECHNO%20SQUARE/SAKR%20PROJECT/api/filters.py#L143-L153) (JobOrderFilter)
- **Permissions:** [api/permissions.py](file:///run/media/storm/New%20Volume/1-TECHNO%20SQUARE/SAKR%20PROJECT/api/permissions.py) (JobOrderPermission)
