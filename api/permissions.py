# # # api/permissions.py
# # from rest_framework.permissions import BasePermission, SAFE_METHODS

# # class IsAdminOrReadOnly(BasePermission):
# #     """
# #     Allows full access to admin users, but only read-only access to others.
# #     """
# #     def has_permission(self, request, view):
# #         # Read permissions are allowed to any request,
# #         # so we'll always allow GET, HEAD or OPTIONS requests.
# #         if request.method in SAFE_METHODS:
# #             return True

# #         # Write permissions are only allowed to users in the "Admin" group.
# #         return request.user and request.user.groups.filter(name='Admin').exists()

# # class IsHROrReadOnly(BasePermission):
# #     """
# #     Allows HR to edit users, but others can only view.
# #     """
# #     def has_permission(self, request, view):
# #         if request.method in SAFE_METHODS:
# #             return True
# #         # Check if the user is in the "HR" or "Admin" group for write access.
# #         return request.user and request.user.groups.filter(name__in=['HR', 'Admin']).exists()

# # api/permissions.py
# from rest_framework.permissions import BasePermission, SAFE_METHODS

# class IsAdminOrReadOnly(BasePermission):
#     """
#     Allows full access to admin users, but only read-only access to others.
#     """
#     def has_permission(self, request, view):
#         # Read permissions are allowed to any request,
#         # so we'll always allow GET, HEAD or OPTIONS requests.
#         if request.method in SAFE_METHODS:
#             return True

#         # Write permissions are only allowed to users in the "Admin" group.
#         return request.user and request.user.groups.filter(name='Admin').exists()

# class IsHROrReadOnly(BasePermission):
#     """
#     Allows HR to edit users, but others can only view.
#     """
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         # Check if the user is in the "HR" or "Admin" group for write access.
#         return request.user and request.user.groups.filter(name__in=['HR', 'Admin']).exists()

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .roles import canonical_role


class IsAdmin(BasePermission):
    """Full system access - Admin only"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'Admin'
        )


class IsHRManager(BasePermission):
    """HR Manager or Admin access"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['Admin', 'HR Manager']
        )


class IsRecruiter(BasePermission):
    """Recruiter, HR Manager, or Admin access"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['Admin', 'HR Manager', 'Recruiter']
        )


class IsEmployee(BasePermission):
    """Any authenticated user"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsHROrReadOnly(BasePermission):
    """HR/Admin can edit, others can only read"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ['Admin', 'HR Manager']


class IsOwnerOrHR(BasePermission):
    """User can access own data, HR/Admin can access all"""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['Admin', 'HR Manager']:
            return True
        # Check if the object belongs to the user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'candidate'):
            return obj.candidate == request.user
        return obj == request.user


class RoleBasedPermission(BasePermission):
    """
    Dynamic role-based permission.
    Define allowed_roles in the view.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        allowed_roles = getattr(view, 'allowed_roles', ['Admin'])
        return request.user.role in allowed_roles


# Permission mapping for different operations
class CVPermission(BasePermission):
    """
    CV Management permissions:
    - Admin/HR: Full access
    - Recruiter: Can view and update status
    - Employee: Can only view/submit own CVs
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role in ['Admin', 'HR Manager']:
            return True
        
        if request.user.role == 'Recruiter':
            return request.method in SAFE_METHODS or request.method == 'PATCH'
        
        # Employee can only create (submit CV) or view
        if request.user.role == 'Employee':
            return request.method in ['GET', 'POST']
        
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return True
        # Employee can only access own CV submissions
        return obj.user == request.user


class InterviewPermission(BasePermission):
    """
    Interview permissions:
    - Admin/HR/Recruiter: Full access
    - Employee: Can only view own interviews
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return True
        
        # Employee can only view
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return True
        return obj.candidate == request.user


