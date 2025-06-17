from ninja import Schema
import uuid
from datetime import datetime

class EventSchema(Schema):
    id: uuid.UUID
    organizer: str
    title: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    location: str
    published: bool
    is_cancelled: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def resolve_organizer(obj):
        return obj.organizer.username