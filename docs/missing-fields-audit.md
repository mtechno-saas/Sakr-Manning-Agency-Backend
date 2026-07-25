# Missing Fields Audit — Sakr Companies & Interviews API

**Generated:** 2026-07-14
**Scope:** Fields requested by the frontend that were not present in the backend response, and the migrations created to add them.

This document covers **4 endpoints** across 2 Django apps. Every section follows the same structure: the fields added, the migration that creates them, the model/serializer files touched, a sample API payload, and the frontend mapping required.

---

## Endpoint 1: `GET / PATCH /api/companies/{id}/`  *(Company Detail)*

### Fields Added

| # | Field Name | API Key | Type | Required | Max Length | UI Label | Example |
|---|---|---|---|---|---|---|---|
| 1 | Postal address | `address` | `string` (long) | No | unlimited | Address | `"12 El Horreya St, Alexandria, Egypt"` |
| 2 | Primary contact name | `contact_person` | `string` | No | 200 | Contact Person | `"Capt. Hassan Mohamed"` |
| 3 | Alternative phone | `alt_phone` | `string` | No | 50 | Alt Phone | `"+20 100 123 4567"` |
| 4 | Internal notes | `notes` | `string` (long) | No | unlimited | Notes | `"Preferred vendor. WhatsApp only."` |

**Migration:** `companies/migrations/0013_company_address_contact_person_alt_phone_notes.py`
**Model file:** `companies/models.py` (Company class, after `owner`)
**Serializer:** `companies/serializers.py` (no change — auto-included via `fields = '__all__'`)

### Sample Response (after migration applied)

```json
{
  "id": 7,
  "company_name": "Maersk Line Egypt",
  "contact_person": "Capt. Hassan Mohamed",
  "alt_phone": "+20 100 123 4567",
  "address": "12 El Horreya St, Alexandria, Egypt",
  "notes": "Preferred vendor. WhatsApp only.",
  "company_type": "Owner",
  "status": "Active",
  "contact_email": "ops@maersk.com",
  "contact_phone": "+201234567890",
  "owner": "Capt. Hassan",
  "website": "https://maersk.com",
  "company_flag": 3,
  "company_flag_name": "Egypt",
  "hourly_rate": "45.00",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2025-07-01T14:22:00Z",
  "ships": [...],
  "open_positions": 12,
  "open_position_names": [...]
}
```

### Frontend Mapping Required

- Add 4 new inputs in the **Company form** bound to the API keys above
- Display the values in the **Company detail/list views**
- All four are optional — send `null` or omit the key on POST/PATCH
- `address` and `notes` are unbounded text — use `<textarea>` inputs in the form
- `contact_person` and `alt_phone` are short strings — use single-line `<input type="text">`

---

## Endpoint 2: `GET / PATCH /api/companies/job-positions/{id}/`  *(Job Position Detail)*

### Fields Added

| # | Field Name | API Key | Type | Required | Auto-managed | UI Label | Format |
|---|---|---|---|---|---|---|---|
| 1 | Creation timestamp | `created_at` | `datetime` (ISO 8601) | auto | yes (server) | Created | `"2026-07-14T10:16:00Z"` |
| 2 | Last-update timestamp | `updated_at` | `datetime` (ISO 8601) | auto | yes (server) | Updated | `"2026-07-14T10:16:00Z"` |

**Migration:** `companies/migrations/0014_joborderposition_created_at_and_more.py`
**Model file:** `companies/models.py` (JobOrderPosition class, after `remarks`)
**Serializer:** `companies/serializers.py` (no change — auto-included via `fields = '__all__'`)

### Sample Response (after migration applied)

