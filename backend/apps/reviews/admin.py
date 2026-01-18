from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "project",
        "review_type",
        "role_code",
        "workflow_node",
        "reviewer",
        "status",
        "reviewed_at",
    ]
    list_filter = ["review_type", "status"]
    search_fields = ["project__project_no", "project__title", "reviewer__real_name"]
    ordering = ["-created_at"]

    def role_code(self, obj):
        return obj.workflow_node.get_role_code() if obj.workflow_node else ""

    role_code.short_description = "角色"
