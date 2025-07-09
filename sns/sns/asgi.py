"""
ASGI config for sns project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from circle.consumers import CircleChatConsumer, CircleNotificationConsumer
from notifications.consumers import TestConsumer, NotificationConsumer
from sns.utils.websocket_auth import JWTAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sns.settings')

websocket_urlpatterns = [
    path('ws/circle/<circle_id>/chat/', CircleChatConsumer.as_asgi()),
    path('ws/circle/<circle_id>/notifications/', CircleNotificationConsumer.as_asgi()),
    path('ws/test/', TestConsumer.as_asgi()),
    path('ws/notification', NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
