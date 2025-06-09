from rest_framework.permissions import BasePermission

class IsCustomAdminUser(BasePermission):
    """
    Faqat `is_admin=True` bo'lgan foydalanuvchilarga ruxsat beradi.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_admin', False)

from rest_framework.permissions import BasePermission

class IsCustomAdminUser(BasePermission):
    """
    Faqat `is_admin=True` bo'lgan foydalanuvchilarga ruxsat beradi.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_admin', False)