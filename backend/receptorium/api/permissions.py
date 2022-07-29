from rest_framework import permissions


class AllowAll(permissions.BasePermission):
    """Дает полный доступ"""
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class NotAllow(permissions.BasePermission):
    """Запрещает доступ для всех"""
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Предоставляет доступ к редактирванию только автору"""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
