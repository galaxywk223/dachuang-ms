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
    require_expert_review: bool
    scope: str
    return_policy: str
    allowed_reject_to: List[int]  # 允许退回的目标节点ID列表
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
            require_expert_review=False,
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
            require_expert_review=False,
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
        WorkflowNodeDef(
            id=2,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type="APPROVAL",
            role="LEVEL2_ADMIN",
            review_level="LEVEL2",
            require_expert_review=True,
            scope="COLLEGE",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1],
        ),
        WorkflowNodeDef(
            id=3,
            code="SCHOOL_PUBLISH",
            name="校级发布立项",
            node_type="APPROVAL",
            role="LEVEL1_ADMIN",
            review_level="LEVEL1",
            require_expert_review=True,
            scope="SCHOOL",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1, 2],
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
            require_expert_review=False,
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
            require_expert_review=False,
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
        WorkflowNodeDef(
            id=2,
            code="COLLEGE_FINALIZE",
            name="学院确认",
            node_type="APPROVAL",
            role="LEVEL2_ADMIN",
            review_level="LEVEL2",
            require_expert_review=True,
            scope="COLLEGE",
            return_policy="STUDENT",
            allowed_reject_to=[0, 1],
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
            require_expert_review=False,
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
            require_expert_review=False,
            scope="",
            return_policy="STUDENT",
            allowed_reject_to=[0],
        ),
        WorkflowNodeDef(
            id=2,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type="APPROVAL",
            role="LEVEL2_ADMIN",
            review_level="LEVEL2",
            require_expert_review=True,
            scope="COLLEGE",
            return_policy="PREVIOUS",
            allowed_reject_to=[0, 1],
        ),
        WorkflowNodeDef(
            id=3,
            code="SCHOOL_FINALIZE",
            name="校级确认结题",
            node_type="APPROVAL",
            role="LEVEL1_ADMIN",
            review_level="LEVEL1",
            require_expert_review=True,
            scope="SCHOOL",
            return_policy="STUDENT",
            allowed_reject_to=[0, 1, 2],
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
            .select_related("role_fk")
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
                require_expert_review=node.require_expert_review,
                scope=node.scope,
                return_policy=node.return_policy,
                allowed_reject_to=node.allowed_reject_to
                if isinstance(node.allowed_reject_to, list)
                else [],
                role_fk_id=cast(Any, node).role_fk_id,
            )
            for node in nodes
        ]

    @staticmethod
    def get_node_by_id(node_id: int) -> Optional[WorkflowNode]:
        """根据ID获取节点对象"""
        try:
            return WorkflowNode.objects.select_related("workflow", "role_fk").get(
                id=node_id
            )
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
        """查找需要专家评审的节点"""
        nodes = WorkflowService.get_nodes(phase, batch)
        for node in nodes:
            if node.require_expert_review and node.review_level == review_level:
                if not scope or node.scope == scope:
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
            .select_related("role_fk")
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
                require_expert_review=node.require_expert_review,
                scope=node.scope,
                return_policy=node.return_policy,
                allowed_reject_to=node.allowed_reject_to
                if isinstance(node.allowed_reject_to, list)
                else [],
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

            submit_nodes = [node for node in nodes if node.node_type == "SUBMIT"]
            if len(submit_nodes) != 1:
                errors.append("流程只能包含一个学生提交节点（SUBMIT类型）")

            # 学生提交节点的角色必须是STUDENT
            if first_node.get_role_code() != "STUDENT":
                errors.append("学生提交节点角色必须是学生（STUDENT）")
            # 验证学生节点不允许退回
            if first_node.allowed_reject_to:
                errors.append("学生提交节点不应允许退回")
            if first_node.require_expert_review:
                errors.append("学生提交节点不能启用专家评审")

            # 验证其他节点不能是学生角色
            node_ids = {cast(Any, n).id for n in nodes}
            node_order = {cast(Any, n).id: idx for idx, n in enumerate(nodes)}
            for idx, node in enumerate(nodes[1:], start=1):
                role_code = node.get_role_code() or node.role
                if role_code == "STUDENT":
                    errors.append(
                        f"节点 '{node.name}' (序号{idx + 1}): 审核节点不能使用学生角色"
                    )

                # 验证退回目标节点存在
                if node.allowed_reject_to:
                    for target_id in node.allowed_reject_to:
                        if target_id not in node_ids:
                            errors.append(
                                f"节点 '{node.name}': 退回目标节点ID {target_id} 不存在"
                            )
                        elif node_order.get(target_id, -1) >= node_order.get(
                            cast(Any, node).id, idx
                        ):
                            errors.append(
                                f"节点 '{node.name}': 退回目标必须为前序节点"
                            )

                if node.node_type == "EXPERT_REVIEW":
                    errors.append(
                        f"节点 '{node.name}': EXPERT_REVIEW 节点类型已废弃，请改用专家评审开关"
                    )

            return {"valid": len(errors) == 0, "errors": errors}

        except WorkflowConfig.DoesNotExist:
            return {"valid": False, "errors": ["工作流配置不存在"]}
        except Exception as e:
            return {"valid": False, "errors": [f"验证失败: {str(e)}"]}

    @staticmethod
    def check_node_time_window(node, check_date):
        """
        检查节点的时间窗口
        返回: (ok: bool, message: str)
        """
        if not node.start_date and not node.end_date:
            # 如果节点没有配置时间限制，则始终允许
            return True, ""

        if node.start_date and check_date < node.start_date:
            return False, f"当前未到开放时间（开始时间：{node.start_date}）"

        if node.end_date and check_date > node.end_date:
            return False, f"当前已超过截止时间（截止时间：{node.end_date}）"

        return True, ""

    @staticmethod
    def get_current_node_for_project(project, phase):
        """
        获取项目在指定阶段的当前节点
        """
        from apps.projects.models import ProjectPhaseInstance

        phase_instance = ProjectPhaseInstance.objects.filter(
            project=project, phase=phase
        ).first()

        if not phase_instance or not phase_instance.current_node_id:
            return None

        try:
            return WorkflowNode.objects.get(id=phase_instance.current_node_id)
        except WorkflowNode.DoesNotExist:
            return None

    @staticmethod
    def check_phase_window(phase, batch, check_date):
        """
        检查阶段的时间窗口（用于学生提交）
        返回: (ok: bool, message: str)
        """
        try:
            workflow = WorkflowConfig.objects.filter(
                batch=batch, phase=phase, is_active=True
            ).first()

            if not workflow:
                return True, ""  # 没有配置则允许

            # 获取学生提交节点（第一个SUBMIT类型节点）
            submit_node = WorkflowNode.objects.filter(
                workflow=workflow, node_type="SUBMIT", is_active=True
            ).first()

            if not submit_node:
                return True, ""  # 没有提交节点则允许

            return WorkflowService.check_node_time_window(submit_node, check_date)
        except Exception:
            return False, "时间窗口校验失败，请联系管理员"

    @staticmethod
    def check_review_node_window(project, phase, check_date):
        """
        检查项目当前审核节点的时间窗口
        返回: (ok: bool, message: str)
        """
        try:
            current_node = WorkflowService.get_current_node_for_project(project, phase)
            if not current_node:
                return True, ""  # 没有当前节点则允许

            return WorkflowService.check_node_time_window(current_node, check_date)
        except Exception:
            return False, "时间窗口校验失败，请联系管理员"