class FinancePermission(BasePermission):
    """
    Finance permissions:
    - Admin/HR: Full access
    - Recruiter: Read only
    - Employee: Can only view own records
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role in ['Admin', 'HR Manager']:
            return True
        
        # Recruiter and Employee can only view
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['Admin', 'HR Manager']:
            return True
        return obj.user == request.user


class CompanyPermission(BasePermission):
    """
    Company permissions:
    - Admin: Full access
    - HR/Recruiter: Can view and edit
    - Employee: Read only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'Admin':
            return True
        
        if request.user.role in ['HR Manager', 'Recruiter']:
            return request.method in SAFE_METHODS + ('PUT', 'PATCH')
        
        # Employee can only view
        return request.method in SAFE_METHODS


class ContractPermission(BasePermission):
    """
    Contract/Document permissions:
    - Admin/HR: Full access
    - Recruiter: Read only
    - Employee: Can only view own contracts
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role in ['Admin', 'HR Manager']:
            return True
        
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['Admin', 'HR Manager']:
            return True
        return obj.user == request.user


# ---------------------------------------------------------------------------
# Authority: who may write WHICH field
# ---------------------------------------------------------------------------
#
# Checking the ROLE alone is not enough.  A caller that is allowed to touch
# an account is not necessarily allowed to change what that account IS:
#
#   role              decides what the API lets the account do
#   is_superuser      Django's "bypass every permission" flag
#   is_staff          grants access to the Django admin site
#   groups            Django groups carry model permissions
#   user_permissions  direct Django model permissions
#
# Every one of those used to be writable by anybody who could reach the
# endpoint, which meant an ordinary Employee could PATCH its own record
# with {"role": "Admin"} -- or {"is_superuser": true, "groups": [1]} -- and
# become an administrator.

PRIVILEGE_FLAG_FIELDS = ('is_superuser', 'is_staff')
PRIVILEGE_M2M_FIELDS = ('groups', 'user_permissions')


def _actor_role(user):
    """The caller's role, trimmed."""
    return (getattr(user, 'role', '') or '').strip()


def is_admin_user(user):
    """True when the caller is an administrator.

    Both the role field and Django's superuser flag count: the live Admin
    accounts carry ``is_superuser=True``, and a Django superuser bypasses
    every permission check in the framework.
    """
    return bool(getattr(user, 'is_superuser', False)) or _actor_role(user) == 'Admin'


def _requested_role(request):
    """The canonical role the payload asks for, or ``None``."""
    data = getattr(request, 'data', None)
    if not data:
        return None
    try:
        raw = data.get('role')
    except AttributeError:
        return None
    if raw is None:
        return None
    return canonical_role(raw)


