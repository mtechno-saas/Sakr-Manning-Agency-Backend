# User Status — 5 states

`Users.user_status` is now a 5-state enum:

| Value | Source | Meaning |
|---|---|---|
| `ON_SITE` | stored (admin) | Free / available. Default for new users. |
| `ON_BOARD` | computed | Currently on a ship with an Active/Signed contract (sign-off null or in the future). |
| `VACATION` | stored (admin) | On vacation. Manual override; wins over computed values. |
| `MEDICAL_VACATION` | stored (admin) | On medical leave. Manual override; wins over computed values. |
| `NEW_APPLICANT` | computed | No contract history at all — never been placed. |

## Resolution order (effective status)

The API exposes `effective_user_status` (computed) alongside `user_status` (stored, what the admin sets). Effective status is:

1. If stored = `VACATION` → `VACATION`
2. If stored = `MEDICAL_VACATION` → `MEDICAL_VACATION`
3. If user has any `Active` or `Signed` contract with `sign_off_date` null or in the future → `ON_BOARD`
4. If user has no contracts whatsoever → `NEW_APPLICANT`
5. Otherwise → `ON_SITE`

Manual overrides (1, 2) always win over contract-derived values (3, 4) — a user on `VACATION` who happens to have an open contract is still shown as `VACATION` until the admin lifts the override.

## Filter

`GET /api/users/users/?user_status=ON_BOARD` accepts any of the 5 values (or repeated values, ORed). The filter is case-insensitive and accepts both forms of `MEDICAL VACATION` (with space, the human label) and `MEDICAL_VACATION` (the stored value).

Filter semantics match `effective_user_status`:

- `?user_status=ON_SITE` → users with stored `ON_SITE` AND at least one past contract AND no active contract
- `?user_status=ON_BOARD` → users with an Active/Signed contract and stored ≠ `VACATION`/`MEDICAL_VACATION`
- `?user_status=VACATION` → stored = `VACATION`
- `?user_status=MEDICAL_VACATION` → stored = `MEDICAL_VACATION`
- `?user_status=NEW_APPLICANT` → stored ≠ `VACATION`/`MEDICAL_VACATION` AND no contracts at all

Invalid values return 400 with a clear `user_status` error.

## Files touched

- `api/models.py`
  - `User_Status` enum: added `ON_BOARD`, `NEW_APPLICANT` (the two computed states). Kept `ON_SITE`, `VACATION`, `MEDICAL_VACATION` (the three admin-settable states).
  - New `Users.get_effective_status()` method implementing the resolution order above.
- `api/serializer.py`
  - `UsersSerializer.effective_user_status` — read-only `SerializerMethodField` calling `get_effective_status()`.
- `api/filters.py`
  - `UsersFilter.filter_user_status` rewritten to handle all 5 values via subqueries (`Exists`/`OuterRef`) for the computed ones.
- `api/migrations/0069_alter_users_user_status_choices.py`
  - Auto-generated `AlterField` expanding the `choices` list. No data migration — existing rows already use one of the 3 stored values which are still valid.
- `api/tests.py`
  - New `UserStatusFiveStateTests` (16 tests): enum contents, effective-status computation under each scenario, serializer exposure, filter for each value, invalid-value 400, multi-value OR logic, both `MEDICAL VACATION` and `MEDICAL_VACATION` accepted.
