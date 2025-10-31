"""
项目路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectProgressViewSet, ProjectAchievementViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="project")
router.register(r"progress", ProjectProgressViewSet, basename="progress")
router.register(r"achievements", ProjectAchievementViewSet, basename="achievement")

urlpatterns = router.urls
