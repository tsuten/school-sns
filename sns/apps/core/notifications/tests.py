from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import json
import uuid

from .models import Notification
from .notification_types import NotificationType
from ninja_jwt.tokens import AccessToken

User = get_user_model()


class NotificationModelTests(TestCase):
    """通知モデルのテスト"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_notification_creation(self):
        """通知の基本作成テスト"""
        notification = Notification.objects.create(
            user=self.user1,
            type=NotificationType.POST_LIKED,
            content="テスト通知",
            href_web="/test/url"
        )
        
        self.assertEqual(notification.user, self.user1)
        self.assertEqual(notification.type, NotificationType.POST_LIKED)
        self.assertEqual(notification.content, "テスト通知")
        self.assertEqual(notification.href_web, "/test/url")
        self.assertFalse(notification.is_read)
        self.assertIsInstance(notification.id, uuid.UUID)
    
    def test_get_notifications(self):
        """NotificationManager.get_notifications のテスト"""
        # user1に通知を作成
        Notification.objects.create(
            user=self.user1,
            type=NotificationType.MESSAGE,
            content="User1の通知1"
        )
        Notification.objects.create(
            user=self.user1,
            type=NotificationType.POST_LIKED,
            content="User1の通知2"
        )
        
        # user2に通知を作成
        Notification.objects.create(
            user=self.user2,
            type=NotificationType.MESSAGE,
            content="User2の通知"
        )
        
        # user1の通知のみ取得されることを確認
        user1_notifications = Notification.objects.get_notifications(self.user1)
        self.assertEqual(user1_notifications.count(), 2)
        
        # user2の通知のみ取得されることを確認
        user2_notifications = Notification.objects.get_notifications(self.user2)
        self.assertEqual(user2_notifications.count(), 1)
    
    def test_update_read_status(self):
        """既読状態更新のテスト"""
        notification = Notification.objects.create(
            user=self.user1,
            type=NotificationType.MESSAGE,
            content="テスト通知",
            is_read=False
        )
        
        # 既読に更新
        success, message, count = Notification.objects.update_read_status(
            notification_id=notification.id,
            user=self.user1,
            is_read=True
        )
        
        self.assertTrue(success)
        self.assertEqual(count, 1)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_mark_all_read(self):
        """全件既読のテスト"""
        # 複数の通知を作成
        Notification.objects.create(
            user=self.user1,
            type=NotificationType.MESSAGE,
            content="通知1",
            is_read=False
        )
        Notification.objects.create(
            user=self.user1,
            type=NotificationType.POST_LIKED,
            content="通知2",
            is_read=False
        )
        
        # 全件既読
        success, message, count = Notification.objects.mark_all_read(self.user1)
        
        self.assertTrue(success)
        self.assertEqual(count, 2)
        
        # 全て既読になっていることを確認
        unread_count = Notification.objects.filter(
            user=self.user1, 
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)


class NotificationAPITests(TestCase):
    """通知API エンドポイントのテスト"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # JWT トークンを生成
        self.access_token = AccessToken.for_user(self.user)
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        
        # テスト用通知を作成
        self.notification1 = Notification.objects.create(
            user=self.user,
            type=NotificationType.POST_LIKED,
            content="投稿にいいねされました",
            is_read=False
        )
        self.notification2 = Notification.objects.create(
            user=self.user,
            type=NotificationType.MESSAGE,
            content="新しいメッセージ",
            is_read=True
        )
    
    def test_get_notifications(self):
        """通知一覧取得のテスト"""
        response = self.client.get(
            '/api/notifications/',
            **self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 2)
    
    def test_get_notification_types(self):
        """通知タイプ一覧取得のテスト"""
        response = self.client.get(
            '/api/notifications/types',
            **self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    def test_update_read_status(self):
        """個別既読更新のテスト"""
        response = self.client.patch(
            f'/api/notifications/{self.notification1.id}/read',
            data=json.dumps({'is_read': True}),
            content_type='application/json',
            **self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['data']['success'])
        
        # DBで確認
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
    
    def test_unauthorized_access(self):
        """認証なしでのアクセステスト"""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 401)


class NotificationTypeTests(TestCase):
    """通知タイプ定義のテスト"""
    
    def test_notification_type_choices(self):
        """通知タイプの選択肢テスト"""
        choices = NotificationType.choices
        self.assertGreater(len(choices), 0)
        
        # 基本的なタイプが含まれていることを確認
        type_values = [choice[0] for choice in choices]
        self.assertIn('announcement', type_values)
        self.assertIn('message', type_values)
        self.assertIn('post_liked', type_values)


