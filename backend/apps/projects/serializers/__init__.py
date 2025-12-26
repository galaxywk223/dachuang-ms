"""
项目序列化器
"""

from rest_framework import serializers
from ..models import (
    Project,
    ProjectMember,
    ProjectAdvisor,
    ProjectProgress,
    ProjectAchievement,
    ProjectExpenditure,
    ProjectChangeRequest,
    ProjectChangeReview,
    ProjectArchive,
    ProjectPushRecord,
)
from apps.dictionaries.models import DictionaryItem
from apps.system_settings.services import SystemSettingService
from apps.system_settings.models import ProjectBatch


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
    batch_name = serializers.SerializerMethodField()
    batch_year = serializers.SerializerMethodField()
    batch = serializers.PrimaryKeyRelatedField(
        queryset=ProjectBatch.objects.all(),
        required=False,
        allow_null=True,
    )
    proposal_file_url = serializers.SerializerMethodField()
    attachment_file_url = serializers.SerializerMethodField()
    proposal_file_name = serializers.SerializerMethodField()
    attachment_file_name = serializers.SerializerMethodField()
    contract_file_url = serializers.SerializerMethodField()
    contract_file_name = serializers.SerializerMethodField()
    task_book_file_url = serializers.SerializerMethodField()
    task_book_file_name = serializers.SerializerMethodField()
    mid_term_report_url = serializers.SerializerMethodField()
    mid_term_report_name = serializers.SerializerMethodField()
    final_report_url = serializers.SerializerMethodField()
    final_report_name = serializers.SerializerMethodField()
    achievement_file_url = serializers.SerializerMethodField()
    achievement_file_name = serializers.SerializerMethodField()
    proposal_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    attachment_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    contract_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    task_book_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    mid_term_report = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    is_key_field = KeyFieldBoolean(required=False)
    expected_results_data = serializers.JSONField(required=False)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "batch",
            "batch_name",
            "batch_year",
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
            "approved_budget",
            "research_content",
            "research_plan",
            "expected_results",
            "expected_results_data",
            "innovation_points",
            "proposal_file",
            "attachment_file",
            "contract_file",
            "task_book_file",
            "final_report",
            "achievement_file",
            "mid_term_report",
            "proposal_file_url",
            "attachment_file_url",
            "contract_file_url",
            "task_book_file_url",
            "mid_term_report_url",
            "final_report_url",
            "achievement_file_url",
            "proposal_file_name",
            "attachment_file_name",
            "contract_file_name",
            "task_book_file_name",
            "mid_term_report_name",
            "final_report_name",
            "achievement_file_name",
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

    def get_contract_file_url(self, obj):
        return self._build_file_url(obj.contract_file)

    def get_task_book_file_url(self, obj):
        return self._build_file_url(obj.task_book_file)

    def get_proposal_file_name(self, obj):
        return obj.proposal_file.name if obj.proposal_file else ""

    def get_attachment_file_name(self, obj):
        return obj.attachment_file.name if obj.attachment_file else ""

    def get_contract_file_name(self, obj):
        return obj.contract_file.name if obj.contract_file else ""

    def get_task_book_file_name(self, obj):
        return obj.task_book_file.name if obj.task_book_file else ""

    def get_mid_term_report_url(self, obj):
        return self._build_file_url(obj.mid_term_report)

    def get_mid_term_report_name(self, obj):
        return obj.mid_term_report.name if obj.mid_term_report else ""

    def get_final_report_url(self, obj):
        return self._build_file_url(obj.final_report)

    def get_final_report_name(self, obj):
        return obj.final_report.name if obj.final_report else ""

    def get_achievement_file_url(self, obj):
        return self._build_file_url(obj.achievement_file)

    def get_achievement_file_name(self, obj):
        return obj.achievement_file.name if obj.achievement_file else ""

    def get_college(self, obj):
        if not obj.leader or not obj.leader.college:
            return ""
        item = DictionaryItem.objects.filter(
            dict_type__code="college", value=obj.leader.college
        ).first()
        return item.label if item else obj.leader.college

    def get_batch_name(self, obj):
        if not obj.batch:
            return ""
        return obj.batch.name

    def get_batch_year(self, obj):
        if not obj.batch:
            return obj.year
        return obj.batch.year

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
        request = self.context.get("request")
        is_draft = bool(self.context.get("is_draft", False))
        batch = attrs.get("batch") or (self.instance.batch if self.instance else None)
        if request and request.method == "POST":
            user = request.user
            if user.is_student:
                limits = SystemSettingService.get_setting("LIMIT_RULES", batch=batch)
                process_rules = SystemSettingService.get_setting("PROCESS_RULES", batch=batch)
                max_student_active = int(limits.get("max_student_active", 1) or 0)
                allow_active_reapply = bool(process_rules.get("allow_active_reapply", False))

                if not allow_active_reapply and not is_draft:
                    active_projects_count = Project.objects.filter(leader=user).exclude(
                        status__in=[
                        Project.ProjectStatus.DRAFT,
                        Project.ProjectStatus.CLOSED,
                        Project.ProjectStatus.COMPLETED,
                        Project.ProjectStatus.TEACHER_REJECTED,
                        Project.ProjectStatus.TERMINATED,
                    ]
                    ).count()
                    if max_student_active and active_projects_count >= max_student_active:
                        raise serializers.ValidationError(
                            "您已有在研或审核中的项目，在校期间限报一项。"
                        )

        limits = SystemSettingService.get_setting("LIMIT_RULES", batch=batch)
        if not is_draft and limits.get("dedupe_title"):
            title = attrs.get("title")
            if title:
                queryset = Project.objects.filter(title__iexact=title)
                if self.instance:
                    queryset = queryset.exclude(id=self.instance.id)
                if queryset.exists():
                    raise serializers.ValidationError("项目名称已存在，请勿重复申报")

        if not is_draft:
            leader = attrs.get("leader") or (request.user if request else None)
            year = attrs.get("year") or (self.instance.year if self.instance else None)
            college_code = leader.college if leader else ""
            college_quota = limits.get("college_quota") or {}
            if college_code and year and college_code in college_quota:
                try:
                    quota = int(college_quota.get(college_code) or 0)
                except (TypeError, ValueError):
                    quota = 0
                if quota:
                    qs = Project.objects.filter(
                        year=year, leader__college=college_code
                    ).exclude(status=Project.ProjectStatus.DRAFT)
                    if batch:
                        qs = qs.filter(batch=batch)
                    if self.instance:
                        qs = qs.exclude(id=self.instance.id)
                    if qs.count() >= quota:
                        raise serializers.ValidationError("该学院本年度名额已满")

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
            if not is_draft and not next_key_domain_code:
                raise serializers.ValidationError(
                    {"key_domain_code": "重点项目必须选择重点领域代码"}
                )
        else:
            # 仅当明确切换为一般项目时清空重点领域代码，避免 partial update 意外抹掉
            if "is_key_field" in attrs:
                attrs["key_domain_code"] = ""

        return attrs

    def create(self, validated_data):
        # 自动生成项目编号（基于年份+学院+序号）
        from django.utils import timezone
        from .services import ProjectService

        if not validated_data.get("project_no"):
            request = self.context.get("request")
            leader = validated_data.get("leader") or (request.user if request else None)
            batch = validated_data.get("batch") or SystemSettingService.get_current_batch()
            if batch and not validated_data.get("batch"):
                validated_data["batch"] = batch
            year = validated_data.get("year") or (batch.year if batch else timezone.now().year)
            validated_data["year"] = year
            college_code = leader.college if leader else ""
            validated_data["project_no"] = ProjectService.generate_project_no(
                year, college_code
            )

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
    proposal_file_url = serializers.SerializerMethodField()
    contract_file_url = serializers.SerializerMethodField()
    task_book_file_url = serializers.SerializerMethodField()
    mid_term_report_url = serializers.SerializerMethodField()
    final_report_url = serializers.SerializerMethodField()
    batch_name = serializers.SerializerMethodField()
    batch_year = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "batch",
            "batch_name",
            "batch_year",
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
            "approved_budget",
            "is_key_field",
            "key_domain_code",
            "proposal_file_url",
            "contract_file_url",
            "task_book_file_url",
            "mid_term_report_url",
            "final_report_url",
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

    def get_batch_name(self, obj):
        if not obj.batch:
            return ""
        return obj.batch.name

    def get_batch_year(self, obj):
        if not obj.batch:
            return obj.year
        return obj.batch.year

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

    def get_contract_file_url(self, obj):
        return self._build_file_url(obj.contract_file)

    def get_task_book_file_url(self, obj):
        return self._build_file_url(obj.task_book_file)

    def get_mid_term_report_url(self, obj):
        return self._build_file_url(obj.mid_term_report)

    def get_final_report_url(self, obj):
        return self._build_file_url(obj.final_report)


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
            "extra_data",
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
    category_name = serializers.CharField(source="category.label", read_only=True)
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


class ProjectChangeReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.real_name", read_only=True)
    review_level_display = serializers.CharField(
        source="get_review_level_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ProjectChangeReview
        fields = [
            "id",
            "change_request",
            "review_level",
            "review_level_display",
            "reviewer",
            "reviewer_name",
            "status",
            "status_display",
            "comments",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "reviewed_at"]


class ProjectChangeRequestSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    leader_name = serializers.CharField(source="project.leader.real_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    request_type_display = serializers.CharField(
        source="get_request_type_display", read_only=True
    )
    attachment_url = serializers.SerializerMethodField()
    reviews = ProjectChangeReviewSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectChangeRequest
        fields = [
            "id",
            "project",
            "project_title",
            "project_no",
            "leader_name",
            "request_type",
            "request_type_display",
            "reason",
            "change_data",
            "requested_end_date",
            "attachment",
            "attachment_url",
            "status",
            "status_display",
            "created_by",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
            "reviews",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_attachment_url(self, obj):
        if not obj.attachment:
            return ""
        try:
            request = self.context.get("request")
            url = obj.attachment.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return ""

    def validate(self, attrs):
        request_type = attrs.get("request_type") or (
            self.instance.request_type if self.instance else None
        )
        requested_end_date = attrs.get("requested_end_date")
        status_val = attrs.get("status") or (
            self.instance.status if self.instance else ProjectChangeRequest.ChangeStatus.DRAFT
        )
        if (
            request_type == ProjectChangeRequest.ChangeType.EXTENSION
            and not requested_end_date
            and status_val != ProjectChangeRequest.ChangeStatus.DRAFT
        ):
            raise serializers.ValidationError("延期申请必须填写延期日期")
        return attrs

    def validate_change_data(self, value):
        if isinstance(value, str):
            try:
                import json

                return json.loads(value) if value else {}
            except json.JSONDecodeError:
                raise serializers.ValidationError("变更内容JSON格式不正确")
        return value


class ProjectChangeReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["approve", "reject"], help_text="审核操作"
    )
    comments = serializers.CharField(required=False, allow_blank=True)


class ProjectArchiveSerializer(serializers.ModelSerializer):
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = ProjectArchive
        fields = [
            "id",
            "project",
            "project_no",
            "project_title",
            "snapshot",
            "attachments",
            "archived_at",
        ]
        read_only_fields = ["id", "archived_at"]


class ProjectPushRecordSerializer(serializers.ModelSerializer):
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ProjectPushRecord
        fields = [
            "id",
            "project",
            "project_no",
            "project_title",
            "target",
            "payload",
            "response_message",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
