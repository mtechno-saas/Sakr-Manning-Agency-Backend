# Global Unified Search (`/api/global-search/`)

Use this endpoint to search across all platform sections (Users, Ships, Companies, CVs, and Contracts) using a single query.

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `q` | `string` | `icontains` | Search term (Min 2 chars). Searches Name, Email, Phone, IMO, Status, etc. |

---

# Module-Specific Filters

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
| `user_status` | `list` | `multiple` | Filter by user status (e.g., `?user_status=ON_SITE&user_status=VACATION`) |
| `nationality` | `list` | `multiple` | Filter by nationality (e.g., `?nationality=Egypt&nationality=Syria`) |
| `nearest_port` | `string` | `icontains` | Partial match on Nearest Port |
| `rank_name` | `string` | `icontains` | Partial match on any assigned Rank name |
| `assigned_code` | `string` | `icontains` | Partial match on UserRank assigned code |
| `role` | `list` | `multiple` | Filter by user role (e.g., `?role=Employee&role=Admin`) |
| `is_blacklisted` | `boolean` | `exact` | `true` or `false` |
| `company` | `int` | `exact` | Filter by Company ID (linked via contracts) |
| `company_name` | `string` | `icontains` | Partial match on Company Name |
| `ship` | `int` | `exact` | Filter by Ship ID (linked via contracts) |
| `ship_name` | `string` | `icontains` | Partial match on Ship Name |
| `job_position_name` | `string` | `icontains` | Partial match on Job Position name in contracts |
| `position` | `string` | `icontains` | Search by Rank name OR Application Position |
| `language` | `string` | `icontains` | Partial match on Language (e.g., "English") |
| `contract_status` | `list` | `multiple` | Filter by contract status (Supports multiple e.g. `?contract_status=Signed&contract_status=Draft`) |
| `signed_on_from` | `date` | `>=` | Contract sign-on date range start |
| `signed_on_to` | `date` | `<=` | Contract sign-on date range end |
| `signed_off_from` | `date` | `>=` | Contract sign-off date range start |
| `signed_off_to` | `date` | `<=` | Contract sign-off date range end |
| `company_type` | `string` | `icontains` | Filter by Company Type name (via contracts) |
| `ship_type` | `string` | `icontains` | Filter by Ship Type name (via contracts) |
| `passport_no` | `string` | `icontains` | Search by Passport Number |
| `passport_type` | `string` | `icontains` | Filter by Passport type (e.g., "Official", "Diplomatic") |
| `passport_expiry_from` / `to` | `date` | `range` | Passport expiry date range |
| `seaman_book_no` | `string` | `icontains` | Search by Seaman Book Number |
| `seaman_book_type` | `string` | `icontains` | Filter by Seaman Book type (e.g., "Panama", "Bahamas") |
| `seaman_book_expiry_from` / `to` | `date` | `range` | Seaman Book expiry date range |
| `document_type` | `string` | `icontains` | General search across all personal document types |
| `medical_no` | `string` | `icontains` | Search by Medical/Health Certificate Number |
| `medical_expiry_from` / `to` | `date` | `range` | Medical certificate expiry date range |
| `course_name` | `string` | `icontains` | Filter by Marine Course name |
| `document_status` | `string` | `iexact` | Filter by Document status (Pending, Active, Blacklist) |
| `document_title` | `string` | `icontains` | Search by Document title |

---

## 2. Companies (`/api/companies/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `name` | `string` | `icontains` | Partial match on company name |
| `company_type` | `list` | `multiple` | Filter by company type (e.g., `?company_type=Agency&company_type=Owner`) |
| `status` | `list` | `multiple` | Exact match on status (e.g., `?status=Active&status=Inactive`) |

---

## 3. Ships (`/api/ships/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `name` | `string` | `icontains` | Partial match on ship name |
| `imo_number` | `string` | `icontains` | Partial match on IMO number |
| `company` | `int` | `exact` | Filter ships by Company ID |
| `status` | `list` | `multiple` | Exact match on ship status (e.g., `?status=Active`) |
| `flag` | `string` | `icontains` | Partial match on Flag name |
| `ship_type` | `string` | `icontains` | Partial match on Ship Type name |

---

## 4. Job Orders (`/api/companies/job-orders/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `company` | `int` | `exact` | Filter by Company ID |
| `ship` | `int` | `exact` | Filter by Ship ID |
| `status` | `list` | `multiple` | Exact match on status (e.g., `?status=Open&status=Pending`) |
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

---

## 10. Contracts (`/api/contracts/`)

| Query Parameter | Type | Match Type | Description |
|---|---|---|---|
| `user` | `int` | `exact` | Filter by Seafarer (User) ID |
| `ship` | `int` | `exact` | Filter by Ship ID |
| `company` | `int` | `exact` | Filter by Company ID |
| `rank` | `int` | `exact` | Filter by Rank ID |
| `status` | `list` | `multiple` | Filter by contract status (e.g., `?status=Active&status=Signed`) |
| `sign_on_from` | `date` | `>=` | Sign-on date is greater than or equal to |
| `sign_on_to` | `date` | `<=` | Sign-on date is less than or equal to |
| `sign_off_from` | `date` | `>=` | Sign-off date is greater than or equal to |
| `sign_off_to` | `date` | `<=` | Sign-off date is less than or equal to |
| `applicant_name` | `string` | `icontains` | Partial match on the seafarer's first name |
