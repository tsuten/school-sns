from ninja import Schema
from datetime import datetime
import uuid
from enum import Enum
from typing import Optional

class WhoSentMessage(Enum):
    REQUEST_USER = "request_user"
    TARGET_USER = "target_user"
    OTHER_SENDER = "other_sender"

class MessageSchema(Schema):
    id: uuid.UUID
    sent_by: str  # Enum値の文字列のみを返す
    content: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class MessageListInputSchema(Schema):
    until_date: datetime
    get_amount: int = 25

class MessageListOutputSchema(Schema):
    messages: list[MessageSchema]

class MessageCreateInputSchema(Schema):
    receiver_id: uuid.UUID
    content: str

class MessageCreateOutputSchema(Schema):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    created_at: datetime

class MessageReadInputSchema(Schema):
    message_id: uuid.UUID

class MessageReadOutputSchema(Schema):
    success: bool
    read_at: datetime