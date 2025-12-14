from django.contrib import admin
from .models import DictionaryType, DictionaryItem


class DictionaryItemInline(admin.TabularInline):
    model = DictionaryItem
    extra = 1
    fields = ["value", "label", "sort_order", "is_active", "description"]


@admin.register(DictionaryType)
class DictionaryTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_system", "is_active", "created_at"]
    list_filter = ["is_system", "is_active"]
    search_fields = ["code", "name"]
    inlines = [DictionaryItemInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DictionaryItem)
class DictionaryItemAdmin(admin.ModelAdmin):
    list_display = ["dict_type", "value", "label", "sort_order", "is_active"]
    list_filter = ["dict_type", "is_active"]
    search_fields = ["value", "label"]
    readonly_fields = ["created_at", "updated_at"]
