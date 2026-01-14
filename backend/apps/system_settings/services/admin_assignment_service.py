"""
管理员分配解析服务
基于角色的 scope_dimension 和用户的 managed_scope_value 进行自动解析
"""

from apps.users.models import User
from apps.dictionaries.models import DictionaryItem, DictionaryType


class AdminAssignmentService:
    @staticmethod
    def resolve_admin_user(project, phase, workflow_node):
        """
        解析唯一管理员用户
        根据工作流节点的角色和角色的数据范围维度，自动查找负责该项目的管理员

        Args:
            project: 项目实例
            phase: 阶段（APPLICATION/MID_TERM/CLOSURE）
            workflow_node: 工作流节点实例

        Returns:
            User: 负责该项目的管理员用户

        Raises:
            ValueError: 未找到管理员或配置错误时
        """
        role = workflow_node.role_fk
        if not role:
            raise ValueError("节点未配置执行角色")

        scope_dimension = role.scope_dimension
        if not scope_dimension:
            # 校级管理员（无数据范围限制）
            # 返回该角色的任意用户（假设只有一个校级管理员）
            user = User.objects.filter(role_fk=role, is_active=True).first()
            if not user:
                raise ValueError(f"未找到角色为 {role.name} 的管理员用户")
            return user

        # 根据维度类型提取项目的维度值（DictionaryItem.id）
        scope_value_id = AdminAssignmentService.get_scope_value_id(
            project, scope_dimension
        )

        # 查找管理员用户
        user = User.objects.filter(
            role_fk=role, managed_scope_value_id=scope_value_id, is_active=True
        ).first()

        if not user:
            raise ValueError(
                f"未找到负责该项目的管理员。"
                f"角色：{role.name}，维度：{scope_dimension}，维度值ID：{scope_value_id}。"
                f"请联系校级管理员在用户管理中配置相应管理员。"
            )

        return user

    @staticmethod
    def get_scope_value_id(project, scope_dimension):
        """
        根据维度类型提取项目的维度值ID（DictionaryItem.id）

        Args:
            project: 项目实例
            scope_dimension: 数据范围维度（COLLEGE/PROJECT_CATEGORY/PROJECT_LEVEL/KEY_FIELD）

        Returns:
            int: 对应的 DictionaryItem.id

        Raises:
            ValueError: 项目缺少必要信息或字典项不存在时
        """
        if scope_dimension == "COLLEGE":
            college_value = project.leader.college if project.leader else None
            if not college_value:
                raise ValueError("项目负责人缺少学院信息")
            item = DictionaryItem.objects.filter(
                dict_type__code="college", value=college_value
            ).first()
            if not item:
                raise ValueError(f"未找到学院字典项：{college_value}")
            return item.id

        elif scope_dimension == "PROJECT_CATEGORY":
            if not project.category_id:
                raise ValueError("项目缺少项目类别")
            return project.category_id

        elif scope_dimension == "PROJECT_LEVEL":
            if not project.level_id:
                raise ValueError("项目缺少项目级别")
            return project.level_id

        elif scope_dimension == "KEY_FIELD":
            # 重点领域的处理
            try:
                key_field_type = DictionaryType.objects.get(code="key_field")
            except DictionaryType.DoesNotExist:
                raise ValueError("未找到重点领域字典类型，请联系管理员配置")

            if project.is_key_field and project.key_domain_code:
                # 重点项目，使用具体的重点领域代码
                item = DictionaryItem.objects.filter(
                    dict_type=key_field_type, value=project.key_domain_code
                ).first()
            else:
                # 一般项目
                item = DictionaryItem.objects.filter(
                    dict_type=key_field_type, value="GENERAL"
                ).first()

            if not item:
                raise ValueError("未找到重点领域字典项")
            return item.id

        else:
            raise ValueError(f"不支持的数据范围维度：{scope_dimension}")
