import json
from django.shortcuts import render
from ninja import Router
from ninja.errors import HttpError
from .models import UserProfile, UserProfileManager, User, UserActivity, UserSettings
from .schemas import UserProfileSchema, UserProfileUpdateSchema, UserAffiliationSchema, UserThemeSettingsSchema, UserNotificationSettingsSchema, UserPrivacySettingsSchema, UserUnifiedSettingsSchema, UserSettingsResponseSchema
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



@router.get('/settings', auth=JWTAuth(), response=UserSettingsResponseSchema)
def get_user_settings(request):
    """ユーザー設定を取得する"""
    try:
        settings = UserSettings.objects.get_user_settings(request.user.id)
        return UserSettingsResponseSchema.from_settings(settings)
    except Exception:
        raise HttpError(400, "設定の取得に失敗しました")

@router.post('/settings', auth=JWTAuth(), response=dict)
def update_user_settings(request, payload: UserUnifiedSettingsSchema):
    """統合ユーザー設定更新エンドポイント - type.label形式で分岐処理"""
    try:
        settings = UserSettings.objects.get_user_settings(request.user.id)
        updated_settings = {}
        
        for key, value in payload.settings.items():
            if not isinstance(value, bool):
                raise HttpError(400, "無効な設定事項です")
                
            # type.label形式を解析
            if '.' not in key:
                raise HttpError(400, "無効な設定事項です")
                
            type_name, label = key.split('.', 1)
            
            if type_name == "theme":
                if label == "darkmode":
                    settings.is_dark_mode_enabled = value
                    updated_settings[key] = value
                else:
                    raise HttpError(400, "無効な設定事項です")
                    
            elif type_name == "notification":
                if label == "notification":
                    settings.is_notification_enabled = value
                    updated_settings[key] = value
                else:
                    raise HttpError(400, "無効な設定事項です")
                    
            elif type_name == "privacy":
                if label == "profile":
                    settings.is_profile_public = value
                    updated_settings[key] = value
                elif label == "birthday":
                    settings.is_birthday_public = value
                    updated_settings[key] = value
                elif label == "location":
                    settings.is_location_public = value
                    updated_settings[key] = value
                elif label == "activity":
                    settings.is_activity_public = value
                    updated_settings[key] = value
                else:
                    raise HttpError(400, "無効な設定事項です")
            else:
                raise HttpError(400, "無効な設定事項です")
        
        settings.save()
        
        return {
            "success": True,
            "message": "設定が正常に更新されました",
            "updated_settings": updated_settings
        }
        
    except Exception:
        raise HttpError(400, "無効な設定事項です")