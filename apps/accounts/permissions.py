from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allows access only to users with the 'Admin' role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'Admin')

class IsHR(BasePermission):
    """Allows access only to users with the 'HR' role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'HR')

class IsAdminOrHR(BasePermission):
    """Allows access to users with either 'Admin' or 'HR' roles."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['Admin', 'HR'])