# Bug: HR Managers and Recruiters never reach `/dashboard` — they get bounced to `/quick-apply`

**Reporter:** backend (mahmoud)
**Severity:** high (a whole role tier is locked out of the product they operate)
**Frontend owner:** Karim
**Backend status:** fixed and deployed — this is a frontend-only patch
**Backend branch:** `mtechno-saas/Sakr-Manning-Agency-Backend:server-updates` @ `736a5a4e`

---

## Symptoms

1. Sign in as **HR Manager** (`amro@sakrshipping.com`) → the app throws you to
   `/quick-apply` instead of `/dashboard`.
2. Type `/dashboard` in the address bar → you are bounced to `/` (the landing page).
3. The header shows **no Dashboard link** for an HR Manager.
4. Open any CV submission → the **Admin Related Attachments**, **Generate Contract**
   and **Pipeline** sections are missing from the modal.

The backend is fine. Verified live:

```
GET /api/users/users/me/   (as amro@sakrshipping.com)
  -> role: "HR Manager"
  -> effective_user_status: "ON_SITE"
```

---

## Root cause

The dashboard is guarded by a check that only knows two role names, and it is
**duplicated in three places**.

### Gate 1 — `src/App.jsx:32-36` (this is what produced the redirect)

```jsx
/** Shared helper – keep in sync with ProtectedRoute & authService */
export const isAdminRole = (role) => {
  const r = role?.toLowerCase();
  return r === "admin" || r === "administrator";
};
```

Used at:

| Line | What it does |
|---|---|
| `src/App.jsx:63` | on auth init → `navigate("/dashboard")` else `navigate(intendedPath \|\| "/quick-apply")` |
| `src/App.jsx:83` | right after `login()` resolves → same branch |

`"HR Manager".toLowerCase()` is `"hr manager"` — it matches neither string, so
`isAdminRole()` returns `false` and the user is sent to `/quick-apply`.

### Gate 2 — `src/components/layout/ProtectedRoute.jsx:19-22` (the same helper, copy-pasted)

```jsx
const isAdminRole = (role) => {
  const r = role?.toLowerCase();
  return r === "admin" || r === "administrator";
};
```

Used at:

| Line | What it does |
|---|---|
| `src/components/layout/ProtectedRoute.jsx:49` | hard-refresh pre-check → `<Navigate to="/" />` |
| `src/components/layout/ProtectedRoute.jsx:78` | live check → `<Navigate to="/" />` |

`requiredRole="admin"` (`src/App.jsx:307` and `:315`) is only a **truthy flag** —
the string `"admin"` is never compared against anything, so it does not need to change.

### Gate 3 — `src/components/landing/layout/Header.jsx:24` (the missing Dashboard link)

```jsx
const isAdmin = ["admin", "administrator"].includes(user?.role?.toLowerCase());
```

An HR Manager never sees the Dashboard entry in the header.

### Gate 4 — `src/components/dashboard/Components/Modal/ViewModal/CVSubmissionEditModal.jsx:127`

```jsx
const isAdminOrHR = currentUser?.role === "Admin" || currentUser?.role === "HR";
```

The backend sends `"HR Manager"`, never `"HR"`. The comparison is also
case-sensitive. The three admin-only blocks below it therefore never render
for HR Managers.

### Gate 5 — `src/hooks/useAuth.js:43` (dead code, but wrong)

```jsx
requiresAdminRedirect: result.user.role?.toLowerCase() === "admin",
```

Nothing consumes this field today. Fix it anyway so it does not become a bug
the day someone wires it up.

### Gate 6 — `src/services/Auth/tokenStorage.js:115-118` (latent)

```jsx
isStoredAdmin: () => {
  const role = tokenStorage.getStoredRole();
  return role === "admin" || role === "administrator";
},
```

Currently **not called anywhere**. Fix it now so the next caller does not
reintroduce the bug.

---

## Already correct — do not touch

`src/hooks/dashboard/usePermissions.js:18-25` already handles the roles properly:

