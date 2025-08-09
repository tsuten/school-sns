from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from ninja_jwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import uuid
import json

from .models import PrivateMessage, RoomMessage, RoomType
from apps.core.users.models import UserProfile

User = get_user_model()


class PrivateMessageModelTest(TestCase):
    """PrivateMessageモデルのテスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='pm_user1',
            email='pm_user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='pm_user2', 
            email='pm_user2@test.com',
            password='testpass123'
        )
        
        # UserProfileは自動作成される（signals.pyで設定済み）
        
    def test_create_message(self):
        """メッセージ作成テスト"""
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello World"
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Hello World")
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)
        self.assertFalse(message.is_deleted)
        
    def test_cannot_message_self(self):
        """自分自身にメッセージ送信できないテスト"""
        with self.assertRaises(ValidationError):
            PrivateMessage.objects.create(
                sender=self.user1,
                receiver=self.user1,
                content="Hello Self"
            )
            
    def test_mark_as_read(self):
        """既読機能テスト"""
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello"
        )
        
        # 既読にする
        message.mark_as_read()
        
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
        
    def test_mark_as_read_already_read(self):
        """既に既読のメッセージを既読にしようとした場合のテスト"""
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello"
        )
        
        # 既読にする
        message.mark_as_read()
        
        # 再度既読にしようとするとエラー
        with self.assertRaises(ValidationError):
            message.mark_as_read()
            
    def test_string_representation(self):
        """文字列表現のテスト"""
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test Content"
        )
        
        self.assertEqual(str(message), "Test Content")


class PrivateMessageManagerTest(TestCase):
    """PrivateMessageManagerのテスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='pmm_user1',
            email='pmm_user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='pmm_user2',
            email='pmm_user2@test.com', 
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='pmm_user3',
            email='pmm_user3@test.com',
            password='testpass123'
        )
        
        # UserProfileは自動作成される（signals.pyで設定済み）
            
        # テストメッセージ作成
        self.message1 = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1"
        )
        self.message2 = PrivateMessage.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 2"
        )
        self.message3 = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user3,
            content="Message 3"
        )
        
    def test_get_from_sender(self):
        """送信者でフィルタするテスト"""
        messages = PrivateMessage.objects.get_from_sender(self.user1.id)
        self.assertEqual(messages.count(), 2)
        
    def test_get_from_receiver(self):
        """受信者でフィルタするテスト"""
        messages = PrivateMessage.objects.get_from_receiver(self.user2.id)
        self.assertEqual(messages.count(), 1)
        
    def test_get_between_users(self):
        """ユーザー間のメッセージ取得テスト"""
        messages = PrivateMessage.objects.get_between_users(self.user1, self.user2)
        self.assertEqual(messages.count(), 2)
        
    def test_get_unread_count(self):
        """未読メッセージ数取得テスト"""
        unread_count = PrivateMessage.objects.get_unread_count(self.user2)
        self.assertEqual(unread_count, 1)  # user1からのメッセージ1件
        
        # メッセージを既読にする
        self.message1.mark_as_read()
        unread_count = PrivateMessage.objects.get_unread_count(self.user2)
        self.assertEqual(unread_count, 0)
        
    def test_get_latest_message_between_users(self):
        """ユーザー間の最新メッセージ取得テスト"""
        latest = PrivateMessage.objects.get_latest_message_between_users(
            self.user1, self.user2
        )
        self.assertEqual(latest, self.message2)  # 時間的に後に作成
        
    @patch('chat.signals.send_message_post_signal')
    def test_send_message(self, mock_signal):
        """メッセージ送信メソッドのテスト"""
        message = PrivateMessage.objects.send_message(
            sender=self.user1,
            receiver=self.user2,
            content="New message"
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "New message")
        
    @patch('chat.signals.send_message_update_signal')
    def test_mark_message_as_read(self, mock_signal):
        """既読処理メソッドのテスト"""
        message = PrivateMessage.objects.mark_message_as_read(self.message1.id)
        
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
        
    def test_mark_already_read_message(self):
        """既に既読のメッセージを既読処理しようとした場合のテスト"""
        self.message1.mark_as_read()
        
        with self.assertRaises(ValidationError):
            PrivateMessage.objects.mark_message_as_read(self.message1.id)
            
    @patch('chat.signals.send_message_delete_signal')
    def test_delete_message(self, mock_signal):
        """メッセージ削除メソッドのテスト"""
        message = PrivateMessage.objects.delete_message(self.message1.id)
        
        self.assertTrue(message.is_deleted)
        
    @patch('chat.signals.send_message_restore_signal')
    def test_restore_message(self, mock_signal):
        """メッセージ復元メソッドのテスト"""
        # 先に削除
        PrivateMessage.objects.delete_message(self.message1.id)
        
        # 復元
        message = PrivateMessage.objects.restore_message(self.message1.id)
        
        self.assertFalse(message.is_deleted)
        self.assertIsNone(message.deleted_at)
        
    def test_get_list_of_users_have_history_with_user(self):
        """メッセージ交信履歴取得テスト"""
        users_data = PrivateMessage.objects.get_list_of_users_have_history_with_user(
            self.user1
        )
        
        # user1はuser2とuser3とやり取りがある
        self.assertEqual(len(users_data), 2)
        
        # 最新メッセージ順でソートされているか確認
        user_ids = [data['user_id'] for data in users_data]
        # user3とのやり取りが最新なのでuser3が先頭
        self.assertEqual(user_ids[0], self.user3.id)


