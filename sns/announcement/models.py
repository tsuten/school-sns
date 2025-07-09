import uuid
from django.core.exceptions import ValidationError
from django.db import models
from users.models import User
from enrollments.models import School, Class

# Create your models here.
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