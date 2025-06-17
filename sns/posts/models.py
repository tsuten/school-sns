from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def get_published_posts(self):
        return self.get_queryset().filter(is_deleted=False)
    
    def get_posts_by_user(self, user):
        return self.get_queryset().filter(user=user)

    def search_posts(self, query):
        return self.get_queryset().filter(title__icontains=query)
    
    def search_posts_by_content(self, query):
        return self.get_queryset().filter(content__icontains=query)
    
    def get_non_deleted_posts(self):
        return self.get_queryset().filter(is_deleted=False)
    
    def get_new_posts(self, count=10):
        return self.get_non_deleted_posts().order_by('-created_at')[:count]
    
    def get_random_within_last_day(self, count=10):
        return self.get_non_deleted_posts().filter(created_at__gte=timezone.now() - timedelta(days=1)).order_by('?')[:count]
    
    def post(self, user, title, content):
        post = self.model(user=user, title=title, content=content)
        post.save()
        return post
    
class Category(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

# Create your models here.
class Post(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    content = models.TextField(blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    is_deleted = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    objects = PostManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        return self
    
    def public(self, *args, **kwargs):
        self.is_public = True
        self.save()
        return self
    
    def private(self, *args, **kwargs):
        self.is_public = False
        self.save()
        return self
    
    def save(self, *args, **kwargs):
        if self.is_deleted and self.deleted_at is None:
            self.deleted_at = timezone.now()
        super().save(*args, **kwargs)


class Like(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]