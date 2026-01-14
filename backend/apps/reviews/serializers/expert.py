from rest_framework import serializers
from ..models import ExpertGroup
from apps.users.serializers import UserSerializer


class ExpertGroupSerializer(serializers.ModelSerializer):
    members_info = UserSerializer(source="members", many=True, read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )

    class Meta:
        model = ExpertGroup
        fields = [
            "id",
            "name",
            "members",
            "members_info",
            "created_by",
            "created_by_name",
            "scope",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at", "scope"]

    def validate_members(self, value):
        """
        验证专家组成员：
        1. 学院级管理员只能选择本学院教师
        2. 确保所有成员都是教师角色
        """
        request = self.context.get("request")
        if not request or not request.user:
            return value

        creator = request.user

        # 检查所有成员都是教师角色
        for member in value:
            if not member.role_fk or member.role_fk.code != "TEACHER":
                raise serializers.ValidationError(
                    f"用户 {member.real_name}({member.employee_id}) 不是教师角色，不能作为专家组成员"
                )
            if not member.is_expert:
                raise serializers.ValidationError(
                    f"教师 {member.real_name}({member.employee_id}) 未设置为专家"
                )

        # 学院级管理员的学院限制检查
        if creator.role_fk and creator.role_fk.scope_dimension == "COLLEGE":
            creator_college_item = creator.managed_scope_value
            if not creator_college_item:
                raise serializers.ValidationError("学院级管理员未配置管理范围")

            creator_college = creator_college_item.value
            for member in value:
                if member.college != creator_college:
                    raise serializers.ValidationError(
                        f"学院级管理员只能选择本学院教师作为专家。"
                        f"教师 {member.real_name}({member.employee_id}) 不属于 {creator_college}"
                    )
                if member.expert_assigned_by_id and member.expert_assigned_by_id != creator.id:
                    raise serializers.ValidationError(
                        "无权限选择其他管理员设置的专家"
                    )

        return value
