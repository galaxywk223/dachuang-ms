"""
系统设置视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsLevel1Admin
from .models import SystemSetting, CertificateSetting, ProjectBatch
from .serializers import (
    SystemSettingSerializer,
    CertificateSettingSerializer,
    ProjectBatchSerializer,
)
from .services import DEFAULT_SETTINGS, SystemSettingService


class SystemSettingViewSet(viewsets.ModelViewSet):
    """
    系统设置管理
    """

    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_permissions(self):
        if self.action in ["list", "retrieve", "effective"]:
            return [IsAuthenticated()]
        return [IsLevel1Admin()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("code")
        batch_id = request.query_params.get("batch_id")
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked:
            return Response(
                {"code": 400, "message": "该配置已锁定，无法修改"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    @action(detail=False, methods=["get"], url_path="effective")
    def effective(self, request):
        """
        获取合并默认值后的有效配置
        """
        data = {}
        batch_id = request.query_params.get("batch_id")
        batch = batch_id or None
        for code in DEFAULT_SETTINGS.keys():
            data[code] = SystemSettingService.get_setting(code, batch=batch)
        return Response({"code": 200, "message": "获取成功", "data": data})

    @action(detail=False, methods=["put"], url_path="by-code/(?P<code>[^/.]+)")
    def upsert_by_code(self, request, code=None):
        """
        按编码更新配置（不存在则创建）
        """
        batch_id = request.query_params.get("batch_id") or request.data.get("batch")
        batch = None
        if batch_id:
            batch = ProjectBatch.objects.filter(id=batch_id).first()
        else:
            batch = SystemSettingService.get_current_batch()

        setting = SystemSetting.objects.filter(code=code).first()
        if batch:
            setting = SystemSetting.objects.filter(code=code, batch=batch).first()
        if setting and setting.is_locked:
            return Response(
                {"code": 400, "message": "该配置已锁定，无法修改"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = request.data.copy()
        payload["code"] = code
        if batch:
            payload["batch"] = batch.id
        if setting:
            serializer = self.get_serializer(setting, data=payload, partial=True)
        else:
            serializer = self.get_serializer(data=payload)

        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})


class ProjectBatchViewSet(viewsets.ModelViewSet):
    """
    项目批次管理
    """

    queryset = ProjectBatch.objects.all()
    serializer_class = ProjectBatchSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "current"]:
            return [IsAuthenticated()]
        return [IsLevel1Admin()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-year", "-created_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def _sync_batch_status(self, instance):
        if instance.status == ProjectBatch.STATUS_RUNNING:
            ProjectBatch.objects.exclude(id=instance.id).update(
                status=ProjectBatch.STATUS_PUBLISHED, is_current=False
            )
            instance.is_current = True
            instance.is_active = True
            instance.save(update_fields=["is_current", "is_active"])
        elif instance.status == ProjectBatch.STATUS_ARCHIVED:
            instance.is_current = False
            instance.is_active = False
            instance.save(update_fields=["is_current", "is_active"])
        else:
            if instance.is_current:
                instance.is_current = False
                instance.save(update_fields=["is_current"])
            if not instance.is_active:
                instance.is_active = True
                instance.save(update_fields=["is_active"])

    def perform_create(self, serializer):
        instance = serializer.save()
        self._sync_batch_status(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._sync_batch_status(instance)

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        batch = SystemSettingService.get_current_batch()
        if not batch:
            return Response({"code": 200, "message": "获取成功", "data": None})
        serializer = self.get_serializer(batch)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(detail=True, methods=["post"], url_path="set-current")
    def set_current(self, request, pk=None):
        batch = self.get_object()
        ProjectBatch.objects.exclude(id=batch.id).update(
            status=ProjectBatch.STATUS_PUBLISHED, is_current=False
        )
        batch.is_current = True
        batch.is_active = True
        batch.status = ProjectBatch.STATUS_RUNNING
        batch.save(update_fields=["is_current", "is_active", "status"])
        serializer = self.get_serializer(batch)
        return Response({"code": 200, "message": "设置成功", "data": serializer.data})


class CertificateSettingViewSet(viewsets.ModelViewSet):
    """
    结题证书配置管理
    """

    queryset = CertificateSetting.objects.all()
    serializer_class = CertificateSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsLevel1Admin()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-updated_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(
            {"code": 200, "message": "创建成功", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})
