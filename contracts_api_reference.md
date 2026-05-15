# 📜 Contracts — API Reference

The Contracts section manages the legal and operational deployment of seafarers. It handles contract creation, digital signing, and the coordination of the seafarer's tour of duty.

---

## 1. Description
This section represents the final step in the hiring process (Step 6). It transforms a successful CV Submission into a formal employment agreement. The API ensures that seafarers are not double-booked, tracks their sign-on/sign-off dates, and manages the associated financial terms and vessel assignments.

**Key Features:**
- **Automated Generation:** Create contracts directly from CV Submissions with auto-populated client and vessel data.
- **Overlap Validation:** Built-in logic prevents scheduling a seafarer for overlapping periods on different ships.
- **Tour Management:** Tracks `sign_on_date` and `sign_off_date` to manage the crew's operational status.
- **Digital Records:** Stores signed contract files and timestamps for compliance.
- **Integration:** Directly linked to the Seafarer Application (Step 6) to gather final logistics data (Next of Kin, Medical history, etc.).

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/contracts/` | List all contracts (supports date filtering) |
| `POST` | `/api/contracts/` | Create a new contract (manually or from CV) |
| `GET` | `/api/contracts/{id}/` | Full contract detail (includes ship/user details) |
| `PATCH` | `/api/contracts/{id}/` | Update dates, salary, or status |
| `DELETE` | `/api/contracts/{id}/` | Cancel/Delete a contract |
| `GET` | `/api/contracts/stats/` | KPIs (Active contracts, sign-ons this month) |
| `POST` | `/api/contracts/{id}/generate_pdf/` | Generate the official PDF contract document |

---

## 3. Endpoint Details

### 3.1 Contract Detail (`GET /api/contracts/{id}/`)
**Description:** Returns the complete contract record, including technical ship details and the seafarer's full application profile.
- **Response Body:**
```json
{
  "id": 150,
  "user_name": "Mohamed Ali Hassan",
  "generated_id": "202405150012",
  "company_name": "Sakr Shipping",
  "ship_name": "Sakr Voyager",
  "rank_name": "Chief Officer",
  "sign_on_date": "2026-06-01",
  "sign_off_date": "2026-10-01",
  "salary": "4500.00",
  "status": "Signed",
  "ship_details": {
    "id": 22,
    "ship_name": "Sakr Voyager",
    "imo_number": "9988776",
    "ship_type": "Tanker",
    "flag": "Egypt"
  },
  "user_documents": {
    "passport": { "passport_no": "A1234567", "expiry_date": "2030-01-14", "file_url": "/media/passports/a123.pdf" },
    "seaman_book": { "seaman_book_no": "SB-9988", "expiry_date": "2028-05-20", "file_url": "/media/sb/sb99.pdf" }
  },
  "certificates": [
    { "id": 1, "name": "Basic Safety Training", "expiry_date": "2029-12-31" }
  ],
  "coded_rank": [
    { "assigned_code": "DO-2.001", "rank_name": "Chief Officer" }
  ],
  "seafarer_application": {
    "personal_details": { "nationality": "Egyptian", "birth_date": "1990-01-01", "blood_type": "O+" },
    "next_of_kin": { "full_name": "Fatima Ali", "relationship": "Wife", "phone": "+20100...", "email": "f@example.com" },
    "professional_qualification": { "coc_number": "COC-8877", "expiry_date": "2030-05-15" }
  }
}
```

### 3.2 Create Contract (`POST /api/contracts/`)
**Description:** There are two ways to create a contract: manually or by linking a successful CV Submission.
- **Request Body (From CV Submission):**
| Field | Type | Description |
|---|---|---|
| `cv_submission`| Integer | ID of the successful submission (Auto-fills user/ship/rank) |
| `sign_on_date` | Date | Expected embarkation date (`YYYY-MM-DD`) |
| `sign_off_date`| Date | Expected disembarkation date |
| `salary` | Decimal | Final agreed salary |

**Example Request:**
```json
{
  "cv_submission": 88,
  "sign_on_date": "2026-06-01",
  "sign_off_date": "2026-10-01",
  "salary": "4500.00",
  "currency": "USD"
}
```

### 3.2 Update Status & Files (`PATCH /api/contracts/{id}/`)
**Description:** Used to update the status to `Signed` or `Completed` and attach the signed document.
- **Example Request:**
```json
{
  "status": "Signed",
  "signed_at": "2026-05-15T18:35:00Z",
  "signed_file": "BASE64_OR_MULTIPART_FILE"
}
```

---

## 4. Data Modeling

### Contract Model
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Unique identifier |
| `user` | FK | The Seafarer |
| `ship` | FK | Assigned Vessel |
| `company` | FK | Client Company |
| `rank` | FK | Contracted Position |
| `sign_on_date` | Date | Embarkation |
| `sign_off_date`| Date | Disembarkation |
| `salary` | Decimal | Monthly rate |
| `status` | Choice | `Pending`, `Signed`, `Active`, `Completed`, `Cancelled` |
| `signed_file` | File | The legally signed PDF |

---

## 5. Permissions

- **Admin / HR Manager:** Full control over contract creation and financial terms.
- **Recruiter:** Can initiate contracts from successful submissions.
- **Employee (Seafarer):** Can view and download their current and past contracts.

---

> [!WARNING]
> The API will return a `400 Bad Request` if you attempt to create a contract for a seafarer whose `sign_on_date` overlaps with an existing `Active` or `Signed` contract.
