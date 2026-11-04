"""
Canonical role spellings -- one implementation, two consumers.

``Users.ROLE_CHOICES`` is canonical ("Admin", "HR Manager", "Recruiter",
"Employee", "Crew"), but the dashboard's add-user form posts lower-case
values ("employee", "crew", "admin") and the users table uses the UI
*label* "applicant" for the Employee role.

Two places need to agree on what a spelling means:

  * ``api.serializer.RoleChoiceField`` -- normalises the value on the way IN
  * ``api.permissions.UserPermission`` -- decides whether the caller is
    allowed to write that role

They MUST use the same table.  When they did not, the permission layer
compared the raw payload against the literal string ``"Admin"`` while the
serializer normalised ``"admin"`` UP to ``"Admin"`` on the way in, so an
HR Manager could mint an Admin account by sending a lower-case role --
and the permission check, which is supposed to be the gate, waved it
through.

This module is the single source of truth.  Import it from both places
rather than re-implementing the alias table.
"""

from __future__ import annotations

# Aliases the UI sends instead of the stored role value.
ROLE_ALIASES = {
    # "Applicant" is the UI *label* for the Employee role -- see the
    # users table dropdown: <option value="Employee">Applicant</option>.
    'applicant': 'Employee',
    'administrator': 'Admin',
    'hr': 'HR Manager',
    'hr_manager': 'HR Manager',
    'hrmanager': 'HR Manager',
}


def canonical_role(value, choices=None):
    """Return the canonical spelling of ``value``, or ``None``.

    ``None`` means "this is not a role we recognise".  The caller decides
    what that means: the serializer turns it into a validation error, the
    permission layer treats it as "not a role change" and lets the
    serializer reject it.

    Resolution order:

    1. exact match against the canonical choices
    2. the alias table above ("administrator" -> "Admin")
    3. case-insensitive match ("admin" -> "Admin", "hr manager" -> "HR Manager")

    ``choices`` defaults to ``Users.ROLE_CHOICES``.  It is imported lazily
    so that ``api.roles`` stays importable from ``api.models``'s import
    chain without creating a cycle.
    """
    if not isinstance(value, str):
        return None

    if choices is None:
        from .models import Users

        choices = [c for c, _ in Users.ROLE_CHOICES]
    choices = list(choices)

    stripped = value.strip()
    if stripped in choices:
        return stripped

    key = stripped.lower().replace(' ', '_')
    alias = ROLE_ALIASES.get(key)
    if alias in choices:
        return alias

    for choice in choices:
        if choice.lower().replace(' ', '_') == key:
            return choice
    return None
