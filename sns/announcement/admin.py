from django.contrib import admin
from .models import Announcement
from .forms import AnnouncementForm

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    AnnouncementモデルのDjango管理画面設定
    """
    # カスタムフォームを使用して、配信先の選択ロジックを実装します
    form = AnnouncementForm

    # 一覧ページの表示設定
    list_display = ('title', 'posted_by', 'priority', 'is_pinned', 'created_at', 'get_schools_display', 'get_classes_display')
    list_filter = ('priority', 'is_pinned', 'is_deleted', 'created_at')
    search_fields = ('title', 'content', 'posted_by__username')
    ordering = ('-created_at',)

    # 編集ページのレイアウト設定
    fieldsets = (
        (None, {
            'fields': ('title', 'content') # posted_by を削除
        }),
        ('配信先設定', {
            'description': "配信先の種類を選択し、対応する学校またはクラスを指定してください。",
            'fields': ('post_to_type', 'target_school', 'target_class'),
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
        1. フォームからインスタンスを作成するが、DBにはまだ保存しない。
        2. posted_by に現在ログイン中のユーザーを設定する。
        3. モデルのバリデーションをバイパスして、まずインスタンスをDBに保存する。
        4. フォームで選択された配信先(M2M)を設定する。
        """
        # 1. フォームのデータでインスタンスを作成
        instance = form.save(commit=False)
        
        # 2. 投稿者を現在のユーザーに設定
        instance.posted_by = request.user
        
        # 3. モデルのsave()をバイパスして保存（NOT NULL制約とM2M検証を回避）
        super(Announcement, instance).save()

        # 4. 配信先(M2M)を設定
        post_type = form.cleaned_data.get('post_to_type')
        school = form.cleaned_data.get('target_school')
        class_ = form.cleaned_data.get('target_class')

        instance.posted_to_school.clear()
        instance.posted_to_class.clear()

        if post_type == 'school':
            instance.posted_to_school.add(school)
        elif post_type == 'class':
            instance.posted_to_class.add(class_)

    @admin.display(description='配信先学校')
    def get_schools_display(self, obj):
        return ", ".join([school.name for school in obj.posted_to_school.all()]) or "ー"

    @admin.display(description='配信先クラス')
    def get_classes_display(self, obj):
        return ", ".join([cls.name for cls in obj.posted_to_class.all()]) or "ー"
    
    def get_queryset(self, request):
        # パフォーマンス向上のために関連オブジェクトをプリフェッチ
        return super().get_queryset(request).prefetch_related('posted_to_school', 'posted_to_class').select_related('posted_by')