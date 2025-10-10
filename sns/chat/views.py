from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count
from ninja import Router
from ninja_jwt.authentication import JWTAuth
import uuid
from shared.decorators import with_base_schema
from .models import PrivateMessage
from .schemas import (
    MessageSchema, 
    MessageListInputSchema, 
    MessageListOutputSchema,
    MessageCreateInputSchema, 
    MessageCreateOutputSchema,
    MessageUpdateInputSchema,
    MessageUpdateOutputSchema,
    MessageReadInputSchema,
    MessageReadOutputSchema,
    WhoSentMessage,
    UsersHaveHistoryWithUserOutputSchema,
)
from apps.core.organizations.utils import OrganizationManagerService

# viewsに直接ビジネスロジックを書いているので後々サービス層作ってそこに移行

User = get_user_model()
router = Router(tags=['messages'])
private_message_router = Router(tags=['private_messages'])

def determine_who_sent_message(message, request_user):
    """メッセージの送信者を判定する"""
    if message.sender == request_user:
        return WhoSentMessage.REQUEST_USER.value  # Enum値の文字列部分のみ返す
    else:
        return WhoSentMessage.TARGET_USER.value   # Enum値の文字列部分のみ返す

@private_message_router.get('/messages/{user_id}', auth=JWTAuth())
@with_base_schema
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
        messages = PrivateMessage.objects.get_messages_between_users(
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
        
        return MessageListOutputSchema(messages=message_schemas).dict()
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの取得に失敗しました: {str(e)}")

@private_message_router.post('/messages', auth=JWTAuth())
@with_base_schema
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
        message = PrivateMessage.objects.send_message(
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
        ).dict()
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの送信に失敗しました: {str(e)}")

@private_message_router.post('/messages/{message_id}/read', auth=JWTAuth())
@with_base_schema
def mark_message_as_read(request, message_id: str):
    """メッセージを既読にする"""
    try:
        message = get_object_or_404(PrivateMessage, id=message_id)
        current_user = request.user
        
        # 受信者のみが既読にできる
        if message.receiver != current_user:
            from ninja.errors import HttpError
            raise HttpError(403, "このメッセージを既読にする権限がありません")
        
        # 既読にする
        message = PrivateMessage.objects.mark_message_as_read(message_id=message_id)
        
        return MessageReadOutputSchema(
            success=True,
            read_at=message.read_at
        ).dict()
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの既読処理に失敗しました: {str(e)}")

@private_message_router.get('/conversations', auth=JWTAuth())
@with_base_schema
def get_conversations(request):
    """会話相手一覧を取得（最新メッセージ付き）"""
    try:
        current_user = request.user
        
        # 自分が送信または受信したメッセージがあるユーザーを取得
        sent_to_users = PrivateMessage.objects.filter(
            sender=current_user, is_deleted=False
        ).values_list('receiver', flat=True).distinct()
        
        received_from_users = PrivateMessage.objects.filter(
            receiver=current_user, is_deleted=False
        ).values_list('sender', flat=True).distinct()
        
        # 重複を除いてユーザーIDのセットを作成
        user_ids = set(sent_to_users) | set(received_from_users)
        user_ids.discard(None)  # null値を除外
        
        conversations = []
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                latest_message = PrivateMessage.objects.get_latest_message_between_users(current_user, user)
                unread_count = PrivateMessage.objects.filter(
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

@private_message_router.get('/unread-count', auth=JWTAuth())
@with_base_schema
def get_unread_count(request):
    """未読メッセージの総数を取得"""
    try:
        current_user = request.user
        unread_count = PrivateMessage.objects.get_unread_count(current_user)
        
        return {'unread_count': unread_count}
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"未読メッセージ数の取得に失敗しました: {str(e)}")

@private_message_router.post("/send-message", auth=JWTAuth())
@with_base_schema
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
        message = PrivateMessage.objects.send_message(
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
        ).dict()
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの送信に失敗しました: {str(e)}")
    
@private_message_router.get("/users-have-history-with-user", auth=JWTAuth())
@with_base_schema
def get_users_have_history_with_user(request):
    """指定ユーザーとメッセージを交信したユーザーのリストを最新メッセージ情報と共に取得"""
    try:
        current_user = request.user
        users_data = PrivateMessage.objects.get_list_of_users_have_history_with_user(current_user)
        
        # スキーマに変換
        users_with_messages = []
        
        for entry in users_data:
            user = entry['user']
            
            # ユーザー情報は既に辞書形式で構築されているためそのまま使用
            user_profile_data = {
                'user_id': user['id'],
                'user_username': user['user_username'],
                'display_name': user['display_name'],
                'pfp': user['pfp'],
            }
            
            user_with_message = {
                'user_id': entry['user_id'],
                'user': user_profile_data,
                'latest_message': {
                    'content': entry['latest_message']['content'],
                    'created_at': entry['latest_message']['created_at'],
                    'sender_id': entry['latest_message']['sender_id'],
                    'is_sent_by_me': entry['latest_message']['is_sent_by_me'],
                    'is_read': entry['latest_message']['is_read']
                }
            }
            users_with_messages.append(user_with_message)
        
        return UsersHaveHistoryWithUserOutputSchema(users=users_with_messages).dict()
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"ユーザーのリストの取得に失敗しました: {str(e)}")

