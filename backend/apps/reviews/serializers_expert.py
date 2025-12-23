from rest_framework import serializers
from .models import ExpertGroup
from apps.users.serializers import UserSerializer

class ExpertGroupSerializer(serializers.ModelSerializer):
    members_info = UserSerializer(source='members', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.real_name', read_only=True)

    class Meta:
        model = ExpertGroup
        fields = ['id', 'name', 'members', 'members_info', 'created_by', 'created_by_name', 'scope', 'created_at']
        read_only_fields = ['created_by', 'created_at']
