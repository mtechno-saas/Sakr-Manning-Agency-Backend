# Sakr Manning Agency - Complete API Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [API Endpoints](#api-endpoints)

---

## Introduction

This documentation provides comprehensive information about the Sakr Manning Agency Backend API, including:

- Complete data model specifications
- Detailed request and response formats
- Error handling patterns
- Real-world examples for all endpoints

**Base URL**: `http://your-domain.com`  
**API Version**: 1.0  
**Authentication**: JWT (JSON Web Tokens)

---

## Authentication

### JWT Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### 1. **Login (Obtain JWT Token)**

**Endpoint**: `POST /api/login/`  
**Permission**: AllowAny

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Success Response** (200 OK):

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses**:

```json
// 401 Unauthorized
{
  "detail": "No active account found with the given credentials"
}

// 400 Bad Request
{
  "email": ["This field is required."],
  "password": ["This field is required."]
}
```

---

#### 2. **Refresh JWT Token**

**Endpoint**: `POST /api/login/refresh/`  
**Permission**: AllowAny

**Request Body**:

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (200 OK):

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### 3. **User Registration**

**Endpoint**: `POST /api/register/`  
**Permission**: AllowAny

**Request Body**:

```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123",
  "first_name": "John",
  "middle_name": "Michael",
  "phone_number": "+201234567890",
  "nationality": "Egyptian"
}
```

**Success Response** (201 Created):

```json
{
  "id": 15,
  "email": "newuser@example.com",
  "first_name": "John",
  "middle_name": "Michael",
  "phone_number": "+201234567890",
  "nationality": "Egyptian",
  "role": "Employee",
  "is_active": true
}
```

---

## Data Models

### Users Model

Complete user model with all fields:

```python
{
  "id": integer,
  "email": string (unique, required),
  "first_name": string (required),
  "middle_name": string,
  "profile_image": file (image),
  
  # Personal Information
  "age": integer,
  "blood_type": string,
  "smoker": boolean,
  "us_visa_status": string,
  "schengen_visa_status": string,
  "date_of_birth": date (YYYY-MM-DD),
  "marital_status": string (choices: "Single", "Married"),
  "user_status": string (choices: "On Site", "Vacation", "Medical Vacation"),
  "nationality": string,
  "Place_Of_Birth": string,
  "Nearest_Port": string,
  "Height_Cm": integer,
  "Weight_Kg": integer,
  
  # Contact
  "address": string,
  "phone_number": string (required),
  "tel_number": string,
  
  # Passport
  "passport_no": string,
  "passport_issue_date": date,
  "passport_expiry_date": date,
  "passport_issued_by": string,
  "passport_place_of_issue": string,
  
  # Seaman Books
  "seaman_book_no": string,
  "seaman_book_issue_date": date,
  "seaman_book_expiry_date": date,
  "seaman_book_issued_by": string,
  "seaman_book_place_of_issue": string,
  
  # Certificates of Competency (COC)
  "coc_certificate_name": string,
  "coc_certificate_number": string,
  "coc_issue_date": date,
  "coc_expiry_date": date,
  "coc_issued_by": string (default: "EAMS"),
  "coc_issued_at": string (default: "Alex."),
  
  # Health Information
  "health_flag_state": string,
  "health_number": string,
  "health_issue_date": date,
  "health_expiry_date": date,
  
  # COVID-19 Vaccination
  "covid_vaccine_name": string,
  "covid_first_dose": date,
  "covid_second_dose": date,
  "covid_other_doses_or_remarks": text,
  
  # Sizes
  "overall_size": string,
  "shirt_size": string,
  "trouser_size": string,
  "shoes_size": string,
  
  # Languages
  "english_language_level": string,
  "other_language": string,
  "other_language_level": string,
  
  # Medical History
  "disease_history": text,
  "accident_history": text,
  "psychiatric_treatment_history": text,
  "addiction_history": text,
  
  # Employment
  "salary": decimal,
  "role": string (choices: "Admin", "HR Manager", "Recruiter", "Employee"),
  
  # Relationships
  "certificates": array of Certificate IDs,
  "codes": array of Rank IDs,
  "user_ranks": array of UserRank objects,
  "references": array of Reference objects,
  "sea_services": array of SeaService objects,
  
  # Timestamps
  "created_at": datetime,
  "updated_at": datetime,
  "is_active": boolean,
  "is_staff": boolean
}
```

