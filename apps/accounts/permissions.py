from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsPharmacie(BasePermission):
    """Only pharmacie users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'pharmacie'


class IsTechnicien(BasePermission):
    """Only technicien users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'technicien'


class IsAdminOrSelf(BasePermission):
    """Admin or the user themselves."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj == request.user


class IsAdminOrPharmacie(BasePermission):
    """Admin or pharmacie."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'pharmacie')


class IsAdminOrTechnicien(BasePermission):
    """Admin or technicien."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'technicien')


class IsValidated(BasePermission):
    """Only validated users can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_validated
