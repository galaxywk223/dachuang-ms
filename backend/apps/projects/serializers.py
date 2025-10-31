"""
项目序列化器
"""

from rest_framework import serializers
from .models import Project, ProjectMember, ProjectProgress, ProjectAchievement


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员序列化器
    """

    user_name = serializers.CharField(source="user.real_name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id",
            "user",
            "user_name",
            "employee_id",
            "role",
            "join_date",
            "contribution",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目序列化器
    """

    leader_name = serializers.CharField(source="leader.real_name", read_only=True)
    members_info = ProjectMemberSerializer(
        source="projectmember_set", many=True, read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    achievements_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "title",
            "description",
            "level",
            "level_display",
            "leader",
            "leader_name",
            "members_info",
            "advisor",
            "advisor_title",
            "category",
            "research_field",
            "keywords",
            "start_date",
            "end_date",
            "budget",
            "research_content",
            "research_plan",
            "expected_results",
            "innovation_points",
            "proposal_file",
            "final_report",
            "achievement_file",
            "status",
            "status_display",
            "college",
            "ranking",
            "achievements_count",
            "created_at",
            "updated_at",
            "submitted_at",
            "closure_applied_at",
        ]
        read_only_fields = [
            "id",
            "project_no",
            "created_at",
            "updated_at",
            "submitted_at",
            "closure_applied_at",
        ]

    def get_achievements_count(self, obj):
        """获取项目成果数量"""
        return obj.achievements.count()

    def validate_proposal_file(self, value):
        """
        验证申报书文件
        """
        if value:
            # 检查文件格式
            if not value.name.lower().endswith(".pdf"):
                raise serializers.ValidationError("申报书必须是PDF格式")

            # 检查文件大小（不超过2MB）
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("申报书文件大小不能超过2MB")

        return value

    def create(self, validated_data):
        # 自动生成项目编号
        import datetime

        year = datetime.datetime.now().year
        count = Project.objects.filter(project_no__startswith=f"DC{year}").count() + 1
        validated_data["project_no"] = f"DC{year}{count:04d}"

        # 自动设置学院为负责人的学院
        leader = validated_data["leader"]
        validated_data["college"] = leader.college

        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """
    项目列表序列化器（简化版）
    """

    leader_name = serializers.CharField(source="leader.real_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "title",
            "level",
            "level_display",
            "leader",
            "leader_name",
            "status",
            "status_display",
            "college",
            "created_at",
            "submitted_at",
        ]


class ProjectProgressSerializer(serializers.ModelSerializer):
    """
    项目进度序列化器
    """

    creator_name = serializers.CharField(source="created_by.real_name", read_only=True)

    class Meta:
        model = ProjectProgress
        fields = [
            "id",
            "project",
            "title",
            "content",
            "attachment",
            "created_by",
            "creator_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]


class ProjectSubmitSerializer(serializers.Serializer):
    """
    项目提交序列化器
    """

    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        try:
            project = Project.objects.get(id=value)
            # 检查项目是否可以提交
            if project.status not in [Project.ProjectStatus.DRAFT]:
                raise serializers.ValidationError("项目状态不允许提交")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("项目不存在")


class ProjectAchievementSerializer(serializers.ModelSerializer):
    """
    项目成果序列化器
    """

    achievement_type_display = serializers.CharField(
        source="get_achievement_type_display", read_only=True
    )

    class Meta:
        model = ProjectAchievement
        fields = [
            "id",
            "project",
            "achievement_type",
            "achievement_type_display",
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        根据成果类型验证必填字段
        """
        achievement_type = attrs.get("achievement_type")

        if achievement_type == ProjectAchievement.AchievementType.PAPER:
            if not attrs.get("authors") or not attrs.get("journal"):
                raise serializers.ValidationError("论文成果需要填写作者和期刊信息")

        elif achievement_type == ProjectAchievement.AchievementType.PATENT:
            if not attrs.get("applicant"):
                raise serializers.ValidationError("专利成果需要填写申请人")

        elif achievement_type == ProjectAchievement.AchievementType.SOFTWARE_COPYRIGHT:
            if not attrs.get("copyright_owner"):
                raise serializers.ValidationError("软著成果需要填写著作权人")

        elif achievement_type == ProjectAchievement.AchievementType.COMPETITION_AWARD:
            if not attrs.get("competition_name") or not attrs.get("award_level"):
                raise serializers.ValidationError("竞赛成果需要填写竞赛名称和获奖等级")

        return attrs


class ProjectClosureSerializer(serializers.Serializer):
    """
    项目结题申请序列化器
    """

    project_id = serializers.IntegerField()
    final_report = serializers.FileField(required=True, help_text="结题报告书（必需）")
    is_draft = serializers.BooleanField(default=False, help_text="是否保存为草稿")

    def validate_project_id(self, value):
        """
        验证项目ID和项目状态
        """
        try:
            project = Project.objects.get(id=value)
            # 只有进行中的项目才能结题
            if project.status != Project.ProjectStatus.IN_PROGRESS:
                raise serializers.ValidationError("只有进行中的项目才能申请结题")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("项目不存在")

    def validate_final_report(self, value):
        """
        验证结题报告文件
        """
        # 检查文件格式
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("结题报告必须是PDF格式")

        # 检查文件大小（不超过2MB）
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("结题报告文件大小不能超过2MB")

        return value
