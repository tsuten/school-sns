from django.contrib import admin
from django.utils.html import format_html
from .models import Emoji


@admin.register(Emoji)
class EmojiAdmin(admin.ModelAdmin):
    list_display = ('emoji_display', 'name', 'circle', 'slug', 'created_at')
    list_filter = ('circle', 'created_at')
    search_fields = ('name', 'slug', 'circle__name')
    list_per_page = 50
    ordering = ('circle', 'name')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'circle', 'image')
        }),
        ('自動生成フィールド', {
            'fields': ('slug',),
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

    def get_queryset(self, request):
        """クエリセットの最適化"""
        return super().get_queryset(request).select_related('circle')