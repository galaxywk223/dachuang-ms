from django.contrib import admin
from .models import Project, ProjectMember, ProjectAdvisor, ProjectProgress


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "project_no",
        "title",
        "leader",
        "level",
        "category",
        "status",
        "created_at",
    ]
    list_filter = ["status", "level", "category"]
    search_fields = ["project_no", "title"]
    ordering = ["-created_at"]


@admin.register(ProjectAdvisor)
class ProjectAdvisorAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "order"]
    list_filter = []
    search_fields = ["project__title", "user__real_name"]
    ordering = ["project", "order"]


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
