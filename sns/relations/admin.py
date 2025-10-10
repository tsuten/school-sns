from django.contrib import admin
from .models import Friend, FriendRequest, RelationManagement

# Register your models here.
admin.site.register(Friend)
admin.site.register(FriendRequest)
admin.site.register(RelationManagement)