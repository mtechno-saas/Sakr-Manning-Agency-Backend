"""
Dedupe ``api.PersonalDocument`` rows for the same (user, document_type) pair.

The Sakr-template parser (SeafarerApplicationSerializer.update) and the
``/api/parse/`` endpoint normally use ``update_or_create(user, document_type)``
so a single row per (user, type) is the expected steady state. However,
some real Sakr CVs cause the OCR layer to emit the same travel-doc row
twice — and historical /ai/parse/ runs on those CVs ended up saving
two rows for the same (user, document_type) pair (symptom: every row
in the Travel Documents CRUD table on the Edit modal appears twice).

The fix going forward is two-layered:
  1. The serializer now dedupes its input by the resolved
     ``document_type`` *choice* before writing (last entry wins).
  2. The ``PersonalDocument`` model now has
     ``unique_together = ('user', 'document_type')`` so any code path
     that bypasses the dedup and tries to write a second row fails
     fast with ``IntegrityError``.

This command is the cleanup for the rows that already exist. It walks
every (user, document_type) group that has >1 row, keeps the
"best" row (most recently updated, or the one with the most populated
fields), and deletes the rest. Run with ``--dry-run`` first to see
what would change.

Usage::

    python manage.py dedupe_personal_documents --dry-run
    python manage.py dedupe_personal_documents
    python manage.py dedupe_personal_documents --user 141
    python manage.py dedupe_personal_documents --user 141 --user 142
    python manage.py dedupe_personal_documents --report /tmp/dedupe.txt
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, F

from api.models import PersonalDocument


def _keep_score(pd: PersonalDocument) -> tuple:
    """
    Higher score = better row to keep. Compares:

      * ``updated_at`` is more recent (so an admin's manual edit wins
        over an older OCR'd value)
      * the row with more populated fields wins (an empty row is
        clearly less useful than a row with full data)
    """
    populated = sum(
        1
        for f in (
            pd.document_number,
            pd.issue_date,
            pd.expiry_date,
            pd.issuing_country,
            pd.issued_by,
            pd.place_of_issue,
        )
        if f not in (None, "")
    )
    return (pd.updated_at, populated)


def _walk_dup_groups(user_ids: Iterable[int] | None = None):
    qs = (
        PersonalDocument.objects.values("user_id", "document_type")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .order_by("user_id", "document_type")
    )
    if user_ids is not None:
        qs = qs.filter(user_id__in=list(user_ids))
    for grp in qs:
        yield grp["user_id"], grp["document_type"]


def _resolve_keep_and_drop(user_id: int, document_type: str):
    rows = list(
        PersonalDocument.objects.filter(
            user_id=user_id, document_type=document_type
        ).order_by("id")
    )
    if len(rows) <= 1:
        return None, []
    rows.sort(key=_keep_score, reverse=True)
    return rows[0], rows[1:]


class Command(BaseCommand):
    help = (
        "Dedupe PersonalDocument rows: keep one row per "
        "(user, document_type) pair, delete the rest."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Don't write anything. Print the (user, document_type) "
                "groups that have duplicates and the IDs that would be "
                "kept / deleted."
            ),
        )
        parser.add_argument(
            "--user",
            action="append",
            type=int,
            default=None,
            help=(
                "Restrict to one or more user ids. May be passed "
                "multiple times. Default: all users."
            ),
        )
        parser.add_argument(
            "--report",
            default=None,
            help=(
                "Optional path to write a human-readable report of what "
                "was changed. The file is created (or overwritten) with "
                "one line per removed row."
            ),
        )

    def handle(self, *args, **opts):
        dry_run: bool = opts["dry_run"]
        user_ids: list[int] | None = opts.get("user")
        report_path: str | None = opts.get("report")

        report_lines: list[str] = []
        total_groups = 0
        total_deleted = 0

        for user_id, document_type in _walk_dup_groups(user_ids):
            total_groups += 1
            keep, drop = _resolve_keep_and_drop(user_id, document_type)
            if keep is None:
                continue
            self.stdout.write(
                f"user={user_id} type={document_type!r}: "
                f"keep id={keep.id} (updated_at={keep.updated_at:%Y-%m-%d %H:%M}), "
                f"delete ids={[d.id for d in drop]}"
            )
            for d in drop:
                report_lines.append(
                    f"DELETE PersonalDocument id={d.id} "
                    f"user_id={d.user_id} document_type={d.document_type!r} "
                    f"document_number={d.document_number!r} "
                    f"updated_at={d.updated_at:%Y-%m-%d %H:%M}"
                )
            total_deleted += len(drop)
            if not dry_run:
                with transaction.atomic():
                    PersonalDocument.objects.filter(
                        id__in=[d.id for d in drop]
                    ).delete()

        if not dry_run:
            # Sanity-check: should now be zero dup groups.
            remaining = (
                PersonalDocument.objects.values("user_id", "document_type")
                .annotate(c=Count("id"))
                .filter(c__gt=1)
            )
            leftover = list(remaining)
            if leftover:
                self.stdout.write(self.style.WARNING(
                    f"WARNING: {len(leftover)} duplicate groups remain "
                    f"after cleanup (likely blocked by a different process). "
                    f"First few: {leftover[:3]}"
                ))

        self.stdout.write("")
        self.stdout.write(
            f"Total duplicate (user, type) groups: {total_groups}"
        )
        self.stdout.write(
            f"Total rows {'that would be' if dry_run else ''} deleted: "
            f"{total_deleted}"
        )
        if dry_run:
            self.stdout.write(self.style.NOTICE(
                "DRY RUN — no changes were written. Re-run without "
                "--dry-run to apply."
            ))

        if report_path:
            mode = "w"
            with open(report_path, mode, encoding="utf-8") as fh:
                fh.write(
                    f"dedupe_personal_documents "
                    f"{'(DRY RUN)' if dry_run else '(APPLIED)'}\n"
                )
                fh.write(
                    f"Total duplicate groups: {total_groups}\n"
                )
                fh.write(
                    f"Total rows {'that would be' if dry_run else ''} "
                    f"deleted: {total_deleted}\n"
                )
                fh.write("\n".join(report_lines))
                if report_lines:
                    fh.write("\n")
            self.stdout.write(f"Wrote report to {report_path}")
