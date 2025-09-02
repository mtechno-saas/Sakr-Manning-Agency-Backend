# Sakr Manning Agency - Management System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white )
![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-A30000?style=for-the-badge&logo=django&logoColor=white )
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white )

A robust web application designed to manage the complete operations of a maritime manning agency. This system, built with Django and Django REST Framework, provides a comprehensive and **secure backend solution** for managing seafarers (users), their professional documentation, ranks, certificates, company details, and their assignments to various ships.

## Core Features

This project provides a full-featured backend system with a powerful Django Admin interface and a complete REST API for programmatic access.

### 1. Seafarer (Custom User) Management
-   **Custom User Model**: Built on Django's `AbstractUser` to provide a flexible and secure foundation. **Login is handled via email and password.**
-   **Public User Registration**: New users can sign up through a dedicated, public API endpoint.
-   **Detailed Seafarer Profiles**: Store extensive information for each seafarer, including personal details, contact information, and professional qualifications.
-   **Dynamic Ranks & Certificates**: Assign multiple professional ranks and certificates to each user through a flexible many-to-many relationship.
-   **Document Management**: Upload and manage scanned documents like tickets and traveling papers for each user.

### 2. Ship & Company Management
-   **Ship Fleet Profiles**: Manage a fleet of ships with details like IMO number, type, flag, and operational status.
-   **Company Database**: Maintain a list of companies that own or operate the ships.
-   **Crew Roster Management**: A key feature allowing the assignment of multiple users (crew members) to each ship, creating a dynamic and trackable crew roster for every vessel.

### 3. Secure REST API with JWT Authentication
A complete RESTful API built with Django REST Framework provides programmatic access to all resources. The API is secured using **JSON Web Tokens (JWT)** with a 15-day refresh token lifetime.

**Authentication & Registration Endpoints:**

| Method | URL                     | Description                                                  |
| :----- | :---------------------- | :----------------------------------------------------------- |
| `POST` | `/api/register/`        | **Register (Public)**: Create a new user account with email, password, and name. |
| `POST` | `/api/login/`           | **Login**: Authenticate with **email** and password to receive an access and a refresh token. |
| `POST` | `/api/login/refresh/`   | **Refresh Token**: Use a valid refresh token to get a new access token. |

**Key API Endpoints (Requires Authentication):**

| Resource | Method | URL                                         | Description                                  |
| :--- | :----- | :------------------------------------------ | :------------------------------------------- |
| **Users** | `GET`  | `/api/users/`                               | Get a list of all users.                     |
| | `POST` | `/api/users/`                               | Create a new user (as an admin).             |
| | `GET`  | `/api/users/<id>/`                          | Retrieve a specific user's details.          |
| | `PUT`  | `/api/users/<id>/`                          | Update a user's details.                     |
| | `DELETE`| `/api/users/<id>/`                          | Delete a user.                               |
| **Ships** | `GET`  | `/api/ships/`                               | Get a list of all ships.                     |
| | `POST` | `/api/ships/`                               | Create a new ship.                           |
| | `GET`  | `/api/ships/<id>/`                          | Retrieve a specific ship's details.          |
| | `PUT`  | `/api/ships/<id>/`                          | Update a ship's details.                     |
| | `DELETE`| `/api/ships/<id>/`                          | Delete a ship.                               |
| | `POST` | `/api/ships/<id>/assign-user/`              | **Action**: Assign a user to a ship's crew.  |
| **User Documents** | `GET`  | `/api/users/<user_id>/tickets/`             | List all tickets for a specific user.        |
| | `POST` | `/api/users/<user_id>/tickets/`             | Upload a new ticket for a user.              |
| | `DELETE`| `/api/users/<user_id>/tickets/<ticket_id>/` | Delete a specific ticket.                    |
| | `GET`  | `/api/users/<user_id>/traveling-papers/`    | List all traveling papers for a user.        |
| | `POST` | `/api/users/<user_id>/traveling-papers/`    | Upload a new traveling paper for a user.     |
| | `DELETE`| `/api/users/<user_id>/traveling-papers/<paper_id>/`| Delete a specific traveling paper.         |

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python (3.8 or newer)
-   Django
-   Django REST Framework
-   djangorestframework-simplejwt
-   drf-nested-routers
-   A `requirements.txt` file should be present in the project.

### Installation

1.  **Clone the repository.**
2.  **Create and activate a virtual environment.**
3.  **Install the required packages:** `pip install -r requirements.txt`
4.  **Apply database migrations:** `python manage.py makemigrations` and then `python manage.py migrate`
5.  **Create a superuser:** `python manage.py createsuperuser` (You will be prompted for an **email** as the login field).
6.  **Run the development server:** `python manage.py runserver`

### Accessing the API

1.  **Register a new user:** Send a `POST` request to `http://127.0.0.1:8000/api/register/`.
2.  **Get your tokens:** Send a `POST` request to `http://127.0.0.1:8000/api/login/` with your email and password.
3.  **Authorize your requests:** To access a protected endpoint, include an `Authorization` header with the value `Bearer <your_access_token>`.

## Future Development Roadmap

-   [x] **API Authentication**: Implemented JWT with a 15-day refresh token.
-   [x] **File Uploads via API**: Implemented for profile pictures and user documents.
-   [x] **User Roles & Permissions**: Foundational system using Django Groups is in place.
-   [ ] **Advanced Reporting**: Develop a module for generating reports on crew composition, certificate expiry dates, etc.
-   [ ] **Frontend Application**: Build a frontend client (e.g., using React, Vue.js, or Svelte ) to provide a rich user interface for interacting with the API.
