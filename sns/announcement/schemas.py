import uuid
from ninja import Schema, Field
from datetime import datetime
from typing import List, Optional

class AnnouncementPostSchema(Schema):
    title: str
    content: str
    post_to: str = Field(choices=['school', 'class'])
    target: uuid.UUID
    priority: str = Field(choices=['high', 'medium', 'low'])

class AnnouncementResponseSchema(Schema):
    id: uuid.UUID
    title: str
    content: str
    priority: str
    is_pinned: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    posted_by: str  # ユーザー名
    posted_to_schools: List[str]  # 学校名のリスト
    posted_to_classes: List[str]  # クラス名のリスト
    users_read: List[str]  # 既読したユーザー名のリスト
    
    @classmethod
    def from_announcement(cls, announcement):
        return cls(
            id=announcement.id,
            title=announcement.title,
            content=announcement.content,
            priority=announcement.priority,
            is_pinned=announcement.is_pinned,
            is_deleted=announcement.is_deleted,
            created_at=announcement.created_at,
            updated_at=announcement.updated_at,
            posted_by=announcement.posted_by.username,
            posted_to_schools=[school.name for school in announcement.posted_to_school.all()],
            posted_to_classes=[f"{cls.school.name} - {cls.name}" for cls in announcement.posted_to_class.all()],
            users_read=[user.username for user in announcement.read.all()],
        )