# Sakr Manning Agency - API Documentation

## 1. Introduction

Welcome to the Sakr Manning Agency API documentation. This API powers the Manning Agency platform, facilitating the management of seafarers, companies, ships, and recruitment processes. It is built using Django REST Framework.

**Base URL:** `http://<your-domain>/api/`

## 2. Authentication

The API uses JWT (JSON Web Token) for authentication.

### Authentication Endpoints

#### Login

Obtain a pair of access and refresh tokens.

- **URL:** `/api/login/`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "username": "user123",
        "password": "password123"
    }
    ```

- **Response:**

    ```json
    {
        "refresh": "ey...",
        "access": "ey..."
    }
    ```

#### Refresh Token

Get a new access token using a valid refresh token.

- **URL:** `/api/login/refresh/`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "refresh": "ey..."
    }
    ```

#### Register

Register a new user account.

- **URL:** `/api/register/`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "username": "newuser",
        "email": "user@example.com",
        "password": "securepassword",
        "role": "seafarer" 
    }
    ```

- **Response:**

    ```json
    {
        "message": "User registered successfully",
        "user": {
            "id": 1,
            "username": "newuser",
            "email": "user@example.com",
            "role": "seafarer"
        }
    }
    ```

---

## 3. Data Flows

### 3.1 User Data Flow (Seafarer)

1. **Registration & Onboarding**:
    - User registers via `/api/register/`.
    - User logs in via `/api/login/` to receive a JWT.
    - User completes their profile using `/api/users/<id>/`.

2. **Document Management**:
    - User uploads documents (Passport, Seaman Book, etc.) via `/ai/upload/` or `/ai/integrated-upload/`.
    - The system uses AI to extract data from the uploaded documents.
    - Extracted data is verified and saved to the user's profile.

3. **Certificates & Ranks**:
    - User views their assigned ranks via `/api/users/<id>/ranks/`.
    - User manages certificates via `/api/users/<id>/certificates/`.

4. **Job Application**:
    - User can view available opportunities (if implemented).
    - User submits CV via `/api/cv-submissions/`.

### 3.2 Admin Data Flow

1. **User Management**:
    - Admin views all users via `/api/all/` or `/api/users/`.
    - Admin filters users based on criteria via `/api/filter/`.
    - Admin creates new users manually via `/api/create/`.

2. **Master Data Management**:
    - Admin manages Companies via `/api/companies/`.
    - Admin manages Ships via `/api/ships/`.
    - Admin manages Ranks and Certificates via `/api/ranks/` and `/api/certificates/`.

3. **Recruitment Process**:
    - Admin schedules and manages interviews via `/api/interviews/`.
    - Admin tracks traveling papers and tickets via `/api/tickets-papers/`.

4. **AI & Automation**:
    - Admin can batch convert applicants to users via `/ai/batch-convert/`.
    - Admin monitors sync status of documents via `/ai/sync-status/`.

---

## 4. User Endpoints

### Get Own Profile

Retrieve details of the logged-in user.

- **URL:** `/api/users/<id>/`
- **Method:** `GET`
- **Permissions:** Authenticated User
- **Response:**

    ```json
    {
        "id": 1,
        "username": "seafarer1",
        "email": "seafarer1@example.com",
        "role": "seafarer",
        "profile": { ... }
    }
    ```

### Manage Certificates

List or add certificates for a specific user.

- **URL:** `/api/users/<user_id>/certificates/`
- **Method:** `GET`
- **Response:**

    ```json
    [
        {
            "id": 1,
            "name": "STCW Basic Safety Training",
            "issue_date": "2023-01-01",
            "expiry_date": "2028-01-01"
        }
    ]
    ```

- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "name": "Advanced Fire Fighting",
        "issue_date": "2023-05-01",
        "expiry_date": "2028-05-01"
    }
    ```

### Manage Ranks

List or add ranks for a specific user.

- **URL:** `/api/users/<user_id>/ranks/`
- **Method:** `GET`
- **Response:**

    ```json
    [
        {
            "id": 1,
            "title": "Chief Officer",
            "code": "CO"
        }
    ]
    ```

