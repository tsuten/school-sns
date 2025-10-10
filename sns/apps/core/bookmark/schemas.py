from ninja import Schema
from typing import Optional
from datetime import datetime
import uuid


class AddBookmarkSchema(Schema):
    """ブックマーク追加用スキーマ（BookmarkV2対応）"""
    bookmark_type: str  # ブックマークタイプ（post, circle, event等）
    object_id: uuid.UUID  # ブックマーク対象のID（UUID）
    title: Optional[str] = None  # タイトル（オプション）
    description: Optional[str] = None  # 説明（オプション）


class DeleteBookmarkSchema(Schema):
    """ブックマーク削除用スキーマ"""
    bookmark_id: uuid.UUID  # 削除するブックマークのID（UUID）


class BookmarkSchema(Schema):
    """既存のBookmarkモデル用スキーマ（後方互換性のため残す）"""
    id: uuid.UUID
    user_id: uuid.UUID  # UUID型に修正
    content_type_id: int
    object_id: uuid.UUID
    created_at: datetime
    # models.pyのto_dict()メソッドに合わせてupdated_atは除外
    # 関連オブジェクトの情報（必要に応じて）
    item_title: Optional[str] = None
    item_type: Optional[str] = None


class BookmarkV2Schema(Schema):
    """BookmarkV2用のスキーマ"""
    id: uuid.UUID
    user_id: uuid.UUID
    bookmark_type: str
    object_id: uuid.UUID
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class BookmarkTypeSchema(Schema):
    """ブックマークタイプ一覧用スキーマ"""
    value: str
    name: str 