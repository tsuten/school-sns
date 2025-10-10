from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count
from ninja import Router
from ninja_jwt.authentication import JWTAuth
import uuid
from shared.decorators import with_base_schema
from .models import RoomMessage
from .schemas import RoomMessageSchema, RoomMessageCreateSchema
from typing import List
from datetime import datetime

router = Router(tags=["room_messages"])

@router.get("/room-messages/{room_type}/{room_id}", auth=JWTAuth())
@with_base_schema
def get_room_messages(request, room_type: str, room_id: uuid.UUID, before_date: datetime = None, get_amount: int = 25):
    """ルームのメッセージを取得"""
    try:
        messages = RoomMessage.objects.get_messages_from_room(
            user=request.user, 
            room_type=room_type, 
            room_id=room_id, 
            before_date=before_date, 
            limit=get_amount
        )
        return {
            "messages": [RoomMessageSchema.from_orm(message) for message in messages]
        }
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(422, f"メッセージの取得に失敗しました: {str(e)}")

@router.post("/room-messages", auth=JWTAuth())
@with_base_schema
def send_room_message(request, payload: RoomMessageCreateSchema):
    """ルームメッセージを送信"""
    try:
        message = RoomMessage.objects.send_message(
            sender=request.user,
            room_type=payload.room_type,
            room_id=payload.room_id,
            content=payload.content
        )
        
        return {
            "message": RoomMessageSchema.from_orm(message)
        }
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(422, f"メッセージの送信に失敗しました: {str(e)}")