from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from .models import PrivateMessage, RoomMessage
from users.models import UserProfile

# プライベートメッセージ用カスタムシグナル
message_post_signal = Signal()
message_update_signal = Signal()
message_delete_signal = Signal()
message_restore_signal = Signal()

# ルームメッセージ用カスタムシグナル
room_message_post_signal = Signal()
room_message_update_signal = Signal()
room_message_delete_signal = Signal()
room_message_restore_signal = Signal()

# シグナル送信のラッパー関数
def send_message_post_signal(message):
    """メッセージ作成シグナルを送信"""
    message_post_signal.send(
        sender=PrivateMessage,
        message=message,
        action='post',
        user_id=message.sender.id if message.sender else None,
        receiver_id=message.receiver.id if message.receiver else None
    )

def send_message_update_signal(message):
    """メッセージ更新シグナルを送信"""
    message_update_signal.send(
        sender=PrivateMessage,
        message=message,
        action='update',
        user_id=message.sender.id if message.sender else None,
        receiver_id=message.receiver.id if message.receiver else None
    )

def send_message_delete_signal(message):
    """メッセージ削除シグナルを送信"""
    message_delete_signal.send(
        sender=PrivateMessage,
        message=message,
        action='delete',
        user_id=message.sender.id if message.sender else None,
        receiver_id=message.receiver.id if message.receiver else None
    )

def send_message_restore_signal(message):
    """メッセージ復元シグナルを送信"""
    message_restore_signal.send(
        sender=PrivateMessage,
        message=message,
        action='restore',
        user_id=message.sender.id if message.sender else None,
        receiver_id=message.receiver.id if message.receiver else None
    )

# ルームメッセージ用シグナル送信ラッパー関数
def send_room_message_post_signal(message):
    """ルームメッセージ作成シグナルを送信"""
    room_message_post_signal.send(
        sender=RoomMessage,
        message=message,
        action='post',
        user_id=message.sender.id if message.sender else None,
        room_type=message.room_type,
        room_id=str(message.room_id) if message.room_id else None
    )

def send_room_message_update_signal(message):
    """ルームメッセージ更新シグナルを送信"""
    room_message_update_signal.send(
        sender=RoomMessage,
        message=message,
        action='update',
        user_id=message.sender.id if message.sender else None,
        room_type=message.room_type,
        room_id=str(message.room_id) if message.room_id else None
    )

def send_room_message_delete_signal(message):
    """ルームメッセージ削除シグナルを送信"""
    room_message_delete_signal.send(
        sender=RoomMessage,
        message=message,
        action='delete',
        user_id=message.sender.id if message.sender else None,
        room_type=message.room_type,
        room_id=str(message.room_id) if message.room_id else None
    )

def send_room_message_restore_signal(message):
    """ルームメッセージ復元シグナルを送信"""
    room_message_restore_signal.send(
        sender=RoomMessage,
        message=message,
        action='restore',
        user_id=message.sender.id if message.sender else None,
        room_type=message.room_type,
        room_id=str(message.room_id) if message.room_id else None
    )

# カスタムシグナルを受信するハンドラー
@receiver(message_post_signal, sender=PrivateMessage)
def handle_message_post_signal(sender, message, action, user_id, receiver_id, **kwargs):
    """メッセージ作成シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_user
    import asyncio
    
    try:
        sender_profile = UserProfile.objects.get_userdata_and_profile(message.sender.id)
        
        message_data = {
            "id": str(message.id),
            "sender": {
                "id": str(message.sender.id),
                "pfp": str(sender_profile[1].pfp) if sender_profile[1].pfp else None,
                "display_name": sender_profile[1].display_name,
                "username": message.sender.username
            },
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "is_deleted": message.is_deleted,
        }
        
        # 送信者と受信者の両方に新規メッセージ通知を送信
        # if message.sender:
        #     asyncio.run(send_to_user(message.sender.id, "message", message_data, "create"))
            
        if message.receiver:
            asyncio.run(send_to_user(message.receiver.id, "message", message_data, "create"))
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"新規メッセージ通知の送信に失敗しました: {e}")

@receiver(message_update_signal, sender=PrivateMessage)
def handle_message_update_signal(sender, message, action, user_id, receiver_id, **kwargs):
    """メッセージ更新シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_user
    import asyncio
    
    try:
        # is_deletedの変更を検出
        if hasattr(message, 'is_deleted'):
            if message.is_deleted:
                # 削除された場合
                if message.sender:
                    asyncio.run(send_to_user(
                        message.sender.id,
                        "message",
                        {
                            "id": str(message.id),
                            "sender_id": str(message.sender.id),
                            "receiver_id": str(message.receiver.id) if message.receiver else None,
                            "deleted_at": message.deleted_at.isoformat() if hasattr(message, 'deleted_at') and message.deleted_at else message.updated_at.isoformat(),
                            "room_type": "private"
                        },
                        "delete"
                    ))
                
                if message.receiver:
                    asyncio.run(send_to_user(
                        message.receiver.id,
                        "message", 
                        {
                            "id": str(message.id),
                            "sender_id": str(message.sender.id) if message.sender else None,
                            "receiver_id": str(message.receiver.id),
                            "deleted_at": message.deleted_at.isoformat() if hasattr(message, 'deleted_at') and message.deleted_at else message.updated_at.isoformat(),
                            "room_type": "private"
                        },
                        "delete"
                    ))
            else:
                # 通常の更新（content等の変更）
                sender_profile = UserProfile.objects.get_userdata_and_profile(message.sender.id)
                
                message_data = {
                    "id": str(message.id),
                    "sender": {
                        "id": str(message.sender.id),
                        "pfp": str(sender_profile[1].pfp) if sender_profile[1].pfp else None,
                        "display_name": sender_profile[1].display_name,
                        "username": message.sender.username
                    },
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                    "is_deleted": message.is_deleted,
                    "updated_at": message.updated_at.isoformat()
                }
                
                if message.sender:
                    asyncio.run(send_to_user(message.sender.id, "message", message_data, "update"))
                
                if message.receiver:
                    asyncio.run(send_to_user(message.receiver.id, "message", message_data, "update"))
                    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"メッセージ更新通知の送信に失敗しました: {e}")

