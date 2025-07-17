from ninja import Schema
from datetime import datetime
import uuid
from typing import Optional

class NotificationSchema(Schema):
    id: uuid.UUID   
    type: Optional[str]  # Noneを許可
    content: str
    is_read: bool
    created_at: datetime    