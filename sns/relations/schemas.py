from ninja import Schema
import uuid
from typing import Optional
from .models import RelationManagementType
from datetime import datetime

class SendFriendRequestSchema(Schema):
    to_user_id: uuid.UUID 

class AcceptFriendRequestSchema(Schema):
    friend_request_id: uuid.UUID

class RejectFriendRequestSchema(Schema):
    friend_request_id: uuid.UUID

class CancelFriendRequestSchema(Schema):
    friend_request_id: uuid.UUID

class RelationManagementSchema(Schema):
    target_user_id: uuid.UUID

class RemoveFriendSchema(Schema):
    friend_user_id: uuid.UUID

class UserBasicSchema(Schema):
    id: uuid.UUID
    username: str
    request_id: Optional[uuid.UUID] = None

class RelationManagementEntrySchema(Schema):
    id: uuid.UUID
    user_id: uuid.UUID # 誰が管理しているか
    target_user: UserBasicSchema # 対象ユーザーの情報
    management: RelationManagementType
    created_at: datetime