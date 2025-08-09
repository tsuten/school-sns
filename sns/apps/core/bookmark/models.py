from django.db import models
from django.conf import settings
from shared.abstract_models import AbstractBaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

class BookmarkManager(models.Manager):
    def get_bookmarks(self, user):
        return self.get_queryset().filter(user=user, content_type__isnull=False)

    def get_bookmark(self, user, item):
        return self.get_queryset().filter(user=user, content_type=item.__class__, object_id=item.id).first()

class Bookmark(AbstractBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.UUIDField(default=None, null=True, blank=True)
    item = GenericForeignKey('content_type', 'object_id')

    def add_bookmark(self, user, item):
        return self.save(user=user, content_type=item.__class__, object_id=item.id)

    objects = BookmarkManager()

    def clean(self):
        model_class = self.content_type.model_class()
        if not model_class.objects.filter(id=self.object_id).exists():
            raise ValidationError("指定された対象は存在しません。")


    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'{self.user.username} bookmarked {self.item}'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type_id': self.content_type_id,
            'object_id': self.object_id,
            'created_at': self.created_at,
        }