class RoomMessageModelTest(TestCase):
    """RoomMessageモデルのテスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='rm_user1',
            email='rm_user1@test.com',
            password='testpass123'
        )
        self.room_id = uuid.uuid4()
        
        # UserProfileは自動作成される（signals.pyで設定済み）
        
    def test_create_room_message(self):
        """ルームメッセージ作成テスト"""
        message = RoomMessage.objects.create(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            content="Hello Room"
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.room_type, RoomType.GROUP)
        self.assertEqual(message.room_id, self.room_id)
        self.assertEqual(message.content, "Hello Room")
        
    def test_string_representation(self):
        """文字列表現のテスト"""
        message = RoomMessage.objects.create(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            content="Test Room Content"
        )
        
        self.assertEqual(str(message), "Test Room Content")


class RoomMessageManagerTest(TestCase):
    """RoomMessageManagerのテスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='rmm_user1',
            email='rmm_user1@test.com',
            password='testpass123'
        )
        self.room_id = uuid.uuid4()
        
        # UserProfileは自動作成される（signals.pyで設定済み）
        
        # テストメッセージ作成
        self.message1 = RoomMessage.objects.create(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            content="Message 1"
        )
        self.message2 = RoomMessage.objects.create(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            content="Message 2"
        )
        
    def test_validate_room_exists_group(self):
        """グループルームの存在確認テスト（常にTrue）"""
        exists = RoomMessage.objects.validate_room_exists(RoomType.GROUP, self.room_id)
        self.assertTrue(exists)
        
    @patch('apps.core.organizations.organizations.models.Class.objects.filter')
    def test_validate_room_exists_class(self, mock_filter):
        """クラスルームの存在確認テスト"""
        mock_filter.return_value.exists.return_value = True
        
        exists = RoomMessage.objects.validate_room_exists(RoomType.CLASS, self.room_id)
        self.assertTrue(exists)
        
    def test_can_user_access_room_group(self):
        """グループルームアクセス権限テスト（常にTrue）"""
        can_access = RoomMessage.objects.can_user_access_room(
            self.user1, RoomType.GROUP, self.room_id
        )
        self.assertTrue(can_access)
        
    def test_get_messages_from_room(self):
        """ルームメッセージ取得テスト"""
        messages = RoomMessage.objects.get_messages_from_room(
            user=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id
        )
        
        self.assertEqual(messages.count(), 2)
        
    def test_get_messages_from_room_with_limit(self):
        """ルームメッセージ取得（制限付き）テスト"""
        messages = RoomMessage.objects.get_messages_from_room(
            user=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            limit=1
        )
        
        self.assertEqual(messages.count(), 1)
        
    def test_get_messages_from_nonexistent_room(self):
        """存在しないルームからのメッセージ取得テスト"""
        with patch.object(RoomMessage.objects, 'validate_room_exists', return_value=False):
            with self.assertRaises(ValidationError):
                RoomMessage.objects.get_messages_from_room(
                    user=self.user1,
                    room_type=RoomType.CLASS,
                    room_id=uuid.uuid4()
                )
                
    @patch('chat.signals.send_room_message_post_signal')
    def test_send_message(self, mock_signal):
        """ルームメッセージ送信テスト"""
        message = RoomMessage.objects.send_message(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            content="New room message"
        )
        
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.room_type, RoomType.GROUP)
        self.assertEqual(message.content, "New room message")
        
    def test_send_message_no_permission(self):
        """権限なしルームメッセージ送信テスト"""
        with patch.object(RoomMessage.objects, 'can_user_access_room', return_value=False):
            with self.assertRaises(ValidationError):
                RoomMessage.objects.send_message(
                    sender=self.user1,
                    room_type=RoomType.CLASS,
                    room_id=uuid.uuid4(),
                    content="Unauthorized message"
                )


