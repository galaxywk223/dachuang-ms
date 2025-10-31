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
        "college",
        "created_at",
    ]
    list_filter = ["status", "level", "category", "college"]
    search_fields = ["project_no", "title"]
    ordering = ["-created_at"]


@admin.register(ProjectAdvisor)
class ProjectAdvisorAdmin(admin.ModelAdmin):
    list_display = ["project", "name", "title", "department", "order"]
    list_filter = ["title"]
    search_fields = ["project__title", "name"]
    ordering = ["project", "order"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "role", "student_id", "join_date"]
    list_filter = ["role"]
    search_fields = ["project__title", "user__real_name", "student_id"]


@admin.register(ProjectProgress)
class ProjectProgressAdmin(admin.ModelAdmin):
    list_display = ["project", "title", "created_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["project__title", "title"]
    ordering = ["-created_at"]
