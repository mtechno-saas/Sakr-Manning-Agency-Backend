# Global API Filters Reference

This document outlines all the available query parameters (filters) you can append to the URL for `GET` requests across the different sections of the backend. 

* **Example usage:** `/api/users/?user_status=ON_SITE&nationality=Egypt`
* **Note on exact vs contains:** Fields marked as `icontains` allow partial matches (e.g. `?name=ahmed` matches "Ahmed Hassan"). Fields marked as `iexact` or `exact` require an exact match.

---

## 1. Seafarers / Users (`/api/users/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `name` | `string` | `icontains` | Searches the user's `first_name` |
| `age` | `int` | `exact` | Exact age match |
| `marital_status` | `string` | `iexact` | e.g., "SINGLE", "MARRIED" |
| `user_status` | `string` | `iexact` | e.g., "ON_SITE", "VACATION", "MEDICAL VACATION" |
| `nationality` | `string` | `icontains` | Partial match on nationality |
| `nearest_port` | `string` | `icontains` | Partial match on Nearest Port |
| `rank_name` | `string` | `icontains` | Partial match on any assigned Rank name |
| `assigned_code` | `string` | `icontains` | Partial match on UserRank assigned code |
| `role` | `string` | `iexact` | Filter by user role (e.g., "Employee", "Admin") |
| `is_blacklisted` | `boolean` | `exact` | `true` or `false` |

---

## 2. Companies (`/api/companies/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `name` | `string` | `icontains` | Partial match on company name |
| `company_type` | `string` | `iexact` | Exact match on company type |
| `status` | `string` | `iexact` | Exact match on status (e.g., "Active", "Inactive") |

---

## 3. Ships (`/api/ships/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `name` | `string` | `icontains` | Partial match on ship name |
| `imo_number` | `string` | `icontains` | Partial match on IMO number |
| `company` | `int` | `exact` | Filter ships by Company ID |
| `status` | `string` | `iexact` | Exact match on ship status (e.g., "Active") |
| `flag` | `string` | `icontains` | Partial match on Flag name |
| `ship_type` | `string` | `icontains` | Partial match on Ship Type name |

---

## 4. Job Orders (`/api/companies/job-orders/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `company` | `int` | `exact` | Filter by Company ID |
| `ship` | `int` | `exact` | Filter by Ship ID |
| `status` | `string` | `iexact` | Exact match on status (e.g., "Open", "Pending") |
| `reference_number` | `string` | `icontains` | Partial match on Job Order reference number |
| `request_date_from` | `date` | `>=` | Request date is greater than or equal to |
| `request_date_to` | `date` | `<=` | Request date is less than or equal to |

---

## 5. CV Submissions (`/api/cv-submissions/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `user` | `int` | `exact` | Filter by Seafarer (User) ID |
| `position` | `int` | `exact` | Filter by Rank ID |
| `status` | `string` | `iexact` | Exact match on status (e.g., "Approved", "Pending") |
| `submitted_date_from` | `date` | `>=` | Submitted date is greater than or equal to |
| `submitted_date_to` | `date` | `<=` | Submitted date is less than or equal to |

---

## 6. Interviews (`/api/interviews/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `candidate` | `int` | `exact` | Filter by Seafarer (User) ID |
| `company` | `int` | `exact` | Filter by Company ID |
| `status` | `string` | `iexact` | Exact match on status (e.g., "Scheduled", "Completed") |
| `scheduled_date` | `date` | `exact` | Exact scheduled date |
| `scheduled_date_from` | `date` | `>=` | Scheduled date is greater than or equal to |
| `scheduled_date_to` | `date` | `<=` | Scheduled date is less than or equal to |

---

## 7. Finance Records (`/api/finance/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `user` | `int` | `exact` | Filter by Seafarer (User) ID |
| `company` | `int` | `exact` | Filter by Company ID |
| `record_type` | `string` | `iexact` | Exact match on record type |
| `status` | `string` | `iexact` | Exact match on status |
| `start_date_from` | `date` | `>=` | Start date is greater than or equal to |
| `start_date_to` | `date` | `<=` | Start date is less than or equal to |

---

## 8. Logistics

### Flight Bookings (`/api/logistics/flights/`)
| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `user` | `int` | `exact` | Filter by Seafarer (User) ID |
| `status` | `string` | `iexact` | Exact match on booking status |
| `airline` | `string` | `icontains` | Partial match on airline name |
| `departure_date` | `date` | `exact` | Exact departure date |

### Visa Applications (`/api/logistics/visas/`)
| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `user` | `int` | `exact` | Filter by Seafarer (User) ID |
| `country` | `string` | `icontains` | Partial match on country name |
| `status` | `string` | `iexact` | Exact match on status |
| `visa_type` | `string` | `iexact` | Exact match on visa type |

### Joining Instructions (`/api/logistics/joining-instructions/`)
| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `user` | `int` | `exact` | Filter by Seafarer (User) ID |

---

## 9. Compliance

### Audits (`/api/compliance/audits/`)
| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `company` | `int` | `exact` | Filter by Company ID |
| `ship` | `int` | `exact` | Filter by Ship ID |
| `audit_type` | `string` | `iexact` | Exact match on audit type |
| `status` | `string` | `iexact` | Exact match on status |
| `audit_date_from` | `date` | `>=` | Audit date is greater than or equal to |
| `audit_date_to` | `date` | `<=` | Audit date is less than or equal to |

### Incident Reports (`/api/compliance/incident-reports/`)
| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `ship` | `int` | `exact` | Filter by Ship ID |
| `incident_type` | `string` | `iexact` | Exact match on incident type |
| `severity` | `string` | `iexact` | Exact match on severity level |
| `is_closed` | `boolean` | `exact` | `true` or `false` |
