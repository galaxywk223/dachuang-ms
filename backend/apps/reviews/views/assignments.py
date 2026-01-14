"""
专家评审分配视图
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ExpertGroup, Review
from ..services import ReviewService


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
        user = request.user
        if not user.is_admin:
            return Response(
                {"message": "无权限分配评审任务"},
                status=status.HTTP_403_FORBIDDEN,
            )
        project_ids = request.data.get('project_ids', [])
        group_id = request.data.get('group_id')
        review_type = request.data.get('review_type', Review.ReviewType.APPLICATION)
        target_node_id = request.data.get("target_node_id")
        
        if not project_ids or not group_id:
            return Response(
                {"message": "Empty project_ids or group_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            group = ExpertGroup.objects.get(pk=group_id)
        except ExpertGroup.DoesNotExist:
            return Response({"message": "Expert group not found"}, status=status.HTTP_404_NOT_FOUND)

        if group.created_by_id != user.id:
            return Response(
                {"message": "只能使用自己创建的专家组分配评审任务"},
                status=status.HTTP_403_FORBIDDEN,
            )

        review_level = request.data.get("review_level")

        try:
            created = ReviewService.assign_project_to_group(
                project_ids=project_ids,
                group_id=group_id,
                review_type=review_type,
                review_level=review_level,
                creator=request.user,
                target_node_id=target_node_id,
            )
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "message": f"Successfully assigned {len(created)} review tasks.",
            "count": len(created)
        })
