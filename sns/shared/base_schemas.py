from ninja import Schema
from datetime import datetime
from enum import Enum

class Status(Enum):
    SUCCESS = "success"
    ERROR = "error"

class BaseSchema(Schema):
    status: Status
    timestamp: datetime

class WebsocketBaseSchema(Schema):
    type: str
    data: dict
    timestamp: datetime