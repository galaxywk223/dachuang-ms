"""
通知路由配置
"""

from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, PlatformMaterialViewSet, PlatformNoticeViewSet

router = DefaultRouter()
router.register(r"notices", PlatformNoticeViewSet, basename="platform-notice")
router.register(r"materials", PlatformMaterialViewSet, basename="platform-material")
router.register(r"", NotificationViewSet, basename="notification")

urlpatterns = router.urls
