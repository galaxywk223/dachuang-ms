"""
系统设置服务
"""

from ..models import SystemSetting, ProjectBatch
from .workflow_service import WorkflowService
from .admin_assignment_service import AdminAssignmentService


DEFAULT_SETTINGS = {
    "APPLICATION_WINDOW": {
        "enabled": False,
        "start": "",
        "end": "",
    },
    "MIDTERM_WINDOW": {
        "enabled": False,
        "start": "",
        "end": "",
    },
    "CLOSURE_WINDOW": {
        "enabled": False,
        "start": "",
        "end": "",
    },
    "LIMIT_RULES": {
        "max_advisors": 2,
        "max_members": 5,
        "max_teacher_active": 5,
        "max_student_active": 1,
        "max_student_member": 1,
        "teacher_excellent_bonus": 0,
        "college_quota": {},
        "dedupe_title": True,
        "advisor_title_required": False,
    },
    "PROCESS_RULES": {
        "allow_active_reapply": False,
        "show_material_in_closure_review": True,
    },
    "REVIEW_RULES": {
        "teacher_application_comment_min": 0,
    },
    "VALIDATION_RULES": {
        "title_regex": "",
        "title_min_length": 0,
        "title_max_length": 200,
        "allowed_project_types": [],
        "allowed_project_types_by_college": {},
        "allowed_levels_by_college": {},
    },
}


class SystemSettingService:
    """
    系统设置读取辅助
    """

    @staticmethod
    def get_current_batch():
        return (
            ProjectBatch.objects.filter(
                status=ProjectBatch.STATUS_ACTIVE, is_active=True, is_deleted=False
            )
            .order_by("-year", "-id")
            .first()
        )

    @staticmethod
    def get_setting(code, default=None, batch=None):
        """
        获取指定批次的配置。
        每个批次必须有自己的独立配置，不应该回退到全局配置。
        """
        batch_obj = batch
        if batch_obj is None:
            batch_obj = SystemSettingService.get_current_batch()
        elif isinstance(batch_obj, int):
            batch_obj = ProjectBatch.objects.filter(id=batch_obj).first()
        elif isinstance(batch_obj, str) and batch_obj.isdigit():
            batch_obj = ProjectBatch.objects.filter(id=int(batch_obj)).first()

        # 只查找指定批次的配置，不回退到全局配置
        setting = None
        if batch_obj:
            setting = SystemSetting.objects.filter(
                code=code, is_active=True, batch=batch_obj
            ).first()

        # 如果找到配置，合并到默认值
        base = default or DEFAULT_SETTINGS.get(code, {})
        if setting:
            merged = dict(base)
            merged.update(setting.data or {})
            return merged
        return base

    # 时间窗口检查统一使用阶段窗口配置
    # 请使用 WorkflowService.check_phase_window


__all__ = [
    "DEFAULT_SETTINGS",
    "SystemSettingService",
    "WorkflowService",
    "AdminAssignmentService",
]
