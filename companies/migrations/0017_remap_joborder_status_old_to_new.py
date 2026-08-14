"""
Remap legacy JobOrder.status values to the new 3-state set
(Open, Close, Full Filled) BEFORE migration 0016 restricts the
choices. Without this, rows with values like 'Pending', 'Hold',
'Active', 'In Progress', 'Fulfilled', 'Cancelled', or 'Closed'
would fail the new choice validation when the alter runs.

Mapping (intentional, per the user's spec):
  Open          -> Open         (unchanged)
  Close         -> Close        (renamed from 'Closed')
  Full Filled   -> Full Filled   (renamed from 'Fulfilled')

  Pending       -> Open         (still recruiting)
  Hold          -> Open         (admin override re-opens)
  Active        -> Open         (still recruiting)
  In Progress   -> Open         (still recruiting)
  Closed        -> Close        (cancelled / closed; close enough)
  Cancelled     -> Close        (cancelled; close is the new name)
  Fulfilled     -> Full Filled   (renamed)

Anything else (defensive) is mapped to Open.

Idempotent: safe to re-run because the values being set are all
in the new choice set.
"""
from django.db import migrations


_MAP = {
    "Open": "Open",
    "Close": "Close",
    "Full Filled": "Full Filled",
    "Pending": "Open",
    "Hold": "Open",
    "Active": "Open",
    "In Progress": "Open",
    "Closed": "Close",
    "Cancelled": "Close",
    "Fulfilled": "Full Filled",
}


def remap(apps, schema_editor):
    JobOrder = apps.get_model("companies", "JobOrder")
    counts = {}
    for jo in JobOrder.objects.all().only("id", "status"):
        new_status = _MAP.get(jo.status, "Open")
        if new_status != jo.status:
            counts[jo.status] = counts.get(jo.status, 0) + 1
            jo.status = new_status
            jo.save(update_fields=["status"])
    if counts:
        print(f"[0017] Remapped JobOrder.status:")
        for old, n in sorted(counts.items()):
            print(f"[0017]   {old!r:20} -> {_MAP[old]!r:20}  ({n} rows)")
    else:
        print("[0017] No legacy statuses to remap (DB was already clean).")


def reverse_noop(apps, schema_editor):
    # Forward-only migration. Rolling back the choices would
    # re-enable the legacy values, but the data was already
    # remapped and we don't know the original mapping. So the
    # reverse is a no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0015_alter_joborder_status_choices"),
    ]

    operations = [
        migrations.RunPython(remap, reverse_noop),
    ]
