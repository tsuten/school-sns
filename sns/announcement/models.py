import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from apps.core.users.models import User
from shared.abstract_models import AbstractBaseModel
from apps.core.organizations.models import School, Class
from watson import search as watson

class AnnouncementManager(models.Manager):

    def get_announcements(self, id):
        return self.get_queryset().filter(is_deleted=False, post_to=id).order_by('-created_at')
    
    def post_announcement(self, title, content, posted_by, post_to, target, priority):
        # ManyToManyフィールドの関連付け前にバリデーションを回避するため、
        # 一時的にsave()をオーバーライドしてfull_clean()をスキップ
        announcement = Announcement(
            title=title,
            content=content,
            posted_by=posted_by,
            priority=priority,
        )
        
        # バリデーションをスキップしてオブジェクトを保存
        super(Announcement, announcement).save()
        
        # ManyToManyフィールドに関連付けを追加
        if post_to == 'school':
            school = School.objects.get(id=target)
            announcement.posted_to = school.id
        elif post_to == 'class':
            class_obj = Class.objects.get(id=target)
            announcement.posted_to = class_obj.id
        
        # 関連付け後にバリデーションを実行
        announcement.full_clean()
        
        return announcement
    
    def read_announcement(self, user_id, announcement_id):
        try:
            announcement = self.get_queryset().get(id=announcement_id)
            user = User.objects.get(id=user_id)
            
            # 既読チェック
            if announcement.read.filter(id=user_id).exists():
                return {"message": "既に既読です"}
            
            # 既読に追加
            announcement.read.add(user)
            announcement.save()
            return {"message": "既読にしました"}
            
        except Announcement.DoesNotExist:
            raise ValueError("指定されたお知らせが見つかりません")
        except User.DoesNotExist:
            raise ValueError("指定されたユーザーが見つかりません")

class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_announcements')
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=[('high', '高'), ('medium', '中'), ('low', '低')], default='low')
    post_to = models.UUIDField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    read = models.ManyToManyField(User, related_name='read_announcements', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AnnouncementManager()

    def read_announcement(self, user_id):
        user = User.objects.get(id=user_id)
        self.read.add(user)
        self.save()

    def __str__(self):
        return self.title

    def clean(self):
        if not self.post_to:
            raise ValidationError({
                'post_to': '配信先を選択してください。'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# django-watson 検索対象モデルの登録
watson.register(Announcement, fields=('title', 'content'))