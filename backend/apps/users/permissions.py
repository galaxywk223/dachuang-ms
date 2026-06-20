from rest_framework import permissions


class IsLevel1Admin(permissions.BasePermission):
    """
    允许校级管理员访问（含自定义全校范围角色）
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_school_admin or request.user.is_level1_admin)
        )


class IsAdmin(permissions.BasePermission):
    """
    允许任何管理员访问（支持多级管理员）
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_admin
        )
