"""
Clean up placeholder Users that were auto-created by the legacy
`DocumentViewSet.perform_create` flow.

These accounts match the pattern:
    applicant_<8-hex-chars>@placeholder.sakrshipping.com
    first_name = "Applicant" (or extracted from filename)
    password   = unusable
    role       = "Employee"

They were spawned silently whenever an admin uploaded a document
without supplying a `user` field. The Documents linked to these users
showed up as "Unknown" rows in the Applicants dashboard.

Running this command deletes those users (and CASCADEs their Documents,
Documents-attached files, generated_id, etc.). It is idempotent — a
second run is a no-op.

Usage:
  python manage.py clean_placeholder_users --dry-run         # preview
  python manage.py clean_placeholder_users --backup out.json  # backup first
  python manage.py clean_placeholder_users                   # apply
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Users


class Command(BaseCommand):
    help = "Delete placeholder Users (and cascade their Documents) created by the legacy Documents auto-create flow."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Preview what would be deleted without writing.")
        parser.add_argument("--backup", type=str, default=None,
                            help="Write a JSON backup of the would-be-deleted users to this path.")
        parser.add_argument("--limit", type=int, default=None,
                            help="Stop after deleting N users (useful for testing).")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        backup_path = options["backup"]

        targets = Users.objects.filter(
            email__regex=r"^applicant_[0-9a-f]{8}@placeholder\.sakrshipping\.com$"
        ).order_by("id")

        to_delete = list(targets)
        if limit is not None:
            to_delete = to_delete[:limit]

        # Preview
        for u in to_delete[:20]:
            self.stdout.write(
                f"  #{u.id:>4} {u.email}  "
                f"first_name={u.first_name!r}  middle_name={u.middle_name!r}  "
                f"docs={u.documents.count()}"
            )
        if len(to_delete) > 20:
            self.stdout.write(f"  ... and {len(to_delete) - 20} more")

        self.stdout.write("")
        self.stdout.write(
            f"  total matched: {targets.count()}, "
            f"to delete: {len(to_delete)}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run — no changes written. Re-run without --dry-run to apply."
            ))
            return

        if not to_delete:
            self.stdout.write(self.style.SUCCESS("\nNothing to clean."))
            return

        if backup_path:
            p = Path(backup_path)
            payload = [
                {
                    "id": u.id,
                    "email": u.email,
                    "first_name": u.first_name,
                    "middle_name": u.middle_name,
                    "role": u.role,
                    "documents_count": u.documents.count(),
                }
                for u in to_delete
            ]
            p.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self.stdout.write(self.style.SUCCESS(
                f"\nBackup written to {p} ({p.stat().st_size:,} bytes)."
            ))

        # Apply in a transaction so partial failures don't leave the
        # table in an inconsistent state. CASCADE on Document.user
        # removes the dependent Documents and their files.
        deleted = 0
        with transaction.atomic():
            for u in to_delete:
                u.delete()
                deleted += 1
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Deleted {deleted} placeholder user(s)."
        ))
