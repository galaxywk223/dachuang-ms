"""
审核统计相关视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import ProjectChangeRequest
from apps.reviews.models import Review
from apps.reviews.services import ReviewService


class ReviewStatisticsViewSet(viewsets.ViewSet):
    """
    审核统计视图集
    """

    permission_classes = [IsAuthenticated]

    @action(methods=["get"], detail=False, url_path="pending-counts")
    def pending_counts(self, request):
        """
        获取各类审核的待审核数量
        """
        user = request.user

        # 验证用户是管理员
        if not user.is_admin:
            return Response(
                {"code": 403, "message": "无权限访问"},
                status=status.HTTP_403_FORBIDDEN,
            )

        result = {
            "establishment": 0,  # 立项审核
            "midterm": 0,  # 中期审核（仅level2）
            "closure": 0,  # 结题审核
            "change": 0,  # 异动审核
        }

        pending_reviews = ReviewService.get_pending_reviews_for_admin(user)
        result["establishment"] = pending_reviews.filter(
            review_type=Review.ReviewType.APPLICATION
        ).count()
        result["midterm"] = pending_reviews.filter(
            review_type=Review.ReviewType.MID_TERM
        ).count()
        result["closure"] = pending_reviews.filter(
            review_type=Review.ReviewType.CLOSURE
        ).count()

        # 异动审核待审数量
        if user.is_level1_admin:
            change_status = "LEVEL1_REVIEWING"
        else:  # non-level1 admin
            change_status = "LEVEL2_REVIEWING"

        change_queryset = ProjectChangeRequest.objects.filter(status=change_status)
        if user.is_college_admin and user.college:
            change_queryset = change_queryset.filter(
                project__leader__college=user.college
            )
        result["change"] = change_queryset.count()

        return Response({"code": 200, "message": "获取成功", "data": result})
