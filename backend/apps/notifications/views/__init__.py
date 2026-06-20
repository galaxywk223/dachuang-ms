"""
通知视图
"""

from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.dictionaries.models import DictionaryItem
from ..models import Notification, PlatformMaterial, PlatformNotice
from ..serializers import (
    NotificationSerializer,
    PlatformMaterialSerializer,
    PlatformNoticeSerializer,
)
from apps.users.models import User
from apps.utils.downloads import file_field_download_response
from apps.utils.pagination import positive_int_list

PROJECT_TEMPLATE_MATERIAL_PREFIX = "project_template_"
PROJECT_TYPE_DICT_CODE = "project_type"


def _role_code(user):
    return user.role_fk.code if user.role_fk else ""


def _audience_role_codes(user):
    codes = {_role_code(user)}
    if user.is_school_admin or user.is_level1_admin:
        codes.add(User.UserRole.LEVEL1_ADMIN)
    if user.is_college_admin:
        codes.add(User.UserRole.LEVEL2_ADMIN)
    codes.discard("")
    return codes


def _visible_to_user(queryset, user):
    role_codes = _audience_role_codes(user)
    visible = queryset.filter(target_roles=[])
    for role_code in role_codes:
        visible = visible | queryset.filter(target_roles__contains=[role_code])
    return visible


def _can_manage_all_platform_content(user):
    role_code = user.get_role_code()
    return bool(
        user.is_superuser
        or role_code == User.UserRole.LEVEL1_ADMIN
        or (
            user.is_admin
            and user.role_fk
            and user.role_fk.scope_dimension in (None, "")
            and role_code != User.UserRole.LEVEL2_ADMIN
        )
    )


def _ensure_notice_published_at(data, instance=None):
    status_value = data.get("status")
    if not status_value:
        status_value = (
            instance.status
            if instance is not None
            else PlatformNotice.NoticeStatus.PUBLISHED
        )
    if status_value != PlatformNotice.NoticeStatus.PUBLISHED:
        return data
    if data.get("published_at"):
        return data
    if instance is not None and instance.published_at:
        return data
    data["published_at"] = timezone.now()
    return data


def _project_template_material_id(item):
    return f"{PROJECT_TEMPLATE_MATERIAL_PREFIX}{item.pk}"


def _project_template_file_url(request, item):
    return f"/api/v1/notifications/materials/{_project_template_material_id(item)}/download/"


def _project_template_material_payload(request, item):
    title = f"{item.label}申请书模板"
    return {
        "id": _project_template_material_id(item),
        "title": title,
        "description": item.description or f"项目类型“{item.label}”对应的申请书模板。",
        "category": "申请书模板",
        "target_roles": [],
        "file": item.template_file.url if item.template_file else "",
        "file_url": _project_template_file_url(request, item),
        "file_name": item.template_file.name.rsplit("/", 1)[-1] if item.template_file else title,
        "external_url": "",
        "is_active": True,
        "download_count": None,
        "created_by": None,
        "created_by_name": "",
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "source": "project_template",
    }


def _project_template_materials(request):
    items = (
        DictionaryItem.objects.select_related("dict_type")
        .filter(
            dict_type__code=PROJECT_TYPE_DICT_CODE,
            dict_type__is_active=True,
            is_active=True,
        )
        .exclude(template_file="")
        .exclude(template_file__isnull=True)
        .order_by("sort_order", "id")
    )
    return [_project_template_material_payload(request, item) for item in items]


