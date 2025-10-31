"""
项目路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectProgressViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="project")
router.register(r"progress", ProjectProgressViewSet, basename="progress")

urlpatterns = router.urls
