from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Class, School, Organization

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'grade_number', 'class_number', 'has_logo', 'get_managers_count', 'get_students_count', 'created_at')
    list_filter = ('school', 'grade_number', 'class_number', 'created_at')
    search_fields = ('name', 'school__name', 'grade_number', 'class_number', 'managers__username', 'members__username')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'school', 'grade_number', 'class_number'),
            'description': 'クラスの基本情報'
        }),
        ('ロゴ・画像', {
            'fields': ('logo', 'logo_preview'),
            'description': 'クラスのロゴ画像'
        }),
        ('管理者・学生', {
            'fields': ('managers', 'members'),
            'description': 'クラスの管理者と学生（メンバー）'
        }),
        ('システム情報', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'システムによって自動的に管理される情報'
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'logo_preview')
    filter_horizontal = ('managers', 'members')
    
    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'ロゴあり'
    
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" height="100" style="object-fit: cover;" />')
        return "ロゴなし"
    logo_preview.short_description = 'ロゴプレビュー'
    
    def get_managers_count(self, obj):
        return obj.managers.count()
    get_managers_count.short_description = '管理者数'
    
    def get_students_count(self, obj):
        return obj.members.count()
    get_students_count.short_description = '学生数'

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone', 'email', 'has_logo', 'get_managers_count', 'get_classes_count', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('name', 'location', 'phone', 'email', 'managers__username')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'location'),
            'description': '学校の基本情報'
        }),
        ('ロゴ・画像', {
            'fields': ('logo', 'logo_preview'),
            'description': '学校のロゴ画像'
        }),
        ('連絡先情報', {
            'fields': ('phone', 'email', 'website'),
            'description': '学校の連絡先情報'
        }),
        ('管理者', {
            'fields': ('managers',),
            'description': '学校の管理者'
        }),
        ('システム情報', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'システムによって自動的に管理される情報'
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'logo_preview')
    filter_horizontal = ('managers',)
    
    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = 'ロゴあり'
    
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" height="100" style="object-fit: cover;" />')
        return "ロゴなし"
    logo_preview.short_description = 'ロゴプレビュー'
    
    def get_managers_count(self, obj):
        return obj.managers.count()
    get_managers_count.short_description = '管理者数'
    
    def get_classes_count(self, obj):
        return obj.class_set.count()
    get_classes_count.short_description = 'クラス数'

admin.site.register(Class, ClassAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Organization)