### Ship Model

```python
{
  "id": integer,
  "ship_name": string (required, max 200),
  "imo_number": string (unique, max 10),
  "company": integer (Company ID, required),
  "ship_type": integer (VesselType ID, nullable),
  "flag": integer (Flag ID, nullable),
  "official_no": string,
  "call_sign": string,
  "mmsi_no": string,
  "port_of_registry": string,
  "gross_tonnage": integer,
  "deadweight": integer,
  "year_built": integer,
  "builder": string,
  "engine_type": string,
  "engine_power_kw": integer,
  "status": string (choices: "Active", "Under Maintenance", "Inactive"),
  "crew": array of User IDs (many-to-many),
  "created_at": datetime,
  "updated_at": datetime
}
```

### Company Model

```python
{
  "id": integer,
  "name": string (required, max 255),
  "company_type": string (choices: "Ship Owner", "Ship Manager", "Crewing Agency", "Training Center", "Other"),
  "email": email,
  "phone": string,
  "address": text,
  "country": string,
  "website": url,
  "contact_person": string,
  "contact_person_email": email,
  "contact_person_phone": string,
  "notes": text,
  "open_positions": integer (default: 0),
  "status": string (choices: "Active", "Inactive", "Prospect"),
  "created_at": datetime,
  "updated_at": datetime
}
```

### Contract Model

