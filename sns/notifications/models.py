from django.db import models
import uuid
from django.conf import settings

class NotificationType(models.TextChoices):
    ANNOUNCEMENT = 'announcement', 'Announcement'
    MESSAGE = 'message', 'Message'

class NotificationManager(models.Manager):
    def get_notifications(self, user):
        return self.filter(user=user)

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    issued_by = models.UUIDField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=NotificationType.choices, null=True, blank=True)
    content = models.TextField(default="")
    href_web = models.CharField(max_length=255, default="", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()