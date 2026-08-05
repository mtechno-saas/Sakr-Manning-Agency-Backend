from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Object-level permission for Vaccination records.

    Same pattern as `api.permissions.IsOwnerOrHR`:
      * SAFE_METHODS  -> always allowed
      * Admin / HR Manager role -> always allowed
      * Otherwise     -> only the record's owner

    NOTE: the `?user=N` query param is intentionally NOT honoured here.
    It is a LIST-filtering convenience for the frontend; the security
    boundary is the user's role, not the URL parameter.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        if user and getattr(user, "role", None) in ("Admin", "HR Manager"):
            return True
        return obj.user == user
