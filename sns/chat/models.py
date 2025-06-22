from django.db import models
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
class MessageManager(models.Manager):
    def get_from_sender(self, sender_id):
        return self.filter(sender_id=sender_id)
    
    def get_from_receiver(self, receiver_id):
        return self.filter(receiver_id=receiver_id)
    
    def get_between_users(self, user1, user2):
        return self.filter(Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1))
    
    def get_messages_between_users(self, user1, user2, before_date, get_amount):
        messages = self.filter(Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1))
        messages = messages.filter(created_at__lte=before_date, is_deleted=False)
        messages = messages.order_by('-created_at')
        messages = messages[:get_amount]
        return messages
    
    def get_unread_count(self, user):
        """指定ユーザーの未読メッセージ数を取得"""
        return self.filter(receiver=user, is_read=False, is_deleted=False).count()
    
    def get_latest_message_between_users(self, user1, user2):
        """2人のユーザー間の最新メッセージを取得"""
        return self.filter(
            Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1),
            is_deleted=False
        ).order_by('-created_at').first()


# Create your models here.
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    objects = MessageManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_read']),
        ]

    def delete_message(self):
        self.is_deleted = True
        self.save()

    def restore_message(self):
        self.is_deleted = False
        self.save()
    
    def mark_as_read(self):
        """メッセージを既読にする"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def clean(self):
        if self.sender == self.receiver:
            raise ValidationError("sender and receiver cannot be the same")

    def save(self, *args, **kwargs):
        self.clean()
        super(Message, self).save(*args, **kwargs)

    def __str__(self):
        return self.content