from django.contrib import admin
from .models import User


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


