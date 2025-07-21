from ninja import Schema
from datetime import datetime
import uuid
from enum import Enum
from typing import Optional
from users.schemas import UserProfileSchema
from typing import Any
from shared.base_schemas import BaseSchema, Status

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

class MessageUpdateInputSchema(Schema):
    content: str

class MessageUpdateOutputSchema(Schema):
    success: bool
    message_id: uuid.UUID
    content: str
    updated_at: datetime

class MessageReadInputSchema(Schema):
    message_id: uuid.UUID

class MessageReadOutputSchema(Schema):
    success: bool
    read_at: datetime

class LatestMessageSchema(Schema):
    content: str
    created_at: datetime
    sender_id: uuid.UUID
    is_sent_by_me: bool
    is_read: bool

class UserWithLatestMessageSchema(Schema):
    user_id: uuid.UUID
    user: Any  # UserProfileSchema - 循環インポートを避けるためAnyを使用
    latest_message: LatestMessageSchema

class UsersHaveHistoryWithUserOutputSchema(Schema):
    users: list[UserWithLatestMessageSchema]

