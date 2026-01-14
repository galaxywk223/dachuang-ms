"""
系统设置序列化器
"""

from rest_framework import serializers

from ..models import (
    SystemSetting,
    CertificateSetting,
    ProjectBatch,
    WorkflowConfig,
    WorkflowNode,
    PhaseScopeConfig,
    AdminAssignment,
)


class SystemSettingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )

    class Meta:
        model = SystemSetting
        fields = [
            "id",
            "code",
            "name",
            "data",
            "batch",
            "is_locked",
            "is_active",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]


class ProjectBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectBatch
        fields = [
            "id",
            "name",
            "year",
            "code",
            "status",
            "is_current",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_deleted"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        new_status = attrs.get("status")
        if not instance and new_status and new_status != ProjectBatch.STATUS_DRAFT:
            raise serializers.ValidationError({"status": "新建批次仅允许草稿状态"})
        if instance and new_status and new_status != instance.status:
            transitions = {
                ProjectBatch.STATUS_DRAFT: ProjectBatch.STATUS_ACTIVE,
                ProjectBatch.STATUS_ACTIVE: ProjectBatch.STATUS_FINISHED,
                ProjectBatch.STATUS_FINISHED: ProjectBatch.STATUS_ARCHIVED,
            }
            expected = transitions.get(instance.status)
            if expected != new_status:
                labels = dict(ProjectBatch.STATUS_CHOICES)
                from_label = labels.get(instance.status, instance.status)
                to_label = labels.get(new_status, new_status)
                raise serializers.ValidationError(
                    {"status": f"批次状态不允许从{from_label}变更为{to_label}"}
                )
        return attrs


class CertificateSettingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )
    background_image_url = serializers.SerializerMethodField()
    seal_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CertificateSetting
        fields = [
            "id",
            "name",
            "school_name",
            "issuer_name",
            "template_code",
            "background_image",
            "seal_image",
            "background_image_url",
            "seal_image_url",
            "style_config",
            "project_level",
            "project_category",
            "is_active",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]

    def _build_file_url(self, file_field):
        if not file_field:
            return ""
        try:
            request = self.context.get("request")
            url = file_field.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return ""

    def get_background_image_url(self, obj):
        return self._build_file_url(obj.background_image)

    def get_seal_image_url(self, obj):
        return self._build_file_url(obj.seal_image)


class WorkflowNodeSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(
        source="role_fk.name", read_only=True, allow_null=True
    )
    role_code = serializers.CharField(
        source="role_fk.code", read_only=True, allow_null=True
    )

    class Meta:
        model = WorkflowNode
        fields = [
            "id",
            "workflow",
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkflowConfigSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )
    nodes = WorkflowNodeSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowConfig
        fields = [
            "id",
            "name",
            "phase",
            "batch",
            "version",
            "description",
            "is_active",
            "is_locked",
            "updated_by",
            "updated_by_name",
            "nodes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]


class PhaseScopeConfigSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )

    class Meta:
        model = PhaseScopeConfig
        fields = [
            "id",
            "batch",
            "phase",
            "scope_type",
            "created_by",
            "created_by_name",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]


class AdminAssignmentSerializer(serializers.ModelSerializer):
    admin_user_name = serializers.CharField(
        source="admin_user.real_name", read_only=True
    )
    workflow_name = serializers.CharField(
        source="workflow_node.name", read_only=True
    )

    class Meta:
        model = AdminAssignment
        fields = [
            "id",
            "batch",
            "phase",
            "workflow_node",
            "workflow_name",
            "scope_value",
            "admin_user",
            "admin_user_name",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        batch = attrs.get("batch") or (instance.batch if instance else None)
        phase = attrs.get("phase") or (instance.phase if instance else None)
        workflow_node = attrs.get("workflow_node") or (
            instance.workflow_node if instance else None
        )
        admin_user = attrs.get("admin_user") or (
            instance.admin_user if instance else None
        )
        scope_value = attrs.get("scope_value") or (
            instance.scope_value if instance else None
        )

        if not batch or not phase or not workflow_node or not admin_user:
            return attrs

        if workflow_node.workflow.batch_id != batch.id:
            raise serializers.ValidationError("节点所属批次与分配批次不一致")
        if workflow_node.workflow.phase != phase:
            raise serializers.ValidationError("节点所属阶段与分配阶段不一致")
        if workflow_node.node_type == "SUBMIT":
            raise serializers.ValidationError("学生提交节点不能配置管理员分配")

        role_code = admin_user.get_role_code()
        if not role_code or not role_code.endswith("_ADMIN"):
            raise serializers.ValidationError("管理员用户必须为管理员角色")

        scope_config = PhaseScopeConfig.objects.filter(batch=batch, phase=phase).first()
        if not scope_config:
            raise serializers.ValidationError("请先配置阶段数据范围")
        if scope_config.scope_type == PhaseScopeConfig.ScopeType.KEY_FIELD:
            if str(scope_value) not in ("0", "1"):
                raise serializers.ValidationError("重点领域维度值必须为0或1")

        qs = AdminAssignment.objects.filter(
            batch=batch,
            phase=phase,
            scope_value=scope_value,
            admin_user=admin_user,
        )
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("同一维度值不能配置同一管理员多个节点")

        qs = AdminAssignment.objects.filter(
            batch=batch,
            phase=phase,
            workflow_node=workflow_node,
            scope_value=scope_value,
        )
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("该节点下的维度值已配置管理员")

        return attrs