```python
{
  "id": integer,
  "user": integer (User ID, required),
  "ship": integer (Ship ID, required),
  "company": integer (Company ID, nullable),
  "rank": integer (Rank ID, nullable),
  "sign_on_date": date (required),
  "sign_off_date": date,
  "salary": decimal,
  "currency": string (choices: "USD", "EUR", "GBP", "EGP"),
  "status": string (choices: "Active", "Completed", "Pending", "Signed", "Pending Signature", "Draft", "Cancelled"),
  "signed_file": file,
  "signed_at": datetime,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Interview Model

```python
{
  "id": integer,
  "candidate": integer (User ID, required),
  "company": integer (Company ID, nullable),
  "position": integer (Rank ID, nullable),
  "scheduled_date": date (required),
  "scheduled_time": time (required),
  "duration_minutes": integer (default: 30),
  "interview_type": string (choices: "Phone", "Video", "In-Person", "Technical"),
  "location": string,
  "meeting_link": url,
  "status": string (choices: "Scheduled", "Completed", "Cancelled", "Rescheduled", "No Show"),
  "result": string (choices: "Pending", "Passed", "Failed", "On Hold"),
  "interviewer_notes": text,
  "candidate_feedback": text,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Finance Record Model

```python
{
  "id": integer,
  "user": integer (User ID, required),
  "company": integer (Company ID, required),
  "start_date": date (required),
  "end_date": date (required),
  "daily_rate": decimal (auto-calculated from company's hourly_rate),
  "total_days": integer (auto-calculated),
  "total_money": decimal (auto-calculated),
  "status": string (choices: "Pending", "Approved", "Paid"),
  "notes": text,
  "created_at": datetime,
  "updated_at": datetime
}
```

### CV Submission Model

```python
{
  "id": integer,
  "user": integer (User ID, required),
  "company": integer (Company ID, required),
  "position": integer (Rank ID, nullable),
  "cv_file": file (required),
  "cover_letter": text,
  "submitted_date": date (auto),
  "status": string (choices: "Pending", "Under Review", "Interviewed", "Approved", "Rejected"),
  "rating": integer (1-5),
  "reviewed_by": integer (User ID, nullable),
  "reviewed_date": date,
  "notes": text,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Certificate Model

```python
{
  "id": integer,
  "code": string (unique, max 100),
  "name": string (max 255)
}
```

### Rank Model

```python
{
  "id": integer,
  "code": string (unique, e.g., "DO-1.000"),
  "name": string (e.g., "Master")
}
```

---

## Error Handling

### Standard Error Response Format

All error responses follow this structure:

```json
{
  "field_name": ["Error message 1", "Error message 2"],
  "another_field": ["Error message"],
  "detail": "General error message"
}
```

### Common HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |

### Example Error Responses

**Validation Error (400)**:

```json
{
  "email": ["This field is required."],
  "first_name": ["This field is required."],
  "phone_number": ["Enter a valid phone number."]
}
```

**Authentication Error (401)**:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Error (403)**:

```json
{
  "error": "Permission denied"
}
```

**Not Found Error (404)**:

```json
{
  "detail": "Not found."
}
```

---

## API Endpoints

### User Management

#### 1. List All Users

**Endpoint**: `GET /api/users/`  
**Permissions**: Admin/HR/Recruiter (all users), Employee (self only)

**Query Parameters**:

- `role`: Filter by role (Admin, HR Manager, Recruiter, Employee)
- `nationality`: Filter by nationality
- `user_status`: Filter by status
- `search`: Search by name or email

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "first_name": "Admin",
    "middle_name": "User",
    "profile_image": "http://domain.com/media/users/profile1.jpg",
    "age": 35,
    "nationality": "Egyptian",
    "phone_number": "+201234567890",
    "role": "Admin",
    "user_status": "On Site",
    "created_at": "2024-01-15T10:30:00Z",
    "certificates": [
      {"id": 1, "code": "STCW_95", "name": "STCW 95"},
      {"id": 2, "code": "GMDSS", "name": "G.M.D.S.S"}
    ],
    "user_ranks": [
      {
        "id": 1,
        "assigned_code": "DO-1.001",
        "rank": {"id": 1, "code": "DO-1.000", "name": "Master"}
      }
    ]
  }
]
```

---

#### 2. Create User

**Endpoint**: `POST /api/users/`  
**Permissions**: Admin/HR only

**Request Body**:

```json
{
  "email": "captain@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "middle_name": "Smith",
  "phone_number": "+201234567890",
  "nationality": "Egyptian",
  "age": 45,
  "date_of_birth": "1979-05-15",
  "marital_status": "Married",
  "role": "Employee",
  "passport_no": "A12345678",
  "passport_issue_date": "2020-01-01",
  "passport_expiry_date": "2030-01-01",
  "rank_ids": [1, 2],
  "certificate_ids": [1, 2, 3]
}
```

**Success Response** (201 Created):

```json
{
  "id": 25,
  "email": "captain@example.com",
  "first_name": "John",
  "middle_name": "Smith",
  "role": "Employee",
  "created_at": "2024-12-01T15:30:00Z",
  "message": "User created successfully"
}
```

**Error Response** (400):

```json
{
  "email": ["User with this email already exists."],
  "password": ["This field is required."]
}
```

---

#### 3. Get User Details

**Endpoint**: `GET /api/users/{id}/`  
**Permissions**: Admin/HR/Recruiter (all), Employee (self only)

**Success Response** (200 OK):

```json
{
  "id": 5,
  "email": "seafarer@example.com",
  "first_name": "Ahmed",
  "middle_name": "Mohamed",
  "profile_image": "http://domain.com/media/users/ahmed.jpg",
  "age": 32,
  "blood_type": "A+",
  "smoker": false,
  "nationality": "Egyptian",
  "date_of_birth": "1992-03-20",
  "marital_status": "Single",
  "user_status": "On Site",
  "phone_number": "+201234567890",
  "address": "123 Seafarer St, Alexandria",
  "passport_no": "A98765432",
  "passport_issue_date": "2021-06-15",
  "passport_expiry_date": "2031-06-15",
  "seaman_book_no": "SB123456",
  "seaman_book_expiry_date": "2026-12-31",
  "coc_certificate_name": "Master Mariner",
  "coc_certificate_number": "COC12345",
  "coc_expiry_date": "2027-05-20",
  "health_expiry_date": "2025-08-30",
  "covid_vaccine_name": "Pfizer",
  "covid_first_dose": "2021-04-15",
  "covid_second_dose": "2021-05-15",
  "english_language_level": "Advanced",
  "salary": "5000.00",
  "role": "Employee",
  "certificates": [
    {"id": 1, "code": "STCW", "name": "STCW 95"},
    {"id": 5, "code": "GMDSS", "name": "G.M.D.S.S"}
  ],
  "user_ranks": [
    {
      "id": 3,
      "assigned_code": "EO-1.005",
      "rank": {"id": 15, "code": "EO-1.000", "name": "1st. Engineer"}
    }
  ],
  "references": [],
  "sea_services": [],
  "created_at": "2024-05-10T08:20:00Z",
  "updated_at": "2024-11-25T14:30:00Z"
}
```

---

#### 4. Update User

**Endpoint**: `PUT /api/users/{id}/` or `PATCH /api/users/{id}/`  
**Permissions**: Admin/HR (all users), Employee (self only)

**Request Body** (PATCH for partial update):

```json
{
  "phone_number": "+201987654321",
  "address": "456 New Address, Cairo",
  "passport_expiry_date": "2032-01-01",
  "user_status": "Vacation"
}
```

**Success Response** (200 OK):

```json
{
  "id": 5,
  "email": "seafarer@example.com",
  "phone_number": "+201987654321",
  "address": "456 New Address, Cairo",
  "passport_expiry_date": "2032-01-01",
  "user_status": "Vacation",
  "updated_at": "2024-12-01T16:45:00Z"
}
```

---

#### 5. Delete User

**Endpoint**: `DELETE /api/users/{id}/`  
**Permissions**: Admin only

**Success Response** (204 No Content)

**Error Response** (403):

```json
{
  "error": "Only admins can delete users"
}
```

---

#### 6. Get Current User Profile

**Endpoint**: `GET /api/users/me/`  
**Permissions**: Authenticated

**Success Response** (200 OK):

```json
{
  "id": 8,
  "email": "current@example.com",
  "first_name": "Current",
  "middle_name": "User",
  "role": "Employee",
  "profile_image": "http://domain.com/media/users/current.jpg"
}
```

---

#### 7. Get User Statistics

**Endpoint**: `GET /api/users/stats/`  
**Permissions**: Admin/HR only

**Success Response** (200 OK):

```json
{
  "total_users": 150,
  "admins": 3,
  "hr_managers": 5,
  "recruiters": 10,
  "employees": 132,
  "active_users": 145
}
```

---

### Ships Management

#### 1. List All Ships

**Endpoint**: `GET /api/ships/`  
**Permissions**: Authenticated (ShipManager or Admin for modifications)

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "ship_name": "MV Ocean Voyager",
    "imo_number": "1234567",
    "company": {
      "id": 3,
      "name": "Global Shipping Co."
    },
    "ship_type": {
      "id": 1,
      "name": "Container Ship"
    },
    "flag": {
      "id": 5,
      "name": "Panama",
      "code": "PA"
    },
    "official_no": "OFF12345",
    "call_sign": "ABCD",
    "mmsi_no": "123456789",
    "port_of_registry": "Panama City",
    "gross_tonnage": 50000,
    "deadweight": 75000,
    "year_built": 2015,
    "builder": "Hyundai Heavy Industries",
    "engine_type": "MAN B&W",
    "engine_power_kw": 25000,
    "status": "Active",
    "crew": [1, 5, 8, 12],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-11-15T10:30:00Z"
  }
]
```

---

#### 2. Create Ship

**Endpoint**: `POST /api/ships/`  
**Permissions**: ShipManager or Admin

**Request Body**:

```json
{
  "ship_name": "MV Pacific Star",
  "imo_number": "9876543",
  "company": 3,
  "ship_type": 2,
  "flag": 5,
  "official_no": "OFF98765",
  "call_sign": "WXYZ",
  "port_of_registry": "Singapore",
  "gross_tonnage": 65000,
  "deadweight": 90000,
  "year_built": 2018,
  "builder": "Samsung Heavy Industries",
  "engine_type": "Wärtsilä",
  "engine_power_kw": 30000,
  "status": "Active"
}
```

**Success Response** (201 Created):

```json
{
  "id": 15,
  "ship_name": "MV Pacific Star",
  "imo_number": "9876543",
  "status": "Active",
  "created_at": "2024-12-01T17:00:00Z"
}
```

---

#### 3. Assign User to Ship Crew

**Endpoint**: `POST /api/ships/{id}/assign-user/`  
**Permissions**: ShipManager or Admin

**Request Body**:

```json
{
  "user_id": 25
}
```

**Success Response** (200 OK):

```json
{
  "status": "User Ahmed assigned to ship MV Ocean Voyager"
}
```

**Error Responses**:

```json
// 400 Bad Request
{
  "error": "user_id must be provided in the request body."
}

