# 👤 Users — API Reference

The Users section is the central registry of all individuals in the system, primarily focusing on seafarers' professional and personal data.

---

## 1. Description
This section provides complete management of user profiles. For seafarers, it stores their comprehensive "Seafarer CV" data, including contact information, physical attributes, travel documents (Passport/Seaman's Book), and professional test results (Marlins/CES). For staff, it manages roles and system permissions.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users/` | List all users with advanced filtering |
| `GET` | `/api/users/me/` | Current authenticated user profile |
| `GET` | `/api/users/{id}/` | Full profile detail of a specific user |
| `PATCH` | `/api/users/{id}/` | Update profile information |
| `DELETE` | `/api/users/{id}/` | Deactivate/Remove a user |
| `GET` | `/api/users/stats/` | User distribution by role and status |
| `GET` | `/api/users/{id}/download-passport/` | Download seafarer's passport file |
| `GET` | `/api/users/{id}/download-marlins/` | Download Marlins test certificate |

---

## 3. Endpoint Details

### 3.1 User List & Search (`GET /api/users/`)
**Description:** Retrieves a paginated list of users. Supports query parameters for deep filtering.
- **Filter Parameters:** `nationality`, `user_status`, `role`, `is_blacklisted`.
- **Response Body (200):**
```json
{
  "count": 1250,
  "next": "http://api.sakr.com/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 105,
      "email": "m.ali@example.com",
      "first_name": "Mohamed",
      "middle_name": "Ali",
      "generated_id": "202405150012",
      "nationality": "Egyptian",
      "user_status": "VACATION",
      "role": "Employee",
      "profile_image": "http://domain.com/media/profiles/m_ali.jpg"
    }
  ]
}
```

### 3.2 Current User (`GET /api/users/me/`)
**Description:** Returns basic info for the currently logged-in user.
- **Response Body (200):**
```json
{
  "id": 1,
  "email": "admin@sakr.com",
  "first_name": "System",
  "middle_name": "Admin",
  "role": "Admin",
  "cv_status": true // true if active and verified
}
```

### 3.3 User Detail (`GET /api/users/{id}/`)
**Description:** Returns the full professional and personal profile.
- **Response Body (200):**
```json
{
  "id": 105,
  "email": "m.ali@example.com",
  "first_name": "Mohamed",
  "middle_name": "Ali",
  "generated_id": "202405150012",
  "passport_no": "A12345678",
  "seaman_book_no": "SB-998877",
  "nationality": "Egyptian",
  "Height_Cm": 182,
  "Weight_Kg": 78,
  "bmi": { "value": 23.5, "category": "Normal" },
  "ranks": [
    { "rank_name": "Chief Officer", "assigned_code": "DO-2.001" }
  ],
  "certificates": [
    { "name": "Basic Safety Training", "expiry_date": "2029-12-31" }
  ]
}
```

### 3.4 Update Profile (`PATCH /api/users/{id}/`)
**Description:** Partial update of user attributes.
- **Request Body:**
```json
{
  "first_name": "Mohamed Ali",
  "phone_number": "+201098765432",
  "user_status": "ON_SITE",
  "Height_Cm": 185
}
```

### 3.5 System Statistics (`GET /api/users/stats/`)
**Description:** High-level metrics for the dashboard.
- **Response Body (200):**
```json
{
  "total_users": 1250,
  "admins": 5,
  "hr_managers": 12,
  "recruiters": 25,
  "employees": 1208,
  "active_users": 1240
}
```

### 3.6 Document Downloads (`GET /api/users/{id}/download-passport/`)
**Description:** Returns the raw file stream for the requested document.
- **Permissions:** Admin or Owner.
- **Response:** `200 OK` with `Content-Type: application/pdf` or `404 Not Found`.

---

## 4. Permissions Matrix

| Endpoint | Admin | HR Manager | Recruiter | Employee |
|---|---|---|---|---|
| `GET /api/users/` | ✅ | ✅ | ✅ | ❌ |
| `GET /api/users/me/` | ✅ | ✅ | ✅ | ✅ |
| `PATCH /api/users/{id}/`| ✅ | ✅ (Non-Admin)| ❌ | ✅ (Own) |
| `DELETE /api/users/{id}/`| ✅ | ✅ (Non-Admin)| ❌ | ❌ |
| `GET /api/users/stats/` | ✅ | ✅ | ❌ | ❌ |

---

> [!TIP]
> The `PATCH` endpoint accepts `multipart/form-data` if you need to upload a new `profile_image` or document attachments. For simple field updates, `application/json` is sufficient.
