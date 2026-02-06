# Sakr Manning Agency API Documentation

**Version:** 1.0.0  
**Base URL:** `https://api.backend.hs.vc` (Production) / `http://localhost:8000` (Development)

## 📖 Overview

The Sakr Manning Agency API provides a comprehensive backend for managing maritime crew, ships, companies, and related logistics. It is built with Django REST Framework (DRF) and serves as the data layer for the frontend application.

The API supports:

- **User Management**: Crew members, admins, recruiters.
- **Ship Management**: Vessel details, crew assignments.
- **Certificate Management**: Track individual certificates and marine courses with detailed instances.
- **Logistics**: Tickets, traveling papers, visas.
- **Finance**: Payroll, daily rates, contracts.
- **Recruitment**: Interviews, AI-powered candidate search.
- **AI Integration**: Document parsing and intelligent chatbots.

---

## 🔐 Authentication

The API uses **JWT (JSON Web Token)** authentication.

### Headers

All authenticated requests must include the `Authorization` header:

```http
Authorization: Bearer <your_access_token>
```

### Flow

1. **Login** with username/password to get `access` and `refresh` tokens.
2. Use `access` token for API requests (valid for ~15 days).
3. When `access` token expires, use `refresh` token to get a new pair.

---

## 📡 Request & Response Structure

### Standard Success Response

Most endpoints return JSON objects or arrays.

```json
{
  "id": 1,
  "name": "Object Name",
  "created_at": "2023-10-27T10:00:00Z"
}
```

### Standard Error Response

Errors are returned with appropriate HTTP status codes and a detailed JSON body.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Validation Errors (400 Bad Request):**

```json
{
  "email": ["Enter a valid email address."],
  "password": ["This field is required."]
}
```

---

## 🚦 Status Codes

| Code | Meaning | Description |
| :--- | :--- | :--- |
| `200` | **OK** | Request successful. |
| `201` | **Created** | Resource successfully created. |
| `204` | **No Content** | Request successful, no content returned (e.g., DELETE). |
| `400` | **Bad Request** | Validation error or malformed request. |
| `401` | **Unauthorized** | Authentication failed or token missing. |
| `403` | **Forbidden** | User authenticated but lacks permission. |
| `404` | **Not Found** | Resource does not exist. |
| `500` | **Internal Server Error** | Server-side error. |

---

# 📚 Endpoints

## 1. Authentication

### Login (Obtain Token)

**POST** `/api/login/`

Authenticate a user and retrieve access/refresh tokens.

**Request Body:**

```json
{
  "email": "admin@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Code Example

```bash
curl -X POST https://api.backend.hs.vc/api/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "pass"}'
```

### Refresh Token

**POST** `/api/login/refresh/`

Get a new access token using a valid refresh token.

**Request Body:**

```json
{
  "refresh": "your_refresh_token_here"
}
```

---

## 2. Users (Crew & Staff)

### List All Users

**GET** `/api/users/`

Retrieve a paginated list of all users.

**Query Parameters:**

- `page`: Page number (default: 1)
- `search`: Search by name or email
- `role`: Filter by role (Admin, Recruiter, Employee)

**Response (200 OK):**

```json
{
  "count": 102,
  "next": "https://api.backend.hs.vc/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "crew@sakr.com",
      "first_name": "Ahmed",
      "last_name": "Ali",
      "role": "Employee",
      "nationality": "Egyptian",
      "rank": "Captain"
    }
  ]
}
```

### Create User

**POST** `/api/users/`

Create a new user profile.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "New",
  "last_name": "User",
  "role": "Employee",
  "nationality": "Filipino",
  "date_of_birth": "1990-01-01"
}
```

### Get User Details

**GET** `/api/users/{id}/`

Retrieve detailed profile for a specific user.

---

## 3. Ships (Vessels)

### List Ships

**GET** `/api/ships/`