```jsx
const userRole = user?.role?.toLowerCase();
const isAdmin = userRole === "admin" || userRole === "administrator";
const isHR =
  userRole === "hr" ||
  userRole === "hr_manager" ||
  userRole === "hr manager";
const isRecruiter = userRole === "recruiter";
```

This is the file to align the rest of the app with. The bug is not that the app
cannot tell an HR Manager from an Employee — `usePermissions` does that fine.
The bug is that the **route guard** uses a much narrower list.

> `usePermissions` derives the role from the **live** user object, which
> `useAuth` re-hydrates from the API on every load (`authService.getUserRole()`
> → `GET /api/users/users/me/`). Editing `localStorage` therefore does **not**
> work around this — there is no client-side workaround. It has to be a code fix.

---

## The fix

### Step 1 — one shared helper

Create **`src/utils/roles.js`** (new file):

```js
/**
 * Canonical staff role names as returned by the backend.
 * Source of truth: api/models.py -> Users.ROLE_CHOICES / STAFF_ROLES
 *
 *   Admin | Administrator | HR Manager | HR | Recruiter
 *
 * `isStaffRole()` normalises case and spaces so "HR Manager", "hr manager"
 * and "HR_MANAGER" all match.
 */
export const STAFF_ROLES = [
  "Admin",
  "Administrator",
  "HR Manager",
  "HR",
  "Recruiter",
];

const STAFF_ROLE_KEYS = new Set(
  STAFF_ROLES.map((r) => r.toLowerCase().replace(/\s+/g, "_"))
);

/** True when the role is one of the staff roles that belong in the dashboard. */
export const isStaffRole = (role) => {
  if (!role) return false;
  return STAFF_ROLE_KEYS.has(
    String(role).toLowerCase().replace(/\s+/g, "_")
  );
};
```

### Step 2 — `src/App.jsx`

Replace the local helper (lines 32–36):

```jsx
// BEFORE
/** Shared helper – keep in sync with ProtectedRoute & authService */
export const isAdminRole = (role) => {
  const r = role?.toLowerCase();
  return r === "admin" || r === "administrator";
};

// AFTER
import { isStaffRole } from "./utils/roles";
```

Then the two call sites:

```jsx
// line 63
if (isStaffRole(user.role)) {

// line 83
if (isStaffRole(result.user.role)) {
```

> If anything else imports `isAdminRole` from `App.jsx`, keep it as a thin alias so
> the import does not break: `export const isAdminRole = isStaffRole;`

### Step 3 — `src/components/layout/ProtectedRoute.jsx`

Delete the duplicated helper (lines 19–22) and import the shared one:

```jsx
// BEFORE
const isAdminRole = (role) => {
  const r = role?.toLowerCase();
  return r === "admin" || r === "administrator";
};

// AFTER
import { isStaffRole } from "../../utils/roles";
```

Then the two call sites:

```jsx
// line 49
const storedRoleOk = isStaffRole(storedUser.role);

// line 78
const hasRole = isStaffRole(user.role);
```

### Step 4 — `src/components/landing/layout/Header.jsx`

```jsx
// BEFORE (line 24)
const isAdmin = ["admin", "administrator"].includes(user?.role?.toLowerCase());

// AFTER
const isAdmin = isStaffRole(user?.role);
```

Add the import:

```js
import { isStaffRole } from "../../../utils/roles";
```

### Step 5 — `src/components/dashboard/Components/Modal/ViewModal/CVSubmissionEditModal.jsx`

```jsx
// BEFORE (line 127)
const isAdminOrHR = currentUser?.role === "Admin" || currentUser?.role === "HR";

// AFTER
const isAdminOrHR = isStaffRole(currentUser?.role);
```

Add the import (this file sits 5 levels below `src/` — same depth as the
existing `import api from "../../../../../services/Auth/api";` on line 11):

```js
import { isStaffRole } from "../../../../../utils/roles";
```

### Step 6 — `src/services/Auth/tokenStorage.js`

```jsx
// BEFORE (lines 115-118)
isStoredAdmin: () => {
  const role = tokenStorage.getStoredRole();
  return role === "admin" || role === "administrator";
},

// AFTER
isStoredAdmin: () => {
  const role = tokenStorage.getStoredRole();
  return isStaffRole(role);
},
```

