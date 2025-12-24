"""
系统设置路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SystemSettingViewSet, CertificateSettingViewSet, ProjectBatchViewSet

router = DefaultRouter()
router.register(r"settings", SystemSettingViewSet, basename="system-settings")
router.register(r"certificates", CertificateSettingViewSet, basename="certificate-settings")
router.register(r"batches", ProjectBatchViewSet, basename="project-batches")

urlpatterns = [
    path("", include(router.urls)),
]
