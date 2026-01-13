"""
审核路由配置
"""

from rest_framework.routers import DefaultRouter
from .views import (
    ReviewViewSet,
    ExpertGroupViewSet,
    ReviewAssignmentViewSet,
    ReviewStatisticsViewSet,
)

router = DefaultRouter()
router.register(r"statistics", ReviewStatisticsViewSet, basename="review-statistics")
router.register(r"groups", ExpertGroupViewSet, basename="expert-groups")
router.register(r"assignments", ReviewAssignmentViewSet, basename="assignments")
router.register(r"", ReviewViewSet, basename="reviews")

urlpatterns = router.urls
