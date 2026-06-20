"""
项目路由配置
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    ProjectAchievementViewSet,
    ProjectExpenditureViewSet,
    ProjectManagementViewSet,
    AchievementManagementViewSet,
    ProjectChangeRequestViewSet,
    ProjectApplicationViewSet,
    ProjectClosureViewSet,
)

router = DefaultRouter()
router.register(r"admin/manage", ProjectManagementViewSet, basename="admin-manage")
# router.register(r"admin/achievements", AchievementManagementViewSet, basename="admin-achievements")
router.register(r"achievements", ProjectAchievementViewSet, basename="achievement")
router.register(r"expenditures", ProjectExpenditureViewSet, basename="expenditure")
router.register(
    r"change-requests", ProjectChangeRequestViewSet, basename="change-request"
)
router.register(
    r"application", ProjectApplicationViewSet, basename="project-application"
)
router.register(r"closure", ProjectClosureViewSet, basename="project-closure")
router.register(r"", ProjectViewSet, basename="project")

urlpatterns = [
    path(
        "admin/achievements/",
        AchievementManagementViewSet.as_view({"get": "list"}),
        name="admin-achievements-list",
    ),
    path(
        "admin/achievements/export/",
        AchievementManagementViewSet.as_view({"get": "export_data"}),
        name="admin-achievements-export",
    ),
] + router.urls
