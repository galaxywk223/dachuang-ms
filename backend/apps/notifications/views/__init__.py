"""
通知视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer
from apps.users.models import User


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
        if not (user.is_level1_admin or user.is_level2_admin):
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

        queryset = User.objects.filter(is_active=True)
        if recipients and isinstance(recipients, list):
            queryset = queryset.filter(id__in=recipients)
        if role:
            queryset = queryset.filter(role=role)
        if college:
            queryset = queryset.filter(college=college)
        if user.is_level2_admin:
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
