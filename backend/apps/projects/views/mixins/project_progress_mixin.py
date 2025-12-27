"""
Project progress actions.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import ProjectMember, ProjectRecycleBin
from ...serializers import ProjectProgressSerializer
from ...services import ProjectRecycleService


class ProjectProgressMixin:
    @action(methods=["get"], detail=True)
    def progress(self, request, pk=None):
        """
        获取项目进度列表
        """
        project = self.get_object()
        progress_list = project.progress_records.all()
        serializer = ProjectProgressSerializer(progress_list, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(methods=["post"], detail=True, url_path="add-progress")
    def add_progress(self, request, pk=None):
        """
        添加项目进度
        """
        project = self.get_object()

        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
            return Response(
                {"code": 403, "message": "只有项目成员可以添加进度"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, created_by=request.user)

        return Response({"code": 200, "message": "进度添加成功", "data": serializer.data})

    @action(methods=["delete"], detail=True, url_path="remove-progress/(?P<progress_id>[^/.]+)")
    def remove_progress(self, request, pk=None, progress_id=None):
        """
        删除项目进度（进入回收站）
        """
        project = self.get_object()

        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
            return Response(
                {"code": 403, "message": "只有项目成员可以删除进度"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            progress = project.progress_records.get(id=progress_id)
        except Exception:
            return Response(
                {"code": 404, "message": "进度不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {
            "title": progress.title,
            "content": progress.content,
            "attachment": progress.attachment.name if progress.attachment else "",
            "created_by": progress.created_by_id,
        }
        ProjectRecycleService.add_item(
            project=project,
            resource_type=ProjectRecycleBin.ResourceType.PROGRESS,
            resource_id=progress.id,
            payload=payload,
            attachments=[payload.get("attachment")] if payload.get("attachment") else [],
            deleted_by=request.user,
        )
        progress.delete()
        return Response({"code": 200, "message": "已移入回收站"})
