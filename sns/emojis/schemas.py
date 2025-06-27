from ninja import Schema
from datetime import datetime
import uuid
from circle.schemas import CircleSchema

class EmojiSchema(Schema):
    id: uuid.UUID
    name: str
    circle: CircleSchema
    slug: str
    image: str
    created_at: datetime
    updated_at: datetime

class SimpleEmojiSchema(Schema):
    id: uuid.UUID
    name: str
    slug: str
    image: str