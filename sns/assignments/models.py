from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from shared.abstract_models import AbstractBaseModel

class AssignmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def get_active_assignments(self):
        return self.get_queryset().filter(is_deleted=False, due_date__gte=timezone.now())
    
    def get_assignments_by_user(self, user):
        return self.get_queryset().filter(assigned_to=user)
    
    def get_assignments_by_creator(self, user):
        return self.get_queryset().filter(created_by=user)
    
    def get_overdue_assignments(self):
        return self.get_queryset().filter(is_deleted=False, due_date__lt=timezone.now())
    
    def search_assignments(self, query):
        return self.get_queryset().filter(title__icontains=query)
    
    def search_assignments_by_description(self, query):
        return self.get_queryset().filter(description__icontains=query)

class Assignment(AbstractBaseModel):
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='概要')
    due_date = models.DateTimeField(verbose_name='提出期限')
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_assignments', verbose_name='割当てユーザー')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assignments', verbose_name='発行ユーザー')

    objects = AssignmentManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '課題'
        verbose_name_plural = '課題'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['due_date']),
        ]

    def is_overdue(self):
        """期限切れかどうかを判定"""
        return self.due_date < timezone.now()
    
    def get_remaining_time(self):
        """残り時間を取得"""
        remaining = self.due_date - timezone.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def delete(self, *args, **kwargs):
        """論理削除"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        return self
