from django.shortcuts import render
from django.utils import timezone
from ninja import Router
from .models import Class, School, Organization
from users.schemas import UserProfileSchema, ClassSchema
from .schemas import ClassInfoSchema
from .utils import OrganizationManagerService
from shared.decorators import with_base_schema
from shared.base_schemas import Status
from typing import List, Dict, Any
from ninja_jwt.authentication import JWTAuth    
import uuid

router = Router(tags=["organizations"])

@router.get("/members/{class_id}", response=List[UserProfileSchema])
@with_base_schema
def get_members(request, class_id: str):
    members = Class.objects.get_members(class_id)
    return [UserProfileSchema.from_user(member) for member in members]

@router.get("/my_classes", response=List[ClassSchema], auth=JWTAuth())
@with_base_schema
def get_my_classes(request):
    classes = Class.objects.get_user_classes(request.user.id)
    return [ClassSchema.from_class(class_obj) for class_obj in classes]

@router.get("/class_info/{class_id}", response=ClassInfoSchema, auth=JWTAuth())
@with_base_schema
def get_class_info(request, class_id: str):
    class_obj = Class.objects.get_class_info(class_id)
    return ClassInfoSchema.from_class(class_obj)

@router.get("/is_manager/{class_id}", response=bool, auth=JWTAuth())
@with_base_schema
def is_manager(request, class_id: str):
    return Class.objects.is_manager(request.user.id, class_id)

@router.get("/organization_type/{organization_id}", auth=JWTAuth())
@with_base_schema
def get_organization_type(request, organization_id):
    """組織タイプを明示的に取得"""
    organization_type = Organization.objects.get_organization_type_by_id(organization_id=organization_id)
    return {
        "organization_type": str(organization_type)
    }

