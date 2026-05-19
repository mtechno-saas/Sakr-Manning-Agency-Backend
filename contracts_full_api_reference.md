# `/api/contracts/` — Full Endpoint Reference

---

## 📊 Data Model — `Contract`

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | Auto | Primary key |
| `user` | FK → Users | Yes* | The seafarer. *Auto-filled if using `cv_submission_id` |
| `ship` | FK → Ship | No | The ship they are joining |
| `company` | FK → Company | No* | The hiring company. *Auto-filled from CV |
| `rank` | FK → Rank | No* | Position/rank. *Auto-filled from CV |
| `job_position` | FK → JobOrderPosition | No | Linked job order position |
| `sign_on_date` | date | Yes | Date they board the ship (YYYY-MM-DD) |
| `sign_off_date` | date | No | Scheduled disembarkation date |
| `salary` | decimal(10,2) | No | Auto-fills from `job_position.salary_max` if omitted |
| `currency` | string | No | `USD` (default), `EUR`, `GBP`, `EGP` |
| `status` | string | No | Default: `Pending`. Options: `Active`, `Completed`, `Pending`, `Signed`, `Pending Signature`, `Draft`, `Cancelled` |
| `repatriation_terms` | text | No | Notes on flight/travel coverage |
| `leave_pay_terms` | text | No | Notes on paid leave |
| `signed_file` | file | No | Uploaded signed contract document |
| `signed_at` | datetime | No | Timestamp when contract was signed |
| `created_at` | datetime | Auto | Record creation timestamp |
| `updated_at` | datetime | Auto | Record last modified timestamp |

---

## 🔐 Permission Matrix — `ContractPermission`

| Role | GET (List) | GET (Detail) | POST | PATCH/PUT | DELETE |
|---|---|---|---|---|---|
| **Admin** | ✅ All contracts | ✅ Any | ✅ | ✅ | ✅ |
| **HR Manager** | ✅ All contracts | ✅ Any | ✅ | ✅ | ✅ |
| **Recruiter** | ✅ All contracts | ✅ Any | ❌ | ❌ | ❌ |
| **Employee** | ✅ Own contracts only | ✅ Own only | ❌ | ❌ | ❌ |

---

## 1️⃣ `GET /api/contracts/` — List All Contracts

Uses **ContractListSerializer** (lightweight, no seafarer_application).

### Request
```
GET /api/contracts/
Authorization: Bearer <JWT_TOKEN>
```

### Response — `200 OK`
```json
[
    {
        "id": 101,
        "user": 50,
        "user_name": "Ahmed Hassan",
        "ship_name": "Ocean Voyager",
        "company_name": "Global Maritime Solutions",
        "rank_name": "Chief Officer",
        "sign_on_date": "2026-06-01",
        "sign_off_date": "2026-12-01",
        "status": "Signed"
    },
    {
        "id": 102,
        "user": 55,
        "user_name": "Mohamed Ali",
        "ship_name": "Star Navigator",
        "company_name": "Maersk Line",
        "rank_name": "2nd Engineer",
        "sign_on_date": "2026-07-15",
        "sign_off_date": null,
        "status": "Draft"
    }
]
```

### Error Responses
| Code | Reason |
|---|---|
| `401` | Missing or invalid JWT token |
| `403` | Unauthenticated request |

---

## 2️⃣ `GET /api/contracts/{id}/` — Retrieve Single Contract

Uses **ContractSerializer** (full payload including `seafarer_application`).

### Request
```
GET /api/contracts/101/
Authorization: Bearer <JWT_TOKEN>
```

