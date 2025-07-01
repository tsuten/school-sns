from django.db import models
import uuid
from circle.models import Circle

class EmojiManager(models.Manager):
    def get_by_circle(self, circle):
        return self.get_queryset().filter(circle=circle)

class Emoji(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    image = models.ImageField(upload_to='emojis/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EmojiManager()

    def save(self, *args, **kwargs):
        self.slug = self.circle.name.lower().replace(' ', '-') + "." + self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name