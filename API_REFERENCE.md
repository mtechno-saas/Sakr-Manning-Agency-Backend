# Sakr Manning Agency — Complete API Reference

> All dates use **YYYY-MM-DD** format. All file uploads use **multipart/form-data**.
> All endpoints require **Authorization: Bearer {token}** unless noted.

---
## Authentication

### POST `/api/login/`
**Permission:** AllowAny

**Request Body:**
```json
{"email": "user@example.com", "password": "YourPassword123"}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### POST `/api/login/refresh/`
**Permission:** AllowAny

**Request Body:**
```json
{"refresh": "eyJhbGciOiJIUzI1NiIs..."}
```

### POST `/api/users/register/`
**Permission:** AllowAny

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "middle_name": "Michael",
  "role": "Employee"
}
```

### POST `/api/users/logout/`
**Permission:** IsAuthenticated

---
## Users

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/users/` | List all users | Admin, HR Manager, Recruiter (read-only), Employee (own) |
| GET | `/api/users/users/{id}/` | Get user by ID | Admin, HR Manager, Recruiter (read-only), Employee (own) |
| POST | `/api/users/users/` | Create user | Admin (all), HR Manager (non-admin) |
| PATCH | `/api/users/users/{id}/` | Update user | Admin (all), HR Manager (non-admin), Employee (own) |
| DELETE | `/api/users/users/{id}/` | Delete user | Admin only |

### User Fields & Choices

#### `role` choices:
| Value |
|-------|
| Admin |
| HR Manager |
| Recruiter |
| Employee |

#### `application_for_position` choices:
| Value |
|-------|
| Master |
| 1st. Officer – Chief Off. |
| 2nd. Officer |
| 3rd. Officer |
| Tug Master |
| Boson |
| A.B – O.S |
| Steward / Galley Boy |
| Cook / 2nd. Cook / Ass. Cook / Baker / Pastry |
| Carpenter |
| Waiter |
| Purser |
| Doctor |
| 1st. Engineer |
| 2nd. Engineer |
| 3rd. Engineer |
| Electrical Engineer – E/E – ETO |
| Assistant Electrician |
| 4th. Engineer |
| Electrician |
| Motor Man / Mechanic |
| Oiler |
| Fitter – Welder |
| Wiper |
| Other |

#### `coc_certificate_name` choices:
| Value |
|-------|
| Master |
| Chief Mate |
| 2nd Officer |
| 3rd Officer |
| Marine Chief Eng. |
| 2nd Marine Eng. |
| 3rd Marine Eng. |
| Electro-Technical Officer |
| Gmdss General Operator |

#### `user_status` choices:
| Value | Label |
|-------|-------|
| VACATION | VACATION |
| ON_SITE | ON_SITE |
| MEDICAL VACATION | MEDICAL VACATION |

### Request Body Example — PATCH `/api/users/users/{id}/`
```json
{
  "first_name": "John",
  "middle_name": "Michael",
  "date_of_birth": "1991-05-15",
  "nationality": "Egyptian",
  "marital_status": "Single",
  "role": "Employee",
  "application_for_position": "1st. Engineer",
  "available_date": "2025-04-01",
  "salary": "3500.00",
  "phone_number": "+201234567890",
  "country": "Egypt",
  "city": "Alexandria",
  "Height_Cm": 175,
  "Weight_Kg": 80,
  "passport_no": "A12345678",
  "passport_issue_date": "2022-03-01",
  "passport_expiry_date": "2029-03-01",
  "coc_certificate_name": "Master",
  "coc_certificate_number": "COC-5432",
  "coc_issue_date": "2021-06-01",
  "coc_expiry_date": "2026-06-01"
}
```

### Response Body Example
```json
{
  "id": 33,
  "email": "john@example.com",
  "first_name": "John",
  "middle_name": "Michael",
  "profile_image": "/media/users/profile.jpg",
  "role": "Employee",
  "salary": "3500.00",
  "application_for_position": "1st. Engineer",
  "passport_no": "A12345678",
  "passport_attachment": "/media/passports/scan.pdf",
  "seaman_book_attachment": "/media/seaman_books/book.pdf",
  "coc_certificate_name": "Master",
  "ranks": [{"id": 1, "rank_name": "1st. Engineer", "assigned_code": "EO-1.001"}],
  "certificates": [{"id": 1, "code": "GMDSS", "name": "G.M.D.S.S"}],
  "references": [],
  "sea_services": [],
  "bmi": {"value": 26.1, "category": "Overweight"},
  "created_at": "2024-01-10T10:00:00Z"
}
```

---
## References

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/references/?user={id}` | List | All authenticated |
| POST | `/api/users/references/` | Create | All authenticated |
| PATCH | `/api/users/references/{id}/` | Update | All authenticated |
| DELETE | `/api/users/references/{id}/` | Delete | All authenticated |

