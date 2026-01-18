"""
系统设置路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SystemSettingViewSet,
    CertificateSettingViewSet,
    ProjectBatchViewSet,
)
from .views.batch_workflow import BatchWorkflowViewSet

router = DefaultRouter()
router.register(r"settings", SystemSettingViewSet, basename="system-settings")
router.register(
    r"certificates", CertificateSettingViewSet, basename="certificate-settings"
)
router.register(r"batches", ProjectBatchViewSet, basename="project-batches")
router.register(r"batch-workflows", BatchWorkflowViewSet, basename="batch-workflows")

urlpatterns = [
    path("", include(router.urls)),
]
