# Sakr Manning Agency - Management System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white )
![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-A30000?style=for-the-badge&logo=django&logoColor=white )
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white )

A robust web application designed to manage the complete operations of a maritime manning agency. This system, built with Django and Django REST Framework, provides a comprehensive backend solution for managing seafarers (users), their professional documentation, ranks, certificates, company details, and their assignments to various ships.

## Core Features

This project provides a full-featured backend system with a powerful Django Admin interface and a complete REST API for programmatic access.

### 1. Seafarer (User) Management
-   **Detailed Seafarer Profiles**: Store extensive information for each seafarer, including personal details, contact information, travel documents (passports, seaman's books), health certificates, and professional qualifications.
-   **Dynamic Ranks & Certificates**: Assign multiple professional ranks and certificates to each user through a flexible many-to-many relationship.
-   **Automatic User Codes**: The system automatically generates a unique `assigned_code` for each rank a user holds, simplifying tracking and identification.

### 2. Ship & Company Management
-   **Ship Fleet Profiles**: Manage a fleet of ships with details like IMO number, type, flag, and operational status.
-   **Company Database**: Maintain a list of companies that own or operate the ships.
-   **Crew Roster Management**: A key feature allowing the assignment of multiple users (crew members) to each ship, creating a dynamic and trackable crew roster for every vessel.

### 3. Powerful Django Admin
-   **Customized Admin Panels**: User-friendly admin views for all models, including Users, Ships, Ranks, and Certificates.
-   **Efficient Data Management**: Utilizes features like `list_display`, `search_fields`, and `list_filter` for easy data browsing and management.
-   **Intuitive Relationship Editing**: Implements `filter_horizontal` widgets for an excellent user experience when assigning ranks, certificates, and crew members to ships.
-   **Inline Editing**: Manage related objects like tickets and travel papers directly from the user's detail page in the admin.

### 3. Secure REST API with JWT Authentication
A complete RESTful API built with Django REST Framework provides programmatic access to all resources. The API is secured using **JSON Web Tokens (JWT)** with a 15-day refresh token lifetime.

**Authentication Endpoints:**

| Method | URL                     | Description                                                  |
| :----- | :---------------------- | :----------------------------------------------------------- |
| `POST` | `/api/login/`           | **Login**: Authenticate with username and password to receive an access and a refresh token. |
| `POST` | `/api/login/refresh/`   | **Refresh Token**: Use a valid refresh token to get a new access token. |

### 4. Full-Featured REST API
A complete RESTful API built with Django REST Framework provides programmatic access to all resources, enabling integration with frontend applications or other services.

**Key API Endpoints:**

| Method | URL                                         | Description                                  |
| :----- | :------------------------------------------ | :------------------------------------------- |
| `GET`  | `/api/users/`                               | Get a list of all users.                     |
| `POST` | `/api/users/create`                         | Create a new user.                           |
| `GET`  | `/api/users/filter/`                        | Filter users by name, nationality, rank, etc. |
| `GET`  | `/api/users/<id>/`                          | Retrieve a specific user's details.          |
| `PUT`  | `/api/users/<id>/`                          | Update a user's details.                     |
| `DELETE`| `/api/users/<id>/`                          | Delete a user.                               |
| `GET`  | `/api/ships/`                               | Get a list of all ships.                     |
| `POST` | `/api/ships/`                               | Create a new ship.                           |
| `GET`  | `/api/ships/<id>/`                          | Retrieve a specific ship's details.          |
| `PUT`  | `/api/ships/<id>/`                          | Update a ship's details.                     |
| `DELETE`| `/api/ships/<id>/`                          | Delete a ship.                               |
| `POST` | `/api/ships/<id>/assign-user/`              | **Action**: Assign a user to a ship's crew.  |
| `POST` | `/api/ships/<id>/unassign-user/`            | **Action**: Remove a user from a ship's crew.|

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

-   Python (3.8 or newer)
-   Django
-   Django REST Framework
-   django-filter
-   A `requirements.txt` file should be present in the project.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Create and activate a virtual environment:**
    This isolates the project's dependencies from your system's Python installation.
    ```bash
    # For Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you don't have a `requirements.txt` file yet, you can create one with `pip freeze > requirements.txt` )*

4.  **Apply database migrations:**
    This command creates the necessary database tables for all the apps based on the models defined.
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a superuser:**
    This will create an admin account, allowing you to log in to the Django admin panel.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set your username, email, and password.

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The project will now be running at `http://127.0.0.1:8000/`.
    -   Access the **API** at `http://127.0.0.1:8000/api/`.
    -   Access the **Admin Panel** at `http://127.0.0.1:8000/admin/`.

## Future Development Roadmap

Potential features and improvements planned for the future:

-   [x] **API Authentication**: Implement token-based authentication (e.g., JWT or DRF's TokenAuthentication ) to secure the API.
-   [ ] **User Roles & Permissions**: Define distinct roles (e.g., Admin, Ship Manager, HR) with specific permissions for accessing and modifying data.
-   [ ] **File Uploads via API**: Enhance API endpoints to handle uploads for seafarer profile pictures and scanned document files.
-   [ ] **Advanced Reporting**: Develop a module for generating reports on crew composition, certificate expiry dates, and ship assignments.
-   [ ] **Frontend Application**: Build a frontend client (e.g., using React, Vue.js, or Svelte) to provide a rich user interface for interacting with the API.