@receiver(message_delete_signal, sender=PrivateMessage)
def handle_message_delete_signal(sender, message, action, user_id, receiver_id, **kwargs):
    """メッセージ削除シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_user
    import asyncio
    
    try:
        # 論理削除されたメッセージの通知を両方のユーザーに送信
        if message.sender:
            asyncio.run(send_to_user(
                message.sender.id,
                "message",
                {
                    "id": str(message.id),
                    "sender_id": str(message.sender.id),
                    "receiver_id": str(message.receiver.id) if message.receiver else None,
                    "deleted_at": message.deleted_at.isoformat() if hasattr(message, 'deleted_at') and message.deleted_at else message.updated_at.isoformat(),
                    "room_type": "private"
                },
                "delete"
            ))
        
        if message.receiver:
            asyncio.run(send_to_user(
                message.receiver.id,
                "message", 
                {
                    "id": str(message.id),
                    "sender_id": str(message.sender.id) if message.sender else None,
                    "receiver_id": str(message.receiver.id),
                    "deleted_at": message.deleted_at.isoformat() if hasattr(message, 'deleted_at') and message.deleted_at else message.updated_at.isoformat(),
                    "room_type": "private"
                },
                "delete"
            ))
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"メッセージ削除通知の送信に失敗しました: {e}")

@receiver(message_restore_signal, sender=PrivateMessage)
def handle_message_restore_signal(sender, message, action, user_id, receiver_id, **kwargs):
    """メッセージ復元シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_user
    import asyncio
    
    try:
        sender_profile = UserProfile.objects.get_userdata_and_profile(message.sender.id)
        
        message_data = {
            "id": str(message.id),
            "sender": {
                "id": str(message.sender.id),
                "pfp": str(sender_profile[1].pfp) if sender_profile[1].pfp else None,
                "display_name": sender_profile[1].display_name,
                "username": message.sender.username
            },
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "is_deleted": message.is_deleted,
            "restored_at": message.updated_at.isoformat()
        }
        
        if message.sender:
            asyncio.run(send_to_user(message.sender.id, "message", message_data, "restore"))
        
        if message.receiver:
            asyncio.run(send_to_user(message.receiver.id, "message", message_data, "restore"))
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"メッセージ復元通知の送信に失敗しました: {e}")

