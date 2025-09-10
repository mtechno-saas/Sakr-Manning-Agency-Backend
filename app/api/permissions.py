# api/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Allows full access to admin users, but only read-only access to others.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to users in the "Admin" group.
        return request.user and request.user.groups.filter(name='Admin').exists()

class IsHROrReadOnly(BasePermission):
    """
    Allows HR to edit users, but others can only view.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        # Check if the user is in the "HR" or "Admin" group for write access.
        return request.user and request.user.groups.filter(name__in=['HR', 'Admin']).exists()

