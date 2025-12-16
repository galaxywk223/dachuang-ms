"""
项目路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectProgressViewSet, ProjectAchievementViewSet
from .views_application import (
    create_project_application,
    update_project_application,
    withdraw_project_application,
    get_my_projects,
    get_my_drafts,
)
from .views_closure import (
    get_pending_closure_projects,
    get_applied_closure_projects,
    get_closure_drafts,
    create_closure_application,
    update_closure_application,
    delete_closure_draft,
    get_project_achievements,
)
from .views_review import ProjectReviewViewSet
from .views_management import ProjectManagementViewSet, AchievementManagementViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="project")
router.register(r"progress", ProjectProgressViewSet, basename="progress")
router.register(r"admin/review", ProjectReviewViewSet, basename="admin-review")
# router.register(r"admin/achievements", AchievementManagementViewSet, basename="admin-achievements")
router.register(r"achievements", ProjectAchievementViewSet, basename="achievement")

urlpatterns = [
    # 立项管理
    path("application/create/", create_project_application, name="create-application"),
    path(
        "application/<int:pk>/update/",
        update_project_application,
        name="update-application",
    ),
    path(
        "application/<int:pk>/withdraw/",
        withdraw_project_application,
        name="withdraw-application",
    ),
    path("my-projects/", get_my_projects, name="my-projects"),
    path("my-drafts/", get_my_drafts, name="my-drafts"),
    # 结题管理
    path(
        "closure/pending/",
        get_pending_closure_projects,
        name="pending-closure-projects",
    ),
    path(
        "closure/applied/",
        get_applied_closure_projects,
        name="applied-closure-projects",
    ),
    path("closure/drafts/", get_closure_drafts, name="closure-drafts"),
    path(
        "closure/<int:pk>/create/",
        create_closure_application,
        name="create-closure",
    ),
    path(
        "closure/<int:pk>/update/",
        update_closure_application,
        name="update-closure",
    ),
    path(
        "closure/<int:pk>/delete/",
        delete_closure_draft,
        name="delete-closure-draft",
    ),
    path(
        "closure/<int:pk>/achievements/",
        get_project_achievements,
        name="project-achievements",
    ),
    path(
        "admin/achievements/",
        AchievementManagementViewSet.as_view({"get": "list"}),
        name="admin-achievements-list",
    ),
    path(
        "admin/achievements/export/",
        AchievementManagementViewSet.as_view({"get": "export_data"}),
        name="admin-achievements-export",
    ),
] + router.urls