@private_message_router.delete('/messages/{message_id}/delete', auth=JWTAuth())
@with_base_schema
def delete_message(request, message_id: str):
    """メッセージを論理削除する"""
    try:
        message = get_object_or_404(PrivateMessage, id=message_id)
        current_user = request.user
        
        # 送信者のみが削除できる
        if message.sender != current_user:
            from ninja.errors import HttpError
            raise HttpError(403, "このメッセージを削除する権限がありません")
        
        # 既に削除済みの場合はエラーを返す
        if message.is_deleted:
            from ninja.errors import HttpError
            raise HttpError(400, "このメッセージは既に削除済みです")
        
        # 論理削除
        deleted_message = PrivateMessage.objects.delete_message(message_id=message_id)
        
        return {
            'success': True,
            'message_id': str(deleted_message.id),
            'deleted_at': deleted_message.updated_at.isoformat()
        }
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの削除に失敗しました: {str(e)}")

@private_message_router.patch('/messages/{message_id}/restore', auth=JWTAuth())
@with_base_schema
def restore_message(request, message_id: str):
    """削除されたメッセージを復元する"""
    try:
        message = get_object_or_404(PrivateMessage, id=message_id)
        current_user = request.user
        
        # 送信者のみが復元できる
        if message.sender != current_user:
            from ninja.errors import HttpError
            raise HttpError(403, "このメッセージを復元する権限がありません")
        
        # 既に復元済みの場合はエラーを返す
        if not message.is_deleted:
            from ninja.errors import HttpError
            raise HttpError(400, "このメッセージは既に復元済みです")
        
        # 復元
        restored_message = PrivateMessage.objects.restore_message(message_id=message_id)
        
        return {
            'success': True,
            'message_id': str(restored_message.id),
            'restored_at': restored_message.updated_at.isoformat()
        }
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの復元に失敗しました: {str(e)}")

@private_message_router.patch('/messages/{message_id}/update', auth=JWTAuth())
@with_base_schema
def update_message(request, message_id: uuid.UUID, payload: MessageUpdateInputSchema):
    """メッセージの内容を更新する"""
    try:
        message = get_object_or_404(PrivateMessage, id=message_id)
        current_user = request.user
        
        # 送信者のみが更新できる
        if message.sender != current_user:
            from ninja.errors import HttpError
            raise HttpError(403, "このメッセージを更新する権限がありません")
        
        # 内容を更新
        updated_message = PrivateMessage.objects.update_message_content(
            message_id=message_id,
            content=payload.content
        )
        
        return {
            'success': True,
            'message_id': updated_message.id,
            'content': updated_message.content,
            'updated_at': updated_message.updated_at.isoformat()
        }
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"メッセージの更新に失敗しました: {str(e)}")
    
@router.get("/room-list", auth=JWTAuth())
def get_room_list(request):
    """ルーム一覧を取得"""
    try:
        current_user = request.user
        
        # 自分が送信または受信したメッセージがあるユーザーを取得
        sent_to_users = PrivateMessage.objects.filter(
            sender=current_user, is_deleted=False
        ).values_list('receiver', flat=True).distinct()
        
        received_from_users = PrivateMessage.objects.filter(
            receiver=current_user, is_deleted=False
        ).values_list('sender', flat=True).distinct()
        
        # 重複を除いてユーザーIDのセットを作成
        user_ids = set(sent_to_users) | set(received_from_users)
        user_ids.discard(None)  # null値を除外
        
        conversations = []
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                latest_message = PrivateMessage.objects.get_latest_message_between_users(current_user, user)
                unread_count = PrivateMessage.objects.filter(
                    sender=user, receiver=current_user, is_read=False, is_deleted=False
                ).count()
                
                # ユーザーの所属組織情報を取得
                user_organizations = OrganizationManagerService.get_user_organizations_with_role(str(user.id))
                
                # 組織情報を整形
                organizations_info = {
                    'classes': {
                        'managed': [
                            {
                                'id': str(org['organization'].id),
                                'name': org['organization'].name,
                                'role': org['role'],
                                'grade_number': getattr(org['organization'], 'grade_number', None),
                                'class_number': getattr(org['organization'], 'class_number', None),
                                'school_name': org['organization'].school.name if hasattr(org['organization'], 'school') and org['organization'].school else None
                            } for org in user_organizations['classes']['managed']
                        ],
                        'member': [
                            {
                                'id': str(org['organization'].id),
                                'name': org['organization'].name,
                                'role': org['role'],
                                'grade_number': getattr(org['organization'], 'grade_number', None),
                                'class_number': getattr(org['organization'], 'class_number', None),
                                'school_name': org['organization'].school.name if hasattr(org['organization'], 'school') and org['organization'].school else None
                            } for org in user_organizations['classes']['member']
                        ]
                    },
                    'schools': {
                        'managed': [
                            {
                                'id': str(org['organization'].id),
                                'name': org['organization'].name,
                                'role': org['role'],
                                'location': org['organization'].location
                            } for org in user_organizations['schools']['managed']
                        ],
                        'member': [
                            {
                                'id': str(org['organization'].id),
                                'name': org['organization'].name,
                                'role': org['role'],
                                'location': org['organization'].location
                            } for org in user_organizations['schools']['member']
                        ]
                    }
                }
                
                conversations.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': getattr(user, 'display_name', user.username),
                    'last_message': latest_message.content if latest_message else '',
                    'last_message_time': latest_message.created_at if latest_message else None,
                    'unread_count': unread_count,
                    'organizations': organizations_info
                })
            except User.DoesNotExist:
                continue
        
        # 最新メッセージの時間順でソート
        conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
        
        return conversations
        
    except Exception as e:
        from ninja.errors import HttpError
        raise HttpError(400, f"会話一覧の取得に失敗しました: {str(e)}")