// 404 Not Found
{
  "error": "User not found."
}
```

---

#### 4. Unassign User from Ship Crew

**Endpoint**: `POST /api/ships/{id}/unassign-user/`  
**Permissions**: ShipManager or Admin

**Request Body**:

```json
{
  "user_id": 25
}
```

**Success Response** (200 OK):

```json
{
  "status": "User Ahmed unassigned from ship MV Ocean Voyager"
}
```

---

### Companies Management

#### 1. List All Companies

**Endpoint**: `GET /api/companies/`  
**Permissions**: Authenticated (all can read)

**Query Parameters**:

- `status`: Filter by status (Active, Inactive, Prospect)
- `company_type`: Filter by type
- `search`: Search by name, email, or contact person

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "name": "Global Shipping Company",
    "company_type": "Ship Owner",
    "email": "info@globalship.com",
    "phone": "+1234567890",
    "country": "Singapore",
    "website": "https://globalship.com",
    "contact_person": "John Doe",
    "contact_person_email": "john@globalship.com",
    "contact_person_phone": "+1234567891",
    "open_positions": 15,
    "status": "Active",
    "created_at": "2023-01-15T00:00:00Z"
  }
]
```

---

#### 2. Create Company

**Endpoint**: `POST /api/companies/`  
**Permissions**: Admin only