def _project_template_id_from_pk(pk):
    value = str(pk or "")
    if not value.startswith(PROJECT_TEMPLATE_MATERIAL_PREFIX):
        return None
    try:
        parsed = int(value.removeprefix(PROJECT_TEMPLATE_MATERIAL_PREFIX))
    except ValueError:
        return None
    return parsed if parsed > 0 else None


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    通知视图集（只读）
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["notification_type", "is_read"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """
        只返回当前用户的通知
        """
        return Notification.objects.filter(recipient=self.request.user)

    @action(methods=["post"], detail=True)
    def mark_read(self, request, pk=None):
        """
        标记为已读
        """
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response({"code": 200, "message": "已标记为已读"})

    @action(methods=["post"], detail=False, url_path="mark-all-read")
    def mark_all_read(self, request):
        """
        标记所有为已读
        """
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

        return Response({"code": 200, "message": "已标记所有通知为已读"})

    @action(methods=["get"], detail=False)
    def unread_count(self, request):
        """
        获取未读通知数量
        """
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        return Response({"code": 200, "data": {"count": count}})

    @action(methods=["post"], detail=False, url_path="batch-send")
    def batch_send(self, request):
        """
        批量发送通知（管理员）
        """
        user = request.user
        if not user.is_admin:
            return Response(
                {"code": 403, "message": "无权限发送通知"},
                status=status.HTTP_403_FORBIDDEN,
            )

        title = request.data.get("title")
        content = request.data.get("content")
        recipients = request.data.get("recipients", [])
        role = request.data.get("role")
        college = request.data.get("college")

        if not title or not content:
            return Response(
                {"code": 400, "message": "标题和内容不能为空"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if recipients:
            recipients = positive_int_list(recipients)
            if not recipients:
                return Response(
                    {"code": 400, "message": "接收人列表不合法"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if user.is_college_admin and not user.college:
            return Response(
                {"code": 400, "message": "当前账号未设置学院信息"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = User.objects.filter(is_active=True)
        if recipients:
            queryset = queryset.filter(id__in=recipients)
        if role:
            queryset = queryset.filter(role_fk__code=role)
        if college:
            queryset = queryset.filter(college=college)
        if user.is_college_admin:
            queryset = queryset.filter(college=user.college)

        created = 0
        for recipient in queryset:
            Notification.objects.create(
                recipient=recipient,
                title=title,
                content=content,
                notification_type=Notification.NotificationType.SYSTEM,
            )
            created += 1

        return Response(
            {"code": 200, "message": "发送成功", "data": {"created": created}}
        )


class PlatformNoticeViewSet(viewsets.ModelViewSet):
    serializer_class = PlatformNoticeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "is_pinned"]

    def get_queryset(self):
        queryset = PlatformNotice.objects.all()
        if _can_manage_all_platform_content(self.request.user):
            return queryset
        return _visible_to_user(
            queryset.filter(status=PlatformNotice.NoticeStatus.PUBLISHED),
            self.request.user,
        )

    def create(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限发布公告"},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = _ensure_notice_published_at(request.data.copy())
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response({"code": 200, "message": "创建成功", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限修改公告"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        data = _ensure_notice_published_at(request.data.copy(), instance)
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限修改公告"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        data = _ensure_notice_published_at(request.data.copy(), instance)
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限删除公告"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class PlatformMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = PlatformMaterialSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["category", "is_active"]

    def get_queryset(self):
        queryset = PlatformMaterial.objects.all()
        if _can_manage_all_platform_content(self.request.user):
            return queryset
        return _visible_to_user(queryset.filter(is_active=True), self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        platform_materials = self.get_serializer(queryset, many=True).data
        materials = _project_template_materials(request) + list(platform_materials)

        page = self.paginate_queryset(materials)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(materials)

    def create(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限上传资料"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response({"code": 200, "message": "创建成功", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限修改资料"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限修改资料"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"code": 403, "message": "无权限删除资料"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        template_item_id = _project_template_id_from_pk(pk)
        if template_item_id is not None:
            item = (
                DictionaryItem.objects.filter(
                    id=template_item_id,
                    dict_type__code=PROJECT_TYPE_DICT_CODE,
                    dict_type__is_active=True,
                    is_active=True,
                )
                .exclude(template_file="")
                .first()
            )
            if item is None:
                return Response(
                    {"code": 404, "message": "资料文件不存在"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return file_field_download_response(
                item.template_file,
                missing_message="资料文件不存在",
            )

        material = self.get_object()
        if not material.file:
            return Response(
                {"code": 404, "message": "资料文件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        response = file_field_download_response(
            material.file,
            missing_message="资料文件不存在",
        )
        if isinstance(response, FileResponse):
            material.download_count += 1
            material.save(update_fields=["download_count"])
        return response

    @action(methods=["post"], detail=True)
    def record_download(self, request, pk=None):
        if _project_template_id_from_pk(pk) is not None:
            return Response(
                {
                    "code": 200,
                    "message": "记录成功",
                    "data": {"download_count": None},
                }
            )

        material = self.get_object()
        material.download_count += 1
        material.save(update_fields=["download_count"])
        return Response(
            {
                "code": 200,
                "message": "记录成功",
                "data": {"download_count": material.download_count},
            }
        )
