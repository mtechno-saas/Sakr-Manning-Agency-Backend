"""
Audit trail for destructive / security-relevant user actions.

Why this exists
---------------
The gunicorn access log records *that* a DELETE happened but never *who*
did it -- every request reaches gunicorn through the nginx proxy, so the
access log shows ``127.0.0.1`` for every caller. When a set of accounts
disappeared from the live database we could only tell it was "a browser
session using the bulk-delete UI", not which account was responsible.

Every line below is a single, greppable, structured record:

    [USER-AUDIT] action=bulk_delete actor_id=13 actor_email=admin@sakrshipping.com
    actor_role=Admin target_ids=[51, 52] count=2 ip=203.0.113.7
    ua="Mozilla/5.0 ..."

Where it lands
--------------
The ``audit`` logger is configured in ``saker/settings.py`` with two
handlers: the console handler (which gunicorn mirrors into
``/var/log/gunicorn/error.log``) and a dedicated file handler writing to
``/var/log/gunicorn/user_audit.log``. The dedicated file survives
gunicorn's error-log rotation and keeps the audit trail out of the error
noise.

Grep it with::

    grep USER-AUDIT /var/log/gunicorn/user_audit.log
"""

import logging

logger = logging.getLogger('audit')

# Keys whose values are wrapped in repr() so a value containing spaces
# (a User-Agent string, a free-text field) cannot break the key=value
# parsing of the log line. `target_email` is deliberately NOT quoted --
# an email address can never contain a space, and quoting it would make
# the line inconsistent with `actor_email`.
_QUOTED_KEYS = {'ua', 'fields', 'target_role'}


def _client_ip(request):
    """Best-effort original client IP behind the nginx proxy.

    nginx sets ``X-Forwarded-For`` to ``$proxy_add_x_forwarded_for``, so
    the left-most entry is the original client and the rest are the
    proxies it passed through. Falls back to ``REMOTE_ADDR`` (which is
    the proxy itself) when the header is absent.
    """
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '') or ''
    if forwarded:
        first = forwarded.split(',')[0].strip()
        if first:
            return first
    return request.META.get('REMOTE_ADDR', 'unknown')


def _actor(request):
    """Return ``(id, email, role)`` for the authenticated caller."""
    user = getattr(request, 'user', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return None, None, None
    return (
        getattr(user, 'id', None),
        getattr(user, 'email', ''),
        getattr(user, 'role', ''),
    )


def log_user_action(request, action, target_ids=None, extra=None):
    """Emit one audit record for a user-management action.

    :param request: the DRF request (used for the actor and the client IP)
    :param action: short verb, e.g. ``bulk_delete`` / ``delete_user``
    :param target_ids: iterable of affected user ids
    :param extra: optional dict of additional key/value pairs
    """
    actor_id, actor_email, actor_role = _actor(request)
    # Sorted so the same request always produces the same line -- the
    # queryset that supplies the ids has no guaranteed order.
    ids = sorted({int(i) for i in (target_ids or []) if str(i).isdigit()})

    fields = [
        '[USER-AUDIT]',
        f'action={action}',
        f'actor_id={actor_id}',
        f'actor_email={actor_email}',
        f'actor_role={actor_role}',
        f'target_ids={ids}',
        f'count={len(ids)}',
        f'ip={_client_ip(request)}',
    ]

    extra = extra or {}
    for key, value in extra.items():
        if key in _QUOTED_KEYS:
            fields.append(f'{key}={value!r}')
        else:
            fields.append(f'{key}={value}')

    fields.append(f'ua={request.META.get("HTTP_USER_AGENT", "")!r}')

    logger.info(' '.join(fields))
