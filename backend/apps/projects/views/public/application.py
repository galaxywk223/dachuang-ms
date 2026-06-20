"""
项目申报相关视图（ViewSet）。

保留原有 URL 结构：
- POST   /projects/application/create/
- PUT    /projects/application/{id}/update/
- POST   /projects/application/{id}/withdraw/
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...services.application_service import ProjectApplicationService


class ProjectApplicationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create")
    def create_application(self, request):
        payload, status_code = ProjectApplicationService.create_application(request)
        return Response(payload, status=status_code)

    @action(detail=True, methods=["put"], url_path="update")
    def update_application(self, request, pk=None):
        payload, status_code = ProjectApplicationService.update_application(request, pk)
        return Response(payload, status=status_code)

    @action(detail=True, methods=["post"], url_path="withdraw")
    def withdraw(self, request, pk=None):
        payload, status_code = ProjectApplicationService.withdraw_application(request, pk)
        return Response(payload, status=status_code)
