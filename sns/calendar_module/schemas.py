from ninja import Schema
from datetime import datetime
import uuid
class CalendarSchema(Schema):
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

class ScheduleSchema(Schema):  
    id: uuid.UUID
    calendar: uuid.UUID
    title: str
    description: str
    is_all_day: bool
    start_time: datetime
    end_time: datetime
    location: str
    created_at: datetime
    updated_at: datetime