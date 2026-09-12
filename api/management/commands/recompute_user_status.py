"""
Management command to recompute every user's stored `user_status` field
from their actual contract state, using Users.get_effective_status().

The stored `user_status` field can drift from reality:
  - 9 of 10 ON_SITE users might actually be ON_BOARD (have active contracts)
    but nobody ever updated the stored value when contracts were created.
  - Users finish a contract and stay stored as ON_BOARD until someone
    manually flips them back.

This command walks all users and writes `user.get_effective_status()` back
to `user_status`. After it runs, the stored field reflects reality, and
the `?user_status=` filter (which still uses effective status) agrees
with `?user_status_stored=` (which is the literal stored field).

Options:
  --dry-run              Show what would change without saving
  --user <id>            Recompute only this user (repeatable)
  --report <path>        Write a CSV report of changes to <path>
  --quiet                Suppress per-user progress output
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Users


class Command(BaseCommand):
    help = (
        "Recompute every user's stored user_status from contract state. "
        "Idempotent — users already at the correct status are skipped."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Compute and report changes without saving anything.",
        )
        parser.add_argument(
            "--user",
            action="append",
            type=int,
            default=[],
            metavar="ID",
            help="Recompute only this user ID (repeatable for many users).",
        )
        parser.add_argument(
            "--report",
            metavar="PATH",
            help="Write a CSV report of (id, email, before, after) to PATH.",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress per-user progress output (only summary at the end).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        target_user_ids = options["user"]
        report_path = options["report"]
        quiet = options["quiet"]

        qs = Users.objects.all().order_by("id")
        if target_user_ids:
            qs = qs.filter(id__in=target_user_ids)

        report_rows = []
        changed = 0
        unchanged = 0
        errors = 0

        if not quiet:
            mode = "DRY-RUN" if dry_run else "WRITE"
            self.stdout.write(f"[{mode}] Recomputing user_status for {qs.count()} users...")

        # batch_atomic lets us save many users but rollback the whole
        # batch on any error, rather than half-applying changes.
        with transaction.atomic():
            for user in qs.iterator():
                try:
                    before = (user.user_status or "").strip()
                    after = user.get_effective_status()
                    if before == after:
                        unchanged += 1
                        continue
                    report_rows.append((user.id, user.email, before, after))
                    changed += 1
                    if not dry_run:
                        user.user_status = after
                        user.save(update_fields=["user_status"])
                except Exception as exc:
                    errors += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"  user_id={user.id} email={user.email}: {exc}"
                        )
                    )
                    # Re-raise so the whole transaction rolls back
                    # unless we're in dry-run mode (then keep going).
                    if not dry_run:
                        raise

        if report_path:
            import csv
            with open(report_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["id", "email", "before", "after"])
                w.writerows(report_rows)
            if not quiet:
                self.stdout.write(f"Wrote report to {report_path}")

        verb = "would change" if dry_run else "changed"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. "
                f"{changed} {verb}, "
                f"{unchanged} already correct, "
                f"{errors} errors."
            )
        )
        if changed:
            self.stdout.write(
                f"  (Re-run with --dry-run first to preview. "
                f"Use --user <id> to scope to specific users.)"
            )
