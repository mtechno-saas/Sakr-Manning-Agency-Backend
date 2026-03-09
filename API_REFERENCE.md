# Sakr Manning Agency — API Reference

---

## Authentication

### Login
- **POST** `/api/login/`
- **Body:** `{"email": "...", "password": "..."}`
- **Response:** `{"access": "JWT_TOKEN", "refresh": "..."}`
- **Permission:** AllowAny

### Register
- **POST** `/api/users/register/`
- **Permission:** AllowAny

### Logout
- **POST** `/api/users/logout/`
- **Permission:** IsAuthenticated

### Refresh Token
- **POST** `/api/login/refresh/`
- **Body:** `{"refresh": "REFRESH_TOKEN"}`
- **Permission:** AllowAny

---

## Users

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/users/` | List all users | IsAuthenticated |
| GET | `/api/users/users/{id}/` | Get user by ID | IsAuthenticated |
| POST | `/api/users/users/` | Create user | IsAuthenticated |
| PATCH | `/api/users/users/{id}/` | Update user | IsAuthenticated |
| DELETE | `/api/users/users/{id}/` | Delete user | IsAuthenticated |
| GET | `/api/users/all/` | Get all users (flat list) | IsAuthenticated |
| POST | `/api/users/create/` | Create user (alt) | IsAuthenticated |
| GET | `/api/users/filter/` | Filter users | IsAuthenticated |

### User Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | Auto-generated |
| email | string | ✅ | Unique |
| password | string | ✅ (create) | Write-only |
| first_name | string | ✅ | |
| middle_name | string | ❌ | |
| profile_image | file | ❌ | Image upload |
| age | int | ❌ | |
| blood_type | string | ❌ | |
| smoker | bool | ❌ | Default: false |
| date_of_birth | date | ❌ | YYYY-MM-DD |
| marital_status | string | ❌ | Default: "Single" |
| user_status | string | ❌ | See choices below |
| nationality | string | ❌ | |
| Place_Of_Birth | string | ❌ | |
| Nearest_Port | string | ❌ | |
| Height_Cm | int | ❌ | For BMI calculation |
| Weight_Kg | int | ❌ | For BMI calculation |
| college_or_school | string | ❌ | |
| salary | string | ❌ | String field (accepts any format) |
| address | string | ❌ | |
| phone_number | string | ❌ | |
| tel_number | string | ❌ | |
| country | string | ❌ | |
| city | string | ❌ | |
| role | string | ❌ | See choices |
| register_code | string | read-only | Auto-generated |
| register_date | date | ❌ | YYYY-MM-DD |
| last_updated_date | datetime | read-only | Auto-updated |
| generated_id | string | read-only | 12-digit ID |
| application_for_position | string | ❌ | See choices |
| other_position | string | ❌ | Free text |
| available_date | date | ❌ | YYYY-MM-DD |
| us_visa_status | string | ❌ | |
| schengen_visa_status | string | ❌ | |
| is_blacklisted | bool | ❌ | Default: false |
| blacklist_reason | string | ❌ | |
| created_at | datetime | read-only | |
| updated_at | datetime | read-only | |

### Travel Documents (on User)
| Field | Type | Notes |
|-------|------|-------|
| passport_no | string | |
| passport_issue_date | date | |
| passport_expiry_date | date | |
| passport_issued_by | string | |
| passport_place_of_issue | string | |
| passport_attachment | file | Upload via multipart/form-data |
| seaman_book_no | string | |
| seaman_book_issue_date | date | |
| seaman_book_expiry_date | date | |
| seaman_book_issued_by | string | |
| seaman_book_place_of_issue | string | |
| seaman_book_attachment | file | Upload via multipart/form-data |
| other_seaman_book_no | string | |
| other_seaman_book_issue_date | date | |
| other_seaman_book_expiry_date | date | |
| other_seaman_book_issued_by | string | |
| other_seaman_book_place_of_issue | string | |
| other_seaman_book_attachment | file | Upload via multipart/form-data |

### COC — Certificate of Competency (on User)
| Field | Type | Notes |
|-------|------|-------|
| coc_certificate_name | string | See choices |
| coc_certificate_number | string | |
| coc_issue_date | date | |
| coc_expiry_date | date | |
| coc_issued_by | string | |
| coc_issued_at | string | |

### GOC — General Operator Certificate (on User)
| Field | Type | Notes |
|-------|------|-------|
| goc_certificate_number | string | |
| goc_issue_date | date | |
| goc_expiry_date | date | |
| goc_issued_by | string | |
| goc_issued_at | string | |

### Marlins & CES Tests (on User)
| Field | Type | Notes |
|-------|------|-------|
| marlins_test_result | string | |
| marlins_test_issued_date | date | |
| marlins_test_issued_by | string | |
| marlins_test_issued_at | string | |
| marlins_test_attachment | file | Upload via multipart/form-data |
| ces_test_result | string | |
| ces_test_issued_date | date | |
| ces_test_issued_by | string | |
| ces_test_issued_at | string | |
| ces_test_attachment | file | Upload via multipart/form-data |

### Health Certificates (on User)
| Field | Type |
|-------|------|
| health_flag_state | string |
| health_number | string |
| health_issue_date | date |
| health_expiry_date | date |
| health_issued_by | string |
| health_issued_at | string |
| international_medical_number | string |
| international_medical_issue_date | date |
| international_medical_expiry_date | date |
| yellow_fever_number | string |
| yellow_fever_issue_date | date |
| yellow_fever_expiry_date | date |
| cholera_number | string |
| cholera_issue_date | date |
| cholera_expiry_date | date |
| covid_vaccine_name | string |
| covid_first_dose | date |
| covid_second_dose | date |
| covid_other_doses_or_remarks | string |

### Next of Kin (flat on User)
| Field | Type |
|-------|------|
| next_of_kin_full_name | string |
| next_of_kin_relationship | string |
| next_of_kin_address_country | string |
| next_of_kin_phone | string |
| next_of_kin_phone2 | string |
| next_of_kin_email | string |

### Other Fields (on User)
| Field | Type |
|-------|------|
| overall_size | string |
| shirt_size | string |
| trouser_size | string |
| shoes_size | string |
| english_language_level | string |
| other_language | string |
| other_language_level | string |
| disease_history | string |
| accident_history | string |
| psychiatric_treatment_history | string |
| addiction_history | string |
| declaration_consent | bool |
| declaration_date | date |
| declaration_place | string |
| initial_assessment_comments | string |
| responsible_person_name | string |
| assessment_date | date |

### Nested (Read-Only in Response)
| Field | Type | Description |
|-------|------|-------------|
| ranks | array | User's assigned ranks |
| certificates | array | User's certificates |
| references | array | User's references |
| sea_services | array | User's sea service records |
| bmi | object | `{"value": 26.1, "category": "Overweight"}` |

---

## References

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/references/?user={id}` | List user's references | IsAuthenticated |
| POST | `/api/users/references/` | Create reference | IsAuthenticated |
| PATCH | `/api/users/references/{id}/` | Update reference | IsAuthenticated |
| DELETE | `/api/users/references/{id}/` | Delete reference | IsAuthenticated |