class NotificationDeleteTests(TestCase):
    """通知削除機能のテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.MESSAGE,
            content="削除テスト通知"
        )
    
    def test_delete_notification(self):
        """個別通知の論理削除テスト"""
        success, message, count = Notification.objects.delete_notification(
            notification_id=self.notification.id,
            user=self.user
        )
        
        self.assertTrue(success)
        self.assertEqual(count, 1)
        
        # DBで論理削除されていることを確認
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_deleted)
        self.assertIsNotNone(self.notification.deleted_at)
    
    def test_restore_notification(self):
        """削除した通知の復元テスト"""
        # まず削除
        self.notification.delete_object()
        self.assertTrue(self.notification.is_deleted)
        
        # 復元
        success, message, count = Notification.objects.restore_notification(
            notification_id=self.notification.id,
            user=self.user
        )
        
        self.assertTrue(success)
        self.assertEqual(count, 1)
        
        # DBで復元されていることを確認
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.is_deleted)
        self.assertIsNone(self.notification.deleted_at)
    
    def test_get_notifications_excludes_deleted(self):
        """削除済み通知が一覧に含まれないことを確認"""
        # 追加通知を作成
        Notification.objects.create(
            user=self.user,
            type=NotificationType.POST_LIKED,
            content="通常の通知"
        )
        
        # 1つを削除
        self.notification.delete_object()
        
        # 削除されていない通知のみ取得されることを確認
        notifications = Notification.objects.get_notifications(self.user)
        self.assertEqual(notifications.count(), 1)
        
        # 削除済みを含めて取得
        all_notifications = Notification.objects.get_notifications(self.user, include_deleted=True)
        self.assertEqual(all_notifications.count(), 2)
    
    def test_bulk_delete_notifications(self):
        """一括削除のテスト"""
        # 追加通知を作成
        notification2 = Notification.objects.create(
            user=self.user,
            type=NotificationType.POST_LIKED,
            content="通知2"
        )
        notification3 = Notification.objects.create(
            user=self.user,
            type=NotificationType.FRIEND_REQUEST,
            content="通知3"
        )
        
        # 一括削除
        success, message, count = Notification.objects.bulk_delete_notifications(
            notification_ids=[self.notification.id, notification2.id],
            user=self.user
        )
        
        self.assertTrue(success)
        self.assertEqual(count, 2)
        
        # 削除されたことを確認
        self.notification.refresh_from_db()
        notification2.refresh_from_db()
        notification3.refresh_from_db()
        
        self.assertTrue(self.notification.is_deleted)
        self.assertTrue(notification2.is_deleted)
        self.assertFalse(notification3.is_deleted)  # 削除対象外


class NotificationStatsTests(TestCase):
    """通知統計機能のテスト"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 各種状態の通知を作成
        self.unread_notification1 = Notification.objects.create(
            user=self.user,
            type=NotificationType.MESSAGE,
            content="未読通知1",
            is_read=False
        )
        self.unread_notification2 = Notification.objects.create(
            user=self.user,
            type=NotificationType.POST_LIKED,
            content="未読通知2",
            is_read=False
        )
        self.read_notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.MESSAGE,
            content="既読通知",
            is_read=True
        )
        
        # 削除済み通知
        deleted_notification = Notification.objects.create(
            user=self.user,
            type=NotificationType.FRIEND_REQUEST,
            content="削除済み通知"
        )
        deleted_notification.delete_object()
    
    def test_get_unread_count(self):
        """未読通知数取得のテスト"""
        unread_count = Notification.objects.get_unread_count(self.user)
        self.assertEqual(unread_count, 2)
    
    def test_get_unread_count_by_type(self):
        """タイプ別未読通知数取得のテスト"""
        unread_by_type = list(Notification.objects.get_unread_count_by_type(self.user))
        
        # 結果を辞書に変換して確認
        type_counts = {item['type']: item['count'] for item in unread_by_type}
        
        self.assertEqual(type_counts.get(NotificationType.MESSAGE), 1)
        self.assertEqual(type_counts.get(NotificationType.POST_LIKED), 1)
        self.assertNotIn(NotificationType.FRIEND_REQUEST, type_counts)  # 削除済みは含まれない
    
    def test_get_notification_stats(self):
        """通知統計情報取得のテスト"""
        stats = Notification.objects.get_notification_stats(self.user)
        
        self.assertEqual(stats['total_count'], 3)  # 削除済みを除く
        self.assertEqual(stats['unread_count'], 2)
        self.assertEqual(stats['read_count'], 1)
        self.assertEqual(stats['deleted_count'], 1)
    
    def test_unread_count_api(self):
        """未読数API のテスト"""
        from ninja_jwt.tokens import AccessToken
        
        access_token = AccessToken.for_user(self.user)
        auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {access_token}'
        }
        
        response = self.client.get(
            '/api/notifications/unread-count',
            **auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['unread_count'], 2)
    
    def test_stats_api(self):
        """統計情報API のテスト"""
        from ninja_jwt.tokens import AccessToken
        
        access_token = AccessToken.for_user(self.user)
        auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {access_token}'
        }
        
        response = self.client.get(
            '/api/notifications/stats',
            **auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        stats = data['data']
        self.assertEqual(stats['total_count'], 3)
        self.assertEqual(stats['unread_count'], 2)
        self.assertEqual(stats['read_count'], 1)
        self.assertEqual(stats['deleted_count'], 1)
