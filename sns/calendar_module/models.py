from django.db import models
import uuid
from django.conf import settings
from datetime import datetime
from django.db.models import Q

class CalendarManager(models.Manager):
    def get_calendar_by_user(self, user):
        return self.get_queryset().filter(user=user)
    

class Calendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initial = models.CharField(max_length=1, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CalendarManager()

    def __str__(self):
        return self.name
    
class ScheduleManager(models.Manager):
    def get_schedule_by_calendar(self, calendar_id, year, month):
        # 指定された年月の開始日と終了日を計算
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
        
        # スケジュールが指定された年月と重なる条件：
        # 1. start_timeが月の範囲内にある
        # 2. end_timeが月の範囲内にある
        # 3. start_timeが月より前で、end_timeが月より後（月全体をまたぐ）
        return self.get_queryset().filter(
            calendar_id=calendar_id
        ).filter(
            Q(start_time__gte=month_start, start_time__lt=month_end) |  # start_timeが月内
            Q(end_time__gte=month_start, end_time__lt=month_end) |      # end_timeが月内
            Q(start_time__lt=month_start, end_time__gte=month_end)      # 月全体をまたぐ
        )
    
class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_all_day = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ScheduleManager()

    def __str__(self):
        return self.title