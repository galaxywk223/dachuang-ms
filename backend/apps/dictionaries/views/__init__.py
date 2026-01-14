"""
数据字典视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore[import-untyped]
from rest_framework.filters import SearchFilter

from ..models import DictionaryType, DictionaryItem
from ..serializers import (
    DictionaryTypeSerializer,
    DictionaryTypeDetailSerializer,
    DictionaryItemSerializer,
    DictionaryItemSimpleSerializer,
    DictionaryBatchSerializer,
    DictionaryItemBulkSerializer,
)
from apps.users.permissions import IsLevel1Admin


class DictionaryTypeViewSet(viewsets.ModelViewSet):
    """
    数据字典类型视图集
    提供字典类型的CRUD操作和批量获取接口
    """

    queryset = DictionaryType.objects.filter(is_active=True)
    serializer_class = DictionaryTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["is_system", "is_active"]
    search_fields = ["code", "name"]

    def get_permissions(self):
        """
        GET请求只需认证，修改操作需要一级管理员权限
        """
        if self.action in ["list", "retrieve", "by_code", "batch", "all_dictionaries"]:
            return [IsAuthenticated()]
        return [IsLevel1Admin()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DictionaryTypeDetailSerializer
        return DictionaryTypeSerializer

    def destroy(self, request, *args, **kwargs):
        """
        删除字典类型（系统内置类型不可删除）
        """
        instance = self.get_object()
        if instance.is_system:
            return Response(
                {"detail": "系统内置字典类型不可删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="by-code/(?P<code>[^/.]+)")
    def by_code(self, request, code=None):
        """
        根据编码获取字典类型及其条目
        GET /api/dictionaries/types/by-code/{code}/
        """
        try:
            dict_type = DictionaryType.objects.prefetch_related("items").get(
                code=code, is_active=True
            )
        except DictionaryType.DoesNotExist:
            return Response(
                {"detail": f"字典类型 '{code}' 不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 只返回启用的条目
        items = dict_type.items.filter(is_active=True).order_by("sort_order", "id")
        serializer = DictionaryItemSimpleSerializer(items, many=True)

        return Response(
            {
                "code": dict_type.code,
                "name": dict_type.name,
                "items": serializer.data,
            }
        )

    @action(detail=False, methods=["post"], url_path="batch")
    def batch(self, request):
        """
        批量获取多个字典类型的数据
        POST /api/dictionaries/types/batch/
        Body: {"codes": ["project_level", "project_category"]}
        """
        serializer = DictionaryBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        codes = serializer.validated_data["codes"]
        result = {}

        dict_types = DictionaryType.objects.prefetch_related("items").filter(
            code__in=codes, is_active=True
        )

        for dict_type in dict_types:
            items = dict_type.items.filter(is_active=True).order_by("sort_order", "id")
            result[dict_type.code] = {
                "name": dict_type.name,
                "items": DictionaryItemSimpleSerializer(items, many=True).data,
            }

        return Response(result)

    @action(detail=False, methods=["get"], url_path="all")
    def all_dictionaries(self, request):
        """
        获取所有字典数据（用于前端初始化缓存）
        GET /api/dictionaries/types/all/
        """
        dict_types = DictionaryType.objects.prefetch_related("items").filter(
            is_active=True
        )

        result = {}
        for dict_type in dict_types:
            items = dict_type.items.filter(is_active=True).order_by("sort_order", "id")
            result[dict_type.code] = {
                "name": dict_type.name,
                "items": DictionaryItemSimpleSerializer(items, many=True).data,
            }

        return Response(result)


class DictionaryItemViewSet(viewsets.ModelViewSet):
    """
    数据字典条目视图集
    """

    queryset = DictionaryItem.objects.select_related("dict_type")
    serializer_class = DictionaryItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["dict_type", "is_active"]
    search_fields = ["value", "label"]

    def get_permissions(self):
        """
        GET请求只需认证，修改操作需要一级管理员权限
        """
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsLevel1Admin()]

    def get_queryset(self):
        queryset = super().get_queryset()
        dict_type_code = self.request.query_params.get("dict_type_code")
        if dict_type_code:
            queryset = queryset.filter(dict_type__code=dict_type_code)
        return queryset

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_create(self, request):
        """
        批量导入字典条目
        POST /api/dictionaries/items/bulk/
        Body: { dict_type: 1 | dict_type_code: "college", items: [{label, value}] }
        """
        dict_type_id = request.data.get("dict_type")
        dict_type_code = request.data.get("dict_type_code")
        if not dict_type_id and not dict_type_code:
            return Response(
                {"detail": "缺少字典类型参数"}, status=status.HTTP_400_BAD_REQUEST
            )

        if dict_type_id:
            dict_type = DictionaryType.objects.filter(id=dict_type_id).first()
        else:
            dict_type = DictionaryType.objects.filter(code=dict_type_code).first()

        if not dict_type:
            return Response(
                {"detail": "字典类型不存在"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = DictionaryItemBulkSerializer(
            data=request.data.get("items", []), many=True
        )
        serializer.is_valid(raise_exception=True)

        existing_values = set(
            DictionaryItem.objects.filter(dict_type=dict_type).values_list(
                "value", flat=True
            )
        )
        max_sort = (
            DictionaryItem.objects.filter(dict_type=dict_type).aggregate(
                Max("sort_order")
            )["sort_order__max"]
            or 0
        )

        created_count = 0
        skipped_count = 0
        for item in serializer.validated_data:
            label = item.get("label", "").strip()
            value = (item.get("value") or label).strip()
            if not label or not value:
                skipped_count += 1
                continue
            if value in existing_values:
                skipped_count += 1
                continue
            max_sort += 1
            DictionaryItem.objects.create(
                dict_type=dict_type,
                label=label,
                value=value,
                description=item.get("description", ""),
                extra_data=item.get("extra_data") or {},
                sort_order=max_sort,
                is_active=True,
            )
            existing_values.add(value)
            created_count += 1

        return Response(
            {"created": created_count, "skipped": skipped_count},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="clear")
    def clear_items(self, request):
        """
        清空字典条目
        POST /api/dictionaries/items/clear/
        Body: { dict_type: 1 | dict_type_code: "college" }
        """
        dict_type_id = request.data.get("dict_type")
        dict_type_code = request.data.get("dict_type_code")
        if not dict_type_id and not dict_type_code:
            return Response(
                {"detail": "缺少字典类型参数"}, status=status.HTTP_400_BAD_REQUEST
            )

        if dict_type_id:
            dict_type = DictionaryType.objects.filter(id=dict_type_id).first()
        else:
            dict_type = DictionaryType.objects.filter(code=dict_type_code).first()

        if not dict_type:
            return Response(
                {"detail": "字典类型不存在"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            deleted_count, _ = DictionaryItem.objects.filter(
                dict_type=dict_type
            ).delete()
        except ProtectedError:
            return Response(
                {"detail": "存在被引用的条目，无法清空"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)
