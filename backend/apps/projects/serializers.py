"""
项目序列化器
"""

from rest_framework import serializers
from .models import (
    Project,
    ProjectMember,
    ProjectAdvisor,
    ProjectProgress,
    ProjectAchievement,
    ProjectExpenditure,
)
from apps.dictionaries.models import DictionaryItem


class ProjectAdvisorSerializer(serializers.ModelSerializer):
    """
    项目指导教师序列化器
    """

    job_number = serializers.CharField(source="user.employee_id", read_only=True)
    name = serializers.CharField(source="user.real_name", read_only=True)
    user_name = serializers.CharField(source="user.real_name", read_only=True)
    department = serializers.CharField(source="user.department", read_only=True)
    contact = serializers.CharField(source="user.phone", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    title = serializers.CharField(source="user.title", read_only=True, allow_blank=True, default="")
    
    class Meta:
        model = ProjectAdvisor
        fields = [
            "id",
            "user",
            "job_number",
            "name",
            "user_name",
            "department",
            "contact",
            "email",
            "title",
            "order",
        ]


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员序列化器
    """

    user_name = serializers.CharField(source="user.real_name", read_only=True)
    student_id = serializers.CharField(source="user.employee_id", read_only=True)
    name = serializers.CharField(source="user.real_name", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id",
            "user",
            "user_name",
            "student_id",
            "name",
            "role",
            "join_date",
            "contribution",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目序列化器
    """

    class KeyFieldBoolean(serializers.BooleanField):
        """
        兼容前端字符串 KEY/NORMAL/TRUE/FALSE 等
        """

        TRUE_VALUES = {"true", "t", "1", "yes", "y", "on", "key"}
        FALSE_VALUES = {"false", "f", "0", "no", "n", "off", "normal"}

        def to_internal_value(self, data):
            # DRF 3.16 BooleanField no longer accepts Python bool/int directly,
            # so normalize them here for JSON clients.
            if isinstance(data, bool):
                return data
            if isinstance(data, int) and data in (0, 1):
                return bool(data)
            if isinstance(data, str):
                data = data.strip().lower()
            return super().to_internal_value(data)

    leader_name = serializers.CharField(source="leader.real_name", read_only=True)
    leader_student_id = serializers.CharField(source="leader.employee_id", read_only=True)
    members_info = ProjectMemberSerializer(
        source="projectmember_set", many=True, read_only=True
    )
    advisors_info = ProjectAdvisorSerializer(
        source="advisors", many=True, read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    level_display = serializers.CharField(source="level.label", read_only=True)
    category_display = serializers.CharField(source="category.label", read_only=True)
    source_display = serializers.CharField(source="source.label", read_only=True)
    source_display = serializers.CharField(source="source.label", read_only=True)
    college = serializers.SerializerMethodField()
    major_code = serializers.CharField(source="leader.major", read_only=True, allow_blank=True)
    leader_contact = serializers.CharField(source="leader.phone", read_only=True, allow_blank=True)
    leader_email = serializers.EmailField(source="leader.email", read_only=True, allow_blank=True)
    leader_major = serializers.CharField(source="leader.major", read_only=True, allow_blank=True)
    leader_grade = serializers.CharField(source="leader.grade", read_only=True, allow_blank=True)
    leader_class_name = serializers.CharField(
        source="leader.class_name", read_only=True, allow_blank=True
    )
    leader_department = serializers.CharField(
        source="leader.department", read_only=True, allow_blank=True
    )
    # 接收前端传入的字典项 value（字符串代码），自动转换为 DictionaryItem
    level = serializers.SlugRelatedField(
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_level"),
        required=False,
        allow_null=True,
    )
    category = serializers.SlugRelatedField(
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_type"),
        required=False,
        allow_null=True,
    )
    source = serializers.SlugRelatedField(
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_source"),
        required=False,
        allow_null=True,
    )
    achievements_count = serializers.SerializerMethodField()
    proposal_file_url = serializers.SerializerMethodField()
    attachment_file_url = serializers.SerializerMethodField()
    proposal_file_name = serializers.SerializerMethodField()
    attachment_file_name = serializers.SerializerMethodField()
    mid_term_report_url = serializers.SerializerMethodField()
    mid_term_report_name = serializers.SerializerMethodField()
    proposal_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    attachment_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    mid_term_report = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    is_key_field = KeyFieldBoolean(required=False)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "title",
            "description",
            "level",
            "level_display",
            "category",
            "category_display",
            "source",
            "source_display",
            "leader",
            "leader_name",
            "leader_student_id",
            "college",
            "major_code",
            "leader_contact",
            "leader_email",
            "leader_major",
            "leader_grade",
            "leader_class_name",
            "leader_department",
            "members_info",
            "advisors_info",
            "is_key_field",
            "key_domain_code",
            "self_funding",
            "category_description",
            "start_date",
            "end_date",
            "budget",
            "research_content",
            "research_plan",
            "expected_results",
            "innovation_points",
            "proposal_file",
            "attachment_file",
            "final_report",
            "achievement_file",
            "mid_term_report",
            "proposal_file_url",
            "attachment_file_url",
            "mid_term_report_url",
            "proposal_file_name",
            "attachment_file_name",
            "mid_term_report_name",
            "status",
            "status_display",
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
            "mid_term_submitted_at",
            "closure_applied_at",
        ]

    def get_achievements_count(self, obj):
        """获取项目成果数量"""
        return obj.achievements.count()

    def _build_file_url(self, file_field):
        if not file_field:
            return ""
        try:
            request = self.context.get("request")
            url = file_field.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return ""

    def get_proposal_file_url(self, obj):
        return self._build_file_url(obj.proposal_file)

    def get_attachment_file_url(self, obj):
        return self._build_file_url(obj.attachment_file)

    def get_proposal_file_name(self, obj):
        return obj.proposal_file.name if obj.proposal_file else ""

    def get_attachment_file_name(self, obj):
        return obj.attachment_file.name if obj.attachment_file else ""

    def get_mid_term_report_url(self, obj):
        return self._build_file_url(obj.mid_term_report)

    def get_mid_term_report_name(self, obj):
        return obj.mid_term_report.name if obj.mid_term_report else ""

    def get_college(self, obj):
        if not obj.leader or not obj.leader.college:
            return ""
        item = DictionaryItem.objects.filter(
            dict_type__code="college", value=obj.leader.college
        ).first()
        return item.label if item else obj.leader.college

    def validate_proposal_file(self, value):
        """
        验证申报书文件
        """
        if not value:
            return None
            
        # Treat empty file (0 bytes) as None
        if value.size == 0:
            return None

        # 检查文件格式
        allowed_extensions = [".pdf", ".doc", ".docx"]
        ext = value.name.lower()[value.name.rfind(".") :]
        if ext not in allowed_extensions:
            raise serializers.ValidationError("申报书必须是PDF或Word格式")

        # 检查文件大小（不超过20MB）
        if value.size > 20 * 1024 * 1024:
            raise serializers.ValidationError("申报书文件大小不能超过20MB")

        return value

    def validate_level(self, value):
        """
        兼容前端的 SCHOOL_KEY 选项
        """
        # value is a DictionaryItem object
        if value and value.value == "SCHOOL_KEY":
            return value
        return value

    def validate(self, attrs):
        """
        重点领域逻辑：
        - 一般项目(is_key_field=False)不要求/不保留重点领域代码
        - 重点项目(is_key_field=True)必须提供 key_domain_code
        """
        instance = getattr(self, "instance", None)
        next_is_key_field = attrs.get(
            "is_key_field",
            instance.is_key_field if instance is not None else False,
        )
        next_key_domain_code = attrs.get(
            "key_domain_code",
            instance.key_domain_code if instance is not None else "",
        )

        if next_is_key_field:
            if not next_key_domain_code:
                raise serializers.ValidationError(
                    {"key_domain_code": "重点项目必须选择重点领域代码"}
                )
        else:
            # 仅当明确切换为一般项目时清空重点领域代码，避免 partial update 意外抹掉
            if "is_key_field" in attrs:
                attrs["key_domain_code"] = ""

        return attrs

    def create(self, validated_data):
        # 自动生成项目编号
        import datetime

        year = datetime.datetime.now().year
        count = Project.objects.filter(project_no__startswith=f"DC{year}").count() + 1
        validated_data["project_no"] = f"DC{year}{count:04d}"

        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """
    项目列表序列化器（简化版）
    """

    leader_name = serializers.CharField(source="leader.real_name", read_only=True)
    leader_student_id = serializers.CharField(source="leader.employee_id", read_only=True)
    leader_contact = serializers.CharField(source="leader.phone", read_only=True)
    leader_email = serializers.CharField(source="leader.email", read_only=True)
    college = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    level_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "title",
            "level",
            "level_display",
            "category",
            "category_display",
            "leader",
            "leader_name",
            "leader_student_id",
            "leader_contact",
            "leader_email",
            "status",
            "status_display",
            "college",
            "budget",
            "is_key_field",
            "key_domain_code",
            "created_at",
            "submitted_at",
        ]

    def get_level_display(self, obj):
        return obj.level.label if obj.level else ""

    def get_category_display(self, obj):
        return obj.category.label if obj.category else ""

    def get_college(self, obj):
        if not obj.leader or not obj.leader.college:
            return ""
        item = DictionaryItem.objects.filter(
            dict_type__code="college", value=obj.leader.college
        ).first()
        return item.label if item else obj.leader.college


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
        source="achievement_type.label", read_only=True
    )
    project_title = serializers.CharField(source="project.title", read_only=True)
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    leader_name = serializers.CharField(source="project.leader.real_name", read_only=True)
    college = serializers.SerializerMethodField()

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


class ProjectExpenditureSerializer(serializers.ModelSerializer):
    """
    项目经费支出序列化器
    """
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.real_name", read_only=True)
    proof_file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectExpenditure
        fields = [
            "id",
            "project",
            "title",
            "amount",
            "expenditure_date",
            "category",
            "category_name",
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
