"""
项目进度视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ProjectProgress
from .serializers import ProjectProgressSerializer

class ProjectProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    项目进度视图集（只读）
    """

    queryset = ProjectProgress.objects.all()
    serializer_class = ProjectProgressSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project"]
    ordering_fields = ["created_at"]
