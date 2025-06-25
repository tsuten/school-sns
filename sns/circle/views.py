from django.shortcuts import render
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .models import Circle, CircleCategory
from .schemas import CircleSchema, CircleCategorySchema

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
    try:
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