@router.get("/organization/{organization_id}/check_membership/{user_id}", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def check_user_membership(request, organization_id: str, user_id: str, org_type: str = None):
    """明示的な分岐によるメンバーシップチェック"""
    is_member = Organization.objects.get_user_is_member(user_id, organization_id, org_type)
    is_manager = Organization.objects.get_user_is_manager(user_id, organization_id, org_type)
    role = Organization.objects.get_user_role(user_id, organization_id, org_type)
    
    return {
        "is_member": is_member,
        "is_manager": is_manager,
        "role": role,
        "organization_id": organization_id,
        "user_id": user_id
    }

@router.get("/organization/{organization_id}/members_explicit", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def get_organization_members_explicit(request, organization_id: str, org_type: str = None):
    """明示的な分岐による組織メンバー取得"""
    members_data = Organization.objects.get_organization_members(organization_id, org_type)
    
    return {
        "managers": [UserProfileSchema.from_user(user) for user in members_data['managers']],
        "members": [UserProfileSchema.from_user(user) for user in members_data['members']],
        "managers_count": members_data['managers_count'],
        "members_count": members_data['members_count'],
        "organization_type": members_data['organization_type'],
        "organization_name": members_data['organization_name']
    }

@router.post("/organization/{organization_id}/add_user_explicit", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def add_user_explicit(request, organization_id: str, user_id: str, role: str = 'member', org_type: str = None):
    """明示的な分岐によるユーザー追加"""
    success = Organization.objects.add_user_to_organization(user_id, organization_id, role, org_type)
    return {
        "success": success,
        "organization_id": organization_id,
        "user_id": user_id,
        "role": role
    }

@router.post("/organization/{organization_id}/remove_user_explicit", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def remove_user_explicit(request, organization_id: str, user_id: str, role: str = None, org_type: str = None):
    """明示的な分岐によるユーザー削除"""
    success = Organization.objects.remove_user_from_organization(user_id, organization_id, role, org_type)
    return {
        "success": success,
        "organization_id": organization_id,
        "user_id": user_id,
        "role": role
    }

# OrganizationManagerServiceを使用した新しいエンドポイント

@router.get("/organization/{organization_id}/members_info", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def get_organization_members_info(request, organization_id: str, org_type: str = None):
    """組織のメンバー情報を役割付きで取得"""
    members_info = OrganizationManagerService.get_members_with_role_info(organization_id, org_type)
    return {
        "managers": [UserProfileSchema.from_user(user) for user in members_info['managers']],
        "members": [UserProfileSchema.from_user(user) for user in members_info['members']],
        "managers_count": members_info['managers_count'],
        "members_count": members_info['members_count'],
        "total_count": members_info['total_count']
    }

@router.get("/user/{user_id}/organizations", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def get_user_organizations(request, user_id: str):
    """ユーザーが所属する全組織を役割付きで取得"""
    organizations_data = OrganizationManagerService.get_user_organizations_with_role(user_id)
    
    # レスポンス用にシリアライズ
    return {
        "classes": {
            "managed": [
                {
                    "organization": ClassSchema.from_class(item['organization']),
                    "role": item['role'],
                    "members_count": item['members_count'],
                    "managers_count": item['managers_count']
                } for item in organizations_data['classes']['managed']
            ],
            "member": [
                {
                    "organization": ClassSchema.from_class(item['organization']),
                    "role": item['role'],
                    "members_count": item['members_count'],
                    "managers_count": item['managers_count']
                } for item in organizations_data['classes']['member']
            ]
        },
        "schools": {
            "managed": organizations_data['schools']['managed'],
            "member": organizations_data['schools']['member']
        }
    }

@router.post("/organization/{organization_id}/add_user", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def add_user_to_organization(request, organization_id: str, user_id: str, role: str = 'member', org_type: str = None):
    """組織にユーザーを追加"""
    success = OrganizationManagerService.add_user_to_organization(organization_id, user_id, role, org_type)
    return {"success": success}

@router.post("/organization/{organization_id}/remove_user", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def remove_user_from_organization(request, organization_id: str, user_id: str, role: str = None, org_type: str = None):
    """組織からユーザーを削除"""
    success = OrganizationManagerService.remove_user_from_organization(organization_id, user_id, role, org_type)
    return {"success": success}

@router.post("/organization/{organization_id}/change_role", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def change_user_role(request, organization_id: str, user_id: str, new_role: str, org_type: str = None):
    """ユーザーの役割を変更"""
    success = OrganizationManagerService.change_user_role(organization_id, user_id, new_role, org_type)
    return {"success": success}

@router.get("/organization/{organization_id}/stats", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def get_organization_stats(request, organization_id: str, org_type: str = None):
    """組織の統計情報を取得"""
    stats = OrganizationManagerService.get_organization_stats(organization_id, org_type)
    if stats:
        return stats
    else:
        return {
            'status': Status.ERROR.value,
            'timestamp': timezone.now(),
            'data': None,
            'error': 'Organization not found'
        }

@router.get("/user/{user_id}/organizations_by_permission", response=List[Dict[str, Any]], auth=JWTAuth())
@with_base_schema
def search_organizations_by_permission(request, user_id: str, permission_level: str = 'member'):
    """ユーザーの権限レベルに基づいて組織を検索"""
    organizations = OrganizationManagerService.search_organizations_by_user_permission(user_id, permission_level)
    
    result = []
    for org in organizations:
        if hasattr(org, 'class_number'):  # Classの場合
            result.append({
                "type": "class",
                "data": ClassSchema.from_class(org)
            })
        else:  # Schoolの場合
            result.append({
                "type": "school", 
                "data": {
                    "id": str(org.id),
                    "name": org.name,
                    "location": org.location,
                    "phone": org.phone,
                    "email": org.email,
                    "website": org.website
                }
            })
    
    return result

# 動的組織管理の新しいエンドポイント

@router.get("/organization/{organization_id}/methods", response=List[Dict[str, Any]], auth=JWTAuth())
@with_base_schema
def get_available_methods(request, organization_id: str, org_type: str = None):
    """組織で利用可能なメソッド一覧を取得"""
    methods = OrganizationManagerService.get_available_methods(organization_id, org_type)
    return methods

@router.post("/organization/{organization_id}/execute_method", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def execute_organization_method(request, organization_id: str, method_name: str, 
                               org_type: str = None, args: List[Any] = None, kwargs: Dict[str, Any] = None):
    """動的に組織のメソッドを実行"""
    args = args or []
    kwargs = kwargs or {}
    
    result = OrganizationManagerService.execute_organization_method(
        organization_id, method_name, *args, org_type=org_type, **kwargs
    )
    
    return {
        "success": True,
        "result": result,
        "method": method_name,
        "organization_id": organization_id
    }

@router.post("/organization/batch_operations", response=List[Dict[str, Any]], auth=JWTAuth())
@with_base_schema
def batch_execute_operations(request, operations: List[Dict[str, Any]]):
    """複数の組織操作をバッチで実行"""
    results = OrganizationManagerService.batch_execute_methods(operations)
    return results

@router.post("/organization/{organization_id}/smart_member_operation", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def smart_member_operation(request, organization_id: str, user_id: str, operation: str,
                          role: str = None, org_type: str = None):
    """スマートなメンバー操作（動的メソッド選択）"""
    result = OrganizationManagerService.smart_member_operation(
        organization_id, user_id, operation, role, org_type
    )
    return {
        "success": True,
        "result": result,
        "operation": operation,
        "user_id": user_id,
        "organization_id": organization_id
    }

@router.get("/user/{user_id}/cross_organization_analysis", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def cross_organization_analysis(request, user_id: str):
    """複数組織をまたいだユーザー分析"""
    analysis = OrganizationManagerService.cross_organization_analysis(user_id)
    return {"analysis": analysis}

@router.get("/organization/{organization_id}/auto_detect_type", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def auto_detect_organization_type(request, organization_id: str):
    """組織タイプを自動検出"""
    org_type = OrganizationManagerService.auto_detect_organization_type(organization_id)
    return {
        "organization_id": organization_id,
        "detected_type": org_type
    }

@router.get("/organization_models/registry", response=Dict[str, Any], auth=JWTAuth())
@with_base_schema
def get_organization_models_registry(request):
    """登録済み組織モデルの一覧を取得"""
    registry = OrganizationManagerService.get_registered_models()
    
    registry_info = {}
    for org_type, model_class in registry.items():
        registry_info[org_type] = {
            "model_name": model_class.__name__,
            "app_label": model_class._meta.app_label,
            "verbose_name": model_class._meta.verbose_name,
            "verbose_name_plural": model_class._meta.verbose_name_plural
        }
    
    return {"registry": registry_info}