### Upload Document (AI Powered)

Upload a document for AI processing.

- **URL:** `/ai/upload/`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  - `file`: (Binary file data)
  - `document_type`: "passport" | "seaman_book" | "certificate"
- **Response:**

    ```json
    {
        "id": 123,
        "status": "processing",
        "message": "Document uploaded successfully"
    }
    ```

### Submit CV

Submit a CV for review.

- **URL:** `/api/cv-submissions/`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  - `file`: (Binary file data)
  - `user`: 1
- **Response:**

    ```json
    {
        "id": 45,
        "status": "submitted",
        "submitted_at": "2023-10-27T10:00:00Z"
    }
    ```

---

## 5. Admin Endpoints

### User Management

#### List All Users

Retrieve a list of all registered users.

- **URL:** `/api/all/`
- **Method:** `GET`
- **Permissions:** Admin
- **Response:**

    ```json
    [
        {
            "id": 1,
            "username": "user1",
            "email": "user1@example.com",
            "role": "seafarer"
        },
        ...
    ]
    ```

#### Create User

Manually create a new user.

- **URL:** `/api/create/`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "username": "newadmin",
        "email": "admin@example.com",
        "password": "securepassword",
        "role": "admin"
    }
    ```

#### Filter Users

Filter users based on specific criteria.

- **URL:** `/api/filter/`
- **Method:** `GET`
- **Query Params:** `?rank=Captain&status=Available`
- **Response:** (List of users matching criteria)

### Master Data Management

#### Companies

Manage shipping companies.

- **URL:** `/api/companies/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "name": "Ocean Lines",
        "address": "123 Port Road",
        "contact_email": "contact@oceanlines.com"
    }
    ```

#### Ships

Manage ships in the fleet.

- **URL:** `/api/ships/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "name": "MV Voyager",
        "imo_number": "1234567",
        "company": 1,
        "vessel_type": "Bulk Carrier"
    }
    ```

#### Ranks

Manage available ranks.

- **URL:** `/api/ranks/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "title": "Second Engineer",
        "code": "2E"
    }
    ```

#### Certificates

Manage certificate types.

- **URL:** `/api/certificates/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "name": "GMDSS General Operator",
        "code": "GMDSS"
    }
    ```

### Recruitment & Operations

#### Interviews

Schedule and track interviews.

- **URL:** `/api/interviews/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "candidate": 1,
        "interviewer": 2,
        "scheduled_time": "2023-11-01T14:00:00Z",
        "status": "scheduled"
    }
    ```

#### Tickets

Manage flight tickets for seafarers.

- **URL:** `/api/tickets-papers/tickets/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "user": 1,
        "ticket_number": "ET123456789",
        "file": (Binary file)
    }
    ```

#### Traveling Papers

Manage visa and other travel documents.

- **URL:** `/api/tickets-papers/traveling-papers/`
- **Method:** `GET`, `POST`
- **Request Body (POST):**

    ```json
    {
        "user": 1,
        "title": "Schengen Visa",
        "issued_date": "2023-10-01",
        "file": (Binary file)
    }
    ```

### AI & Automation

#### Batch Convert Applicants

Convert multiple AI-processed applicants into system users.

- **URL:** `/ai/batch-convert/`
- **Method:** `POST`
- **Request Body:**

    ```json
    {
        "applicant_ids": [101, 102, 103]
    }
    ```

- **Response:**

    ```json
    {
        "converted_count": 3,
        "errors": []
    }
    ```

#### Sync Status

Check if an applicant's data has been synced to the main user database.

- **URL:** `/ai/sync-status/`
- **Method:** `GET`
- **Query Params:** `?applicant_id=101`
- **Response:**

    ```json
    {
        "synced": true,
        "user_id": 55,
        "sync_date": "2023-10-27T12:00:00Z"
    }
    ```

---

## 6. Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request successful.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Invalid input data.
- `401 Unauthorized`: Authentication credentials missing or invalid.
- `403 Forbidden`: You do not have permission to perform this action.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server-side error.
