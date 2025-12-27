"""
通知序列化器
"""

from rest_framework import serializers
from ..models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    """

    type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )
    project_title = serializers.CharField(
        source="related_project.title", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "content",
            "notification_type",
            "type_display",
            "recipient",
            "related_project",
            "project_title",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "recipient", "created_at", "read_at"]
