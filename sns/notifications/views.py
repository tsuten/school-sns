from django.shortcuts import render
from .models import Notification
from ninja import Router
from .schemas import NotificationSchema
from typing import List
from ninja_jwt.authentication import JWTAuth

router = Router(tags=['notifications'])

# Create your views here.
@router.get('/notifications', response=List[NotificationSchema], auth=JWTAuth())
def get_notifications(request):
    notifications = Notification.objects.get_notifications(request.user)
    return notifications