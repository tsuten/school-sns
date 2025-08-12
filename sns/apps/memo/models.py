from django.db import models
from django.conf import settings
from django.db.models import Q
from shared.abstract_models import AbstractBaseModel
from django.utils import timezone

class MemoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')
    
    def search(self, query, user):
        """メモを検索する"""
        return self.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            user=user,
            is_deleted=False
        ).order_by('-created_at')
    
    def get_recent_memos(self, user, limit=5):
        """最近のメモを取得する"""
        return self.filter(
            user=user,
            is_deleted=False
        ).order_by('-created_at')[:limit]
    
    def get_memo_count(self, user):
        """ユーザーのメモ数を取得する"""
        return self.filter(
            user=user,
            is_deleted=False
        ).count()

class Memo(AbstractBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    objects = MemoManager()

    class Meta:
        verbose_name = 'メモ'
        verbose_name_plural = 'メモ'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'is_deleted']),
        ]

    def __str__(self):
        return self.title
    
    def get_excerpt(self, length=100):
        """メモの内容を指定された長さで切り詰める"""
        if len(self.content) <= length:
            return self.content
        return self.content[:length] + '...'
    
    def is_recent(self, days=7):
        """指定された日数以内に作成されたかチェック"""
        from django.utils import timezone
        from datetime import timedelta
        return self.created_at >= timezone.now() - timedelta(days=days)
    
    def get_word_count(self):
        """メモの文字数を取得"""
        return len(self.content)
    
    def duplicate(self, new_title=None):
        """メモを複製する"""
        new_memo = Memo.objects.create(
            user=self.user,
            title=new_title or f"{self.title} (コピー)",
            content=self.content
        )
        return new_memo
    
    def move_to_user(self, new_user):
        """メモを別のユーザーに移動する"""
        if new_user != self.user:
            self.user = new_user
            self.save()
            return True
        return False
    
    def archive(self):
        """メモをアーカイブする（論理削除の代替）"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def unarchive(self):
        """メモをアーカイブから復元する"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
    
    def get_related_memos(self, limit=5):
        """関連するメモを取得する（同じユーザーの類似タイトル）"""
        return Memo.objects.filter(
            user=self.user,
            is_deleted=False,
            title__icontains=self.title[:10]  # タイトルの最初の10文字で検索
        ).exclude(id=self.id)[:limit]