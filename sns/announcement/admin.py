from django.contrib import admin
from .models import Announcement

# Register your models here.
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'priority', 'is_pinned', 'is_deleted', 'created_at', 'get_schools', 'get_classes')
    list_filter = ('priority', 'is_pinned', 'is_deleted', 'created_at', 'posted_by')
    search_fields = ('title', 'content', 'posted_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('id', 'title', 'posted_by', 'content')
        }),
        ('設定', {
            'fields': ('priority', 'is_pinned', 'is_deleted')
        }),
        ('配信先', {
            'fields': ('posted_to_school', 'posted_to_class')
        }),
        ('既読者', {
            'fields': ('read',),
            'classes': ('collapse',)
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ('posted_to_school', 'posted_to_class', 'read')
    
    def get_schools(self, obj):
        return ', '.join([school.name for school in obj.posted_to_school.all()]) or '未設定'
    get_schools.short_description = '配信先学校'
    
    def get_classes(self, obj):
        return ', '.join([f"{cls.school.name} - {cls.name}" for cls in obj.posted_to_class.all()]) or '未設定'
    get_classes.short_description = '配信先クラス'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('posted_by').prefetch_related('posted_to_school', 'posted_to_class')
