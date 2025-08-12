from ninja import Schema
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from shared.base_schemas import BaseResponseSchema

class MemoCreateSchema(Schema):
    """メモ作成用スキーマ"""
    title: str
    content: str

class MemoUpdateSchema(Schema):
    """メモ更新用スキーマ"""
    title: Optional[str] = None
    content: Optional[str] = None

class MemoResponseSchema(Schema):
    """メモレスポンス用スキーマ"""
    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

class MemoListResponseSchema(BaseResponseSchema):
    """メモ一覧レスポンス用スキーマ"""
    data: List[MemoResponseSchema]

class MemoDetailResponseSchema(BaseResponseSchema):
    """メモ詳細レスポンス用スキーマ"""
    data: MemoResponseSchema

class MemoCreateResponseSchema(BaseResponseSchema):
    """メモ作成レスポンス用スキーマ"""
    data: MemoResponseSchema

class MemoUpdateResponseSchema(BaseResponseSchema):
    """メモ更新レスポンス用スキーマ"""
    data: MemoResponseSchema

class MemoDeleteResponseSchema(BaseResponseSchema):
    """メモ削除レスポンス用スキーマ"""
    message: str = "メモが正常に削除されました" 