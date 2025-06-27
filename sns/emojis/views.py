from django.shortcuts import render
from ninja import Router
from .models import Emoji
from .schemas import EmojiSchema, SimpleEmojiSchema

router = Router(tags=['emojis'])

@router.get("/", response=list[EmojiSchema])
def get_emojis(request):
    return Emoji.objects.all()

@router.get("/{circle_id}", response=list[SimpleEmojiSchema])
def get_emojis_by_circle(request, circle_id: str):
    return Emoji.objects.get_by_circle(circle_id)