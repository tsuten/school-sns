from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from .utils import Prefectures

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('username is required')
                
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser must have is_superuser=True')
        
        return self.create_user(username, password, **extra_fields)
    
    def get_users_randomly(self, amount: int):
        return self.order_by('?')[:amount]

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username
    
class UserProfileManager(models.Manager):
    def get_userdata_and_profile(self, user_id):
        user = User.objects.get(id=user_id)
        profile = UserProfile.objects.get(user=user)
        return user, profile
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=50, blank=True)
    pfp = models.ImageField(upload_to='pfp/', null=True, blank=True)
    bio = models.TextField(blank=True)
    birthday = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True, choices=Prefectures.get_prefecture_choices())
    birth_place = models.CharField(max_length=255, blank=True, null=True, choices=Prefectures.get_prefecture_choices())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserProfileManager()

    def __str__(self):
        return self.user.username
    