Retrieve all ships in the fleet.

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "ship_name": "MV Pacific Queen",
    "imo_number": "IMO7654321",
    "status": "Active",
    "company": 2,
    "crew": [...] 
  }
]
```

### Create Ship

**POST** `/api/ships/`

Add a new vessel to the system. Requires Admin or Ship Manager privileges.

**Request Body:**

```json
{
  "ship_name": "MV Atlantic Star",
  "imo_number": "IMO9876543",
  "company": 1,
  "ship_type": 1,
  "flag": 2,
  "official_no": "OFF99999",
  "crew_ids": [10, 25, 33],
  "engine_type": "MAN B&W"
}
```

**Response (201 Created):**

```json
{
  "id": 5,
  "ship_name": "MV Atlantic Star",
  "crew": [ ...list of crew objects... ]
}
```

**Error (403 Forbidden):**
Returned if user is not an Admin/Superuser.

---

## 4. Companies

### List Companies

**GET** `/api/companies/`

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "company_name": "Maersk Line",
    "company_type": "Shipping Manning Companies",
    "status": "Active",
    "hourly_rate": "550.00",
    "open_positions": 5
  }
]
```

### Create Company

**POST** `/api/companies/`

Create a new company.

**Request Body:**

```json
{
  "company_name": "Oceanic Transport",
  "company_type": "Shipping Manning Companies",
  "contact_email": "contact@oceanic.com",
  "status": "Active",
  "open_positions": 5,
  "hourly_rate": "150.00"
}
```

**Valid `company_type` Choices:**

- Shipping Manning Companies
- Cargo Manning Companies
- Cruise & Hospitality Manning Companies
- Offshore & Oil/Gas Manning Companies
- Fishing Fleet Manning Companies
- General Crew Manning Companies
- Specialized Marine Manning Companies
- Temporary / Contract Manning Agencies
- Full Crew Management Companies
- Other

**For Frontend (JSON Array):**

```json
[
  "Shipping Manning Companies",
  "Cargo Manning Companies",
  "Cruise & Hospitality Manning Companies",
  "Offshore & Oil/Gas Manning Companies",
  "Fishing Fleet Manning Companies",
  "General Crew Manning Companies",
  "Specialized Marine Manning Companies",
  "Temporary / Contract Manning Agencies",
  "Full Crew Management Companies",
  "Other"
]
```

**Response (201 Created):**

```json
{
  "id": 2,
  "company_name": "Oceanic Transport",
  "company_type": "Shipping Manning Companies",
  "status": "Active",
  "created_at": "2024-03-15T10:00:00Z"
}
```

### Get Company Stats

**GET** `/api/companies/stats/`

Returns aggregated statistics about companies.

**Response (200 OK):**

```json
{
  "total_companies": 15,
  "active_companies": 12,
  "hiring_companies": 5
}
```

---

## 5. Logistics (Tickets & Papers)

### List Tickets

**GET** `/api/tickets-papers/tickets/`

Retrieve all travel tickets.

### Upload Ticket

**POST** `/api/tickets-papers/tickets/`

**Request Body (Multipart Form-Data):**

- `user`: User ID (integer)
- `ticket_number`: String
- `file`: File upload (PDF/Image)

### List Traveling Papers

**GET** `/api/tickets-papers/traveling-papers/`

Retrieve visas, seaman books, and other travel docs.

---

## 6. Finance

### List Finance Records

**GET** `/api/finance/finance-records/`

Retrieve payroll records details.

### Create Finance Record

**POST** `/api/finance/finance-records/`

**Request Body:**

```json
{
  "user": 5,
  "company": 2,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "status": "Paid"
}
```

**Response (201 Created):**

```json
{
  "id": 101,
  "user": 5,
  "total_days": 31,
  "daily_rate": 200.0,
  "total_money": 6200.0
}
```

---

## 7. Interviews

### List Interviews

**GET** `/api/interviews/`

### Schedule Interview

**POST** `/api/interviews/`

**Request Body:**

```json
{
  "candidate": 5,
  "interviewer": 1,
  "date": "2024-02-15T10:00:00Z",
  "status": "Scheduled",
  "link": "https://meet.google.com/abc-defg-hij"
}
```

