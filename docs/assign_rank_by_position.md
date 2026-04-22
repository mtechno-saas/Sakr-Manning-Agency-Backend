# Assign Coded Rank by Position — API Documentation

> **Endpoint:** `POST /api/users/{user_id}/assign-by-position/`  
> **Access:** Admin / HR Manager only  
> **Auth:** Bearer JWT Token required

---

## Overview

This endpoint bridges the **position dropdown** (`GET /api/positions/`) with the **coded rank assignment** system.

The admin picks a position from the dropdown, sends it to this endpoint, and the system:
1. Validates the position against the known list
2. Maps it to a short rank code (`"Master"` → `"MST"`)
3. Auto-generates a unique `assigned_code` (`"MST.001"`, `"MST.002"`, …)
4. Assigns the rank to the employee

---

## Full Flow

### Step 1 — Load the Dropdown

```http
GET /api/positions/
Authorization: Bearer <token>
```

**Response `200 OK`:**
```json
[
  { "value": "Master",                                         "label": "Master" },
  { "value": "1st. Officer – Chief Off.",                      "label": "1st. Officer – Chief Off." },
  { "value": "2nd. Officer",                                   "label": "2nd. Officer" },
  { "value": "3rd. Officer",                                   "label": "3rd. Officer" },
  { "value": "Tug Master",                                     "label": "Tug Master" },
  { "value": "Boson",                                          "label": "Boson" },
  { "value": "A.B – O.S",                                      "label": "A.B – O.S" },
  { "value": "Steward / Galley Boy",                           "label": "Steward / Galley Boy" },
  { "value": "Cook / 2nd. Cook / Ass. Cook / Baker / Pastry",  "label": "Cook / 2nd. Cook / Ass. Cook / Baker / Pastry" },
  { "value": "Carpenter",                                      "label": "Carpenter" },
  { "value": "Waiter",                                         "label": "Waiter" },
  { "value": "Purser",                                         "label": "Purser" },
  { "value": "Doctor",                                         "label": "Doctor" },
  { "value": "1st. Engineer",                                  "label": "1st. Engineer" },
  { "value": "2nd. Engineer",                                  "label": "2nd. Engineer" },
  { "value": "3rd. Engineer",                                  "label": "3rd. Engineer" },
  { "value": "Electrical Engineer – E/E – ETO",                "label": "Electrical Engineer – E/E – ETO" },
  { "value": "Assistant Electrician",                          "label": "Assistant Electrician" },
  { "value": "4th. Engineer",                                  "label": "4th. Engineer" },
  { "value": "Electrician",                                    "label": "Electrician" },
  { "value": "Motor Man / Mechanic",                           "label": "Motor Man / Mechanic" },
  { "value": "Oiler",                                          "label": "Oiler" },
  { "value": "Fitter – Welder",                                "label": "Fitter – Welder" },
  { "value": "Wiper",                                          "label": "Wiper" },
  { "value": "Other",                                          "label": "Other" }
]
```

> Admin sees this list as a dropdown and selects a position — for example **"2nd. Engineer"**.

---

### Step 2 — Assign the Coded Rank

Take the `value` from the selected dropdown item and send it as the `position` field.

```http
POST /api/users/42/assign-by-position/
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "position": "2nd. Engineer"
}
```

**Response `201 Created`:**
```json
{
  "message": "Rank '2nd. Engineer' successfully assigned to Ahmed Mohamed.",
  "rank_created_in_db": true,
  "user_rank": {
    "id": 7,
    "assigned_code": "2ND_ENG.001",
    "rank_code": "2ND_ENG",
    "rank_name": "2nd. Engineer",
    "rank": {
      "id": 5,
      "code": "2ND_ENG",
      "name": "2nd. Engineer"
    }
  }
}
```

---

## Response Fields

| Field | Description |
|---|---|
| `message` | Human-readable confirmation message |
| `rank_created_in_db` | `true` if this position's rank was created for the first time, `false` if it already existed |
| `user_rank.assigned_code` | Auto-generated unique code for this user-rank (e.g. `2ND_ENG.001`) |
| `user_rank.rank_code` | Short code for the rank type (e.g. `2ND_ENG`) |
| `user_rank.rank_name` | Full name of the rank |
| `user_rank.rank` | Full nested rank object (`id`, `code`, `name`) |

