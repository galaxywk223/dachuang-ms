"""
项目经费序列化器
"""

from pathlib import Path

from django.urls import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from ..models import ProjectExpenditure
from ..services.expenditure_workflow_service import ExpenditureWorkflowService
from apps.system_settings.models import WorkflowNode
from ..upload_validation import validate_project_support_file


class ProjectExpenditureSerializer(serializers.ModelSerializer):
    """
    项目经费支出序列化器
    """

    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)
    project_leader_name = serializers.CharField(
        source="project.leader.real_name", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    leader_review_status_display = serializers.CharField(
        source="get_leader_review_status_display", read_only=True
    )
    proof_file = serializers.FileField(required=False, allow_null=True, write_only=True)
    proof_file_url = serializers.SerializerMethodField()
    proof_file_name = serializers.SerializerMethodField()
    current_node_name = serializers.SerializerMethodField()
    current_node_role_code = serializers.SerializerMethodField()
    current_node_role_name = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = ProjectExpenditure
        fields = [
            "id",
            "project",
            "project_no",
            "project_title",
            "project_leader_name",
            "title",
            "amount",
            "expenditure_date",
            "proof_file",
            "proof_file_url",
            "proof_file_name",
            "status",
            "status_display",
            "leader_review_status",
            "leader_review_status_display",
            "current_node_id",
            "current_node_name",
            "current_node_role_code",
            "current_node_role_name",
            "can_review",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "leader_review_status",
            "current_node_id",
            "created_by",
            "created_at",
        ]

    def get_proof_file_url(self, obj):
        if not obj.proof_file:
            return ""
        request = self.context.get("request")
        try:
            return reverse("expenditure-download", args=[obj.pk], request=request)
        except NoReverseMatch:
            return f"/api/v1/projects/expenditures/{obj.pk}/download/"

    def get_proof_file_name(self, obj):
        if not obj.proof_file:
            return ""
        return Path(obj.proof_file.name).name

    def _get_current_node(self, obj):
        if not obj.current_node_id:
            return None
        return WorkflowNode.objects.filter(id=obj.current_node_id).select_related(
            "role_fk"
        ).first()

    def get_current_node_name(self, obj):
        node = self._get_current_node(obj)
        return node.name if node else ""

    def get_current_node_role_code(self, obj):
        node = self._get_current_node(obj)
        return node.get_role_code() if node else ""

    def get_current_node_role_name(self, obj):
        node = self._get_current_node(obj)
        return node.role_fk.name if node and node.role_fk else ""

    def get_can_review(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        result = ExpenditureWorkflowService.get_pending_review_for_user(
            obj, request.user
        )
        return bool(result and result.get("type") == "NODE")

    def validate_proof_file(self, value):
        """
        验证经费凭证附件
        """
        return validate_project_support_file(
            value,
            label="经费凭证",
            max_size_mb=10,
            empty_as_none=True,
        )


class ProjectExpenditureReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    comments = serializers.CharField(required=False, allow_blank=True)
