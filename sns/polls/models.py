from django.db import models
from django.conf import settings
import uuid
from django.db.models import Sum
from django.core.exceptions import ValidationError

class PollManager(models.Manager):
    def create_poll(self, question, choices):
        if len(choices) > 5:
            raise ValidationError('投票には最大5つまでの選択肢しか設定できません。')
        if len(choices) < 2:
            raise ValidationError('投票には最低2つの選択肢が必要です。')
        
        poll = self.model(question=question)
        poll.save()
        for choice in choices:
            Choice.objects.create(poll=poll, choice_text=choice)
        return poll

class Poll(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    question = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PollManager()

    def __str__(self):
        return self.question

class Choice(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll_choices')
    choice_text = models.CharField(max_length=200)
    vote_count = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 新規作成の場合のみチェック
        if not self.pk:
            existing_choices_count = Choice.objects.filter(poll=self.poll).count()
            if existing_choices_count >= 5:
                raise ValidationError(f'投票「{self.poll.question}」には既に5つの選択肢があります。これ以上追加できません。')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.choice_text
    
# logic complicated, idk what i'm doing here
class VoteManager(models.Manager):
    def get_total_vote_count(self, choice):
        return self.filter(choice=choice).count()
    
class Vote(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_votes')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='choice_votes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VoteManager()

    class Meta:
        unique_together = ('user', 'choice')  # 同じユーザーが同じ選択肢に重複投票を防ぐ

    def __str__(self):
        return f"{self.choice.poll.question} - {self.choice.choice_text}"