### Get Interview Status Stats

**GET** `/api/interviews/status/`

Returns counts of interviews by status.

**Response (200 OK):**

```json
{
  "scheduled": 5,
  "completed": 20,
  "pending": 2
}
```

---

## 8. Certificate Instance Management

The Certificate Instance Management API allows users to track individual certificates and marine courses with detailed information including document numbers, issue/expiry dates, issuer information, and file uploads.

### Overview

**Two-Level System:**
1. **Certificate Types** (`/api/users/certificates/`) - Predefined certificate types (44 options)
2. **Certificate Instances** (`/api/users/user-certificates/`) - Individual user certificates with details

### List User Certificates

**GET** `/api/users/user-certificates/`

Retrieve certificate instances based on user role and permissions.

**Query Parameters:**
- `category`: Filter by "Certificate" or "Course"
- `user_id`: Filter by specific user (Admin/HR/Recruiter only)

**Role-Based Access:**
- **Admin/HR Manager**: View all certificates
- **Recruiter**: View all certificates (read-only)
- **Employee**: View only their own certificates

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user": 5,
    "certificate_type": 12,
    "certificate_type_name": "GMDSS",
    "certificate_type_code": "GMDSS",
    "document_name": "G.M.D.S.S",
    "document_number": "GMDSS-2024-00456",
    "country_of_issue": "Panama",
    "issue_date": "2024-01-15",
    "expiry_date": "2029-01-15",
    "issued_by": "Panama Maritime Authority",
    "issued_at": "Panama City",
    "certificate_file": "/media/certificates/cert_456.pdf",
    "category": "Certificate",
    "rank": null,
    "rank_name": null,
    "is_expired": false,
    "created_at": "2026-02-06T19:05:00Z",
    "updated_at": "2026-02-06T19:05:00Z"
  }
]
```

### Create Certificate Instance

**POST** `/api/users/user-certificates/`

Add a new certificate instance for a user.

**Permissions:**
- **Employee**: Can only create for themselves (user field auto-set)
- **Admin/HR Manager**: Can create for any user

**Request Body:**

```json
{
  "user": 5,
  "certificate_type": 12,
  "document_name": "STCW Basic Safety Training",
  "document_number": "STCW-2024-00123",
  "country_of_issue": "Panama",
  "issue_date": "2024-01-15",
  "expiry_date": "2029-01-15",
  "issued_by": "Panama Maritime Authority",
  "issued_at": "Panama City",
  "category": "Certificate",
  "certificate_file": "<file upload>"
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "user": 5,
  "certificate_type": 12,
  "certificate_type_name": "STCW Basic Safety",
  "document_number": "STCW-2024-00123",
  "is_expired": false,
  "created_at": "2026-02-06T19:10:00Z"
}
```

### Update Certificate Instance

**PUT** `/api/users/user-certificates/{id}/`  
**PATCH** `/api/users/user-certificates/{id}/`

Update certificate details.

**Permissions:**
- **Employee**: Can only update their own certificates
- **Admin/HR Manager**: Can update any certificate
- **Recruiter**: Cannot update (read-only)

**Request Body (PATCH example):**

```json
{
  "document_number": "STCW-2024-00124",
  "expiry_date": "2030-01-15"
}
```

### Delete Certificate Instance

**DELETE** `/api/users/user-certificates/{id}/`

Delete a certificate instance.

**Permissions:**
- **Admin/HR Manager only**

**Response (204 No Content)**

### Get Certificate Statistics

**GET** `/api/users/user-certificates/stats/`

Returns certificate statistics based on user's access level.

**Response (200 OK):**

```json
{
  "total_certificates": 45,
  "certificates": 32,
  "courses": 13,
  "expired": 3,
  "expiring_soon": 7
}
```

### Filtering Examples

**Get only certificates (not courses):**
```
GET /api/users/user-certificates/?category=Certificate
```

**Get only marine courses:**
```
GET /api/users/user-certificates/?category=Course
```

**Get certificates for specific user (Admin/HR/Recruiter only):**
```
GET /api/users/user-certificates/?user_id=123
```

### List Certificate Types

**GET** `/api/users/certificates/`

Retrieve all available certificate types that users can select from.

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "code": "PERSONAL_SURVIVAL_TECHNIQUES",
    "name": "Personal Survival Techniques"
  },
  {
    "id": 2,
    "code": "GMDSS",
    "name": "G.M.D.S.S"
  }
]
```

