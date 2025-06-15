from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Poll, Choice, Vote

# fuck this fucking signal, i don't think this works well
# lucky if this works
@receiver(post_save, sender=Vote)
def update_vote_count_on_save(sender, instance, created, **kwargs):
    """投票が作成または更新された時に選択肢の投票数を更新"""
    choice = instance.choice
    choice.vote_count = choice.choice_votes.count()
    choice.save()

@receiver(post_delete, sender=Vote)
def update_vote_count_on_delete(sender, instance, **kwargs):
    """投票が削除された時に選択肢の投票数を更新"""
    choice = instance.choice
    choice.vote_count = choice.choice_votes.count()
    choice.save()