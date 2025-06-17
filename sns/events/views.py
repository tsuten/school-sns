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

@router.get('/previous_events', response=List[EventSchema])
def get_previous_events(request):
    events = Event.objects.get_previous_events()
    return events

@router.get('/next_events', response=List[EventSchema])
def get_next_events(request):
    events = Event.objects.get_next_events()
    return events