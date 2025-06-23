from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count
from ninja import Router
from ninja_jwt.authentication import JWTAuth
import uuid
from .models import Message
from .schemas import (
    MessageSchema, 
    MessageListInputSchema, 
    MessageListOutputSchema,
    MessageCreateInputSchema, 
    MessageCreateOutputSchema,
    MessageReadInputSchema,
    MessageReadOutputSchema,
    WhoSentMessage,
    UsersHaveHistoryWithUserOutputSchema,
)

# viewsに直接ビジネスロジックを書いているので後々サービス層作ってそこに移行

User = get_user_model()
router = Router(tags=['chat'])

def determine_who_sent_message(message, request_user):
    """メッセージの送信者を判定する"""
    if message.sender == request_user:
        return WhoSentMessage.REQUEST_USER.value  # Enum値の文字列部分のみ返す
    else:
        return WhoSentMessage.TARGET_USER.value   # Enum値の文字列部分のみ返す

@router.get('/messages/{user_id}', response=MessageListOutputSchema, auth=JWTAuth())
def get_messages_with_user(request, user_id: uuid.UUID, until_date: str = None, get_amount: int = 25):
    """特定ユーザーとの会話履歴を取得"""
    try:
        target_user = get_object_or_404(User, id=user_id)
        current_user = request.user
        
        # until_dateの処理
        if until_date:
            from datetime import datetime
            until_datetime = datetime.fromisoformat(until_date.replace('Z', '+00:00'))
        else:
            from django.utils import timezone
            until_datetime = timezone.now()
        
        # メッセージを取得
        messages = Message.objects.get_messages_between_users(
            current_user, target_user, until_datetime, get_amount
        )
        
        # スキーマに変換
        message_schemas = []
        for message in messages:
            message_schemas.append(MessageSchema(
                id=message.id,
                sent_by=determine_who_sent_message(message, current_user),
                content=message.content,
                is_read=message.is_read,
                read_at=message.read_at,
                created_at=message.created_at,
                updated_at=message.updated_at
            ))
        
        return MessageListOutputSchema(messages=message_schemas)
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの取得に失敗しました: {str(e)}")

@router.post('/messages', response=MessageCreateOutputSchema, auth=JWTAuth())
def create_message(request, payload: MessageCreateInputSchema):
    """新しいメッセージを送信"""
    try:
        receiver = get_object_or_404(User, id=payload.receiver_id)
        sender = request.user
        
        # 自分自身にはメッセージを送れない
        if sender == receiver:
            from ninja.errors import HttpError
            raise HttpError(400, "自分自身にメッセージを送ることはできません")
        
        # メッセージを作成
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=payload.content
        )
        
        return MessageCreateOutputSchema(
            id=message.id,
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=message.content,
            created_at=message.created_at
        )
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの送信に失敗しました: {str(e)}")

@router.post('/messages/{message_id}/read', response=MessageReadOutputSchema, auth=JWTAuth())
def mark_message_as_read(request, message_id: str):
    """メッセージを既読にする"""
    try:
        message = get_object_or_404(Message, id=message_id)
        current_user = request.user
        
        # 受信者のみが既読にできる
        if message.receiver != current_user:
            from ninja.errors import HttpError
            raise HttpError(403, "このメッセージを既読にする権限がありません")
        
        # 既読にする
        message.mark_as_read()
        
        return MessageReadOutputSchema(
            success=True,
            read_at=message.read_at
        )
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの既読処理に失敗しました: {str(e)}")

@router.get('/conversations', auth=JWTAuth())
def get_conversations(request):
    """会話相手一覧を取得（最新メッセージ付き）"""
    try:
        current_user = request.user
        
        # 自分が送信または受信したメッセージがあるユーザーを取得
        sent_to_users = Message.objects.filter(
            sender=current_user, is_deleted=False
        ).values_list('receiver', flat=True).distinct()
        
        received_from_users = Message.objects.filter(
            receiver=current_user, is_deleted=False
        ).values_list('sender', flat=True).distinct()
        
        # 重複を除いてユーザーIDのセットを作成
        user_ids = set(sent_to_users) | set(received_from_users)
        user_ids.discard(None)  # null値を除外
        
        conversations = []
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                latest_message = Message.objects.get_latest_message_between_users(current_user, user)
                unread_count = Message.objects.filter(
                    sender=user, receiver=current_user, is_read=False, is_deleted=False
                ).count()
                
                conversations.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': getattr(user, 'display_name', user.username),
                    'last_message': latest_message.content if latest_message else '',
                    'last_message_time': latest_message.created_at if latest_message else None,
                    'unread_count': unread_count
                })
            except User.DoesNotExist:
                continue
        
        # 最新メッセージの時間順でソート
        conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
        
        return conversations
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"会話一覧の取得に失敗しました: {str(e)}")

@router.get('/unread-count', auth=JWTAuth())
def get_unread_count(request):
    """未読メッセージの総数を取得"""
    try:
        current_user = request.user
        unread_count = Message.objects.get_unread_count(current_user)
        
        return {'unread_count': unread_count}
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"未読メッセージ数の取得に失敗しました: {str(e)}")

@router.post("/send-message", auth=JWTAuth(), response=MessageCreateOutputSchema)
def send_message(request, payload: MessageCreateInputSchema):
    """メッセージを送信"""
    try:
        receiver = get_object_or_404(User, id=payload.receiver_id)
        sender = request.user
        
        # 自分自身にはメッセージを送れない
        if sender == receiver:
            from ninja.errors import HttpError
            raise HttpError(400, "自分自身にメッセージを送ることはできません")
        
        # メッセージを作成
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=payload.content
        )
        return message
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの送信に失敗しました: {str(e)}")
    
@router.get("/users-have-history-with-user", auth=JWTAuth(), response=UsersHaveHistoryWithUserOutputSchema)
def get_users_have_history_with_user(request):
    """指定ユーザーとメッセージを交信したユーザーのリストを取得"""
    try:
        current_user = request.user
        users = Message.objects.get_list_of_users_have_history_with_user(current_user)
        return UsersHaveHistoryWithUserOutputSchema(users=users)
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"ユーザーのリストの取得に失敗しました: {str(e)}")