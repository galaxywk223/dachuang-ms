"""
项目审核相关视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from ...serializers import ProjectSerializer
from apps.system_settings.services import SystemSettingService
from django.utils import timezone


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
        user = request.user
        if not (user.is_level1_admin or user.is_level2_admin):
            return Response(
                {"code": 403, "message": "只有管理员可以查看待审核列表"},
                status=status.HTTP_403_FORBIDDEN,
            )

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        search = request.query_params.get("search", "")
        review_type = request.query_params.get(
            "type", "establishment"
        )  # establishment, midterm, closure

        if review_type == "closure":
            return Response(
                {"code": 400, "message": "结题流程需先分配校级专家评审，管理员不能直接审核（请到专家评审分配/校级结题审核页操作）"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review_type_map = {
            "establishment": Review.ReviewType.APPLICATION,
            "closure": Review.ReviewType.CLOSURE,
        }

        review_type_value = review_type_map.get(
            review_type, Review.ReviewType.APPLICATION
        )

        # 查询当前管理员可见的待审核记录
        queryset = (
            ReviewService.get_pending_reviews_for_admin(user)
            .filter(review_type=review_type_value)
            .select_related("project")
            .order_by("-created_at")
        )

        if search:
            queryset = queryset.filter(project__title__icontains=search)

        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        reviews = queryset[start:end]

        # 返回项目详情并附带审核信息，便于前端展示
        projects_data = []
        for review in reviews:
            project_data = ProjectSerializer(review.project).data
            project_data.update(
                {
                    "review_id": review.id,
                    "review_level": review.review_level,
                    "review_level_display": review.get_review_level_display(),
                    "review_type": review.review_type,
                    "review_type_display": review.get_review_type_display(),
                }
            )
            projects_data.append(project_data)

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "results": projects_data,
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
        review = self._get_pending_review_for_user(request.user, pk)
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )

        ok, msg = SystemSettingService.check_review_window(
            review.review_type,
            review.review_level,
            timezone.now().date(),
            batch=review.project.batch,
        )
        if not ok:
            return Response(
                {"code": 400, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if review.review_type == Review.ReviewType.CLOSURE:
            return Response(
                {"code": 400, "message": "结题流程需先分配专家评审，管理员不能直接审核"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = request.data.get("comment", "")
        score = request.data.get("score")
        closure_rating = request.data.get("closure_rating")
        approved_budget = request.data.get("approved_budget")

        if (
            review.review_type == Review.ReviewType.APPLICATION
            and review.review_level == Review.ReviewLevel.LEVEL1
        ):
            if approved_budget in (None, ""):
                return Response(
                    {"code": 400, "message": "请填写批准经费"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                from decimal import Decimal

                approved_budget = Decimal(str(approved_budget))
            except Exception:
                return Response(
                    {"code": 400, "message": "批准经费格式不正确"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if approved_budget < 0:
                return Response(
                    {"code": 400, "message": "批准经费不能为负数"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            review.project.approved_budget = approved_budget
            review.project.save(update_fields=["approved_budget", "updated_at"])

        ReviewService.approve_review(review, request.user, comment, score, closure_rating)

        return Response(
            {
                "code": 200,
                "message": "审核通过",
                "data": ProjectSerializer(review.project).data,
            }
        )

    @action(methods=["post"], detail=True, url_path="reject")
    def reject_project(self, request, pk=None):
        """
        驳回项目
        """
        review = self._get_pending_review_for_user(request.user, pk)
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )

        ok, msg = SystemSettingService.check_review_window(
            review.review_type,
            review.review_level,
            timezone.now().date(),
            batch=review.project.batch,
        )
        if not ok:
            return Response(
                {"code": 400, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = request.data.get("comment", "")
        reject_to = request.data.get("reject_to")
        if review.review_type == Review.ReviewType.CLOSURE:
            return Response(
                {"code": 400, "message": "结题流程需先分配专家评审，管理员不能直接审核"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not comment:
            return Response(
                {"code": 400, "message": "请填写驳回原因"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ReviewService.reject_review(review, request.user, comment, reject_to)

        return Response(
            {
                "code": 200,
                "message": "已驳回",
                "data": ProjectSerializer(review.project).data,
            }
        )

    def _get_pending_review_for_user(self, user, project_id):
        """
        根据当前管理员角色获取指定项目的待审核记录
        """
        queryset = ReviewService.get_pending_reviews_for_admin(user).filter(
            project_id=project_id
        )
        return queryset.select_related("project").first()
