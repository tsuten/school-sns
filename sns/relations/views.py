from django.shortcuts import render
from .models import FriendRequest
from ninja import Router
import uuid
from django.contrib.contenttypes.models import ContentType
from ninja_jwt.authentication import JWTAuth
from shared.decorators import with_base_schema
from .models import Friend
from .schemas import SendFriendRequestSchema, AcceptFriendRequestSchema, RelationManagementSchema, UserBasicSchema, RelationManagementEntrySchema, RejectFriendRequestSchema, RemoveFriendSchema, CancelFriendRequestSchema # スキーマをインポート
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import RelationManagement, RelationManagementType # RelationManagementTypeもインポート
from shared.base_schemas import BaseSchema # BaseSchemaをインポート
User = get_user_model()

router = Router(tags=['relations'])

@router.post('/request/send', auth=JWTAuth())
@with_base_schema
def create_friend_request(request, data: SendFriendRequestSchema):
    # ユーザーが自分自身にフレンドリクエストを送ることを禁止
    if request.user.id == data.to_user_id:
        return {'status': 'error', 'error': 'You cannot send a friend request to yourself'}
    
    to_user = User.objects.get(id=data.to_user_id)
    if to_user is None:
        return {'status': 'error', 'error': 'User not found'}
    
    try:
        # FriendRequestモデルのsend_friend_requestメソッドを利用
        FriendRequest.send_friend_request(from_user=request.user, to_user=to_user)
        return {"status": "success", "message": "Friend request sent successfully"}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'フレンドリクエストの送信中にエラーが発生しました: {e}'}
    
@router.post('/request/accept', auth=JWTAuth())
@with_base_schema
def accept_friend_request(request, data: AcceptFriendRequestSchema):
    friend_request = FriendRequest.objects.get(id=data.friend_request_id)
    if friend_request.to_user != request.user:
        return {'status': 'error', 'error': 'You are not the recipient of this friend request'}
    
    friend_request.accept()
    return {"status": "success", "message": "Friend request accepted successfully"}

@router.post('/request/reject', auth=JWTAuth())
@with_base_schema
def reject_friend_request(request, data: RejectFriendRequestSchema):
    try:
        friend_request = FriendRequest.objects.get(id=data.friend_request_id)
        if friend_request.to_user != request.user:
            return {'status': 'error', 'error': 'You are not the recipient of this friend request'}
        
        friend_request.reject()
        return {"status": "success", "message": "Friend request rejected successfully"}
    except FriendRequest.DoesNotExist:
        return {'status': 'error', 'error': 'Friend request not found'}
    except Exception as e:
        return {'status': 'error', 'error': f'フレンドリクエストの拒否中にエラーが発生しました: {e}'}

@router.post('/request/cancel', auth=JWTAuth())
@with_base_schema
def cancel_friend_request(request, data: CancelFriendRequestSchema):
    try:
        friend_request = FriendRequest.objects.get(id=data.friend_request_id)
        if friend_request.from_user != request.user:
            return {'status': 'error', 'error': 'You can only cancel your own friend requests'}
        
        friend_request.cancel()
        return {"status": "success", "message": "Friend request cancelled successfully"}
    except FriendRequest.DoesNotExist:
        return {'status': 'error', 'error': 'Friend request not found'}
    except Exception as e:
        return {'status': 'error', 'error': f'フレンドリクエストの取り消し中にエラーが発生しました: {e}'}

@router.post('/management/block', auth=JWTAuth())
@with_base_schema
def block_user(request, data: RelationManagementSchema):
    try:
        target_user = User.objects.get(id=data.target_user_id)
        RelationManagement.block_user(request.user, target_user)
        return {"status": "success", "message": "User blocked successfully"}
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'Target user not found.'}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'ユーザーのブロック中にエラーが発生しました: {e}'}

@router.post('/management/unblock', auth=JWTAuth())
@with_base_schema
def unblock_user(request, data: RelationManagementSchema):
    try:
        target_user = User.objects.get(id=data.target_user_id)
        RelationManagement.unblock_user(request.user, target_user)
        return {"status": "success", "message": "User unblocked successfully"}
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'Target user not found.'}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'ユーザーのブロック解除中にエラーが発生しました: {e}'}

@router.post('/management/mute', auth=JWTAuth())
@with_base_schema
def mute_user(request, data: RelationManagementSchema):
    try:
        target_user = User.objects.get(id=data.target_user_id)
        RelationManagement.mute_user(request.user, target_user)
        return {"status": "success", "message": "User muted successfully"}
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'Target user not found.'}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'ユーザーのミュート中にエラーが発生しました: {e}'}

@router.post('/management/unmute', auth=JWTAuth())
@with_base_schema
def unmute_user(request, data: RelationManagementSchema):
    try:
        target_user = User.objects.get(id=data.target_user_id)
        RelationManagement.unmute_user(request.user, target_user)
        return {"status": "success", "message": "User unmuted successfully"}
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'Target user not found.'}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'ユーザーのミュート解除中にエラーが発生しました: {e}'}

@router.post('/management/ignore', auth=JWTAuth())
@with_base_schema
def ignore_user(request, data: RelationManagementSchema):
    try:
        target_user = User.objects.get(id=data.target_user_id)
        RelationManagement.ignore_user(request.user, target_user)
        return {"status": "success", "message": "User ignored successfully"}
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'Target user not found.'}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'ユーザーの無視中にエラーが発生しました: {e}'}