### Request Body — POST
```json
{"user": 5, "name": "Capt. Ahmed", "company_name": "Maersk", "position": "Master", "email": "ahmed@maersk.com", "tel": "+201555123456"}
```

### Response Body
```json
{"id": 1, "user": 5, "name": "Capt. Ahmed", "company_name": "Maersk", "position": "Master", "email": "ahmed@maersk.com", "tel": "+201555123456"}
```

---
## Sea Services

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/sea-services/?user={id}` | List | All authenticated |
| POST | `/api/users/sea-services/` | Create | All authenticated |
| PATCH | `/api/users/sea-services/{id}/` | Update | All authenticated |
| DELETE | `/api/users/sea-services/{id}/` | Delete | All authenticated |

### Request Body — POST (`multipart/form-data`)
```json
{
  "user": 5, "company_name": "Maersk", "rank": "1st. Engineer",
  "vessel_name": "MV Explorer", "imo_number": "9876543", "flag": "Panama",
  "signed_on": "2024-03-01", "signed_off": "2024-09-15",
  "vessel_type": "Bulk Carrier", "dwt": "75000", "grt": "42000",
  "engine_type": "MAN B&W", "reason_for_sign_off": "End of contract"
}
```

### Response Body
```json
{
  "id": 1, "user": 5, "company_name": "Maersk", "rank": "1st. Engineer",
  "vessel_name": "MV Explorer", "signed_on": "2024-03-01", "signed_off": "2024-09-15",
  "period": "6m 14d", "vessel_type": "Bulk Carrier", "file": null
}
```

---
## Professional Qualifications / Licenses

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/my-licenses/?user={id}` | List | All authenticated |
| POST | `/api/my-licenses/` | Create | All authenticated |
| PATCH | `/api/my-licenses/{id}/` | Update | All authenticated |
| DELETE | `/api/my-licenses/{id}/` | Delete | All authenticated |
| GET | `/api/my-licenses/{id}/download/` | Download | All authenticated |

#### `document_name` choices:
| Value |
|-------|
| Master (Reg. II/2 Par. 1-2) |
| Master (Reg. II/2 Par. 1-2) Endorsement |
| Master <3,000 GRT (Reg. II/2 Par. 3-4) |
| Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement |
| Master <500 GRT (Reg. II/3 Par. 5-6) |
| Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement |
| Yachtmaster Coastal |
| Chief Officer (Reg. II/2 Par. 1-2) |
| Chief Officer (Reg. II/2 Par. 1-2) Endorsement |
| Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) |
| Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement |
| Navigational Watch Officer (Reg. II/1) |
| Navigational Watch Officer (Reg. II/1) Endorsement |
| Navigational Watch Officer <500 GRT (II/3 Par. 3-4) |
| Chief Engineer (Reg. III/2) |
| Chief Engineer (Reg. III/2) Endorsement |
| Chief Engineer – Steam (Reg. III/2) |
| Chief Engineer – Steam (Reg. III/2) Endorsement |
| Chief Engineer <3,000 KW (Reg. III/3) |
| 2nd Engineer (Reg. III/2) |
| 2nd Engineer (Reg. III/2) Endorsement |
| 2nd Engineer – Steam (Reg. III/3) |
| 2nd Engineer – Steam (Reg. III/3) Endorsement |
| 2nd Engineer <3,000 KW (Reg. III/3) |
| Engineering Watch Officer (Reg. III/1) |
| Engineering Watch Officer (Reg. III/1) Endorsement |
| Electro Technical Officer (Reg. III/6) |
| Electro Technical Officer (Reg. III/6) Endorsement |
| Electro Technical Rating (Reg. III/7) |
| Able Seaman Deck (Reg. II/5) |
| Able Seaman Deck (Reg. II/5) Endorsement |
| Able Seaman Engine (Reg. III/5) |
| Able Seaman Engine (Reg. III/5) Endorsement |
| Qualified Steward/Messman Endorsement |
| GMDSS Radio Operator (Reg. IV/2) |
| GMDSS Radio Operator (Reg. IV/2) Endorsement |
| GMDSS Endorsement (Reg. IV/2) Flag CRA |
| GMDSS Restricted Operator (ROC) (Reg. IV/2) |
| GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement |
| GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA |
| Qualified Ship’s Cook (MLC 2006) |
| Qualified Ship’s Cook (MLC 2006) Endorsement |
| Navigational Watch Rating (Reg. II/4) |
| Navigational Watch Rating (Reg. II/4) Endorsement |
| COC – Certificate of Competency |
| COC – Certificate of Competency Endorsement |
| GOC – General Operator Certificate |
| GOC – General Operator Certificate Endorsement |

