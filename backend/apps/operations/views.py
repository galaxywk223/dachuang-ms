from pathlib import Path
from io import BytesIO
import logging

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AsyncTaskRecord, OperationLog
from .serializers import AsyncTaskRecordSerializer, OperationLogSerializer
from .services import DataCenterService
from apps.utils.downloads import (
    attachment_content_disposition,
    file_field_download_response,
)

logger = logging.getLogger(__name__)


def _has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


class AsyncTaskRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AsyncTaskRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["task_type", "status"]

    def _require_level1_admin(self, request, message):
        if _has_school_admin_scope(request.user):
            return None
        return Response(
            {"code": 403, "message": message},
            status=status.HTTP_403_FORBIDDEN,
        )

    def _cleanup_preview_file(self, file_path):
        if not file_path:
            return
        try:
            Path(file_path).unlink(missing_ok=True)
        except OSError:
            logger.warning("Failed to remove preview import file: %s", file_path)

    def get_queryset(self):
        user = self.request.user
        queryset = AsyncTaskRecord.objects.all()
        if _has_school_admin_scope(user):
            return queryset
        return queryset.filter(created_by=user)

    @action(methods=["get"], detail=False, url_path="data-center/kinds")
    def data_kinds(self, request):
        denied = self._require_level1_admin(request, "无权限查看导入类型")
        if denied is not None:
            return denied
        return Response(
            {"code": 200, "message": "获取成功", "data": DataCenterService.get_import_kinds()}
        )

    @action(methods=["get"], detail=False, url_path="data-center/template")
    def download_template(self, request):
        denied = self._require_level1_admin(request, "无权限下载导入模板")
        if denied is not None:
            return denied
        kind = request.query_params.get("kind", "")
        try:
            workbook = DataCenterService.build_template(kind)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        response = HttpResponse(
            stream.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = attachment_content_disposition(
            f"{kind}_template.xlsx",
            fallback="template.xlsx",
        )
        return response

    @action(methods=["post"], detail=False, url_path="data-center/preview")
    def preview_import(self, request):
        kind = request.data.get("kind", "")
        uploaded_file = request.FILES.get("file")
        file_path = None
        denied = self._require_level1_admin(request, "无权限预校验导入数据")
        if denied is not None:
            return denied
        if not uploaded_file:
            return Response(
                {"code": 400, "message": "请上传文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            file_path = DataCenterService.save_upload(uploaded_file)
            preview = DataCenterService.preview_file(kind, file_path)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finally:
            self._cleanup_preview_file(file_path)
        return Response({"code": 200, "message": "预校验完成", "data": preview})

    @action(methods=["post"], detail=False, url_path="data-center/import")
    def execute_import(self, request):
        kind = request.data.get("kind", "")
        uploaded_file = request.FILES.get("file")
        denied = self._require_level1_admin(request, "无权限导入数据")
        if denied is not None:
            return denied
        if not uploaded_file:
            return Response(
                {"code": 400, "message": "请上传文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            task = DataCenterService.create_import_task(request.user, kind, uploaded_file)
            try:
                from .tasks import run_import_task

                async_result = run_import_task.delay(task.id)
                task.payload["celery_task_id"] = async_result.id
                task.save(update_fields=["payload"])
            except Exception:
                logger.exception(
                    "Failed to enqueue import task %s; running synchronously",
                    task.id,
                )
                DataCenterService.run_import_task(task.id)
                task.refresh_from_db()
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(task)
        return Response({"code": 200, "message": "任务已创建", "data": serializer.data})

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        task = self.get_object()
        if not task.result_file:
            return Response(
                {"code": 404, "message": "任务结果文件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return file_field_download_response(
            task.result_file,
            missing_message="任务结果文件不存在",
        )


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["module", "action", "status", "target_type"]

    def get_queryset(self):
        user = self.request.user
        queryset = OperationLog.objects.select_related("operator")
        if _has_school_admin_scope(user):
            return queryset
        if user.is_admin:
            return queryset.filter(operator=user)
        return OperationLog.objects.none()
