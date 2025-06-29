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


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sns.settings')

websocket_urlpatterns = [
    path('ws/circle/<int:circle_id>/chat/', CircleChatConsumer.as_asgi()),
    path('ws/circle/notifications/', CircleNotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