### Request Body — POST (`multipart/form-data`)
```json
{"user": 5, "document_name": "Master (Reg. II/2 Par. 1-2)", "document_number": "COC-9999", "country_of_issue": "Egypt", "issue_date": "2024-01-01", "expiration_date": "2029-01-01", "document_file": "(PDF)"}
```

### Response Body
```json
{"id": 1, "user": 5, "document_name": "Master (Reg. II/2 Par. 1-2)", "document_number": "COC-9999", "country_of_issue": "Egypt", "issue_date": "2024-01-01", "expiration_date": "2029-01-01", "document_file": "/media/user_5/licenses/coc.pdf", "created_at": "2026-03-10T00:00:00Z", "updated_at": "2026-03-10T00:00:00Z"}
```

---
## Personal Documents

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/personal-documents/?user={id}` | List | All authenticated |
| POST | `/api/users/personal-documents/` | Create | All authenticated |
| PATCH | `/api/users/personal-documents/{id}/` | Update | All authenticated |
| DELETE | `/api/users/personal-documents/{id}/` | Delete | All authenticated |

#### `document_type` choices:
| Value |
|-------|
| Bahamas Seaman's Book |
| Belize Seaman's Book |
| Bermuda Seaman's Book |
| Eu National Id |
| Exit Interview |
| Liberian Seaman's Book |
| Local Id Card |
| Luxembourg Seaman's Book |
| Palau Seaman's Book |
| Panama Seaman's Book |
| Passport |
| Permesso Soggiorno Permanente |
| Permesso Soggiorno Temporaneo |
| Personal Record Sheet |
| Residence Certificate |
| Seafarers' Id. Doc. Ilo 185 |
| Seaman's Book |
| Seaman's Book/Card Or Id |
| U.K. Seaman's Book |

**Accepted files:** PDF, DOCX, DOC, JPG, JPEG, PNG

### Request Body — POST (`multipart/form-data`)
```json
{"user": 5, "document_type": "Passport", "document_number": "A12345678", "issue_date": "2022-03-01", "expiry_date": "2029-03-01", "issuing_country": "Egypt", "issued_by": "Ministry of Interior", "place_of_issue": "Cairo", "file": "(file)"}
```

### Response Body
```json
{"id": 14, "user": 5, "document_type": "Passport", "document_number": "A12345678", "issue_date": "2022-03-01", "expiry_date": "2029-03-01", "issuing_country": "Egypt", "issued_by": "Ministry of Interior", "place_of_issue": "Cairo", "file": "/media/personal_documents/passport.pdf", "created_at": "2026-03-10T00:00:00Z", "updated_at": "2026-03-10T00:00:00Z"}
```

---
## Next of Kin

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/next-of-kin/?user={id}` | List | All authenticated |
| POST | `/api/users/next-of-kin/` | Create | All authenticated |
| PATCH | `/api/users/next-of-kin/{id}/` | Update | All authenticated |
| DELETE | `/api/users/next-of-kin/{id}/` | Delete | All authenticated |

#### `relationship` choices:
| Value |
|-------|
| Father |
| Mother |
| Brother |
| Sister |
| Wife |
| Husband |
| Son |
| Daughter |
| Uncle |
| Aunt |
| Friend |
| Other |

