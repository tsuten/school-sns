from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from shared.abstract_models import AbstractBaseModel
from .decorators import send_message_signal
from apps.core.organizations.models import OrganizationType

class AbstractBaseMessage(AbstractBaseModel):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='%(class)s_sent'  # 動的related_name（private_message_sent, room_message_sent）
    )
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
        from apps.core.users.models import User
        
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
                    from apps.core.users.models import User
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
    
class RoomType(models.TextChoices):
    CLASS = OrganizationType.CLASS
    SCHOOL = OrganizationType.SCHOOL  
    CIRCLE = OrganizationType.CIRCLE
    GROUP = "group", "グループ"

class RoomMessageManager(models.Manager):
    def get_messages_from_room(self, user, room_type, room_id, before_date=None, limit=50):
        if not self.validate_room_exists(room_type, room_id):
            raise ValidationError(f"Room {room_type}:{room_id} does not exist")
        
        try:
            messages = self.filter(room_type=room_type, room_id=room_id, is_deleted=False)
            if before_date:
                messages = messages.filter(created_at__lte=before_date)
            messages = messages.order_by('-created_at')[:limit]
            print(f"messages: {messages}")
            return messages
        except Exception as e:
            raise ValidationError(f"メッセージの取得に失敗しました: {str(e)}")
    
    def validate_room_exists(self, room_type, room_id):
        """部屋の存在確認（統一API使用）"""
        if room_type == RoomType.GROUP:
            return True  # グループは常にOK
            
        try:
            if room_type == RoomType.CLASS:
                from apps.core.organizations.models import Class
                return Class.objects.filter(id=room_id).exists()
            elif room_type == RoomType.SCHOOL:
                from apps.core.organizations.models import School
                return School.objects.filter(id=room_id).exists()
            elif room_type == RoomType.CIRCLE:
                from circle.models import Circle
                return Circle.objects.filter(id=room_id).exists()
            else:
                return False
        except Exception:
            return False  # エラー時は存在しないとみなす
    
    def can_user_access_room(self, user, room_type, room_id):
        """ユーザーがルームにアクセス可能かチェック（統一API使用）"""
        if room_type == RoomType.GROUP:
            return True  # グループは誰でもアクセス可能
            
        try:
            if room_type == RoomType.CLASS:
                from apps.core.organizations.models import Class
                org = Class.objects.get(id=room_id)
                return org.can_send_message(user)
            elif room_type == RoomType.SCHOOL:
                from apps.core.organizations.models import School
                org = School.objects.get(id=room_id)
                return org.can_send_message(user)
            elif room_type == RoomType.CIRCLE:
                from circle.models import Circle
                # Circleモデルが統一APIを持っていない場合の暫定処理
                circle = Circle.objects.get(id=room_id)
                # TODO: CircleもAbstractOrganizationを継承して統一APIを実装
                return circle.members.filter(id=user.id).exists()
            else:
                return False
        except Exception:
            return False
    
    def send_message(self, sender, room_type, room_id, content):
        """メッセージ送信（統一権限チェック・シグナル送信）"""
        # 存在確認
        if not self.validate_room_exists(room_type, room_id):
            raise ValidationError(f"Room {room_type}:{room_id} does not exist")
        
        # 権限確認（統一API使用）
        if not self.can_user_access_room(sender, room_type, room_id):
            raise ValidationError(f"User {sender.username} does not have permission to send messages to {room_type}:{room_id}")
        
        message = self.create(sender=sender, room_type=room_type, 
                             room_id=room_id, content=content)
        
        # リアルタイム通知シグナルを送信
        from .signals import send_room_message_post_signal
        send_room_message_post_signal(message)
        
        return message
    
class RoomMessage(AbstractBaseMessage):
    room_type = models.CharField(max_length=255, choices=RoomType.choices, null=True, blank=True)
    room_id = models.UUIDField(null=True, blank=True)
    users_read = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    objects = RoomMessageManager()

    def send_message(self, sender, room_type, room_id, content):
        """メッセージ送信（Managerメソッドを使用）"""
        return RoomMessage.objects.send_message(sender, room_type, room_id, content)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room_type', 'room_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.content