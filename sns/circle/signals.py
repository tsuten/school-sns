from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Circle


@receiver(post_save, sender=Circle)
def add_founder_to_members(sender, instance, created, **kwargs):
    """サークル作成時に創始者をメンバーに自動追加"""
    if created and instance.founder:
        instance.members.add(instance.founder)
