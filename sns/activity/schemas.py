from ninja import Schema
from datetime import datetime
import uuid
from typing import Optional, Dict, Any

class ActivitySchema(Schema):
    """アクティビティのスキーマ"""
    id: str
    type: str
    description: str
    user_id: str
    username: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = {}

class ActivityFilterSchema(Schema):
    """アクティビティフィルタリング用スキーマ"""
    user_id: Optional[str] = None
    activity_type: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
