from django.contrib import admin
from .models import User, LoginLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "employee_id",
        "real_name",
        "role_fk",
        "college",
        "is_active",
        "created_at",
    ]
    list_filter = ["role_fk", "is_active", "college"]
    search_fields = ["employee_id", "real_name", "phone", "email"]
    ordering = ["-created_at"]


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ["user", "login_time", "ip_address", "login_status"]
    list_filter = ["login_status", "login_time"]
    search_fields = ["user__real_name", "user__employee_id", "ip_address"]
    ordering = ["-login_time"]