**Note:** There are 44 predefined certificate types available.

---

## 9. Sea Service \u0026 References

### Sea Service Records

Sea service records track a crew member's employment history on vessels. This information is critical for compliance, CV generation, and experience verification.

#### List Sea Services

**GET** `/api/users/sea-services/`

Retrieve all sea service records.

**Permissions:**
- **Admin/HR Manager**: View all records
- **Recruiter**: View all records (read-only)
- **Employee**: View only their own records

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user": 5,
    "company_name": "Maersk Line",
    "rank": "3rd Officer",
    "vessel_name_imo": "MV Nordic Star / IMO9876543",
    "flag": "Panama",
    "signed_on": "2022-01-15",
    "signed_off": "2022-07-15",
    "period": "6 months",
    "vessel_type": "Container Ship",
    "dwt_grt": "50,000 DWT",
    "engine_type_bh_kw": "MAN B&W 12,000 BHP",
    "reason_for_sign_off": "End of contract"
  }
]
```

#### Create Sea Service Record

**POST** `/api/users/sea-services/`

Add a new sea service record for a crew member.

**Permissions:**
- **Admin/HR Manager**: Can create for any user
- **Employee**: Can create for themselves

**Request Body:**

```json
{
  "user": 5,
  "company_name": "Pacific Shipping Ltd",
  "rank": "2nd Officer",
  "vessel_name_imo": "MV Ocean Queen / IMO1234567",
  "flag": "Liberia",
  "signed_on": "2023-01-20",
  "signed_off": "2023-08-20",
  "period": "7 months",
  "vessel_type": "Bulk Carrier",
  "dwt_grt": "75,000 DWT",
  "engine_type_bh_kw": "Wartsila 15,000 BHP",
  "reason_for_sign_off": "Promotion"
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "user": 5,
  "company_name": "Pacific Shipping Ltd",
  "rank": "2nd Officer",
  "vessel_name_imo": "MV Ocean Queen / IMO1234567",
  "signed_on": "2023-01-20",
  "signed_off": "2023-08-20",
  "period": "7 months"
}
```

#### Update Sea Service Record

**PUT** `/api/users/sea-services/{id}/`  
**PATCH** `/api/users/sea-services/{id}/`

Update sea service details.

**Permissions:**
- **Admin/HR Manager**: Can update any record
- **Employee**: Can update their own records
- **Recruiter**: Read-only access

#### Delete Sea Service Record

**DELETE** `/api/users/sea-services/{id}/`

**Permissions:**
- **Admin/HR Manager**: Can delete any record

**Response (204 No Content)**

---

### References

Professional references from previous employers or supervisors.

#### List References

**GET** `/api/users/references/`

Retrieve all reference records.

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user": 5,
    "number": "01200",
    "name": "Captain John Smith",
    "company_name": "Maersk Line",
    "management": "Deck Department",
    "country": "Egypt",
    "position": "Master",
    "email": "john.smith@maersk.com",
    "tel": "+45-1234-5678"
  }
]
```

#### Create Reference

**POST** `/api/users/references/`

Add a new professional reference.

**Request Body:**

```json
{
  "user": 5,
  "number": "0120000",
  "name": "Captain Sarah Johnson",
  "company_name": "MSC Cruises",
  "management": "Bridge Team",
  "country": "Egypt",
  "position": "Chief Officer",
  "email": "sarah.johnson@msc.com",
  "tel": "+41-22-123-4567"
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "user": 5,
  "number": "0120000",
  "name": "Captain Sarah Johnson",
  "company_name": "MSC Cruises",
  "management": "Bridge Team",
  "country": "Egypt",
  "position": "Chief Officer",
  "email": "sarah.johnson@msc.com",
  "tel": "+41-22-123-4567"
}
```

