from django.contrib import admin
from .models import Event, WhoWantsToParticipate

# Register your models here.

admin.site.register(Event)
admin.site.register(WhoWantsToParticipate)
