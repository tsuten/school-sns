from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Announcement
from websocket.unified_consumers import send_to_group

@receiver(post_save, sender=Announcement)
def send_to_announcements_group(sender, instance, created, **kwargs):
    from websocket.unified_consumers import send_to_group
    import asyncio
    
    # 非同期関数を同期的に呼び出し
    asyncio.run(send_to_group(
        "announcements_" + str(instance.post_to), 
        "announcement", 
        {
            "announcement_id": str(instance.id),
            "title": instance.title,
            "content": instance.content,
            "priority": instance.priority,
            "posted_by": str(instance.posted_by.id),
            "post_to": str(instance.post_to),
            "is_pinned": instance.is_pinned,
            "is_deleted": instance.is_deleted,
            "created_at": instance.created_at.isoformat()
        }
    ))