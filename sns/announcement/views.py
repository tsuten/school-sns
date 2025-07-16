from django.shortcuts import render
from django.http import Http404
from .models import Announcement
from .schemas import AnnouncementPostSchema, AnnouncementResponseSchema
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from enrollments.models import School, Class
from typing import List

router = Router(tags=['announcement'])

@router.post('/announcement/post', response=AnnouncementResponseSchema, auth=JWTAuth())
def post_announcement(request, announcement: AnnouncementPostSchema):
    print("うんこ:", announcement.post_to)
    try:
        announcement_obj = Announcement.objects.post_announcement(
            title=announcement.title,
            content=announcement.content,
            posted_by=request.user,
            post_to=announcement.post_to,
            target=announcement.target,
            priority=announcement.priority,
        )
        return AnnouncementResponseSchema.from_announcement(announcement_obj)
    except (School.DoesNotExist, Class.DoesNotExist):
        raise Http404("指定されたターゲットが見つかりません")

@router.get('/announcements/{id}', response=List[AnnouncementResponseSchema])
def get_announcements(request, id: str):
    announcements = Announcement.objects.get_announcements(id)
    return [AnnouncementResponseSchema.from_announcement(announcement) for announcement in announcements]

@router.post('/announcement/{id}/read', auth=JWTAuth())
def read_announcement(request, id: str):
    response = Announcement.objects.read_announcement(request.user.id, id)
    return response