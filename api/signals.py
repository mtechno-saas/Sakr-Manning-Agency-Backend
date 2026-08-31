"""
Django signals for the api app.

Currently a single signal: ``SeaService.post_save`` triggers an
overlap dedup (half-open, longer record wins) for the same user's
records, as a final safety net for any code path that creates or
updates a ``SeaService`` without going through the explicit dedup
in ``SeaServiceViewSet.perform_create`` / ``perform_update`` or
``SeafarerApplicationSerializer.update``.

The signal is idempotent and safe:
  * ``post_save`` fires on create AND update but not on delete, so
    the dedup's own ``.delete()`` calls don't re-trigger it.
  * Each run touches at most one other row (the overlap victim);
    nested overlap dedups converge in O(1) extra work.
  * Records with unparseable dates are left alone by the dedup
    helper, so they pass through unchanged.

The pre-existing dedups in the viewset + serializer are still the
first line of defense — this signal just guarantees no path can
slip a duplicate into the DB.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="api.SeaService")
def dedupe_sea_service_on_save(sender, instance, created, **kwargs):
    """After any SeaService row is saved, drop any sibling rows for
    the same user that overlap with it (using the half-open rule;
    longer record wins). Skipped silently if the user has no
    user_id or the dates are unparseable.
    """
    from ai_document.views import _dedupe_overlapping_sea_service
    from api.models import SeaService

    user_id = instance.user_id
    if not user_id:
        return

    siblings = list(
        SeaService.objects.filter(user_id=user_id).order_by("id")
    )
    dicts = []
    for r in siblings:
        dicts.append({
            "id": r.id,
            "vessel_name_imo": r.vessel_name_imo or "",
            "vessel_name": r.vessel_name or "",
            "company_name": r.company_name or "",
            "rank": r.rank or "",
            "signed_on": r.signed_on,
            "signed_off": r.signed_off,
            "period": r.period or "",
        })

    kept, dropped = _dedupe_overlapping_sea_service(dicts)
    kept_ids = {d["id"] for d in kept if d.get("id") is not None}
    if instance.id in kept_ids:
        ids_to_delete = [
            d["record"]["id"]
            for d in dropped
            if d.get("record", {}).get("id") is not None
        ]
    else:
        # The just-saved row lost — delete it and the others.
        # The kept winner stays.
        ids_to_delete = [
            d["record"]["id"]
            for d in dropped
            if d.get("record", {}).get("id") is not None
        ]
        if instance.id not in ids_to_delete:
            ids_to_delete.append(instance.id)

    if ids_to_delete:
        SeaService.objects.filter(id__in=ids_to_delete).delete()
