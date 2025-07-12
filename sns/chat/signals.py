from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassMessage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=ClassMessage)
def send_class_message(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        
        # グループ名を作成（コンシューマーと同じ形式）
        group_name = f"class_{instance.class_id.id}"
        
        # WebSocketグループにメッセージを送信
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'class_message',
                'data': {
                    'id': str(instance.id),
                    'sender': {
                        'id': str(instance.sender.id) if instance.sender else None,
                        'username': instance.sender.username if instance.sender else 'Unknown'
                    },
                    'content': instance.content,
                    'class_id': str(instance.class_id.id),
                    'created_at': instance.created_at.isoformat(),
                    'is_deleted': instance.is_deleted
                }
            }
        )
