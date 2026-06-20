from pathlib import Path

from django.urls import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import AsyncTaskRecord, OperationLog


class AsyncTaskRecordSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    task_type_display = serializers.CharField(
        source="get_task_type_display", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )
    result_file_url = serializers.SerializerMethodField()
    result_file_name = serializers.SerializerMethodField()

    class Meta:
        model = AsyncTaskRecord
        fields = [
            "id",
            "task_type",
            "task_type_display",
            "title",
            "status",
            "status_display",
            "progress",
            "message",
            "payload",
            "result",
            "result_file_url",
            "result_file_name",
            "created_by",
            "created_by_name",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields

    def get_result_file_url(self, obj):
        if not obj.result_file:
            return ""
        request = self.context.get("request")
        try:
            return reverse("async-task-download", args=[obj.pk], request=request)
        except NoReverseMatch:
            return f"/api/v1/operations/tasks/{obj.pk}/download/"

    def get_result_file_name(self, obj):
        if not obj.result_file:
            return ""
        return Path(obj.result_file.name).name


class OperationLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    operator_name = serializers.CharField(source="operator.real_name", read_only=True)

    class Meta:
        model = OperationLog
        fields = [
            "id",
            "module",
            "action",
            "target_type",
            "target_id",
            "target_name",
            "status",
            "status_display",
            "detail",
            "ip_address",
            "operator",
            "operator_name",
            "created_at",
        ]
        read_only_fields = fields
