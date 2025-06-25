from ninja import Schema
from datetime import datetime
import uuid
from typing import Optional

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