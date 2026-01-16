"""
用户路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, AdminUserViewSet
from .views.role_views import RoleViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"admin/users", AdminUserViewSet, basename="admin-users")
router.register(r"roles", RoleViewSet, basename="role")

urlpatterns = [
    path("login/", AuthViewSet.as_view({"post": "login"}), name="login"),
    path("logout/", AuthViewSet.as_view({"post": "logout"}), name="logout"),
    path(
        "profile/",
        AuthViewSet.as_view({"get": "profile", "put": "update_profile"}),
        name="profile",
    ),
    path(
        "change-password/",
        AuthViewSet.as_view({"post": "change_password"}),
        name="change-password",
    ),
    path("", include(router.urls)),
]
