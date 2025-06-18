from django.shortcuts import render
from .models import Calendar, Schedule
from ninja import Router
from .schemas import CalendarSchema, ScheduleSchema
from ninja_jwt.authentication import JWTAuth

router = Router(tags=['calendar'])

@router.get('/calendars', response=list[CalendarSchema], auth=JWTAuth())
def get_calendars(request):
    return Calendar.objects.get_calendar_by_user(request.user)