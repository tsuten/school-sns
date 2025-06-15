from django.contrib import admin
from .models import Poll, Choice, Vote

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    max_num = 5  # 最大5つまで
    readonly_fields = ('id', 'vote_count', 'created_at', 'updated_at')
    fields = ('choice_text', 'vote_count', 'created_at')
    
    def get_max_num(self, request, obj=None, **kwargs):
        """動的に最大数を制御"""
        if obj:
            existing_count = obj.poll_choices.count()
            return max(5, existing_count)  # 既に5つ以上ある場合は現在の数を維持
        return 5

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_choices_count', 'get_choices_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('question',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [ChoiceInline]  # インライン編集を追加
    
    def get_choices_count(self, obj):
        """選択肢の数を表示"""
        return obj.poll_choices.count()
    get_choices_count.short_description = '選択肢数'
    get_choices_count.admin_order_field = 'poll_choices__count'
    
    def get_choices_preview(self, obj):
        """選択肢のプレビューを表示（最初の3つまで）"""
        choices = obj.poll_choices.all()[:3]
        choice_texts = [choice.choice_text for choice in choices]
        preview = ', '.join(choice_texts)
        if obj.poll_choices.count() > 3:
            preview += f' ... (+{obj.poll_choices.count() - 3}個)'
        return preview or '選択肢なし'
    get_choices_preview.short_description = '選択肢'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'poll', 'vote_count', 'created_at')
    list_filter = ('poll', 'created_at')
    search_fields = ('choice_text', 'poll__question')
    readonly_fields = ('id', 'vote_count', 'created_at', 'updated_at')
    list_select_related = ('poll',)  # パフォーマンス向上のため

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_poll', 'choice', 'created_at')
    list_filter = ('choice__poll', 'created_at')
    search_fields = ('user__username', 'choice__poll__question', 'choice__choice_text')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_select_related = ('user', 'choice', 'choice__poll')  # パフォーマンス向上のため
    
    def get_poll(self, obj):
        """choice経由でpoll情報を取得"""
        return obj.choice.poll.question
    get_poll.short_description = 'Poll'
    get_poll.admin_order_field = 'choice__poll__question'