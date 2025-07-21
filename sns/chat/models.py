from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from shared.abstract_models import AbstractBaseModel
from .decorators import send_message_signal

class AbstractBaseMessage(AbstractBaseModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sender')
    content = models.TextField()

    class Meta:
        abstract = True



# 個人メッセージ
class PrivateMessageManager(models.Manager):

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
        from django.db.models import Q
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
                
                # UserProfileを通してpfpを取得
                try:
                    pfp_url = other_user.profile.pfp.url if other_user.profile.pfp else None
                    display_name = other_user.profile.display_name
                except:
                    pfp_url = None
                    display_name = other_user.username
                
                result.append({
                    'user_id': other_user_id,
                    'user': {
                        'id': other_user.id,
                        'user_username': other_user.username,
                        'display_name': display_name,
                        'pfp': pfp_url,
                    },
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

    @send_message_signal('post')
    def send_message(self, sender, receiver, content):
        """メッセージを送信するメソッド"""
        message = self.create(
            sender=sender,
            receiver=receiver,
            content=content
        )
        return message

    @send_message_signal('update')
    def update_message(self, message_id, **kwargs):
        """メッセージを更新するメソッド"""
        message = self.get(id=message_id)
        for key, value in kwargs.items():
            setattr(message, key, value)
        message.save()
        return message

    @send_message_signal('update')
    def update_message_content(self, message_id, content):
        """メッセージの内容を更新するメソッド"""
        message = self.get(id=message_id)
        message.content = content
        message.save()
        return message

    @send_message_signal('update')
    def update_message_read_status(self, message_id, is_read=True):
        """メッセージの既読状態を更新するメソッド"""
        message = self.get(id=message_id)
        message.is_read = is_read
        if is_read:
            message.read_at = timezone.now()
        else:
            message.read_at = None
        message.save()
        return message

    @send_message_signal('update')
    def update_message_deleted_status(self, message_id, is_deleted=True):
        """メッセージの削除状態を更新するメソッド"""
        message = self.get(id=message_id)
        message.is_deleted = is_deleted
        if is_deleted:
            message.deleted_at = timezone.now()
        message.save()
        return message

    @send_message_signal('restore')
    def restore_message(self, message_id):
        """削除されたメッセージを復元するメソッド"""
        message = self.get(id=message_id)
        message.is_deleted = False
        message.deleted_at = None
        message.save()
        return message

    @send_message_signal('delete')
    def delete_message(self, message_id):
        """メッセージを論理削除するメソッド"""
        message = self.get(id=message_id)
        message.is_deleted = True
        message.save()
        return message

    @send_message_signal('update')
    def mark_message_as_read(self, message_id):
        """メッセージを既読にするメソッド"""
        message = self.get(id=message_id)
        if message.is_read:
            raise ValidationError("Message is already read")
        
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
        return message


# Create your models here.
class PrivateMessage(AbstractBaseMessage):
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='receiver')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    objects = PrivateMessageManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_read']),
        ]

    def mark_as_read(self):
        if self.is_read:
            raise ValidationError("Message is already read")
        
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def clean(self):
        if self.sender == self.receiver:
            raise ValidationError("sender and receiver cannot be the same")

    def save(self, *args, **kwargs):
        self.clean()
        super(PrivateMessage, self).save(*args, **kwargs)

    def __str__(self):
        return self.content
    