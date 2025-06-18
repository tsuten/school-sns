from ninja import Schema
from datetime import datetime
import uuid
from typing import Optional

class CalendarSchema(Schema):
    id: uuid.UUID
    initial: Optional[str] = None
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ScheduleSchema(Schema):  
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    is_all_day: bool
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime