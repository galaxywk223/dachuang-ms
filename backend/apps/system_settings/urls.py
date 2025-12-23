"""
系统设置路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SystemSettingViewSet, CertificateSettingViewSet

router = DefaultRouter()
router.register(r"settings", SystemSettingViewSet, basename="system-settings")
router.register(r"certificates", CertificateSettingViewSet, basename="certificate-settings")

urlpatterns = [
    path("", include(router.urls)),
]
