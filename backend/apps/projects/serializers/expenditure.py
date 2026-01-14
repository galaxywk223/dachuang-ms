"""
项目经费序列化器
"""

from rest_framework import serializers

from ..models import ProjectExpenditure


class ProjectExpenditureSerializer(serializers.ModelSerializer):
    """
    项目经费支出序列化器
    """

    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )
    proof_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectExpenditure
        fields = [
            "id",
            "project",
            "title",
            "amount",
            "expenditure_date",
            "proof_file",
            "proof_file_url",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_by", "created_at"]

    def get_proof_file_url(self, obj):
        if obj.proof_file:
            return obj.proof_file.url
        return None
