from ninja import Schema
from datetime import datetime
import uuid
from typing import Optional, List

class NotificationSchema(Schema):
    id: uuid.UUID   
    type: Optional[str]  # Noneを許可
    content: str
    is_read: bool
    created_at: datetime
    issued_by: Optional[uuid.UUID] = None
    href_web: Optional[str] = None

class NotificationReadUpdateSchema(Schema):
    is_read: bool

class BulkReadUpdateSchema(Schema):
    notification_ids: List[uuid.UUID]

class ReadStatusResponse(Schema):
    success: bool
    message: str
    updated_count: Optional[int] = None

class NotificationFilterSchema(Schema):
    type: Optional[str] = None
    is_read: Optional[bool] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class NotificationCategorySchema(Schema):
    category: str
    count: int
    types: List[str]

class BulkDeleteSchema(Schema):
    notification_ids: List[uuid.UUID]

class DeleteStatusResponse(Schema):
    success: bool
    message: str
    deleted_count: Optional[int] = None

class NotificationStatsSchema(Schema):
    total_count: int
    unread_count: int
    read_count: int
    deleted_count: int

class UnreadCountByTypeSchema(Schema):
    type: Optional[str]
    count: int    