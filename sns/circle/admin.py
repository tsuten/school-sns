from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Circle, CircleMessage, Tag

class TagsWidget(forms.Textarea):
    """タグ入力用のカスタムウィジェット"""
    def __init__(self, attrs=None):
        default_attrs = {
            'rows': 3,
            'cols': 50,
            'placeholder': 'タグをカンマ区切りで入力してください（例：Python, Django, ウェブ開発）'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class CircleAdminForm(forms.ModelForm):
    """Circleモデル用のカスタムフォーム"""
    tags_input = forms.CharField(
        label='タグ',
        required=False,
        widget=TagsWidget(),
        help_text='タグをカンマ区切りで入力してください。新しいタグは自動的に作成されます。'
    )

    class Meta:
        model = Circle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 既存のタグをカンマ区切りの文字列として表示
            existing_tags = self.instance.tags.all()
            if existing_tags:
                self.fields['tags_input'].initial = ', '.join([tag.name for tag in existing_tags])
            else:
                self.fields['tags_input'].initial = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
        
        # カンマ区切りの文字列からタグを作成・関連付け
        tags_string = self.cleaned_data.get('tags_input', '')
        if tags_string:
            # カンマで分割し、空白をトリミングして空でないタグのみを保持
            tag_names = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
            
            # 既存のタグをクリア
            instance.tags.clear()
            
            # タグを作成または取得して関連付け
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        else:
            # タグが空の場合、全ての関連を削除
            instance.tags.clear()
        
        return instance

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'circle_count', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def circle_count(self, obj):
        """このタグを使用しているサークル数"""
        return obj.circles.count()
    circle_count.short_description = 'サークル数'

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    form = CircleAdminForm
    list_display = ('name', 'founder', 'is_public', 'category', 'tags_display', 'member_count', 'banned_count', 'moderator_count', 'created_at', 'updated_at')
    list_filter = ('is_public', 'created_at', 'updated_at', 'category', 'tags')
    search_fields = ('name', 'description', 'founder__username', 'tags__name', 'members__username', 'banned_users__username', 'moderators__username')
    readonly_fields = ('id', 'created_at', 'updated_at', 'tags_display_readonly')
    filter_horizontal = ('members', 'banned_users', 'moderators')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('founder', 'name', 'description', 'is_public', 'category')
        }),
        ('タグ設定', {
            'fields': ('tags_input', 'tags_display_readonly'),
            'description': 'サークルに関連するタグを設定できます。検索やフィルタリングに使用されます。'
        }),
        ('メンバー管理', {
            'fields': ('members',),
            'description': 'サークルの通常メンバーを管理します。'
        }),
        ('モデレーション', {
            'fields': ('moderators', 'banned_users'),
            'description': 'モデレーション権限を持つユーザーとBANされたユーザーを管理します。',
            'classes': ('collapse',)
        }),
        ('システム情報', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        """メンバー数を表示"""
        return obj.members.count()
    member_count.short_description = 'メンバー数'
    
    def banned_count(self, obj):
        """BANされたユーザー数を表示"""
        count = obj.banned_users.count()
        if count > 0:
            return format_html('<span style="color: #d32f2f; font-weight: bold;">{}</span>', count)
        return count
    banned_count.short_description = 'BAN数'
    
    def moderator_count(self, obj):
        """モデレーター数を表示"""
        count = obj.moderators.count()
        if count > 0:
            return format_html('<span style="color: #1976d2; font-weight: bold;">{}</span>', count)
        return count
    moderator_count.short_description = 'モデレーター数'
    
    def tags_display(self, obj):
        """タグを見やすく表示（一覧用）"""
        tags = obj.tags.all()
        if not tags:
            return '-'
        
        tags_html = []
        for tag in tags[:3]:  # 最大3つまで表示
            tags_html.append(f'<span style="background-color: #e3f2fd; padding: 2px 6px; border-radius: 3px; margin-right: 3px; font-size: 11px;">{tag.name}</span>')
        
        if tags.count() > 3:
            tags_html.append(f'<span style="color: #666; font-size: 11px;">+{tags.count() - 3}個</span>')
        
        return format_html(''.join(tags_html))
    tags_display.short_description = 'タグ'
    
    def tags_display_readonly(self, obj):
        """タグを読み取り専用で表示（詳細用）"""
        tags = obj.tags.all()
        if not tags:
            return format_html('<span style="color: #999;">タグが設定されていません</span>')
        
        tags_html = []
        for tag in tags:
            tags_html.append(f'<span style="background-color: #e8f5e8; padding: 4px 8px; border-radius: 4px; margin-right: 5px; margin-bottom: 3px; display: inline-block; border: 1px solid #c8e6c9;">{tag.name}</span>')
        
        return format_html('<div style="max-width: 500px;">{}</div>'.format(''.join(tags_html)))
    tags_display_readonly.short_description = '現在のタグ'
    
    def get_queryset(self, request):
        """クエリセットの最適化"""
        return super().get_queryset(request).select_related('founder').prefetch_related('members', 'banned_users', 'moderators', 'tags')
    
    # カスタムアクション
    actions = ['ban_selected_members', 'unban_selected_users', 'promote_to_moderator', 'demote_from_moderator']
    
    def ban_selected_members(self, request, queryset):
        """選択されたサークルのメンバーをBANする（一括操作用のプレースホルダー）"""
        self.message_user(request, 'この機能は個別のサークル編集画面で実行してください。')
    ban_selected_members.short_description = '選択されたサークルでメンバー管理を行う'
    
    def unban_selected_users(self, request, queryset):
        """選択されたサークルのBANユーザーを解除する"""
        total_unbanned = 0
        for circle in queryset:
            banned_count = circle.banned_users.count()
            circle.banned_users.clear()
            total_unbanned += banned_count
        
        self.message_user(request, f'{total_unbanned}人のBANを解除しました。')
    unban_selected_users.short_description = '選択されたサークルの全BANを解除する'
    
    def promote_to_moderator(self, request, queryset):
        """メンバー管理の詳細情報を表示"""
        self.message_user(request, 'モデレーター昇格は個別のサークル編集画面で実行してください。')
    promote_to_moderator.short_description = 'モデレーター管理画面へ'
    
    def demote_from_moderator(self, request, queryset):
        """選択されたサークルの全モデレーターを解除する"""
        total_demoted = 0
        for circle in queryset:
            moderator_count = circle.moderators.count()
            circle.moderators.clear()
            total_demoted += moderator_count
        
        self.message_user(request, f'{total_demoted}人のモデレーター権限を解除しました。')
    demote_from_moderator.short_description = '選択されたサークルの全モデレーター権限を解除する'

@admin.register(CircleMessage)
class CircleMessageAdmin(admin.ModelAdmin):
    list_display = ('circle', 'user', 'content_preview', 'is_pinned', 'is_edited', 'is_deleted', 'created_at')
    list_filter = ('is_pinned', 'is_edited', 'is_deleted', 'created_at', 'circle')
    search_fields = ('content', 'user__username', 'circle__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('メッセージ情報', {
            'fields': ('circle', 'user', 'content')
        }),
        ('ステータス', {
            'fields': ('is_deleted', 'is_edited')
        }),
        ('ピン設定', {
            'fields': ('is_pinned', 'pinned_at', 'pinned_by'),
            'classes': ('collapse',)
        }),
        ('システム情報', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """メッセージ内容のプレビューを表示（最初の50文字）"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'メッセージ内容'
    
    def get_queryset(self, request):
        """関連オブジェクトを事前に取得してクエリを最適化"""
        return super().get_queryset(request).select_related('user', 'circle', 'pinned_by')
    
    actions = ['mark_as_deleted', 'mark_as_undeleted', 'pin_messages', 'unpin_messages']
    
    def mark_as_deleted(self, request, queryset):
        """選択したメッセージを削除済みにマーク"""
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f'{updated}件のメッセージを削除済みにしました。')
    mark_as_deleted.short_description = '選択したメッセージを削除済みにする'
    
    def mark_as_undeleted(self, request, queryset):
        """選択したメッセージの削除を解除"""
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f'{updated}件のメッセージの削除を解除しました。')
    mark_as_undeleted.short_description = '選択したメッセージの削除を解除する'
    
    def pin_messages(self, request, queryset):
        """選択したメッセージをピンする"""
        from django.utils import timezone
        updated = queryset.update(is_pinned=True, pinned_at=timezone.now(), pinned_by=request.user)
        self.message_user(request, f'{updated}件のメッセージをピンしました。')
    pin_messages.short_description = '選択したメッセージをピンする'
    
    def unpin_messages(self, request, queryset):
        """選択したメッセージのピンを解除"""
        updated = queryset.update(is_pinned=False, pinned_at=None, pinned_by=None)
        self.message_user(request, f'{updated}件のメッセージのピンを解除しました。')
    unpin_messages.short_description = '選択したメッセージのピンを解除する'