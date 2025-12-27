"""
项目结题相关视图（ViewSet）。

保留原有 URL 结构：
- GET    /projects/closure/pending/
- GET    /projects/closure/applied/
- GET    /projects/closure/drafts/
- POST   /projects/closure/{id}/create/
- PUT    /projects/closure/{id}/update/
- DELETE /projects/closure/{id}/delete/
- GET    /projects/closure/{id}/achievements/
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...services.closure_service import ProjectClosureService


class ProjectClosureViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        payload, status_code = ProjectClosureService.pending(request)
        return Response(payload, status=status_code)

    @action(detail=False, methods=["get"], url_path="applied")
    def applied(self, request):
        payload, status_code = ProjectClosureService.applied(request)
        return Response(payload, status=status_code)

    @action(detail=False, methods=["get"], url_path="drafts")
    def drafts(self, request):
        payload, status_code = ProjectClosureService.drafts(request)
        return Response(payload, status=status_code)

    @action(detail=True, methods=["post"], url_path="create")
    def create_application(self, request, pk=None):
        payload, status_code = ProjectClosureService.create_application(request, pk)
        return Response(payload, status=status_code)

    @action(detail=True, methods=["put"], url_path="update")
    def update_application(self, request, pk=None):
        payload, status_code = ProjectClosureService.update_application(request, pk)
        return Response(payload, status=status_code)

    @action(detail=True, methods=["delete"], url_path="delete")
    def delete(self, request, pk=None):
        payload, status_code = ProjectClosureService.delete(request, pk)
        return Response(payload, status=status_code)

    @action(detail=True, methods=["get"], url_path="achievements")
    def achievements(self, request, pk=None):
        payload, status_code = ProjectClosureService.achievements(request, pk)
        return Response(payload, status=status_code)
