from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .consumers import NotificationConsumer

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        print("通知の送信イベントが発火されました")
        
        # チャンネルレイヤーを取得
        channel_layer = get_channel_layer()
        
        # 特定ユーザーの通知グループに送信
        user_group_name = f"notifications_{instance.user.id}"

        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'send_notification',
                'notification_type': instance.type,
                'message': instance.content,
                'user_id': str(instance.user.id),
                'notification_id': str(instance.id),
                'is_read': instance.is_read,
                'created_at': instance.created_at.isoformat()
            }
        )