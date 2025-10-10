import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class ClassChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # 認証チェック
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        
        # URLパスパラメータからclass_idを取得
        class_id = self.scope['url_route']['kwargs']['class_id']
        
        # グループ名を設定
        self.group_name = f"class_{class_id}"
        
        # グループに参加
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # 接続を受け入れる
        await self.accept()

        # await self.send_message('connected', {
        #     'message': f'Connected to {self.group_name}',
        #     'user_id': str(self.scope['user'].id),
        #     'class_id': str(class_id)
        # })
        
    async def disconnect(self, close_code):
        # グループから退出
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send_message('pong', {'message': 'pong'})
            else:
                await self.send_message('error', {'message': 'Unknown message type'})
                
        except json.JSONDecodeError:
            await self.send_message('error', {'message': 'Invalid JSON'})
        except Exception as e:
            await self.send_message('error', {'message': str(e)})
    
    async def send_message(self, message_type, data):
        await self.send(text_data=json.dumps({
            'type': message_type,
            'data': data
        }))
    
    async def class_message(self, event):
        """
        シグナルから送信されたクラスメッセージを受信してクライアントに転送
        """
        await self.send_message('class_message', event['data'])
    
    async def enrollment_notification(self, event):
        await self.send_message('enrollment_notification', event['data'])
