"""
系统设置路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SystemSettingViewSet,
    CertificateSettingViewSet,
    ProjectBatchViewSet,
    WorkflowConfigViewSet,
    WorkflowNodeViewSet,
    ReviewTemplateViewSet,
    ReviewTemplateItemViewSet,
)

router = DefaultRouter()
router.register(r"settings", SystemSettingViewSet, basename="system-settings")
router.register(r"certificates", CertificateSettingViewSet, basename="certificate-settings")
router.register(r"batches", ProjectBatchViewSet, basename="project-batches")
router.register(r"workflows", WorkflowConfigViewSet, basename="workflow-configs")
router.register(r"workflow-nodes", WorkflowNodeViewSet, basename="workflow-nodes")
router.register(r"review-templates", ReviewTemplateViewSet, basename="review-templates")
router.register(r"review-template-items", ReviewTemplateItemViewSet, basename="review-template-items")

urlpatterns = [
    path("", include(router.urls)),
]