@patch('websocket.unified_consumers.send_to_user')  
class PrivateMessageSignalTest(TestCase):
    """プライベートメッセージシグナル処理のテスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='pms_user1',
            email='pms_user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='pms_user2',
            email='pms_user2@test.com',
            password='testpass123'
        )
        
        # UserProfileは自動作成される（signals.pyで設定済み）
            
    def test_message_post_signal(self, mock_send_to_user):
        """メッセージ作成シグナルのテスト"""
        from .signals import send_message_post_signal
        
        mock_send_to_user.return_value = None
        
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Signal test message"
        )
        
        send_message_post_signal(message)
        
        # WebSocket送信が呼ばれたか確認
        self.assertTrue(mock_send_to_user.called)
        
    def test_message_update_signal(self, mock_send_to_user):
        """メッセージ更新シグナルのテスト"""
        from .signals import send_message_update_signal
        
        mock_send_to_user.return_value = None
        
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Update test message"
        )
        
        send_message_update_signal(message)
        
        self.assertTrue(mock_send_to_user.called)
        
    def test_message_delete_signal(self, mock_send_to_user):
        """メッセージ削除シグナルのテスト"""
        from .signals import send_message_delete_signal
        
        mock_send_to_user.return_value = None
        
        message = PrivateMessage.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Delete test message"
        )
        
        send_message_delete_signal(message)
        
        self.assertTrue(mock_send_to_user.called)


@patch('websocket.unified_consumers.send_to_group')
class RoomMessageSignalTest(TestCase):
    """ルームメッセージシグナル処理のテスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='rms_user1',
            email='rms_user1@test.com',
            password='testpass123'
        )
        self.room_id = uuid.uuid4()
        
        # UserProfileは自動作成される（signals.pyで設定済み）
        
    def test_room_message_post_signal(self, mock_send_to_group):
        """ルームメッセージ作成シグナルのテスト"""
        from .signals import send_room_message_post_signal
        
        mock_send_to_group.return_value = None
        
        message = RoomMessage.objects.create(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=self.room_id,
            content="Room signal test message"
        )
        
        send_room_message_post_signal(message)
        
        # WebSocket送信が呼ばれたか確認
        self.assertTrue(mock_send_to_group.called)


class IntegrationTest(TestCase):
    """統合テスト"""
    
    def setUp(self):
        """テストデータ準備"""
        self.user1 = User.objects.create_user(
            username='int_user1',
            email='int_user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='int_user2',
            email='int_user2@test.com',
            password='testpass123'
        )
        
        # UserProfileは自動作成される（signals.pyで設定済み）
            
    @patch('websocket.unified_consumers.send_to_user')
    def test_full_message_lifecycle(self, mock_send_to_user):
        """メッセージのライフサイクル統合テスト"""
        mock_send_to_user.return_value = None
        
        # 1. メッセージ作成
        message = PrivateMessage.objects.send_message(
            sender=self.user1,
            receiver=self.user2,
            content="Integration test message"
        )
        
        self.assertFalse(message.is_read)
        self.assertFalse(message.is_deleted)
        
        # 2. 既読処理
        read_message = PrivateMessage.objects.mark_message_as_read(message.id)
        self.assertTrue(read_message.is_read)
        
        # 3. メッセージ更新
        updated_message = PrivateMessage.objects.update_message_content(
            message.id, "Updated content"
        )
        self.assertEqual(updated_message.content, "Updated content")
        
        # 4. メッセージ削除
        deleted_message = PrivateMessage.objects.delete_message(message.id)
        self.assertTrue(deleted_message.is_deleted)
        
        # 5. メッセージ復元
        restored_message = PrivateMessage.objects.restore_message(message.id)
        self.assertFalse(restored_message.is_deleted)
        
        # WebSocket通知が各段階で送信されたか確認
        self.assertTrue(mock_send_to_user.called)
        
    def test_conversation_flow(self):
        """会話フロー統合テスト"""
        # 複数のメッセージをやり取り
        msg1 = PrivateMessage.objects.send_message(
            sender=self.user1,
            receiver=self.user2,
            content="Hello"
        )
        
        msg2 = PrivateMessage.objects.send_message(
            sender=self.user2,
            receiver=self.user1,
            content="Hi there"
        )
        
        msg3 = PrivateMessage.objects.send_message(
            sender=self.user1,
            receiver=self.user2,
            content="How are you?"
        )
        
        # 会話履歴の取得
        messages = PrivateMessage.objects.get_between_users(self.user1, self.user2)
        self.assertEqual(messages.count(), 3)
        
        # 最新メッセージの確認
        latest = PrivateMessage.objects.get_latest_message_between_users(
            self.user1, self.user2
        )
        self.assertEqual(latest, msg3)
        
        # 未読数の確認
        unread_count = PrivateMessage.objects.get_unread_count(self.user2)
        self.assertEqual(unread_count, 2)  # msg1とmsg3
        
        # 会話相手リストの確認
        user1_contacts = PrivateMessage.objects.get_list_of_users_have_history_with_user(
            self.user1
        )
        self.assertEqual(len(user1_contacts), 1)
        self.assertEqual(user1_contacts[0]['user_id'], self.user2.id)
        
    def test_room_message_flow(self):
        """ルームメッセージフロー統合テスト"""
        room_id = uuid.uuid4()
        
        # ルームメッセージ送信
        message = RoomMessage.objects.send_message(
            sender=self.user1,
            room_type=RoomType.GROUP,
            room_id=room_id,
            content="Hello room"
        )
        
        self.assertEqual(message.room_type, RoomType.GROUP)
        self.assertEqual(message.room_id, room_id)
        
        # ルームメッセージ取得
        messages = RoomMessage.objects.get_messages_from_room(
            user=self.user1,
            room_type=RoomType.GROUP,
            room_id=room_id
        )
        
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first(), message)
