"""
数据字典URL配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DictionaryTypeViewSet, DictionaryItemViewSet

router = DefaultRouter()
router.register(r"types", DictionaryTypeViewSet, basename="dictionary-type")
router.register(r"items", DictionaryItemViewSet, basename="dictionary-item")

urlpatterns = [
    path("", include(router.urls)),
]
