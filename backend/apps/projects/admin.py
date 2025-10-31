from django.contrib import admin
from .models import Project, ProjectMember, ProjectProgress


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "project_no",
        "title",
        "leader",
        "level",
        "status",
        "college",
        "created_at",
    ]
    list_filter = ["status", "level", "college"]
    search_fields = ["project_no", "title", "advisor"]
    ordering = ["-created_at"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "role", "join_date"]
    list_filter = ["role"]
    search_fields = ["project__title", "user__real_name"]


@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ["project", "title", "created_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["project__title", "title"]
    ordering = ["-created_at"]
