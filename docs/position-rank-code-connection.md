# POSITION ↔ RANK CODE — they are connected now

**For the frontend dev (Karim). No frontend change is required — this is a
backend fix.** The columns just start telling the truth.

---

## What was wrong

The dashboard shows a POSITION column and a RANK CODE column next to each
other, but the code was never derived from the position.

The rank code came from a separate table (`UserRank` — the rank *assignments*
a person holds), and every read path took **the newest row** ("last write
wins"). So an applicant who held more than one rank always saw the code of
whichever rank was written last:

| Row said | Code shown | Why |
|---|---|---|
| POSITION = Master | `DR-32.001` (Baker's code) | Baker was the newest assignment |
| POSITION = Baker | `DR-32.001` | same row — the code "never changed" |

Changing the position from Master to Baker looked like a no-op, because the
column was already showing Baker's code.

## What it does now

**The rank code shown belongs to the position shown.** One rule, everywhere.

| Position | RANK CODE column | `rank_code` (the position's own code) |
|---|---|---|
| Master | the Master's assigned code (`DO-1.094`) | `DO-1.000` |
| Baker | the Baker's assigned code (`DR-32.001`) | `DR-32.000` |
| a position the person does not hold yet | the position's own code, no assigned code | the position's code |

Changing the position changes the code, in both directions, and the change is
visible on the next GET — no reload gymnastics.

---

## The two code fields (they are different things)

| Field | Meaning | Example |
|---|---|---|
| `rank_code` | the code the *rank* carries (the position's own code) | `DO-1.000` |
| `assigned_code` | the code *issued to this person* for that rank | `DO-1.094` |

The dashboard column labelled **RANK CODE** renders `assigned_code` (the
person's own code) — it is the one that matters, because it is what identifies
the person on a contract. `rank_code` is the generic code of the position and
is the same for everybody who holds that rank.

Both are now position-derived, so they never contradict the POSITION column.

---

## API surface — nothing changed for you

No new fields, no removed fields, no changed endpoints.

| Endpoint | Change |
|---|---|
| `GET /api/cv-submissions/` | `coded_rank[0]` is now the rank of **this row's** position (was: the newest assignment of the applicant) |
| `GET /api/cv-submissions/{id}/` | same |
| `PATCH /api/cv-submissions/{id}/` with `{"position": "Baker"}` | the applicant is given the Baker assignment if they did not hold it; the response's `coded_rank` / `rank_code` / `assigned_code` already follow the new position |
| `GET /api/users/users/{id}/` | `rank_code`, `assigned_code` and `coded_rank[0]` now follow `application_for_position`; `ranks[0]` is the assignment that matches the position (the dashboard's Rank + Assigned Code columns read `ranks[0]`) |
| `PATCH /api/users/users/{id}/` with `{"application_for_position": "Baker"}` | the profile now points at Baker's code, and the Baker assignment is created if it did not exist |
| `POST /api/users/users/{id}/assign-by-position/` | **was 400 "User already has the rank"** → now **200** with `already_assigned: true` and the existing code in `user_rank`. Assigning the same rank twice is no longer an error. |
| `POST /api/users/users/bulk-edit/` with `{"ids": [...], "data": {"rank": "Baker"}}` | **was broken** (the lookup raised `FieldError` on every call and the assignment was silently skipped) → it now really assigns the rank |

### The one thing to check in the UI

The "RANK CODE" column renders `assigned_code`. If a position has no issued
code yet, the cell shows the position's own `rank_code` instead (or `—`).
That is intentional: there is no personal code to show yet.

---

## Data note

Nothing is deleted. A person who was a Master and is now a Baker keeps both
assignments — both codes are still valid, they are just no longer both shown
in the same column. The one shown is always the one of the current position.