### Response — `200 OK`
```json
{
    "id": 101,
    "user": 50,
    "user_name": "Ahmed Hassan",
    "user_email": "ahmed.hassan@example.com",
    "generated_id": "240503000012",
    "ship": 2,
    "ship_name": "Ocean Voyager",
    "ship_details": {
        "id": 2,
        "ship_name": "Ocean Voyager",
        "imo_number": "1234567",
        "ship_type": "Container",
        "flag": "Panama",
        "status": "Active"
    },
    "company": 5,
    "company_name": "Global Maritime Solutions",
    "company_details": {
        "id": 5,
        "company_name": "Global Maritime Solutions",
        "company_type": "Ship Owner",
        "country": "Egypt",
        "contact_person": "John Doe",
        "contact_email": "john@example.com",
        "status": "Active"
    },
    "rank": 3,
    "rank_name": "Chief Officer",
    "assigned_code": "D.01",
    "job_position": 12,
    "sign_on_date": "2026-06-01",
    "sign_off_date": "2026-12-01",
    "salary": "8500.00",
    "currency": "USD",
    "status": "Signed",
    "signed_file": null,
    "signed_at": null,
    "certificates": [
        {"id": 1, "code": "CERT-001", "name": "STCW Basic Safety"}
    ],
    "coded_rank": [
        {"assigned_code": "D.01", "rank_code": "CO", "rank_name": "Chief Officer"}
    ],
    "user_documents": {
        "passport": {
            "passport_no": "A12345678",
            "issue_date": "2022-01-15",
            "expiry_date": "2032-01-15",
            "issued_by": "EAMS",
            "place_of_issue": "Cairo",
            "file_url": "http://localhost:8000/media/passports/ahmed_passport.pdf"
        },
        "seaman_book": {
            "seaman_book_no": "SB-99887",
            "issue_date": "2023-03-10",
            "expiry_date": "2028-03-10",
            "issued_by": "EAMS",
            "place_of_issue": "Alexandria",
            "file_url": null
        },
        "other_seaman_book": {
            "seaman_book_no": null, "issue_date": null, "expiry_date": null,
            "issued_by": null, "place_of_issue": null, "file_url": null
        },
        "coc": {
            "certificate_name": "Chief Mate",
            "certificate_number": "COC-2023-456",
            "issue_date": "2023-06-01",
            "expiry_date": "2028-06-01",
            "issued_by": "EAMS",
            "issued_at": "Alex."
        },
        "goc": {
            "certificate_number": "GOC-789",
            "issue_date": "2023-06-01",
            "expiry_date": "2028-06-01",
            "issued_by": "NTRA",
            "issued_at": "Cairo"
        },
        "health_certificate": {
            "flag_state": null,
            "number": "MED-001",
            "issue_date": "2025-01-01",
            "expiry_date": "2027-01-01",
            "issued_by": "Port Health Office",
            "issued_at": "Alexandria",
            "international_medical_number": "MED-001",
            "international_medical_issue_date": "2025-01-01",
            "international_medical_expiry_date": "2027-01-01"
        },
        "licenses": [
            {
                "id": 10, "document_name": "GMDSS Operator", "document_number": "LIC-555",
                "country_of_issue": "Egypt", "issue_date": "2024-01-01",
                "expiration_date": "2029-01-01", "file_url": null
            }
        ]
    },
    "job_position_details": {
        "id": 12,
        "job_position_name": "Chief Officer",
        "quantity": 2,
        "salary_min": "7000.00",
        "salary_max": "8500.00",
        "currency": "USD",
        "contract_duration_months": 6,
        "remarks": "Tanker experience preferred"
    },
    "seafarer_application": {
        "document_info": {
            "agency_name": "SAKR MANNING AGENCY",
            "description": "FOR RECRUITING EGYPTIAN LABOR ABROAD",
            "manual_name": "Crewing Management Manual",
            "form_name": "Seafarer Employment Application",
            "revision": "13",
            "page": "4"
        },
        "application_header": {
            "issue_date": "2026-01-15",
            "revision_date": "2026-05-04",
            "application_for_position_as": "1st. Officer – Chief Off.",
            "register_code": "REG-2026-050",
            "other_position_if_any": "",
            "register_date": "2026-01-15",
            "last_update_data": "2026-05-04 16:30",
            "expected_salary": "5000.00",
            "available_date": "2026-06-01"
        },
        "1_personal_details": {
            "full_name": "Ahmed Hassan",
            "date_of_birth": "1990-05-20",
            "marital_status": {"single": false, "married": true},
            "nationality": "Egyptian",
            "height_cm": 180, "weight_kg": 82,
            "place_of_birth": "Cairo",
            "overall_size": "L", "shirt_size": "L",
            "nearest_port": "Alexandria",
            "trouser_size": "34", "shoes_size": "43"
        },
        "2_education": {
            "college_school": "Arab Academy for Science & Technology",
            "marline_test": {
                "issued_date": "2025-03-01",
                "result_percentage": "92%",
                "issued_by_authority": "Marlins",
                "issued_at": "Alexandria"
            },
            "english_language": {"fluent": false, "good": true, "average": false, "poor": false},
            "german_language": {"fluent": false, "good": false, "average": false, "poor": false}
        },
        "3_contact_details": {
            "home_address_city": "Smouha, Alexandria",
            "e_mail": "ahmed.hassan@example.com",
            "mobile_tel": "+201012345678"
        },
        "4_travel_documents": [
            {"type": "Passport", "document_no": "A12345678", "iss_date": "2022-01-15", "exp_date": "2032-01-15", "iss_by_authority": "EAMS", "place_of_issue": "Cairo"},
            {"type": "Seaman Book", "document_no": "SB-99887", "iss_date": "2023-03-10", "exp_date": "2028-03-10", "iss_by_authority": "EAMS", "place_of_issue": "Alexandria"},
            {"type": "Other Seaman Book", "document_no": "", "iss_date": "", "exp_date": "", "iss_by_authority": "", "place_of_issue": ""}
        ],
        "5_professional_qualification_certificate_of_competency": [
            {"certificate_name": "COC (Chief Mate)", "number": "COC-2023-456", "issue_date": "2023-06-01", "expiry_date": "2028-06-01", "issued_by": "EAMS", "issued_at": "Alex."},
            {"certificate_name": "GOC", "number": "GOC-789", "issue_date": "2023-06-01", "expiry_date": "2028-06-01", "issued_by": "NTRA", "issued_at": "Cairo"}
        ],
        "6_next_of_kin_emergency_contact": {
            "full_name": "Fatma Hassan",
            "address_country": "Egypt",
            "tel_no_mobile": "+201098765432",
            "relationship": "Wife",
            "email": "fatma.hassan@example.com"
        },
        "7_health_certificates_and_vaccinations": {
            "certificates": [
                {"flag_state": "International Medical", "number": "MED-001", "issue_date": "2025-01-01", "expiry_date": "2027-01-01", "issued_by": "Port Health Office", "issued_at": "Alexandria"},
                {"flag_state": "Yellow Fever", "number": "YF-100", "issue_date": "2024-06-01", "expiry_date": "", "issued_by": "", "issued_at": ""},
                {"flag_state": "Cholera", "number": "", "issue_date": "", "expiry_date": "", "issued_by": "", "issued_at": ""}
            ],
            "covid_19": {
                "vaccination_name": "Pfizer-BioNTech",
                "first_dose": "2021-08-01",
                "second_dose": "2021-09-01",
                "other_does_or_remarks": "Booster Dec 2022"
            }
        },
        "8_marine_courses": [
            {"course_name": "Personal Survival Techniques", "number": "PST-001", "issue_date": "2023-01-15", "expiry_date": "2028-01-15", "issued_by_at": "AASTMT / Alexandria"}
        ],
        "9_complete_sea_service_details": {
            "applicant_info": {"name": "Ahmed Hassan", "rank": "1st. Officer – Chief Off.", "register_code": "REG-2026-050"},
            "service_records": [
                {
                    "company_name": "Maersk Line", "rank": "2nd Officer",
                    "vessel_name_imo_number": "Maersk Utah / 9001234",
                    "flag": "Denmark", "signed_on": "2024-01-10", "signed_off": "2024-06-15",
                    "period": "5 months", "vessel_type": "Container",
                    "dwt_grt": "65000 / 40000", "engine_type": "MAN B&W",
                    "bh_kw": "30000 / 22000", "reason_for_sign_off": "End of contract"
                }
            ]
        },
        "10_references": [
            {"no": "1", "company_management_country": "Maersk / Denmark", "position": "Master", "name": "Capt. Lars Jensen", "tel": "+4512345678", "email": "lars.jensen@maersk.com"}
        ],
        "11_declaration": {
            "questions": {
                "suffer_disease_unfit_for_sea": {"answer": "NO", "details": ""},
                "addicted_to_alcohol_or_drugs": {"answer": "NO"},
                "suffer_accident_disabled": {"answer": "NO"},
                "undergo_psychiatric_treatment": {"answer": "NO"}
            },
            "consent_statement": "I hereby declare that the above facts and information are true and accurate...",
            "place": "Alexandria", "date": "2026-01-15", "signature": ""
        },
        "12_for_office_use_only": {
            "initial_assessment_of_applicant": "",
            "comments": "Strong candidate. Recommended for Chief Officer position.",
            "responsible_person": {"name_signature": "Capt. Omar Sakr", "date": "2026-01-20"}
        }
    },
    "created_at": "2026-05-03T23:40:00Z",
    "updated_at": "2026-05-04T16:35:00Z"
}
```

