from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile, UserSettings

# thanks claude for writing this code <33
# also i don't know if this works properly  
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')

class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('username', 'email')
    ordering = ('username',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'created_at')
    search_fields = ('user__username', 'display_name')
    list_filter = ('created_at',)

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_dark_mode_enabled', 'is_notification_enabled', 'is_profile_public', 'is_birthday_public', 'is_location_public', 'is_activity_public')
    search_fields = ('user__username',)
    list_filter = ('created_at', 'is_dark_mode_enabled', 'is_notification_enabled', 'is_profile_public')
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('テーマ設定', {
            'fields': ('is_dark_mode_enabled',),
            'description': 'ユーザーの表示テーマに関する設定'
        }),
        ('通知設定', {
            'fields': ('is_notification_enabled',),
            'description': 'ユーザーの通知に関する設定'
        }),
        ('プライバシー設定', {
            'fields': ('is_profile_public', 'is_birthday_public', 'is_location_public', 'is_activity_public'),
            'description': 'ユーザーのプライバシーに関する設定'
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'システムによって自動的に管理される情報'
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)