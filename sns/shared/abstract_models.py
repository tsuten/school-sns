from django.db import models
from django.utils import timezone
import uuid

class AbstractBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

    def delete_object(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore_object(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()