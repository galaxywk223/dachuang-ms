from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "project",
        "review_type",
        "review_level",
        "reviewer",
        "status",
        "reviewed_at",
    ]
    list_filter = ["review_type", "review_level", "status"]
    search_fields = ["project__project_no", "project__title", "reviewer__real_name"]
    ordering = ["-created_at"]
