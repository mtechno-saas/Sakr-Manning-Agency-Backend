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
    ua="Mozilla/5.0 ..." xff="203.0.113.7, 162.158.217.38"

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
# (a User-Agent string, a free-text field, an attacker-supplied email)
# cannot break the key=value parsing of the log line. `target_email` is
# deliberately NOT quoted -- a real email address can never contain a
# space, and quoting it would make the line inconsistent with
# `actor_email`.
_QUOTED_KEYS = {'ua', 'fields', 'target_role', 'email'}


def _client_ip(request):
    """Best-effort original client IP.

    The production topology is::

        client -> Cloudflare -> nginx -> gunicorn (127.0.0.1:8000)

    so Django never sees the client's socket address: REMOTE_ADDR is
    always 127.0.0.1, and the *nginx* access log shows a Cloudflare edge
    address (162.158.x / 162.159.x / 104.16.x ...).

    Three headers carry the real address, in descending order of
    trustworthiness:

    1. ``CF-Connecting-IP`` -- Cloudflare's authoritative header. It
       holds exactly ONE address and Cloudflare *overwrites* it (never
       appends), so it cannot be spoofed by a request that travelled
       through Cloudflare. This is what Cloudflare's own docs tell you
       to use for logging: "look at CF-Connecting-IP or True-Client-IP
       instead of X-Forwarded-For".
    2. ``True-Client-IP`` -- the Enterprise-plan alias of the same
       value.
    3. ``X-Real-IP`` -- nginx's own output. It is only meaningful when
       nginx's ``real_ip`` module is configured (see the deployment
       notes in the README of this module's PR); otherwise it is just
       whatever nginx forwarded.
    4. ``X-Forwarded-For`` -- a comma-separated chain that every proxy
       *appends* to. Cloudflare appends, so a client-supplied value
       stays at the LEFT of the chain and is therefore the least
       trustworthy entry. We read the left-most entry, the conventional
       choice for an append-style chain, and keep the raw chain in the
       ``xff=`` field so the evidence survives.

    Residual risk: a request that reaches the origin *directly* (bypassing
    Cloudflare) could carry a forged CF-Connecting-IP. That is why the
    nginx vhost must use ``real_ip_header CF-Connecting-IP`` with
    ``set_real_ip_from`` limited to Cloudflare's published ranges -- that
    is the trust anchor. See the deployment notes.
    """
    for header in (
        'HTTP_CF_CONNECTING_IP',
        'HTTP_TRUE_CLIENT_IP',
        'HTTP_X_REAL_IP',
    ):
        value = (request.META.get(header) or '').strip()
        if value:
            return value.split(',')[0].strip()

    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '') or ''
    if forwarded:
        first = forwarded.split(',')[0].strip()
        if first:
            return first

    return request.META.get('REMOTE_ADDR', 'unknown')


def _forwarded_chain(request):
    """The raw X-Forwarded-For chain, kept as forensic evidence."""
    return (request.META.get('HTTP_X_FORWARDED_FOR', '') or '').strip()


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


def log_user_action(request, action, target_ids=None, extra=None, actor=None):
    """Emit one audit record for a user-management action.

    :param request: the DRF request (used for the actor and the client IP)
    :param action: short verb, e.g. ``bulk_delete`` / ``delete_user``
    :param target_ids: iterable of affected user ids
    :param extra: optional dict of additional key/value pairs
    :param actor: optional ``(id, email, role)`` override, for events that
        happen before the request is authenticated (a login, for example)
    """
    if actor is None:
        actor_id, actor_email, actor_role = _actor(request)
    else:
        actor_id, actor_email, actor_role = actor

    # Sorted so the same request always produces the same line -- the
    # queryset that supplies the ids has no guaranteed order.
    ids = sorted({int(i) for i in (target_ids or []) if str(i).isdigit()})

    fields = ['[USER-AUDIT]', f'action={action}']

    # An anonymous request has no actor to name (a login, a failed
    # login). Omit the fields entirely rather than printing "None".
    if actor_id is not None or actor_email:
        fields.append(f'actor_id={actor_id}')
        fields.append(f'actor_email={actor_email}')
        fields.append(f'actor_role={actor_role}')

    fields.append(f'target_ids={ids}')
    fields.append(f'count={len(ids)}')
    fields.append(f'ip={_client_ip(request)}')

    extra = extra or {}
    for key, value in extra.items():
        if key in _QUOTED_KEYS:
            fields.append(f'{key}={value!r}')
        else:
            fields.append(f'{key}={value}')

    chain = _forwarded_chain(request)
    if chain:
        fields.append(f'xff={chain!r}')

    fields.append(f'ua={request.META.get("HTTP_USER_AGENT", "")!r}')

    logger.info(' '.join(fields))
