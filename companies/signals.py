"""
Signals for the companies app.

The most important one: when a Contract becomes Active/Signed (or
loses that status) OR when a JobOrderPosition's quantity changes,
re-check the parent JobOrder and auto-transition its status to
"Fulfilled" if all positions are fully filled.

One-way only: we do NOT auto-revert Fulfilled back to Open. The
admin can manually flip it if a position reopens.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.models import Contract
from .models import JobOrder, JobOrderPosition


# Statuses that can auto-promote to Fulfilled. Cancelled / Closed /
# Hold are intentionally excluded so a manual override sticks.
_AUTO_PROMOTABLE_STATUSES = {
    "Pending", "Open", "In Progress", "Active",
}


def _maybe_promote_to_fulfilled(job_order: JobOrder) -> None:
    """
    If every position under `job_order` is fully filled, AND the
    current status is one of the auto-promotable ones, set the
    status to "Fulfilled" and save. No-op otherwise.
    """
    if job_order.status not in _AUTO_PROMOTABLE_STATUSES:
        return
    if not job_order.is_fully_filled():
        return
    job_order.status = "Fulfilled"
    # update_fields avoids touching unrelated columns.
    job_order.save(update_fields=["status", "updated_at"])


@receiver(post_save, sender=Contract)
def contract_saved_check_parent_jo(sender, instance, **kwargs):
    """
    When a Contract is created or its status changes, check the
    parent JobOrder (via JobOrderPosition) and auto-promote if
    every position is now fully filled.
    """
    pos = instance.job_position
    if pos is None:
        return
    _maybe_promote_to_fulfilled(pos.job_order)


@receiver(post_delete, sender=Contract)
def contract_deleted_check_parent_jo(sender, instance, **kwargs):
    """
    When a Contract is deleted, the parent JobOrder may have just
    lost a filled slot. We re-evaluate the rollup; if the order is
    already "Fulfilled" the one-way rule means we leave it alone.
    """
    pos = instance.job_position
    if pos is None:
        return
    _maybe_promote_to_fulfilled(pos.job_order)


@receiver(post_save, sender=JobOrderPosition)
@receiver(post_delete, sender=JobOrderPosition)
def position_changed_check_parent_jo(sender, instance, **kwargs):
    """
    When a position is created, its quantity changes, or it is
    deleted, re-evaluate the parent JobOrder's rollup.
    """
    if instance.job_order_id is None:
        return
    try:
        jo = JobOrder.objects.get(pk=instance.job_order_id)
    except JobOrder.DoesNotExist:
        return
    _maybe_promote_to_fulfilled(jo)