@router.post('/management/unignore', auth=JWTAuth())
@with_base_schema
def unignore_user(request, data: RelationManagementSchema):
    try:
        target_user = User.objects.get(id=data.target_user_id)
        RelationManagement.unignore_user(request.user, target_user)
        return {"status": "success", "message": "User unignored successfully"}
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'Target user not found.'}
    except ValidationError as e:
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        return {'status': 'error', 'error': f'ユーザーの無視解除中にエラーが発生しました: {e}'}

@router.get('/management/blocked', auth=JWTAuth(), response=BaseSchema) # responseをBaseSchemaに変更
@with_base_schema
def list_blocked_users(request):
    try:
        # 認証されたユーザーがブロックしているユーザーのRelationManagementエントリを取得
        blocked_users_ids = RelationManagement.objects.filter(user=request.user, management=RelationManagementType.BLOCK).values_list('target_user__id', flat=True)
        blocked_users = User.objects.filter(id__in=list(blocked_users_ids))
        
        # UserBasicSchemaに変換
        result = [UserBasicSchema(id=user.id, username=user.username).dict() for user in blocked_users]
        return {"status": "success", "data": result}
    except Exception as e:
        return {'status': 'error', 'error': f'ブロックユーザーの取得中にエラーが発生しました: {e}'}

@router.get('/management/muted', auth=JWTAuth(), response=BaseSchema) # responseをBaseSchemaに変更
@with_base_schema
def list_muted_users(request):
    try:
        muted_users_ids = RelationManagement.objects.filter(user=request.user, management=RelationManagementType.MUTE).values_list('target_user__id', flat=True)
        muted_users = User.objects.filter(id__in=list(muted_users_ids))
        result = [UserBasicSchema(id=user.id, username=user.username).dict() for user in muted_users]
        return {"status": "success", "data": result}
    except Exception as e:
        return {'status': 'error', 'error': f'ミュートユーザーの取得中にエラーが発生しました: {e}'}

@router.get('/management/ignored', auth=JWTAuth(), response=BaseSchema) # responseをBaseSchemaに変更
@with_base_schema
def list_ignored_users(request):
    try:
        ignored_users_ids = RelationManagement.objects.filter(user=request.user, management=RelationManagementType.IGNORE).values_list('target_user__id', flat=True)
        ignored_users = User.objects.filter(id__in=list(ignored_users_ids))
        result = [UserBasicSchema(id=user.id, username=user.username).dict() for user in ignored_users]
        return {"status": "success", "data": result}
    except Exception as e:
        return {'status': 'error', 'error': f'無視ユーザーの取得中にエラーが発生しました: {e}'}
    
@router.get('/friends', auth=JWTAuth(), response=BaseSchema)
@with_base_schema
def list_friends(request):
    try:
        friend_ids = Friend.objects.get_friends(request.user)
        friends = User.objects.filter(id__in=list(friend_ids))
        result = [UserBasicSchema(id=friend.id, username=friend.username).dict() for friend in friends]
        return {"status": "success", "data": result}
    except Exception as e:
        return {'status': 'error', 'error': f'フレンドの取得中にエラーが発生しました: {e}'}

@router.post('/friends/remove', auth=JWTAuth())
@with_base_schema
def remove_friend(request, data: RemoveFriendSchema):
    try:
        # 削除対象のユーザーを取得
        friend_user = User.objects.get(id=data.friend_user_id)
        
        # 自分自身を削除しようとしていないかチェック
        if request.user.id == friend_user.id:
            return {'status': 'error', 'error': 'You cannot remove yourself from friends'}
        
        # フレンドかどうかチェック
        if not Friend.objects.check_friend(request.user, friend_user):
            return {'status': 'error', 'error': 'You are not friends with this user'}
        
        # フレンド削除
        success = Friend.objects.remove_friend(request.user, friend_user)
        if success:
            return {"status": "success", "message": "Friend removed successfully"}
        else:
            return {'status': 'error', 'error': 'Failed to remove friend'}
            
    except User.DoesNotExist:
        return {'status': 'error', 'error': 'User not found'}
    except Exception as e:
        return {'status': 'error', 'error': f'フレンドの削除中にエラーが発生しました: {e}'}
    
@router.get('/requests', auth=JWTAuth(), response=BaseSchema)
@with_base_schema
def list_friend_requests(request):
    try:
        pending_friend_requests = FriendRequest.objects.get_pending_friend_requests(request.user)
        result = [UserBasicSchema(id=friend_request.from_user.id, username=friend_request.from_user.username, request_id=friend_request.id).dict() for friend_request in pending_friend_requests]
        return {"status": "success", "data": result}
    except Exception as e:
        return {'status': 'error', 'error': f'フレンドリクエストの取得中にエラーが発生しました: {e}'}

@router.get('/requests/sent', auth=JWTAuth(), response=BaseSchema)
@with_base_schema
def list_sent_friend_requests(request):
    try:
        sent_friend_requests = FriendRequest.objects.get_sent_friend_requests(request.user)
        result = [UserBasicSchema(id=friend_request.to_user.id, username=friend_request.to_user.username, request_id=friend_request.id).dict() for friend_request in sent_friend_requests]
        return {"status": "success", "data": result}
    except Exception as e:
        return {'status': 'error', 'error': f'送信済みフレンドリクエストの取得中にエラーが発生しました: {e}'}