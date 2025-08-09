from django.db import models
import uuid
from django.conf import settings
from posts.models import Post, Like

# 全てのデータを保存できるブックマークモデルを作成

#class Bookmark(models.Model):
#    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    item = models.ForeignKey(Post, on_delete=models.CASCADE)
#    created_at = models.DateTimeField(auto_now_add=True)

#    class Meta:
#        unique_together = ['user', 'post']
#        ordering = ['-created_at']
#        indexes = [
#            models.Index(fields=['created_at']),
#        ]