### Fields
| Field | Type | Required |
|-------|------|----------|
| id | int | read-only |
| user | int | ✅ (in body for other users) |
| name | string | ❌ |
| company_name | string | ❌ |
| position | string | ❌ (choice field — see Positions) |
| email | string | ❌ |
| tel | string | ❌ |

---

## Sea Services

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/sea-services/?user={id}` | List user's sea services | IsAuthenticated |
| POST | `/api/users/sea-services/` | Create sea service | IsAuthenticated |
| PATCH | `/api/users/sea-services/{id}/` | Update sea service | IsAuthenticated |
| DELETE | `/api/users/sea-services/{id}/` | Delete sea service | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | ✅ | |
| company_name | string | ❌ | |
| rank | string | ❌ | |
| vessel_name | string | ❌ | |
| imo_number | string | ❌ | |
| flag | string | ❌ | |
| signed_on | date | ❌ | YYYY-MM-DD |
| signed_off | date | ❌ | YYYY-MM-DD |
| period | string | read-only | Auto-calculated |
| vessel_type | string | ❌ | |
| dwt | string | ❌ | |
| grt | string | ❌ | |
| engine_type | string | ❌ | |
| bh | string | ❌ | |
| kw | string | ❌ | |
| file | file | ❌ | Upload via multipart/form-data |
| reason_for_sign_off | string | ❌ | |

---

## Professional Qualifications / Licenses

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/my-licenses/?user={id}` | List user's licenses | IsAuthenticated |
| POST | `/api/my-licenses/` | Create license | IsAuthenticated |
| PATCH | `/api/my-licenses/{id}/` | Update license | IsAuthenticated |
| DELETE | `/api/my-licenses/{id}/` | Delete license | IsAuthenticated |
| GET | `/api/my-licenses/{id}/download/` | Download license file | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | auto/optional | Send user ID to create for another user |
| document_name | string | ✅ | See choices |
| document_number | string | ✅ | |
| country_of_issue | string | ✅ | |
| issue_date | date | ✅ | YYYY-MM-DD |
| expiration_date | date | ✅ | YYYY-MM-DD |
| document_file | file | ❌ | PDF only |
| created_at | datetime | read-only | |
| updated_at | datetime | read-only | |

