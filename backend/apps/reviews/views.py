"""
审核视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Review, ExpertGroup
from .serializers import ReviewSerializer, ReviewActionSerializer
from .serializers_expert import ExpertGroupSerializer
from .services import ReviewService
from apps.projects.models import Project


class ReviewViewSet(viewsets.ModelViewSet):
    """
    审核管理视图集
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "review_type", "review_level", "project"]
    search_fields = ["project__project_no", "project__title"]
    ordering_fields = ["created_at", "reviewed_at"]

    def get_queryset(self):
        """
        根据用户角色过滤审核记录
        """
        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己项目的审核记录
        if user.is_student:
            queryset = queryset.filter(project__leader=user)
        # 二级管理员只能看到本学院的审核记录
        elif user.is_level2_admin:
            queryset = queryset.filter(
                project__leader__college=user.college,
                review_level=Review.ReviewLevel.LEVEL2,
            )
        # 一级管理员可以看到所有一级审核记录
        elif user.is_level1_admin:
            queryset = queryset.filter(review_level=Review.ReviewLevel.LEVEL1)

        return queryset

    @action(methods=["post"], detail=True)
    def review(self, request, pk=None):
        """
        执行审核操作
        """
        review = self.get_object()
        user = request.user

        # 检查审核权限
        if not self.check_review_permission(review, user):
            return Response(
                {"code": 403, "message": "无权限审核此项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查审核状态
        if review.status != Review.ReviewStatus.PENDING:
            return Response(
                {"code": 400, "message": "该审核记录已处理"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证请求数据
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")
        score = serializer.validated_data.get("score")

        # 执行审核
        closure_rating = serializer.validated_data.get("closure_rating")

        if action_type == "approve":
            result = ReviewService.approve_review(
                review, user, comments, score, closure_rating
            )
        else:
            result = ReviewService.reject_review(review, user, comments)

        if result:
            return Response(
                {
                    "code": 200,
                    "message": "审核成功",
                    "data": ReviewSerializer(review).data,
                }
            )
        else:
            return Response(
                {"code": 500, "message": "审核失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["get"], detail=False)
    def pending(self, request):
        """
        获取待审核列表
        """
        user = request.user

        if user.is_level2_admin:
            # 二级管理员获取本学院待审核的项目
            queryset = Review.objects.filter(
                project__leader__college=user.college,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.PENDING,
            )
        elif user.is_level1_admin:
            # 一级管理员获取待一级审核的项目
            queryset = Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
            )
        else:
            return Response(
                {"code": 403, "message": "无权限访问"}, status=status.HTTP_403_FORBIDDEN
            )

        # 应用过滤和排序
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "data": serializer.data})

    def check_review_permission(self, review, user):
        """
        检查用户是否有权限审核
        """
        if review.review_level == Review.ReviewLevel.LEVEL2:
            # 二级审核：必须是二级管理员且是同一学院
            project_college = (
                review.project.leader.college if review.project and review.project.leader else None
            )
            return user.is_level2_admin and user.college == project_college
        elif review.review_level == Review.ReviewLevel.LEVEL1:
            # 一级审核：必须是一级管理员
            return user.is_level1_admin
        return False

    @action(methods=["post"], detail=False, url_path="submit-to-level1")
    def submit_to_level1(self, request):
        """
        二级管理员提交项目到一级审核
        """
        user = request.user
        if not user.is_level2_admin:
            return Response(
                {"code": 403, "message": "只有二级管理员可以提交到一级审核"},
                status=status.HTTP_403_FORBIDDEN,
            )

        project_id = request.data.get("project_id")
        if not project_id:
            return Response(
                {"code": 400, "message": "请提供项目ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(id=project_id, leader__college=user.college)

            # 检查二级审核是否已通过
            from .models import Review
            level2_passed = Review.objects.filter(
                project=project,
                review_type=Review.ReviewType.APPLICATION,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.APPROVED,
            ).exists()
            if not level2_passed:
                return Response(
                    {"code": 400, "message": "项目必须先通过二级审核"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 创建一级审核记录
            review = ReviewService.create_level1_review(project)

            # 更新项目状态
            project.status = Project.ProjectStatus.SUBMITTED
            project.save(update_fields=["status"])

            return Response(
                {
                    "code": 200,
                    "message": "已提交至一级管理员审核",
                    "data": ReviewSerializer(review).data,
                }
            )
        except Project.DoesNotExist:
            return Response(
                {"code": 404, "message": "项目不存在"}, status=status.HTTP_404_NOT_FOUND
            )


class ExpertGroupViewSet(viewsets.ModelViewSet):
    """
    专家组管理视图集
    """
    queryset = ExpertGroup.objects.all()
    serializer_class = ExpertGroupSerializer
    permission_classes = [IsAuthenticated] # Typically admin only, but for now authenticated

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReviewAssignmentViewSet(viewsets.ViewSet):
    """
    专家评审分配视图
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def assign_batch(self, request):
        """
        批量分配项目给专家组
        DATA: {
            "project_ids": [1, 2, 3],
            "group_id": 1,
            "review_type": "APPLICATION" (optional)
        }
        """
        project_ids = request.data.get('project_ids', [])
        group_id = request.data.get('group_id')
        review_type = request.data.get('review_type', Review.ReviewType.APPLICATION)
        
        if not project_ids or not group_id:
             return Response({"message": "Empty project_ids or group_id"}, status=status.HTTP_400_BAD_REQUEST)

        created = ReviewService.assign_project_to_group(
            project_ids=project_ids,
            group_id=group_id,
            review_type=review_type,
            creator=request.user
        )
        
        return Response({
            "message": f"Successfully assigned {len(created)} review tasks.",
            "count": len(created)
        })