Add the import at the top of the file:

```js
import { isStaffRole } from "../../utils/roles";
```

### Step 7 — `src/hooks/useAuth.js` (dead code, fix anyway)

```jsx
// BEFORE (line 43)
requiresAdminRedirect: result.user.role?.toLowerCase() === "admin",

// AFTER
requiresAdminRedirect: isStaffRole(result.user.role),
```

```js
import { isStaffRole } from "../utils/roles";
```

---

## Backend reference (do not change)

**Roles** — `api/models.py` → `Users.ROLE_CHOICES`:

| Value | Label |
|---|---|
| `Admin` | Admin |
| `HR Manager` | HR Manager |
| `Recruiter` | Recruiter |
| `Employee` | Employee |
| `Crew` | Crew |

**Permissions** — `api/permissions.py` → `UserPermission`:

| Role | May do |
|---|---|
| `Admin` | everything |
| `HR Manager` | everything **except** creating Admins |
| `Recruiter` | read-only (`SAFE_METHODS` only) |
| `Employee` / `Crew` | read-only |

**Statuses** — `api/models.py` → `User_Status` (5 values):

`NEW_APPLICANT` · `ON_SITE` · `ON_BOARD` · `VACATION` · `MEDICAL_VACATION`

The API also accepts the human label `"MEDICAL VACATION"` (with a space) on the
`?user_status=` filter.

**Two rules that landed with the backend fix** — the frontend must agree with them:

1. **Promotion to a staff role IS the approval.** There is no "pending" state for
   staff. Admin / HR Manager / Recruiter always compute to
   `effective_user_status="ON_SITE"`, even with no contracts. Only `Employee` /
   `Crew` can be `NEW_APPLICANT`.
2. `?user_status=NEW_APPLICANT` on `GET /api/users/users/` returns **only**
   employees — staff are excluded. `?user_status=ON_SITE` returns the staff +
   on-site seafarers.

**Read `effective_user_status` for display, `user_status` for writes.** The API
exposes both: `effective_user_status` is the computed status, `user_status` is
the raw stored override and is what the write path accepts.

---

## Acceptance

- [ ] Sign in as **HR Manager** → lands on `/dashboard`, not `/quick-apply`
- [ ] Sign in as **Recruiter** → lands on `/dashboard`
- [ ] Sign in as **Admin** → still lands on `/dashboard`
- [ ] Type `/dashboard` as HR Manager → stays there
- [ ] Hard-refresh `/dashboard` as HR Manager → no bounce to `/` or `/auth`
- [ ] Header shows the **Dashboard** link for an HR Manager
- [ ] Sign in as **Employee** → still lands on `/quick-apply`, `/dashboard` still redirects to `/`
- [ ] Open a CV submission as HR Manager → **Admin Related Attachments**,
      **Generate Contract** and **Pipeline** are all visible
- [ ] An HR Manager can still NOT create an Admin (the backend returns 403 and the
      UI must not offer the control)

---

## Files to change

| # | File | Change |
|---|---|---|
| 1 | `src/utils/roles.js` | **new** — shared `STAFF_ROLES` + `isStaffRole()` |
| 2 | `src/App.jsx` | 32–36, 63, 83 |
| 3 | `src/components/layout/ProtectedRoute.jsx` | 19–22, 49, 78 |
| 4 | `src/components/landing/layout/Header.jsx` | 24 + import |
| 5 | `src/components/dashboard/Components/Modal/ViewModal/CVSubmissionEditModal.jsx` | 127 + import |
| 6 | `src/services/Auth/tokenStorage.js` | 115–118 + import |
| 7 | `src/hooks/useAuth.js` | 43 + import |

Optional but recommended: grep the codebase for any other hard-coded role
comparison that misses `"HR Manager"` or `"Recruiter"`:

```bash
grep -rn 'toLowerCase() === "admin"\|=== "HR"\|=== '"'"'HR'"'"'\|"admin", "administrator"' src/
grep -rn "isAdminRole" src/
```

There should be exactly one role helper in the app after this change, and it
should be `src/utils/roles.js`.
