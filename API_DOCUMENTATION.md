# Sakr Manning Agency API Documentation

**Version:** 1.0.0  
**Base URL:** `https://api.backend.hs.vc` (Production) / `http://localhost:8000` (Development)

## 📖 Overview

The Sakr Manning Agency API provides a comprehensive backend for managing maritime crew, ships, companies, and related logistics. It is built with Django REST Framework (DRF) and serves as the data layer for the frontend application.

The API supports:

- **User Management**: Crew members, admins, recruiters.
- **Ship Management**: Vessel details, crew assignments.
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

## 8. Core (Reference Data)

### Vessel Types

**GET** `/api/core/vessel-types/`  
**POST** `/api/core/vessel-types/`  
Body: `{"name": "Bulk Carrier"}`

### Flags (Countries)

**GET** `/api/core/flags/`  
**POST** `/api/core/flags/`  
Body: `{"name": "Panama", "icon": <file>}`

---

## 9. AI Agents & Documents

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

---

## 10. Appendix: Field Choices Reference

When submitting data to the API, specific fields require exact string matches from the lists below.

### 10.1 User & Profile

#### **Role** (`role`)
- `Admin`
- `HR Manager`
- `Recruiter`
- `Employee`

#### **User Status** (`user_status`)
- `VACATION`
- `ON_SITE`
- `MEDICAL VACATION`

#### **Marital Status** (`marital_status`)
- `SINGLE`
- `MARRIED`

### 10.2 Medical & Vaccinations

#### **Vaccine/Certificate Name** (`name`)
*Used in `/api/vaccinations/`*
- `QUARANTINE LETTER`
- `RUBELLA IMMUNITY`
- `TESSERA SANITARIA`
- `TUBERCULOSIS_LAB_SCREEN`
- `TYPHOID_VACCINATION`
- `VARICELLA_IMMUNIZATION`
- `YELLOW_FEVER_IMMUNIZATION`
- `CHICKENPOX_IMMUNITY_SCREENING`
- `COLOR_VISION_CERTIFICATE`
- `COVID_SARS_VACCINATION`
- `COVID_FORM`
- `FOODHANDLER_EXAMS`
- `HEALTH_QUESTIONNAIRE`
- `HEPATITIS_A_IMMUNIZATION`
- `HEPATITIS_B_IMMUNIZATION`
- `ITALIAN_MEDICAL_PRE_EMBARK`
- `MEASLES_IMMUNITY`
- `MEDICAL_CERT_SEAFARERS`
- `MMR_BOOSTER_2`
- `MMR_VACC_IMMUNIZATION`
- `MUMPS_IMMUNITY`
- `PERTUSSIS_IMMUNIZATION`

### 10.3 Compliance

#### **Audit Type** (`audit_type`)
- `MLC` (MLC 2006)
- `ISO` (ISO 9001)
- `PSC` (Port State Control)
- `Internal` (Internal Audit)
- `Client` (Client Audit)

#### **Incident Type** (`incident_type`)
- `Accident` (Accident / Injury)
- `Near Miss`
- `Grievance` (Crew Grievance / Complaint)
- `Disciplinary` (Disciplinary Action)
- `Pollution` (Pollution / Environmental)
- `Security` (Security Breach)

#### **Severity** (`severity`)
- `Low`
- `Medium`
- `High`
- `Critical`

### 10.4 Documents

#### **Document Position/Rank** (`position`)
*Used in `/api/documents/`*
- `Master`
- `1st. Officer – Chief Off.`
- `2nd. Officer`
- `3rd. Officer`
- `Tug Master`
- `Boson`
- `A.B – O.S`
- `Steward / Galley Boy`
- `Cook / 2nd. Cook / Ass. Cook / Baker / Pastry`
- `Carpenter`
- `Waiter`
- `Purser`
- `Doctor`
- `1st. Engineer`
- `2nd. Engineer`
- `3rd. Engineer`
- `Electrical Engineer – E/E – ETO`
- `Assistant Electrician`
- `4th. Engineer`
- `Electrician`
- `Motor Man / Mechanic`
- `Oiler`
- `Fitter – Welder`
- `Wiper`
- `Other`

#### **Personal Document Type** (`document_type`)
*Used in `/api/personal-documents/`*
- `BAHAMAS SEAMAN'S BOOK`
- `BELIZE SEAMAN'S BOOK`
- `BERMUDA SEAMAN'S BOOK`
- `EU national ID`
- `Exit Interview`
- `LIBERIAN SEAMAN'S BOOK`
- `Local ID Card`
- `LUXEMBOURG SEAMAN'S BOOK`
- `PALAU SEAMAN'S BOOK`
- `PANAMA SEAMAN'S BOOK`
- `Passport`
- `PERMESSO SOGGIORNO PERMANENTE`
- `PERMESSO SOGGIORNO TEMPORANEO`
- `Personal Record Sheet`
- `RESIDENCE CERTIFICATE`
- `SEAFARERS' ID. DOC. ILO 185`
- `Seaman's Book`
- `Seaman's Book/Card or ID`
- `U.K. SEAMAN'S BOOK`

### 10.5 Language Proficiency

