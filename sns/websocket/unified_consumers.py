import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from datetime import datetime

async def send_to_user(user_id, message_type, data, operation=None):
    """特定のユーザーIDに対してメッセージを送信"""
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'send_message',
            'message_type': message_type,
            'data': data,
            'operation': operation
        }
    )

async def send_to_group(group_name, message_type, data, operation=None):
    """グループに対してメッセージを送信"""
    channel_layer = get_channel_layer()
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'send_message',
            'message_type': message_type,
            'data': data,
            'operation': operation
        }
    )

class UnifiedConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # 認証チェック
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        
        # グループ名を設定
        self.group_name = f"user_{self.scope['user'].id}"
        
        # グループに参加
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # 接続を受け入れる
        await self.accept()
        
    async def disconnect(self, close_code):
        # グループから退出
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """WebSocketからのメッセージを受信して処理"""
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
            
            if action == 'join_group':
                group_name = text_data_json.get('group_name')
                if group_name:
                    await self.join_group(group_name)
                    await self.send(text_data=json.dumps({
                        'type': 'group_joined',
                        'data': {'group_name': group_name},
                        'timestamp': datetime.now().isoformat()
                    }))
            
            elif action == 'leave_group':
                group_name = text_data_json.get('group_name')
                if group_name:
                    await self.leave_group(group_name)
                    await self.send(text_data=json.dumps({
                        'type': 'group_left',
                        'data': {'group_name': group_name},
                        'timestamp': datetime.now().isoformat()
                    }))
            
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'data': {'message': 'Unknown action'},
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'data': {'message': 'Invalid JSON'},
                'timestamp': datetime.now().isoformat()
            }))

    async def send_message(self, event):
        """チャンネルレイヤーからのメッセージを処理"""
        message_type = event['message_type']
        data = event['data']
        operation = event.get('operation', 'other')

        await self.send(text_data=json.dumps({
            'type': message_type,
            'operation': operation,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def join_group(self, group_name):
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
    
    async def leave_group(self, group_name):
        await self.channel_layer.group_discard(
            group_name,
            self.channel_name
        )

    async def send_to_group(self, group_name, message_type, data, operation=None):
        await send_to_group(group_name, message_type, data, operation)