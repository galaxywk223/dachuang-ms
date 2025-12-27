"""
Backward-compatible re-export for admin views.

This package name was previously used for "admin/management" views, but it is
easy to confuse with Django management commands.
"""

from ..admin import AchievementManagementViewSet, ProjectManagementViewSet

__all__ = ["ProjectManagementViewSet", "AchievementManagementViewSet"]