**Request Body**:

```json
{
  "name": "New Maritime Company",
  "company_type": "Ship Manager",
  "email": "contact@newmaritime.com",
  "phone": "+9876543210",
  "address": "123 Harbor St, Port City",
  "country": "Greece",
  "website": "https://newmaritime.com",
  "contact_person": "Maria Smith",
  "contact_person_email": "maria@newmaritime.com",
  "contact_person_phone": "+9876543211",
  "open_positions": 5,
  "status": "Active",
  "notes": "New client, focus on tanker vessels"
}
```

**Success Response** (201 Created):

```json
{
  "id": 10,
  "name": "New Maritime Company",
  "company_type": "Ship Manager",
  "status": "Active",
  "created_at": "2024-12-01T18:00:00Z"
}
```

---

#### 3. Get Company Statistics

**Endpoint**: `GET /api/companies/stats/`  
**Permissions**: Authenticated

**Success Response** (200 OK):

```json
{
  "total_companies": 45,
  "active_companies": 38,
  "total_open_positions": 127
}
```

---

#### 4. Job Orders (replaces Vacancies)

**Endpoint**: `GET /api/companies/job-orders/`  
**Endpoint**: `POST /api/companies/job-orders/`  
**Permissions**: Authenticated (Admin/HR/Recruiter = Full CRUD, Employee = Read Only)

**Query Parameters (GET)**:
- `company`: filter by company ID
- `status`: e.g. Open, Pending

**Success Response (GET)** (200 OK):
```json
[
  {
    "id": 1,
    "company": 3,
    "company_name": "Sakr Shipping",
    "reference_number": "JO-2026-001",
    "status": "Open",
    "positions": [
       { "id": 1, "rank": 7, "rank_name": "2nd. Officer", "quantity": 2 }
    ]
  }
]
```

#### 5. Job Order Positions

**Endpoint**: `GET /api/companies/job-positions/`  
**Endpoint**: `POST /api/companies/job-positions/`  
**Permissions**: Authenticated (Admin/HR/Recruiter = Full CRUD, Employee = Read Only)

**Bulk Create Request (POST - Admin/HR)**:
```json
[
  { "job_order": 1, "rank": "2nd. Officer", "quantity": 2 },
  { "job_order": 1, "rank": "Bosun", "quantity": 1 }
]
```

#### 6. Quick Apply (Employee)