```json
{
  "id": 42,
  "job_order": 7,
  "rank": 4,
  "rank_name": "Chief Officer",
  "quantity": 1,
  "salary_min": "3000.00",
  "salary_max": "4500.00",
  "currency": "USD",
  "contract_duration_months": 6,
  "remarks": "Urgent hire",
  "status": "Open",
  "company_name": "Maersk Line Egypt",
  "ship_name": "Maersk Horizon",
  "filled_slots": 0,
  "remaining_slots": 1,
  "assigned_to": [],
  "created_at": "2026-07-14T10:16:00Z",
  "updated_at": "2026-07-14T10:16:00Z"
}
```

### Frontend Mapping Required

- Add a **"Created"** column in the job-positions table/list mapped to `created_at`
- (Optional) Add an **"Updated"** column mapped to `updated_at`
- **Do NOT send** these fields in POST/PATCH — they are read-only on the API. The server auto-fills them on create and update respectively.
- Existing rows were backfilled with the migration timestamp; new rows will get the real creation time automatically.

---

## Endpoint 3: `POST / GET / PATCH / DELETE /api/reminders/`  *(now in its own `reminders` app)*

A `Reminder` resource exposed at `/api/reminders/`. Was originally added to the `interviews` app on 2026-07-14, then moved to its own `reminders` app on 2026-07-25 for better separation. See `docs/reminders-app.md` for the full app reference.

### Fields Added (new `Reminder` model)

| # | Field Name | API Key | Type | Required | UI Label | Example |
|---|---|---|---|---|---|---|
| 1 | Crew member (user) | `user` | `integer` (FK to `Users`) | Yes | Crew Member Name | `42` |
| 2 | Reminder message | `text` | `string` (long) | Yes | Reminder | `"Call Capt. Hassan about medicals"` |
| 3 | Reminder date | `reminder_date` | `date` (YYYY-MM-DD) | Yes | Date | `"2026-07-20"` |
| 4 | Reminder time | `reminder_time` | `time` (HH:MM:SS) | Yes | Time | `"14:30:00"` |
| 5 | Completion flag | `is_completed` | `boolean` | No (default `false`) | — | `false` |
| 6 | Created at | `created_at` | `datetime` (ISO 8601) | auto (server) | — | `"2026-07-14T11:00:00Z"` |
| 7 | Updated at | `updated_at` | `datetime` (ISO 8601) | auto (server) | — | `"2026-07-14T11:00:00Z"` |

### Computed Fields (read-only)

| Field | Type | Source | Purpose |
|---|---|---|---|
| `user_name` | `string` | `user.get_full_name()` | Display name of the assigned crew member |
| `user_email` | `string` | `user.email` | Email of the assigned crew member |

