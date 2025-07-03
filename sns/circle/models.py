from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
from .schemas import ResponseSchema
import mimetypes
from django.utils import timezone

class CircleCategory(models.TextChoices):
    STUDY = 'study', '学習'
    HOBBY = 'hobby', '趣味'
    GAME = 'game', 'ゲーム'
    MUSIC = 'music', '音楽'
    ART = 'art', '美術'
    SPORTS = 'sports', 'スポーツ'
    OTHER = 'other', 'その他'

    @classmethod
    def get_categories(cls):
        return [choice[1] for choice in cls.choices]

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CircleManager(models.Manager):
    def get_circles_by_user(self, user):
        return self.get_queryset().filter(members=user)
    
    def get_public_circles(self):
        return self.get_queryset().filter(is_public=True)
    
    def get_circles_by_category(self, category):
        return self.get_queryset().filter(category=category)
    
    def join_circle(self, user, circle):
        if circle.founder == user:
            return ResponseSchema(status="error", error_code="founder", message="あなたはこのサークルの創始者です")
        
        if not circle.is_public:
            return ResponseSchema(status="error", error_code="not_public", message="このサークルは非公開です")
        
        if circle.members.filter(id=user.id).exists():
            return ResponseSchema(status="error", error_code="already_member", message="あなたはすでにこのサークルのメンバーです")
        
        circle.members.add(user)
        circle.save()
        return ResponseSchema(status="success", message="サークルに参加しました")
                
    def leave_circle(self, user, circle):
        if circle.founder == user:
            return ResponseSchema(status="error", error_code="cannot_leave_own_circle", message="あなたが建てたサークルを退会することはできません")
        
        if not circle.members.filter(id=user.id).exists():
            return ResponseSchema(status="error", error_code="not_member", message="あなたはこのサークルのメンバーではありません")

        circle.members.remove(user)
        circle.save()
        return ResponseSchema(status="success", message="サークルから退会しました")
    
    def delete_circle(self, user, circle):
        if circle.founder != user:
            return ResponseSchema(status="error", error_code="not_founder", message="あなたはこのサークルの創始者ではありません")
        
        circle.delete()
        return ResponseSchema(status="success", message="サークルを削除しました")  

    def ban_user(self, user, target_user, circle):
        if circle.founder != user:
            return ResponseSchema(status="error", error_code="not_founder", message="あなたはこのサークルの創始者ではありません")
        
        if not circle.members.filter(id=target_user.id).exists():
            return ResponseSchema(status="error", error_code="not_member", message="対象のユーザーはこのサークルのメンバーではありません")
        
        circle.members.remove(target_user)
        circle.save()
        return ResponseSchema(status="success", message="ユーザーをサークルから退会しました")
    
    def is_member(self, user, circle_id):
        try:
            # circle_idのUUID形式をバリデーション
            import uuid
            try:
                uuid.UUID(circle_id)
            except ValueError:
                return False
                
            circle = self.get(id=circle_id)
            return circle.members.filter(id=user.id).exists()
        except Circle.DoesNotExist:
            return False
        
    def get_history(self, user, circle_id, until=timezone.now()):
        try:
            circle = self.get(id=circle_id)
            messages = circle.messages.filter(user=user)
            if until:
                messages = messages.filter(created_at__lte=until)
            return messages.order_by('-created_at')
        except CircleMessage.DoesNotExist:
            return []
    
    def get_circle_activity(self, circle_id, limit=50, until=None):
        """サークルのメッセージ、メディア、通知を統合して取得（ポインターページネーション対応）"""
        from django.utils import timezone
        
        if until is None:
            until = timezone.now()
        
        try:
            circle = self.get(id=circle_id)
            
            # メッセージを取得（untilより前のもの）
            messages = CircleMessage.objects.filter(
                circle=circle,
                created_at__lt=until
            ).select_related('user').values(
                'id', 'content', 'user__id', 'user__username', 'created_at'
            )
            
            # 通知を取得（untilより前のもの）
            notifications = CircleNotification.objects.filter(
                circle=circle,
                created_at__lt=until
            ).values(
                'id', 'message', 'created_at'
            )
            
            # メッセージを統一形式に変換
            message_activities = []
            for msg in messages:
                message_activities.append({
                    'id': msg['id'],
                    'activity_type': 'message',
                    'activity_content': msg['content'] or '',
                    'activity_user': msg['user__username'] or 'Unknown',
                    'activity_timestamp': msg['created_at'],
                    'user__id': msg['user__id'],
                    'user__username': msg['user__username']
                })
            
            # 通知を統一形式に変換
            notification_activities = []
            for notif in notifications:
                notification_activities.append({
                    'id': notif['id'],
                    'activity_type': 'notification',
                    'activity_content': notif['message'] or '',
                    'activity_user': 'System',
                    'activity_timestamp': notif['created_at']
                })
            
            # 全てを統合してタイムスタンプでソート
            all_activities = message_activities + notification_activities
            all_activities.sort(key=lambda x: x['activity_timestamp'], reverse=True)
            
            # limit+1個取得して、次のページがあるかチェック
            activities = all_activities[:limit + 1]
            has_next = len(activities) > limit
            
            if has_next:
                activities = activities[:limit]
            
            # 次のページのポインター（最後のアイテムのタイムスタンプ）
            next_until = None
            if has_next and activities:
                next_until = activities[-1]['activity_timestamp']
            
            return {
                'activities': activities,
                'has_next': has_next,
                'next_until': next_until,
                'count': len(activities)
            }
            
        except Circle.DoesNotExist:
            return {
                'activities': [],
                'has_next': False,
                'next_until': None,
                'count': 0
            }
        
    def make_circle_public(self, circle, user):
        """サークルを公開"""
        if circle.founder != user:
            raise ValueError("あなたはこのサークルの創始者ではありません。")
        circle.make_circle_public()
        return ResponseSchema(status="success", message="サークルを公開しました")
    
    def make_circle_private(self, circle, user):
        """サークルを非公開"""
        if circle.founder != user:
            raise ValueError("あなたはこのサークルの創始者ではありません。")
        circle.make_circle_private()
        return ResponseSchema(status="success", message="サークルを非公開しました")
    