def as_bool(value):
    """Interpret a payload value as a boolean.

    Multipart payloads carry booleans as STRINGS, and ``bool("false")`` is
    True in Python.  Reading it naively would invent a privilege change
    that is not there and refuse a perfectly ordinary edit.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('true', '1', 'yes', 'on')
    return bool(value)


def _payload_values(data, field):
    """Every value the payload carries for ``field``.

    A multipart body can repeat a field, and ``QueryDict.get`` would only
    return the last one.
    """
    getlist = getattr(data, 'getlist', None)
    if callable(getlist):
        return getlist(field)
    raw = data.get(field)
    if isinstance(raw, (list, tuple)):
        return list(raw)
    return [] if raw is None else [raw]


def _changed_privilege_fields(request, obj):
    """Which authority-bearing fields this payload would actually change.

    Comparing against the CURRENT value is what keeps harmless round-trips
    working: the dashboard sends back the whole user object, so a PATCH
    routinely contains ``is_superuser: false`` for an account that already
    has ``is_superuser: false``.  That is not a privilege change and must
    not be treated as one.
    """
    data = getattr(request, 'data', None)
    if not data:
        return []

    changed = []
    for field in PRIVILEGE_FLAG_FIELDS:
        if field not in data:
            continue
        incoming = as_bool(data.get(field))
        if incoming != bool(getattr(obj, field, False)):
            changed.append(field)

    for field in PRIVILEGE_M2M_FIELDS:
        if field not in data:
            continue
        requested = set()
        for raw in _payload_values(data, field):
            try:
                requested.add(int(raw))
            except (TypeError, ValueError):
                continue  # malformed -- the serializer reports it
        current = set(getattr(obj, field).values_list('id', flat=True))
        if requested != current:
            changed.append(field)

    return changed


def _is_detail_route(view):
    """True when the request targets ONE existing object.

    The router puts the looked-up id in ``view.kwargs``; a collection
    route has no such key.  This is what separates "update my own
    profile" (a detail route, then limited by the object-level rule)
    from "create a new account" (a collection route, which has no object
    to limit at all).
    """
    kwargs = getattr(view, 'kwargs', None) or {}
    if 'pk' in kwargs:
        return True
    # DRF's own naming: these actions always operate on a single object.
    return getattr(view, 'action', None) in (
        'retrieve', 'update', 'partial_update', 'destroy',
    )


class UserPermission(BasePermission):
    """
    User management permissions:
    - Admin: Full access to all users
    - HR Manager: Can manage non-admin users
    - Recruiter: Can view users, edit candidates
    - Employee: Can only view/edit own profile

    The rules are about AUTHORITY, not only about the object: a caller may
    only write the fields that carry authority if it is allowed to do so.
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        role = _actor_role(user)

        if role == 'HR Manager':
            if request.method == 'POST':
                # An HR Manager may create accounts, but never an Admin.
                #
                # The comparison MUST be against the CANONICAL spelling.
                # It used to be a literal ``!= 'Admin'``, so a payload of
                # {"role": "admin"} passed the gate and the serializer then
                # normalised it up to "Admin" -- an HR Manager could mint
                # an Admin account.
                requested = canonical_role(request.data.get('role', 'Employee'))
                return requested != 'Admin'
            return True

        if role == 'Recruiter':
            return request.method in SAFE_METHODS

        # Employee: own profile only.
        #
        # The object-level rule ("you may only touch yourself") cannot
        # contain a CREATE -- a brand new account has no object yet. So a
        # collection-level write has to be denied here, otherwise any
        # Employee could POST a new Admin.
        #
        # A write on a DETAIL route is allowed through to the
        # object-level rule, which limits it to their own record.
        if request.method in SAFE_METHODS:
            return True
        return _is_detail_route(view)

    def has_object_permission(self, request, view, obj):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        role = _actor_role(user)
        target_role = (getattr(obj, 'role', '') or '').strip()

        # The authority-bearing flags are Admin-only, whoever the target
        # is. Without this an Employee could grant itself is_superuser /
        # is_staff / Django groups on its own record.
        if _changed_privilege_fields(request, obj):
            return False

        requested_role = _requested_role(request)
        role_change = requested_role is not None and requested_role != target_role

        if role == 'HR Manager':
            # An HR Manager cannot touch an Admin account...
            if target_role == 'Admin':
                return False
            # ...and cannot promote anybody to Admin.
            if role_change and requested_role == 'Admin':
                return False
            return True

        if role == 'Recruiter':
            return request.method in SAFE_METHODS

        # Employee: own profile only, and never a role change.
        if obj != user:
            return False
        if role_change:
            return False
        return True


class IsAdminRole(BasePermission):
    """Only an administrator may pass.

    Used by the staff-account creation endpoint: minting an Admin is the
    most privileged thing this API can do, so it is not delegated to an
    HR Manager.
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return is_admin_user(user)


class IsOwnerOrAdminDownload(BasePermission):
    """
    Download permission: only the profile owner or Admin can download documents.
    Used on UserViewSet download actions.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin always has access
        if request.user.role == 'Admin':
            return True
        # Owner can access their own profile
        return obj == request.user


class JobOrderPermission(BasePermission):
    """
    Job Order & Position permissions:
    - Admin/HR/Recruiter: Full CRUD
    - Employee: Read-only + 'apply' action (POST)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin, HR, Recruiter — full access
        if request.user.role in ['Admin', 'HR Manager', 'Recruiter']:
            return True

        # Employee — read-only + apply action
        if request.user.role == 'Employee':
            # Allow GET (list, retrieve)
            if request.method in SAFE_METHODS:
                return True
            # Allow POST only on the 'apply' action
            if request.method == 'POST' and getattr(view, 'action', None) == 'apply':
                return True
            return False

        return False