"""
通知业务逻辑层
"""

from ..models import Notification


class NotificationService:
    """
    通知服务类
    """

    @staticmethod
    def create_notification(
        recipient,
        title,
        content,
        notification_type=Notification.NotificationType.SYSTEM,
        related_project=None,
    ):
        """
        创建通知
        """
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            content=content,
            notification_type=notification_type,
            related_project=related_project,
        )

    @staticmethod
    def _notify_users(users, title, content, notification_type, related_project=None):
        unique = {}
        for user in users:
            if user and user.id not in unique:
                unique[user.id] = user
        for user in unique.values():
            NotificationService.create_notification(
                recipient=user,
                title=title,
                content=content,
                notification_type=notification_type,
                related_project=related_project,
            )

    @staticmethod
    def notify_project_submitted(project):
        """
        通知：项目已提交
        """
        NotificationService._notify_users(
            [project.leader],
            title="项目提交成功",
            content=f"您的项目《{project.title}》已成功提交，等待审核。",
            notification_type=Notification.NotificationType.PROJECT,
            related_project=project,
        )
        advisors = [advisor.user for advisor in project.advisors.select_related("user")]
        NotificationService._notify_users(
            advisors,
            title="新的项目待审核",
            content=f"项目《{project.title}》已提交，请及时处理审核。",
            notification_type=Notification.NotificationType.REVIEW,
            related_project=project,
        )

    @staticmethod
    def notify_midterm_submitted(project):
        """
        通知：中期报告已提交
        """
        NotificationService._notify_users(
            [project.leader],
            title="中期报告提交成功",
            content=f"项目《{project.title}》中期报告已提交，等待审核。",
            notification_type=Notification.NotificationType.PROJECT,
            related_project=project,
        )
        advisors = [advisor.user for advisor in project.advisors.select_related("user")]
        NotificationService._notify_users(
            advisors,
            title="中期报告待审核",
            content=f"项目《{project.title}》中期报告已提交，请及时审核。",
            notification_type=Notification.NotificationType.REVIEW,
            related_project=project,
        )

    @staticmethod
    def notify_closure_submitted(project):
        """
        通知：结题报告已提交
        """
        NotificationService._notify_users(
            [project.leader],
            title="结题申请提交成功",
            content=f"项目《{project.title}》结题申请已提交，等待审核。",
            notification_type=Notification.NotificationType.PROJECT,
            related_project=project,
        )
        advisors = [advisor.user for advisor in project.advisors.select_related("user")]
        NotificationService._notify_users(
            advisors,
            title="结题申请待审核",
            content=f"项目《{project.title}》结题申请已提交，请及时审核。",
            notification_type=Notification.NotificationType.REVIEW,
            related_project=project,
        )

    @staticmethod
    def notify_review_assigned(review):
        """
        通知：评审任务分配
        """
        if not review or not review.reviewer:
            return
        project = review.project
        NotificationService.create_notification(
            recipient=review.reviewer,
            title="新的评审任务",
            content=f"项目《{project.title}》已分配给您评审，请及时处理。",
            notification_type=Notification.NotificationType.REVIEW,
            related_project=project,
        )

    @staticmethod
    def notify_review_result(project, approved, comments=""):
        """
        通知：审核结果
        """
        if approved:
            title = "项目审核通过"
            content = f"恭喜！您的项目《{project.title}》审核通过。"
        else:
            title = "项目审核未通过"
            content = f"很抱歉，您的项目《{project.title}》审核未通过。"

        if comments:
            content += f"\n审核意见：{comments}"

        NotificationService.create_notification(
            recipient=project.leader,
            title=title,
            content=content,
            notification_type=Notification.NotificationType.REVIEW,
            related_project=project,
        )

    @staticmethod
    def notify_establishment_published(project):
        """
        通知：立项结果已发布
        """
        level = project.final_level or project.level
        budget = project.final_budget or project.approved_budget
        details = []
        if project.project_no:
            details.append(f"项目编号：{project.project_no}")
        if level:
            details.append(f"立项级别：{level.label}")
        if budget is not None:
            details.append(f"批准经费：{budget}元")
        detail_text = "\n".join(details)
        content = f"您的项目《{project.title}》立项结果已发布。"
        if detail_text:
            content = f"{content}\n{detail_text}"

        users = [project.leader]
        users.extend([advisor.user for advisor in project.advisors.select_related("user")])
        users.extend(list(project.members.all()))
        NotificationService._notify_users(
            users,
            title="立项结果已发布",
            content=content,
            notification_type=Notification.NotificationType.PROJECT,
            related_project=project,
        )

    @staticmethod
    def notify_expenditure_submitted(project, expenditure, created_by):
        """
        通知：经费支出已提交
        """
        users = [project.leader]
        users.extend([advisor.user for advisor in project.advisors.select_related("user")])
        NotificationService._notify_users(
            users,
            title="经费支出待审核",
            content=(
                f"项目《{project.title}》提交了经费支出"
                f"《{expenditure.title}》，金额：{expenditure.amount}元。"
            ),
            notification_type=Notification.NotificationType.PROJECT,
            related_project=project,
        )
        if created_by and created_by.id != project.leader_id:
            NotificationService.create_notification(
                recipient=created_by,
                title="经费支出提交成功",
                content=f"经费支出《{expenditure.title}》已提交，等待审核。",
                notification_type=Notification.NotificationType.PROJECT,
                related_project=project,
            )

    @staticmethod
    def notify_expenditure_reviewed(project, expenditure, reviewer, approved, comment=""):
        """
        通知：经费支出审核结果
        """
        result = "通过" if approved else "驳回"
        content = (
            f"项目《{project.title}》的经费支出《{expenditure.title}》"
            f"审核{result}。"
        )
        if comment:
            content = f"{content}\n审核意见：{comment}"
        NotificationService._notify_users(
            [project.leader, expenditure.created_by],
            title=f"经费支出审核{result}",
            content=content,
            notification_type=Notification.NotificationType.REVIEW,
            related_project=project,
        )
        if reviewer:
            NotificationService.create_notification(
                recipient=reviewer,
                title="经费支出审核已处理",
                content=f"经费支出《{expenditure.title}》审核已处理。",
                notification_type=Notification.NotificationType.REVIEW,
                related_project=project,
            )

    @staticmethod
    def get_unread_count(user):
        """
        获取用户未读通知数量
        """
        return Notification.objects.filter(recipient=user, is_read=False).count()