### Error Responses
| Code | Reason |
|---|---|
| `401` | Missing or invalid JWT |
| `403` | Employee trying to access another user's contract |
| `404` | Contract ID not found |

---

## 3️⃣ `POST /api/contracts/` — Create Contract

**Permission**: Admin, HR Manager only.

### Option A — Create from CV Submission (Recommended)

Auto-fills `user`, `company`, `rank`, `salary`, `currency` from the CV.

**Request Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `cv_submission` | int | **Yes** | ID of the approved CV Submission. Auto-fills user, company, rank, job_position. |
| `applicant_name` | string | Optional | Full name of the targeted applicant. If provided, the backend **validates** it matches the CV owner. Returns a `400` error if it doesn't match. |
| `ship_name` | string | Optional | Name of the ship (case-insensitive lookup). Alternatively pass `ship` as an int ID. If omitted, contract is created without a ship. |
| `sign_on_date` | date | **Yes** | Board date — format `YYYY-MM-DD`. |
| `sign_off_date` | date | No | Planned disembarkation date. |
| `salary` | decimal | No | Auto-fills from `job_position.salary_max` if omitted. |
| `currency` | string | No | Auto-fills from job position, defaults to `USD`. |
| `status` | string | No | Default: `Draft`. Options: `Active`, `Completed`, `Pending`, `Signed`, `Pending Signature`, `Draft`, `Cancelled`. |

