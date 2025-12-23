"""
系统设置视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsLevel1Admin
from .models import SystemSetting, CertificateSetting
from .serializers import SystemSettingSerializer, CertificateSettingSerializer
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
        for code in DEFAULT_SETTINGS.keys():
            data[code] = SystemSettingService.get_setting(code)
        return Response({"code": 200, "message": "获取成功", "data": data})

    @action(detail=False, methods=["put"], url_path="by-code/(?P<code>[^/.]+)")
    def upsert_by_code(self, request, code=None):
        """
        按编码更新配置（不存在则创建）
        """
        setting = SystemSetting.objects.filter(code=code).first()
        if setting and setting.is_locked:
            return Response(
                {"code": 400, "message": "该配置已锁定，无法修改"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = request.data.copy()
        payload["code"] = code
        if setting:
            serializer = self.get_serializer(setting, data=payload, partial=True)
        else:
            serializer = self.get_serializer(data=payload)

        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})


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
