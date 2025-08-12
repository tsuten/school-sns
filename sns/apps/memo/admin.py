from django.contrib import admin
from .models import Memo

@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    """メモモデルの管理者画面設定"""
    list_display = ('title', 'user', 'created_at', 'updated_at', 'is_deleted')
    list_filter = ('is_deleted', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('基本情報', {
            'fields': ('id', 'user', 'title', 'content')
        }),
        ('システム情報', {
            'fields': ('is_deleted', 'deleted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """削除されたメモも表示"""
        return super().get_queryset(request)
    
    def has_delete_permission(self, request, obj=None):
        """物理削除の権限を制限"""
        return False