### Available HTTP Methods

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/api/reminders/` | List all visible reminders | Bearer JWT |
| POST | `/api/reminders/` | Create a new reminder | Bearer JWT |
| GET | `/api/reminders/{id}/` | Retrieve one reminder | Bearer JWT |
| PUT | `/api/reminders/{id}/` | Full update | Bearer JWT |
| PATCH | `/api/reminders/{id}/` | Partial update | Bearer JWT |
| DELETE | `/api/reminders/{id}/` | Delete a reminder | Bearer JWT |
| GET | `/api/reminders/upcoming/` | List upcoming, not-completed reminders (custom action) | Bearer JWT |

### Authorization Rules

- **Admin / HR Manager / Recruiter** — sees and manages every reminder
- **Any other authenticated user** — sees only their own reminders (`user == request.user`)

**Migration:** `interviews/migrations/0002_reminder.py`
**Model file:** `interviews/models.py` (new `Reminder` class)
**Serializer file:** `interviews/serializers.py` (new `ReminderSerializer`)
**View file:** `interviews/views.py` (new `ReminderViewSet`)
**URL file:** `interviews/urls.py` (router register `r'reminders'`)

### Sample Request (POST)

```http
POST /api/reminders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user": 42,
  "text": "Call Capt. Hassan about medicals",
  "reminder_date": "2026-07-20",
  "reminder_time": "14:30:00"
}
```

### Sample Response (GET single)

```json
{
  "id": 7,
  "user": 42,
  "user_name": "Capt. Hassan Mohamed",
  "user_email": "hassan@example.com",
  "text": "Call Capt. Hassan about medicals",
  "reminder_date": "2026-07-20",
  "reminder_time": "14:30:00",
  "is_completed": false,
  "created_at": "2026-07-14T11:00:00Z",
  "updated_at": "2026-07-14T11:00:00Z"
}
```

### Frontend Mapping Required

- Add 4 inputs in the **Add Reminder** modal mapped to `user`, `text`, `reminder_date`, `reminder_time`
- Send the user as the integer `id` (not the name string)
- Send dates as `YYYY-MM-DD`, times as `HH:MM:SS` (or `HH:MM`)
- Use `/api/reminders/` for create, list, and delete
- Use `/api/reminders/upcoming/` if you want a "today and later" feed
- Optionally display `is_completed` with a checkbox to mark reminders done (PATCH `{"is_completed": true}`)

---

## Endpoint 4: `POST / GET / PATCH / DELETE /api/interviews/`  *(Interview Detail)*

Fields added to the existing `Interview` model — this endpoint already existed; the new fields expand what the UI can show/save.

### Fields Added (model)

| # | Field Name | API Key | Type | Required | UI Label | Example |
|---|---|---|---|---|---|---|
| 1 | Principal (Company) | `principal` | `integer` (FK to `companies.Company`) | No | Principal | `12` |
| 2 | Position | `position` | `string` | No | Position | `"Chief Officer"` |
| 3 | Interview type | `type` | `string` (choice) | No | Type | `"Video"` |
| 4 | Duration | `duration_minutes` | `integer` | No | Duration (min) | `30` |
| 5 | Location | `location` | `string` | No | Location | `"Zoom"` |
| 6 | Result | `result` | `string` (choice) | No | Result | `"Pass"` |
| 7 | Feedback | `feedback` | `string` (long) | No | Feedback | `"Strong communicator."` |

### Computed Fields Added (serializer, read-only)

| Field | Type | Source | UI Label | Purpose |
|---|---|---|---|---|
| `candidate_email` | `string` | `candidate.email` | Candidate Email | Flat email of the candidate |
| `interviewer_email` | `string` | `interviewer.email` | Interviewer Email | Flat email of the interviewer |

### Choice Values

**`type`** must be one of:
- `"Phone"`
- `"Video"`
- `"In-Person"`

**`result`** must be one of:
- `"Pending"`
- `"Pass"`
- `"Fail"`
- `"Hold"`

**Migration:** `interviews/migrations/0003_interview_more_fields.py`
**Depends on:** `interviews.0002_reminder`, `companies.0014_joborderposition_created_at_and_more`
**Model file:** `interviews/models.py` (Interview class)
**Serializer file:** `interviews/serializers.py` (InterviewSerializer)

### Date / Time Note (Option A — single DateTimeField)

`date` stays as a single `DateTimeField` on the backend. The frontend splits it for the **Date** and **Time** columns using JavaScript:

```js
const d = new Date(interview.date);
const dateStr = d.toISOString().slice(0, 10);   // "2026-07-20"
const timeStr = d.toTimeString().slice(0, 5);   // "14:30"
```

Send `date` on POST/PATCH as ISO 8601: `"2026-07-20T14:30:00Z"`.

### Sample Request (POST)

```http
POST /api/interviews/
Authorization: Bearer <token>
Content-Type: application/json

