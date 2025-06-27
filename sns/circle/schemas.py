from ninja import Schema
from datetime import datetime
import uuid
from typing import Optional, Literal

class UserSchema(Schema):
    id: uuid.UUID
    username: str

class TagSchema(Schema):
    id: uuid.UUID
    name: str

class CircleSchema(Schema):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    founder: UserSchema
    category: str
    tags: list[TagSchema]
    members: list[UserSchema]
    is_public: bool
    created_at: datetime
    updated_at: datetime

class CircleCategorySchema(Schema):
    category: str
    circle_count: int

class ResponseSchema(Schema):
    status: Literal["success", "error"]
    error_code: Optional[str] = None
    message: str

class CircleMessageSchema(Schema):
    id: uuid.UUID
    circle: str
    user: str
    content: str
    created_at: datetime
    updated_at: datetime

class CircleMessageCreateSchema(Schema):
    content: str

class CircleMediaSchema(Schema):
    id: uuid.UUID
    media: str
    circle: str
    user: str
    path: str
    type: str
    label: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CircleMediaCreateSchema(Schema):
    media: str
    label: Optional[str] = None