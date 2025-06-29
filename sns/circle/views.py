from django.shortcuts import render
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .models import Circle, CircleCategory, CircleMessage, CircleMedia
from .schemas import CircleSchema, CircleCategorySchema, ResponseSchema, CircleMessageSchema, CircleMessageCreateSchema, CircleMediaCreateSchema, CircleMediaSchema
from ninja.files import UploadedFile

# Create your views here.
router = Router(tags=['circle'])

@router.get("/you", auth=JWTAuth(), response=list[CircleSchema])
def get_circles(request):
    circles = Circle.objects.get_circles_by_user(request.user).prefetch_related('tags')
    return circles

@router.get("/public", response=list[CircleSchema])
def get_public_circles(request):
    circles = Circle.objects.get_public_circles().prefetch_related('tags')
    return circles

@router.get("/category/{category}", response=list[CircleSchema])
def get_circles_by_category(request, category: str):
    circles = Circle.objects.get_circles_by_category(category).prefetch_related('tags')
    return circles

@router.get("/category", response=list[CircleCategorySchema])
def get_categories(request):
    categories = []
    for category_choice in CircleCategory.choices:
        category_value = category_choice[0]
        count = Circle.objects.filter(category=category_value).count()
        categories.append(CircleCategorySchema(category=category_value, circle_count=count))
    return categories

@router.get("/{circle_id}", response=CircleSchema)
def get_circle_detail(request, circle_id: str):
    import uuid
    try:
        # circle_idのUUID形式をバリデーション
        try:
            uuid.UUID(circle_id)
        except ValueError:
            from ninja.errors import HttpError
            raise HttpError(400, "サークルIDの形式が正しくありません")
            
        circle = Circle.objects.select_related('founder').prefetch_related('tags', 'members').get(id=circle_id)
        
        # 創始者を含む全メンバーを取得
        all_members = circle.get_all_members()
        
        # レスポンス用のデータを構築
        circle_data = {
            'id': circle.id,
            'name': circle.name,
            'description': circle.description,
            'founder': {
                'id': circle.founder.id,
                'username': circle.founder.username
            },
            'category': circle.category,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in circle.tags.all()],
            'members': [{'id': member.id, 'username': member.username} for member in all_members],
            'is_public': circle.is_public,
            'created_at': circle.created_at,
            'updated_at': circle.updated_at
        }
        
        return circle_data
    except Circle.DoesNotExist:
        from ninja.errors import HttpError
        raise HttpError(404, "サークルが見つかりません")
    
@router.post("/{circle_id}/join", auth=JWTAuth(), response=ResponseSchema)
def join_circle(request, circle_id: str):
    circle = Circle.objects.get(id=circle_id)
    return Circle.objects.join_circle(request.user, circle)

@router.post("/{circle_id}/leave", auth=JWTAuth(), response=ResponseSchema)
def leave_circle(request, circle_id: str):
    circle = Circle.objects.get(id=circle_id)
    return Circle.objects.leave_circle(request.user, circle)

@router.post("/{circle_id}/messages", auth=JWTAuth(), response=CircleMessageSchema)
def send_message(request, circle_id: str, data: CircleMessageCreateSchema):
    circle = Circle.objects.get(id=circle_id)
    message = CircleMessage.objects.create_message(circle, request.user, data.content)
    
    return {
        'id': message.id,
        'circle': message.circle.name,
        'user': message.user.username,
        'content': message.content,
        'created_at': message.created_at,
        'updated_at': message.updated_at
    }

@router.get("/{circle_id}/messages", auth=JWTAuth(), response=list[CircleMessageSchema])
def get_messages(request, circle_id: str):
    circle = Circle.objects.get(id=circle_id)
    messages = CircleMessage.objects.get_messages_by_circle(circle).select_related('user', 'circle')
    
    return [
        {
            'id': message.id,
            'circle': message.circle.name,
            'user': message.user.username,
            'content': message.content,
            'created_at': message.created_at,
            'updated_at': message.updated_at
        }
        for message in messages
    ]

@router.post("/{circle_id}/media", auth=JWTAuth(), response=CircleMediaSchema)
def upload_media(request, circle_id: str, file: UploadedFile):
    circle = Circle.objects.get(id=circle_id)
    media = CircleMedia.objects.create_media(circle, request.user, file)
    
    return {
        'id': media.id,
        'media': media.media.name,
        'circle': media.circle.name,
        'user': media.user.username,
        'path': media.media.url,
        'type': media.type,
        'label': media.label,
        'created_at': media.created_at,
        'updated_at': media.updated_at
    }

@router.get("/{circle_id}/is-member", auth=JWTAuth())
def is_member(request, circle_id: str):
    is_member = Circle.objects.is_member(request.user, circle_id)
    return {
        "circle_id": circle_id,
        "user_id": request.user.id,
        "is_member": is_member
    }

@router.get("/{circle_id}/activity", auth=JWTAuth())
def get_circle_activity(request, circle_id: str, limit: int = 50, until: str = None):
    """サークルのメッセージ、メディア、通知を統合して取得（ポインターページネーション対応）"""
    from datetime import datetime
    from django.utils import timezone
    from django.core.exceptions import ValidationError
    import uuid
    
    try:
        # circle_idのUUID形式をバリデーション
        try:
            uuid.UUID(circle_id)
        except ValueError:
            from ninja.errors import HttpError
            raise HttpError(400, "サークルIDの形式が正しくありません")
        
        # メンバーシップ確認
        if not Circle.objects.is_member(request.user, circle_id):
            from ninja.errors import HttpError
            raise HttpError(403, "このサークルのメンバーではありません")
        
        # untilパラメータをdatetimeに変換
        until_datetime = None
        if until:
            try:
                # ISO形式の文字列をdatetimeに変換
                until_datetime = datetime.fromisoformat(until.replace('Z', '+00:00'))
                if until_datetime.tzinfo is None:
                    until_datetime = timezone.make_aware(until_datetime)
            except ValueError:
                from ninja.errors import HttpError
                raise HttpError(400, "untilパラメータの形式が正しくありません")
        
        result = Circle.objects.get_circle_activity(circle_id, limit, until_datetime)
        
        # レスポンス形式を統一
        formatted_activities = []
        for activity in result['activities']:
            formatted_activity = {
                'id': activity['id'],
                'type': activity['activity_type'],
                'content': activity['activity_content'],
                'user': activity['activity_user'],
                'timestamp': activity['activity_timestamp'],
            }
            
            # メッセージの場合、追加情報を含める
            if activity['activity_type'] == 'message':
                formatted_activity.update({
                    'user_id': activity.get('user__id'),
                    'username': activity.get('user__username'),
                })
            
            formatted_activities.append(formatted_activity)
        
        return {
            'circle_id': circle_id,
            'activities': formatted_activities,
            'has_next': result['has_next'],
            'next_until': result['next_until'].isoformat() if result['next_until'] else None,
            'count': result['count']
        }
        
    except Circle.DoesNotExist:
        from ninja.errors import HttpError
        raise HttpError(404, "サークルが見つかりません")
    except ValidationError:
        from ninja.errors import HttpError
        raise HttpError(400, "サークルIDの形式が正しくありません")