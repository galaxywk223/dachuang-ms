"""
项目申报智能校验服务
"""

from ..models import Project, ProjectMember
from apps.system_settings.services import SystemSettingService
from apps.users.models import User


class ProjectValidationService:
    """
    项目申报智能校验服务
    包括：标题查重、超项拦截、学院配额校验等
    """

    @staticmethod
    def validate_project_application(project, user, is_update=False):
        """
        验证项目申报
        :param project: 项目实例
        :param user: 申报用户
        :param is_update: 是否为更新操作
        :return: 校验结果 dict，包含 is_valid 和 errors
        """
        errors = []

        # 获取批次配置
        if not project.batch:
            errors.append("项目必须关联到有效批次")
            return {"is_valid": False, "errors": errors}

        settings_service = SystemSettingService()
        limit_rules = (
            settings_service.get_setting("LIMIT_RULES", project.batch.id) or {}
        )
        validation_rules = (
            settings_service.get_setting("VALIDATION_RULES", project.batch.id) or {}
        )

        # 1. 标题查重校验
        if limit_rules.get("dedupe_title", True):
            title_error = ProjectValidationService._validate_title_duplication(
                project, is_update
            )
            if title_error:
                errors.append(title_error)

        # 2. 标题格式校验
        title_format_error = ProjectValidationService._validate_title_format(
            project.title, validation_rules
        )
        if title_format_error:
            errors.append(title_format_error)

        # 3. 项目级别学院限制校验
        if project.level and project.leader:
            level_error = ProjectValidationService._validate_level_by_college(
                project.level.id, project.leader.college, validation_rules
            )
            if level_error:
                errors.append(level_error)

        # 4. 学院配额校验
        if project.leader:
            quota_error = ProjectValidationService._validate_college_quota(
                project, limit_rules, is_update
            )
            if quota_error:
                errors.append(quota_error)

        # 5. 指导教师校验
        if hasattr(project, "_advisors_list"):
            advisor_errors = ProjectValidationService._validate_advisors(
                project, limit_rules, is_update
            )
            errors.extend(advisor_errors)

        # 6. 项目成员校验
        if hasattr(project, "_members_list"):
            member_errors = ProjectValidationService._validate_members(
                project, limit_rules, is_update
            )
            errors.extend(member_errors)

        return {"is_valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def _validate_title_duplication(project, is_update):
        """
        标题查重：检查是否与历史项目标题重复
        """
        query = Project.objects.filter(title__iexact=project.title, is_deleted=False)

        # 如果是更新操作，排除自身
        if is_update and project.id:
            query = query.exclude(id=project.id)

        duplicate = query.first()
        if duplicate:
            return f"项目标题与已有项目重复（项目编号：{duplicate.project_no}，批次：{duplicate.batch.name if duplicate.batch else '未知'}）"

        return None

    @staticmethod
    def _validate_title_format(title, validation_rules):
        """
        标题格式校验
        """
        import re

        # 标题长度校验
        min_length = validation_rules.get("title_min_length", 0)
        max_length = validation_rules.get("title_max_length", 200)

        if len(title) < min_length:
            return f"项目标题长度不能少于{min_length}个字符"

        if len(title) > max_length:
            return f"项目标题长度不能超过{max_length}个字符"

        # 标题正则校验
        title_regex = validation_rules.get("title_regex", "")
        if title_regex:
            if not re.match(title_regex, title):
                return "项目标题格式不符合要求"

        return None

    @staticmethod
    def _validate_level_by_college(level_id, college, validation_rules):
        """
        按学院限制项目级别
        """
        allowed_levels = validation_rules.get("allowed_levels_by_college", {})
        if not allowed_levels:
            return None

        college_name = college or "未知学院"
        if college_name in allowed_levels:
            if level_id not in allowed_levels[college_name]:
                return f"{college_name}不允许申报该项目级别"

        return None

    @staticmethod
    def _validate_college_quota(project, limit_rules, is_update):
        """
        学院配额校验
        """
        college_quota = limit_rules.get("college_quota", {})
        if not college_quota:
            return None

        college = project.leader.college if project.leader else None
        if not college or college not in college_quota:
            return None

        # 获取配额限制
        quota_limit = college_quota[college]

        # 统计当前学院在同一批次的项目数
        query = Project.objects.filter(
            batch=project.batch, leader__college=college, is_deleted=False
        ).exclude(
            status__in=[
                Project.ProjectStatus.DRAFT,
                Project.ProjectStatus.TERMINATED,
                Project.ProjectStatus.APPLICATION_RETURNED,
            ]
        )

        # 如果是更新操作，排除自身
        if is_update and project.id:
            query = query.exclude(id=project.id)

        current_count = query.count()

        if current_count >= quota_limit:
            return f"{college}的项目配额已满（限额{quota_limit}项，已申报{current_count}项）"

        return None

    @staticmethod
    def _validate_advisors(project, limit_rules, is_update):
        """
        指导教师校验
        """
        errors = []
        advisors = getattr(project, "_advisors_list", [])

        # 指导教师数量限制
        max_advisors = limit_rules.get("max_advisors", 2)
        if len(advisors) > max_advisors:
            errors.append(f"指导教师数量不能超过{max_advisors}人")

        # 职称要求校验
        if limit_rules.get("advisor_title_required", False):
            for advisor in advisors:
                if not advisor.get("title"):
                    errors.append(
                        f"指导教师 {advisor.get('name', '未知')} 必须填写职称"
                    )

        # 指导教师在研项目数限制
        max_teacher_active = limit_rules.get("max_teacher_active", 5)
        teacher_excellent_bonus = limit_rules.get("teacher_excellent_bonus", 0)

        for advisor in advisors:
            advisor_user_id = advisor.get("user_id")
            if not advisor_user_id:
                continue

            # 统计教师在研项目数
            active_count = Project.objects.filter(
                advisor_id=advisor_user_id,
                is_deleted=False,
                status__in=[
                    Project.ProjectStatus.IN_PROGRESS,
                    Project.ProjectStatus.MID_TERM_DRAFT,
                    Project.ProjectStatus.MID_TERM_SUBMITTED,
                    Project.ProjectStatus.MID_TERM_REVIEWING,
                    Project.ProjectStatus.MID_TERM_APPROVED,
                    Project.ProjectStatus.READY_FOR_CLOSURE,
                ],
            ).count()

            # 计算优秀项目奖励名额
            if teacher_excellent_bonus > 0:
                excellent_count = Project.objects.filter(
                    advisor_id=advisor_user_id,
                    is_deleted=False,
                    status=Project.ProjectStatus.CLOSED,
                    closure_rating="EXCELLENT",
                ).count()
                max_allowed = max_teacher_active + (
                    excellent_count * teacher_excellent_bonus
                )
            else:
                max_allowed = max_teacher_active

            if active_count >= max_allowed:
                errors.append(
                    f"指导教师 {advisor.get('name', '未知')} 在研项目数已达上限（{active_count}/{max_allowed}）"
                )

        return errors

    @staticmethod
    def _validate_members(project, limit_rules, is_update):
        """
        项目成员校验
        """
        errors = []
        members = getattr(project, "_members_list", [])

        # 成员数量限制
        max_members = limit_rules.get("max_members", 5)
        if len(members) > max_members:
            errors.append(f"项目成员数量不能超过{max_members}人（不含负责人）")

        # 学生参与项目数限制
        max_student_member = limit_rules.get("max_student_member", 1)

        # 检查所有成员（包括负责人）
        all_members = []
        if project.leader:
            all_members.append(project.leader.id)
        all_members.extend([m.get("user_id") for m in members if m.get("user_id")])

        for member_id in all_members:
            # 统计学生作为负责人的项目数
            leader_count = Project.objects.filter(
                leader_id=member_id, batch=project.batch, is_deleted=False
            ).exclude(
                status__in=[
                    Project.ProjectStatus.DRAFT,
                    Project.ProjectStatus.TERMINATED,
                ]
            )

            # 如果是更新操作，排除自身
            if is_update and project.id:
                leader_count = leader_count.exclude(id=project.id)

            leader_count = leader_count.count()

            # 统计学生作为成员的项目数
            member_count = ProjectMember.objects.filter(
                user_id=member_id,
                project__batch=project.batch,
                project__is_deleted=False,
                is_deleted=False,
            ).exclude(
                project__status__in=[
                    Project.ProjectStatus.DRAFT,
                    Project.ProjectStatus.TERMINATED,
                ]
            )

            if is_update and project.id:
                member_count = member_count.exclude(project_id=project.id)

            member_count = member_count.count()

            total_count = leader_count + member_count

            if total_count >= max_student_member:
                try:
                    user = User.objects.get(id=member_id)
                    user_name = user.real_name or user.username
                except User.DoesNotExist:
                    user_name = "未知"

                errors.append(
                    f"成员 {user_name} 在当前批次参与的项目数已达上限（{total_count}/{max_student_member}）"
                )

        return errors

    @staticmethod
    def validate_advisor_available(advisor_user, batch):
        """
        检查指导教师是否有未结题项目限报
        :param advisor_user: 教师用户
        :param batch: 项目批次
        :return: dict with is_available and message
        """
        # 检查是否有未结题的历史项目
        unfinished_projects = Project.objects.filter(
            advisor=advisor_user,
            is_deleted=False,
            status__in=[
                Project.ProjectStatus.IN_PROGRESS,
                Project.ProjectStatus.MID_TERM_DRAFT,
                Project.ProjectStatus.MID_TERM_SUBMITTED,
                Project.ProjectStatus.MID_TERM_REVIEWING,
                Project.ProjectStatus.MID_TERM_APPROVED,
                Project.ProjectStatus.READY_FOR_CLOSURE,
                Project.ProjectStatus.CLOSURE_DRAFT,
                Project.ProjectStatus.CLOSURE_SUBMITTED,
                Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
                Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            ],
        ).exclude(batch=batch)

        if unfinished_projects.exists():
            project_titles = ", ".join([p.title for p in unfinished_projects[:3]])
            return {
                "is_available": False,
                "message": f"该教师有未结题项目：{project_titles}{'等' if unfinished_projects.count() > 3 else ''}",
            }

        return {"is_available": True, "message": ""}
