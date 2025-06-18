from django.shortcuts import render
from .models import Calendar, Schedule
from ninja import Router
from .schemas import CalendarSchema, ScheduleSchema
from ninja_jwt.authentication import JWTAuth
import uuid

router = Router(tags=['calendar'])

@router.get('/calendars', response=list[CalendarSchema], auth=JWTAuth())
def get_calendars(request):
    return Calendar.objects.get_calendar_by_user(request.user)

@router.get('/schedules/{calendar_id}/{year}/{month}', response=list[ScheduleSchema], auth=JWTAuth())
def get_schedules(request, calendar_id: uuid.UUID, year: int, month: int):
    return Schedule.objects.get_schedule_by_calendar(calendar_id, year, month)