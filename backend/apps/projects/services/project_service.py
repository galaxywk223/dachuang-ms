"""
项目业务逻辑层
"""

from django.utils import timezone
from django.db import transaction
from ..models import (
    Project,
    ProjectMember,
    ProjectProgress,
    ProjectExpenditure,
    ProjectChangeRequest,
    ProjectChangeReview,
)


class ProjectService:
    """
    项目服务类
    """

    @staticmethod
    def generate_project_no(year, college_code=""):
        """
        生成项目编号
        格式：YYYY + 学院代码 + 4位序号
        例如：2025CS0001
        """
        import re

        college_code = (college_code or "").strip().upper()
        # 保证学院代码只包含字母数字
        college_code = re.sub(r"[^0-9A-Z]", "", college_code) or "XX"
        prefix = f"{year}{college_code}"

        last_project = (
            Project.objects.filter(project_no__startswith=prefix)
            .order_by("-project_no")
            .first()
        )
        if last_project:
            suffix = last_project.project_no[len(prefix) :]
            if suffix.isdigit():
                return f"{prefix}{int(suffix) + 1:04d}"

        return f"{prefix}0001"

    @staticmethod
    @transaction.atomic
    def submit_project(project):
        """
        提交项目申报
        """
        if project.status == Project.ProjectStatus.DRAFT:
            project.status = Project.ProjectStatus.SUBMITTED
            project.submitted_at = timezone.now()
            project.save()
            return True
        return False

    @staticmethod
    def validate_member_participation(user, exclude_project_id=None):
        """
        验证学生是否已参与其他项目
        业务规则：每个学生不能同时参加两个项目
        """
        from django.db.models import Q

        # 查询用户参与的进行中的项目
        active_statuses = [
            Project.ProjectStatus.SUBMITTED,
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
        ]

        query = Q(leader=user) | Q(members=user)
        projects = Project.objects.filter(query, status__in=active_statuses)

        if exclude_project_id:
            projects = projects.exclude(id=exclude_project_id)

        return projects.count() == 0

    @staticmethod
    @transaction.atomic
    def add_project_member(project, user, role=ProjectMember.MemberRole.MEMBER):
        """
        添加项目成员
        """
        # 检查是否已经是成员
        if ProjectMember.objects.filter(project=project, user=user).exists():
            return None

        # 检查学生是否已参与其他项目
        if not ProjectService.validate_member_participation(user, project.id):
            raise ValueError("该学生已参与其他项目，不能重复参与")

        return ProjectMember.objects.create(project=project, user=user, role=role)

    @staticmethod
    def remove_project_member(project, user):
        """
        移除项目成员
        """
        try:
            member = ProjectMember.objects.get(project=project, user=user)
            if member.role != ProjectMember.MemberRole.LEADER:
                member.delete()
                return True
        except ProjectMember.DoesNotExist:
            pass
        return False

    @staticmethod
    def add_progress(project, user, title, content, attachment=None):
        """
        添加项目进度
        """
        return ProjectProgress.objects.create(
            project=project,
            title=title,
            content=content,
            attachment=attachment,
            created_by=user,
        )

    @staticmethod
    def get_user_projects(user):
        """
        获取用户相关的项目
        """
        from django.db import models

        return Project.objects.filter(
            models.Q(leader=user) | models.Q(members=user)
        ).distinct()

    @staticmethod
    def get_college_projects(college):
        """
        获取学院的项目
        """
        return Project.objects.filter(leader__college=college)

    @staticmethod
    @transaction.atomic
    def apply_closure(project, final_report, is_draft=False):
        """
        申请项目结题
        """
        if project.status not in [
            Project.ProjectStatus.READY_FOR_CLOSURE,
            Project.ProjectStatus.MID_TERM_APPROVED,  # legacy
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
            Project.ProjectStatus.CLOSURE_RETURNED,
        ]:
            raise ValueError("当前项目状态无法申请结题")

        # 更新结题报告（未重新上传则保留原文件）
        if final_report is not None:
            project.final_report = final_report

        if is_draft:
            # 保存为草稿
            project.status = Project.ProjectStatus.CLOSURE_DRAFT
        else:
            # 提交结题申请
            project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
            project.closure_applied_at = timezone.now()

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def submit_closure(project):
        """
        提交结题申请（从草稿状态）
        """
        if project.status == Project.ProjectStatus.CLOSURE_DRAFT:
            # 验证必需的材料
            if not project.final_report:
                raise ValueError("请先上传结题报告书")

            # 验证至少有一项成果
            if project.achievements.count() < 1:
                raise ValueError("请至少添加一项研究成果")

            expected_list = project.expected_results_data or []
            if expected_list:
                actual_counts = {}
                for ach in project.achievements.select_related("achievement_type"):
                    if not ach.achievement_type:
                        continue
                    type_value = ach.achievement_type.value
                    actual_counts[type_value] = actual_counts.get(type_value, 0) + 1
                for expected in expected_list:
                    if not isinstance(expected, dict):
                        continue
                    type_value = expected.get("achievement_type")
                    try:
                        expected_count = int(
                            expected.get("expected_count") or expected.get("count") or 0
                        )
                    except (TypeError, ValueError):
                        expected_count = 0
                    if not type_value or expected_count <= 0:
                        continue
                    actual = actual_counts.get(type_value, 0)
                    if actual < expected_count:
                        raise ValueError(
                            f"预期成果未完成：{type_value} 需{expected_count}项，当前{actual}项"
                        )

            project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
            project.closure_applied_at = timezone.now()
            project.save()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def revoke_closure(project):
        """
        撤销结题申请
        """
        # 只能在学院审核前撤销
        if project.status == Project.ProjectStatus.CLOSURE_SUBMITTED:
            project.status = Project.ProjectStatus.IN_PROGRESS
            project.save()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def apply_mid_term(project, mid_term_report, is_draft=False):
        """
        申请项目中期检查
        """
        allowed_statuses = {
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.MID_TERM_DRAFT,
            Project.ProjectStatus.MID_TERM_REJECTED,
            Project.ProjectStatus.MID_TERM_RETURNED,
        }
        if project.status not in allowed_statuses:
            raise ValueError("当前项目状态不允许提交中期检查")

        # 更新中期报告（未重新上传则保留原文件）
        if mid_term_report is not None:
            project.mid_term_report = mid_term_report

        if is_draft:
            # 保存为草稿
            project.status = Project.ProjectStatus.MID_TERM_DRAFT
        else:
            # 提交中期申请
            project.status = Project.ProjectStatus.MID_TERM_SUBMITTED
            project.mid_term_submitted_at = timezone.now()

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def submit_mid_term(project):
        """
        提交中期申请（从草稿状态）
        """
        if project.status == Project.ProjectStatus.MID_TERM_DRAFT:
            # 验证必需的材料
            if not project.mid_term_report:
                raise ValueError("请先上传中期检查报告书")

            project.status = Project.ProjectStatus.MID_TERM_SUBMITTED
            project.mid_term_submitted_at = timezone.now()
            project.save()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def revoke_mid_term(project):
        """
        撤销中期申请
        """
        if project.status == Project.ProjectStatus.MID_TERM_SUBMITTED:
            project.status = Project.ProjectStatus.IN_PROGRESS
            project.save()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def submit_mid_term_review(project, reviewer, review_comments, is_approved=True):
        """
        提交中期审核
        """
        if project.status != Project.ProjectStatus.MID_TERM_REVIEWING:
            raise ValueError("项目不在中期审核中")

        if is_approved:
            project.status = Project.ProjectStatus.READY_FOR_CLOSURE
        else:
            project.status = Project.ProjectStatus.MID_TERM_REJECTED

        project.save()
        return True

    @staticmethod
    def get_budget_stats(project):
        """
        获取项目经费统计
        """
        from decimal import Decimal

        expenditures = project.expenditures.all()
        if project.budget is None:
            total_budget = Decimal("0")
        else:
            total_budget = (
                project.budget
                if isinstance(project.budget, Decimal)
                else Decimal(str(project.budget))
            )
        used_amount = sum([exp.amount for exp in expenditures], Decimal("0"))
        remaining_amount = total_budget - used_amount
        usage_rate = float(used_amount / total_budget * 100) if total_budget else 0

        return {
            "total_budget": total_budget,
            "used_amount": used_amount,
            "remaining_amount": remaining_amount,
            "usage_rate": round(usage_rate, 2),
        }

    @staticmethod
    def add_expenditure(project, title, amount, expenditure_date, category, proof_file, created_by):
        """
        添加经费支出
        """
        stats = ProjectService.get_budget_stats(project)
        if amount > stats["remaining_amount"]:
            raise ValueError(
                f"余额不足！当前剩余经费：{stats['remaining_amount']}元，本次申请：{amount}元"
            )
        return ProjectExpenditure.objects.create(
            project=project,
            title=title,
            amount=amount,
            expenditure_date=expenditure_date,
            category=category,
            proof_file=proof_file,
            created_by=created_by,
        )

    @staticmethod
    def approve_change_request(change_request, reviewer, is_approved=True, comments=None):
        """
        审批项目变更申请
        """
        if change_request.status not in [
            ProjectChangeRequest.ChangeStatus.TEACHER_REVIEWING,
            ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
        ]:
            raise ValueError("变更申请不是待审核状态")

        change_request.reviewed_at = timezone.now()
        change_request.status = (
            ProjectChangeRequest.ChangeStatus.APPROVED
            if is_approved
            else ProjectChangeRequest.ChangeStatus.REJECTED
        )
        change_request.save()

        # Apply the change to the project if approved
        if is_approved:
            ProjectChangeReview.apply_change(change_request)

        return True
