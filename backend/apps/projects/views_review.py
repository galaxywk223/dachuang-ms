"""
项目审核相关视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Project
from .serializers import ProjectSerializer


class ProjectReviewViewSet(viewsets.ViewSet):
    """
    项目审核视图集
    """

    permission_classes = [IsAuthenticated]

    @action(methods=["get"], detail=False, url_path="pending")
    def get_pending_reviews(self, request):
        """
        获取待审核项目列表
        """
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        search = request.query_params.get("search", "")
        review_type = request.query_params.get(
            "type", "establishment"
        )  # establishment, midterm, closure

        # 根据审核类型确定项目状态
        status_map = {
            "establishment": ["SUBMITTED"],
            "midterm": ["MIDTERM_SUBMITTED"],
            "closure": ["CLOSURE_SUBMITTED"],
        }

        project_status = status_map.get(review_type, ["SUBMITTED"])

        # 查询待审核项目
        queryset = Project.objects.filter(status__in=project_status)

        if search:
            queryset = queryset.filter(title__icontains=search)

        queryset = queryset.order_by("-created_at")

        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = queryset[start:end]

        serializer = ProjectSerializer(projects, many=True)

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "results": serializer.data,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }
        )

    @action(methods=["post"], detail=True, url_path="approve")
    def approve_project(self, request, pk=None):
        """
        审核通过项目
        """
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {"code": 404, "message": "项目不存在"}, status=status.HTTP_404_NOT_FOUND
            )

        comment = request.data.get("comment", "")

        with transaction.atomic():
            # 更新项目状态
            if project.status == "SUBMITTED":
                project.status = "APPROVED"
                next_status = "IN_PROGRESS"
            elif project.status == "MIDTERM_SUBMITTED":
                project.status = "MIDTERM_APPROVED"
                next_status = "IN_PROGRESS"
            elif project.status == "CLOSURE_SUBMITTED":
                project.status = "CLOSURE_APPROVED"
                next_status = "COMPLETED"
            else:
                return Response(
                    {"code": 400, "message": "项目状态不正确"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project.save()

            # 创建审核记录
            # TODO: 创建 Review 模型后取消注释
            # Review.objects.create(
            #     project=project,
            #     reviewer=request.user,
            #     review_type="ESTABLISHMENT"
            #     if project.status == "APPROVED"
            #     else "MIDTERM"
            #     if project.status == "MIDTERM_APPROVED"
            #     else "CLOSURE",
            #     result="APPROVED",
            #     comment=comment,
            # )

            # 更新到下一个状态
            project.status = next_status
            project.save()

        return Response({"code": 200, "message": "审核通过"})

    @action(methods=["post"], detail=True, url_path="reject")
    def reject_project(self, request, pk=None):
        """
        驳回项目
        """
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {"code": 404, "message": "项目不存在"}, status=status.HTTP_404_NOT_FOUND
            )

        comment = request.data.get("comment", "")

        if not comment:
            return Response(
                {"code": 400, "message": "请填写驳回原因"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # 更新项目状态
            if project.status == "SUBMITTED":
                project.status = "REJECTED"
                review_type = "ESTABLISHMENT"
            elif project.status == "MIDTERM_SUBMITTED":
                project.status = "MIDTERM_REJECTED"
                review_type = "MIDTERM"
            elif project.status == "CLOSURE_SUBMITTED":
                project.status = "CLOSURE_REJECTED"
                review_type = "CLOSURE"
            else:
                return Response(
                    {"code": 400, "message": "项目状态不正确"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project.save()

            # 创建审核记录
            # TODO: 创建 Review 模型后取消注释
            # Review.objects.create(
            #     project=project,
            #     reviewer=request.user,
            #     review_type=review_type,
            #     result="REJECTED",
            #     comment=comment,
            # )

        return Response({"code": 200, "message": "已驳回"})
