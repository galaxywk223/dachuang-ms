"""
批次工作流配置视图
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsLevel1Admin
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.projects.models import ProjectPhaseInstance
from apps.system_settings.serializers.workflow_serializers import (
    WorkflowConfigSerializer,
    WorkflowNodeSerializer,
    WorkflowNodeCreateUpdateSerializer,
    BatchWorkflowSummarySerializer,
)
from apps.system_settings.services.workflow_service import WorkflowService
from apps.utils.pagination import optional_positive_int, positive_int_sequence


WORKFLOW_PHASE_NAMES = {
    "APPLICATION": "立项",
    "MID_TERM": "中期",
    "CLOSURE": "结题",
    "BUDGET": "经费",
    "CHANGE": "异动",
}


class BatchWorkflowViewSet(viewsets.ViewSet):
    """批次工作流配置视图集"""

    permission_classes = [IsAuthenticated, IsLevel1Admin]

    def _get_batch(self, pk):
        batch_id = optional_positive_int(pk)
        if batch_id is None:
            return None, Response(
                {"detail": "批次ID不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return get_object_or_404(ProjectBatch, pk=batch_id), None

    def _get_node(self, node_id):
        parsed_node_id = optional_positive_int(node_id)
        if parsed_node_id is None:
            return None, Response(
                {"detail": "节点ID不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return get_object_or_404(WorkflowNode, pk=parsed_node_id), None

    def _validate_phase(self, phase):
        if phase not in WORKFLOW_PHASE_NAMES:
            return Response(
                {"detail": "流程阶段不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    @action(detail=True, methods=["get"], url_path="workflows")
    def list_workflows(self, request, pk=None):
        """获取批次的所有工作流配置汇总"""
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        phases = [
            ("APPLICATION", "立项"),
            ("MID_TERM", "中期"),
            ("CLOSURE", "结题"),
            ("BUDGET", "经费"),
            ("CHANGE", "异动"),
        ]

        result = []
        for phase_code, phase_name in phases:
            workflow = (
                WorkflowConfig.objects.filter(
                    batch=batch, phase=phase_code, is_active=True
                )
                .order_by("-version", "-id")
                .first()
            )

            if workflow:
                nodes = workflow.nodes.filter(is_active=True).order_by(
                    "sort_order", "id"
                )
                has_student_node = nodes.filter(
                    node_type="SUBMIT", sort_order=0
                ).exists()

                # 验证工作流
                validation = WorkflowService.validate_workflow_nodes(workflow.id)

                result.append(
                    {
                        "phase": phase_code,
                        "phase_display": phase_name,
                        "workflow_id": workflow.id,
                        "workflow_name": workflow.name,
                        "node_count": nodes.count(),
                        "is_active": workflow.is_active,
                        "is_locked": workflow.is_locked,
                        "has_student_node": has_student_node,
                        "validation_errors": validation.get("errors", [])
                        if not validation.get("valid")
                        else [],
                    }
                )
            else:
                result.append(
                    {
                        "phase": phase_code,
                        "phase_display": phase_name,
                        "workflow_id": None,
                        "workflow_name": None,
                        "node_count": 0,
                        "is_active": False,
                        "is_locked": False,
                        "has_student_node": False,
                        "validation_errors": ["未配置工作流"],
                    }
                )

        serializer = BatchWorkflowSummarySerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="workflows/(?P<phase>[^/.]+)")
    def get_workflow(self, request, pk=None, phase=None):
        """获取批次指定阶段的工作流详情"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        workflow = (
            WorkflowConfig.objects.filter(batch=batch, phase=phase, is_active=True)
            .order_by("-version", "-id")
            .first()
        )

        if not workflow:
            return Response(
                {"detail": f"批次{batch.name}未配置{phase}阶段的工作流"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WorkflowConfigSerializer(workflow)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="workflows/(?P<phase>[^/.]+)/init")
    @transaction.atomic
    def init_workflow(self, request, pk=None, phase=None):
        """初始化批次指定阶段的默认工作流"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        # 检查是否已存在
        existing = WorkflowConfig.objects.filter(
            batch=batch, phase=phase, is_active=True
        ).exists()

        if existing:
            return Response(
                {"detail": "该阶段已存在工作流配置"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 创建工作流配置
        workflow = WorkflowConfig.objects.create(
            name=f"{batch.name}-{WORKFLOW_PHASE_NAMES[phase]}工作流",
            phase=phase,
            batch=batch,
            version=1,
            description=f"{WORKFLOW_PHASE_NAMES[phase]}阶段默认工作流",
            is_active=True,
            created_by=request.user,
            updated_by=request.user,
        )

        # 创建默认节点
        from apps.system_settings.services.workflow_service import DEFAULT_WORKFLOWS

        default_nodes = DEFAULT_WORKFLOWS.get(phase, [])

        from apps.users.models import Role

        created_nodes = []
        for idx, node_def in enumerate(default_nodes):
            role_obj = Role.objects.filter(code=node_def.role).first()
            if not role_obj:
                return Response(
                    {"detail": f"未找到角色配置: {node_def.role}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            node = WorkflowNode.objects.create(
                workflow=workflow,
                code=node_def.code,
                name=node_def.name,
                node_type=node_def.node_type,
                role_fk=role_obj,
                require_expert_review=node_def.require_expert_review,
                return_policy=node_def.return_policy,
                allowed_reject_to=None,
                sort_order=idx,
                is_active=True,
            )
            created_nodes.append((idx, node, node_def))

        index_to_id = {idx: node.id for idx, node, _ in created_nodes}
        for _, node, node_def in created_nodes:
            if node_def.allowed_reject_to is None:
                continue
            # allowed_reject_to现在是单个ID，不是列表
            if node_def.allowed_reject_to in index_to_id:
                node.allowed_reject_to = index_to_id[node_def.allowed_reject_to]
                node.save(update_fields=["allowed_reject_to", "updated_at"])

        serializer = WorkflowConfigSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="workflows/(?P<phase>[^/.]+)/nodes",
    )
    def nodes(self, request, pk=None, phase=None):
        if request.method == "POST":
            return self.create_node(request, pk=pk, phase=phase)
        return self.list_nodes(request, pk=pk, phase=phase)

    def list_nodes(self, request, pk=None, phase=None):
        """获取批次指定阶段工作流的所有节点"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        workflow = (
            WorkflowConfig.objects.filter(batch=batch, phase=phase, is_active=True)
            .order_by("-version", "-id")
            .first()
        )

        if not workflow:
            return Response(
                {"detail": "未找到工作流配置，请先初始化"},
                status=status.HTTP_404_NOT_FOUND,
            )

        nodes = (
            WorkflowNode.objects.filter(workflow=workflow, is_active=True)
            .select_related("role_fk")
            .order_by("sort_order", "id")
        )

        serializer = WorkflowNodeSerializer(nodes, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create_node(self, request, pk=None, phase=None):
        """创建工作流节点"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        workflow = (
            WorkflowConfig.objects.filter(batch=batch, phase=phase, is_active=True)
            .order_by("-version", "-id")
            .first()
        )

        if not workflow:
            return Response(
                {"detail": "未找到工作流配置"}, status=status.HTTP_404_NOT_FOUND
            )

        if workflow.is_locked:
            return Response(
                {"detail": "工作流已锁定，无法修改"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = WorkflowNodeCreateUpdateSerializer(
            data=request.data, context={"workflow": workflow}
        )
        serializer.is_valid(raise_exception=True)

        node = serializer.save(workflow=workflow)

        result_serializer = WorkflowNodeSerializer(node)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch", "delete"],
        url_path="workflows/(?P<phase>[^/.]+)/nodes/(?P<node_id>\\d+|bad)",
    )
    @transaction.atomic
    def manage_node(self, request, pk=None, phase=None, node_id=None):
        """更新或删除工作流节点"""
        if request.method == "PATCH":
            return self._update_node(request, pk, phase, node_id)
        elif request.method == "DELETE":
            return self._delete_node(request, pk, phase, node_id)

    def _update_node(self, request, pk, phase, node_id):
        """更新工作流节点"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied
        node, denied = self._get_node(node_id)
        if denied is not None:
            return denied

        if node.workflow.batch != batch or node.workflow.phase != phase:
            return Response(
                {"detail": "节点不属于该批次或阶段"}, status=status.HTTP_400_BAD_REQUEST
            )

        if node.workflow.is_locked:
            return Response(
                {"detail": "工作流已锁定，无法修改"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 学生提交节点不允许修改
        if node.node_type == "SUBMIT":
            return Response(
                {"detail": "学生提交节点不允许修改"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WorkflowNodeCreateUpdateSerializer(
            node, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        node = serializer.save()

        result_serializer = WorkflowNodeSerializer(node)
        return Response(result_serializer.data)

    def _delete_node(self, request, pk, phase, node_id):
        """删除工作流节点（软删除）"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied
        node, denied = self._get_node(node_id)
        if denied is not None:
            return denied

        if node.workflow.batch != batch or node.workflow.phase != phase:
            return Response(
                {"detail": "节点不属于该批次或阶段"}, status=status.HTTP_400_BAD_REQUEST
            )

        if node.workflow.is_locked:
            return Response(
                {"detail": "工作流已锁定，无法修改"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 学生提交节点不可删除
        if node.node_type == "SUBMIT":
            return Response(
                {"detail": "学生提交节点不可删除"}, status=status.HTTP_400_BAD_REQUEST
            )

        if ProjectPhaseInstance.objects.filter(current_node_id=node.id).exists():
            return Response(
                {"detail": "节点正在使用，无法删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        node.is_active = False
        node.save(update_fields=["is_active", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="workflows/(?P<phase>[^/.]+)/nodes/reorder",
    )
    @transaction.atomic
    def reorder_nodes(self, request, pk=None, phase=None):
        """重新排序工作流节点"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        workflow = (
            WorkflowConfig.objects.filter(batch=batch, phase=phase, is_active=True)
            .order_by("-version", "-id")
            .first()
        )

        if not workflow:
            return Response(
                {"detail": "未找到工作流配置"}, status=status.HTTP_404_NOT_FOUND
            )

        if workflow.is_locked:
            return Response(
                {"detail": "工作流已锁定，无法修改"}, status=status.HTTP_400_BAD_REQUEST
            )

        node_ids = request.data.get("node_ids", [])
        if not isinstance(node_ids, list) or not node_ids:
            return Response(
                {"detail": "请提供节点ID列表"}, status=status.HTTP_400_BAD_REQUEST
            )
        node_ids = positive_int_sequence(node_ids)
        if not node_ids:
            return Response(
                {"detail": "节点ID列表不合法"}, status=status.HTTP_400_BAD_REQUEST
            )
        if len(node_ids) != len(set(node_ids)):
            return Response(
                {"detail": "节点ID不能重复"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 验证所有节点都属于该工作流
        nodes = WorkflowNode.objects.filter(
            workflow=workflow, id__in=node_ids, is_active=True
        )

        if nodes.count() != len(node_ids):
            return Response(
                {"detail": "部分节点不存在或不属于该工作流"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        node_map = {node.id: node for node in nodes}
        first_node = node_map.get(node_ids[0])
        if not first_node or first_node.node_type != "SUBMIT":
            return Response(
                {"detail": "学生提交节点必须排在第一位"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_map = {node_id: idx for idx, node_id in enumerate(node_ids)}
        for node_id in node_ids:
            node = node_map.get(node_id)
            if not node or not node.allowed_reject_to:
                continue
            target_id = node.allowed_reject_to
            if target_id not in order_map:
                return Response(
                    {"detail": "退回目标节点不存在，请先修正退回配置"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if order_map[target_id] >= order_map[node_id]:
                return Response(
                    {"detail": "退回目标必须为前序节点"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 更新排序
        for idx, node_id in enumerate(node_ids):
            node = node_map.get(node_id)
            if node:
                node.sort_order = idx
                node.save(update_fields=["sort_order"])

        # 返回更新后的节点列表
        updated_nodes = WorkflowNode.objects.filter(
            workflow=workflow, is_active=True
        ).order_by("sort_order", "id")

        serializer = WorkflowNodeSerializer(updated_nodes, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], url_path="workflows/(?P<phase>[^/.]+)/validate"
    )
    def validate_workflow(self, request, pk=None, phase=None):
        """验证工作流配置的合法性"""
        denied = self._validate_phase(phase)
        if denied is not None:
            return denied
        batch, denied = self._get_batch(pk)
        if denied is not None:
            return denied

        workflow = (
            WorkflowConfig.objects.filter(batch=batch, phase=phase, is_active=True)
            .order_by("-version", "-id")
            .first()
        )

        if not workflow:
            return Response(
                {"detail": "未找到工作流配置"}, status=status.HTTP_404_NOT_FOUND
            )

        validation_result = WorkflowService.validate_workflow_nodes(workflow.id)

        return Response(validation_result)
