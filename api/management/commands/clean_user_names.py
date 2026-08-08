"""
Clean dirty first_name / middle_name pairs in the Users table.

The history: the `to_representation` of UsersSerializer used to merge
`first_name + " " + middle_name` into the API response's `first_name`
field, and the frontend then concatenated that AGAIN with
`middle_name` to display the user name. Over time, repeated round-trips
left rows where first_name already contained the merged string, so the
display showed visible duplication (e.g. "Mohamed Sami Afifi Soliman
Sami Afifi Soliman").

Now that the merge in to_representation is removed, clean rows display
correctly via the frontend's `first_name + " " + middle_name` concat.
This command cleans the remaining dirty rows by:

  1. Detecting overlap: middle_name's words appear in first_name (or
     first_name already looks like a merged full name).
  2. Reconstructing the canonical full name: union of first_name words
     and middle_name words, deduped while preserving order.
  3. Re-splitting: first word -> first_name, rest -> middle_name
     (the same split rule as `to_internal_value`).

The command is idempotent — running it twice on already-clean data is
a no-op.

Usage:
  python manage.py clean_user_names --dry-run          # preview changes
  python manage.py clean_user_names --limit 5          # only first 5 dirty rows
  python manage.py clean_user_names --backup out.json  # write a JSON backup
  python manage.py clean_user_names                    # apply for real
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Users


def compute_clean_name(first, middle):
    """
    Return (new_first, new_middle) — clean split of the given values.

    Returns the originals if they're already clean (no overlap, no
    shared words). Returns the union-then-split form if they overlap.

    Only flags a row as dirty if at least one of first_name or
    middle_name is multi-word. Single-word first_name + single-word
    middle_name with overlap (e.g. "John" / "John") is treated as a
    legitimate "user named John with middle name John" case and left
    alone — also avoids touching test fixtures where first_name and
    middle_name are both the same single letter like "A" / "A".
    """
    first = (first or "").strip()
    middle = (middle or "").strip()

    if not first and not middle:
        return "", ""
    if not middle:
        return first, ""
    if not first:
        return "", middle

    first_words = first.split()
    middle_words = middle.split()

    # Only consider "dirty" if either side is multi-word. A 1+1 case
    # with a shared word is a legitimate match, not corruption.
    if len(first_words) < 2 and len(middle_words) < 2:
        return first, middle

    # If no word in middle_name appears in first_name, the data is
    # already in the standard "first word / rest" form. Don't touch.
    if not set(middle_words) & set(first_words):
        # Also check the special "first_name already contains middle_name
        # as a trailing substring" case.
        if not first.rstrip().endswith(middle):
            return first, middle

    # Build the canonical full name: union of both word lists,
    # deduped while preserving order from first_name first.
    seen = set()
    canonical = []
    for w in first_words + middle_words:
        if w not in seen:
            canonical.append(w)
            seen.add(w)

    new_first = canonical[0] if canonical else ""
    new_middle = " ".join(canonical[1:]) if len(canonical) > 1 else ""

    # If the new split is identical to the current values, no change.
    if new_first == first and new_middle == middle:
        return first, middle

    return new_first, new_middle


class Command(BaseCommand):
    help = "Clean dirty first_name/middle_name pairs in the Users table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the changes that would be made without writing to the DB.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Stop after cleaning N rows. Useful for testing.",
        )
        parser.add_argument(
            "--backup",
            type=str,
            default=None,
            help="Write a JSON backup of before/after values to this path.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        backup_path = options["backup"]

        users = Users.objects.exclude(first_name__isnull=True)
        changes = []
        skipped = 0

        for user in users:
            new_first, new_middle = compute_clean_name(
                user.first_name, user.middle_name
            )
            if new_first == (user.first_name or "") and new_middle == (user.middle_name or ""):
                skipped += 1
                continue

            changes.append({
                "id": user.id,
                "email": user.email,
                "before": {"first_name": user.first_name, "middle_name": user.middle_name},
                "after": {"first_name": new_first, "middle_name": new_middle},
            })

            if limit is not None and len(changes) >= limit:
                break

        # Print a preview
        for c in changes:
            self.stdout.write(
                f"  user #{c['id']:>4} ({c['email']}):\n"
                f"    before: first_name={c['before']['first_name']!r}, middle_name={c['before']['middle_name']!r}\n"
                f"    after : first_name={c['after']['first_name']!r}, middle_name={c['after']['middle_name']!r}"
            )

        self.stdout.write("")
        self.stdout.write(
            f"  total scanned={users.count()}, "
            f"clean={skipped}, dirty={len(changes)}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run — no changes written. Re-run without --dry-run to apply."
            ))
            return

        if not changes:
            self.stdout.write(self.style.SUCCESS("\nNothing to clean."))
            return

        if backup_path:
            p = Path(backup_path)
            p.write_text(
                json.dumps(changes, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self.stdout.write(self.style.SUCCESS(
                f"\nBackup written to {p} ({p.stat().st_size:,} bytes)."
            ))

        # Apply in a single transaction so partial failures don't leave
        # the table half-cleaned.
        with transaction.atomic():
            for c in changes:
                user = Users.objects.get(id=c["id"])
                user.first_name = c["after"]["first_name"]
                user.middle_name = c["after"]["middle_name"]
                user.save(update_fields=["first_name", "middle_name"])

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Cleaned {len(changes)} user(s)."
        ))
