from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

class EventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def get_published_events(self):
        return self.get_queryset().filter(published=True)
    
    def get_held_events(self):
        return self.get_queryset().filter(start_datetime__lte=timezone.now(), end_datetime__gte=timezone.now(), is_cancelled=False, published=True) # 開催中のイベントを取得
    
    def get_previous_events(self, amount = 10):
        return self.get_queryset().filter(end_datetime__lt=timezone.now()).order_by('-end_datetime')[:amount] # 終了後のイベントを取得
    
    def get_next_events(self, amount = 10):
        return self.get_queryset().filter(start_datetime__gt=timezone.now()).order_by('start_datetime')[:amount] # 開始前のイベントを取得
    
    def create_event(self, organizer, title, description, start_datetime, end_datetime, location, published):
        return self.create(
            organizer=organizer,
            title=title,
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            published=published
        )

class Event(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=False)
    start_datetime = models.DateTimeField(blank=False, null=True, default=None)
    end_datetime = models.DateTimeField(blank=False, null=True, default=None)
    location = models.CharField(max_length=200, blank=False) #後々住所を選択式にする
    published = models.BooleanField(default=False)
#   public_range = 学校か全体かクラスか
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    is_deleted = models.BooleanField(default=False)

    objects = EventManager()

    class Meta:
        permissions = [
            ('unpublish_event', 'Can unpublish event'),
        ]

    def __str__(self):
        return self.title

# モデル名が長すぎる
# もっといいのがあれば変える
class WhoWantsToParticipate(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('event', 'user')
