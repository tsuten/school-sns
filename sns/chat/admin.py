from django.contrib import admin
from .models import Message, ClassMessage

# Register your models here.
admin.site.register(Message)
admin.site.register(ClassMessage)