"""
审核序列化器
"""

from rest_framework import serializers
from ..models import Review
from apps.projects.serializers import ProjectListSerializer
from apps.system_settings.services import SystemSettingService
from .expert import ExpertGroupSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """
    审核序列化器
    """

    project_info = serializers.SerializerMethodField()
    reviewer_name = serializers.CharField(source="reviewer.real_name", read_only=True)
    review_type_display = serializers.CharField(
        source="get_review_type_display", read_only=True
    )
    review_level_display = serializers.CharField(
        source="get_review_level_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    closure_rating_display = serializers.CharField(
        source="get_closure_rating_display", read_only=True
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "project",
            "project_info",
            "review_type",
            "review_type_display",
            "review_level",
            "review_level_display",
            "reviewer",
            "reviewer_name",
            "status",
            "status_display",
            "comments",
            "score",
            "closure_rating",
            "closure_rating_display",
            "created_at",
            "reviewed_at",
        ]
        read_only_fields = ["id", "created_at", "reviewed_at"]

    def get_project_info(self, obj):
        request = self.context.get("request")
        data = ProjectListSerializer(obj.project, context={"request": request}).data
        if obj.review_type == Review.ReviewType.CLOSURE:
            rules = SystemSettingService.get_setting(
                "PROCESS_RULES", batch=obj.project.batch
            )
            if not rules.get("show_material_in_closure_review", True):
                data["proposal_file_url"] = ""
        return data


class ReviewActionSerializer(serializers.Serializer):
    """
    审核操作序列化器
    """

    action = serializers.ChoiceField(
        choices=["approve", "reject"], help_text="审核操作：approve-通过，reject-不通过"
    )
    comments = serializers.CharField(
        required=False, allow_blank=True, help_text="审核意见"
    )
    score = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=100,
        help_text="评分（0-100）",
    )
    closure_rating = serializers.ChoiceField(
        choices=Review.ClosureRating.choices,
        required=False,
        help_text="结题评价等级（仅结题审核需要）",
    )
    reject_to = serializers.ChoiceField(
        choices=["teacher", "student"],
        required=False,
        help_text="结题驳回流向（teacher-退回导师，student-退回学生）",
    )


__all__ = [
    "ReviewSerializer",
    "ReviewActionSerializer",
    "ExpertGroupSerializer",
]
