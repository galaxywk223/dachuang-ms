"""
批量操作服务
"""

from django.db import transaction
from django.utils import timezone
from ..models import Project
from apps.reviews.models import Review
from apps.notifications.services import NotificationService


class BatchOperationService:
    """
    批量操作服务类
    """

    @staticmethod
    @transaction.atomic
    def batch_approve_projects(
        project_ids, reviewer, review_type, review_level, comment=""
    ):
        """
        批量审核通过项目
        :param project_ids: 项目ID列表
        :param reviewer: 审核人
        :param review_type: 审核类型 (APPLICATION, TASK_BOOK, MID_TERM, CLOSURE)
        :param review_level: 审核级别 (TEACHER, LEVEL2, LEVEL1)
        :param comment: 审核意见
        :return: 成功和失败的统计
        """
        success_count = 0
        failed_count = 0
        failed_reasons = []

        for project_id in project_ids:
            try:
                project = Project.objects.select_for_update().get(
                    id=project_id, is_deleted=False
                )

                # 查找对应的审核记录
                review = Review.objects.filter(
                    project=project,
                    review_type=review_type,
                    review_level=review_level,
                    status=Review.ReviewStatus.PENDING,
                ).first()

                if not review:
                    failed_count += 1
                    failed_reasons.append(f"项目 {project.title}: 未找到待审核记录")
                    continue

                # 更新审核记录
                review.status = Review.ReviewStatus.APPROVED
                review.comment = comment
                review.reviewed_by = reviewer
                review.reviewed_at = timezone.now()
                review.save()

                # 更新项目状态（根据审核类型和级别）
                _update_project_status_on_approve(project, review_type, review_level)

                success_count += 1

                # 发送通知
                NotificationService.notify_review_result(
                    project, review_type, review_level, True, comment, reviewer
                )

            except Project.DoesNotExist:
                failed_count += 1
                failed_reasons.append(f"项目ID {project_id}: 项目不存在")
            except Exception as e:
                failed_count += 1
                failed_reasons.append(f"项目ID {project_id}: {str(e)}")

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_reasons": failed_reasons,
        }

    @staticmethod
    @transaction.atomic
    def batch_reject_projects(
        project_ids, reviewer, review_type, review_level, comment=""
    ):
        """
        批量审核拒绝项目
        """
        success_count = 0
        failed_count = 0
        failed_reasons = []

        for project_id in project_ids:
            try:
                project = Project.objects.select_for_update().get(
                    id=project_id, is_deleted=False
                )

                review = Review.objects.filter(
                    project=project,
                    review_type=review_type,
                    review_level=review_level,
                    status=Review.ReviewStatus.PENDING,
                ).first()

                if not review:
                    failed_count += 1
                    failed_reasons.append(f"项目 {project.title}: 未找到待审核记录")
                    continue

                review.status = Review.ReviewStatus.REJECTED
                review.comment = comment
                review.reviewed_by = reviewer
                review.reviewed_at = timezone.now()
                review.save()

                # 更新项目状态为退回
                _update_project_status_on_reject(project, review_type, review_level)

                success_count += 1

                # 发送通知
                NotificationService.notify_review_result(
                    project, review_type, review_level, False, comment, reviewer
                )

            except Project.DoesNotExist:
                failed_count += 1
                failed_reasons.append(f"项目ID {project_id}: 项目不存在")
            except Exception as e:
                failed_count += 1
                failed_reasons.append(f"项目ID {project_id}: {str(e)}")

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_reasons": failed_reasons,
        }

    @staticmethod
    @transaction.atomic
    def batch_update_project_status(project_ids, new_status, operator):
        """
        批量更新项目状态
        """
        success_count = 0
        failed_count = 0
        failed_reasons = []

        for project_id in project_ids:
            try:
                project = Project.objects.select_for_update().get(
                    id=project_id, is_deleted=False
                )

                # 验证状态转换是否合法
                if not _is_valid_status_transition(project.status, new_status):
                    failed_count += 1
                    failed_reasons.append(
                        f"项目 {project.title}: 状态转换不合法 ({project.get_status_display()} -> {new_status})"
                    )
                    continue

                project.status = new_status
                project.save()

                success_count += 1

                # 记录操作日志（可选）
                # OperationLog.objects.create(...)

            except Project.DoesNotExist:
                failed_count += 1
                failed_reasons.append(f"项目ID {project_id}: 项目不存在")
            except Exception as e:
                failed_count += 1
                failed_reasons.append(f"项目ID {project_id}: {str(e)}")

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_reasons": failed_reasons,
        }

    @staticmethod
    @transaction.atomic
    def batch_send_notifications(user_ids, title, content, notification_type="SYSTEM"):
        """
        批量发送通知
        """
        from apps.notifications.models import Notification
        from apps.users.models import User

        success_count = 0
        failed_count = 0

        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id, is_active=True)

                Notification.objects.create(
                    user=user,
                    title=title,
                    content=content,
                    notification_type=notification_type,
                    is_read=False,
                )

                success_count += 1

            except User.DoesNotExist:
                failed_count += 1
            except Exception:
                failed_count += 1

        return {"success_count": success_count, "failed_count": failed_count}

    @staticmethod
    def batch_export_documents(project_ids, document_type):
        """
        批量导出文档
        :param project_ids: 项目ID列表
        :param document_type: 文档类型 (application, contract, task_book, midterm, closure)
        :return: 文件路径列表或压缩包路径
        """
        import os
        import zipfile
        from django.conf import settings
        from ..services.document import ProjectDocumentService

        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp", "batch_export")
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        zip_filename = f"batch_{document_type}_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for project_id in project_ids:
                try:
                    project = Project.objects.get(id=project_id, is_deleted=False)

                    # 根据文档类型生成相应文档
                    if document_type == "application":
                        doc_path = ProjectDocumentService.generate_application_doc(
                            project
                        )
                    elif document_type == "contract":
                        doc_path = ProjectDocumentService.generate_contract_doc(project)
                    elif document_type == "task_book":
                        doc_path = ProjectDocumentService.generate_task_book_doc(
                            project
                        )
                    elif document_type == "midterm":
                        doc_path = ProjectDocumentService.generate_midterm_doc(project)
                    elif document_type == "closure":
                        doc_path = ProjectDocumentService.generate_closure_doc(project)
                    else:
                        continue

                    if doc_path and os.path.exists(doc_path):
                        # 添加到压缩包，使用项目编号作为文件名
                        filename = f"{project.project_no}_{document_type}.docx"
                        zipf.write(doc_path, filename)

                except Exception as e:
                    # 记录错误但继续处理其他项目
                    print(f"Error processing project {project_id}: {str(e)}")
                    continue

        return zip_path


