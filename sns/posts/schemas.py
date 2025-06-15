from ninja import Schema
from datetime import datetime
import uuid

class PostSchema(Schema):
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    is_public: bool
    user_id: uuid.UUID

class CreatePostSchema(Schema):
    title: str
    content: str