```
POST /api/contracts/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

```json
{
    "cv_submission": 45,
    "applicant_name": "Ahmed Hassan",
    "ship_name": "Ocean Voyager",
    "sign_on_date": "2026-06-01",
    "sign_off_date": "2026-12-01",
    "status": "Draft"
}
```

> 💡 `salary` and `currency` are omitted — the backend pulls them directly from the job position linked to CV #45.

> ⚠️ **`applicant_name` Validation:** If the name doesn't match the CV owner you get:
> ```json
> {"applicant_name": "Name 'Ahmed Hassan' does not match the applicant on CV #45 ('Mohamed Ali'). Please verify you have the right CV."}
> ```

### Option B — Create Manually (without CV)

```json
{
    "user": 50,
    "ship": 2,
    "company": 5,
    "rank": 3,
    "sign_on_date": "2026-06-01",
    "sign_off_date": "2026-12-01",
    "salary": "8500.00",
    "currency": "USD",
    "status": "Draft"
}
```

### Option C — Create + Update Seafarer Profile

```json
{
    "cv_submission": 45,
    "ship_name": "Ocean Voyager",
    "sign_on_date": "2026-06-01",
    "status": "Draft",
    "personal_details": {
        "full_name": "Ahmed Mohamed Hassan",
        "height_cm": 180, "weight_kg": 82,
        "nationality": "Egyptian",
        "marital_status": {"married": true, "single": false},
        "place_of_birth": "Cairo",
        "overall_size": "L", "shirt_size": "L",
        "nearest_port": "Alexandria",
        "trouser_size": "34", "shoes_size": "43"
    },
    "contact_details": {
        "home_address_city": "Smouha, Alexandria",
        "e_mail": "ahmed.hassan@example.com",
        "mobile_tel": "+201012345678"
    },
    "travel_documents": [
        {"type": "Passport", "document_no": "A12345678", "iss_date": "2022-01-15", "exp_date": "2032-01-15", "iss_by_authority": "EAMS", "place_of_issue": "Cairo"},
        {"type": "Seaman Book", "document_no": "SB-99887", "iss_date": "2023-03-10", "exp_date": "2028-03-10", "iss_by_authority": "EAMS", "place_of_issue": "Alexandria"}
    ],
    "next_of_kin": {
        "full_name": "Fatma Hassan", "address_country": "Egypt",
        "tel_no_mobile": "+201098765432", "relationship": "Wife",
        "email": "fatma.hassan@example.com"
    },
    "sea_service_details": {
        "service_records": [
            {
                "company_name": "Maersk Line", "rank": "2nd Officer",
                "vessel_name_imo_number": "Maersk Utah / 9001234",
                "flag": "Denmark", "signed_on": "2024-01-10", "signed_off": "2024-06-15",
                "period": "5 months", "vessel_type": "Container",
                "dwt_grt": "65000 / 40000", "engine_type": "MAN B&W",
                "bh_kw": "30000 / 22000", "reason_for_sign_off": "End of contract"
            }
        ]
    },
    "marine_courses": [
        {"course_name": "Personal Survival Techniques", "number": "PST-001", "issue_date": "2023-01-15", "expiry_date": "2028-01-15", "issued_by_at": "AASTMT / Alexandria"}
    ],
    "health_certificates": {
        "certificates": [
            {"flag_state": "International Medical", "number": "MED-001", "issue_date": "2025-01-01", "expiry_date": "2027-01-01", "issued_by": "Port Health Office", "issued_at": "Alexandria"},
            {"flag_state": "Yellow Fever", "number": "YF-100", "issue_date": "2024-06-01", "expiry_date": "", "issued_by": "", "issued_at": ""}
        ],
        "covid_19": {"vaccination_name": "Pfizer-BioNTech", "first_dose": "2021-08-01", "second_dose": "2021-09-01", "other_does_or_remarks": "Booster Dec 2022"}
    },
    "references": [
        {"company_management_country": "Maersk / Denmark", "position": "Master", "name": "Capt. Lars Jensen", "tel": "+4512345678", "email": "lars.jensen@maersk.com"}
    ],
    "declaration": {
        "questions": {"suffer_disease_unfit_for_sea": {"answer": "NO", "details": ""}},
        "place": "Alexandria", "date": "2026-01-15"
    },
    "for_office_use_only": {
        "comments": "Strong candidate. Recommended.",
        "responsible_person": {"name_signature": "Capt. Omar Sakr", "date": "2026-01-20"}
    }
}
```

### Response — `201 Created`

Returns the full `ContractSerializer` response (same structure as GET by ID above).

### Error Responses
| Code | Body | Reason |
|---|---|---|
| `400` | `{"applicant_name": "Name '...' does not match the applicant on CV #45 ('...')."}` | `applicant_name` mismatch |
| `400` | `{"error": "This CV Submission has no assigned position/rank..."}` | CV missing position |
| `400` | `{"error": "This CV Submission has no linked company..."}` | CV missing company |
| `400` | `{"error": "CV Submission with id 999 not found."}` | Invalid `cv_submission` ID |
| `400` | `{"ship_name": "Ship with name 'X' not found."}` | `ship_name` not found in DB |
| `400` | `{"sign_on_date": ["This field is required."]}` | Missing required fields |
| `401` | Unauthorized | Invalid/missing token |
| `403` | Forbidden | Recruiter or Employee trying to POST |

---

## 4️⃣ `PATCH /api/contracts/{id}/` — Partial Update

**Permission**: Admin, HR Manager only.

### Request — Update Contract Fields Only
```
PATCH /api/contracts/101/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```
```json
{
    "status": "Signed",
    "sign_off_date": "2027-01-15",
    "salary": "9000.00"
}
```

### Request — Update Contract + Seafarer Profile
```json
{
    "status": "Active",
    "personal_details": {"weight_kg": 85},
    "next_of_kin": {
        "full_name": "Sara Hassan", "relationship": "Wife",
        "address_country": "Egypt", "tel_no_mobile": "+201099999999",
        "email": "sara@example.com"
    },
    "marine_courses": [
        {"course_name": "Advanced Fire Fighting", "number": "AFF-010", "issue_date": "2026-03-01", "expiry_date": "2031-03-01", "issued_by_at": "AASTMT / Alex"},
        {"course_name": "Medical First Aid", "number": "MFA-011", "issue_date": "2026-03-05", "expiry_date": "2031-03-05", "issued_by_at": "AASTMT / Alex"}
    ]
}
```

### Response — `200 OK`
Returns full updated `ContractSerializer` response.

| Error Code | Reason |
|---|---|
| `400` | Invalid field values |
| `401` | Unauthorized |
| `403` | Recruiter/Employee attempting update |
| `404` | Contract ID not found |

---

## 5️⃣ `PUT /api/contracts/{id}/` — Full Update

**Permission**: Admin, HR Manager only. Same as PATCH but all required fields must be present.

```
PUT /api/contracts/101/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```
```json
{
    "user": 50, "ship": 2, "company": 5, "rank": 3,
    "sign_on_date": "2026-06-01", "sign_off_date": "2027-01-15",
    "salary": "9000.00", "currency": "USD", "status": "Active"
}
```

### Response — `200 OK`
| Error Code | Reason |
|---|---|
| `400` | Missing required fields (`sign_on_date`) |
| `401` | Unauthorized |
| `403` | Recruiter/Employee attempting update |
| `404` | Contract ID not found |

---

## 6️⃣ `DELETE /api/contracts/{id}/` — Delete Contract

**Permission**: Admin, HR Manager only.

```
DELETE /api/contracts/101/
Authorization: Bearer <JWT_TOKEN>
```

### Response — `204 No Content` (empty body)

| Error Code | Reason |
|---|---|
| `401` | Unauthorized |
| `403` | Recruiter/Employee attempting delete |
| `404` | Contract ID not found |

---

## 7️⃣ `GET /api/contracts/stats/` — Contract Statistics

**Permission**: All authenticated users (scoped by role).

```
GET /api/contracts/stats/
Authorization: Bearer <JWT_TOKEN>
```
```json
{
    "signed_contracts": 24,
    "pending_signature": 8,
    "drafts": 3,
    "critical": 2,
    "warning": 5,
    "notice": 7
}
```

| Field | Description |
|---|---|
| `signed_contracts` | Contracts with status `Signed` |
| `pending_signature` | Contracts with status `Pending Signature` |
| `drafts` | Contracts with status `Draft` |
| `critical` | Active/Signed contracts expiring within 7 days |
| `warning` | Active/Signed contracts expiring within 8–30 days |
| `notice` | Active/Signed contracts expiring within 31–60 days |

---

## 📝 Seafarer Application Write Fields Reference

These fields are **write-only** on POST/PATCH. They update the user's profile and appear in the **read-only** `seafarer_application` response object.

| Write Field | Type | What it Updates |
|---|---|---|
| `personal_details` | JSON object | User name, DOB, nationality, height, weight, sizes |
| `application_header` | JSON object | Position, register code, dates |
| `education` | JSON object | College, Marlins test, language levels |
| `contact_details` | JSON object | Address, email, phone |
| `travel_documents` | JSON array | Passport, seaman book fields on User |
| `professional_qualification` | JSON array | COC and GOC certificate fields |
| `next_of_kin` | JSON object | Emergency contact fields |
| `health_certificates` | JSON object | Medical, Yellow Fever, Cholera, COVID |
| `marine_courses` | JSON array | **Replaces all** courses for the user |
| `sea_service_details` | JSON object | **Replaces all** sea service records |
| `references` | JSON array | **Replaces all** reference records |
| `declaration` | JSON object | Declaration questions and consent |
| `for_office_use_only` | JSON object | Assessment comments, responsible person |

> ⚠️ **Important**: `marine_courses`, `sea_service_details.service_records`, and `references` use a **delete-and-recreate** pattern. When you send these fields, all existing records are deleted and replaced. Always send the complete list.