def _update_project_status_on_approve(project, review_type, review_level):
    """
    审核通过后更新项目状态
    """
    if review_type == Review.ReviewType.APPLICATION:
        if review_level == Review.ReviewLevel.TEACHER:
            project.status = Project.ProjectStatus.TEACHER_APPROVED
        elif review_level == Review.ReviewLevel.LEVEL2:
            project.status = Project.ProjectStatus.COLLEGE_AUDITING
        elif review_level == Review.ReviewLevel.LEVEL1:
            project.status = Project.ProjectStatus.IN_PROGRESS

    elif review_type == Review.ReviewType.TASK_BOOK:
        if review_level == Review.ReviewLevel.TEACHER:
            project.status = Project.ProjectStatus.TASK_BOOK_APPROVED
        elif review_level == Review.ReviewLevel.LEVEL2:
            project.status = Project.ProjectStatus.IN_PROGRESS

    elif review_type == Review.ReviewType.MID_TERM:
        if review_level == Review.ReviewLevel.TEACHER:
            project.status = Project.ProjectStatus.MID_TERM_APPROVED
        elif review_level == Review.ReviewLevel.LEVEL2:
            project.status = Project.ProjectStatus.READY_FOR_CLOSURE

    elif review_type == Review.ReviewType.CLOSURE:
        if review_level == Review.ReviewLevel.TEACHER:
            project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
        elif review_level == Review.ReviewLevel.LEVEL2:
            project.status = Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED
        elif review_level == Review.ReviewLevel.LEVEL1:
            project.status = Project.ProjectStatus.CLOSED

    project.save()


def _update_project_status_on_reject(project, review_type, review_level):
    """
    审核拒绝后更新项目状态
    """
    if review_type == Review.ReviewType.APPLICATION:
        project.status = Project.ProjectStatus.APPLICATION_RETURNED
    elif review_type == Review.ReviewType.TASK_BOOK:
        project.status = Project.ProjectStatus.TASK_BOOK_RETURNED
    elif review_type == Review.ReviewType.MID_TERM:
        project.status = Project.ProjectStatus.MID_TERM_RETURNED
    elif review_type == Review.ReviewType.CLOSURE:
        project.status = Project.ProjectStatus.CLOSURE_RETURNED

    project.save()


def _is_valid_status_transition(from_status, to_status):
    """
    检查状态转换是否合法
    """
    # 任意状态转换都允许（根据实际业务需求调整）
    return True
