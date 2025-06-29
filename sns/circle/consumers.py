import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Circle, CircleMessage

User = get_user_model()


class CircleChatConsumer(AsyncWebsocketConsumer):
    """サークルチャット用のWebSocketコンシューマー"""
    
    async def connect(self):
        """WebSocket接続時の処理"""
        self.circle_id = self.scope['url_route']['kwargs']['circle_id']
        self.circle_group_name = f'circle_chat_{self.circle_id}'
        self.user = self.scope['user']
        
        # 認証チェック
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # サークルメンバーシップチェック
        is_member = await self.check_circle_membership()
        if not is_member:
            await self.close()
            return
        
        # グループに参加
        await self.channel_layer.group_add(
            self.circle_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 参加通知をグループに送信
        await self.channel_layer.group_send(
            self.circle_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )
    
    async def disconnect(self, close_code):
        """WebSocket切断時の処理"""
        # 退出通知をグループに送信
        await self.channel_layer.group_send(
            self.circle_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )
        
        # グループから退出
        await self.channel_layer.group_discard(
            self.circle_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """WebSocketからメッセージを受信した時の処理"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
            elif message_type == 'stop_typing':
                await self.handle_stop_typing(text_data_json)
            else:
                # 未知のメッセージタイプ
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))
    
    async def handle_chat_message(self, data):
        """チャットメッセージの処理"""
        message_content = data.get('message', '').strip()
        
        if not message_content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return
        
        # メッセージをデータベースに保存
        message = await self.save_message(message_content)
        
        if message:
            # グループ内の全メンバーにメッセージを送信
            await self.channel_layer.group_send(
                self.circle_group_name,
                {
                    'type': 'chat_message',
                    'message_id': str(message.id),
                    'message': message_content,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': message.created_at.isoformat(),
                }
            )
    
    async def handle_typing(self, data):
        """タイピング中の処理"""
        await self.channel_layer.group_send(
            self.circle_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )
    
    async def handle_stop_typing(self, data):
        """タイピング停止の処理"""
        await self.channel_layer.group_send(
            self.circle_group_name,
            {
                'type': 'user_stop_typing',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )
    
    # グループメッセージハンドラー
    async def chat_message(self, event):
        """チャットメッセージをWebSocketに送信"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))
    
    async def user_joined(self, event):
        """ユーザー参加通知をWebSocketに送信"""
        # 自分の参加は通知しない
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
            }))
    
    async def user_left(self, event):
        """ユーザー退出通知をWebSocketに送信"""
        # 自分の退出は通知しない
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username'],
            }))
    
    async def user_typing(self, event):
        """タイピング中通知をWebSocketに送信"""
        # 自分のタイピングは通知しない
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'user_id': event['user_id'],
                'username': event['username'],
            }))
    
    async def user_stop_typing(self, event):
        """タイピング停止通知をWebSocketに送信"""
        # 自分のタイピング停止は通知しない
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_stop_typing',
                'user_id': event['user_id'],
                'username': event['username'],
            }))
    
    # データベース操作（非同期化）
    @database_sync_to_async
    def check_circle_membership(self):
        """サークルメンバーシップを確認"""
        try:
            circle = Circle.objects.get(id=self.circle_id)
            return circle.members.filter(id=self.user.id).exists()
        except Circle.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """メッセージをデータベースに保存"""
        try:
            circle = Circle.objects.get(id=self.circle_id)
            message = CircleMessage.objects.create(
                circle=circle,
                user=self.user,
                content=content
            )
            return message
        except Circle.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error saving message: {e}")
            return None


class CircleNotificationConsumer(AsyncWebsocketConsumer):
    """サークル通知用のWebSocketコンシューマー"""
    
    async def connect(self):
        """WebSocket接続時の処理"""
        self.user = self.scope['user']
        
        # 認証チェック
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # ユーザー固有の通知グループに参加
        self.notification_group_name = f'user_notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """WebSocket切断時の処理"""
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """WebSocketからメッセージを受信した時の処理"""
        # 通知システムでは通常、クライアントからのメッセージは処理しない
        pass
    
    async def circle_notification(self, event):
        """サークル通知をWebSocketに送信"""
        await self.send(text_data=json.dumps({
            'type': 'circle_notification',
            'notification_id': event.get('notification_id'),
            'circle_id': event.get('circle_id'),
            'circle_name': event.get('circle_name'),
            'message': event.get('message'),
            'timestamp': event.get('timestamp'),
        }))
