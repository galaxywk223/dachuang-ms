"""
项目管理相关视图（管理员）
"""

from .views_management_project import ProjectManagementViewSet
from .views_management_achievement import AchievementManagementViewSet

__all__ = ["ProjectManagementViewSet", "AchievementManagementViewSet"]
