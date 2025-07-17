from django.contrib import admin
from .models import Announcement
from .forms import AnnouncementForm
from enrollments.models import School, Class

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    AnnouncementモデルのDjango管理画面設定
    """
    # カスタムフォームを使用
    form = AnnouncementForm

    # 一覧ページの表示設定
    list_display = ('title', 'posted_by', 'priority', 'is_pinned', 'created_at', 'get_post_to_display')
    list_filter = ('priority', 'is_pinned', 'is_deleted', 'created_at')
    search_fields = ('title', 'content', 'posted_by__username')
    ordering = ('-created_at',)

    # 編集ページのレイアウト設定
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('配信先設定', {
            'description': "配信先の学校またはクラスを選択してください。",
            'fields': ('post_to_selection',),
        }),
        ('オプション', {
            'fields': ('priority', 'is_pinned', 'is_deleted'),
        }),
        ('既読情報', {
            'classes': ('collapse',),
            'fields': ('read',),
        }),
        ('タイムスタンプ', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    # 読み取り専用フィールド
    readonly_fields = ('created_at', 'updated_at')
    
    # ManyToManyフィールドを使いやすくするための設定
    filter_horizontal = ('read',)

    def save_model(self, request, obj, form, change):
        """
        カスタム保存ロジック:
        posted_byに現在のユーザーを設定してから保存
        """
        # posted_byを現在のユーザーに設定
        obj.posted_by = request.user
        
        # フォームで処理済みのpost_toを使用して保存
        obj.save()

    @admin.display(description='配信先')
    def get_post_to_display(self, obj):
        """配信先を表示（学校またはクラス）"""
        if not obj.post_to:
            return "未設定"
        
        try:
            # まず学校として検索
            school = School.objects.filter(id=obj.post_to).first()
            if school:
                return f"学校: {school.name}"
            
            # 次にクラスとして検索
            class_obj = Class.objects.filter(id=obj.post_to).first()
            if class_obj:
                return f"クラス: {class_obj.name}"
            
            return "不明な配信先"
        except:
            return "エラー"
    
    def get_queryset(self, request):
        # パフォーマンス向上のために関連オブジェクトを取得
        return super().get_queryset(request).select_related('posted_by')