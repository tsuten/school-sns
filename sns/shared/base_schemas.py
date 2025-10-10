from ninja import Schema
from datetime import datetime
from enum import Enum
from typing import Any

class Status(Enum):
    SUCCESS = "success"
    ERROR = "error"

class BaseSchema(Schema):
    status: str
    timestamp: datetime
    data: dict = None
    error: str = None

class BaseResponseSchema(Schema):
    """API レスポンス用のベーススキーマ"""
    status: str
    timestamp: datetime
    data: Any

class WebsocketBaseSchema(Schema):
    type: str
    data: dict
    timestamp: datetime