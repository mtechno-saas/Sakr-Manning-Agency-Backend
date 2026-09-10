"""
Backfill ``CVSubmission.position`` + ``UserRank`` for CVs that were
parsed by ``/ai/parse/`` BEFORE commit 53651b22 added that step.

Symptom that motivates this command: a seafarer uploaded via
/ai/parse/ shows up on the Crew Management table with
``POSITION: "—"`` and ``RANK CODE: "—"`` even though the underlying
user row has ``application_for_position`` populated. The reason is
historical: the parser used to save the position to the User row
only, never to the CV submission's FK or the UserRank lookup
table. Starting with commit 53651b22 the parser does both, but
rows written before that fix are still empty.

This command walks every CV submission with ``position IS NULL``,
looks up the rank by the user row's ``application_for_position``
(case-insensitive exact name, then ``istartswith`` fallback for
short-form labels like "Wiper" vs canonical
"Wiper/Assistant Mechanic"), and:

  1. Sets ``cv_submission.position = matched_rank``.
  2. Creates a ``UserRank`` for the user via ``get_or_create`` so
     the list endpoint's ``coded_rank`` / ``assigned_code`` /
     ``rank_code`` fields are populated.

Idempotent: re-running on a CV that already has a position is a
no-op (the queryset filters those out). Re-running on a user that
already has a UserRank for the matched rank also does nothing
(``get_or_create``).

Usage::

    python manage.py backfill_cv_submission_ranks --dry-run
    python manage.py backfill_cv_submission_ranks
    python manage.py backfill_cv_submission_ranks --user 134
    python manage.py backfill_cv_submission_ranks --report /tmp/backfill.txt
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import CVSubmission, Rank, UserRank


def _resolve_rank(name: str) -> Rank | None:
    """Same matching strategy the live parser uses — exact, then
    ``istartswith``. Returns None if nothing matches."""
    if not name:
        return None
    match = Rank.objects.filter(name__iexact=name).first()
    if match:
        return match
    return (
        Rank.objects.filter(name__istartswith=name)
        .order_by("name")
        .first()
    )


class Command(BaseCommand):
    help = (
        "Backfill CVSubmission.position + UserRank for CVs parsed "
        "before the rank-write step was added to /ai/parse/."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't write anything. Print what would change.",
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
                "was changed (or what would change in --dry-run)."
            ),
        )

    def handle(self, *args, **opts):
        dry_run: bool = opts["dry_run"]
        user_ids: list[int] | None = opts.get("user")
        report_path: str | None = opts.get("report")

        qs = CVSubmission.objects.filter(
            position__isnull=True,
            user__application_for_position__isnull=False,
        )
        if user_ids is not None:
            qs = qs.filter(user_id__in=list(user_ids))

        # Order by id so the report is stable run-to-run.
        qs = qs.order_by("id").select_related("user")

        report_lines: list[str] = []
        scanned = 0
        resolved = 0
        unresolved = 0
        no_match_submissions: list[CVSubmission] = []

        for cv in qs.iterator():
            scanned += 1
            user = cv.user
            pos_name = (user.application_for_position or "").strip()
            if not pos_name:
                continue

            rank = _resolve_rank(pos_name)
            if rank is None:
                # No matching Rank row — leave position NULL but record
                # the submission for the report so the admin can see
                # which users need a Rank row created manually.
                unresolved += 1
                no_match_submissions.append(cv)
                report_lines.append(
                    f"NO_MATCH cv_submission_id={cv.id} user_id={user.id} "
                    f"application_for_position={pos_name!r}"
                )
                continue

            # We have a Rank. Apply the same set + create-UserRank pair
            # that the live parser uses.
            report_lines.append(
                f"SET cv_submission_id={cv.id} user_id={user.id} "
                f"position={rank.name!r} (id={rank.id}, code={rank.code!r})"
            )
            resolved += 1

            if dry_run:
                # Skip the UserRank creation in dry-run so the report
                # matches the dry-run claim (no writes).
                continue

            with transaction.atomic():
                cv.position = rank
                cv.save(update_fields=["position"])
                UserRank.objects.get_or_create(user=user, rank=rank)

        if not dry_run:
            # Sanity check: any submissions still NULL after the
            # backfill? (We filter by position__isnull=True in the
            # queryset, so this should be the ones we couldn't
            # resolve.)
            remaining = (
                CVSubmission.objects
                .filter(
                    position__isnull=True,
                    user__application_for_position__isnull=False,
                )
                .count()
            )
            if remaining:
                self.stdout.write(self.style.WARNING(
                    f"WARNING: {remaining} CV submissions still have "
                    f"position=NULL after backfill. These are likely "
                    f"users whose application_for_position does not "
                    f"match any Rank row. See --report for details."
                ))

        self.stdout.write("")
        self.stdout.write(f"Scanned: {scanned} CV submissions with position IS NULL")
        self.stdout.write(
            f"Resolved: {resolved} "
            f"{'(would be updated' if dry_run else 'updated'}"
        )
        self.stdout.write(
            f"Unresolved: {unresolved} "
            f"(no Rank match for application_for_position)"
        )
        if dry_run:
            self.stdout.write(self.style.NOTICE(
                "DRY RUN — no changes were written. Re-run without "
                "--dry-run to apply."
            ))

        if report_path:
            with open(report_path, "w", encoding="utf-8") as fh:
                fh.write(
                    f"backfill_cv_submission_ranks "
                    f"{'(DRY RUN)' if dry_run else '(APPLIED)'}\n"
                )
                fh.write(
                    f"Scanned: {scanned}\n"
                    f"Resolved: {resolved}\n"
                    f"Unresolved: {unresolved}\n\n"
                )
                fh.write("\n".join(report_lines))
                if report_lines:
                    fh.write("\n")
            self.stdout.write(f"Wrote report to {report_path}")