---

## Personal Documents

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/personal-documents/?user={id}` | List personal docs | IsAuthenticated |
| GET | `/api/users/personal-documents/{id}/` | Get single doc | IsAuthenticated |
| POST | `/api/users/personal-documents/` | Create personal doc | IsAuthenticated |
| PATCH | `/api/users/personal-documents/{id}/` | Update personal doc | IsAuthenticated |
| DELETE | `/api/users/personal-documents/{id}/` | Delete personal doc | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | ❌ | Auto-set to logged-in user |
| document_type | string | ✅ | See choices |
| document_number | string | ❌ | |
| issue_date | date | ❌ | YYYY-MM-DD |
| expiry_date | date | ❌ | YYYY-MM-DD |
| issuing_country | string | ❌ | |
| issued_by | string | ❌ | |
| place_of_issue | string | ❌ | |
| file | file | ❌ | PDF, DOCX, DOC, JPG, JPEG, PNG |
| created_at | datetime | read-only | |
| updated_at | datetime | read-only | |

---

## Next of Kin

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/next-of-kin/?user={id}` | List next of kin | IsAuthenticated |
| POST | `/api/users/next-of-kin/` | Create next of kin | IsAuthenticated |
| PATCH | `/api/users/next-of-kin/{id}/` | Update | IsAuthenticated |
| DELETE | `/api/users/next-of-kin/{id}/` | Delete | IsAuthenticated |

### Fields
| Field | Type | Required |
|-------|------|----------|
| id | int | read-only |
| user | int | ❌ (auto-set) |
| full_name | string | ✅ |
| relationship | string | ✅ (choice) |
| address_country | string | ❌ |
| phone | string | ✅ |
| phone2 | string | ❌ |
| email | string | ❌ |

---

## Languages

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/user-languages/?user={id}` | List languages | IsAuthenticated |
| POST | `/api/users/user-languages/` | Create language | IsAuthenticated |
| PATCH | `/api/users/user-languages/{id}/` | Update | IsAuthenticated |
| DELETE | `/api/users/user-languages/{id}/` | Delete | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | ❌ | |
| language | string | ✅ | |
| general_remarks | string | ❌ | |
| speaking_level | string | ❌ | See choices |
| writing_level | string | ❌ | See choices |
| reading_level | string | ❌ | See choices |
| cefr_level | string | ❌ | See choices |
| cefr_description | string | ❌ | |
| attachment | file | ❌ | |

---

## Courses

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/courses/?user={id}` | List courses | IsAuthenticated |
| POST | `/api/courses/` | Create course | IsAuthenticated |
| PATCH | `/api/courses/{id}/` | Update course | IsAuthenticated |
| DELETE | `/api/courses/{id}/` | Delete course | IsAuthenticated |
| GET | `/api/courses/{id}/download/` | Download document | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | ✅ | |
| course_name | string | ✅ | |
| course_number | string | ✅ | |
| issue_date | date | ✅ | YYYY-MM-DD |
| expiry_date | date | ✅ | YYYY-MM-DD |
| issued_by | string | ✅ | |
| issued_at | string | ✅ | |
| country_of_issue | string | ✅ | |
| document | file | ❌ | Upload via multipart/form-data |

