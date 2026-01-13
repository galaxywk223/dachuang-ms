"""
Workflow configuration helper.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, cast

from apps.system_settings.models import WorkflowConfig, WorkflowNode, ProjectBatch


@dataclass(frozen=True)
class WorkflowNodeDef:
    id: int  # 添加节点ID用于退回逻辑
    code: str
    name: str
    node_type: str
    role: str
    review_level: str
    scope: str
    return_policy: str
    allowed_reject_to: List[int]  # 允许退回的目标节点ID列表
    review_template_id: Optional[int] = None
    role_fk_id: Optional[int] = None  # 角色外键ID


DEFAULT_WORKFLOWS = {
    "APPLICATION": [
        WorkflowNodeDef(
            id=0,
            code="STUDENT_SUBMIT",
            name="学生提交立项",
            node_type="SUBMIT",
            role="STUDENT",
            review_level="",
            scope="",
            return_policy="NONE",
            allowed_reject_to=[],
        ),
        WorkflowNodeDef(
            id=1,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type="REVIEW",
            role="TEACHER",
            review_level="TEACHER",
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
        WorkflowNodeDef(
            id=2,
            code="COLLEGE_EXPERT",
            name="院级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL2",
            scope="COLLEGE",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1],
        ),
        WorkflowNodeDef(
            id=3,
            code="SCHOOL_EXPERT",
            name="校级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL1",
            scope="SCHOOL",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1, 2],
        ),
        WorkflowNodeDef(
            id=4,
            code="SCHOOL_PUBLISH",
            name="校级发布立项",
            node_type="APPROVAL",
            role="LEVEL1_ADMIN",
            review_level="LEVEL1",
            scope="",
            return_policy="NONE",
            allowed_reject_to=[],
        ),
    ],
    "MID_TERM": [
        WorkflowNodeDef(
            id=0,
            code="STUDENT_SUBMIT",
            name="学生提交中期",
            node_type="SUBMIT",
            role="STUDENT",
            review_level="",
            scope="",
            return_policy="NONE",
            allowed_reject_to=[],
        ),
        WorkflowNodeDef(
            id=1,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type="REVIEW",
            role="TEACHER",
            review_level="TEACHER",
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
        WorkflowNodeDef(
            id=2,
            code="COLLEGE_EXPERT",
            name="院级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL2",
            scope="COLLEGE",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1],
        ),
        WorkflowNodeDef(
            id=3,
            code="COLLEGE_FINALIZE",
            name="学院确认",
            node_type="APPROVAL",
            role="LEVEL2_ADMIN",
            review_level="LEVEL2",
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
    ],
    "CLOSURE": [
        WorkflowNodeDef(
            id=0,
            code="STUDENT_SUBMIT",
            name="学生提交结题",
            node_type="SUBMIT",
            role="STUDENT",
            review_level="",
            scope="",
            return_policy="NONE",
            allowed_reject_to=[],
        ),
        WorkflowNodeDef(
            id=1,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type="REVIEW",
            role="TEACHER",
            review_level="TEACHER",
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
        WorkflowNodeDef(
            id=2,
            code="COLLEGE_EXPERT",
            name="院级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL2",
            scope="COLLEGE",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1],
        ),
        WorkflowNodeDef(
            id=3,
            code="SCHOOL_EXPERT",
            name="校级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL1",
            scope="SCHOOL",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1, 2],
        ),
        WorkflowNodeDef(
            id=4,
            code="SCHOOL_FINALIZE",
            name="校级确认结题",
            node_type="APPROVAL",
            role="LEVEL1_ADMIN",
            review_level="LEVEL1",
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
    ],
}


class WorkflowService:
    @staticmethod
    def get_active_workflow(
        phase: str, batch: Optional[ProjectBatch] = None
    ) -> Optional[WorkflowConfig]:
        """获取激活的流程配置"""
        qs = WorkflowConfig.objects.filter(phase=phase, is_active=True)
        if batch:
            workflow = qs.filter(batch=batch).order_by("-version", "-id").first()
            if workflow:
                return workflow
        return qs.filter(batch__isnull=True).order_by("-version", "-id").first()

    @staticmethod
    def get_nodes(
        phase: str, batch: Optional[ProjectBatch] = None
    ) -> List[WorkflowNodeDef]:
        """获取流程所有节点"""
        workflow = WorkflowService.get_active_workflow(phase, batch)
        if not workflow:
            return DEFAULT_WORKFLOWS.get(phase, [])
        nodes = list(
            WorkflowNode.objects.filter(workflow=workflow, is_active=True)
            .select_related("role_fk", "review_template")
            .order_by("sort_order", "id")
            .all()
        )
        if not nodes:
            return DEFAULT_WORKFLOWS.get(phase, [])
        return [
            WorkflowNodeDef(
                id=cast(Any, node).id,
                code=node.code,
                name=node.name,
                node_type=node.node_type,
                role=node.get_role_code() or node.role,
                review_level=node.review_level,
                scope=node.scope,
                return_policy=node.return_policy,
                allowed_reject_to=node.allowed_reject_to
                if isinstance(node.allowed_reject_to, list)
                else [],
                review_template_id=node.review_template.id
                if node.review_template
                else None,
                role_fk_id=cast(Any, node).role_fk_id,
            )
            for node in nodes
        ]

    @staticmethod
    def get_node_by_id(node_id: int) -> Optional[WorkflowNode]:
        """根据ID获取节点对象"""
        try:
            return WorkflowNode.objects.select_related(
                "workflow", "role_fk", "review_template"
            ).get(id=node_id)
        except WorkflowNode.DoesNotExist:
            return None

    @staticmethod
    def get_initial_node(
        phase: str, batch: Optional[ProjectBatch] = None
    ) -> Optional[WorkflowNodeDef]:
        """获取首个节点（学生提交节点）"""
        nodes = WorkflowService.get_nodes(phase, batch)
        return nodes[0] if nodes else None

    @staticmethod
    def get_next_node_by_id(current_node_id: int) -> Optional[WorkflowNodeDef]:
        """根据当前节点ID获取下一节点"""
        current_node = WorkflowService.get_node_by_id(current_node_id)
        if not current_node:
            return None

        nodes = WorkflowService.get_nodes(
            current_node.workflow.phase, current_node.workflow.batch
        )
        for idx, node in enumerate(nodes):
            if node.id == current_node_id:
                return nodes[idx + 1] if idx + 1 < len(nodes) else None
        return None

    @staticmethod
    def get_next_node(
        phase: str, current_code: str, batch: Optional[ProjectBatch] = None
    ) -> Optional[WorkflowNodeDef]:
        """根据节点code获取下一节点（向后兼容）"""
        nodes = WorkflowService.get_nodes(phase, batch)
        for idx, node in enumerate(nodes):
            if node.code == current_code:
                return nodes[idx + 1] if idx + 1 < len(nodes) else None
        return None

    @staticmethod
    def get_previous_node(
        phase: str, current_code: str, batch: Optional[ProjectBatch] = None
    ) -> Optional[WorkflowNodeDef]:
        """根据节点code获取上一节点（向后兼容）"""
        nodes = WorkflowService.get_nodes(phase, batch)
        for idx, node in enumerate(nodes):
            if node.code == current_code:
                return nodes[idx - 1] if idx - 1 >= 0 else None
        return None

    @staticmethod
    def get_node_by_code(
        phase: str, code: str, batch: Optional[ProjectBatch] = None
    ) -> Optional[WorkflowNodeDef]:
        """根据code获取节点"""
        nodes = WorkflowService.get_nodes(phase, batch)
        for node in nodes:
            if node.code == code:
                return node
        return None

    @staticmethod
    def find_expert_node(
        phase: str,
        review_level: str,
        scope: str,
        batch: Optional[ProjectBatch] = None,
    ) -> Optional[WorkflowNodeDef]:
        """查找专家评审节点"""
        nodes = WorkflowService.get_nodes(phase, batch)
        for node in nodes:
            if (
                node.node_type == "EXPERT_REVIEW"
                and node.review_level == review_level
                and node.scope == scope
            ):
                return node
        return None

    @staticmethod
    def get_reject_target_nodes(current_node_id: int) -> List[WorkflowNodeDef]:
        """获取当前节点可退回的目标节点列表"""
        current_node = WorkflowService.get_node_by_id(current_node_id)
        if not current_node or not current_node.allowed_reject_to:
            return []

        # 获取所有允许退回的节点
        target_nodes = (
            WorkflowNode.objects.filter(
                id__in=current_node.allowed_reject_to, is_active=True
            )
            .select_related("role_fk", "review_template")
            .order_by("sort_order", "id")
        )

        return [
            WorkflowNodeDef(
                id=cast(Any, node).id,
                code=node.code,
                name=node.name,
                node_type=node.node_type,
                role=node.get_role_code() or node.role,
                review_level=node.review_level,
                scope=node.scope,
                return_policy=node.return_policy,
                allowed_reject_to=node.allowed_reject_to
                if isinstance(node.allowed_reject_to, list)
                else [],
                review_template_id=node.review_template.id
                if node.review_template
                else None,
                role_fk_id=cast(Any, node).role_fk_id,
            )
            for node in target_nodes
        ]

    @staticmethod
    def validate_workflow_nodes(workflow_id: int) -> Dict[str, Any]:
        """
        验证工作流节点配置的合法性
        返回: {'valid': bool, 'errors': List[str]}
        """
        errors = []

        try:
            workflow = WorkflowConfig.objects.get(id=workflow_id)
            nodes = list(
                WorkflowNode.objects.filter(workflow=workflow, is_active=True).order_by(
                    "sort_order", "id"
                )
            )

            if not nodes:
                errors.append("流程至少需要一个节点")
                return {"valid": False, "errors": errors}

            # 验证第一个节点必须是学生提交节点
            first_node = nodes[0]
            if first_node.node_type != "SUBMIT":
                errors.append("第一个节点必须是学生提交节点（SUBMIT类型）")

            # 学生提交节点的角色应该是STUDENT
            if first_node.get_role_code() == "STUDENT" or first_node.role == "STUDENT":
                # 验证学生节点不允许退回
                if first_node.allowed_reject_to:
                    errors.append("学生提交节点不应允许退回")

            # 验证其他节点不能是学生角色
            for idx, node in enumerate(nodes[1:], start=1):
                role_code = node.get_role_code() or node.role
                if role_code == "STUDENT":
                    errors.append(
                        f"节点 '{node.name}' (序号{idx + 1}): 审核节点不能使用学生角色"
                    )

                # 验证退回目标节点存在
                if node.allowed_reject_to:
                    node_ids = {cast(Any, n).id for n in nodes}
                    for target_id in node.allowed_reject_to:
                        if target_id not in node_ids:
                            errors.append(
                                f"节点 '{node.name}': 退回目标节点ID {target_id} 不存在"
                            )

            return {"valid": len(errors) == 0, "errors": errors}

        except WorkflowConfig.DoesNotExist:
            return {"valid": False, "errors": ["工作流配置不存在"]}
        except Exception as e:
            return {"valid": False, "errors": [f"验证失败: {str(e)}"]}
