from rest_framework import permissions


class IsLevel1Admin(permissions.BasePermission):
    """
    允许一级管理员（校级管理员）访问
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_level1_admin
        )


class IsAdmin(permissions.BasePermission):
    """
    允许任何管理员访问（支持多级管理员）
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_admin
        )
