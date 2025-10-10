from django.db import models
import uuid
from django.conf import settings
from shared.abstract_models import AbstractBaseModel
from .notification_types import NotificationType

class NotificationManager(models.Manager):
    def get_notifications(self, user, include_deleted=False):
        """通知一覧を取得（論理削除を考慮）"""
        queryset = self.filter(user=user)
        if not include_deleted:
            queryset = queryset.filter(is_deleted=False)
        return queryset
    
    def issue_notification(self, user, type, content, href_web=None, issued_by=None):
        notification = self.create(
            user=user,
            type=type,
            content=content,
            href_web=href_web,
            issued_by=issued_by
        )
        notification.save()
        return notification
    
    def update_read_status(self, notification_id, user, is_read):
        """個別通知の既読状態を更新"""
        try:
            notification = self.get(id=notification_id, user=user, is_deleted=False)
            notification.is_read = is_read
            notification.save()
            return True, "通知の既読状態を更新しました", 1
        except self.model.DoesNotExist:
            return False, "指定された通知が見つかりません", 0
        except Exception as e:
            return False, f"既読状態の更新に失敗しました: {str(e)}", 0
    
    def bulk_update_read_status(self, notification_ids, user):
        """複数通知を一括で既読にする"""
        try:
            updated_count = self.filter(
                id__in=notification_ids,
                user=user,
                is_deleted=False
            ).update(is_read=True)
            return True, f"{updated_count}件の通知を既読にしました", updated_count
        except Exception as e:
            return False, f"一括既読の更新に失敗しました: {str(e)}", 0
    
    def mark_all_read(self, user):
        """全通知を既読にする"""
        try:
            updated_count = self.filter(
                user=user,
                is_read=False,
                is_deleted=False
            ).update(is_read=True)
            return True, f"全{updated_count}件の通知を既読にしました", updated_count
        except Exception as e:
            return False, f"全件既読の更新に失敗しました: {str(e)}", 0
    
    def delete_notification(self, notification_id, user):
        """個別通知を論理削除"""
        try:
            notification = self.get(id=notification_id, user=user, is_deleted=False)
            notification.delete_object()
            return True, "通知を削除しました", 1
        except self.model.DoesNotExist:
            return False, "指定された通知が見つかりません", 0
        except Exception as e:
            return False, f"通知の削除に失敗しました: {str(e)}", 0
    
    def bulk_delete_notifications(self, notification_ids, user):
        """複数通知を一括で論理削除"""
        try:
            notifications = self.filter(
                id__in=notification_ids,
                user=user,
                is_deleted=False
            )
            updated_count = 0
            for notification in notifications:
                notification.delete_object()
                updated_count += 1
            return True, f"{updated_count}件の通知を削除しました", updated_count
        except Exception as e:
            return False, f"一括削除に失敗しました: {str(e)}", 0
    
    def restore_notification(self, notification_id, user):
        """削除した通知を復元"""
        try:
            notification = self.get(id=notification_id, user=user, is_deleted=True)
            notification.restore_object()
            return True, "通知を復元しました", 1
        except self.model.DoesNotExist:
            return False, "指定された削除済み通知が見つかりません", 0
        except Exception as e:
            return False, f"通知の復元に失敗しました: {str(e)}", 0
    
    def get_unread_count(self, user):
        """ユーザーの未読通知数を取得"""
        return self.filter(
            user=user,
            is_read=False,
            is_deleted=False
        ).count()
    
    def get_unread_count_by_type(self, user):
        """タイプ別の未読通知数を取得"""
        from django.db.models import Count
        return self.filter(
            user=user,
            is_read=False,
            is_deleted=False
        ).values('type').annotate(count=Count('type')).order_by('type')
    
    def get_notification_stats(self, user):
        """ユーザーの通知統計情報を取得"""
        total_count = self.filter(user=user, is_deleted=False).count()
        unread_count = self.get_unread_count(user)
        read_count = total_count - unread_count
        deleted_count = self.filter(user=user, is_deleted=True).count()
        
        return {
            'total_count': total_count,
            'unread_count': unread_count,
            'read_count': read_count,
            'deleted_count': deleted_count
        }

class Notification(AbstractBaseModel):
    issued_by = models.UUIDField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=NotificationType.choices, null=True, blank=True)
    content = models.TextField(default="")
    href_web = models.CharField(max_length=255, default="", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    objects = NotificationManager()