---

## Position → Rank Code Mapping

| Position (from dropdown) | Rank Code | Example `assigned_code` |
|---|---|---|
| Master | `MST` | `MST.001` |
| 1st. Officer – Chief Off. | `1ST_OFF` | `1ST_OFF.001` |
| 2nd. Officer | `2ND_OFF` | `2ND_OFF.001` |
| 3rd. Officer | `3RD_OFF` | `3RD_OFF.001` |
| Tug Master | `TUG_MST` | `TUG_MST.001` |
| Boson | `BSN` | `BSN.001` |
| A.B – O.S | `AB_OS` | `AB_OS.001` |
| Steward / Galley Boy | `STW` | `STW.001` |
| Cook / 2nd. Cook / Ass. Cook / Baker / Pastry | `COOK` | `COOK.001` |
| Carpenter | `CARP` | `CARP.001` |
| Waiter | `WTR` | `WTR.001` |
| Purser | `PUR` | `PUR.001` |
| Doctor | `DOC` | `DOC.001` |
| 1st. Engineer | `1ST_ENG` | `1ST_ENG.001` |
| 2nd. Engineer | `2ND_ENG` | `2ND_ENG.001` |
| 3rd. Engineer | `3RD_ENG` | `3RD_ENG.001` |
| Electrical Engineer – E/E – ETO | `ETO` | `ETO.001` |
| Assistant Electrician | `ASS_ELC` | `ASS_ELC.001` |
| 4th. Engineer | `4TH_ENG` | `4TH_ENG.001` |
| Electrician | `ELC` | `ELC.001` |
| Motor Man / Mechanic | `MTR_MAN` | `MTR_MAN.001` |
| Oiler | `OLR` | `OLR.001` |
| Fitter – Welder | `FTR` | `FTR.001` |
| Wiper | `WPR` | `WPR.001` |
| Other | `OTH` | `OTH.001` |

> `assigned_code` auto-increments per position: first user gets `.001`, second gets `.002`, etc.

---

## Error Responses

### 400 — Missing `position` field
```json
{
  "error": "position is required.",
  "hint": "Use GET /api/positions/ to see all valid choices."
}
```

### 400 — Invalid position value
```json
{
  "error": "\"Captain\" is not a valid position.",
  "valid_positions": ["Master", "1st. Officer – Chief Off.", "..."],
  "hint": "Use GET /api/positions/ to get the full list."
}
```

### 400 — User already has this rank
```json
{
  "error": "User already has the rank \"2nd. Engineer\".",
  "existing_assigned_code": "2ND_ENG.001"
}
```

### 403 — Permission denied
```json
{
  "error": "Permission denied. Admin or HR Manager only."
}
```

### 404 — User not found
```json
{
  "error": "User not found."
}
```

---

## Frontend Integration Example

```javascript
// Step 1 — Fetch and render dropdown
const res = await fetch('/api/positions/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const positions = await res.json();

// Render as <select> — use "value" as the option value
positions.forEach(p => {
  const option = document.createElement('option');
  option.value = p.value;   // what gets sent to the API
  option.text  = p.label;   // what the admin sees
  select.appendChild(option);
});

// Step 2 — On form submit, send selected value to bridge endpoint
const selectedPosition = select.value; // e.g. "2nd. Engineer"

const result = await fetch(`/api/users/${userId}/assign-by-position/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ position: selectedPosition })
});

const data = await result.json();
console.log(data.user_rank.assigned_code); // "2ND_ENG.001"
```

---

## Key Rule

> Always send the **`value`** field from the positions dropdown — not the `label`.  
> In this API they are identical, but using `value` is the correct practice.

```
GET /api/positions/ → { "value": "2nd. Engineer", "label": "2nd. Engineer" }
                                     ↓
POST /api/users/42/assign-by-position/ → { "position": "2nd. Engineer" }
                                                          ↑
                                              send this "value" directly
```
