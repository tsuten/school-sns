from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Assignment

@receiver(post_save, sender=Assignment)
def assignment_post_save(sender, instance, created, **kwargs):
    """課題が保存された時の処理"""
    if created:
        # 新規作成時の処理
        print(f"新しい課題が作成されました: {instance.title}")
    else:
        # 更新時の処理
        print(f"課題が更新されました: {instance.title}")

@receiver(post_delete, sender=Assignment)
def assignment_post_delete(sender, instance, **kwargs):
    """課題が削除された時の処理"""
    print(f"課題が削除されました: {instance.title}")