#### Update Reference

**PUT** `/api/users/references/{id}/`  
**PATCH** `/api/users/references/{id}/`

Update reference details.

**Request Body (PATCH example):**

```json
{
  "tel": "+41-22-987-6543",
  "email": "sarah.j@msc.com",
  "country": "Switzerland"
}
```


#### Delete Reference

**DELETE** `/api/users/references/{id}/`

Remove a reference record.

**Response (204 No Content)**


---

## 10. Health Declarations

Health declarations capture medical history and consent information required for seafarers.

### List Declarations

**GET** `/api/declarations/`

Retrieve all health declarations based on user permissions.

**Permissions:**
- **Admin/HR Manager**: View all declarations
- **Recruiter**: View all declarations (read-only)
- **Employee**: View only their own declarations

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user": 5,
    "user_name": "Ahmed Ali Mohamed",
    "user_email": "ahmed.ali@example.com",
    "has_disease": false,
    "disease_details": "",
    "has_accident": false,
    "accident_details": "",
    "has_psychiatric_treatment": false,
    "psychiatric_treatment_details": "",
    "has_addiction": false,
    "addiction_details": "",
    "consent_given": true,
    "declaration_place": "Cairo",
    "declaration_date": "2026-02-06",
    "signature": "Ahmed Ali",
    "created_at": "2026-02-06T19:30:00Z",
    "updated_at": "2026-02-06T19:30:00Z"
  }
]
```

### Create Declaration

**POST** `/api/declarations/`

Create a new health declaration.

**Permissions:**
- **Admin/HR Manager**: Can create for any user
- **Employee**: Can create for themselves

**Request Body:**

```json
{
  "user": 5,
  "has_disease": false,
  "disease_details": "",
  "has_accident": true,
  "accident_details": "Minor ankle sprain in 2022, fully recovered",
  "has_psychiatric_treatment": false,
  "psychiatric_treatment_details": "",
  "has_addiction": false,
  "addiction_details": "",
  "consent_given": true,
  "declaration_place": "Cairo",
  "declaration_date": "2026-02-06",
  "signature": "Ahmed Ali"
}
```

**Field Descriptions:**
- `has_disease` (boolean): YES/NO - Did you suffer any disease that might render you unfit for sea service?
- `disease_details` (string, optional): Details if `has_disease` is true
- `has_accident` (boolean): YES/NO - Did you suffer any accident causing disability?
- `accident_details` (string, optional): Details if `has_accident` is true
- `has_psychiatric_treatment` (boolean): YES/NO - Did you undergo psychiatric treatment?
- `psychiatric_treatment_details` (string, optional): Details if `has_psychiatric_treatment` is true
- `has_addiction` (boolean): YES/NO - Are you addicted to alcohol or drugs?
- `addiction_details` (string, optional): Details if `has_addiction` is true
- `consent_given` (boolean): Whether user consents to data processing
- `declaration_place` (string): Location where declaration was signed
- `declaration_date` (date): Date of declaration
- `signature` (string, optional): Signature or name

**Note:** For Employee role, the `user` field is automatically set to the authenticated user and can be omitted.

**Response (201 Created):**

```json
{
  "id": 1,
  "user": 5,
  "user_name": "Ahmed Ali Mohamed",
  "user_email": "ahmed.ali@example.com",
  "has_disease": false,
  "disease_details": "",
  "has_accident": true,
  "accident_details": "Minor ankle sprain in 2022, fully recovered",
  "has_psychiatric_treatment": false,
  "psychiatric_treatment_details": "",
  "has_addiction": false,
  "addiction_details": "",
  "consent_given": true,
  "declaration_place": "Cairo",
  "declaration_date": "2026-02-06",
  "signature": "Ahmed Ali",
  "created_at": "2026-02-06T19:30:00Z",
  "updated_at": "2026-02-06T19:30:00Z"
}
```

### Get Declaration Details

**GET** `/api/declarations/{id}/`

Retrieve detailed information for a specific declaration.

**Permissions:**
- **Admin/HR Manager/Recruiter**: Can view any declaration
- **Employee**: Can only view their own declarations

**Response (200 OK):**

```json
{
  "id": 1,
  "user": 5,
  "user_name": "Ahmed Ali Mohamed",
  "user_email": "ahmed.ali@example.com",
  "has_disease": false,
  "disease_details": "",
  "has_accident": true,
  "accident_details": "Minor ankle sprain in 2022, fully recovered",
  "has_psychiatric_treatment": false,
  "psychiatric_treatment_details": "",
  "has_addiction": false,
  "addiction_details": "",
  "consent_given": true,
  "declaration_place": "Cairo",
  "declaration_date": "2026-02-06",
  "signature": "Ahmed Ali",
  "created_at": "2026-02-06T19:30:00Z",
  "updated_at": "2026-02-06T19:30:00Z"
}
```

### Update Declaration

**PUT** `/api/declarations/{id}/`  
**PATCH** `/api/declarations/{id}/`

Update declaration details.

**Permissions:**
- **Admin/HR Manager**: Can update any declaration
- **Employee**: Can update their own declarations
- **Recruiter**: Cannot update (read-only)

**Request Body (PATCH example):**

```json
{
  "has_disease": true,
  "disease_details": "Updated: Minor asthma, well-controlled with medication",
  "consent_given": true
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "user": 5,
  "user_name": "Ahmed Ali Mohamed",
  "user_email": "ahmed.ali@example.com",
  "has_disease": true,
  "disease_details": "Updated: Minor asthma, well-controlled with medication",
  "has_accident": true,
  "accident_details": "Minor ankle sprain in 2022, fully recovered",
  "has_psychiatric_treatment": false,
  "psychiatric_treatment_details": "",
  "has_addiction": false,
  "addiction_details": "",
  "consent_given": true,
  "declaration_place": "Cairo",
  "declaration_date": "2026-02-06",
  "signature": "Ahmed Ali",
  "created_at": "2026-02-06T19:30:00Z",
  "updated_at": "2026-02-06T20:15:00Z"
}
```

### Delete Declaration

**DELETE** `/api/declarations/{id}/`

Delete a health declaration.

**Permissions:**
- **Admin/HR Manager only**: Can delete declarations

**Response (204 No Content)**

---

## 11. Core (Reference Data)



### Vessel Types

**GET** `/api/core/vessel-types/`  
**POST** `/api/core/vessel-types/`  
Body: `{"name": "Bulk Carrier"}`

### Flags (Countries)

**GET** `/api/core/flags/`  
**POST** `/api/core/flags/`  
Body: `{"name": "Panama", "icon": <file>}`

---

## 11. AI Agents & Documents

### Document Upload (Parsed)

**POST** `/ai/upload/`
Upload a document (CV, Passport) for AI parsing.

**Request Body:**

- `file`: PDF/Image
- `document_type`: "Passport", "CV", etc.

### Chat with AI

**POST** `/ai-agents/chat/`

Search database or chat using natural language.

**Request Body:**

```json
{
  "query": "Find me a Captain with 5 years experience on Tankers",
  "session_id": "optional-uuid"
}
```

---

## 💻 Developer Examples

### Python (requests)

```python
import requests

url = "https://api.backend.hs.vc/api/ships/"
token = "your_access_token"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "ship_name": "MV Python",
    "imo_number": "IMO1234567",
    "company": 1
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### JavaScript (fetch)

```javascript
const createShip = async () => {
  const response = await fetch('https://api.backend.hs.vc/api/ships/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + localStorage.getItem('token'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      ship_name: 'MV JS',
      imo_number: 'IMO9999999',
      company: 1
    })
  });
  
  const data = await response.json();
  console.log(data);
};
```
