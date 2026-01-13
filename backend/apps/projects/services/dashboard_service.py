"""
仪表板统计服务
"""

from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from ..models import Project, ProjectAchievement
from apps.reviews.models import Review
from apps.users.models import User


class DashboardService:
    """
    仪表板数据统计服务
    """

    @staticmethod
    def get_student_dashboard(user):
        """
        获取学生端仪表板数据
        """
        # 我的项目统计
        my_projects = Project.objects.filter(
            Q(leader=user) | Q(members__user=user), is_deleted=False
        ).distinct()

        project_stats = {
            "total": my_projects.count(),
            "draft": my_projects.filter(status=Project.ProjectStatus.DRAFT).count(),
            "in_progress": my_projects.filter(
                status__in=[
                    Project.ProjectStatus.IN_PROGRESS,
                    Project.ProjectStatus.TASK_BOOK_DRAFT,
                    Project.ProjectStatus.TASK_BOOK_SUBMITTED,
                    Project.ProjectStatus.MID_TERM_DRAFT,
                    Project.ProjectStatus.MID_TERM_SUBMITTED,
                ]
            ).count(),
            "completed": my_projects.filter(
                status__in=[
                    Project.ProjectStatus.COMPLETED,
                    Project.ProjectStatus.CLOSED,
                ]
            ).count(),
        }

        # 待办事项
        pending_tasks = []

        # 待提交申报
        draft_projects = my_projects.filter(status=Project.ProjectStatus.DRAFT)
        if draft_projects.exists():
            pending_tasks.append(
                {
                    "type": "submit_application",
                    "title": "待提交项目申报",
                    "count": draft_projects.count(),
                    "priority": "high",
                }
            )

        # 退回修改的项目
        returned_projects = my_projects.filter(
            status__in=[
                Project.ProjectStatus.APPLICATION_RETURNED,
                Project.ProjectStatus.TASK_BOOK_RETURNED,
                Project.ProjectStatus.MID_TERM_RETURNED,
                Project.ProjectStatus.CLOSURE_RETURNED,
            ]
        )
        if returned_projects.exists():
            pending_tasks.append(
                {
                    "type": "revise_project",
                    "title": "需要修改的项目",
                    "count": returned_projects.count(),
                    "priority": "urgent",
                }
            )

        # 待提交任务书
        task_book_pending = my_projects.filter(
            status__in=[
                Project.ProjectStatus.IN_PROGRESS,
                Project.ProjectStatus.TASK_BOOK_DRAFT,
            ],
            task_book_file="",
        )
        if task_book_pending.exists():
            pending_tasks.append(
                {
                    "type": "submit_task_book",
                    "title": "待提交任务书",
                    "count": task_book_pending.count(),
                    "priority": "high",
                }
            )

        # 待提交中期报告
        midterm_pending = my_projects.filter(
            status__in=[
                Project.ProjectStatus.TASK_BOOK_APPROVED,
                Project.ProjectStatus.MID_TERM_DRAFT,
            ]
        )
        if midterm_pending.exists():
            pending_tasks.append(
                {
                    "type": "submit_midterm",
                    "title": "待提交中期报告",
                    "count": midterm_pending.count(),
                    "priority": "medium",
                }
            )

        # 待提交结题报告
        closure_pending = my_projects.filter(
            status__in=[
                Project.ProjectStatus.READY_FOR_CLOSURE,
                Project.ProjectStatus.CLOSURE_DRAFT,
            ]
        )
        if closure_pending.exists():
            pending_tasks.append(
                {
                    "type": "submit_closure",
                    "title": "待提交结题报告",
                    "count": closure_pending.count(),
                    "priority": "high",
                }
            )

        # 最近动态（最近7天）
        recent_date = timezone.now() - timedelta(days=7)
        recent_activities = []

        # 项目状态更新
        recent_updates = my_projects.filter(updated_at__gte=recent_date).order_by(
            "-updated_at"
        )[:5]

        for project in recent_updates:
            recent_activities.append(
                {
                    "type": "project_update",
                    "project_id": project.id,
                    "project_name": project.title,
                    "status": project.get_status_display(),
                    "time": project.updated_at,
                }
            )

        return {
            "project_stats": project_stats,
            "pending_tasks": pending_tasks,
            "recent_activities": recent_activities,
        }

    @staticmethod
    def get_teacher_dashboard(user):
        """
        获取教师端仪表板数据
        """
        # 指导项目统计
        guided_projects = Project.objects.filter(
            advisors__user=user, is_deleted=False
        ).distinct()

        project_stats = {
            "total": guided_projects.count(),
            "in_progress": guided_projects.filter(
                status__in=[
                    Project.ProjectStatus.IN_PROGRESS,
                    Project.ProjectStatus.TASK_BOOK_DRAFT,
                    Project.ProjectStatus.TASK_BOOK_SUBMITTED,
                    Project.ProjectStatus.MID_TERM_DRAFT,
                    Project.ProjectStatus.MID_TERM_SUBMITTED,
                ]
            ).count(),
            "completed": guided_projects.filter(
                status__in=[
                    Project.ProjectStatus.COMPLETED,
                    Project.ProjectStatus.CLOSED,
                ]
            ).count(),
            "excellent": guided_projects.filter(
                status=Project.ProjectStatus.CLOSED, closure_rating="EXCELLENT"
            ).count(),
        }

        # 待审核任务
        pending_reviews = Review.objects.filter(
            project__in=guided_projects,
            review_level=Review.ReviewLevel.TEACHER,
            status=Review.ReviewStatus.PENDING,
        ).select_related("project")

        review_tasks = []
        for review in pending_reviews:
            review_tasks.append(
                {
                    "review_id": review.id,
                    "project_id": review.project.id,
                    "project_name": review.project.title,
                    "review_type": review.get_review_type_display(),
                    "submitted_at": review.created_at,
                }
            )

        return {
            "project_stats": project_stats,
            "pending_reviews": len(review_tasks),
            "review_tasks": review_tasks[:10],  # 只返回前10条
        }

    @staticmethod
    def get_level2_admin_dashboard(user):
        """
        获取学院管理员端仪表板数据
        """
        # 学院项目统计
        college_projects = Project.objects.filter(
            leader__college=user.college, is_deleted=False
        )

        project_stats = {
            "total": college_projects.count(),
            "draft": college_projects.filter(
                status=Project.ProjectStatus.DRAFT
            ).count(),
            "reviewing": college_projects.filter(
                status__in=[
                    Project.ProjectStatus.COLLEGE_AUDITING,
                    Project.ProjectStatus.TASK_BOOK_SUBMITTED,
                    Project.ProjectStatus.MID_TERM_REVIEWING,
                    Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
                ]
            ).count(),
            "in_progress": college_projects.filter(
                status__in=[
                    Project.ProjectStatus.IN_PROGRESS,
                    Project.ProjectStatus.MID_TERM_DRAFT,
                    Project.ProjectStatus.MID_TERM_SUBMITTED,
                ]
            ).count(),
            "completed": college_projects.filter(
                status__in=[
                    Project.ProjectStatus.COMPLETED,
                    Project.ProjectStatus.CLOSED,
                ]
            ).count(),
        }

        # 待审核项目
        pending_reviews = (
            Review.objects.filter(
                project__leader__college=user.college,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.PENDING,
            )
            .values("review_type")
            .annotate(count=Count("id"))
        )

        review_stats = {item["review_type"]: item["count"] for item in pending_reviews}

        # 经费使用统计
        budget_stats = college_projects.aggregate(
            total_budget=Sum("approved_budget"),
            total_expenditure=Sum("expenditures__amount"),
        )

        return {
            "project_stats": project_stats,
            "review_stats": review_stats,
            "budget_stats": {
                "total_budget": float(budget_stats["total_budget"] or 0),
                "total_expenditure": float(budget_stats["total_expenditure"] or 0),
            },
        }

    @staticmethod
    def get_level1_admin_dashboard(user):
        """
        获取校级管理员端仪表板数据
        """
        # 全校项目统计
        all_projects = Project.objects.filter(is_deleted=False)

        # 按状态统计
        status_stats = {}
        for status_choice in Project.ProjectStatus.choices:
            status_code = status_choice[0]
            status_label = status_choice[1]
            count = all_projects.filter(status=status_code).count()
            if count > 0:
                status_stats[status_code] = {"label": status_label, "count": count}

        # 按级别统计
        level_stats = all_projects.values("level__value", "level__label").annotate(
            count=Count("id")
        )

        # 按学院统计
        college_stats = (
            all_projects.values("leader__college")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # 待审核统计
        pending_reviews = (
            Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
            )
            .values("review_type")
            .annotate(count=Count("id"))
        )

        review_stats = {item["review_type"]: item["count"] for item in pending_reviews}

        # 经费统计
        budget_stats = all_projects.aggregate(
            total_budget=Sum("approved_budget"),
            total_expenditure=Sum("expenditures__amount"),
            avg_budget=Avg("approved_budget"),
        )

        # 成果统计
        achievement_stats = (
            ProjectAchievement.objects.filter(is_deleted=False)
            .values("achievement_type__value", "achievement_type__label")
            .annotate(count=Count("id"))
        )

        # 最近7天新增项目
        recent_date = timezone.now() - timedelta(days=7)
        recent_projects = all_projects.filter(created_at__gte=recent_date).count()

        return {
            "overview": {
                "total_projects": all_projects.count(),
                "recent_projects": recent_projects,
                "total_students": User.objects.filter(
                    role=User.UserRole.STUDENT, is_active=True
                ).count(),
                "total_teachers": User.objects.filter(
                    role=User.UserRole.TEACHER, is_active=True
                ).count(),
            },
            "status_stats": status_stats,
            "level_stats": list(level_stats),
            "college_stats": list(college_stats),
            "review_stats": review_stats,
            "budget_stats": {
                "total_budget": float(budget_stats["total_budget"] or 0),
                "total_expenditure": float(budget_stats["total_expenditure"] or 0),
                "avg_budget": float(budget_stats["avg_budget"] or 0),
            },
            "achievement_stats": list(achievement_stats),
        }

    @staticmethod
    def get_expert_dashboard(user):
        """
        获取专家端仪表板数据
        """
        # 待评审任务
        from apps.reviews.models import ExpertReviewTask

        pending_tasks = ExpertReviewTask.objects.filter(
            expert=user, status=ExpertReviewTask.TaskStatus.PENDING
        ).select_related("project", "expert_group")

        # 已完成评审
        completed_tasks = ExpertReviewTask.objects.filter(
            expert=user, status=ExpertReviewTask.TaskStatus.COMPLETED
        ).count()

        task_list = []
        for task in pending_tasks[:10]:
            task_list.append(
                {
                    "task_id": task.id,
                    "project_id": task.project.id,
                    "project_name": task.project.title,
                    "review_type": task.get_review_type_display(),
                    "group_name": task.expert_group.name if task.expert_group else "",
                    "assigned_at": task.assigned_at,
                }
            )

        return {
            "pending_count": pending_tasks.count(),
            "completed_count": completed_tasks,
            "pending_tasks": task_list,
        }
