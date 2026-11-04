# Extra permissions for a staff account

An **Admin** can hand an **HR Manager** or a **Recruiter** extra access on top of what
their role already gives them — "this HR may also see the finance records", "this
Recruiter may also manage users".

This is the follow-up step to `POST /api/users/users/create-staff/`: create the account,
then decide what it may do. Both steps can also be done in **one call** (see
[Doing it in one call](#doing-it-in-one-call)).

---

## The model in one paragraph

Access has two layers:

1. **The role** — `Admin`, `HR Manager`, `Recruiter`, `Employee`, `Crew`. This is the
   baseline and it never changes because of a grant.
2. **Extra permissions** — a list of keys attached to one account
   (`granted_permissions`). A grant **widens** the role.

The rules:

- **Additive only.** A grant adds access; it never removes it. To narrow somebody,
  change their role.
- **A grant never grants a role.** `users.write` lets an account *edit* people; it can
  never change anybody's `role`.
- **A grant never grants account creation.** Creating accounts stays Admin / HR Manager.
- **A grant never grants the authority flags** (`is_superuser`, `is_staff`, Django
  groups) — those stay Admin-only.
- **Admins are unaffected.** They already have everything.

---

## 1. What can be granted

`GET /api/users/users/permission-catalog/`

```http
GET /api/users/users/permission-catalog/
Authorization: Bearer <admin JWT>
```

```json
{
  "permissions": [
    {
      "key": "certificates.write",
      "resource": "certificates",
      "level": "write",
      "label": "Manage certificates",
      "description": "Create, edit and delete certificates."
    },
    {
      "key": "finance.view",
      "resource": "finance",
      "level": "view",
      "label": "See all finance records",
      "description": "See every finance record, not only their own."
    }
  ],
  "resources": ["certificates", "companies", "contracts", "cv_submissions", "finance", "interviews", "job_orders", "users"]
}
```

Admin only (`403` otherwise). Render this list as checkboxes — the label and
description are written for a non-technical admin.

### The full list

| Key | What it opens |
|---|---|
| `users.view_all` | See every account in the list, not just their own profile. |
| `users.write` | Edit other people's accounts. **Never** changes anyone's role. |
| `users.delete` | Delete other people's accounts. |
| `contracts.view` | See every contract, not only their own. |
| `contracts.write` | Create, edit and delete contracts. |
| `companies.view` | See every company record. |
| `companies.write` | Create, edit and delete companies. |
| `interviews.view` | See every interview, not only their own. |
| `interviews.write` | Create, edit and delete interviews. |
| `finance.view` | See every finance record, not only their own. |
| `finance.write` | Create, edit and delete finance records. |
| `cv_submissions.view` | See every CV submission, not only their own. |
| `cv_submissions.write` | Create, edit and delete CV submissions. |
| `certificates.view` | See every certificate. |
| `certificates.write` | Create, edit and delete certificates. |
| `job_orders.view` | See every job order. |
| `job_orders.write` | Create, edit and delete job orders. |

A `write` key always implies the matching `view` key.

---

## 2. Read the grants of one account

`GET /api/users/users/{id}/permissions/`

```json
{
  "id": 78,
  "email": "new.hr@sakrshipping.com",
  "role": "HR Manager",
  "granted_permissions": ["finance.view", "contracts.write"]
}
```

Admin only.

---

## 3. Set the grants of one account

`PATCH /api/users/users/{id}/permissions/`

```json
{
  "permissions": ["finance.view", "contracts.write"]
}
```

The list **replaces** whatever was there before. Send `[]` to clear it.

```json
{
  "id": 78,
  "email": "new.hr@sakrshipping.com",
  "role": "HR Manager",
  "granted_permissions": ["finance.view", "contracts.write"],
  "message": "Permissions updated for new.hr@sakrshipping.com: finance.view, contracts.write."
}
```

| Status | When |
|---|---|
| `200` | Set. |
| `400` | Unknown permission key; `permissions` missing or not a list; the target is not a staff account. |
| `401` | No / invalid token. |
| `403` | The caller is not an Admin. |

Only staff accounts (`Admin`, `HR Manager`, `Recruiter`) can carry grants — setting them
on an Employee is a `400`.

An unknown key is an **error**, not a silent no-op, so a typo in the frontend cannot
look like a successful grant:

```json
{
  "error": "Unknown permission(s): finance.teleport",
  "valid_permissions": ["certificates.write", "certificates.view", "..."]
}
```

Every change is written to the audit trail as
`[USER-AUDIT] action=set_permissions actor_email=… target_email=… permissions=[…]`.

---

## Doing it in one call

`POST /api/users/users/create-staff/` accepts the same list, so creating an HR **and**
giving it access is a single request:

```json
{
  "email": "new.hr@sakrshipping.com",
  "password": "at-least-8-characters",
  "role": "HR Manager",
  "permissions": ["finance.view"]
}
```

The response includes `"granted_permissions": ["finance.view"]`.

---

## What the frontend will see

Every user object now carries a `granted_permissions` field (an array of strings, empty
when there are none):

```json
{
  "id": 78,
  "email": "new.hr@sakrshipping.com",
  "role": "HR Manager",
  "granted_permissions": ["finance.view"]
}
```

Show it as a badge or a small chip next to the role, e.g. `HR Manager · +1 permission`.

### The signed-in user's own grants

Both "me" endpoints report the grants of the **caller**, so the frontend can work out
what the logged-in person may do without a second request:

```
GET /api/users/users/me/     -> { id, email, first_name, middle_name, profile_image,
                                 role, cv_status, granted_permissions }
GET /api/users/me/           -> { id, email, ..., role, user_status,
                                 granted_permissions }
```

An account with no grants reports `"granted_permissions": []` — never `null`, so no null
check is needed.

### Example

```js
// 1. what can be granted?
const { data: cat } = await api.get("/users/users/permission-catalog/");

// 2. what does this account have?
const { data: current } = await api.get(`/users/users/${userId}/permissions/`);

// 3. save the admin's selection
await api.patch(`/users/users/${userId}/permissions/`, {
  permissions: selectedKeys,
});
```

Note the axios base URL already carries the `/api` prefix
(`services/Auth/config.js` → `USERS: "/users/users/"`), so the calls resolve to
`/api/users/users/...`.

---

## Files touched

- `api/capabilities.py` — **new**. The catalogue of grantable permissions and the
  `granted()` / `can_view()` / `can_write()` helpers.
- `api/models.py` — `Users.granted_permissions` (a JSON list, default `[]`).
- `api/migrations/0077_users_granted_permissions.py` — **new**.
- `api/permissions.py`
  - Each role-gated permission class now honours the matching grant:
    `UserPermission`, `ContractPermission`, `CompanyPermission`,
    `InterviewPermission`, `FinancePermission`, `CVPermission`,
    `IsHROrReadOnly` (certificates) and `JobOrderPermission`.
  - `granted_permissions` joins `role`, `is_superuser`, `is_staff`, `groups` and
    `user_permissions` as an authority-bearing field: only an Admin may write it, on
    any path.
  - `privilege_fields_in_payload()` — a **create** has no object to compare against,
    so anything that would hand a new account authority is now refused for
    non-Admins.
- `api/serializer.py`
  - `UsersSerializer.granted_permissions` — read/write, validated against the
    catalogue.
  - `UserMeSerializer.granted_permissions` — read-only, so the signed-in account can
    see its own grants.
  - `StaffAccountCreateSerializer` accepts an optional `permissions` list.
- `api/views.py`
  - `UserViewSet.permission_catalog` — **new** (`GET .../permission-catalog/`).
  - `UserViewSet.set_permissions` — **new** (`GET|PATCH .../{id}/permissions/`).
  - `UserViewSet.get_queryset` honours `users.view_all`.
  - `MeView`'s profile dict reports `granted_permissions`.
  - The legacy `POST /api/users/create/` view now refuses privilege fields from
    non-Admins — it used to let an HR Manager create a Django superuser.
- `api/tests.py`
  - `GrantedPermissionsTests` (34 tests).
