from rest_framework import permissions


class IsAutehenticatedOrAuthorOrReadOnly(permissions.BasePermission):
    """Права доступа для авторизованных и администраторах,
    и автору рецепта (редактировать),
    для неавторизованных пользователей (прочитать)
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_active)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )
