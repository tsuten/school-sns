import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

async def send_to_user(user_id, message_type, data):
    """特定のユーザーIDに対してメッセージを送信"""
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}"
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'send_message',
            'message_type': message_type,
            'data': data
        }
    )

async def send_to_group(group_name, message_type, data):
    """グループに対してメッセージを送信"""
    channel_layer = get_channel_layer()
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'send_message',
            'message_type': message_type,
            'data': data
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

    async def send_message(self, event):
        """チャンネルレイヤーからのメッセージを処理"""
        message_type = event['message_type']
        data = event['data']
        
        await self.send(text_data=json.dumps({
            'type': message_type,
            'data': data
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

    async def send_to_group(self, group_name, message_type, data):
        await send_to_group(group_name, message_type, data)