"""
URL configuration for sns project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI, Redoc
from posts.views import router as posts_router
from users.views import router as users_router
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI
from polls.views import router as polls_router
api = NinjaExtraAPI(title='SNS API', version='1.0.0', docs=Redoc())
api.add_router('posts', posts_router)
api.add_router('users', users_router)
api.add_router('polls', polls_router)
api.register_controllers(NinjaJWTDefaultController)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls, name='api'),
]

# 開発環境でのメディアファイル配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