### Request Body — POST
```json
{"user": 5, "full_name": "Jane Doe", "relationship": "Wife", "address_country": "Egypt", "phone": "+201098765432", "phone2": "+201555666777", "email": "jane@example.com"}
```

### Response Body
```json
{"id": 1, "user": 5, "full_name": "Jane Doe", "relationship": "Wife", "address_country": "Egypt", "phone": "+201098765432", "phone2": "+201555666777", "email": "jane@example.com", "created_at": "2026-03-10T00:00:00Z", "updated_at": "2026-03-10T00:00:00Z"}
```

---
## Languages

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/user-languages/?user={id}` | List | All authenticated |
| POST | `/api/users/user-languages/` | Create | All authenticated |
| PATCH | `/api/users/user-languages/{id}/` | Update | All authenticated |
| DELETE | `/api/users/user-languages/{id}/` | Delete | All authenticated |

#### `speaking_level` / `writing_level` / `reading_level` choices:
| Value |
|-------|
| Elementary |
| Intermediate |
| Advanced |
| Native |

#### `cefr_level` choices:
| Value |
|-------|
| A1 |
| A2 |
| B1 |
| B2 |
| C1 |
| C2 |

### Request Body — POST
```json
{"user": 5, "language": "English", "general_remarks": "Fluent", "speaking_level": "Advanced", "writing_level": "Advanced", "reading_level": "Native", "cefr_level": "C1", "cefr_description": "Can understand complex texts"}
```

### Response Body
```json
{"id": 1, "user": 5, "language": "English", "speaking_level": "Advanced", "writing_level": "Advanced", "reading_level": "Native", "cefr_level": "C1", "attachment": null, "created_at": "2026-03-10T00:00:00Z", "updated_at": "2026-03-10T00:00:00Z"}
```

---
## Courses

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/courses/?user={id}` | List | All authenticated |
| POST | `/api/courses/` | Create | All authenticated |
| PATCH | `/api/courses/{id}/` | Update | All authenticated |
| DELETE | `/api/courses/{id}/` | Delete | All authenticated |
| GET | `/api/courses/{id}/download/` | Download | All authenticated |

### Request Body — POST (`multipart/form-data`)
```json
{"user": 5, "course_name": "Fire Prevention", "course_number": "FPFF-2024", "issue_date": "2024-06-01", "expiry_date": "2029-06-01", "issued_by": "AASTMT", "issued_at": "Alexandria", "country_of_issue": "Egypt", "document": "(file)"}
```

### Response Body
```json
{"id": 1, "user": 5, "course_name": "Fire Prevention", "course_number": "FPFF-2024", "issue_date": "2024-06-01", "expiry_date": "2029-06-01", "issued_by": "AASTMT", "issued_at": "Alexandria", "country_of_issue": "Egypt", "document": "/media/course_docs/fire_cert.pdf"}
```

---
## Vaccinations

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/vaccinations/?user={id}` | List | All authenticated (own records) |
| POST | `/api/vaccinations/` | Create | All authenticated (own records) |
| PATCH | `/api/vaccinations/{id}/` | Update | All authenticated (own records) |
| DELETE | `/api/vaccinations/{id}/` | Delete | All authenticated (own records) |

#### `name` choices:
| Value |
|-------|
| Quarantine Letter |
| Rubella Immunity |
| Tessera Sanitaria |
| Tuberculosis Laboratory Screen |
| Typhoid Vaccination |
| Varicella Immunization |
| Yellow Fever Immunization |
| Chickenpox Immunity Screening |
| Color Vision Certificate |
| Covid-Sars Vaccination |
| Covid Form |
| Foodhandler Exams |
| Health Questionnaire |
| Hepatitis A Immunization |
| Hepatitis B Immunization |
| Italian Medical Pre-Embark Examination |
| Measles Immunity |
| Medical Certificate For Seafarers |
| Mmr Booster 2 |
| Mmr Vaccination / Immunization |
| Mumps Immunity |
| Pertussis Immunization |

**Accepted files:** PDF only

### Request Body — POST (`multipart/form-data`)
```json
{"user": 5, "name": "Yellow Fever Immunization", "number": "YF-9012", "issue_date": "2023-09-01", "expiry_date": "2033-09-01", "issued_by": "Port Health Authority", "issued_at": "Alexandria", "disease": "Yellow Fever", "remarks": "Valid for 10 years", "document": "(PDF)"}
```

### Response Body
```json
{"id": 1, "user": 5, "name": "Yellow Fever Immunization", "number": "YF-9012", "issue_date": "2023-09-01", "expiry_date": "2033-09-01", "issued_by": "Port Health Authority", "issued_at": "Alexandria", "disease": "Yellow Fever", "first_date": null, "last_date": null, "remarks": "Valid for 10 years", "document": "/media/vaccinations/yf_cert.pdf", "created_at": "2026-03-10T00:00:00Z", "updated_at": "2026-03-10T00:00:00Z"}
```

---
## Documents (CV / Quick Apply)

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/documents/` | List | Admin, HR Manager (all), Recruiter (view), Employee (own) |
| POST | `/api/users/documents/` | Upload CV | **AllowAny** (public) |
| PATCH | `/api/users/documents/{id}/` | Update status | Admin, HR Manager, Recruiter |
| DELETE | `/api/users/documents/{id}/` | Delete | Admin, HR Manager |

