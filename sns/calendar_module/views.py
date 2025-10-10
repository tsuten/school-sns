from django.shortcuts import render
from .models import Calendar, Schedule, NewSchedule
from ninja import Router
from .schemas import CalendarSchema, ScheduleSchema, NewScheduleSchema, NewScheduleCreateSchema, NewScheduleUpdateSchema
from ninja_jwt.authentication import JWTAuth
import uuid
from django.http import Http404
from ninja.errors import HttpError
from django.db.models import Q

router = Router(tags=['calendar'])

@router.get('/calendars', response=list[CalendarSchema], auth=JWTAuth())
def get_calendars(request):
    return Calendar.objects.get_calendar_by_user(request.user)

@router.get('/schedules/{calendar_id}/{year}/{month}', response=list[ScheduleSchema], auth=JWTAuth())
def get_schedules(request, calendar_id: uuid.UUID, year: int, month: int):
    return Schedule.objects.get_schedule_by_calendar(calendar_id, year, month)

@router.get('/new-schedules/{year}/{month}', response=list[NewScheduleSchema], auth=JWTAuth())
def get_new_schedules_by_month(request, year: int, month: int):
    """指定された年月の全てのNewScheduleを取得"""
    from datetime import datetime
    
    # 指定された年月の開始日と終了日を計算
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1)
    else:
        month_end = datetime(year, month + 1, 1)
    
    # スケジュールが指定された年月と重なる条件でフィルタリング
    schedules = NewSchedule.objects.filter(
        is_deleted=False
    ).filter(
        Q(start_time__gte=month_start, start_time__lt=month_end) |  # start_timeが月内
        Q(end_time__gte=month_start, end_time__lt=month_end) |      # end_timeが月内
        Q(start_time__lt=month_start, end_time__gte=month_end)      # 月全体をまたぐ
    )
    
    # ユーザーIDだけを含む辞書のリストを作成
    result = []
    for schedule in schedules:
        result.append({
            'id': schedule.id,
            'user': schedule.user.id,  # ユーザーIDだけを設定
            'title': schedule.title,
            'description': schedule.description,
            'is_all_day': schedule.is_all_day,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time,
            'created_at': schedule.created_at,
            'updated_at': schedule.updated_at,
        })
    
    return result

# NewSchedule CRUD operations
@router.get('/new-schedules', response=list[NewScheduleSchema], auth=JWTAuth())
def get_new_schedules(request):
    """ユーザーのNewSchedule一覧を取得"""
    schedules = NewSchedule.objects.get_schedules_by_user(request.user)
    
    # ユーザーIDだけを含む辞書のリストを作成
    result = []
    for schedule in schedules:
        result.append({
            'id': schedule.id,
            'user': schedule.user.id,  # ユーザーIDだけを設定
            'title': schedule.title,
            'description': schedule.description,
            'is_all_day': schedule.is_all_day,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time,
            'created_at': schedule.created_at,
            'updated_at': schedule.updated_at,
        })
    
    return result

@router.get('/new-schedules/{schedule_id}', response=NewScheduleSchema, auth=JWTAuth())
def get_new_schedule(request, schedule_id: uuid.UUID):
    """特定のNewScheduleを取得"""
    schedule = NewSchedule.objects.get_schedule_by_id(schedule_id, request.user)
    if not schedule:
        raise HttpError(404, "Schedule not found")
    
    # ユーザーIDだけを含む辞書を作成
    return {
        'id': schedule.id,
        'user': schedule.user.id,  # ユーザーIDだけを設定
        'title': schedule.title,
        'description': schedule.description,
        'is_all_day': schedule.is_all_day,
        'start_time': schedule.start_time,
        'end_time': schedule.end_time,
        'created_at': schedule.created_at,
        'updated_at': schedule.updated_at,
    }

@router.post('/new-schedules', response=NewScheduleSchema, auth=JWTAuth())
def create_new_schedule(request, payload: NewScheduleCreateSchema):
    """新しいNewScheduleを作成"""
    schedule = NewSchedule.objects.create(
        user=request.user,
        title=payload.title,
        description=payload.description or "",
        is_all_day=payload.is_all_day,
        start_time=payload.start_time,
        end_time=payload.end_time
    )
    
    # ユーザーIDだけを含む辞書を作成
    return {
        'id': schedule.id,
        'user': schedule.user.id,  # ユーザーIDだけを設定
        'title': schedule.title,
        'description': schedule.description,
        'is_all_day': schedule.is_all_day,
        'start_time': schedule.start_time,
        'end_time': schedule.end_time,
        'created_at': schedule.created_at,
        'updated_at': schedule.updated_at,
    }

@router.put('/new-schedules/{schedule_id}', response=NewScheduleSchema, auth=JWTAuth())
def update_new_schedule(request, schedule_id: uuid.UUID, payload: NewScheduleUpdateSchema):
    """NewScheduleを更新"""
    schedule = NewSchedule.objects.get_schedule_by_id(schedule_id, request.user)
    if not schedule:
        raise HttpError(404, "Schedule not found")
    
    # 更新可能なフィールドのみ更新
    if payload.title is not None:
        schedule.title = payload.title
    if payload.description is not None:
        schedule.description = payload.description
    if payload.is_all_day is not None:
        schedule.is_all_day = payload.is_all_day
    if payload.start_time is not None:
        schedule.start_time = payload.start_time
    if payload.end_time is not None:
        schedule.end_time = payload.end_time
    
    schedule.save()
    
    # ユーザーIDだけを含む辞書を作成
    return {
        'id': schedule.id,
        'user': schedule.user.id,  # ユーザーIDだけを設定
        'title': schedule.title,
        'description': schedule.description,
        'is_all_day': schedule.is_all_day,
        'start_time': schedule.start_time,
        'end_time': schedule.end_time,
        'created_at': schedule.created_at,
        'updated_at': schedule.updated_at,
    }

@router.delete('/new-schedules/{schedule_id}', auth=JWTAuth())
def delete_new_schedule(request, schedule_id: uuid.UUID):
    """NewScheduleを削除（論理削除）"""
    schedule = NewSchedule.objects.get_schedule_by_id(schedule_id, request.user)
    if not schedule:
        raise HttpError(404, "Schedule not found")
    
    schedule.delete_object()  # 論理削除
    return {"success": True, "message": "Schedule deleted successfully"}