from rest_framework.routers import DefaultRouter

from .views import AsyncTaskRecordViewSet, OperationLogViewSet

router = DefaultRouter()
router.register(r"tasks", AsyncTaskRecordViewSet, basename="async-task")
router.register(r"logs", OperationLogViewSet, basename="operation-log")

urlpatterns = router.urls