---

## Vaccinations

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/vaccinations/?user={id}` | List vaccinations | IsAuthenticated |
| POST | `/api/vaccinations/` | Create vaccination | IsAuthenticated |
| PATCH | `/api/vaccinations/{id}/` | Update vaccination | IsAuthenticated |
| DELETE | `/api/vaccinations/{id}/` | Delete vaccination | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | ✅ | |
| name | string | ✅ | See choices |
| number | string | ❌ | |
| issue_date | date | ❌ | |
| expiry_date | date | ❌ | |
| issued_by | string | ❌ | |
| issued_at | string | ❌ | |
| disease | string | ❌ | |
| first_date | date | ❌ | |
| last_date | date | ❌ | |
| remarks | string | ❌ | |
| document | file | ❌ | PDF only |

---

## Documents (CV/Quick Apply)

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/documents/` | List documents | IsAuthenticated |
| POST | `/api/users/documents/` | Upload CV/document | AllowAny |
| PATCH | `/api/users/documents/{id}/` | Update | IsAuthenticated |
| DELETE | `/api/users/documents/{id}/` | Delete | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | read-only | |
| title | string | ❌ | Auto-set from filename |
| file | file | ✅ | PDF or DOCX only |
| name | string | ❌ | Applicant name |
| email | string | ❌ | |
| phone_number | string | ❌ | |
| position | string | ❌ | See choices |
| status | string | ❌ | See choices |
| generated_id | string | read-only | Visible to Admin/HR/Recruiter only |

---

## Declarations

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/declarations/` | List declarations | IsAuthenticated |
| POST | `/api/users/declarations/` | Create declaration | IsAuthenticated |
| PATCH | `/api/users/declarations/{id}/` | Update | IsAuthenticated |

### Fields
| Field | Type | Required |
|-------|------|----------|
| id | int | read-only |
| user | int | ❌ (auto-set) |
| has_disease | bool | ❌ |
| disease_details | string | ❌ |
| has_accident | bool | ❌ |
| accident_details | string | ❌ |
| has_psychiatric_treatment | bool | ❌ |
| psychiatric_treatment_details | string | ❌ |
| has_addiction | bool | ❌ |
| addiction_details | string | ❌ |
| consent_given | bool | ❌ |
| declaration_place | string | ❌ |
| declaration_date | date | ❌ |
| signature | string | ❌ |

---

## Companies

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/companies/` | List companies | IsAuthenticated |
| POST | `/api/companies/` | Create company | IsAuthenticated |
| GET | `/api/companies/{id}/` | Get company | IsAuthenticated |
| PATCH | `/api/companies/{id}/` | Update company | IsAuthenticated |
| DELETE | `/api/companies/{id}/` | Delete company | IsAuthenticated |
| GET | `/api/companies/stats/` | Company statistics | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| company_name | string | ✅ | Unique |
| company_type | string | ✅ | See choices |
| open_positions | int | ❌ | Default: 0 |
| status | string | ❌ | See choices |
| contact_email | string | ✅ | |
| hourly_rate | decimal | ❌ | |

---

## Ships

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/ships/` | List ships | IsAuthenticated |
| POST | `/api/ships/` | Create ship | IsAuthenticated |
| GET | `/api/ships/{id}/` | Get ship | IsAuthenticated |
| PATCH | `/api/ships/{id}/` | Update ship | IsAuthenticated |
| DELETE | `/api/ships/{id}/` | Delete ship | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| ship_name | string | ✅ | |
| imo_number | string | ✅ | Unique |
| company | int | ✅ | Company ID |
| ship_type | int | ❌ | VesselType FK |
| flag | int | ❌ | Flag FK |
| official_no | string | ❌ | |
| call_sign | string | ❌ | |
| mmsi_no | string | ❌ | |
| port_of_registry | string | ❌ | |
| gross_tonnage | int | ❌ | |
| deadweight | int | ❌ | |
| year_built | int | ❌ | |
| builder | string | ❌ | |
| engine_type | string | ❌ | |
| engine_power_kw | int | ❌ | |
| status | string | ❌ | See choices |

---

## Contracts

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/contracts/` | List contracts | IsAuthenticated |
| POST | `/api/users/contracts/` | Create contract | IsAuthenticated |
| GET | `/api/users/contracts/{id}/` | Get contract | IsAuthenticated |
| PATCH | `/api/users/contracts/{id}/` | Update contract | IsAuthenticated |

