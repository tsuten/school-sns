from ninja import Schema
from typing import List, Optional, Union
from datetime import datetime
from announcement.schemas import AnnouncementResponseSchema

class FeedItemSchema(Schema):
    """フィードアイテムのスキーマ"""
    id: int
    title: str
    content: str
    created_at: datetime
    author_name: str
    item_type: str  # 'post', 'announcement', 'event' など

class ClassFeedSchema(Schema):
    """クラスフィードのスキーマ"""
    type: str = "class"
    organization: str
    feed_items: List[FeedItemSchema] = []
    total_count: int = 0

class SchoolFeedSchema(Schema):
    """学校フィードのスキーマ"""
    type: str = "school"
    organization: str
    feed_items: List[FeedItemSchema] = []
    total_count: int = 0

class FeedResponseSchema(Schema):
    """フィードレスポンスのスキーマ"""
    success: bool = True
    # クラス/学校の集約レスポンス または お知らせのリスト
    data: Optional[Union[ClassFeedSchema, SchoolFeedSchema, List[AnnouncementResponseSchema]]] = None
    message: Optional[str] = None

class ErrorResponseSchema(Schema):
    """エラーレスポンスのスキーマ"""
    success: bool = False
    error: str
    message: Optional[str] = None 