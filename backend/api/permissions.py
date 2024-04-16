from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Класс разрешений, разрешающий доступ только администратору,
    автору или только для чтения.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )


class AnonimOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    Класс разрешений,
    разрешающий анонимный или аутентифицированный доступ только для чтения.
    """

    def has_object_permission(self, request, view, object):
        return (
            (
                request.method in permissions.SAFE_METHODS
                and (
                    request.user.is_anonymous or request.user.is_authenticated)
            )
            or request.user.is_superuser
            or request.user.is_staff
        )
