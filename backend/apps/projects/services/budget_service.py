"""
经费管理服务
"""

from django.db import transaction
from django.db import models
from django.utils import timezone
from ..models import Project, ProjectExpenditure
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
