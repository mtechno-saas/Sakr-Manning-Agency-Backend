# Sakr Manning Agency - API Documentation

## 1. Introduction

Welcome to the Sakr Manning Agency API documentation. This API powers the Manning Agency platform, facilitating the management of seafarers, companies, ships, recruitment processes, and financial records. It is built using Django REST Framework and features role-based access control (RBAC) and AI-powered document processing.

**Base URL:** `http://<your-domain>/api/`

## 2. Authentication

The API uses JWT (JSON Web Token) for authentication. All protected endpoints require the `Authorization` header.

**Header Format:** `Authorization: Bearer <access_token>`

### Authentication Endpoints

#### Login

Obtain a pair of access and refresh tokens.

- **URL:** `/api/users/users/`
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

- **URL:** `/api/users/users/<id>/register/`
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

---

## 3. Data Flows (Storytelling)

### 3.1 User Data Flow (Seafarer Journey)

This flow describes how a seafarer interacts with the platform.

1. **Onboarding**:
    - The seafarer registers via `/api/register/`.
    - They log in via `/api/login/` to get their access token.
    - They view their profile using `/api/users/me/` or `/api/users/<id>/`.

2. **Document Management**:
    - To verify their qualifications, the seafarer uploads documents (Passport, Seaman Book) using the AI-powered upload at `/ai/upload/`.
    - The system automatically extracts data.
    - They can view their assigned certificates- **URL:** `/api/users/users/<user_id>/certificates/`.

3. **Job Application**:
    - The seafarer submits their CV for review via `/api/cv-submissions/`.
    - They can track the status of their submission (e.g., "Under Review", "Interviewed").

4. **Interview & Deployment**:
    - If selected, they can view their scheduled interviews via `/api/interviews/`.
    - Once hired, they can view their contract details via `/api/contracts/`.
    - Travel arrangements (tickets and visa papers) can be checked under `/api/tickets-papers/tickets/` and `/api/tickets-papers/traveling-papers/`.

5. **AI Assistance**:
    - At any point, the seafarer can ask questions to the AI agent via `/ai-agents/chat/` to get instant support regarding their application or status.

### 3.2 Admin Data Flow (Recruitment & Operations)

This flow describes how an Admin or HR Manager manages the platform.

1. **Dashboard & Overview**:
    - The admin checks high-level statistics using `/api/users/stats/`, `/api/contracts/stats/`, and `/api/interviews/stats/` to see active users, pending contracts, and upcoming interviews.

2. **User & Master Data Management**:
    - Admin manages shipping companies via `/api/companies/` and ships via `/api/ships/`.
    - They manage global settings like Ranks (`/api/ranks/`) and Certificates (`/api/certificates/`).
    - They can manually create users (`/api/create/`) or filter existing ones (`/api/filter/`).

3. **Recruitment Pipeline**:
    - Admin reviews incoming CVs via `/api/cv-submissions/`.
    - They schedule interviews for candidates using `/api/interviews/`.
    - They can batch convert AI-processed applicants into full system users via `/ai/batch-convert/`.

4. **Operations & Logistics**:
    - Admin assigns ranks to users via `/api/users/<id>/assign-rank/`.
    - They manage contracts via `/api/contracts/`, ensuring they are signed and valid.
    - They handle logistics by issuing tickets (`/api/tickets-papers/tickets/`) and traveling papers (`/api/tickets-papers/traveling-papers/`).

5. **Finance**:
    - Admin tracks financial records, payments, and invoices via `/api/finance-records/`.
    - They can export financial data for reporting using `/api/finance-records/export/`.

---

## 4. API Reference

### 4.1 Users & Profiles

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/api/users/` | GET, POST | List or create users | Admin/HR |
| `/api/users/<id>/` | GET, PUT, DELETE | Retrieve, update, or delete a user | Admin/HR/Owner |
| `/api/users/me/` | GET | Get current user's profile | Authenticated |
| `/api/users/stats/` | GET | Get user statistics | Admin/HR |
| `/api/all/` | GET | Get all users (simplified) | Admin/HR |
| `/api/create/` | POST | Manually create a user | Admin/HR |
| `/api/filter/` | GET | Filter users by criteria | Admin/HR/Recruiter |
| `/api/users/<id>/assign-rank/<rank_id>/` | POST | Assign a rank to a user | Admin/HR |
| `/api/users/<id>/ranks/` | GET | Get user's ranks | Admin/HR/Owner |
| `/api/users/<id>/certificates/` | GET | Get user's certificates | Admin/HR/Owner |

### 4.2 Recruitment (CVs & Interviews)

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- **URL:** `/api/users/cv-submissions/` | GET, POST | List or submit CVs | Authenticated |
| `/api/cv-submissions/stats/` | GET | Get CV statistics | Authenticated |
| `/api/cv-submissions/<id>/update-status/` | PATCH | Update CV status | Recruiter+ |
| `/api/interviews/` | GET, POST | List or schedule interviews | Authenticated |
| `/api/interviews/stats/` | GET | Get interview statistics | Authenticated |
| `/api/interviews/calendar/` | GET | Get interviews for calendar view | Authenticated |

### 4.3 Documents & Contracts

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/api/contracts/` | GET, POST | Manage contracts | Admin/HR/Owner |
| `/api/contracts/stats/` | GET | Get contract statistics | Authenticated |
| `/api/certificates/` | GET, POST | Manage certificate types | Admin/HR (Write) |
| `/api/ranks/` | GET, POST | Manage rank types | Admin/HR (Write) |
| `/api/references/` | GET, POST | Manage user references | Authenticated |
| `/api/sea-services/` | GET, POST | Manage sea service records | Authenticated |

### 4.4 Master Data (Companies & Ships)

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/api/companies/` | GET, POST | Manage shipping companies | Admin/HR |
| `/api/companies/stats/` | GET | Get company statistics | Authenticated |
| `/api/ships/` | GET, POST | Manage ships | Admin/HR |
| `/api/core/flags/` | GET | List vessel flags | Authenticated |
| `/api/core/vessel-types/` | GET | List vessel types | Authenticated |

### 4.5 Logistics (Tickets & Papers)

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/api/tickets-papers/tickets/` | GET, POST | Manage flight tickets | Admin/HR |
| `/api/tickets-papers/traveling-papers/` | GET, POST | Manage visa/travel papers | Admin/HR |

### 4.6 Finance

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/api/finance/finance-records/` | GET, POST | Manage finance records | Admin/HR |
| `/api/finance/finance-records/stats/` | GET | Get finance statistics | Admin/HR |
| `/api/finance/finance-records/export/` | GET | Export finance data | Admin/HR |

### 4.7 AI Services

| Endpoint | Method | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/ai/upload/` | POST | Upload document for AI extraction | Authenticated |
| `/ai/applicants/` | GET | List AI-processed applicants | Admin/HR |
| `/ai/batch-convert/` | POST | Convert applicants to users | Admin/HR |
| `/ai/sync-status/` | GET | Check sync status of applicant | Admin/HR |
| `/ai-agents/chat/` | POST | Chat with AI agent | Authenticated |
| `/ai-agents/chat/history/<session_id>/` | GET | Get chat history | Authenticated |

---

## 5. Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request successful.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Invalid input data.
- `401 Unauthorized`: Authentication credentials missing or invalid.
- `403 Forbidden`: You do not have permission to perform this action.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server-side error.
