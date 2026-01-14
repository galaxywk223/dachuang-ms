"""
工作流配置序列化器
"""

from rest_framework import serializers
from apps.system_settings.models import WorkflowConfig, WorkflowNode


class WorkflowNodeSerializer(serializers.ModelSerializer):
    """工作流节点序列化器"""

    role_name = serializers.CharField(
        source="role_fk.name", read_only=True, allow_null=True
    )
    role_code = serializers.CharField(
        source="role_fk.code", read_only=True, allow_null=True
    )
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowNode
        fields = [
            "id",
            "code",
            "name",
            "node_type",
            "role",
            "role_fk",
            "role_name",
            "role_code",
            "review_level",
            "require_expert_review",
            "scope",
            "return_policy",
            "allowed_reject_to",
            "notice",
            "start_date",
            "end_date",
            "sort_order",
            "is_active",
            "can_edit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_can_edit(self, obj):
        """学生提交节点不可编辑"""
        return obj.node_type != "SUBMIT"


class WorkflowNodeCreateUpdateSerializer(serializers.ModelSerializer):
    """工作流节点创建/更新序列化器"""

    class Meta:
        model = WorkflowNode
        fields = [
            "code",
            "name",
            "node_type",
            "role_fk",
            "review_level",
            "require_expert_review",
            "scope",
            "return_policy",
            "allowed_reject_to",
            "notice",
            "start_date",
            "end_date",
            "sort_order",
            "is_active",
        ]

    def validate(self, attrs):
        """验证节点配置"""
        node_type = attrs.get("node_type")
        role_fk = attrs.get("role_fk")

        # 学生节点只能在第一个位置
        if node_type == "SUBMIT":
            if attrs.get("sort_order", 0) != 0:
                raise serializers.ValidationError(
                    "学生提交节点必须排在第一位（sort_order=0）"
                )
            if attrs.get("allowed_reject_to"):
                raise serializers.ValidationError("学生提交节点不允许退回")
            if attrs.get("require_expert_review"):
                raise serializers.ValidationError("学生提交节点不能启用专家评审")

        # 非学生节点不能使用学生角色
        if node_type != "SUBMIT" and role_fk:
            if role_fk.code == "STUDENT":
                raise serializers.ValidationError("审核节点不能使用学生角色")

        return attrs


class WorkflowConfigSerializer(serializers.ModelSerializer):
    """工作流配置序列化器"""

    nodes = serializers.SerializerMethodField()
    node_count = serializers.SerializerMethodField()
    batch_name = serializers.CharField(
        source="batch.name", read_only=True, allow_null=True
    )

    class Meta:
        model = WorkflowConfig
        fields = [
            "id",
            "name",
            "phase",
            "batch",
            "batch_name",
            "version",
            "description",
            "is_active",
            "is_locked",
            "nodes",
            "node_count",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def get_nodes(self, obj):
        """只返回活跃的节点"""
        active_nodes = obj.nodes.filter(is_active=True).order_by("sort_order")
        return WorkflowNodeSerializer(active_nodes, many=True).data

    def get_node_count(self, obj):
        """统计活跃节点数量"""
        return obj.nodes.filter(is_active=True).count()


class WorkflowConfigCreateSerializer(serializers.ModelSerializer):
    """工作流配置创建序列化器"""

    class Meta:
        model = WorkflowConfig
        fields = ["name", "phase", "batch", "version", "description", "is_active"]

    def validate(self, attrs):
        """验证工作流配置"""
        phase = attrs.get("phase")
        batch = attrs.get("batch")
        version = attrs.get("version", 1)

        # 检查是否已存在相同配置
        exists = WorkflowConfig.objects.filter(
            phase=phase, batch=batch, version=version
        ).exists()

        if exists:
            raise serializers.ValidationError(f"该批次的{phase}阶段版本{version}已存在")

        return attrs


class BatchWorkflowSummarySerializer(serializers.Serializer):
    """批次工作流汇总序列化器"""

    phase = serializers.CharField()
    phase_display = serializers.CharField()
    workflow_id = serializers.IntegerField(allow_null=True)
    workflow_name = serializers.CharField(allow_null=True)
    node_count = serializers.IntegerField()
    is_active = serializers.BooleanField()
    is_locked = serializers.BooleanField()
    has_student_node = serializers.BooleanField()
    validation_errors = serializers.ListField(
        child=serializers.CharField(), required=False
    )
