"""
项目回收站视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import ProjectRecycleBin
from ...serializers import ProjectRecycleBinSerializer
from ...services import ProjectRecycleService


class ProjectRecycleBinViewSet(viewsets.ReadOnlyModelViewSet):
    """
    回收站视图（只读 + 恢复）
    """

    queryset = ProjectRecycleBin.objects.all()
    serializer_class = ProjectRecycleBinSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project", "resource_type", "is_restored"]
    ordering_fields = ["deleted_at"]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_student:
            return qs.filter(project__leader=user)
        if user.is_teacher:
            return qs.filter(project__advisors__user=user).distinct()
        if user.is_admin and not user.is_level1_admin:
            return qs.filter(project__leader__college=user.college)
        if user.is_level1_admin:
            return qs
        return qs.none()

    @action(methods=["post"], detail=True, url_path="restore")
    def restore(self, request, pk=None):
        item = self.get_object()
        ok, msg = ProjectRecycleService.restore_item(item, user=request.user)
        if not ok:
            return Response({"code": 400, "message": msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"code": 200, "message": msg})
