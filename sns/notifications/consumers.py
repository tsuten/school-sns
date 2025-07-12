import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # 認証チェック
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close(code=4001)  # 認証エラーコード
            return
        
        self.user_id = str(self.scope['user'].id)
        self.user_group_name = f"notifications_{self.user_id}"
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        # await self.send(text_data=json.dumps({
        #     'type': 'connection',
        #     'message': 'connected',
        #     'connected_to': self.user_group_name,
        #     'user_id': self.user_id
        # }))

    async def disconnect(self, close_code):
        # グループからの削除（認証されていない場合はuser_group_nameが設定されていない可能性があるため確認）
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    # シグナルから呼び出されるメソッド
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'id': event.get('notification_id'),
            'type': event['notification_type'],
            'content': event['message'],
            'is_read': event.get('is_read', False),
            'created_at': event.get('created_at')
        }))


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "test"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'test',
            'message': str(self.scope['user'].id) + " connected"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "test_message",
                "message": "nice unko",
            },
        )

    async def test_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"type": "test", "message": message}))