# ルームメッセージ用シグナルハンドラー
@receiver(room_message_post_signal, sender=RoomMessage)
def handle_room_message_post_signal(sender, message, action, user_id, room_type, room_id, **kwargs):
    """ルームメッセージ作成シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_group
    import asyncio
    
    try:
        sender_profile = UserProfile.objects.get_userdata_and_profile(message.sender.id)
        
        message_data = {
            "id": str(message.id),
            "sender": {
                "id": str(message.sender.id),
                "pfp": str(sender_profile[1].pfp) if sender_profile[1].pfp else None,
                "display_name": sender_profile[1].display_name,
                "username": message.sender.username
            },
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "is_deleted": message.is_deleted,
            "room_type": room_type,
            "room_id": room_id
        }
        
        # ルームグループに新規メッセージ通知を送信
        group_name = f"room_{room_type}_{room_id}"
        asyncio.run(send_to_group(group_name, "room_message", message_data, "create"))
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ルームメッセージ通知の送信に失敗しました: {e}")

@receiver(room_message_update_signal, sender=RoomMessage)
def handle_room_message_update_signal(sender, message, action, user_id, room_type, room_id, **kwargs):
    """ルームメッセージ更新シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_group
    import asyncio
    
    try:
        if hasattr(message, 'is_deleted') and message.is_deleted:
            # 削除された場合
            message_data = {
                "id": str(message.id),
                "sender_id": str(message.sender.id) if message.sender else None,
                "deleted_at": message.deleted_at.isoformat() if hasattr(message, 'deleted_at') and message.deleted_at else message.updated_at.isoformat(),
                "room_type": room_type,
                "room_id": room_id
            }
            
            group_name = f"room_{room_type}_{room_id}"
            asyncio.run(send_to_group(group_name, "room_message", message_data, "delete"))
        else:
            # 通常の更新
            sender_profile = UserProfile.objects.get_userdata_and_profile(message.sender.id)
            
            message_data = {
                "id": str(message.id),
                "sender": {
                    "id": str(message.sender.id),
                    "pfp": str(sender_profile[1].pfp) if sender_profile[1].pfp else None,
                    "display_name": sender_profile[1].display_name,
                    "username": message.sender.username
                },
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "is_deleted": message.is_deleted,
                "updated_at": message.updated_at.isoformat(),
                "room_type": room_type,
                "room_id": room_id
            }
            
            group_name = f"room_{room_type}_{room_id}"
            asyncio.run(send_to_group(group_name, "room_message", message_data, "update"))
                    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ルームメッセージ更新通知の送信に失敗しました: {e}")

@receiver(room_message_delete_signal, sender=RoomMessage)
def handle_room_message_delete_signal(sender, message, action, user_id, room_type, room_id, **kwargs):
    """ルームメッセージ削除シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_group
    import asyncio
    
    try:
        message_data = {
            "id": str(message.id),
            "sender_id": str(message.sender.id) if message.sender else None,
            "deleted_at": message.deleted_at.isoformat() if hasattr(message, 'deleted_at') and message.deleted_at else message.updated_at.isoformat(),
            "room_type": room_type,
            "room_id": room_id
        }
        
        group_name = f"room_{room_type}_{room_id}"
        asyncio.run(send_to_group(group_name, "room_message", message_data, "delete"))
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ルームメッセージ削除通知の送信に失敗しました: {e}")

@receiver(room_message_restore_signal, sender=RoomMessage)
def handle_room_message_restore_signal(sender, message, action, user_id, room_type, room_id, **kwargs):
    """ルームメッセージ復元シグナルを受信してWebSocket通知を送信"""
    from websocket.unified_consumers import send_to_group
    import asyncio
    
    try:
        sender_profile = UserProfile.objects.get_userdata_and_profile(message.sender.id)
        
        message_data = {
            "id": str(message.id),
            "sender": {
                "id": str(message.sender.id),
                "pfp": str(sender_profile[1].pfp) if sender_profile[1].pfp else None,
                "display_name": sender_profile[1].display_name,
                "username": message.sender.username
            },
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "is_deleted": message.is_deleted,
            "restored_at": message.updated_at.isoformat(),
            "room_type": room_type,
            "room_id": room_id
        }
        
        group_name = f"room_{room_type}_{room_id}"
        asyncio.run(send_to_group(group_name, "room_message", message_data, "restore"))
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ルームメッセージ復元通知の送信に失敗しました: {e}")

# Django標準シグナルのハンドラーは無効化（カスタムシグナルを使用するため）
# @receiver(post_save, sender=PrivateMessage)
# def send_new_message_notification(sender, instance, created, **kwargs):
#     """新規メッセージが作成された際にWebSocket通知を送信"""
#     # カスタムシグナルハンドラーで処理するため無効化
#     pass

# Django標準シグナルのハンドラーは無効化（カスタムシグナルを使用するため）
# @receiver(post_save, sender=PrivateMessage)
# def send_message_deleted_notification(sender, instance, created, update_fields, **kwargs):
#     """メッセージが論理削除された際にWebSocket通知を送信"""
#     # カスタムシグナルハンドラーで処理するため無効化
#     pass

# Django標準シグナルのハンドラーは無効化（カスタムシグナルを使用するため）
# @receiver(post_save, sender=PrivateMessage)  
# def send_message_restore_notification(sender, instance, created, update_fields, **kwargs):
#     """メッセージが復元された際にWebSocket通知を送信"""
#     # カスタムシグナルハンドラーで処理するため無効化
#     pass
