from django.db import models
from shared.abstract_models import AbstractBaseModel

# Create your models here.
class Permission(AbstractBaseModel):
    subject = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    object = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.subject} {self.action} {self.object}"