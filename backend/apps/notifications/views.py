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
