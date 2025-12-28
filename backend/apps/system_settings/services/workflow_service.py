"""
Workflow configuration helper.
"""

from dataclasses import dataclass
from typing import List, Optional

from apps.system_settings.models import WorkflowConfig, WorkflowNode, ProjectBatch


@dataclass(frozen=True)
class WorkflowNodeDef:
    code: str
    name: str
    node_type: str
    role: str
    review_level: str
    scope: str
    return_policy: str
    review_template_id: Optional[int] = None


DEFAULT_WORKFLOWS = {
    "APPLICATION": [
        WorkflowNodeDef(
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type="REVIEW",
            role="TEACHER",
            review_level="TEACHER",
            scope="",
            return_policy="STUDENT",
        ),
        WorkflowNodeDef(
            code="COLLEGE_EXPERT",
            name="院级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL2",
            scope="COLLEGE",
            return_policy="PREVIOUS",
        ),
        WorkflowNodeDef(
            code="SCHOOL_EXPERT",
            name="校级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL1",
            scope="SCHOOL",
            return_policy="PREVIOUS",
        ),
        WorkflowNodeDef(
            code="SCHOOL_PUBLISH",
            name="校级发布立项",
            node_type="APPROVAL",
            role="LEVEL1_ADMIN",
            review_level="LEVEL1",
            scope="",
            return_policy="NONE",
        ),
    ],
    "MID_TERM": [
        WorkflowNodeDef(
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type="REVIEW",
            role="TEACHER",
            review_level="TEACHER",
            scope="",
            return_policy="STUDENT",
        ),
        WorkflowNodeDef(
            code="COLLEGE_EXPERT",
            name="院级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL2",
            scope="COLLEGE",
            return_policy="PREVIOUS",
        ),
        WorkflowNodeDef(
            code="COLLEGE_FINALIZE",
            name="学院确认",
            node_type="APPROVAL",
            role="LEVEL2_ADMIN",
            review_level="LEVEL2",
            scope="",
            return_policy="STUDENT",
        ),
    ],
    "CLOSURE": [
        WorkflowNodeDef(
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type="REVIEW",
            role="TEACHER",
            review_level="TEACHER",
            scope="",
            return_policy="STUDENT",
        ),
        WorkflowNodeDef(
            code="COLLEGE_EXPERT",
            name="院级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL2",
            scope="COLLEGE",
            return_policy="PREVIOUS",
        ),
        WorkflowNodeDef(
            code="SCHOOL_EXPERT",
            name="校级专家评审",
            node_type="EXPERT_REVIEW",
            role="EXPERT",
            review_level="LEVEL1",
            scope="SCHOOL",
            return_policy="PREVIOUS",
        ),
        WorkflowNodeDef(
            code="SCHOOL_FINALIZE",
            name="校级确认结题",
            node_type="APPROVAL",
            role="LEVEL1_ADMIN",
            review_level="LEVEL1",
            scope="",
            return_policy="STUDENT",
        ),
    ],
}


class WorkflowService:
    @staticmethod
    def get_active_workflow(phase: str, batch: Optional[ProjectBatch] = None) -> Optional[WorkflowConfig]:
        qs = WorkflowConfig.objects.filter(phase=phase, is_active=True)
        if batch:
            workflow = qs.filter(batch=batch).order_by("-version", "-id").first()
            if workflow:
                return workflow
        return qs.filter(batch__isnull=True).order_by("-version", "-id").first()

    @staticmethod
    def get_nodes(phase: str, batch: Optional[ProjectBatch] = None) -> List[WorkflowNodeDef]:
        workflow = WorkflowService.get_active_workflow(phase, batch)
        if not workflow:
            return DEFAULT_WORKFLOWS.get(phase, [])
        nodes = list(
            WorkflowNode.objects.filter(workflow=workflow, is_active=True)
            .order_by("sort_order", "id")
            .all()
        )
        if not nodes:
            return DEFAULT_WORKFLOWS.get(phase, [])
        return [
            WorkflowNodeDef(
                code=node.code,
                name=node.name,
                node_type=node.node_type,
                role=node.role,
                review_level=node.review_level,
                scope=node.scope,
                return_policy=node.return_policy,
                review_template_id=node.review_template.id if node.review_template else None,
            )
            for node in nodes
        ]

    @staticmethod
    def get_initial_node(phase: str, batch: Optional[ProjectBatch] = None) -> Optional[WorkflowNodeDef]:
        nodes = WorkflowService.get_nodes(phase, batch)
        return nodes[0] if nodes else None

    @staticmethod
    def get_next_node(phase: str, current_code: str, batch: Optional[ProjectBatch] = None) -> Optional[WorkflowNodeDef]:
        nodes = WorkflowService.get_nodes(phase, batch)
        for idx, node in enumerate(nodes):
            if node.code == current_code:
                return nodes[idx + 1] if idx + 1 < len(nodes) else None
        return None

    @staticmethod
    def get_previous_node(
        phase: str, current_code: str, batch: Optional[ProjectBatch] = None
    ) -> Optional[WorkflowNodeDef]:
        nodes = WorkflowService.get_nodes(phase, batch)
        for idx, node in enumerate(nodes):
            if node.code == current_code:
                return nodes[idx - 1] if idx - 1 >= 0 else None
        return None

    @staticmethod
    def get_node_by_code(phase: str, code: str, batch: Optional[ProjectBatch] = None) -> Optional[WorkflowNodeDef]:
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
        nodes = WorkflowService.get_nodes(phase, batch)
        for node in nodes:
            if (
                node.node_type == "EXPERT_REVIEW"
                and node.review_level == review_level
                and node.scope == scope
            ):
                return node
        return None
