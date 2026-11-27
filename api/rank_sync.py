"""
Keeping a POSITION and its RANK CODE in step.

The problem
-----------
A person has a POSITION (what they apply for / hold) and a RANK CODE (the
coded identifier issued for that position). In the database those two live
in different places:

  * ``Users.application_for_position`` -- the position on the profile, as a
    free-text string (the canonical name of a ``Rank``).
  * ``CVSubmission.position`` -- the position of one application, a FK to
    ``Rank``.
  * ``UserRank`` -- the rank *assignments*: one row per (person, rank) pair,
    each carrying the ``assigned_code`` that was issued for it.

Nothing kept them in step. Every read path picked the NEWEST ``UserRank``
row ("last write wins"), so:

  * an admin who changed an application's position from Master to Baker
    kept seeing the OLD position's code whenever the applicant held more
    than one rank -- the code on screen belonged to a rank that was not the
    one in the POSITION column;
  * and changing the position back again changed nothing visible, because
    the newest row never moved.

What this module does
---------------------
One rule, used by every read and write path:

    **the rank shown is the rank of the position shown.**

  * :func:`rank_for_name`       -- resolve a position name to its ``Rank``
  * :func:`assignment_for`      -- the ``UserRank`` a person holds for a rank
  * :func:`ensure_assignment`   -- make sure such an assignment exists
  * :func:`coded_entries`       -- the coded-rank entry to display
  * :func:`ordered_assignments` -- the assignments, the relevant one first

Nothing here deletes a rank assignment: a person who was a Master and is now
a Baker legitimately holds both codes. Only the *display* follows the
position. The one write this module performs is :func:`ensure_assignment`,
which adds an assignment when the person does not hold the new position yet
-- that is what makes "change the position -> the rank code changes" true
for somebody who did not already hold that rank.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def rank_for_name(name):
    """Return the ``Rank`` row for a position name, or ``None``.

    Resolution order:

      1. an existing rank whose name matches exactly (case-insensitive)
      2. the canonical ``RANKS`` table (code + name) -- the source of truth
         for the position names the system issues
      3. a loose "contains" match against that table

    Never creates a row: this is called while serialising, and a GET must
    not write. A position the system does not know is simply unknown, and
    the caller falls back to the person's existing assignment.
    """
    from api.models import RANKS, Rank

    if not name:
        return None
    name = str(name).strip()
    if not name:
        return None

    rank = Rank.objects.filter(name__iexact=name).first()
    if rank is not None:
        return rank

    low = name.lower()
    for code, rank_name in RANKS:
        if str(rank_name).lower().strip() == low:
            return Rank.objects.filter(code=code).first()
    for code, rank_name in RANKS:
        rank_name = str(rank_name).lower()
        if low in rank_name or rank_name in low:
            return Rank.objects.filter(code=code).first()
    return None


def assignment_for(user, rank):
    """The ``UserRank`` a person holds for a given rank (newest wins).

    ``rank`` may be a ``Rank`` instance or a rank id.

    The assignments are read through the related manager, so a queryset
    that prefetched them (the user list does) costs no extra query.
    """
    if user is None or rank is None:
        return None
    rank_id = getattr(rank, 'id', rank)
    try:
        best = None
        for user_rank in user.user_ranks.all():
            if user_rank.rank_id != rank_id:
                continue
            if best is None or user_rank.id > best.id:
                best = user_rank
        return best
    except (ValueError, TypeError):
        return None


def ensure_assignment(user, rank):
    """Make sure the person holds an assignment for this rank.

    An existing assignment is reused, so saving the same position twice
    never issues a second code. When there is none, one is created -- that
    is what makes "change the position -> the rank code changes" true for
    somebody who did not hold the new rank yet.

    Never raises: a failure to issue a code must not fail the save that
    triggered it.
    """
    if user is None or rank is None:
        return None

    existing = assignment_for(user, rank)
    if existing is not None:
        return existing

    from api.models import UserRank

    try:
        return UserRank.objects.create(user=user, rank=rank)
    except Exception:
        # The model's own auto-numbering failed (for example a pre-existing
        # row whose assigned_code is not numeric). Retry with an explicit
        # code so the person still ends up with an assignment.
        logger.exception(
            "rank_sync: auto-numbering failed for rank %s (user %s)",
            getattr(rank, 'code', rank), getattr(user, 'id', None),
        )
        code = safe_assigned_code(rank)
        if not code:
            return None
        try:
            return UserRank.objects.create(user=user, rank=rank, assigned_code=code)
        except Exception:
            logger.exception(
                "rank_sync: could not create the rank assignment for user %s",
                getattr(user, 'id', None),
            )
            return None


def safe_assigned_code(rank):
    """A collision-free assigned code for a rank.

    Used only as a fallback when the model's own numbering fails. The
    number is the highest one actually in use for the rank's prefix, so it
    cannot collide with an existing code.
    """
    from api.models import UserRank

    prefix = str(getattr(rank, 'code', '') or 'RANK').split('.')[0]
    highest = 0
    rows = (
        UserRank.objects
        .filter(rank__code__startswith=prefix)
        .exclude(assigned_code__isnull=True)
        .exclude(assigned_code='')
    )
    for user_rank in rows:
        try:
            highest = max(highest, int(str(user_rank.assigned_code).split('.')[-1]))
        except (TypeError, ValueError):
            continue
    return f"{prefix}.{highest + 1:03d}"


def rank_for_user_position(user, position_name):
    """The ``Rank`` of a person's position.

    Prefers an assignment the person already holds whose rank name matches
    the position -- that is free, the assignments are usually prefetched --
    and falls back to the canonical position table.
    """
    if user is None or not position_name:
        return None
    wanted = str(position_name).strip().lower()
    if wanted:
        for user_rank in user.user_ranks.all():
            rank = user_rank.rank
            if rank is not None and str(rank.name or '').strip().lower() == wanted:
                return rank
    return rank_for_name(position_name)


def coded_entries(user, rank=None):
    """The coded-rank entry to display for a person, in the context of ``rank``.

    Returns a list with at most one entry -- the shape the dashboard
    expects::

        [{"assigned_code": "DR-32.001", "rank_code": "DR-32.000",
          "rank_name": "Baker"}]

    The rules:

      1. the person's assignment for ``rank`` wins (the position's own code)
      2. if the position is known but not assigned, the rank's own code is
         returned with no assigned code -- the display still follows the
         position
      3. otherwise the person's newest assignment is used
    """
    if user is None:
        return []

    rows = _assignments(user)

    if rank is not None:
        for user_rank in rows:
            if user_rank.rank_id == rank.id:
                return [_entry(
                    user_rank.assigned_code,
                    user_rank.rank.code,
                    user_rank.rank.name,
                )]
        return [{
            'assigned_code': None,
            'rank_code': getattr(rank, 'code', None),
            'rank_name': getattr(rank, 'name', None),
        }]

    if not rows:
        return []
    latest = rows[0]
    return [_entry(latest.assigned_code, latest.rank.code, latest.rank.name)]


def ordered_assignments(user, rank=None):
    """The person's rank assignments, the one for ``rank`` first.

    The dashboard reads ``ranks[0]`` for its Rank and Assigned Code
    columns, so the assignment that matches the position has to come
    first. The sort is stable, so the remaining assignments keep their
    newest-first order.
    """
    rows = _assignments(user)
    if rank is not None:
        rows.sort(key=lambda user_rank: user_rank.rank_id != rank.id)
    return rows


def _assignments(user):
    """The person's assignments, newest first."""
    rows = list(user.user_ranks.all())
    rows.sort(key=lambda user_rank: user_rank.id, reverse=True)
    return rows


def _entry(assigned_code, rank_code, rank_name):
    return {
        'assigned_code': assigned_code,
        'rank_code': rank_code,
        'rank_name': rank_name,
    }
