"""
批次工作流配置视图
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.system_settings.serializers.workflow_serializers import (
    WorkflowConfigSerializer,
    WorkflowNodeSerializer,
    WorkflowNodeCreateUpdateSerializer,
    BatchWorkflowSummarySerializer,
)
from apps.system_settings.services.workflow_service import WorkflowService


class BatchWorkflowViewSet(viewsets.ViewSet):
    """批次工作流配置视图集"""

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="workflows")
    def list_workflows(self, request, pk=None):
        """获取批次的所有工作流配置汇总"""
        batch = get_object_or_404(ProjectBatch, pk=pk)

        phases = [
            ("APPLICATION", "立项"),
            ("MID_TERM", "中期"),
            ("CLOSURE", "结题"),
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
        batch = get_object_or_404(ProjectBatch, pk=pk)

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
        batch = get_object_or_404(ProjectBatch, pk=pk)

        # 检查是否已存在
        existing = WorkflowConfig.objects.filter(
            batch=batch, phase=phase, is_active=True
        ).exists()

        if existing:
            return Response(
                {"detail": "该阶段已存在工作流配置"}, status=status.HTTP_400_BAD_REQUEST
            )

        phase_names = {
            "APPLICATION": "立项",
            "MID_TERM": "中期",
            "CLOSURE": "结题",
        }

        # 创建工作流配置
        workflow = WorkflowConfig.objects.create(
            name=f"{batch.name}-{phase_names.get(phase, phase)}工作流",
            phase=phase,
            batch=batch,
            version=1,
            description=f"{phase_names.get(phase)}阶段默认工作流",
            is_active=True,
            created_by=request.user,
            updated_by=request.user,
        )

        # 创建默认节点
        from apps.system_settings.services.workflow_service import DEFAULT_WORKFLOWS

        default_nodes = DEFAULT_WORKFLOWS.get(phase, [])

        for idx, node_def in enumerate(default_nodes):
            WorkflowNode.objects.create(
                workflow=workflow,
                code=node_def.code,
                name=node_def.name,
                node_type=node_def.node_type,
                role=node_def.role,
                review_level=node_def.review_level,
                scope=node_def.scope,
                return_policy=node_def.return_policy,
                allowed_reject_to=node_def.allowed_reject_to,
                sort_order=idx,
                is_active=True,
            )

        serializer = WorkflowConfigSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="workflows/(?P<phase>[^/.]+)/nodes")
    def list_nodes(self, request, pk=None, phase=None):
        """获取批次指定阶段工作流的所有节点"""
        batch = get_object_or_404(ProjectBatch, pk=pk)

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
            .select_related("role_fk", "review_template")
            .order_by("sort_order", "id")
        )

        serializer = WorkflowNodeSerializer(nodes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="workflows/(?P<phase>[^/.]+)/nodes")
    @transaction.atomic
    def create_node(self, request, pk=None, phase=None):
        """创建工作流节点"""
        batch = get_object_or_404(ProjectBatch, pk=pk)

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

        serializer = WorkflowNodeCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        node = serializer.save(workflow=workflow)

        result_serializer = WorkflowNodeSerializer(node)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch"],
        url_path="workflows/(?P<phase>[^/.]+)/nodes/(?P<node_id>[^/.]+)",
    )
    @transaction.atomic
    def update_node(self, request, pk=None, phase=None, node_id=None):
        """更新工作流节点"""
        batch = get_object_or_404(ProjectBatch, pk=pk)
        node = get_object_or_404(WorkflowNode, pk=node_id)

        if node.workflow.batch != batch or node.workflow.phase != phase:
            return Response(
                {"detail": "节点不属于该批次或阶段"}, status=status.HTTP_400_BAD_REQUEST
            )

        if node.workflow.is_locked:
            return Response(
                {"detail": "工作流已锁定，无法修改"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 学生提交节点不可编辑
        if node.node_type == "SUBMIT":
            return Response(
                {"detail": "学生提交节点不可修改"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = WorkflowNodeCreateUpdateSerializer(
            node, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        node = serializer.save()

        result_serializer = WorkflowNodeSerializer(node)
        return Response(result_serializer.data)

    @action(
        detail=True,
        methods=["delete"],
        url_path="workflows/(?P<phase>[^/.]+)/nodes/(?P<node_id>[^/.]+)",
    )
    @transaction.atomic
    def delete_node(self, request, pk=None, phase=None, node_id=None):
        """删除工作流节点（软删除）"""
        batch = get_object_or_404(ProjectBatch, pk=pk)
        node = get_object_or_404(WorkflowNode, pk=node_id)

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

        node.is_active = False
        node.save(update_fields=["is_active"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        url_path="workflows/(?P<phase>[^/.]+)/nodes/reorder",
    )
    @transaction.atomic
    def reorder_nodes(self, request, pk=None, phase=None):
        """重新排序工作流节点"""
        batch = get_object_or_404(ProjectBatch, pk=pk)

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
        if not node_ids:
            return Response(
                {"detail": "请提供节点ID列表"}, status=status.HTTP_400_BAD_REQUEST
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

        # 更新排序
        node_map = {node.id: node for node in nodes}
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
        batch = get_object_or_404(ProjectBatch, pk=pk)

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
