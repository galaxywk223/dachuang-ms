"""
审核权限
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class ExpertGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_level1_admin or request.user.is_level2_admin)
        )


