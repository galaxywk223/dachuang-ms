"""
经费管理服务
"""

from django.db import transaction
from django.utils import timezone
from ..models import Project, ProjectExpenditure, BudgetChangeRequest
from apps.notifications.services import NotificationService


class BudgetService:
    """
    经费管理服务类
    """

    @staticmethod
    @transaction.atomic
    def submit_expenditure(project, user, data):
        """
        提交经费支出
        """
        # 检查项目是否立项
        if project.status not in [
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
        ]:
            raise ValueError("项目必须处于立项或在研状态才能提交经费支出")

        # 检查是否超出预算
        total_expenditure = (
            ProjectExpenditure.objects.filter(
                project=project,
                is_deleted=False,
                status__in=[
                    ProjectExpenditure.ExpenditureStatus.RECORDED,
                    ProjectExpenditure.ExpenditureStatus.PENDING,
                    ProjectExpenditure.ExpenditureStatus.APPROVED,
                ],
            ).aggregate(total=models.Sum("amount"))["total"]
            or 0
        )

        new_amount = data.get("amount", 0)
        if total_expenditure + new_amount > project.approved_budget:
            raise ValueError(
                f"支出总额不能超过预算额度（预算：{project.approved_budget}，"
                f"已支出：{total_expenditure}，本次：{new_amount}）"
            )

        # 创建支出记录
        expenditure = ProjectExpenditure.objects.create(
            project=project,
            title=data.get("title"),
            amount=new_amount,
            expenditure_date=data.get("expenditure_date"),
            category_id=data.get("category"),
            proof_file=data.get("proof_file"),
            status=ProjectExpenditure.ExpenditureStatus.PENDING,
            created_by=user,
        )

        # 发送通知给项目负责人和导师
        NotificationService.notify_expenditure_submitted(project, expenditure, user)

        return expenditure

    @staticmethod
    @transaction.atomic
    def review_expenditure(expenditure, reviewer, approved, comment=""):
        """
        审核经费支出
        """
        if expenditure.status != ProjectExpenditure.ExpenditureStatus.PENDING:
            raise ValueError("只能审核待审核状态的支出记录")

        expenditure.status = (
            ProjectExpenditure.ExpenditureStatus.APPROVED
            if approved
            else ProjectExpenditure.ExpenditureStatus.REJECTED
        )
        expenditure.reviewed_by = reviewer
        expenditure.reviewed_at = timezone.now()
        expenditure.review_comment = comment
        expenditure.save()

        # 发送通知
        NotificationService.notify_expenditure_reviewed(
            expenditure.project, expenditure, reviewer, approved, comment
        )

        return expenditure

    @staticmethod
    @transaction.atomic
    def create_budget_change_request(project, user, data):
        """
        创建预算变更申请
        """
        # 检查项目状态
        if project.status not in [
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.MID_TERM_DRAFT,
            Project.ProjectStatus.MID_TERM_SUBMITTED,
            Project.ProjectStatus.MID_TERM_REVIEWING,
            Project.ProjectStatus.MID_TERM_APPROVED,
            Project.ProjectStatus.READY_FOR_CLOSURE,
        ]:
            raise ValueError("只有在研项目才能申请预算变更")

        # 检查是否有待审核的变更申请
        pending_request = BudgetChangeRequest.objects.filter(
            project=project,
            status__in=[
                BudgetChangeRequest.RequestStatus.PENDING,
                BudgetChangeRequest.RequestStatus.TEACHER_APPROVED,
                BudgetChangeRequest.RequestStatus.LEVEL2_APPROVED,
            ],
            is_deleted=False,
        ).exists()

        if pending_request:
            raise ValueError("已有待审核的预算变更申请，请等待审核完成后再提交新申请")

        # 创建变更申请
        request_obj = BudgetChangeRequest.objects.create(
            project=project,
            original_budget=project.approved_budget or project.budget_amount,
            new_budget=data.get("new_budget"),
            reason=data.get("reason"),
            budget_breakdown=data.get("budget_breakdown", {}),
            status=BudgetChangeRequest.RequestStatus.PENDING,
            created_by=user,
        )

        # 发送通知给导师
        NotificationService.notify_budget_change_submitted(project, request_obj, user)

        return request_obj

    @staticmethod
    @transaction.atomic
    def review_budget_change(request_obj, reviewer, level, approved, comment=""):
        """
        审核预算变更申请
        :param request_obj: 预算变更申请
        :param reviewer: 审核人
        :param level: 审核级别 ('teacher', 'level2', 'level1')
        :param approved: 是否通过
        :param comment: 审核意见
        """
        # 检查审核级别和当前状态
        if level == "teacher":
            if request_obj.status != BudgetChangeRequest.RequestStatus.PENDING:
                raise ValueError("当前状态不允许导师审核")

            if approved:
                request_obj.status = BudgetChangeRequest.RequestStatus.TEACHER_APPROVED
            else:
                request_obj.status = BudgetChangeRequest.RequestStatus.TEACHER_REJECTED

            request_obj.teacher_comment = comment
            request_obj.teacher_reviewed_by = reviewer
            request_obj.teacher_reviewed_at = timezone.now()

        elif level == "level2":
            if request_obj.status != BudgetChangeRequest.RequestStatus.TEACHER_APPROVED:
                raise ValueError("导师审核通过后才能进行学院审核")

            if approved:
                request_obj.status = BudgetChangeRequest.RequestStatus.LEVEL2_APPROVED
            else:
                request_obj.status = BudgetChangeRequest.RequestStatus.LEVEL2_REJECTED

            request_obj.level2_comment = comment
            request_obj.level2_reviewed_by = reviewer
            request_obj.level2_reviewed_at = timezone.now()

        elif level == "level1":
            if request_obj.status != BudgetChangeRequest.RequestStatus.LEVEL2_APPROVED:
                raise ValueError("学院审核通过后才能进行校级审核")

            if approved:
                request_obj.status = BudgetChangeRequest.RequestStatus.APPROVED
                # 更新项目预算
                request_obj.project.approved_budget = request_obj.new_budget
                request_obj.project.save(
                    update_fields=["approved_budget", "updated_at"]
                )
            else:
                request_obj.status = BudgetChangeRequest.RequestStatus.REJECTED

            request_obj.level1_comment = comment
            request_obj.level1_reviewed_by = reviewer
            request_obj.level1_reviewed_at = timezone.now()

        request_obj.save()

        # 发送通知
        NotificationService.notify_budget_change_reviewed(
            request_obj.project, request_obj, reviewer, level, approved, comment
        )

        return request_obj

    @staticmethod
    def calculate_budget_usage(project):
        """
        计算预算使用情况
        """
        total_budget = project.approved_budget or project.budget_amount or 0

        # 统计各状态的支出
        approved_amount = (
            ProjectExpenditure.objects.filter(
                project=project,
                is_deleted=False,
                status=ProjectExpenditure.ExpenditureStatus.APPROVED,
            ).aggregate(total=models.Sum("amount"))["total"]
            or 0
        )

        pending_amount = (
            ProjectExpenditure.objects.filter(
                project=project,
                is_deleted=False,
                status=ProjectExpenditure.ExpenditureStatus.PENDING,
            ).aggregate(total=models.Sum("amount"))["total"]
            or 0
        )

        remaining = total_budget - approved_amount - pending_amount
        usage_rate = (
            (approved_amount + pending_amount) / total_budget * 100
            if total_budget > 0
            else 0
        )

        return {
            "total_budget": float(total_budget),
            "approved_amount": float(approved_amount),
            "pending_amount": float(pending_amount),
            "remaining": float(remaining),
            "usage_rate": round(usage_rate, 2),
        }


from django.db import models
