from django.contrib import admin
from .models import PrivateMessage, RoomMessage
from .signals import send_message_post_signal

class PrivateMessageAdmin(admin.ModelAdmin):
    """PrivateMessageの管理画面設定"""
    
    list_display = ['id', 'sender', 'receiver', 'content', 'created_at', 'is_deleted']
    list_filter = ['created_at', 'is_deleted']
    search_fields = ['content', 'sender__username', 'receiver__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        """モデル保存時にシグナルを送信"""
        # 元のsave_modelを実行
        super().save_model(request, obj, form, change)
        
        # 新規作成の場合のみシグナルを送信
        if not change:  # change=Falseは新規作成を意味する
            send_message_post_signal(obj)

# Register your models here.
admin.site.register(PrivateMessage, PrivateMessageAdmin)
admin.site.register(RoomMessage)