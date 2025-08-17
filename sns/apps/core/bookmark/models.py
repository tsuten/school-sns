from django.db import models
from django.conf import settings
from shared.abstract_models import AbstractBaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from enum import Enum
from typing import Optional
import uuid


class BookmarkType(Enum):
    """ブックマーク可能なコンテンツタイプを定義するenum"""
    POST = 'post'
    CIRCLE = 'circle'
    EVENT = 'event'
    POLL = 'poll'
    ANNOUNCEMENT = 'announcement'
    MEMO = 'memo'
    USER = 'user'
    ORGANIZATION = 'organization'
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class BookmarkManager(models.Manager):
    def get_bookmarks(self, user):
        return self.get_queryset().filter(user=user, content_type__isnull=False)

    def get_bookmark(self, user, item):
        return self.get_queryset().filter(user=user, content_type=item.__class__, object_id=item.id).first()


class BookmarkV2Manager(models.Manager):
    def get_bookmarks(self, user, bookmark_type: Optional[str] = None):
        """ユーザーのブックマークを取得（オプションでタイプ指定）"""
        queryset = self.get_queryset().filter(user=user)
        if bookmark_type:
            queryset = queryset.filter(bookmark_type=bookmark_type)
        return queryset
    
    def get_bookmark(self, user, bookmark_type: str, object_id: uuid.UUID):
        """特定のブックマークを取得"""
        return self.get_queryset().filter(
            user=user, 
            bookmark_type=bookmark_type, 
            object_id=object_id
        ).first()
    
    def create_bookmark(self, user, bookmark_type: str, object_id: uuid.UUID):
        """新しいブックマークを作成"""
        return self.create(
            user=user,
            bookmark_type=bookmark_type,
            object_id=object_id
        )


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


class BookmarkV2(AbstractBaseModel):
    """新しいブックマークモデル（enumでcontent_typeを制御）"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # enumで制御するブックマークタイプ
    bookmark_type = models.CharField(
        max_length=20,
        choices=BookmarkType.choices(),
        help_text="ブックマーク対象のコンテンツタイプ"
    )
    
    # ブックマーク対象のオブジェクトID
    object_id = models.UUIDField(help_text="ブックマーク対象のオブジェクトID")
    
    # 追加のメタデータ（必要に応じて）
    title = models.CharField(max_length=255, blank=True, null=True, help_text="ブックマーク対象のタイトル")
    description = models.TextField(blank=True, null=True, help_text="ブックマーク対象の説明")
    
    objects = BookmarkV2Manager()
    
    class Meta:
        unique_together = ['user', 'bookmark_type', 'object_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bookmark_type', 'object_id']),
            models.Index(fields=['user', 'bookmark_type']),
        ]
        verbose_name = "Bookmark V2"
        verbose_name_plural = "Bookmarks V2"
    
    def __str__(self):
        return f'{self.user.username} bookmarked {self.bookmark_type}:{self.object_id}'
    
    def clean(self):
        """バリデーション：指定されたオブジェクトが存在するかチェック"""
        # 抽象化は後で実装するため、現在はシンプルなバリデーション
        pass
    
    def get_target_object(self):
        """ブックマーク対象のオブジェクトを取得"""
        # 抽象化は後で実装するため、現在はNoneを返す
        return None
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bookmark_type': self.bookmark_type,
            'object_id': self.object_id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
        }