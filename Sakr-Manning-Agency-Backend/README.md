

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white )
![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-A30000?style=for-the-badge&logo=django&logoColor=white )
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white )

A robust web application designed to manage the complete operations of a maritime manning agency. This system, built with Django and Django REST Framework, provides a comprehensive and **secure backend solution** for managing seafarers, their professional documentation, employment contracts, company details, and ship assignments.

## Core Features

This project provides a full-featured backend system with a powerful Django Admin interface and a complete REST API for programmatic access.

### 1. Seafarer & Employment Management
-   **Custom User Model**: Built on Django's `AbstractUser` for a flexible and secure foundation. **Login is handled via email and password.**
-   **Public User Registration**: New users can sign up through a dedicated, public API endpoint.
-   **Detailed Seafarer Profiles**: Store extensive information for each seafarer, including personal, professional, and visa details, based on detailed Figma designs.
-   **Employment Contracts**: A dedicated model to track the employment history of each seafarer, including their rank, vessel, salary, and contract dates.
-   **Dynamic Ranks & Certificates**: Assign multiple professional ranks and certificates to each user.
-   **Document Management**: Upload and manage scanned documents like tickets and traveling papers for each user.

### 2. Ship & Company Management
-   **Detailed Ship Profiles**: Manage a fleet of ships with extensive details including IMO number, vessel type, flag, tonnage, and engine specifications.
-   **Company Database**: Maintain a list of companies that own or operate the ships.
-   **Crew Roster Management**: Assign crew members to ships via the `Contract` model, creating a dynamic and trackable crew roster for every vessel.

### 3. Secure REST API with JWT Authentication
A complete RESTful API provides programmatic access to all resources. The API is secured using **JSON Web Tokens (JWT)** with a 15-day refresh token lifetime.

**Authentication & Registration Endpoints:**

| Method | URL                     | Description                                                  |
| :----- | :---------------------- | :----------------------------------------------------------- |
| `POST` | `/api/register/`        | **Register (Public)**: Create a new user account.            |
| `POST` | `/api/login/`           | **Login**: Authenticate with **email** and password to receive access and refresh tokens. |
| `POST` | `/api/login/refresh/`   | **Refresh Token**: Use a valid refresh token to get a new access token. |

**Key API Endpoints (Requires Authentication):**

| Resource | Method | URL                                         | Description                                  |
| :--- | :----- | :------------------------------------------ | :------------------------------------------- |
| **Users** | `GET`, `POST` | `/api/users/`                               | List or create users.                        |
| | `GET`, `PUT`, `DELETE` | `/api/users/<id>/`                          | Retrieve, update, or delete a specific user. |
| **Ships** | `GET`, `POST` | `/api/ships/`                               | List or create ships.                        |
| | `GET`, `PUT`, `DELETE` | `/api/ships/<id>/`                          | Retrieve, update, or delete a specific ship. |
| **Contracts** | `GET`, `POST` | `/api/contracts/`                           | **New**: List or create employment contracts. |
| | `GET`, `PUT`, `DELETE` | `/api/contracts/<id>/`                      | **New**: Manage a specific contract.         |
| **Core Data** | `GET` | `/api/core/flags/`                          | **New**: Get a list of all country flags.    |
| | `GET` | `/api/core/vessel-types/`                 | **New**: Get a list of all vessel types.     |
| **User Docs** | `GET`, `POST` | `/api/users/<user_id>/tickets/`             | List or upload tickets for a specific user.  |
| | `DELETE`| `/api/users/<user_id>/tickets/<ticket_id>/` | Delete a specific ticket.                    |
| | `GET`, `POST` | `/api/users/<user_id>/traveling-papers/`    | List or upload traveling papers for a user.  |
| | `DELETE`| `/api/users/<user_id>/traveling-papers/<paper_id>/`| Delete a specific traveling paper.         |

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python (3.8 or newer)
-   Django & Django REST Framework
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
-   [ ] **Advanced Reporting**: Develop a module for generating reports on crew composition, certificate expiry dates, and contract statuses.
-   [ ] **Frontend Application**: Build a frontend client (e.g., using React, Vue.js, or Svelte ) to provide a rich user interface for interacting with the API.
# ... (rest of your README )

# Forcing a new commit to sync with Hugging Face.
