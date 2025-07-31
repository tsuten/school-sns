from django.contrib import admin
from .models import SharedFile, FileCategory
# from .models import FileAccess  # ログ履歴機能を一時的に無効化

# Register your models here.

@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'uploader', 'category', 'file_size_display', 'upload_target', 'created_at']
    list_filter = ['category', 'upload_target_type', 'is_active', 'created_at']
    search_fields = ['original_name', 'description', 'uploader__username']
    readonly_fields = ['file_size', 'file_type', 'checksum', 'created_at', 'updated_at']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'ファイルサイズ'


# ログ履歴機能を一時的に無効化
# @admin.register(FileAccess)
# class FileAccessAdmin(admin.ModelAdmin):
#     list_display = ['file', 'user', 'action', 'created_at']
#     list_filter = ['action', 'created_at']
#     search_fields = ['file__original_name', 'user__username']
#     readonly_fields = ['created_at']