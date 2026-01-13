"""
项目基础序列化器
"""

from rest_framework import serializers

from apps.dictionaries.models import DictionaryItem
from apps.system_settings.models import ProjectBatch
from apps.system_settings.services import SystemSettingService

from ..models import Project
from .members import ProjectAdvisorSerializer, ProjectMemberSerializer


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
    leader_student_id = serializers.CharField(
        source="leader.employee_id", read_only=True
    )
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
    major_code = serializers.CharField(
        source="leader.major", read_only=True, allow_blank=True
    )
    leader_contact = serializers.CharField(
        source="leader.phone", read_only=True, allow_blank=True
    )
    leader_email = serializers.EmailField(
        source="leader.email", read_only=True, allow_blank=True
    )
    leader_major = serializers.CharField(
        source="leader.major", read_only=True, allow_blank=True
    )
    leader_grade = serializers.CharField(
        source="leader.grade", read_only=True, allow_blank=True
    )
    leader_class_name = serializers.CharField(
        source="leader.class_name", read_only=True, allow_blank=True
    )
    leader_department = serializers.CharField(
        source="leader.department", read_only=True, allow_blank=True
    )
    # 接收前端传入的字典项 value（字符串代码），自动转换为 DictionaryItem
    level = serializers.SlugRelatedField(  # type: ignore[assignment]
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_level"),
        required=False,
        allow_null=True,
    )
    category = serializers.SlugRelatedField(  # type: ignore[assignment]
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_type"),
        required=False,
        allow_null=True,
    )
    source = serializers.SlugRelatedField(  # type: ignore[assignment]
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
    proposal_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True
    )
    attachment_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True
    )
    contract_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True
    )
    task_book_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True
    )
    mid_term_report = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True
    )
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
            "achievement_summary",
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
                process_rules = SystemSettingService.get_setting(
                    "PROCESS_RULES", batch=batch
                )
                max_student_active = int(limits.get("max_student_active", 1) or 0)
                allow_active_reapply = bool(
                    process_rules.get("allow_active_reapply", False)
                )

                if not allow_active_reapply and not is_draft:
                    active_projects_count = (
                        Project.objects.filter(leader=user)
                        .exclude(
                            status__in=[
                                Project.ProjectStatus.DRAFT,
                                Project.ProjectStatus.CLOSED,
                                Project.ProjectStatus.COMPLETED,
                                Project.ProjectStatus.TEACHER_REJECTED,
                                Project.ProjectStatus.TERMINATED,
                            ]
                        )
                        .count()
                    )
                    if (
                        max_student_active
                        and active_projects_count >= max_student_active
                    ):
                        raise serializers.ValidationError(
                            "您已有在研或审核中的项目，在校期间限报一项。"
                        )

        limits = SystemSettingService.get_setting("LIMIT_RULES", batch=batch)
        validation_rules = SystemSettingService.get_setting(
            "VALIDATION_RULES", batch=batch
        )
        if not is_draft and limits.get("dedupe_title"):
            title = attrs.get("title")
            if title:
                queryset = Project.objects.filter(title__iexact=title)
                if self.instance:
                    queryset = queryset.exclude(id=self.instance.id)
                if queryset.exists():
                    raise serializers.ValidationError("项目名称已存在，请勿重复申报")

        if not is_draft:
            title = attrs.get("title") or (self.instance.title if self.instance else "")
            min_len = int(validation_rules.get("title_min_length", 0) or 0)
            max_len = int(validation_rules.get("title_max_length", 200) or 200)
            if title and (len(title) < min_len or len(title) > max_len):
                raise serializers.ValidationError("项目名称长度不符合要求")
            title_regex = validation_rules.get("title_regex") or ""
            if title_regex:
                import re

                if title and not re.match(title_regex, title):
                    raise serializers.ValidationError("项目名称格式不符合要求")

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

        if not is_draft:
            leader = attrs.get("leader") or (request.user if request else None)
            college_code = leader.college if leader else ""
            allowed_types = validation_rules.get("allowed_project_types") or []
            allowed_by_college = (
                validation_rules.get("allowed_project_types_by_college") or {}
            )
            allowed_levels_by_college = (
                validation_rules.get("allowed_levels_by_college") or {}
            )
            if (
                allowed_types
                and attrs.get("category")
                and attrs.get("category").value not in allowed_types
            ):
                raise serializers.ValidationError("项目类别不符合申报要求")
            if college_code and allowed_by_college:
                college_allowed = allowed_by_college.get(college_code) or []
                if (
                    college_allowed
                    and attrs.get("category")
                    and attrs.get("category").value not in college_allowed
                ):
                    raise serializers.ValidationError("当前学院不允许申报该类别")
            if college_code and allowed_levels_by_college:
                level_allowed = allowed_levels_by_college.get(college_code) or []
                if (
                    level_allowed
                    and attrs.get("level")
                    and attrs.get("level").value not in level_allowed
                ):
                    raise serializers.ValidationError("当前学院不允许申报该级别")

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

        from ..services import ProjectService

        if not validated_data.get("project_no"):
            request = self.context.get("request")
            leader = validated_data.get("leader") or (request.user if request else None)
            batch = (
                validated_data.get("batch") or SystemSettingService.get_current_batch()
            )
            if batch and not validated_data.get("batch"):
                validated_data["batch"] = batch
            year = validated_data.get("year") or (
                batch.year if batch else timezone.now().year
            )
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
    leader_student_id = serializers.CharField(
        source="leader.employee_id", read_only=True
    )
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
