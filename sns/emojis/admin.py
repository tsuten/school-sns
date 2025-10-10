from django.contrib import admin
from django.utils.html import format_html
from .models import Emoji


@admin.register(Emoji)
class EmojiAdmin(admin.ModelAdmin):
    list_display = ('emoji_display', 'name', 'organization_type', 'organization_name', 'created_by', 'created_at')
    list_filter = ('organization_type', 'content_type', 'created_at')
    search_fields = ('name', 'slug', 'organization_type')
    list_per_page = 50
    ordering = ('organization_type', 'name')
    readonly_fields = ('slug', 'organization_type', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'created_by', 'image')
        }),
        ('組織設定', {
            'fields': ('content_type', 'object_id'),
            'description': 'GenericForeignKeyで組織を指定します。organization_typeは自動設定されます。'
        }),
        ('自動生成フィールド', {
            'fields': ('slug', 'organization_type'),
            'classes': ('collapse',)
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def emoji_display(self, obj):
        """絵文字画像またはアイコンを表示"""
        if obj.image:
            return format_html(
                '<img src="{}" width="30" height="30" style="object-fit: contain;" /> {}',
                obj.image.url,
                obj.name
            )
        else:
            return format_html(
                '<span style="font-size: 20px;">🎭</span> {}',
                obj.name
            )
    
    emoji_display.short_description = '絵文字'
    emoji_display.admin_order_field = 'name'

    def organization_name(self, obj):
        """組織名を表示"""
        return obj.organization_name
    organization_name.short_description = '組織名'
    
    def get_queryset(self, request):
        """クエリセットの最適化"""
        return super().get_queryset(request).select_related('created_by', 'content_type')