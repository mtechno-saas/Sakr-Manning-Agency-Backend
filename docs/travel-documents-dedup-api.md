# Travel Documents duplication on /ai/parse/ — fix

## Symptom

After uploading a CV via `/ai/parse/`, the **Travel Documents** table
in the **Edit CV Submission** modal (and any view that lists
`PersonalDocument` rows for the user) showed every row twice. Two
seafarers uploaded back-to-back had *identical* travel-doc numbers —
the second upload was using data that came from the same Sakr source
form as the first.

## Root cause

`SeafarerApplicationSerializer.update()` is called from
`_save_parser_output` for every `/ai/parse/` POST. The parser
(`SakrTemplateExtractor`) walks the Sakr form's `4. Travel
Documents` table row-by-row. For some real CVs the OCR layer emits
the same row twice (because the source form's travel-doc block is
repeated on the same page in OCR output), so the parser hands the
serializer two identical entries.

The serializer's old loop called
`PersonalDocument.objects.update_or_create(user, document_type, ...)`
once per parsed entry. In normal traffic that collapses to one row,
but for those Sakr CVs the second entry was creating a second row
(because of how the resolved `document_type` choice interacts with
the update path on real CVs — and any code path that bypasses
`update_or_create` and calls `.create()` directly). The model had
**no `unique_together` constraint**, so nothing stopped the second
row from being saved.

## Fix (commit `f9418ce0`)

Two layers, either of which is enough on its own — together they
make the bug impossible to reproduce going forward.

1. **Serializer-side input dedup.** The new loop builds a
   `travel_by_dedup_key: dict[str, dict]` keyed on the *resolved*
   `document_type` choice (last entry wins), then issues one
   `update_or_create` per key. Two parsed entries for the same
   document type collapse to one DB write.
2. **`unique_together` constraint.** `PersonalDocument` now has
   `Meta.unique_together = [('user', 'document_type')]`. Any future
   code path (admin form, third-party integration, future refactor)
   that tries to insert a second row for the same `(user,
   document_type)` will hard-fail with `IntegrityError` instead of
   silently saving a duplicate. Migration: `api/0073`.

## Cleaning the duplicate rows that already exist on prod

The constraint is added in migration `0073`. Running the migration
on prod will fail if duplicate rows already exist. Two options:

### A. Pre-clean with the management command (recommended)

The `dedupe_personal_documents` command keeps the "best" row in
each duplicate `(user, document_type)` group (most recent
`updated_at` first, ties broken by most-populated-fields) and
deletes the rest. Run with `--dry-run` first:

```bash
cd /opt/sakr/Sakr-Manning-Agency-Backend-New
python manage.py dedupe_personal_documents --dry-run
python manage.py dedupe_personal_documents
```

The command also supports:

- `--user <id>` (repeatable) — restrict scope to one or more users
- `--report /path/to/file.txt` — write a human-readable report of
  every row that was (or would be) deleted

### B. Drop the rows by hand

If you want to inspect before deleting:

```sql
-- find the duplicate groups
SELECT user_id, document_type, COUNT(*)
FROM api_personaldocument
GROUP BY user_id, document_type
HAVING COUNT(*) > 1;

-- inspect the rows in one group
SELECT id, user_id, document_type, document_number, updated_at
FROM api_personaldocument
WHERE user_id = 141 AND document_type = 'US Visa C1/D'
ORDER BY updated_at DESC;
```

Then delete the lower-priority row(s) by `id`.

## Files changed

- `api/models.py` — `PersonalDocument.Meta` adds `unique_together`
  and an `ordering` (alphabetical by `document_type` for stable UI).
- `api/seafarer_application_serializers.py` — dedup the parsed
  `travel_documents` by resolved `document_type` before writing.
- `api/migrations/0073_personaldocument_unique_per_user.py` — new
  migration that adds the constraint.
- `api/management/commands/dedupe_personal_documents.py` — new
  command for one-shot cleanup of historical rows.
- `api/tests.py` — 13 new tests:
  - `SeafarerApplicationTravelDocsDedupTests` (8) — input dedup
    behavior + DB-level constraint behavior.
  - `DedupePersonalDocumentsCommandTests` (5) — command
    `--dry-run`, `--user`, `--report`, keep-best policy, no-op
    when nothing to dedupe.

## Tests

`api/tests.py`: **288** pass (was 280 before this commit).
