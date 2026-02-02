# ships/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsShipManagerOrAdmin(BasePermission):
    """
    Custom permission to only allow ship managers or admins to edit ships.
    """
    def has_permission(self, request, view):
        # Allow read-only access for any authenticated user.
        if request.method in SAFE_METHODS:
            return True

        # Allow superusers full access
        if request.user and request.user.is_superuser:
            return True

        # Check for role 'Admin' (from User model's role field)
        if getattr(request.user, 'role', None) == 'Admin':
            return True

        # Allow write access only if the user is in the "Ship Manager" or "Admin" group.
        return request.user and request.user.groups.filter(name__in=['Ship Manager', 'Admin']).exists()
