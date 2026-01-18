"""
项目经费序列化器
"""

from rest_framework import serializers

from ..models import ProjectExpenditure
from ..services.expenditure_workflow_service import ExpenditureWorkflowService
from apps.system_settings.models import WorkflowNode


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
    proof_file_url = serializers.SerializerMethodField()
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
        if obj.proof_file:
            return obj.proof_file.url
        return None

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


class ProjectExpenditureReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    comments = serializers.CharField(required=False, allow_blank=True)