**Endpoint**: `POST /api/companies/job-positions/apply/`  
**Permissions**: Authenticated (Employee Only)  
**Description**: Allows an Employee to apply to one or more open job positions. This creates a `Document` record with status `Pending` for each position, saving it to "2. 📋 CVs". When an Admin approves it, it automatically becomes a `CVSubmission`.

**Request Body** (accepts IDs, names, or both):
```json
{
  "position_ids": [1],
  "position_names": ["Bosun", "Chief Cook"]
}
```

**Success Response** (201 Created):
```json
{
  "applied": [
    {
      "document_id": 45,
      "position_id": 1,
      "rank_name": "2nd. Officer",
      "company_name": "Sakr Shipping",
      "status": "Pending"
    }
  ],
  "skipped": [],
  "total_applied": 1,
  "total_skipped": 0
}
```

---

### Interviews Management

#### 1. List All Interviews

**Endpoint**: `GET /api/interviews/interviews/`  
**Permissions**: Admin/HR/Recruiter (all), Employee (own only)

**Query Parameters**:

- `status`: Filter by status
- `scheduled_date`: Filter by date
- `company`: Filter by company ID
- `interview_type`: Filter by type

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "candidate": {
      "id": 5,
      "first_name": "Ahmed",
      "email": "ahmed@example.com"
    },
    "company": {
      "id": 3,
      "name": "Global Shipping Co."
    },
    "position": {
      "id": 15,
      "code": "EO-1.000",
      "name": "1st. Engineer"
    },
    "scheduled_date": "2024-12-05",
    "scheduled_time": "14:00:00",
    "duration_minutes": 60,
    "interview_type": "Video",
    "meeting_link": "https://zoom.us/j/123456789",
    "status": "Scheduled",
    "result": "Pending",
    "created_at": "2024-11-25T10:00:00Z"
  }
]
```

---

#### 2. Create Interview

**Endpoint**: `POST /api/interviews/interviews/`  
**Permissions**: Admin/HR/Recruiter

**Request Body**:

```json
{
  "candidate": 5,
  "company": 3,
  "position": 15,
  "scheduled_date": "2024-12-10",
  "scheduled_time": "10:00:00",
  "duration_minutes": 45,
  "interview_type": "Video",
  "meeting_link": "https://teams.microsoft.com/meet/xyz",
  "status": "Scheduled"
}
```

**Success Response** (201 Created):

```json
{
  "id": 25,
  "candidate": 5,
  "scheduled_date": "2024-12-10",
  "status": "Scheduled",
  "meeting_link": "https://teams.microsoft.com/meet/xyz",
  "created_at": "2024-12-01T19:00:00Z"
}
```

---

#### 3. Get Interview Statistics

**Endpoint**: `GET /api/interviews/interviews/stats/`  
**Permissions**: Admin/HR/Recruiter

**Success Response** (200 OK):

```json
{
  "today_interviews": 3,
  "this_week": 15,
  "pending_confirmation": 8
}
```

---

#### 4. Get Calendar View

**Endpoint**: `GET /api/interviews/interviews/calendar/`  
**Permissions**: Authenticated

**Query Parameters**:

- `month`: Month number (1-12)
- `year`: Year (e.g., 2024)

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "candidate_name": "Ahmed Mohamed",
    "company_name": "Global Shipping Co.",
    "scheduled_date": "2024-12-05",
    "scheduled_time": "14:00:00",
    "status": "Scheduled"
  },
  {
    "id": 2,
    "candidate_name": "John Smith",
    "company_name": "Ocean Transport",
    "scheduled_date": "2024-12-10",
    "scheduled_time": "10:00:00",
    "status": "Scheduled"
  }
]
```

---

### Finance Management

#### 1. List Finance Records

