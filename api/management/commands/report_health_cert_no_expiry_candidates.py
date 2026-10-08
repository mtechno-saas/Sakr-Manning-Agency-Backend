"""
Report Users rows that may have been saved as "no expiry" health
certificates BEFORE the no-expiry parser fix landed.

The sea-service parser learned (commit 491d08f2) to recognize text like
"Valid for life long", "lifetime", "no expiry", "never expires" and set
the corresponding ``*_no_expiry`` boolean to True. CVs uploaded before
that fix would have lost the indicator: the PDF said "no expiry" but the
saved row had ``expiry_date = NULL`` and ``*_no_expiry = False``.

We cannot retroactively fix those rows -- the raw CV text is gone, and
NULL expiry_date is also the normal state for users who haven't filled
in the field yet. What we CAN do is surface the candidates for manual
review by an admin who can compare against the original CV.

Heuristic for "candidate": the certificate has a number (so it was
intentionally saved) AND the expiry date is NULL AND ``*_no_expiry`` is
False. Each such row might be either:

  * a true "no expiry" certificate we missed, or
  * a normal certificate where the user just hasn't entered an expiry
    date yet.

Either way, an admin eyeballing the original CV can resolve the
ambiguity. This command does NOT mutate the DB.

Usage:

  # Print candidates as a human-readable table to stdout
  python manage.py report_health_cert_no_expiry_candidates

  # Limit to one user
  python manage.py report_health_cert_no_expiry_candidates --user 134

  # Write a JSON report
  python manage.py report_health_cert_no_expiry_candidates \\
      --report /tmp/no_expiry_candidates.json

  # Quiet: just the count, no per-row detail
  python manage.py report_health_cert_no_expiry_candidates --quiet

A real fix needs either:

  (a) the user's original CV file re-parsed through the new parser, or
  (b) an admin manually marking ``*_no_expiry = True`` after confirming
      against the PDF.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from api.models import Users


# (number field, expiry-date field, issue-date field, no-expiry flag, human label)
CERT_FIELDS = (
    ("international_medical_number", "international_medical_expiry_date",
     "international_medical_issue_date", "international_medical_no_expiry",
     "International Medical"),
    ("yellow_fever_number", "yellow_fever_expiry_date",
     "yellow_fever_issue_date", "yellow_fever_no_expiry",
     "Yellow Fever"),
    ("cholera_number", "cholera_expiry_date",
     "cholera_issue_date", "cholera_no_expiry",
     "Cholera"),
)


def _serialize_date(value):
    """Render a date/datetime/None as ISO string for JSON output."""
    if value is None:
        return None
    return value.isoformat()


class Command(BaseCommand):
    help = (
        "Report Users rows whose health-cert expiry_date is NULL but "
        "*_no_expiry is False and *_number is set. These rows may have "
        "been saved before the 'no expiry' parser fix landed -- an "
        "admin should eyeball the original CV and update the flag "
        "manually if applicable."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=int,
            default=None,
            help="Only scan this user id. Default: all users.",
        )
        parser.add_argument(
            "--report",
            type=str,
            default=None,
            help="Write a JSON report of candidates to this path.",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Only print the final count, no per-row detail.",
        )

    def handle(self, *args, **options):
        user_filter = options["user"]
        report_path = options["report"]
        quiet = options["quiet"]

        qs = Users.objects.all().order_by("id")
        if user_filter is not None:
            qs = qs.filter(id=user_filter)

        candidates = []
        for user in qs.iterator():
            for number_field, expiry_field, issue_field, no_expiry_field, label in CERT_FIELDS:
                number = (getattr(user, number_field) or "").strip()
                if not number:
                    continue
                expiry = getattr(user, expiry_field)
                no_expiry = getattr(user, no_expiry_field)
                # Candidate iff number set, no expiry date recorded,
                # and the no_expiry flag has not been set.
                if expiry is None and not no_expiry:
                    candidates.append({
                        "user_id": user.id,
                        "user_email": user.email,
                        "certificate": label,
                        "number": number,
                        "issue_date": _serialize_date(getattr(user, issue_field)),
                        "expiry_date": None,
                        "no_expiry": False,
                        "fix_action": (
                            f"Set rf's {no_expiry_field} = True after "
                            f"confirming the {label} certificate has no expiry."
                        ),
                    })

        scanned = qs.count()

        if quiet:
            self.stdout.write(
                f"  candidates: {len(candidates)}"
            )
        else:
            self.stdout.write(
                f"Scanned {scanned} user(s); "
                f"found {len(candidates)} candidate row(s) "
                f"across {len({c['user_id'] for c in candidates})} user(s):"
            )
            self.stdout.write("")
            if not candidates:
                self.stdout.write(self.style.SUCCESS(
                    "  Nothing to report -- DB is clean."
                ))
            else:
                # Group by user for readability
                by_user: dict[int, list[dict]] = {}
                for c in candidates:
                    by_user.setdefault(c["user_id"], []).append(c)
                for uid in sorted(by_user.keys()):
                    user_cands = by_user[uid]
                    email = user_cands[0]["user_email"]
                    self.stdout.write(
                        f"  user #{uid} ({email}):"
                    )
                    for c in user_cands:
                        self.stdout.write(
                            f"    - {c['certificate']:<22} number={c['number']!r}"
                        )
                    self.stdout.write("")
                self.stdout.write(self.style.WARNING(
                    "These rows are NOT modified. Confirm against the original "
                    "CV and update *_no_expiry manually if applicable."
                ))

        if report_path:
            p = Path(report_path)
            p.write_text(
                json.dumps(
                    {
                        "scanned_users": scanned,
                        "candidates_total": len(candidates),
                        "users_with_candidates": len({c["user_id"] for c in candidates}),
                        "rows": candidates,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.stdout.write(self.style.SUCCESS(
                f"\nReport written to {p} ({p.stat().st_size:,} bytes)."
            ))