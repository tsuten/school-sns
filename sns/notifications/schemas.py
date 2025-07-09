from ninja import Schema
from datetime import datetime
import uuid

class NotificationSchema(Schema):
    id: uuid.UUID   
    content: str
    is_read: bool
    created_at: datetime    