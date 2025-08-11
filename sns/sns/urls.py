from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI, Redoc
from posts.views import router as posts_router
from apps.core.users.views import router as users_router
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from polls.views import router as polls_router
from events.views import router as events_router
from calendar_module.views import router as calendar_router
from chat.views import router as chat_router, private_message_router
from chat.room_messages_views import router as room_messages_router
from circle.views import router as circle_router
from emojis.views import router as emojis_router
from announcement.views import router as announcement_router
from apps.core.notifications.views import router as notifications_router
from apps.core.organizations.organizations.views import router as organizations_router
from tests.views import router as tests_router
from search.views import router as search_router
from storage.views import router as storage_router
from shared.handlers import custom_404_handler, custom_500_handler, custom_403_handler, api_exception_handler, api_404_handler
from ninja.errors import ValidationError
from pydantic import ValidationError as PydanticValidationError
from ninja.errors import HttpError
from relations.views import router as relations_router
from setup.views import router as setup_router
from api.dynamic_api_routing import DynamicAPIRouting

api = NinjaExtraAPI(title='SNS API', version='1.0.0', docs=Redoc())
api_v1 = NinjaExtraAPI(title='SNS API v1', version='1.0.0', docs=Redoc())

# 例外ハンドラーを設定
api.add_exception_handler(ValidationError, api_exception_handler)
api.add_exception_handler(PydanticValidationError, api_exception_handler)
api.add_exception_handler(HttpError, api_exception_handler)
api.add_exception_handler(Exception, api_exception_handler)

# 動的APIルーティングを読み込み
dynamic_router = DynamicAPIRouting.get_router()

#new or old
api_switcher = "old"

if api_switcher == "old":
    api.add_router('posts', posts_router)
    api.add_router('users', users_router)
    api.add_router('polls', polls_router)
    api.add_router('events', events_router)
    api.add_router('calendar', calendar_router)
    api.add_router('chat', chat_router)
    api.add_router('circle', circle_router)
    api.add_router('emojis', emojis_router)
    api.add_router('announcement', announcement_router)
    api.add_router('notifications', notifications_router)
    api.add_router('organizations', organizations_router)
    api.add_router('tests', tests_router)
    api.add_router('pm', private_message_router)
    api.add_router('search', search_router)
    api.add_router('storage', storage_router)
    api.add_router('room_messages', room_messages_router)
    api.add_router('relations', relations_router)
    api.add_router('setup', setup_router)
    api.register_controllers(NinjaJWTDefaultController)
else:
    api_v1.add_router('', dynamic_router)
    api_v1.register_controllers(NinjaJWTDefaultController)

# カスタム404ハンドラーを追加
from django.urls import re_path

if api_switcher == "old":
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/', api.urls, name='api'),
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/v1/', api_v1.urls, name='api_v1'),
    ]

# 開発環境でのメディアファイル配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# カスタム404ハンドラーを最後に追加
urlpatterns.append(re_path(r'^.*$', api_404_handler, name='api_404'))

# カスタム404ハンドラー
handler404 = 'shared.handlers.custom_404_handler'
handler500 = 'shared.handlers.custom_500_handler'
handler403 = 'shared.handlers.custom_403_handler'
