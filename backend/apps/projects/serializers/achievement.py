"""
项目成果序列化器
"""

from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem

from ..models import ProjectAchievement


class ProjectAchievementSerializer(serializers.ModelSerializer):
    """
    项目成果序列化器
    """

    achievement_type_display = serializers.CharField(
        source="achievement_type.label", read_only=True
    )
    achievement_type_value = serializers.CharField(
        source="achievement_type.value", read_only=True
    )
    project_title = serializers.CharField(source="project.title", read_only=True)
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    leader_name = serializers.CharField(source="project.leader.real_name", read_only=True)
    college = serializers.SerializerMethodField()
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_role = serializers.CharField(write_only=True, required=False, allow_blank=True)
    company_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    conference_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    conference_level = serializers.CharField(write_only=True, required=False, allow_blank=True)
    conference_date = serializers.DateField(write_only=True, required=False, allow_null=True)
    report_title = serializers.CharField(write_only=True, required=False, allow_blank=True)
    report_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    media_title = serializers.CharField(write_only=True, required=False, allow_blank=True)
    media_format = serializers.CharField(write_only=True, required=False, allow_blank=True)
    media_link = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = ProjectAchievement
        fields = [
            "id",
            "project",
            "project_title",
            "project_no",
            "leader_name",
            "college",
            "achievement_type",
            "achievement_type_display",
            "achievement_type_value",
            "title",
            "description",
            "authors",
            "journal",
            "publication_date",
            "doi",
            "patent_no",
            "patent_type",
            "applicant",
            "copyright_no",
            "copyright_owner",
            "competition_name",
            "award_level",
            "award_date",
            "attachment",
            "extra_data",
            "company_name",
            "company_role",
            "company_date",
            "conference_name",
            "conference_level",
            "conference_date",
            "report_title",
            "report_type",
            "media_title",
            "media_format",
            "media_link",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_college(self, obj):
        if not obj.project.leader or not obj.project.leader.college:
            return ""
        item = DictionaryItem.objects.filter(
            dict_type__code="college", value=obj.project.leader.college
        ).first()
        return item.label if item else obj.project.leader.college

    def validate(self, attrs):
        """
        根据成果类型验证必填字段
        """
        achievement_type = attrs.get("achievement_type")
        # achievement_type is a DictionaryItem object
        if not achievement_type:
            return attrs

        type_value = achievement_type.value

        if type_value == "PAPER":
            if not attrs.get("authors") or not attrs.get("journal"):
                raise serializers.ValidationError("论文成果需要填写作者和期刊信息")

        elif type_value == "PATENT":
            if not attrs.get("applicant"):
                raise serializers.ValidationError("专利成果需要填写申请人")

        elif type_value == "SOFTWARE_COPYRIGHT":
            if not attrs.get("copyright_owner"):
                raise serializers.ValidationError("软著成果需要填写著作权人")

        elif type_value == "COMPETITION_AWARD":
            if not attrs.get("competition_name") or not attrs.get("award_level"):
                raise serializers.ValidationError("竞赛成果需要填写竞赛名称和获奖等级")

        return attrs

    def _extract_extra_data(self, validated_data):
        extra_fields = [
            "company_name",
            "company_role",
            "company_date",
            "conference_name",
            "conference_level",
            "conference_date",
            "report_title",
            "report_type",
            "media_title",
            "media_format",
            "media_link",
        ]
        extra_data = dict(validated_data.get("extra_data") or {})
        for key in extra_fields:
            if key in validated_data:
                value = validated_data.pop(key)
                if value not in (None, ""):
                    extra_data[key] = value
        validated_data["extra_data"] = extra_data

    def create(self, validated_data):
        self._extract_extra_data(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._extract_extra_data(validated_data)
        return super().update(instance, validated_data)
