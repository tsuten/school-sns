import json
from django.shortcuts import render
from ninja import Router
from .models import UserProfile, UserProfileManager, User, UserActivity, UserSettings
from .schemas import UserProfileSchema, UserProfileUpdateSchema, UserAffiliationSchema, UserThemeSettingsSchema, UserNotificationSettingsSchema, UserPrivacySettingsSchema
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

@router.post('/profile', auth=JWTAuth(), response=UserProfileSchema)
def set_user_profile(request, payload: UserProfileUpdateSchema):
    profile = UserProfile.objects.set_user_profile(request.user.id, **payload.dict())
    return UserProfileSchema.from_profile(profile)

@router.get('/affiliation', auth=JWTAuth(), response=UserAffiliationSchema)
def get_user_affiliation(request):
    classes, schools = UserActivity.objects.get_user_affiliation(request.user.id)
    return UserAffiliationSchema.from_affiliation(classes, schools)

@router.post('/settings/theme', auth=JWTAuth(), response=UserThemeSettingsSchema)
def set_user_theme(request, payload: UserThemeSettingsSchema):
    settings_changed = UserSettings.objects.set_theme_settings(request.user.id, payload.darkmode)
    return {"settings_changed": settings_changed, "darkmode": payload.darkmode}

@router.post('/settings/notification', auth=JWTAuth(), response=UserNotificationSettingsSchema)
def set_user_notification(request, payload: UserNotificationSettingsSchema):
    settings_changed = UserSettings.objects.set_notification_settings(request.user.id, payload.notification)
    return {"settings_changed": settings_changed, "notification": payload.notification}

@router.post('/settings/privacy', auth=JWTAuth(), response=UserPrivacySettingsSchema)
def set_user_privacy(request, payload: UserPrivacySettingsSchema):
    # 現在の設定を取得
    current_settings = UserSettings.objects.get_user_settings(request.user.id)
    
    # NULLでない値のみを更新用に設定
    profile = payload.profile if payload.profile is not None else current_settings.is_profile_public
    birthday = payload.birthday if payload.birthday is not None else current_settings.is_birthday_public
    location = payload.location if payload.location is not None else current_settings.is_location_public
    activity = payload.activity if payload.activity is not None else current_settings.is_activity_public
    
    # 設定を更新
    settings_changed = UserSettings.objects.set_privacy_settings(request.user.id, profile, birthday, location, activity)
    
    return {
        "settings_changed": settings_changed, 
        "profile": profile, 
        "birthday": birthday, 
        "location": location, 
        "activity": activity
    }