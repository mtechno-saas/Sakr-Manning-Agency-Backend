# Create a staff account — `POST /api/users/users/create-staff/`

An **Admin** creates a new **Admin / HR Manager / Recruiter** account by passing an
email and a password. The new person signs in at `POST /api/login/` with exactly
those two values — no activation link, no shared default password, no email round-trip.

---

## Request

```http
POST /api/users/users/create-staff/
Authorization: Bearer <admin JWT>
Content-Type: application/json
```

```json
{
  "email": "new.hr@sakrshipping.com",
  "password": "at-least-8-characters",
  "role": "HR Manager",
  "first_name": "New",
  "middle_name": "Hire"
}
```

| Field | Required | Notes |
|---|---|---|
| `email` | yes | Valid email, max 100 chars. Stored **verbatim**. |
| `password` | yes | **8 characters minimum, no other rule** (no common-password / numeric / complexity checks). |
| `role` | yes | One of `Admin`, `HR Manager`, `Recruiter`. Case-insensitive: `"admin"` and `"HR"` are accepted and stored canonically. |
| `first_name` | no | Defaults to `""`. |
| `middle_name` | no | Defaults to `""`. |
| `permissions` | no | Extra permissions to grant on top of the role — e.g. `["finance.view"]`. See [user-permissions-api.md](user-permissions-api.md). An unknown key is a `400`. |

The password is **not** trimmed — if you send `" pass1234 "`, that is the password,
spaces included.

## Response — `201 Created`

```json
{
  "id": 78,
  "email": "new.hr@sakrshipping.com",
  "role": "HR Manager",
  "first_name": "New",
  "middle_name": "Hire",
  "full_name": "New Hire",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "user_status": "ON_SITE",
  "effective_user_status": "ON_SITE",
  "granted_permissions": [],
  "message": "HR Manager account created for new.hr@sakrshipping.com. The account can sign in now with the password you supplied."
}
```

The password is **never** echoed back and never written to the audit trail.

## Errors

| Status | When |
|---|---|
| `400` | Missing/malformed `email`; password shorter than 8; role not one of the three staff roles; email already used. |
| `401` | No / invalid token. |
| `403` | The caller is not an Admin (an HR Manager or Recruiter gets `403` here). |

A `400` body is the usual DRF field-error shape:

```json
{"password": ["Ensure this field has at least 8 characters."]}
{"email": ["An account with this email address already exists."]}
{"role": ["\"employee\" is not a valid choice."]}
```

## Who may call it

| Caller | Result |
|---|---|
| `Admin` | `201` — account created. |
| `HR Manager` | `403`. Minting an administrator is not delegated. |
| `Recruiter` | `403`. |
| `Employee` | `403`. |
| Anonymous | `401`. |

## Notes

- **The email is stored exactly as sent.** Login does an exact match on the email
  column, so the new person must type the same spelling. The duplicate check is
  case-*insensitive* though: `New.HR@x.com` is refused if `new.hr@x.com` exists,
  because two rows that differ only in case would leave one of them unable to log in.
- **No email is sent.** The admin chose the password and can pass it on directly.
  If the mail service is broken (it currently is — the SMTP credential is invalid),
  this endpoint does not care, because it does not depend on email.
- **New Admin accounts get `is_staff=True` and `is_superuser=True`**, matching the
  existing Admin accounts. `HR Manager` and `Recruiter` get both `False`.
- The new account is `ON_SITE` from the start — a staff role is not a "pending
  applicant".
- The creation is written to the audit trail as
  `[USER-AUDIT] action=create_staff_account actor_email=… target_email=… target_role='…'`.

## Frontend

Send the form as JSON to the URL above, then let the user sign in with the
credentials they just chose — **do not** try to read the password back out of the
response, it is not there.

```js
const { data } = await api.post("/users/users/create-staff/", {
  email: form.email,
  password: form.password,
  role: form.role,
  first_name: form.first_name,
  middle_name: form.middle_name,
});
// data.message -> show it
```

Note the base URL already carries the `/api` prefix (`services/Auth/config.js` →
`USERS: "/users/users/"`), so the axios instance resolves the call to
`/api/users/users/create-staff/`.

---

## Why this endpoint came with a permissions fix

While building this, the permission layer turned out to check **who** was writing but
never **what** they were writing. Any account with a valid JWT could reach
`POST /api/users/users/` and mint an administrator. The confirmed holes, all of which
were live on the server before this change:

| Vector | Actor | Was | Now |
|---|---|---|---|
| `POST /api/users/users/` with `role: "Admin"` | Employee | `201`, Admin created | `403` |
| `POST /api/users/users/` with `role: "admin"` | HR Manager | `201`, Admin created | `403` |
| `PATCH /api/users/users/{me}/` with `role: "Admin"` | Employee | self-promoted | `403` |
| `PATCH /api/users/users/{me}/` with `is_superuser: true` | Employee | Django superuser | `403` |
| `PATCH /api/users/users/{me}/` with `groups: [...]` | Employee | Django admin access | `403` |
| `POST /api/users/create/` with `role: "admin"` | HR Manager | `201`, Admin created | `403` |
| `POST /api/users/users/bulk-edit/` with `role: "Admin"` | HR Manager | promoted to Admin | `403` |

The root cause of the `"admin"` bypasses was that the permission layer compared the
raw payload against the literal string `"Admin"`, while the serializer normalised
`"admin"` **up** to `"Admin"` on the way in. The two layers now share one resolver
(`api/roles.py`), so they cannot disagree again.

Nothing that used to work has been broken: Admins can still create and edit anybody,
HR Managers can still create and edit non-admin accounts, and Employees can still
read and update their own profile.

## Files touched

- `api/roles.py` — **new**. One implementation of the role spellings, shared by the
  serializer and the permission layer.
- `api/serializer.py`
  - `RoleChoiceField` now delegates to `api.roles.canonical_role`.
  - `StaffAccountCreateSerializer` — **new**. The strict payload for this endpoint
    (it does not use `fields = '__all__'`, so it can never set `is_superuser`,
    `is_staff` or `groups`).
- `api/permissions.py`
  - `UserPermission` rewritten: collection-level writes denied for Employees,
    canonical role comparison for HR Managers, and a new guard on the
    authority-bearing fields (`role`, `is_superuser`, `is_staff`, `groups`,
    `user_permissions`).
  - `IsAdminRole` — **new**. Admin-only gate for this endpoint.
  - `is_admin_user()` — shared "is this caller an admin" helper.
- `api/views.py`
  - `UserViewSet.create_staff` — **new**. The endpoint.
  - `UserViewSet.get_permissions` — applies `IsAdminRole` to that one action.
  - `bulk_edit` — an HR Manager can no longer assign the Admin role, nor touch an
    Admin account.
  - `create_user` (the legacy `POST /api/users/create/` view) — canonical role
    comparison.
  - `user_detail` — an Admin-only guard on role and privilege-flag writes.
- `api/tests.py`
  - `StaffAccountCreateEndpointTests` (24 tests).
  - `PrivilegeEscalationTests` (17 tests).
