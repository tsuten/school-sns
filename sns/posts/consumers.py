from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        await self.channel_layer.group_add(
            'posts',
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'posts',
            self.channel_name
        )