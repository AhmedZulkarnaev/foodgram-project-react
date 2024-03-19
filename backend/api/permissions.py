from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to modify objects.
    """
    def has_permission(self, request, view):
        # Разрешить чтение для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить запись только администраторам
        return request.user and request.user.is_staff
