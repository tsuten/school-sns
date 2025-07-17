from django.db import models
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from enrollments.models import Class

class BaseMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sender')
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def delete_message(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore_message(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()


# 個人メッセージ
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
    
    def get_list_of_users_have_history_with_user(self, user):
        """指定ユーザーとメッセージを交信したユーザーのリストを最新メッセージ情報と共に取得"""
        from django.db.models import Q, Max, Case, When, Value, CharField
        from users.models import User
        
        # 送信したメッセージの受信者を取得
        sent_to_users = self.filter(
            sender=user, is_deleted=False
        ).values_list('receiver', flat=True).distinct()
        
        # 受信したメッセージの送信者を取得
        received_from_users = self.filter(
            receiver=user, is_deleted=False
        ).values_list('sender', flat=True).distinct()
        
        # 重複を除いてユーザーIDのセットを作成し、Noneと現在のユーザーを除外
        user_ids = set(sent_to_users) | set(received_from_users)
        user_ids.discard(None)  # null値を除外
        user_ids.discard(user.id)  # 現在のユーザーを除外
        
        if not user_ids:
            return []
        
        # 各ユーザーとの最新メッセージを取得
        result = []
        for other_user_id in user_ids:
            # 該当ユーザーとの最新メッセージを取得
            latest_message = self.filter(
                Q(sender=user, receiver_id=other_user_id) | 
                Q(sender_id=other_user_id, receiver=user),
                is_deleted=False
            ).order_by('-created_at').first()
            
            if latest_message:
                # ユーザー情報を取得
                try:
                    other_user = User.objects.get(id=other_user_id)
                except User.DoesNotExist:
                    continue
                
                result.append({
                    'user_id': other_user_id,
                    'user': other_user,
                    'latest_message': {
                        'content': latest_message.content,
                        'created_at': latest_message.created_at,
                        'sender_id': latest_message.sender.id,
                        'is_sent_by_me': latest_message.sender.id == user.id,
                        'is_read': latest_message.is_read
                    }
                })
        
        # 最新メッセージの日時で降順ソート
        result.sort(key=lambda x: x['latest_message']['created_at'], reverse=True)
        
        return result


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
    
class ClassMessageManager(models.Manager):
    def get_messages_by_class_id(self, class_id):
        return self.filter(class_id=class_id)
    
class ClassMessage(BaseMessage):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)

    objects = ClassMessageManager()

    def __str__(self):
        return self.content