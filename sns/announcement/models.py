import uuid
from django.core.exceptions import ValidationError
from django.db import models
from users.models import User
from enrollments.models import School, Class

class AnnouncementManager(models.Manager):
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
            announcement.posted_to_school.add(school)
        elif post_to == 'class':
            class_obj = Class.objects.get(id=target)
            announcement.posted_to_class.add(class_obj)
        
        # 関連付け後にバリデーションを実行
        announcement.full_clean()
        
        return announcement

class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_announcements')
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=[('high', '高'), ('medium', '中'), ('low', '低')], default='low')
    posted_to_school = models.ManyToManyField(School, related_name='posted_announcements', blank=True)
    posted_to_class = models.ManyToManyField(Class, related_name='posted_announcements', blank=True)
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    read = models.ManyToManyField(User, related_name='read_announcements', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AnnouncementManager()

    def __str__(self):
        return self.title

    def clean(self):
        if not self.posted_to_school.exists() and not self.posted_to_class.exists():
            raise ValidationError({
                'posted_to_school': '学校かクラスのどちらかを選択してください。',
                'posted_to_class': '学校かクラスのどちらかを選択してください。'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)