**Endpoint**: `GET /api/finance/finance-records/`  
**Permissions**: Admin/HR (all), Others (own only)

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "user": {
      "id": 5,
      "first_name": "Ahmed",
      "email": "ahmed@example.com"
    },
    "company": {
      "id": 3,
      "name": "Global Shipping Co."
    },
    "start_date": "2024-11-01",
    "end_date": "2024-11-30",
    "daily_rate": "150.00",
    "total_days": 30,
    "total_money": "4500.00",
    "status": "Approved",
    "created_at": "2024-12-01T00:00:00Z"
  }
]
```

---

#### 2. Calculate Finance (Without Saving)

**Endpoint**: `POST /api/finance/finance-records/calculate/`  
**Permissions**: Authenticated

**Request Body**:

```json
{
  "user": 5,
  "company": 3,
  "start_date": "2024-12-01",
  "end_date": "2024-12-15"
}
```

**Success Response** (200 OK):

```json
{
  "total_days": 15,
  "daily_rate": "150.00",
  "total_money": "2250.00"
}
```

---

#### 3. Get Finance Statistics

**Endpoint**: `GET /api/finance/finance-records/stats/`  
**Permissions**: Admin/HR only

**Success Response** (200 OK):

```json
{
  "total_records": 245,
  "pending": 15,
  "approved": 180,
  "paid": 50
}
```

---

### CV Submissions

#### 1. List CV Submissions

**Endpoint**: `GET /api/cv-submissions/`  
**Permissions**: Admin/HR/Recruiter (all), Employee (own only)

**Query Parameters**:

- `status`: Filter by status
- `company`: Filter by company ID
- `rating`: Filter by rating

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "user": {
      "id": 8,
      "first_name": "Mohamed",
      "email": "mohamed@example.com"
    },
    "company": {
      "id": 2,
      "name": "Ocean Transport Ltd"
    },
    "position": {
      "id": 10,
      "code": "DO-2.000",
      "name": "1st. Officer"
    },
    "cv_file": "http://domain.com/media/cvs/mohamed_cv.pdf",
    "submitted_date": "2024-11-20",
    "status": "Under Review",
    "rating": 4,
    "created_at": "2024-11-20T09:00:00Z"
  }
]
```

---

#### 2. Submit CV

**Endpoint**: `POST /api/cv-submissions/`  
**Permissions**: Authenticated

**Request Body** (multipart/form-data):

```
user: 8 (auto-set for Employee role)
company: 2
position: 10
cv_file: [file]
cover_letter: "I am very interested in this position..."
```

**Success Response** (201 Created):

```json
{
  "id": 15,
  "user": 8,
  "company": 2,
  "position": 10,
  "status": "Pending",
  "submitted_date": "2024-12-01",
  "created_at": "2024-12-01T20:00:00Z"
}
```

---

#### 3. Update CV Status

**Endpoint**: `PATCH /api/cv-submissions/{id}/update-status/`  
**Permissions**: Admin/HR/Recruiter

**Request Body**:

```json
{
  "status": "Approved"
}
```

**Success Response** (200 OK):

```json
{
  "id": 15,
  "status": "Approved",
  "reviewed_by": 1,
  "reviewed_date": "2024-12-01"
}
```

---

#### 4. Get CV Statistics

**Endpoint**: `GET /api/cv-submissions/stats/`  
**Permissions**: Authenticated

**Success Response** (200 OK):

```json
{
  "total": 125,
  "under_review": 45,
  "interviewed": 30,
  "pending": 35,
  "approved": 15,
  "under_review_percent": 36,
  "interviewed_percent": 24,
  "pending_percent": 28,
  "approved_percent": 12
}
```

---

### AI Document Processing

#### 1. Upload and Process Document

**Endpoint**: `POST /ai/upload/`  
**Permissions**: Authenticated

**Request Body** (multipart/form-data):

```
document: [PDF or DOCX file]
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "applicant_id": 45,
  "user_id": 67,
  "message": "Document processed and saved successfully",
  "extracted_data": {
    "first_name": "John",
    "middle_name": "Michael",
    "email": "john@example.com",
    "phone_number": "+201234567890",
    "nationality": "Egyptian",
    "passport_no": "A12345678",
    "certificates": ["STCW 95", "GMDSS"],
    "sea_service_experience": "5 years"
  }
}
```

**Error Response** (400):

```json
{
  "error": "No document file provided",
  "details": "Please upload a PDF or DOCX file"
}
```

---

#### 2. List Applicants

**Endpoint**: `GET /ai/applicants/`  
**Permissions**: Authenticated

**Success Response** (200 OK):

