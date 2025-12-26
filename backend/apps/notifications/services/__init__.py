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
    def notify_project_submitted(project):
        """
        通知：项目已提交
        """
        # 通知项目负责人
        NotificationService.create_notification(
            recipient=project.leader,
            title="项目提交成功",
            content=f"您的项目《{project.title}》已成功提交，等待审核。",
            notification_type=Notification.NotificationType.PROJECT,
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
    def get_unread_count(user):
        """
        获取用户未读通知数量
        """
        return Notification.objects.filter(recipient=user, is_read=False).count()