### Fields
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | int | read-only | |
| user | int | ✅ | |
| ship | int | ✅ | Ship ID |
| company | int | ❌ | Company ID |
| rank | int | ❌ | Rank ID |
| sign_on_date | date | ✅ | |
| sign_off_date | date | ❌ | |
| salary | decimal | ❌ | |
| currency | string | ❌ | See choices |
| status | string | ❌ | See choices |
| signed_file | file | ❌ | |

---

## Interviews

### Endpoints
| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/interviews/` | List interviews | IsAuthenticated |
| POST | `/api/users/interviews/` | Create interview | IsAuthenticated |
| PATCH | `/api/users/interviews/{id}/` | Update | IsAuthenticated |

### Fields
| Field | Type | Required |
|-------|------|----------|
| id | int | read-only |
| candidate | int | ✅ |
| company | int | ❌ |
| position | int | ❌ |
| scheduled_date | date | ✅ |
| scheduled_time | time | ✅ |
| duration_minutes | int | ❌ (default: 30) |
| interview_type | string | ❌ (choice) |
| location | string | ❌ |
| meeting_link | string | ❌ |
| interviewer_name | string | ❌ |
| interviewer_email | string | ❌ |
| status | string | ❌ (choice) |
| result | string | ❌ (choice) |
| notes | string | ❌ |
| feedback | string | ❌ |

---

## Lookup Endpoints

| Method | URL | Description | Permission |
|--------|-----|-------------|------------|
| GET | `/api/users/positions/` | All position choices | IsAuthenticated |
| GET | `/api/users/flags/` | All country flags | IsAuthenticated |
| GET | `/api/users/coc-choices/` | COC certificate name choices | IsAuthenticated |
| GET | `/api/core/flags/` | Flag list (id, name) | IsAuthenticated |
| GET | `/api/core/vessel-types/` | Vessel types (id, name) | IsAuthenticated |
| GET | `/api/users/ranks/` | Rank list (id, code, name) | IsAuthenticated |
| GET | `/api/users/certificates/` | Certificate list (id, code, name) | IsAuthenticated |

---

## All Choice Fields

### User Roles
| Value | Label |
|-------|-------|
| Admin | Admin |
| HR Manager | HR Manager |
| Recruiter | Recruiter |
| Employee | Employee |

### User Status
| Value | Label |
|-------|-------|
| ON_SITE | On Site |
| ON_LEAVE | On Leave |
| VACATION | Vacation |
| TERMINATED | Terminated |

### Application Position
| Value | Label |
|-------|-------|
| Master | Master |
| 1st. Officer – Chief Off. | 1st. Officer – Chief Off. |
| 2nd. Officer | 2nd. Officer |
| 3rd. Officer | 3rd. Officer |
| Tug Master | Tug Master |
| Boson | Boson |
| A.B – O.S | A.B – O.S |
| Steward / Galley Boy | Steward / Galley Boy |
| Cook / 2nd. Cook / Ass. Cook / Baker / Pastry | Cook / 2nd. Cook / Ass. Cook / Baker / Pastry |
| Carpenter | Carpenter |
| Waiter | Waiter |
| Purser | Purser |
| Doctor | Doctor |
| 1st. Engineer | 1st. Engineer |
| 2nd. Engineer | 2nd. Engineer |
| 3rd. Engineer | 3rd. Engineer |
| Electrical Engineer – E/E – ETO | Electrical Engineer – E/E – ETO |
| Assistant Electrician | Assistant Electrician |
| 4th. Engineer | 4th. Engineer |
| Electrician | Electrician |
| Motor Man / Mechanic | Motor Man / Mechanic |
| Oiler | Oiler |
| Fitter – Welder | Fitter – Welder |
| Wiper | Wiper |
| Other | Other |

### COC Certificate Names
| Value | Label |
|-------|-------|
| Master | Master |
| Chief Mate | Chief Mate |
| 2nd Officer | 2nd Officer |
| 3rd Officer | 3rd Officer |
| Marine Chief Eng. | Marine Chief Eng. |
| 2nd Marine Eng. | 2nd Marine Eng. |
| 3rd Marine Eng. | 3rd Marine Eng. |
| Electro-Technical Officer | Electro-Technical Officer |
| Gmdss General Operator | Gmdss General Operator |

### Relationship (Next of Kin)
| Value | Label |
|-------|-------|
| Father | Father |
| Mother | Mother |
| Brother | Brother |
| Sister | Sister |
| Wife | Wife |
| Husband | Husband |
| Son | Son |
| Daughter | Daughter |
| Uncle | Uncle |
| Aunt | Aunt |
| Friend | Friend |
| Other | Other |

### Personal Document Types
| Value | Label |
|-------|-------|
| Bahamas Seaman's Book | Bahamas Seaman's Book |
| Belize Seaman's Book | Belize Seaman's Book |
| Bermuda Seaman's Book | Bermuda Seaman's Book |
| Eu National Id | Eu National Id |
| Exit Interview | Exit Interview |
| Liberian Seaman's Book | Liberian Seaman's Book |
| Local Id Card | Local Id Card |
| Luxembourg Seaman's Book | Luxembourg Seaman's Book |
| Palau Seaman's Book | Palau Seaman's Book |
| Panama Seaman's Book | Panama Seaman's Book |
| Passport | Passport |
| Permesso Soggiorno Permanente | Permesso Soggiorno Permanente |
| Permesso Soggiorno Temporaneo | Permesso Soggiorno Temporaneo |
| Personal Record Sheet | Personal Record Sheet |
| Residence Certificate | Residence Certificate |
| Seafarers' Id. Doc. Ilo 185 | Seafarers' Id. Doc. Ilo 185 |
| Seaman's Book | Seaman's Book |
| Seaman's Book/Card Or Id | Seaman's Book/Card Or Id |
| U.K. Seaman's Book | U.K. Seaman's Book |

### License Document Names
| Value | Label |
|-------|-------|
| Master (Reg. II/2 Par. 1-2) | Master (Reg. II/2 Par. 1-2) |
| Master (Reg. II/2 Par. 1-2) Endorsement | Master (Reg. II/2 Par. 1-2) Endorsement |
| Master <3,000 GRT (Reg. II/2 Par. 3-4) | Master <3,000 GRT (Reg. II/2 Par. 3-4) |
| Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement | Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement |
| Master <500 GRT (Reg. II/3 Par. 5-6) | Master <500 GRT (Reg. II/3 Par. 5-6) |
| Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement | Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement |
| Yachtmaster Coastal | Yachtmaster Coastal |
| Chief Officer (Reg. II/2 Par. 1-2) | Chief Officer (Reg. II/2 Par. 1-2) |
| Chief Officer (Reg. II/2 Par. 1-2) Endorsement | Chief Officer (Reg. II/2 Par. 1-2) Endorsement |
| Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) | Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) |
| Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement | Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement |
| Navigational Watch Officer (Reg. II/1) | Navigational Watch Officer (Reg. II/1) |
| Navigational Watch Officer (Reg. II/1) Endorsement | Navigational Watch Officer (Reg. II/1) Endorsement |
| Navigational Watch Officer <500 GRT (II/3 Par. 3-4) | Navigational Watch Officer <500 GRT (II/3 Par. 3-4) |
| Chief Engineer (Reg. III/2) | Chief Engineer (Reg. III/2) |
| Chief Engineer (Reg. III/2) Endorsement | Chief Engineer (Reg. III/2) Endorsement |
| Chief Engineer – Steam (Reg. III/2) | Chief Engineer – Steam (Reg. III/2) |
| Chief Engineer – Steam (Reg. III/2) Endorsement | Chief Engineer – Steam (Reg. III/2) Endorsement |
| Chief Engineer <3,000 KW (Reg. III/3) | Chief Engineer <3,000 KW (Reg. III/3) |
| 2nd Engineer (Reg. III/2) | 2nd Engineer (Reg. III/2) |
| 2nd Engineer (Reg. III/2) Endorsement | 2nd Engineer (Reg. III/2) Endorsement |
| 2nd Engineer – Steam (Reg. III/3) | 2nd Engineer – Steam (Reg. III/3) |
| 2nd Engineer – Steam (Reg. III/3) Endorsement | 2nd Engineer – Steam (Reg. III/3) Endorsement |
| 2nd Engineer <3,000 KW (Reg. III/3) | 2nd Engineer <3,000 KW (Reg. III/3) |
| Engineering Watch Officer (Reg. III/1) | Engineering Watch Officer (Reg. III/1) |
| Engineering Watch Officer (Reg. III/1) Endorsement | Engineering Watch Officer (Reg. III/1) Endorsement |
| Electro Technical Officer (Reg. III/6) | Electro Technical Officer (Reg. III/6) |
| Electro Technical Officer (Reg. III/6) Endorsement | Electro Technical Officer (Reg. III/6) Endorsement |
| Electro Technical Rating (Reg. III/7) | Electro Technical Rating (Reg. III/7) |
| Able Seaman Deck (Reg. II/5) | Able Seaman Deck (Reg. II/5) |
| Able Seaman Deck (Reg. II/5) Endorsement | Able Seaman Deck (Reg. II/5) Endorsement |
| Able Seaman Engine (Reg. III/5) | Able Seaman Engine (Reg. III/5) |
| Able Seaman Engine (Reg. III/5) Endorsement | Able Seaman Engine (Reg. III/5) Endorsement |
| Qualified Steward/Messman Endorsement | Qualified Steward/Messman Endorsement |
| GMDSS Radio Operator (Reg. IV/2) | GMDSS Radio Operator (Reg. IV/2) |
| GMDSS Radio Operator (Reg. IV/2) Endorsement | GMDSS Radio Operator (Reg. IV/2) Endorsement |
| GMDSS Endorsement (Reg. IV/2) Flag CRA | GMDSS Endorsement (Reg. IV/2) Flag CRA |
| GMDSS Restricted Operator (ROC) (Reg. IV/2) | GMDSS Restricted Operator (ROC) (Reg. IV/2) |
| GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement | GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement |
| GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA | GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA |
| Qualified Ship's Cook (MLC 2006) | Qualified Ship's Cook (MLC 2006) |
| Qualified Ship's Cook (MLC 2006) Endorsement | Qualified Ship's Cook (MLC 2006) Endorsement |
| Navigational Watch Rating (Reg. II/4) | Navigational Watch Rating (Reg. II/4) |
| Navigational Watch Rating (Reg. II/4) Endorsement | Navigational Watch Rating (Reg. II/4) Endorsement |
| COC – Certificate of Competency | COC – Certificate of Competency |
| COC – Certificate of Competency Endorsement | COC – Certificate of Competency Endorsement |
| GOC – General Operator Certificate | GOC – General Operator Certificate |
| GOC – General Operator Certificate Endorsement | GOC – General Operator Certificate Endorsement |

### Vaccination Names
| Value | Label |
|-------|-------|
| QUARANTINE LETTER | Quarantine Letter |
| RUBELLA IMMUNITY | Rubella Immunity |
| TESSERA SANITARIA | Tessera Sanitaria |
| TUBERCULOSIS_LAB_SCREEN | Tuberculosis Laboratory Screen |
| TYPHOID_VACCINATION | Typhoid Vaccination |
| VARICELLA_IMMUNIZATION | Varicella Immunization |
| YELLOW_FEVER_IMMUNIZATION | Yellow Fever Immunization |
| CHICKENPOX_IMMUNITY_SCREENING | Chickenpox Immunity Screening |
| COLOR_VISION_CERTIFICATE | Color Vision Certificate |
| COVID_SARS_VACCINATION | COVID-SARS Vaccination |
| COVID_FORM | COVID Form |
| FOODHANDLER_EXAMS | Foodhandler Exams |
| HEALTH_QUESTIONNAIRE | Health Questionnaire |
| HEPATITIS_A_IMMUNIZATION | Hepatitis A Immunization |
| HEPATITIS_B_IMMUNIZATION | Hepatitis B Immunization |
| ITALIAN_MEDICAL_PRE_EMBARK | Italian Medical Pre-Embark Examination |
| MEASLES_IMMUNITY | Measles Immunity |
| MEDICAL_CERT_SEAFARERS | Medical Certificate for Seafarers |
| MMR_BOOSTER_2 | MMR Booster 2 |
| MMR_VACC_IMMUNIZATION | MMR Vaccination / Immunization |
| MUMPS_IMMUNITY | Mumps Immunity |
| PERTUSSIS_IMMUNIZATION | Pertussis Immunization |

### Proficiency Levels (Languages)
| Value | Label |
|-------|-------|
| Elementary | Elementary |
| Intermediate | Intermediate |
| Advanced | Advanced |
| Native | Native |

### CEFR Levels (Languages)
| Value | Label |
|-------|-------|
| A1 | A1 |
| A2 | A2 |
| B1 | B1 |
| B2 | B2 |
| C1 | C1 |
| C2 | C2 |

### Company Types
| Value | Label |
|-------|-------|
| Shipping Manning Companies | Shipping Manning Companies |
| Cargo Manning Companies | Cargo Manning Companies |
| Cruise & Hospitality Manning Companies | Cruise & Hospitality Manning Companies |
| Offshore & Oil/Gas Manning Companies | Offshore & Oil/Gas Manning Companies |
| Fishing Fleet Manning Companies | Fishing Fleet Manning Companies |
| General Crew Manning Companies | General Crew Manning Companies |
| Specialized Marine Manning Companies | Specialized Marine Manning Companies |
| Temporary / Contract Manning Agencies | Temporary / Contract Manning Agencies |
| Full Crew Management Companies | Full Crew Management Companies |
| Other | Other |

### Company Status
| Value | Label |
|-------|-------|
| Active | Active |
| Inactive | Inactive |
| Prospect | Prospect |

### Ship Status
| Value | Label |
|-------|-------|
| Active | Active |
| Under Maintenance | Under Maintenance |
| Inactive | Inactive |

### Contract Status
| Value | Label |
|-------|-------|
| Pending | Pending |
| Active | Active |
| Completed | Completed |
| Cancelled | Cancelled |

### Contract Currency
| Value | Label |
|-------|-------|
| USD | US Dollar |
| EUR | Euro |
| GBP | British Pound |
| EGP | Egyptian Pound |

### Interview Type
| Value | Label |
|-------|-------|
| Phone | Phone |
| Video | Video |
| In-Person | In-Person |
| Technical | Technical |

### Interview Status
| Value | Label |
|-------|-------|
| Scheduled | Scheduled |
| Completed | Completed |
| Cancelled | Cancelled |
| Rescheduled | Rescheduled |
| No Show | No Show |

### Interview Result
| Value | Label |
|-------|-------|
| Pending | Pending |
| Passed | Passed |
| Failed | Failed |
| On Hold | On Hold |

### CV Submission Status
| Value | Label |
|-------|-------|
| Pending | Pending |
| Under Review | Under Review |
| Interviewed | Interviewed |
| Shortlisted | Shortlisted |
| Approved | Approved |
| Rejected | Rejected |
| Hired | Hired |

### Document Status
| Value | Label |
|-------|-------|
| Pending | Pending |
| Active | Active |
| Blacklist | Blacklist |

### Job Order Status
| Value | Label |
|-------|-------|
| Pending | Pending Review |
| Open | Open / Sourcing |
| In Progress | In Progress / Interviewing |
| Fulfilled | Fulfilled |
| Cancelled | Cancelled |