{
  "candidate": 42,
  "interviewer": 7,
  "principal": 12,
  "position": "Chief Officer",
  "type": "Video",
  "duration_minutes": 30,
  "location": "Zoom",
  "date": "2026-07-20T14:30:00Z",
  "status": "Scheduled",
  "result": "Pending",
  "feedback": "",
  "link": "https://zoom.us/j/123",
  "notes": "First round screening"
}
```

### Sample Response (GET single)

```json
{
  "id": 23,
  "candidate": 42,
  "candidate_details": { "id": 42, "first_name": "Hassan", "last_name": "Mohamed", "email": "hassan@example.com" },
  "candidate_email": "hassan@example.com",
  "interviewer": 7,
  "interviewer_details": { "id": 7, "first_name": "Sara", "last_name": "Ali", "email": "sara@example.com" },
  "interviewer_email": "sara@example.com",
  "principal": 12,
  "position": "Chief Officer",
  "type": "Video",
  "duration_minutes": 30,
  "location": "Zoom",
  "date": "2026-07-20T14:30:00Z",
  "status": "Scheduled",
  "result": "Pending",
  "feedback": "",
  "notes": "First round screening",
  "link": "https://zoom.us/j/123",
  "created_at": "2026-07-14T11:00:00Z",
  "updated_at": "2026-07-14T11:00:00Z"
}
```

### Frontend Mapping Required

- Add inputs/columns for the 7 new fields: `principal`, `position`, `type`, `duration_minutes`, `location`, `result`, `feedback`
- Use the flat `candidate_email` and `interviewer_email` instead of digging into `candidate_details` / `interviewer_details`
- Split the single `date` DateTimeField into separate Date and Time inputs on the form (and join them back into ISO 8601 before POST/PATCH)
- Render `type` and `result` as dropdowns with the choice values listed above
- Send `principal` as integer id (not company name)

---

## Frontend Updates — Saved Filter Management (Interviews Page)

These are **UI feature additions** for the **SAVED VIEWS** panel in the Interviews page filter sidebar. No backend changes are required — the saved views are stored locally (React state / `localStorage`); there is no `SavedView` or `SavedFilter` model in the backend.

**Related files (frontend):**
- `src/components/dashboard/Components/Common/SavedFilters.jsx` — main saved-filters chip row at the top of the data table (already has a delete button via `Trash2` icon, but no rename)
- `src/components/dashboard/Components/Common/EnhancedFilterModel.jsx` — right-hand filter sidebar where the **SAVED VIEWS** section is rendered
- `src/components/dashboard/Components/Common/FilterModel.jsx` — alternate / older filter sidebar implementation
- `src/components/dashboard/Components/Common/ConfirmDialog.jsx` — confirm dialog component (already exists, reuse for delete)

### Feature 1: Delete Saved Filter

**Where it lives:** Next to each saved view in the **SAVED VIEWS** list, add a small delete icon (trash / `X`).

**Behavior:**
- Hover the saved view row → reveal the delete icon (e.g. `Trash2` from `lucide-react`, same icon used in `SavedFilters.jsx`)
- Click the delete icon → open the existing `ConfirmDialog` with the message: *"Delete saved view "<name>"? This cannot be undone."*
- On confirm → remove the entry from the saved-views state (and `localStorage` if persisted) and re-render the list
- On cancel → close the dialog, no state change

**Acceptance criteria:**
- [ ] Each saved view has a visible-on-hover delete icon
- [ ] Clicking delete opens a confirmation dialog (does not delete immediately)
- [ ] After confirm, the saved view disappears from the list and the active filters are **not** changed
- [ ] The state persists across page reloads (if `localStorage` is the storage layer)

**Existing reference code:** `SavedFilters.jsx` lines 102–131 already implement a delete button (calls `onDeletePreset(preset.name)`). The implementation in the sidebar should mirror this pattern.

### Feature 2: Rename Saved Filter

**Where it lives:** Each saved view row in the **SAVED VIEWS** list.

**Behavior — Option A (inline edit, recommended):**
- Click on the saved view's name → it becomes an editable `<input>` pre-filled with the current name
- Press **Enter** or click outside → save the new name
- Press **Escape** → cancel and revert to the old name
- The bookmark icon stays to the left of the name throughout

**Behavior — Option B (modal):**
- Click a small pencil/edit icon next to the saved view → open a modal with a single text input pre-filled with the current name
- Save button → commits, modal closes
- Cancel button → closes without saving

**Validation:**
- Name must be non-empty (trim before submit)
- Name must be unique within the user's saved views (case-insensitive)
- Max length: 50 characters
- If validation fails, show a small inline error message under the input

**State changes:**
- Update the entry's `name` field in the saved-views state
- Persist to `localStorage` (or wherever the saved views are stored)
- If the renamed view is currently the **active** filter set, the active filters themselves do **not** change — only the display name

**Acceptance criteria:**
- [ ] User can trigger rename by clicking the name (Option A) or a dedicated icon (Option B)
- [ ] Empty or whitespace-only names are rejected
- [ ] Duplicate names are rejected with a clear error
- [ ] Successful rename persists across page reloads
- [ ] Pressing Escape cancels the rename

### Storage Layer Note

If saved views are currently in `localStorage` under a key like `interviews:savedViews`, the shape of each entry is `{ name, filters }`. The rename operation updates the `name` field in place — the `filters` object stays the same. The delete operation removes the entry from the array.

If the data lives in React state only (no persistence), the changes still apply but won't survive a page refresh — recommend adding `localStorage` sync in the same change.

### API / Backend

**No backend changes are required for either feature.** The backend has no `SavedView` or `SavedFilter` model; saved views are 100% client-side. If you later want them to sync across devices, that would need a new model + endpoint — not in scope for this update.

---

## Frontend Updates — Convert Settings Side Panel to Full-Screen Page

The current Settings UI is implemented as a **slide-out side panel** (drawer from the right edge). The requirement is to convert it into a **full-screen page** so settings are easier to manage (more room for forms, tables, and dropdown management — see the cramped dropdown list in the current screenshot).

**Related file (frontend):**
- `src/components/dashboard/Components/Modal/SettingsSidePanel.jsx` — currently a 36 KB side-drawer component, 1 file contains all 5 tabs

### Current State (side panel)

- Root container: `fixed inset-y-0 right-0 z-[210] w-full max-w-2xl ... transform transition-transform`
- Backdrop: `fixed inset-0 z-[200] bg-slate-900/40 backdrop-blur-sm` (clicking it closes the panel)
- Close button: top-right `X` icon that calls `onClose`
- Max content width: `672px` (Tailwind `max-w-2xl`)
- The page sidebar (left nav) remains visible behind the panel
- No URL changes — opening settings does not change the route

### Target State (full-screen page)

- Root container: `fixed inset-0 w-full h-full` (or `w-screen h-screen`) — covers the whole viewport
- **No backdrop overlay** — replace with normal page chrome
- Sidebar (left nav) may stay visible, but the Settings content fills the rest of the viewport
- Each tab becomes a real page section (or a sub-route if you want deep-linking)
- Add a real route: `/dashboard/settings` with optional `?tab=appearance` query param so the URL reflects the active tab
- Header keeps the same title/subtitle; replace the `X` close button with a **Back to Dashboard** link/button, or with browser back navigation

### Implementation Sketch

1. **Move the component** from `Components/Modal/SettingsSidePanel.jsx` to `Content/SettingsPage.jsx` (or `Pages/SettingsPage.jsx`) — it stops being a modal/drawer
2. **Add a route** in your dashboard router (likely `src/components/dashboard/DashboardApp.jsx`):
   ```jsx
   <Route path="/dashboard/settings" element={<SettingsPage />} />
   ```
3. **Update the left-nav link** for Settings to navigate to that route (use `useNavigate` from `react-router-dom`)
4. **Refactor the root container** from:
   ```jsx
   <div className="fixed inset-y-0 right-0 z-[210] w-full max-w-2xl ...">
   ```
   to:
   ```jsx
   <div className="w-full h-full bg-white dark:bg-slate-900">
   ```
5. **Remove the backdrop** element entirely
6. **Replace the X close button** with a "← Back" link or breadcrumb
7. **Add an optional URL query param** for the active tab, e.g. `?tab=dropdowns`, so the link is shareable / refreshable

### Acceptance Criteria

- [ ] Clicking "Settings" in the left nav navigates to `/dashboard/settings`
- [ ] The Settings page fills the full viewport (no max-width constraint)
- [ ] The 5 tabs work the same as before: Profile & Account, Appearance, Agency Details, Contract Defaults, Dropdown Data, System Management
- [ ] No backdrop overlay blocks interaction with the rest of the app
- [ ] The dropdown-list management section has noticeably more room — the table inside it no longer needs `max-h-[300px] overflow-y-auto` and can show more rows
- [ ] Browser back button returns to the previous page
- [ ] Refreshing the page keeps the user on the Settings page (not kicked back to dashboard)
- [ ] Optional: `?tab=dropdowns` etc. deep-links to a specific tab

### Notes / Considerations

- **No backend changes** — all 5 tabs read/write through existing endpoints (`/api/users/`, `/api/core/`, `/api/companies/job-positions/`, etc.). The settings data layer is unchanged.
- **State management** — the `useState` calls inside the component stay. If the tabs become separate sub-routes, lift the state up or use URL query params to preserve the active tab.
- **Mobile responsiveness** — the current side panel already collapses; full-screen layout will need a max-width on really wide screens (optional) so the dropdown table doesn't get unreadably stretched. Consider `max-w-7xl mx-auto` as a sane upper bound.
- **Browser history** — opening settings should add to the back stack, not replace the current entry. Use `navigate('/dashboard/settings')` (not `replace`).

### API / Backend

**No backend changes required.** The conversion is purely a frontend structural change.

---

## Final Summary

| # | Endpoint | New Fields / Resource | Migration | App |
|---|---|---|---|---|
| 1 | `/api/companies/{id}/` | `address`, `contact_person`, `alt_phone`, `notes` | `0013_company_address_contact_person_alt_phone_notes.py` | companies |
| 2 | `/api/companies/job-positions/{id}/` | `created_at`, `updated_at` | `0014_joborderposition_created_at_and_more.py` | companies |
| 3 | `/api/reminders/` *(now in own `reminders` app)* | `user`, `text`, `reminder_date`, `reminder_time`, `is_completed`, `created_at`, `updated_at` | `reminders/0001_initial.py` | reminders |
| 4 | `/api/interviews/` | `principal`, `position`, `type`, `duration_minutes`, `location`, `result`, `feedback` *(model)* + `candidate_email`, `interviewer_email` *(serializer)* | `0003_interview_more_fields.py` | interviews |

## Apply All Migrations (one command)

```powershell
cd E:\2-TECHNO AQUARE
.\venv\Scripts\activate
python manage.py migrate companies
python manage.py migrate interviews
```

Expected output:
```
Running migrations:
  Applying companies.0013_company_address_contact_person_alt_phone_notes... OK
  Applying companies.0014_joborderposition_created_at_and_more... OK
  Applying interviews.0002_reminder... OK
  Applying interviews.0003_interview_more_fields... OK
```

## Global Handoff Notes for Frontend

1. All new fields are optional except the **Reminder** ones (`user`, `text`, `reminder_date`, `reminder_time` — those are required).
2. Timestamp fields (`created_at`, `updated_at`) are **always read-only** — never send them in POST/PATCH.
3. Foreign key fields (`user`, `principal`, `candidate`, `interviewer`) must be sent as **integer ids**, never as names or objects.
4. Date-only fields (`reminder_date`) use `YYYY-MM-DD`. Time-only fields (`reminder_time`) use `HH:MM:SS`. DateTime fields (`date` on Interview, `created_at`, `updated_at`) use ISO 8601.
