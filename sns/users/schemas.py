from ninja import Schema
from datetime import datetime
from typing import Optional

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
    
class UserProfileUpdateSchema(Schema):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[str] = None
    location: Optional[str] = None
    birth_place: Optional[str] = None
    pfp: Optional[str] = None