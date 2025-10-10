from django.shortcuts import render
from .models import Notification
from .notification_types import NotificationType, NOTIFICATION_CATEGORIES
from ninja import Router, Query
from .schemas import NotificationSchema, NotificationReadUpdateSchema, BulkReadUpdateSchema, ReadStatusResponse, NotificationFilterSchema, NotificationCategorySchema, BulkDeleteSchema, DeleteStatusResponse, NotificationStatsSchema, UnreadCountByTypeSchema
from typing import List
from ninja_jwt.authentication import JWTAuth
from shared.decorators import with_base_schema
import uuid

router = Router(tags=['notifications'])

# Create your views here.
@router.get('/', auth=JWTAuth())
@with_base_schema
def get_notifications(request, filters: NotificationFilterSchema = Query(...)):
    """通知一覧を取得（フィルタ・ページネーション対応）"""
    queryset = Notification.objects.get_notifications(request.user)
    
    # タイプフィルタ
    if filters.type:
        queryset = queryset.filter(type=filters.type)
    
    # 既読状態フィルタ
    if filters.is_read is not None:
        queryset = queryset.filter(is_read=filters.is_read)
    
    # 並び順（新しい順）
    queryset = queryset.order_by('-created_at')
    
    # ページネーション
    start = filters.offset or 0
    end = start + (filters.limit or 20)
    
    # モデルインスタンスを辞書に変換
    notifications = queryset[start:end]
    return [
        {
            "id": str(notification.id),
            "type": notification.type,
            "content": notification.content,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "issued_by": str(notification.issued_by) if notification.issued_by else None,
            "href_web": notification.href_web
        }
        for notification in notifications
    ]

@router.get('/categories', auth=JWTAuth())
@with_base_schema
def get_notification_categories(request):
    """通知のカテゴリ別集計を取得"""
    notifications = Notification.objects.get_notifications(request.user)
    
    result = []
    for category_name, notification_types in NOTIFICATION_CATEGORIES.items():
        # 列挙型の値を文字列に変換
        type_values = [nt.value for nt in notification_types]
        count = notifications.filter(type__in=type_values).count()
        
        if count > 0:
            result.append({
                "category": category_name,
                "count": count,
                "types": type_values
            })
    
    # その他カテゴリ（定義されていないタイプ）
    all_defined_types = []
    for notification_types in NOTIFICATION_CATEGORIES.values():
        all_defined_types.extend([nt.value for nt in notification_types])
    
    other_count = notifications.exclude(type__in=all_defined_types).count()
    if other_count > 0:
        other_types = list(notifications.exclude(type__in=all_defined_types).values_list('type', flat=True).distinct())
        result.append({
            "category": 'その他',
            "count": other_count,
            "types": other_types
        })
    
    return result

@router.get('/types', auth=JWTAuth())
@with_base_schema
def get_notification_types(request):
    """利用可能な通知タイプ一覧を取得"""
    return [
        {"value": choice[0], "label": choice[1]} 
        for choice in NotificationType.choices
    ]

@router.patch('/{uuid:notification_id}/read', auth=JWTAuth())
@with_base_schema
def update_notification_read_status(request, notification_id: uuid.UUID, payload: NotificationReadUpdateSchema):
    """個別通知の既読状態を更新"""
    success, message, updated_count = Notification.objects.update_read_status(
        notification_id=notification_id,
        user=request.user,
        is_read=payload.is_read
    )
    
    return {
        "success": success,
        "message": message,
        "updated_count": updated_count
    }

@router.patch('/bulk-read', auth=JWTAuth())
@with_base_schema
def bulk_update_read_status(request, payload: BulkReadUpdateSchema):
    """複数通知を一括で既読にする"""
    success, message, updated_count = Notification.objects.bulk_update_read_status(
        notification_ids=payload.notification_ids,
        user=request.user
    )
    
    return {
        "success": success,
        "message": message,
        "updated_count": updated_count
    }

@router.patch('/mark-all-read', auth=JWTAuth())
@with_base_schema
def mark_all_notifications_read(request):
    """全通知を既読にする"""
    success, message, updated_count = Notification.objects.mark_all_read(
        user=request.user
    )
    
    return {
        "success": success,
        "message": message,
        "updated_count": updated_count
    }

@router.delete('/{uuid:notification_id}', auth=JWTAuth())
@with_base_schema
def delete_notification(request, notification_id: uuid.UUID):
    """個別通知を論理削除"""
    success, message, deleted_count = Notification.objects.delete_notification(
        notification_id=notification_id,
        user=request.user
    )
    
    return {
        "success": success,
        "message": message,
        "deleted_count": deleted_count
    }

@router.delete('/bulk-delete', auth=JWTAuth())
@with_base_schema
def bulk_delete_notifications(request, payload: BulkDeleteSchema):
    """複数通知を一括で論理削除"""
    success, message, deleted_count = Notification.objects.bulk_delete_notifications(
        notification_ids=payload.notification_ids,
        user=request.user
    )
    
    return {
        "success": success,
        "message": message,
        "deleted_count": deleted_count
    }

@router.patch('/{uuid:notification_id}/restore', auth=JWTAuth())
@with_base_schema
def restore_notification(request, notification_id: uuid.UUID):
    """削除した通知を復元"""
    success, message, restored_count = Notification.objects.restore_notification(
        notification_id=notification_id,
        user=request.user
    )
    
    return {
        "success": success,
        "message": message,
        "restored_count": restored_count
    }

@router.get('/stats', auth=JWTAuth())
@with_base_schema
def get_notification_stats(request):
    """ユーザーの通知統計情報を取得"""
    stats = Notification.objects.get_notification_stats(request.user)
    return stats

@router.get('/unread-count', auth=JWTAuth())
@with_base_schema
def get_unread_count(request):
    """ユーザーの未読通知数を取得"""
    unread_count = Notification.objects.get_unread_count(request.user)
    return {"unread_count": unread_count}

@router.get('/unread-count-by-type', auth=JWTAuth())
@with_base_schema
def get_unread_count_by_type(request):
    """タイプ別の未読通知数を取得"""
    unread_by_type = list(Notification.objects.get_unread_count_by_type(request.user))
    return unread_by_type