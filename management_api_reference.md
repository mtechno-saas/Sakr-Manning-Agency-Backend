# 👥 Management — API Reference

The Management section is the operational core of the system. it handles the relationships with **Companies** (Shipowners/Managers), the tracking of their **Ships**, and the processing of **Job Orders** (Manpower Requests).

---

## 1. Description
This section allows administrators to build the operational framework of the agency. It tracks client details, vessel technical specifications, and current manpower demands. It serves as the source of truth for where seafarers are deployed and which positions need to be filled.

**Key Components:**
- **Companies:** Profile management for client entities and their financial terms.
- **Ships:** Detailed technical records for vessels, including crew lists and IMO tracking.
- **Job Orders:** Formal requests from clients specifying how many seafarers of which rank are needed for a specific ship.

---

## 2. Endpoints Summary

### 🏢 Companies
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/companies/` | List all companies |
| `POST` | `/api/companies/` | Register a new company |
| `GET` | `/api/companies/{id}/` | Full company profile (includes linked ships) |
| `PATCH` | `/api/companies/{id}/` | Update company details |
| `GET` | `/api/companies/stats/` | KPIs (Active companies, total open positions) |

### 🚢 Ships
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/ships/` | List all vessels |
| `POST` | `/api/ships/` | Register a new vessel |
| `GET` | `/api/ships/{id}/` | Ship technical details + current crew list |
| `PATCH` | `/api/ships/{id}/` | Update ship specs or crew assignments |

### 📋 Job Orders & Positions
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/companies/job-orders/` | List all manpower requests |
| `POST` | `/api/companies/job-orders/` | Create a new job order |
| `GET` | `/api/companies/job-positions/` | List specific rank requirements |
| `POST` | `/api/companies/job-positions/` | Define a new rank requirement for an order |

---

## 3. Endpoint Details

### 3.1 Company Detail (`GET /api/companies/{id}/`)
**Description:** Returns full company info, including calculated stats for open positions and a nested list of all ships belonging to this company.
- **Response Body:**
```json
{
  "id": 5,
  "company_name": "Sakr Shipping Co.",
  "company_type_name": "Ship Owner",
  "contact_email": "ops@sakrshipping.com",
  "open_positions": 12, // Calculated total across all job orders
  "open_position_names": [
    { "id": 7, "name": "Chief Officer", "count": 2 },
    { "id": 10, "name": "Oiler", "count": 5 }
  ],
  "ships": [
    { "id": 22, "ship_name": "Sakr Express", "imo_number": "9123456", "status": "Active" }
  ]
}
```

### 3.2 Ship Registration (`POST /api/ships/`)
**Description:** Create a new vessel record.
- **Request Body:**
| Field | Type | Description |
|---|---|---|
| `ship_name` | String | Name of the vessel |
| `imo_number`| String | Unique 7-digit IMO number |
| `company` | Integer| ID of the parent Company |
| `ship_type` | Mixed | VesselType ID or Name (e.g. "Container Ship") |
| `flag` | Mixed | Flag ID or Name (e.g. "Panama") |
| `crew_ids` | List | Optional: IDs of users to assign to this ship |

#### `POST /api/ships/` — Create Ship
**Request:**
```json
{
  "ship_name": "Sakr Voyager",
  "imo_number": "9988776",
  "company": 3,
  "ship_type": "Tanker",
  "flag": "Egypt",
  "deadweight": 50000,
  "year_built": 2022,
  "crew_ids": [45, 12, 88]
}
```

**Response (201):**
```json
{
  "id": 14,
  "ship_name": "Sakr Voyager",
  "imo_number": "9988776",
  "ship_type": 4,
  "ship_type_name": "Tanker",
  "flag": 1,
  "flag_name": "Egypt",
  "company": 3,
  "status": "Active",
  "crew": [
    { "id": 45, "first_name": "Ahmed", "middle_name": "Hassan", "email": "ahmed@example.com" },
    { "id": 12, "first_name": "Mohamed", "middle_name": "Ali", "email": "mali@example.com" }
  ],
  "official_no": null,
  "call_sign": null,
  "deadweight": 50000,
  "year_built": 2022,
  "job_orders": [],
  "jobs_order_count": 0
}
```

#### `POST /api/companies/job-positions/` — Add Rank to Order
**Request:**
```json
{
  "job_order": 12,
  "rank": "Chief Officer", // Can be ID (7) or Name ("Chief Officer")
  "quantity": 2,
  "salary_min": "3500.00",
  "salary_max": "4200.00",
  "currency": "USD",
  "contract_duration_months": 4,
  "remarks": "Must have experience on VLCC tankers."
}
```

**Response (201):**
```json
{
  "id": 55,
  "job_order": 12,
  "rank": 7,
  "rank_name": "Chief Officer",
  "quantity": 2,
  "salary_min": "3500.00",
  "salary_max": "4200.00",
  "currency": "USD",
  "contract_duration_months": 4,
  "remarks": "Must have experience on VLCC tankers."
}
```


---

## 4. Data Modeling

### 🚢 Ship Model (Technical Specs)
| Field | Type | Description |
|---|---|---|
| `ship_name` | String | Vessel Name |
| `imo_number` | String | Unique IMO ID |
| `crew` | M2M | Current seafarers assigned to the ship |
| `gross_tonnage`| Int | GRT |
| `deadweight` | Int | DWT (Metric Tons) |
| `engine_type` | String | Engine Make/Model |
| `engine_power_kw`| Int | Total KW |

### 📋 Job Order Position
| Field | Type | Description |
|---|---|---|
| `rank` | FK | The rank code required (e.g. Master) |
| `quantity` | Int | Number of seafarers needed |
| `salary_min` | Decimal| Minimum budget |
| `salary_max` | Decimal| Maximum budget |
| `duration` | Int | Contract length in months |

---

## 5. Permissions

- **Admin:** Full CRUD access to all management models.
- **HR Manager / Recruiter:** Can view and edit companies, ships, and job orders. Cannot delete core company/ship records in some restricted configurations.
- **Employee:** Read-only access to their assigned Ship profile and basic Company info.

---

> [!TIP]
> When creating a `JobOrderPosition`, you can pass the rank name (e.g. `"rank": "Chief Officer"`) instead of the ID, and the API will automatically resolve it to the correct internal Rank ID.
