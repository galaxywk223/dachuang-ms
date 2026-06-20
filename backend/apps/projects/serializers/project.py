"""
项目基础序列化器
"""

from pathlib import Path

from django.urls import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.dictionaries.models import DictionaryItem
from apps.system_settings.models import ProjectBatch
from apps.system_settings.services import SystemSettingService
from apps.utils.pagination import non_negative_int

from ..models import Project
from .members import ProjectAdvisorSerializer, ProjectMemberSerializer
from ..upload_validation import (
    validate_project_document_file,
    validate_project_support_file,
)


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
    publish_status_display = serializers.CharField(
        source="get_publish_status_display", read_only=True
    )
    level_display = serializers.CharField(source="level.label", read_only=True)
    category_display = serializers.CharField(source="category.label", read_only=True)
    source_display = serializers.CharField(source="source.label", read_only=True)
    recommended_level_display = serializers.CharField(
        source="recommended_level.label", read_only=True
    )
    final_level_display = serializers.CharField(
        source="final_level.label", read_only=True
    )
    published_by_name = serializers.CharField(
        source="published_by.real_name", read_only=True
    )
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
    recommended_level = serializers.SlugRelatedField(  # type: ignore[assignment]
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_level"),
        required=False,
        allow_null=True,
    )
    final_level = serializers.SlugRelatedField(  # type: ignore[assignment]
        slug_field="value",
        queryset=DictionaryItem.objects.filter(dict_type__code="project_level"),
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
    mid_term_report_url = serializers.SerializerMethodField()
    mid_term_report_name = serializers.SerializerMethodField()
    final_report_url = serializers.SerializerMethodField()
    final_report_name = serializers.SerializerMethodField()
    achievement_file_url = serializers.SerializerMethodField()
    achievement_file_name = serializers.SerializerMethodField()
    proposal_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True, write_only=True
    )
    attachment_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True, write_only=True
    )
    mid_term_report = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True, write_only=True
    )
    final_report = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True, write_only=True
    )
    achievement_file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True, write_only=True
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
            "start_date",
            "end_date",
            "budget",
            "approved_budget",
            "recommendation_rank",
            "recommended_level",
            "recommended_level_display",
            "recommended_budget",
            "recommendation_comment",
            "final_level",
            "final_level_display",
            "final_budget",
            "publish_status",
            "publish_status_display",
            "published_at",
            "published_by",
            "published_by_name",
            "expected_results",
            "expected_results_data",
            "proposal_file",
            "attachment_file",
            "final_report",
            "achievement_file",
            "mid_term_report",
            "proposal_file_url",
            "attachment_file_url",
            "mid_term_report_url",
            "final_report_url",
            "achievement_file_url",
            "proposal_file_name",
            "attachment_file_name",
            "mid_term_report_name",
            "final_report_name",
            "achievement_file_name",
            "status",
            "status_display",
            "achievements_count",
            "created_at",
            "updated_at",
            "submitted_at",
            "closure_applied_at",
            "is_deleted",
        ]
        read_only_fields = [
            "id",
            "project_no",
            "created_at",
            "updated_at",
            "submitted_at",
            "mid_term_submitted_at",
            "closure_applied_at",
            "published_at",
            "published_by",
        ]

    def get_achievements_count(self, obj):
        """获取项目成果数量"""
        return obj.achievements.count()

    def _build_file_url(self, obj, field_name):
        file_field = getattr(obj, field_name, None)
        if not file_field:
            return ""
        try:
            request = self.context.get("request")
            return reverse(
                "project-download-file",
                args=[obj.pk, field_name],
                request=request,
            )
        except NoReverseMatch:
            return f"/api/v1/projects/{obj.pk}/files/{field_name}/download/"
        except Exception:
            return ""

    def get_proposal_file_url(self, obj):
        return self._build_file_url(obj, "proposal_file")

    def get_attachment_file_url(self, obj):
        return self._build_file_url(obj, "attachment_file")

    def get_proposal_file_name(self, obj):
        return Path(obj.proposal_file.name).name if obj.proposal_file else ""

    def get_attachment_file_name(self, obj):
        return Path(obj.attachment_file.name).name if obj.attachment_file else ""

    def get_mid_term_report_url(self, obj):
        return self._build_file_url(obj, "mid_term_report")

    def get_mid_term_report_name(self, obj):
        return Path(obj.mid_term_report.name).name if obj.mid_term_report else ""

    def get_final_report_url(self, obj):
        return self._build_file_url(obj, "final_report")

    def get_final_report_name(self, obj):
        return Path(obj.final_report.name).name if obj.final_report else ""

    def get_achievement_file_url(self, obj):
        return self._build_file_url(obj, "achievement_file")

    def get_achievement_file_name(self, obj):
        return Path(obj.achievement_file.name).name if obj.achievement_file else ""

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
        return validate_project_document_file(
            value,
            label="申报书",
            max_size_mb=20,
            empty_as_none=True,
        )

    def validate_attachment_file(self, value):
        """
        验证申报附件文件
        """
        return validate_project_support_file(
            value,
            label="申报附件",
            max_size_mb=20,
            empty_as_none=True,
        )

    def validate_mid_term_report(self, value):
        """
        验证中期报告文件
        """
        return validate_project_document_file(
            value,
            label="中期报告",
            max_size_mb=5,
            empty_as_none=True,
        )

    def validate_final_report(self, value):
        """
        验证结题报告文件
        """
        return validate_project_document_file(
            value,
            label="结题报告",
            max_size_mb=2,
            empty_as_none=True,
        )

    def validate_achievement_file(self, value):
        """
        验证成果材料文件
        """
        return validate_project_support_file(
            value,
            label="成果材料",
            max_size_mb=20,
            empty_as_none=True,
        )

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
            current_batch = SystemSettingService.get_current_batch()
            if not current_batch:
                raise serializers.ValidationError("当前没有进行中的批次，无法创建项目")
            if batch and batch.id != current_batch.id:
                raise serializers.ValidationError({"batch": "只能选择当前进行中的批次"})
            if not batch:
                attrs["batch"] = current_batch
                batch = current_batch
        if request and request.method == "POST":
            user = request.user
            if user.is_student:
                limits = SystemSettingService.get_setting("LIMIT_RULES", batch=batch)
                process_rules = SystemSettingService.get_setting(
                    "PROCESS_RULES", batch=batch
                )
                max_student_active = non_negative_int(
                    limits.get("max_student_active"), 1
                )
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
            min_len = non_negative_int(validation_rules.get("title_min_length"), 0)
            max_len = non_negative_int(validation_rules.get("title_max_length"), 200)
            if title and (len(title) < min_len or len(title) > max_len):
                raise serializers.ValidationError("项目名称长度不符合要求")

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
    publish_status_display = serializers.CharField(
        source="get_publish_status_display", read_only=True
    )
    level_display = serializers.SerializerMethodField()
    recommended_level_display = serializers.SerializerMethodField()
    final_level_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    proposal_file_url = serializers.SerializerMethodField()
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
            "recommendation_rank",
            "recommended_level",
            "recommended_level_display",
            "recommended_budget",
            "recommendation_comment",
            "final_level",
            "final_level_display",
            "final_budget",
            "publish_status",
            "publish_status_display",
            "published_at",
            "is_key_field",
            "key_domain_code",
            "proposal_file_url",
            "mid_term_report_url",
            "final_report_url",
            "created_at",
            "submitted_at",
        ]

    def get_level_display(self, obj):
        return obj.level.label if obj.level else ""

    def get_recommended_level_display(self, obj):
        return obj.recommended_level.label if obj.recommended_level else ""

    def get_final_level_display(self, obj):
        return obj.final_level.label if obj.final_level else ""

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

    def _build_file_url(self, obj, field_name):
        file_field = getattr(obj, field_name, None)
        if not file_field:
            return ""
        try:
            request = self.context.get("request")
            return reverse(
                "project-download-file",
                args=[obj.pk, field_name],
                request=request,
            )
        except NoReverseMatch:
            return f"/api/v1/projects/{obj.pk}/files/{field_name}/download/"
        except Exception:
            return ""

    def get_proposal_file_url(self, obj):
        return self._build_file_url(obj, "proposal_file")

    def get_mid_term_report_url(self, obj):
        return self._build_file_url(obj, "mid_term_report")

    def get_final_report_url(self, obj):
        return self._build_file_url(obj, "final_report")


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
