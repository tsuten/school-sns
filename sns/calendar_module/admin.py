from django.contrib import admin
from .models import Calendar, Schedule, NewSchedule

admin.site.register(Calendar)
admin.site.register(Schedule)
admin.site.register(NewSchedule)