#### **Language** (`language`)
*Used in `/api/my-languages/`*
- `English`
- `Spanish`
- `French`
- `German`
- `Italian`
- `Portuguese`
- `Dutch`
- `Russian`
- `Chinese (Mandarin)`
- `Japanese`
- `Korean`
- `Arabic`
- `Hindi`
- `Greek`
- `Polish`
- `Turkish`
- `Swedish`
- `Norwegian`
- `Danish`
- `Finnish`
- `Czech`
- `Romanian`
- `Ukrainian`
- `Thai`
- `Vietnamese`
- `Indonesian`
- `Malay`
- `Tagalog`
- `Other`

#### **Speaking/Writing/Reading Levels**
*Used in `/api/user-languages/`*
- `Elementary`
- `Intermediate`
- `Advanced`
- `Native`

#### **CEFR Levels**
- `A1` (Beginner)
- `A2` (Elementary)
- `B1` (Intermediate)
- `B2` (Upper Intermediate)
- `C1` (Advanced)
- `C2` (Proficient)

### 10.6 Contracts & Finance

#### **Contract Status**
- `Active`
- `Completed`
- `Pending`
- `Signed`
- `Pending Signature`
- `Draft`
- `Cancelled`

#### **Currency**
- `USD`
- `EUR`
- `GBP`
- `EGP`

### 10.7 Licenses

#### **Document Name** (`document_name`)
*Used in `/api/my-licenses/`*
- `Master (Reg. II/2 Par. 1-2)`
- `Master (Reg. II/2 Par. 1-2) Endorsement`
- `Master <3,000 GRT (Reg. II/2 Par. 3-4)`
- `Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement`
- `Master <500 GRT (Reg. II/3 Par. 5-6)`
- `Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement`
- `Yachtmaster Coastal`
- `Chief Officer (Reg. II/2 Par. 1-2)`
- `Chief Officer (Reg. II/2 Par. 1-2) Endorsement`
- `Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4)`
- `Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement`
- `Navigational Watch Officer (Reg. II/1)`
- `Navigational Watch Officer (Reg. II/1) Endorsement`
- `Navigational Watch Officer <500 GRT (II/3 Par. 3-4)`
- `Chief Engineer (Reg. III/2)`
- `Chief Engineer (Reg. III/2) Endorsement`
- `Chief Engineer – Steam (Reg. III/2)`
- `Chief Engineer – Steam (Reg. III/2) Endorsement`
- `Chief Engineer <3,000 KW (Reg. III/3)`
- `2nd Engineer (Reg. III/2)`
- `2nd Engineer (Reg. III/2) Endorsement`
- `2nd Engineer – Steam (Reg. III/3)`
- `2nd Engineer – Steam (Reg. III/3) Endorsement`
- `2nd Engineer <3,000 KW (Reg. III/3)`
- `Engineering Watch Officer (Reg. III/1)`
- `Engineering Watch Officer (Reg. III/1) Endorsement`
- `Electro Technical Officer (Reg. III/6)`
- `Electro Technical Officer (Reg. III/6) Endorsement`
- `Electro Technical Rating (Reg. III/7)`
- `Able Seaman Deck (Reg. II/5)`
- `Able Seaman Deck (Reg. II/5) Endorsement`
- `Able Seaman Engine (Reg. III/5)`
- `Able Seaman Engine (Reg. III/5) Endorsement`
- `Qualified Steward/Messman Endorsement`
- `GMDSS Radio Operator (Reg. IV/2)`
- `GMDSS Radio Operator (Reg. IV/2) Endorsement`
- `GMDSS Endorsement (Reg. IV/2) Flag CRA`
- `GMDSS Restricted Operator (ROC) (Reg. IV/2)`
- `GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement`
- `GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA`
- `Qualified Ship’s Cook (MLC 2006)`
- `Qualified Ship’s Cook (MLC 2006) Endorsement`
- `Navigational Watch Rating (Reg. II/4)`
- `Navigational Watch Rating (Reg. II/4) Endorsement`

### 10.8 Companies, Ships & Finance

#### **Company Type** (`company_type`)
*Used in `/api/companies/`*
- `Shipping Manning Companies`
- `Cargo Manning Companies`
- `Cruise & Hospitality Manning Companies`
- `Offshore & Oil/Gas Manning Companies`
- `Fishing Fleet Manning Companies`
- `General Crew Manning Companies`
- `Specialized Marine Manning Companies`
- `Temporary / Contract Manning Agencies`
- `Full Crew Management Companies`
- `Other`

#### **Company Status** (`status`)
- `Active`
- `Inactive`
- `Prospect`

#### **Job Order Status** (`status`)
*Used in `/api/companies/job-orders/`* (if applicable)
- `Pending` (Pending Review)
- `Open` (Open / Sourcing)
- `In Progress` (In Progress / Interviewing)
- `Fulfilled`
- `Cancelled`

#### **Ship Status** (`status`)
*Used in `/api/ships/`*
- `Active`
- `Under Maintenance`
- `Inactive`

#### **Finance Record Status** (`status`)
*Used in `/api/finance/`*
- `Pending`
- `Paid`
- `Overdue`
- `Cancelled`