```json
[
  {
    "id": 45,
    "first_name": "John",
    "middle_name": "Michael",
    "email": "john@example.com",
    "phone_number": "+201234567890",
    "nationality": "Egyptian",
    "created_at": "2024-11-28T15:30:00Z"
  }
]
```

---

#### 3. Convert Applicant to User

**Endpoint**: `POST /ai/convert/`  
**Permissions**: Authenticated

**Request Body**:

```json
{
  "applicant_id": 45,
  "password": "SecurePass123",
  "role": "Employee"
}
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "user_id": 68,
  "message": "Applicant converted to user successfully"
}
```

---

### AI Chat Agent

#### 1. Send Message to AI

**Endpoint**: `POST /ai-agents/chat/`  
**Permissions**: AllowAny

**Request Body**:

```json
{
  "message": "Find all seafarers with Master rank",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response** (200 OK):

```json
{
  "response": "I found 5 seafarers with Master rank. Here are the details...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

#### 2. Get Chat History

**Endpoint**: `GET /ai-agents/chat/history/{session_id}/`  
**Permissions**: AllowAny

**Success Response** (200 OK):

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "Find all seafarers with Master rank",
      "timestamp": "2024-12-01T20:00:00Z"
    },
    {
      "role": "assistant",
      "content": "I found 5 seafarers with Master rank...",
      "timestamp": "2024-12-01T20:00:05Z"
    }
  ]
}
```

---

### Contracts Management

#### 1. List Contracts

**Endpoint**: `GET /api/contracts/`  
**Permissions**: Admin/HR/Recruiter (all), Employee (own only)

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "user": {
      "id": 5,
      "first_name": "Ahmed",
      "email": "ahmed@example.com"
    },
    "ship": {
      "id": 1,
      "ship_name": "MV Ocean Voyager"
    },
    "company": {
      "id": 3,
      "name": "Global Shipping Co."
    },
    "rank": {
      "id": 15,
      "code": "EO-1.000",
      "name": "1st. Engineer"
    },
    "sign_on_date": "2024-06-01",
    "sign_off_date": "2024-12-01",
    "salary": "5000.00",
    "currency": "USD",
    "status": "Active",
    "created_at": "2024-05-15T00:00:00Z"
  }
]
```

---

#### 2. Create Contract

**Endpoint**: `POST /api/contracts/`  
**Permissions**: Admin/HR only

**Request Body**:

```json
{
  "user": 5,
  "ship": 1,
  "company": 3,
  "rank": 15,
  "sign_on_date": "2025-01-01",
  "sign_off_date": "2025-07-01",
  "salary": "5500.00",
  "currency": "USD",
  "status": "Pending Signature"
}
```

**Success Response** (201 Created):

```json
{
  "id": 25,
  "user": 5,
  "ship": 1,
  "status": "Pending Signature",
  "created_at": "2024-12-01T21:00:00Z"
}
```

---

#### 3. Get Contract Statistics

**Endpoint**: `GET /api/contracts/stats/`  
**Permissions**: Authenticated

**Success Response** (200 OK):

```json
{
  "signed_contracts": 85,
  "pending_signature": 15,
  "drafts": 8,
  "critical": 5,
  "warning": 12,
  "notice": 20
}
```

---

## Additional Notes

### File Upload Guidelines

When uploading files (images, documents, CVs):

- Use `multipart/form-data` content type
- Maximum file size: 10MB
- Supported formats:
  - Images: JPG, PNG, WEBP
  - Documents: PDF, DOCX
  - Files: PDF (for contracts, CVs)

### Date Formats

All dates should be in ISO 8601 format:

- Date: `YYYY-MM-DD` (e.g., "2024-12-01")
- DateTime: `YYYY-MM-DDTHH:MM:SSZ` (e.g., "2024-12-01T20:30:00Z")
- Time: `HH:MM:SS` (e.g., "14:30:00")

### Pagination

List endpoints support pagination:

- Add `?page=2` to query parameters
- Default page size: 50 items
- Response includes pagination metadata

### Filtering and Search

Many endpoints support filtering:

- Use query parameters like `?status=Active&role=Employee`
- Search fields: `?search=ahmed`
- Combine multiple filters: `?status=Active&nationality=Egyptian&search=engineer`

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Contact**: For API support, contact your system administrator.
