"""
管理员分配解析服务
"""

from apps.system_settings.models import PhaseScopeConfig, AdminAssignment


class AdminAssignmentService:
    @staticmethod
    def get_scope_config(batch, phase):
        config = PhaseScopeConfig.objects.filter(batch=batch, phase=phase).first()
        if not config:
            raise ValueError("未配置阶段数据范围，请联系校级管理员完善配置")
        return config

    @staticmethod
    def get_scope_value(project, scope_type):
        if scope_type == PhaseScopeConfig.ScopeType.COLLEGE:
            college = project.leader.college if project.leader else ""
            if not college:
                raise ValueError("项目缺少学院信息，无法解析管理员配置")
            return college
        if scope_type == PhaseScopeConfig.ScopeType.PROJECT_CATEGORY:
            if not project.category_id:
                raise ValueError("项目缺少项目类别，无法解析管理员配置")
            return str(project.category_id)
        if scope_type == PhaseScopeConfig.ScopeType.PROJECT_LEVEL:
            if not project.level_id:
                raise ValueError("项目缺少项目级别，无法解析管理员配置")
            return str(project.level_id)
        if scope_type == PhaseScopeConfig.ScopeType.KEY_FIELD:
            return "1" if project.is_key_field else "0"
        raise ValueError("不支持的数据范围维度")

    @staticmethod
    def resolve_admin_user(project, phase, workflow_node):
        config = AdminAssignmentService.get_scope_config(project.batch, phase)
        scope_value = AdminAssignmentService.get_scope_value(project, config.scope_type)
        assignment = (
            AdminAssignment.objects.filter(
                batch=project.batch,
                phase=phase,
                workflow_node=workflow_node,
                scope_value=scope_value,
            )
            .select_related("admin_user")
            .first()
        )
        if not assignment:
            raise ValueError("未配置管理员分配，请联系校级管理员完善配置")
        return assignment.admin_user
