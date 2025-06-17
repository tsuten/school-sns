from django.shortcuts import render
from ninja import Router
from .models import Event
from .schemas import EventSchema
from typing import List

router = Router(tags=["events"])

@router.get('/held_events', response=List[EventSchema])
def get_held_events(request):
    events = Event.objects.get_held_events()
    return events

