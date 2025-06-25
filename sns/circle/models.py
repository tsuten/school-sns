from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

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

    def __str__(self):
        return self.name

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