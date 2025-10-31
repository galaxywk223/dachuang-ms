"""
审核序列化器
"""

from rest_framework import serializers
from .models import Review
from apps.projects.serializers import ProjectListSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """
    审核序列化器
    """

    project_info = ProjectListSerializer(source="project", read_only=True)
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
        required=False, min_value=0, max_value=100, help_text="评分（0-100）"
    )
    closure_rating = serializers.ChoiceField(
        choices=Review.ClosureRating.choices,
        required=False,
        help_text="结题评价等级（仅结题审核需要）",
    )
