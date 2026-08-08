"""
Sync the canonical vessel type list into core.VesselType.

Background:
- The migration `0005_populate_vessel_types.py` seeded 10 vessel types.
- Manual additions on production have grown the list to 32+, with
  naming inconsistencies (e.g. "Container Ships" plural vs "Container
  Ship" singular).
- Unlike flags, the Ship form's vessel type dropdown is already
  dynamic, so UX isn't broken — but the Settings list shows the
  duplicate names.

This command:
1. Inserts the canonical vessel type names that aren't in the DB.
2. Does NOT delete or rename existing rows (preserves FK references
   from `Ship.ship_type`).

Run with:
    python manage.py sync_vessel_types            # apply
    python manage.py sync_vessel_types --dry-run  # show what would change
    python manage.py sync_vessel_types --backup   # write before-state to backups/
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from core.models import VesselType


# Canonical vessel type list. Includes the 10 from migration
# 0005 + the 22+ that have been added on production over time, plus
# a few commonly-needed ones. This is a UNION, not a replacement —
# existing rows are never deleted.
CANONICAL = [
    # Cargo
    "Container Ships", "Container Ship",
    "Bulk Carriers", "Bulk Carrier",
    "General Cargo Ship",
    "Reefer Ship",
    "Multi-Purpose Vessel",
    "Heavy Lift Vessel",
    # Tankers
    "Tankers", "Tanker",
    "Oil Tanker", "Chemical Tanker", "Product Tanker",
    "LNG Carrier", "LPG Carrier",
    "VLCC", "Suezmax", "Aframax", "MR Tanker",
    # Passengers
    "Passenger Ships", "Passenger Ship",
    "Cruise Ship", "Ferry",
    "Ro-Ro Ships", "Ro-Ro Ship", "Ro-Ro Passenger (Ro-Pax)",
    # Offshore
    "Offshore Support Vessels", "Offshore Support Vessel",
    "PSV (Platform Supply Vessel)",
    "AHTS (Anchor Handling Tug Supply Vessel)",
    "Drillship", "Semi-Submersible", "FPSO",
    "OSV", "Crew Boat",
    # Specialized
    "Fishing Vessels", "Fishing Vessel",
    "Tugboats", "Tugboat",
    "Barge", "Dredger",
    "Icebreakers", "Icebreaker",
    "Survey Vessel", "Cable Layer", "Pipe Layer",
    # Other
    "Recreational", "Yacht", "Sailboat",
    "River Vessel", "Inland Waterways Vessel",
    "Naval / Military Vessel",
    "Research Vessel",
    "Training Ship",
]


class Command(BaseCommand):
    help = "Sync the canonical vessel type list into core.VesselType (idempotent, add-only)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without touching the DB.",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Write current vessel types to backups/vessel_types_before_sync_<ts>.json",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        do_backup = options["backup"]

        before = list(VesselType.objects.values("id", "name").order_by("name"))
        before_names = {f["name"] for f in before}

        self.stdout.write(self.style.NOTICE(
            f"Current VesselType count: {len(before)}"
        ))

        if do_backup and not dry:
            backup_dir = os.path.join("backups")
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(backup_dir, f"vessel_types_before_sync_{ts}.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(before, fh, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f"Backup written: {path}"))

        to_add = [n for n in CANONICAL if n not in before_names]
        if to_add:
            self.stdout.write(self.style.WARNING(
                f"Canonical names missing from DB ({len(to_add)}): "
                f"{to_add[:10]}{'...' if len(to_add) > 10 else ''}"
            ))
            if not dry:
                VesselType.objects.bulk_create(
                    [VesselType(name=n) for n in to_add],
                    ignore_conflicts=True,
                )
        else:
            self.stdout.write(self.style.SUCCESS(
                "All canonical names already present in DB."
            ))

        after_count = VesselType.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"VesselType count: {len(before)} -> {after_count} "
            f"({'dry run' if dry else 'applied'})"
        ))

        if dry:
            self.stdout.write(self.style.WARNING(
                "\n--dry-run: nothing was written. Re-run without --dry-run to apply."
            ))
