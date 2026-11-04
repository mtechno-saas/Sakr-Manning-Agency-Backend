"""
Per-account permission grants -- "what ELSE may this person do?".

Why this exists
---------------
The API authorises by ROLE. ``Users.role`` is one of Admin / HR Manager /
Recruiter / Employee / Crew, and every permission class in
:mod:`api.permissions` branches on that single value:

    Admin       -> everything
    HR Manager  -> everything except creating Admins
    Recruiter   -> read-only (mostly)
    Employee    -> own records only

That is a blunt instrument. There is no way to say "this HR Manager may
also look at the finance records" or "this Recruiter may also manage
users" without inventing a new role for every combination.

So: a permission grant is an EXTRA capability attached to one account.
It is stored on the account (``Users.granted_permissions``) and only an
Admin can set it.

The rules
---------
1. **Additive only.** A grant can ADD access on top of the role. It can
   never take access away. An HR Manager with a grant still has
   everything an HR Manager has; the grant only widens it. To narrow
   somebody, change their role.
2. **Never grants a role.** Granting ``users.write`` lets somebody EDIT
   accounts; it does not let them change a role or touch the
   authority-bearing fields (``is_superuser``, ``is_staff``, ``groups``,
   ``user_permissions``, ``granted_permissions``). Those stay Admin-only.
3. **Never grants creation.** Creating accounts stays Admin / HR Manager.
4. **Admins are unaffected.** An Admin already has everything, so a grant
   on an Admin account does nothing. Grants are for HR Managers and
   Recruiters.

The catalogue
-------------
Every permission below maps onto a permission class that already exists
in :mod:`api.permissions`, so a grant is enforced in the same place the
role is enforced -- there is no second, parallel authorisation path to
keep in sync.

    key                  resource          effect
    -------------------  ---------------  ---------------------------------
    users.view_all       users             see every account, not just self
    users.write          users             edit accounts (never their role)
    users.delete         users             delete accounts
    contracts.view       contracts         see every contract
    contracts.write      contracts         create / edit / delete contracts
    companies.view       companies         see every company
    companies.write      companies         create / edit / delete companies
    interviews.view      interviews        see every interview
    interviews.write     interviews        create / edit / delete interviews
    finance.view         finance           see every finance record
    finance.write        finance           create / edit / delete finance
    cv_submissions.view  cv_submissions    see every CV submission
    cv_submissions.write cv_submissions    create / edit / delete CVs
    certificates.view    certificates      see every certificate
    certificates.write   certificates      create / edit / delete certs
    job_orders.view      job_orders        see every job order
    job_orders.write     job_orders        create / edit / delete job orders
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# The catalogue
# ---------------------------------------------------------------------------
#
# ``key`` is the stored value. ``resource`` is the area the key belongs to
# and ``level`` is what it opens up. The label/description are what the
# frontend shows in the picker -- keep them plain enough for a non-technical
# admin to understand.

PERMISSION_CATALOG = {
    'users.view_all': {
        'resource': 'users',
        'level': 'view',
        'label': 'See all users',
        'description': 'See every account in the list, not just their own profile.',
    },
    'users.write': {
        'resource': 'users',
        'level': 'write',
        'label': 'Edit users',
        'description': 'Edit other people\'s accounts. It does NOT allow changing anyone\'s role.',
    },
    'users.delete': {
        'resource': 'users',
        'level': 'write',
        'label': 'Delete users',
        'description': 'Delete other people\'s accounts.',
    },
    'contracts.view': {
        'resource': 'contracts',
        'level': 'view',
        'label': 'See all contracts',
        'description': 'See every contract, not only their own.',
    },
    'contracts.write': {
        'resource': 'contracts',
        'level': 'write',
        'label': 'Manage contracts',
        'description': 'Create, edit and delete contracts.',
    },
    'companies.view': {
        'resource': 'companies',
        'level': 'view',
        'label': 'See all companies',
        'description': 'See every company record.',
    },
    'companies.write': {
        'resource': 'companies',
        'level': 'write',
        'label': 'Manage companies',
        'description': 'Create, edit and delete companies.',
    },
    'interviews.view': {
        'resource': 'interviews',
        'level': 'view',
        'label': 'See all interviews',
        'description': 'See every interview, not only their own.',
    },
    'interviews.write': {
        'resource': 'interviews',
        'level': 'write',
        'label': 'Manage interviews',
        'description': 'Create, edit and delete interviews.',
    },
    'finance.view': {
        'resource': 'finance',
        'level': 'view',
        'label': 'See all finance records',
        'description': 'See every finance record, not only their own.',
    },
    'finance.write': {
        'resource': 'finance',
        'level': 'write',
        'label': 'Manage finance records',
        'description': 'Create, edit and delete finance records.',
    },
    'cv_submissions.view': {
        'resource': 'cv_submissions',
        'level': 'view',
        'label': 'See all CV submissions',
        'description': 'See every CV submission, not only their own.',
    },
    'cv_submissions.write': {
        'resource': 'cv_submissions',
        'level': 'write',
        'label': 'Manage CV submissions',
        'description': 'Create, edit and delete CV submissions.',
    },
    'certificates.view': {
        'resource': 'certificates',
        'level': 'view',
        'label': 'See all certificates',
        'description': 'See every certificate.',
    },
    'certificates.write': {
        'resource': 'certificates',
        'level': 'write',
        'label': 'Manage certificates',
        'description': 'Create, edit and delete certificates.',
    },
    'job_orders.view': {
        'resource': 'job_orders',
        'level': 'view',
        'label': 'See all job orders',
        'description': 'See every job order.',
    },
    'job_orders.write': {
        'resource': 'job_orders',
        'level': 'write',
        'label': 'Manage job orders',
        'description': 'Create, edit and delete job orders.',
    },
}


# The resources a grant can apply to -- handy for the catalogue endpoint.
PERMISSION_RESOURCES = sorted({p['resource'] for p in PERMISSION_CATALOG.values()})


def catalog():
    """The catalogue as a list, sorted by resource then level."""
    def sort_key(item):
        key, meta = item
        return (meta['resource'], meta['level'], key)

    return [
        {
            'key': key,
            'resource': meta['resource'],
            'level': meta['level'],
            'label': meta['label'],
            'description': meta['description'],
        }
        for key, meta in sorted(PERMISSION_CATALOG.items(), key=sort_key)
    ]


def granted(user, permission):
    """True when this account has been granted ``permission``.

    Admins are never "granted" anything -- they already have everything,
    so a grant on an Admin account is a no-op by design.
    """
    if user is None or not getattr(user, 'is_authenticated', False):
        return False
    granted_list = getattr(user, 'granted_permissions', None) or []
    try:
        return permission in granted_list
    except TypeError:
        return False


def can_view(user, resource):
    """True when the account may see EVERY record of ``resource``.

    A write grant implies read access.
    """
    return granted(user, f'{resource}.view') or granted(user, f'{resource}.write')


def can_write(user, resource):
    """True when the account may create / edit / delete records of ``resource``."""
    return granted(user, f'{resource}.write')


def sort_permissions(keys):
    """Return the given permission keys in catalogue order.

    Keeps the stored list deterministic: two accounts with the same
    grants always read back exactly the same way.
    """
    wanted = set(keys)
    return [p['key'] for p in catalog() if p['key'] in wanted]


def validate_permissions(values):
    """Validate a list of permission keys.

    :returns: ``(clean, unknown)`` where ``clean`` is the de-duplicated
        list of valid keys in catalogue order and ``unknown`` is the list
        of keys that are not in the catalogue.
    """
    if values is None:
        return [], []
    if not isinstance(values, (list, tuple)):
        raise TypeError('permissions must be a list')

    unknown = []
    wanted = set()
    for value in values:
        if not isinstance(value, str):
            unknown.append(value)
            continue
        key = value.strip()
        if key not in PERMISSION_CATALOG:
            unknown.append(value)
            continue
        wanted.add(key)

    clean = [p['key'] for p in catalog() if p['key'] in wanted]
    return clean, unknown
