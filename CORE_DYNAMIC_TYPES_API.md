# Core Dynamic Types API Reference

This document covers the API endpoints for managing dynamic types in the system: **Flags**, **Company Types**, and **Vessel Types**. These models allow administrators to manage the dropdown choices used across the application.

---

## 1. Flags
Used by both **Companies** and **Ships** to represent nationalities/countries.

### Data Model
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Unique identifier (read-only) |
| `name` | String | Name of the country/flag (Unique) |
| `icon` | File/Image | Optional image file for the flag |

### Endpoints
*   **List Flags**: `GET /api/core/flags/`
*   **Create Flag**: `POST /api/core/flags/`
*   **Retrieve Flag**: `GET /api/core/flags/{id}/`
*   **Update Flag**: `PATCH /api/core/flags/{id}/`
*   **Delete Flag**: `DELETE /api/core/flags/{id}/`

### Request / Response Examples

**POST /api/core/flags/**
```json
{
    "name": "New Country",
    "icon": null
}
```

**Response (201 Created)**
```json
{
    "id": 195,
    "name": "New Country",
    "icon": null
}
```

---

## 2. Company Types
Used by the **Company** model to categorize manning agencies.

### Data Model
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Unique identifier (read-only) |
| `name` | String | Name of the company type (Unique) |

### Endpoints
*   **List Company Types**: `GET /api/core/company-types/`
*   **Create Company Type**: `POST /api/core/company-types/`
*   **Retrieve Company Type**: `GET /api/core/company-types/{id}/`
*   **Update Company Type**: `PATCH /api/core/company-types/{id}/`
*   **Delete Company Type**: `DELETE /api/core/company-types/{id}/`

### Request / Response Examples

**POST /api/core/company-types/**
```json
{
    "name": "Logistics Manning"
}
```

**Response (201 Created)**
```json
{
    "id": 12,
    "name": "Logistics Manning"
}
```

---

## 3. Vessel (Ship) Types
Used by the **Ship** model to categorize vessels.

### Data Model
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Unique identifier (read-only) |
| `name` | String | Name of the vessel type (Unique) |

### Endpoints
*   **List Vessel Types**: `GET /api/core/vessel-types/`
*   **Create Vessel Type**: `POST /api/core/vessel-types/`
*   **Retrieve Vessel Type**: `GET /api/core/vessel-types/{id}/`
*   **Update Vessel Type**: `PATCH /api/core/vessel-types/{id}/`
*   **Delete Vessel Type**: `DELETE /api/core/vessel-types/{id}/`

### Request / Response Examples

**POST /api/core/vessel-types/**
```json
{
    "name": "LNG Carrier"
}
```

**Response (201 Created)**
```json
{
    "id": 12,
    "name": "LNG Carrier"
}
```

---

## Implementation Notes
*   **Authentication**: All endpoints require a valid JWT token (`Authorization: Bearer <token>`).
*   **Dynamic Creation**: In the Company and Ship serializers, providing a string name for these fields (instead of an ID) will automatically resolve the existing record or create a new one if it doesn't exist.
