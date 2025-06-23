import json
from django.shortcuts import render
from ninja import Router
from .models import UserProfile, UserProfileManager, User
from .schemas import UserProfileSchema
from ninja_jwt.authentication import JWTAuth
from .services import get_user_permission
# Create your views here.

router = Router(tags=['users'])

@router.get('/profile/{user_id}', response=UserProfileSchema)
def get_user_profile(request, user_id: str):
    user, profile = UserProfile.objects.get_userdata_and_profile(user_id)
    return UserProfileSchema.from_profile(profile)

@router.get('/profile', response=UserProfileSchema, auth=JWTAuth())

def get_current_user_profile(request):
    user, profile = UserProfile.objects.get_userdata_and_profile(request.user.id)
    return UserProfileSchema.from_profile(profile)

@router.get('/permission', auth=JWTAuth())
def get_user_permission_view(request):
    return get_user_permission(request.user.id)

@router.get('/random/{amount}', response=list[UserProfileSchema])
def get_random_users(request, amount):
    amount = int(amount)
    users = User.objects.get_users_randomly(amount)
    return [UserProfileSchema.from_profile(user.profile) for user in users]