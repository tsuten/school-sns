from ninja import Schema
from datetime import datetime
import uuid
from typing import List, Optional

class AssignmentSchema(Schema):
    id: uuid.UUID
    title: str
    description: Optional[str]
    due_date: datetime
    assigned_to_ids: List[uuid.UUID]
    created_by_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

class CreateAssignmentSchema(Schema):
    title: str
    description: Optional[str]
    due_date: datetime
    assigned_to_ids: List[uuid.UUID]

class UpdateAssignmentSchema(Schema):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    assigned_to_ids: Optional[List[uuid.UUID]]
