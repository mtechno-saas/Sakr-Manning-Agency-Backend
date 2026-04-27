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


class UserPermission(BasePermission):
    """
    User management permissions:
    - Admin: Full access to all users
    - HR Manager: Can manage non-admin users
    - Recruiter: Can view users, edit candidates
    - Employee: Can only view/edit own profile
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'Admin':
            return True
        
        if request.user.role == 'HR Manager':
            # Can't create admins
            if request.method == 'POST':
                role = request.data.get('role', 'Employee')
                return role != 'Admin'
            return True
        
        if request.user.role == 'Recruiter':
            return request.method in SAFE_METHODS
        
        # Employee - handled at object level
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'Admin':
            return True
        
        if request.user.role == 'HR Manager':
            # Can't modify admins
            return obj.role != 'Admin'
        
        if request.user.role == 'Recruiter':
            return request.method in SAFE_METHODS
        
        # Employee can only access own profile
        return obj == request.user


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