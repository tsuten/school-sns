from django.shortcuts import render
from ninja import Router
from .models import Event
from .schemas import EventSchema, EventCreateInputSchema
from typing import List
from ninja_jwt.authentication import JWTAuth

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

@router.post('/create', auth=JWTAuth(), response=EventSchema)
def create_event(request, payload: EventCreateInputSchema):
    event = Event.objects.create_event(
        organizer=request.user,
        title=payload.title,
        description=payload.description,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
        location=payload.location,
        published=payload.published
    )
    return event