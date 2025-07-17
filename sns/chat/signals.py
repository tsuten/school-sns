from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassMessage, Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.models import UserProfile

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

@receiver(post_save, sender=Message)
def send_to_user(sender, instance, created, **kwargs):
    from websocket.unified_consumers import send_to_user
    import asyncio

    sender_profile = UserProfile.objects.get_userdata_and_profile(instance.sender.id)
        
    # 非同期関数を同期的に呼び出し
    asyncio.run(send_to_user(
        instance.receiver.id, 
        "message", 
        {
            "id": str(instance.id),
            "sender": {
                "id": str(instance.sender.id),
                "pfp": str(sender_profile[1].pfp),
                "display_name": sender_profile[1].display_name,
                "username": instance.sender.username
            },
            "content": instance.content,
            "created_at": instance.created_at.isoformat(),
            "is_deleted": instance.is_deleted,
        }
    ))