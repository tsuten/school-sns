import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user_id = str(self.scope['user'].id)
        self.user_group_name = f"user_notifications_{self.user_id}"
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'mark_as_read':
            # 既読処理
            pass
        elif message_type == 'get_notifications':
            # 通知一覧取得
            pass

    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    async def circle_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'circle_notification',
            'data': event['data']
        }))

    async def system_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'data': event['data']
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