#### `position` choices:
| Value |
|-------|
| Master |
| 1st. Officer – Chief Off. |
| 2nd. Officer |
| 3rd. Officer |
| Tug Master |
| Boson |
| A.B – O.S |
| Steward / Galley Boy |
| Cook / 2nd. Cook / Ass. Cook / Baker / Pastry |
| Carpenter |
| Waiter |
| Purser |
| Doctor |
| 1st. Engineer |
| 2nd. Engineer |
| 3rd. Engineer |
| Electrical Engineer – E/E – ETO |
| Assistant Electrician |
| 4th. Engineer |
| Electrician |
| Motor Man / Mechanic |
| Oiler |
| Fitter – Welder |
| Wiper |
| Other |

#### `status` choices:
| Value |
|-------|
| Pending |
| Active |
| Blacklist |

**Accepted files:** PDF, DOCX

### Request Body — POST (`multipart/form-data`)
```json
{"name": "John Doe", "email": "john@example.com", "phone_number": "+201234567890", "position": "1st. Engineer", "file": "(PDF or DOCX)"}
```

### Response Body
```json
{"id": 1, "user": 33, "title": "cv_john.pdf", "file": "/media/documents/cv_john.pdf", "name": "John Doe", "email": "john@example.com", "phone_number": "+201234567890", "position": "1st. Engineer", "status": "Pending", "generated_id": null, "created_at": "2026-03-10T00:00:00Z", "updated_at": "2026-03-10T00:00:00Z"}
```

---
## Declarations

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/declarations/` | List | All authenticated |
| POST | `/api/users/declarations/` | Create | All authenticated |
| PATCH | `/api/users/declarations/{id}/` | Update | All authenticated |

### Request Body — POST
```json
{"user": 5, "has_disease": false, "disease_details": "", "has_accident": false, "has_psychiatric_treatment": false, "has_addiction": false, "consent_given": true, "declaration_place": "Alexandria", "declaration_date": "2026-03-10", "signature": "John Doe"}
```

---
## Companies

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/companies/` | List | All authenticated (read-only for Employee) |
| POST | `/api/companies/` | Create | Admin only |
| GET | `/api/companies/{id}/` | Get | All authenticated |
| PATCH | `/api/companies/{id}/` | Update | Admin, HR Manager, Recruiter |
| DELETE | `/api/companies/{id}/` | Delete | Admin only |
| GET | `/api/companies/stats/` | Stats | All authenticated |

#### `company_type` choices:
| Value |
|-------|
| Shipping Manning Companies |
| Cargo Manning Companies |
| Cruise & Hospitality Manning Companies |
| Offshore & Oil/Gas Manning Companies |
| Fishing Fleet Manning Companies |
| General Crew Manning Companies |
| Specialized Marine Manning Companies |
| Temporary / Contract Manning Agencies |
| Full Crew Management Companies |
| Other |

#### `status` choices:
| Value |
|-------|
| Active |
| Inactive |
| Prospect |

### Request Body — POST
```json
{"company_name": "Maersk Line", "company_type": "Shipping Manning Companies", "open_positions": 5, "status": "Active", "contact_email": "hr@maersk.com", "hourly_rate": 50.00}
```