class Circle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    founder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='founded_circles', null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    # もしpublicがfalseだったらwhitelistを設定するカラムを追加
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='circle_members', blank=True)
    banned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='banned_circles', blank=True)
    invited_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='invited_circles', blank=True)
    whitelist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='whitelisted_circles', blank=True)
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='moderated_circles', blank=True)
    category = models.CharField(max_length=255, choices=CircleCategory.choices, default=CircleCategory.OTHER)
    tags = models.ManyToManyField(Tag, related_name='circles', blank=True)

    objects = CircleManager()

    def get_all_members(self):
        """創始者を含む全メンバーのクエリセットを返す"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # メンバーのIDリストを取得
        member_ids = list(self.members.values_list('id', flat=True))
        
        # 創始者がメンバーリストに含まれていない場合は追加
        if self.founder and self.founder.id not in member_ids:
            member_ids.insert(0, self.founder.id)  # 創始者を先頭に配置
        
        # IDのリストに基づいてユーザーを取得し、創始者を先頭に配置
        return User.objects.filter(id__in=member_ids).order_by(
            models.Case(
                models.When(id=self.founder.id, then=0),
                default=1,
                output_field=models.IntegerField()
            ),
            'username'
        )

    def add_member(self, user):
        """メンバーを追加（BANチェック付き）"""
        if self.banned_users.filter(id=user.id).exists():
            raise ValueError(f"ユーザー '{user.username}' はこのサークルからBANされているため、メンバーに追加できません。")
        self.members.add(user)

    def add_moderator(self, user):
        """モデレーターを追加（BANチェック付き）"""
        if self.banned_users.filter(id=user.id).exists():
            raise ValueError(f"ユーザー '{user.username}' はこのサークルからBANされているため、モデレーターに追加できません。")
        self.moderators.add(user)
        # モデレーターは自動的にメンバーにもなる
        if not self.members.filter(id=user.id).exists():
            self.members.add(user)

    def make_circle_public(self):
        """サークルを公開"""
        if self.is_public:
            raise ValueError("すでに公開されているサークルです。")
        self.is_public = True
        self.save()
    
    def make_circle_private(self):
        """サークルを非公開"""
        if not self.is_public:
            raise ValueError("すでに非公開のサークルです。")
        self.is_public = False
        self.save()
    
    def add_to_whitelist(self, user):
        """ホワイトリストにユーザーを追加"""
        if self.is_public:
            raise ValueError("公開のサークルです。")
        if self.founder == user:
            raise ValueError("あなたはこのサークルの創始者です。")
        if self.whitelist.filter(id=user.id).exists():
            raise ValueError("すでにホワイトリストに追加されています。")
        self.whitelist.add(user)
    
    def remove_from_whitelist(self, user):
        """ホワイトリストからユーザーを削除"""
        if self.is_public:
            raise ValueError("公開のサークルです。")
        if self.founder == user:
            raise ValueError("あなたはこのサークルの創始者です。")
        if not self.whitelist.filter(id=user.id).exists():
            raise ValueError("ホワイトリストに追加されていません。")
        self.whitelist.remove(user)
    
    def __str__(self):
        return self.name

class CircleMessageManager(models.Manager):
    def get_messages_by_circle(self, circle):
        return self.get_queryset().filter(circle=circle).order_by('created_at')
    
    def get_messages_by_user(self, user):
        return self.get_queryset().filter(user=user)
    
    def create_message(self, circle, user, content):
        message = self.model(circle=circle, user=user, content=content)
        message.save()
        return message
    
    def delete_message(self, message):
        message.is_deleted = True
        message.save()
        return message
    
class CircleMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    pinned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='pinned_messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CircleMessageManager()

    def clean(self):
        # ユーザーがサークルのメンバーかどうかをチェック
        if self.user and self.circle and not self.circle.members.filter(id=self.user.id).exists():
            raise ValidationError(f"ユーザー '{self.user.username}' はサークル '{self.circle.name}' のメンバーではありません")

    def save(self, *args, **kwargs):
        # cleanメソッドを呼び出してバリデーションを実行
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.circle.name}"
    
class CircleMediaManager(models.Manager):
    def create_media(self, circle, user, media):
        media = self.model(circle=circle, user=user, media=media)
        media.clean()
        media.save()
        return media

class CircleMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, null=True, blank=True)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = models.FileField(upload_to='circle_media/')
    type = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CircleMediaManager()

    def clean(self):
        mime_type = mimetypes.guess_type(self.media.name)[0]
        if mime_type is None:
            raise ValidationError("Invalid media type")
        
        if "image" in mime_type:
            self.type = "image"
        elif "video" in mime_type:
            self.type = "video"
        elif "audio" in mime_type:
            self.type = "audio"
        else:
            raise ValidationError("Invalid media type")
        

    def __str__(self):
        return f"{self.user.username} - {self.circle.name}"
    
class CircleNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    message = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.circle.name} - {self.message}"