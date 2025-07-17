from ninja import Schema
from datetime import datetime
from typing import Optional, List

class UserProfileSchema(Schema):
    # 関連するUserのフィールド
    user_id: str
    user_username: str


    # UserProfileのフィールド
    display_name: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[str] = None
    location: Optional[str] = None
    birth_place: Optional[str] = None
    pfp: Optional[str] = None  # プロフィール画像のURL
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_profile(cls, profile):
        """UserProfileインスタンスからスキーマを作成"""
        return cls(
            user_id=str(profile.user.id),
            user_username=profile.user.username,
            display_name=profile.display_name,
            bio=profile.bio,
            birthday=profile.birthday.isoformat() if profile.birthday else None,
            location=profile.location,
            birth_place=profile.birth_place,
            pfp=profile.pfp.url if profile.pfp else None,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
    
    @classmethod
    def from_user(cls, user):
        """UserインスタンスからUserProfileを取得してスキーマを作成"""
        try:
            profile = user.profile
            return cls.from_profile(profile)
        except:
            # プロフィールが存在しない場合のデフォルト値
            return cls(
                user_id=str(user.id),
                user_username=user.username,
                display_name=None,
                bio=None,
                birthday=None,
                location=None,
                birth_place=None,
                pfp=None,
                created_at=user.date_joined,
                updated_at=user.date_joined,
            )
    
class UserProfileUpdateSchema(Schema):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[str] = None
    location: Optional[str] = None
    birth_place: Optional[str] = None
    pfp: Optional[str] = None

class ClassSchema(Schema):
    id: str
    name: Optional[str] = None
    grade_number: Optional[int] = None
    class_number: Optional[int] = None
    school_id: Optional[str] = None
    school_name: Optional[str] = None

    @classmethod
    def from_class(cls, class_obj):
        """ClassオブジェクトからClassSchemaを作成"""
        return cls(
            id=str(class_obj.id),
            name=class_obj.name,
            grade_number=class_obj.grade_number,
            class_number=class_obj.class_number,
            school_id=str(class_obj.school.id) if class_obj.school else None,
            school_name=class_obj.school.name if class_obj.school else None,
        )

class SchoolSchema(Schema):
    id: str
    name: str
    location: Optional[str] = None

class UserAffiliationSchema(Schema):
    classes: List[ClassSchema]
    schools: List[SchoolSchema]

    @classmethod
    def from_affiliation(cls, classes, schools):
        # Classオブジェクトから ClassSchema への変換
        class_schemas = []
        for class_obj in classes:
            class_schemas.append(ClassSchema.from_class(class_obj))
        
        # Schoolオブジェクトから SchoolSchema への変換
        school_schemas = []
        # 重複を避けるために set を使用
        unique_schools = {school.id: school for school in schools if school}.values()
        for school in unique_schools:
            school_schemas.append(SchoolSchema(
                id=str(school.id),
                name=school.name,
                location=school.location,
            ))
        
        return cls(classes=class_schemas, schools=school_schemas)
    
class UserThemeSettingsSchema(Schema):
    darkmode: bool

class UserNotificationSettingsSchema(Schema):
    notification: bool

class UserPrivacySettingsSchema(Schema):
    profile: Optional[bool] = None
    birthday: Optional[bool] = None
    location: Optional[bool] = None
    activity: Optional[bool] = None