---
## Ships

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/ships/` | List | All authenticated |
| POST | `/api/ships/` | Create | All authenticated |
| GET | `/api/ships/{id}/` | Get | All authenticated |
| PATCH | `/api/ships/{id}/` | Update | All authenticated |
| DELETE | `/api/ships/{id}/` | Delete | All authenticated |

#### `status` choices:
| Value |
|-------|
| Active |
| Under Maintenance |
| Inactive |

### Request Body — POST
```json
{"ship_name": "MV Explorer", "imo_number": "9876543", "company": 1, "ship_type": 1, "flag": 1, "gross_tonnage": 42000, "deadweight": 75000, "year_built": 2015, "engine_type": "MAN B&W", "engine_power_kw": 11190, "status": "Active"}
```

---
## Contracts

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/contracts/` | List | Admin, HR Manager (all), Recruiter/Employee (own, read-only) |
| POST | `/api/users/contracts/` | Create | Admin, HR Manager |
| PATCH | `/api/users/contracts/{id}/` | Update | Admin, HR Manager |

#### `status` choices:
| Value |
|-------|
| Pending |
| Active |
| Completed |
| Cancelled |

#### `currency` choices:
| Value | Label |
|-------|-------|
| USD | US Dollar |
| EUR | Euro |
| GBP | British Pound |
| EGP | Egyptian Pound |

### Request Body — POST
```json
{"user": 5, "ship": 1, "company": 1, "rank": 1, "sign_on_date": "2024-03-01", "sign_off_date": "2024-09-15", "salary": 3500.00, "currency": "USD", "status": "Active"}
```

---
## Interviews

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/interviews/` | List | Admin, HR Manager, Recruiter (all), Employee (own, read-only) |
| POST | `/api/users/interviews/` | Create | Admin, HR Manager, Recruiter |
| PATCH | `/api/users/interviews/{id}/` | Update | Admin, HR Manager, Recruiter |

#### `interview_type` choices:
| Value |
|-------|
| Phone |
| Video |
| In-Person |
| Technical |

#### `status` choices:
| Value |
|-------|
| Scheduled |
| Completed |
| Cancelled |
| Rescheduled |
| No Show |

#### `result` choices:
| Value |
|-------|
| Pending |
| Passed |
| Failed |
| On Hold |

### Request Body — POST
```json
{"candidate": 5, "company": 1, "position": 1, "scheduled_date": "2026-04-01", "scheduled_time": "10:00", "duration_minutes": 30, "interview_type": "Video", "meeting_link": "https://zoom.us/j/123456", "status": "Scheduled", "result": "Pending"}
```

---
## Lookup Endpoints

| Method | URL | Returns | Permission |
|--------|-----|---------|------------|
| GET | `/api/users/positions/` | Position choices `[{"value": "...", "label": "..."}]` | All authenticated |
| GET | `/api/users/flags/` | Country flags `[{"value": "...", "label": "..."}]` | All authenticated |
| GET | `/api/users/coc-choices/` | COC choices `[{"value": "...", "label": "..."}]` | All authenticated |
| GET | `/api/core/flags/` | Flags `[{"id": 1, "name": "Egypt"}]` | All authenticated |
| GET | `/api/core/vessel-types/` | Vessel types `[{"id": 1, "name": "Bulk Carrier"}]` | All authenticated |
| GET | `/api/users/ranks/` | Ranks `[{"id": 1, "code": "MAS", "name": "Master"}]` | All authenticated |
| GET | `/api/users/certificates/` | Certificates `[{"id": 1, "code": "GMDSS", "name": "G.M.D.S.S"}]` | All authenticated |

---
## Job Orders

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/companies/job-orders/` | List | All authenticated |
| POST | `/api/companies/job-orders/` | Create | Admin, HR Manager |
| PATCH | `/api/companies/job-orders/{id}/` | Update | Admin, HR Manager |

#### `status` choices:
| Value | Label |
|-------|-------|
| Pending | Pending Review |
| Open | Open / Sourcing |
| In Progress | In Progress / Interviewing |
| Fulfilled | Fulfilled |
| Cancelled | Cancelled |

### Request Body — POST
```json
{"company": 1, "ship": 1, "reference_number": "JO-2024-001", "request_date": "2024-01-15", "target_joining_date": "2024-03-01", "status": "Open"}
```