from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import User
from .models import Friend, FriendRequest, FriendRequestStatus, RelationManagement, RelationManagementType
from django.core.exceptions import ValidationError
import json
import uuid

class FriendRequestManagerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user3 = User.objects.create_user(username='testuser3', password='testpassword')
        self.user4 = User.objects.create_user(username='testuser4', password='testpassword')
        self.user5 = User.objects.create_user(username='testuser5', password='testpassword')

        # user1宛てのペンディングリクエスト
        self.req1_2 = FriendRequest.objects.create(from_user=self.user2, to_user=self.user1, status=FriendRequestStatus.PENDING)
        self.req1_3 = FriendRequest.objects.create(from_user=self.user3, to_user=self.user1, status=FriendRequestStatus.PENDING)
        self.req1_4 = FriendRequest.objects.create(from_user=self.user4, to_user=self.user1, status=FriendRequestStatus.PENDING)

        # user1がuser3をブロック
        RelationManagement.objects.create(user=self.user1, target_user=self.user3, management=RelationManagementType.BLOCK)
        # user1がuser4を無視
        RelationManagement.objects.create(user=self.user1, target_user=self.user4, management=RelationManagementType.IGNORE)
        # user1がuser5をミュート（これは今回のテストには直接関係ないが、存在しても問題ないことを確認）
        RelationManagement.objects.create(user=self.user1, target_user=self.user5, management=RelationManagementType.MUTE)

    def test_get_pending_friend_requests_basic(self):
        # user1にブロック/無視されていないuser2からのリクエストが取得されることを確認
        pending_requests = FriendRequest.objects.get_pending_friend_requests(self.user1)
        self.assertEqual(pending_requests.count(), 1)
        self.assertIn(self.req1_2, pending_requests)

    def test_get_pending_friend_requests_exclude_blocked(self):
        # user1にブロックされているuser3からのリクエストが除外されることを確認
        pending_requests = FriendRequest.objects.get_pending_friend_requests(self.user1)
        self.assertNotIn(self.req1_3, pending_requests)

    def test_get_pending_friend_requests_exclude_ignored(self):
        # user1に無視されているuser4からのリクエストが除外されることを確認
        pending_requests = FriendRequest.objects.get_pending_friend_requests(self.user1)
        self.assertNotIn(self.req1_4, pending_requests)

    def test_get_pending_friend_requests_exclude_both(self):
        # user1がuser3とuser4をブロック/無視している場合に、user2からのリクエストのみが取得されることを確認
        pending_requests = FriendRequest.objects.get_pending_friend_requests(self.user1)
        self.assertEqual(pending_requests.count(), 1)
        self.assertIn(self.req1_2, pending_requests)
        self.assertNotIn(self.req1_3, pending_requests)
        self.assertNotIn(self.req1_4, pending_requests)

    def test_get_pending_friend_requests_no_pending(self):
        # ペンディング中のリクエストがない場合に空のクエリセットが返されることを確認
        # user5にはリクエストを送っていないので、user5宛てのリクエストは存在しない
        pending_requests = FriendRequest.objects.get_pending_friend_requests(self.user5)
        self.assertEqual(pending_requests.count(), 0)

    def test_get_pending_friend_requests_other_status(self):
        # ACCEPTED状態のリクエストは取得されないことを確認
        # user2からのリクエストをACCEPTEDにする
        self.req1_2.status = FriendRequestStatus.ACCEPTED
        self.req1_2.save()
        pending_requests = FriendRequest.objects.get_pending_friend_requests(self.user1)
        self.assertNotIn(self.req1_2, pending_requests)


class FriendModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user3 = User.objects.create_user(username='testuser3', password='testpassword')
        self.user4 = User.objects.create_user(username='testuser4', password='testpassword')

    def test_friend_creation_uuid_order(self):
        """UUIDの順序付けが適切に行われることをテスト"""
        # UUIDを文字列として比較し、小さい方をuser1、大きい方をuser2とする
        if str(self.user1.id) < str(self.user2.id):
            user1, user2 = self.user1, self.user2
        else:
            user1, user2 = self.user2, self.user1
        
        friend = Friend.objects.create(user1=user1, user2=user2)
        self.assertEqual(friend.user1, user1)
        self.assertEqual(friend.user2, user2)

    def test_friend_validation_same_user(self):
        """同じユーザー同士の友達関係を禁止することをテスト"""
        with self.assertRaises(ValidationError):
            Friend(user1=self.user1, user2=self.user1).clean()

    def test_friend_validation_wrong_order(self):
        """UUID順序の違反を検出することをテスト"""
        if str(self.user1.id) > str(self.user2.id):
            # user1のUUIDがuser2より大きい場合、ValidationErrorが発生するはず
            with self.assertRaises(ValidationError):
                Friend(user1=self.user1, user2=self.user2).clean()

    def test_friend_manager_check_friend(self):
        """FriendManagerのcheck_friendメソッドをテスト"""
        # 最初は友達ではない
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))
        
        # 友達関係を作成（UUID順序を考慮）
        if str(self.user1.id) < str(self.user2.id):
            Friend.objects.create(user1=self.user1, user2=self.user2)
        else:
            Friend.objects.create(user1=self.user2, user2=self.user1)
        
        # 順序に関係なく友達かどうかチェックできる
        self.assertTrue(Friend.objects.check_friend(self.user1, self.user2))
        self.assertTrue(Friend.objects.check_friend(self.user2, self.user1))

    def test_friend_manager_get_friends(self):
        """FriendManagerのget_friendsメソッドをテスト"""
        # user1がuser2, user3と友達になる
        if str(self.user1.id) < str(self.user2.id):
            Friend.objects.create(user1=self.user1, user2=self.user2)
        else:
            Friend.objects.create(user1=self.user2, user2=self.user1)
        
        if str(self.user1.id) < str(self.user3.id):
            Friend.objects.create(user1=self.user1, user2=self.user3)
        else:
            Friend.objects.create(user1=self.user3, user2=self.user1)
        
        # user1の友達を取得
        friend_ids = list(Friend.objects.get_friends(self.user1))
        self.assertEqual(len(friend_ids), 2)
        self.assertIn(self.user2.id, friend_ids)
        self.assertIn(self.user3.id, friend_ids)
        self.assertNotIn(self.user1.id, friend_ids)  # 自分自身は含まれない
        self.assertNotIn(self.user4.id, friend_ids)  # 友達ではないuser4は含まれない

    def test_friend_manager_remove_friend(self):
        """FriendManagerのremove_friendメソッドをテスト"""
        # 友達関係を作成
        if str(self.user1.id) < str(self.user2.id):
            friend = Friend.objects.create(user1=self.user1, user2=self.user2)
        else:
            friend = Friend.objects.create(user1=self.user2, user2=self.user1)
        
        # 友達であることを確認
        self.assertTrue(Friend.objects.check_friend(self.user1, self.user2))
        
        # 友達関係を削除
        result = Friend.objects.remove_friend(self.user1, self.user2)
        self.assertTrue(result)
        
        # 友達ではなくなったことを確認
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))
        
        # 存在しない友達関係を削除しようとした場合
        result = Friend.objects.remove_friend(self.user1, self.user2)
        self.assertFalse(result)

    def test_friend_unique_together(self):
        """unique_together制約のテスト"""
        if str(self.user1.id) < str(self.user2.id):
            user1, user2 = self.user1, self.user2
        else:
            user1, user2 = self.user2, self.user1
        
        # 最初の友達関係を作成
        Friend.objects.create(user1=user1, user2=user2)
        
        # 同じ組み合わせで重複作成を試みる
        with self.assertRaises(Exception):  # IntegrityError等
            Friend.objects.create(user1=user1, user2=user2)


class FriendRequestModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user3 = User.objects.create_user(username='testuser3', password='testpassword')
        self.user4 = User.objects.create_user(username='testuser4', password='testpassword')

    def test_send_friend_request_success(self):
        """フレンドリクエスト送信の成功ケース"""
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        
        self.assertEqual(friend_request.from_user, self.user1)
        self.assertEqual(friend_request.to_user, self.user2)
        self.assertEqual(friend_request.status, FriendRequestStatus.PENDING)

    def test_send_friend_request_duplicate(self):
        """重複するフレンドリクエスト送信の防止"""
        FriendRequest.send_friend_request(self.user1, self.user2)
        
        with self.assertRaises(ValidationError) as cm:
            FriendRequest.send_friend_request(self.user1, self.user2)
        self.assertIn('Friend request already exists', str(cm.exception))

    def test_send_friend_request_to_existing_friend(self):
        """既に友達のユーザーへのリクエスト送信を防止"""
        # 友達関係を作成
        if str(self.user1.id) < str(self.user2.id):
            Friend.objects.create(user1=self.user1, user2=self.user2)
        else:
            Friend.objects.create(user1=self.user2, user2=self.user1)
        
        with self.assertRaises(ValidationError) as cm:
            FriendRequest.send_friend_request(self.user1, self.user2)
        self.assertIn('Users are already friends', str(cm.exception))

    def test_friend_request_validation_same_user(self):
        """自分自身へのフレンドリクエストを防止"""
        friend_request = FriendRequest(from_user=self.user1, to_user=self.user1)
        with self.assertRaises(ValidationError):
            friend_request.clean()

    def test_friend_request_accept(self):
        """フレンドリクエストの承認テスト"""
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        
        # 承認前は友達ではない
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))
        
        # リクエストを承認
        friend_request.accept()
        
        # 友達関係が作成されたことを確認
        self.assertTrue(Friend.objects.check_friend(self.user1, self.user2))
        
        # リクエストが削除されたことを確認
        self.assertFalse(FriendRequest.objects.filter(id=friend_request.id).exists())

    def test_friend_request_reject(self):
        """フレンドリクエストの拒否テスト"""
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        original_id = friend_request.id
        
        # 拒否前はリクエストが存在する
        self.assertTrue(FriendRequest.objects.filter(id=original_id).exists())
        
        # リクエストを拒否
        friend_request.reject()
        
        # 友達関係は作成されない
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))
        
        # リクエストが削除されたことを確認
        self.assertFalse(FriendRequest.objects.filter(id=original_id).exists())

    def test_friend_request_after_rejection_can_resend(self):
        """拒否後に再度リクエストを送信できることをテスト"""
        # 最初のリクエストを送信・拒否
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        friend_request.reject()
        
        # 拒否後に再度送信できることを確認
        new_friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        self.assertEqual(new_friend_request.from_user, self.user1)
        self.assertEqual(new_friend_request.to_user, self.user2)
        self.assertEqual(new_friend_request.status, FriendRequestStatus.PENDING)
    
    def test_friend_request_cancel(self):
        """フレンドリクエストの取り消しテスト"""
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        original_id = friend_request.id
        
        # 取り消し前はリクエストが存在する
        self.assertTrue(FriendRequest.objects.filter(id=original_id).exists())
        
        # リクエストを取り消し
        friend_request.cancel()
        
        # 友達関係は作成されない
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))
        
        # リクエストが削除されたことを確認
        self.assertFalse(FriendRequest.objects.filter(id=original_id).exists())
    
    def test_friend_request_after_cancel_can_resend(self):
        """取り消し後に再度リクエストを送信できることをテスト"""
        # 最初のリクエストを送信・取り消し
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        friend_request.cancel()
        
        # 取り消し後に再度送信できることを確認
        new_friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        self.assertEqual(new_friend_request.from_user, self.user1)
        self.assertEqual(new_friend_request.to_user, self.user2)
        self.assertEqual(new_friend_request.status, FriendRequestStatus.PENDING)
    
    def test_get_sent_friend_requests(self):
        """送信済みフレンドリクエストの取得テスト"""
        # user1がuser2とuser3にリクエストを送信
        req1_2 = FriendRequest.send_friend_request(self.user1, self.user2)
        req1_3 = FriendRequest.send_friend_request(self.user1, self.user3)
        
        # user4がuser1にリクエストを送信（これは送信済みに含まれない）
        req4_1 = FriendRequest.send_friend_request(self.user4, self.user1)
        
        # user1の送信済みリクエストを取得
        sent_requests = FriendRequest.objects.get_sent_friend_requests(self.user1)
        
        # user1が送信した2つのリクエストが取得される
        self.assertEqual(sent_requests.count(), 2)
        self.assertIn(req1_2, sent_requests)
        self.assertIn(req1_3, sent_requests)
        self.assertNotIn(req4_1, sent_requests)  # 他人からのリクエストは含まれない

    def test_friend_request_unique_together(self):
        """unique_together制約のテスト"""
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2, status=FriendRequestStatus.PENDING)
        
        # 同じ組み合わせで重複作成を試みる
        with self.assertRaises(Exception):  # IntegrityError等
            FriendRequest.objects.create(from_user=self.user1, to_user=self.user2, status=FriendRequestStatus.PENDING)


class RelationManagementModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user3 = User.objects.create_user(username='testuser3', password='testpassword')
        self.user4 = User.objects.create_user(username='testuser4', password='testpassword')

    def test_block_user_success(self):
        """ユーザーブロックの成功ケース"""
        relation = RelationManagement.block_user(self.user1, self.user2)
        
        self.assertEqual(relation.user, self.user1)
        self.assertEqual(relation.target_user, self.user2)
        self.assertEqual(relation.management, RelationManagementType.BLOCK)

    def test_block_user_duplicate(self):
        """重複ブロックの防止"""
        RelationManagement.block_user(self.user1, self.user2)
        
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.block_user(self.user1, self.user2)
        self.assertIn('User is already blocked', str(cm.exception))

    def test_block_user_removes_mute_and_ignore(self):
        """ブロック時にミュートと無視を削除"""
        # ミュートと無視を設定
        RelationManagement.mute_user(self.user1, self.user2)
        RelationManagement.ignore_user(self.user1, self.user3)
        
        # ブロック実行
        RelationManagement.block_user(self.user1, self.user2)
        
        # ミュートが削除されたことを確認
        self.assertFalse(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user2, management=RelationManagementType.MUTE
        ).exists())
        
        # 他ユーザーの無視は影響されない
        self.assertTrue(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user3, management=RelationManagementType.IGNORE
        ).exists())

    def test_mute_user_success(self):
        """ユーザーミュートの成功ケース"""
        relation = RelationManagement.mute_user(self.user1, self.user2)
        
        self.assertEqual(relation.user, self.user1)
        self.assertEqual(relation.target_user, self.user2)
        self.assertEqual(relation.management, RelationManagementType.MUTE)

    def test_mute_user_duplicate(self):
        """重複ミュートの防止"""
        RelationManagement.mute_user(self.user1, self.user2)
        
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.mute_user(self.user1, self.user2)
        self.assertIn('User is already muted', str(cm.exception))

    def test_mute_blocked_user_prevention(self):
        """ブロック済みユーザーのミュート防止"""
        RelationManagement.block_user(self.user1, self.user2)
        
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.mute_user(self.user1, self.user2)
        self.assertIn('User is blocked. You cannot mute a blocked user', str(cm.exception))

    def test_ignore_user_success(self):
        """ユーザー無視の成功ケース"""
        relation = RelationManagement.ignore_user(self.user1, self.user2)
        
        self.assertEqual(relation.user, self.user1)
        self.assertEqual(relation.target_user, self.user2)
        self.assertEqual(relation.management, RelationManagementType.IGNORE)

    def test_ignore_user_duplicate(self):
        """重複無視の防止"""
        RelationManagement.ignore_user(self.user1, self.user2)
        
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.ignore_user(self.user1, self.user2)
        self.assertIn('User is already ignored', str(cm.exception))

    def test_ignore_blocked_user_prevention(self):
        """ブロック済みユーザーの無視防止"""
        RelationManagement.block_user(self.user1, self.user2)
        
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.ignore_user(self.user1, self.user2)
        self.assertIn('User is blocked. You cannot ignore a blocked user', str(cm.exception))

    def test_unblock_user_success(self):
        """ユーザーブロック解除の成功ケース"""
        RelationManagement.block_user(self.user1, self.user2)
        
        result = RelationManagement.unblock_user(self.user1, self.user2)
        self.assertIsNone(result)  # 成功時はNoneを返す
        
        # ブロックが削除されたことを確認
        self.assertFalse(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user2, management=RelationManagementType.BLOCK
        ).exists())

    def test_unblock_not_blocked_user(self):
        """ブロックされていないユーザーの解除を試みる"""
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.unblock_user(self.user1, self.user2)
        self.assertIn('User is not blocked', str(cm.exception))

    def test_unmute_user_success(self):
        """ユーザーミュート解除の成功ケース"""
        RelationManagement.mute_user(self.user1, self.user2)
        
        result = RelationManagement.unmute_user(self.user1, self.user2)
        self.assertIsNone(result)
        
        # ミュートが削除されたことを確認
        self.assertFalse(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user2, management=RelationManagementType.MUTE
        ).exists())

    def test_unmute_not_muted_user(self):
        """ミュートされていないユーザーの解除を試みる"""
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.unmute_user(self.user1, self.user2)
        self.assertIn('User is not muted', str(cm.exception))

    def test_unignore_user_success(self):
        """ユーザー無視解除の成功ケース"""
        RelationManagement.ignore_user(self.user1, self.user2)
        
        result = RelationManagement.unignore_user(self.user1, self.user2)
        self.assertIsNone(result)
        
        # 無視が削除されたことを確認
        self.assertFalse(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user2, management=RelationManagementType.IGNORE
        ).exists())

    def test_unignore_not_ignored_user(self):
        """無視されていないユーザーの解除を試みる"""
        with self.assertRaises(ValidationError) as cm:
            RelationManagement.unignore_user(self.user1, self.user2)
        self.assertIn('User is not ignored', str(cm.exception))

    def test_relation_management_manager_get_blocked_users(self):
        """RelationManagementManagerのget_blocked_usersメソッドをテスト"""
        RelationManagement.block_user(self.user1, self.user2)
        RelationManagement.block_user(self.user1, self.user3)
        RelationManagement.mute_user(self.user1, self.user4)  # ミュートは含まれない
        
        blocked_user_ids = list(RelationManagement.objects.get_blocked_users(self.user1))
        
        self.assertEqual(len(blocked_user_ids), 2)
        self.assertIn(self.user2.id, blocked_user_ids)
        self.assertIn(self.user3.id, blocked_user_ids)
        self.assertNotIn(self.user4.id, blocked_user_ids)

    def test_relation_management_manager_get_muted_users(self):
        """RelationManagementManagerのget_muted_usersメソッドをテスト"""
        RelationManagement.mute_user(self.user1, self.user2)
        RelationManagement.mute_user(self.user1, self.user3)
        RelationManagement.block_user(self.user1, self.user4)  # ブロックは含まれない
        
        muted_user_ids = list(RelationManagement.objects.get_muted_users(self.user1))
        
        self.assertEqual(len(muted_user_ids), 2)
        self.assertIn(self.user2.id, muted_user_ids)
        self.assertIn(self.user3.id, muted_user_ids)
        self.assertNotIn(self.user4.id, muted_user_ids)

    def test_relation_management_manager_get_ignored_users(self):
        """RelationManagementManagerのget_ignored_usersメソッドをテスト"""
        RelationManagement.ignore_user(self.user1, self.user2)
        RelationManagement.ignore_user(self.user1, self.user3)
        RelationManagement.block_user(self.user1, self.user4)  # ブロックは含まれない
        
        ignored_user_ids = list(RelationManagement.objects.get_ignored_users(self.user1))
        
        self.assertEqual(len(ignored_user_ids), 2)
        self.assertIn(self.user2.id, ignored_user_ids)
        self.assertIn(self.user3.id, ignored_user_ids)
        self.assertNotIn(self.user4.id, ignored_user_ids)


class RelationsAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user3 = User.objects.create_user(username='testuser3', password='testpassword')
        
        # JWT認証のモック（実際のプロジェクトではJWTトークンを使用）
        self.client.force_login(self.user1)

    def test_send_friend_request_api(self):
        """フレンドリクエスト送信APIのテスト"""
        url = '/relations/request/send'
        data = {
            'to_user_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # レスポンスの確認（実際のAPIの実装に合わせて調整が必要）
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # フレンドリクエストが作成されたことを確認
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())

    def test_accept_friend_request_api(self):
        """フレンドリクエスト承認APIのテスト"""
        # フレンドリクエストを作成
        friend_request = FriendRequest.send_friend_request(self.user2, self.user1)
        
        url = '/relations/request/accept'
        data = {
            'friend_request_id': str(friend_request.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # 友達関係が作成されたことを確認
        self.assertTrue(Friend.objects.check_friend(self.user1, self.user2))

    def test_reject_friend_request_api(self):
        """フレンドリクエスト拒否APIのテスト"""
        # フレンドリクエストを作成
        friend_request = FriendRequest.send_friend_request(self.user2, self.user1)
        original_id = friend_request.id
        
        url = '/relations/request/reject'
        data = {
            'friend_request_id': str(friend_request.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # フレンドリクエストが削除されたことを確認
        self.assertFalse(FriendRequest.objects.filter(id=original_id).exists())
        # 友達関係は作成されていないことを確認
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))

    def test_remove_friend_api(self):
        """フレンド削除APIのテスト"""
        # 友達関係を作成
        if str(self.user1.id) < str(self.user2.id):
            Friend.objects.create(user1=self.user1, user2=self.user2)
        else:
            Friend.objects.create(user1=self.user2, user2=self.user1)
        
        url = '/relations/friends/remove'
        data = {
            'friend_user_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # 友達関係が削除されたことを確認
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))

    def test_block_user_api(self):
        """ユーザーブロックAPIのテスト"""
        url = '/relations/management/block'
        data = {
            'target_user_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # ブロック関係が作成されたことを確認
        self.assertTrue(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user2, management=RelationManagementType.BLOCK
        ).exists())

    def test_unblock_user_api(self):
        """ユーザーブロック解除APIのテスト"""
        # ブロック関係を作成
        RelationManagement.block_user(self.user1, self.user2)
        
        url = '/relations/management/unblock'
        data = {
            'target_user_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # ブロック関係が削除されたことを確認
        self.assertFalse(RelationManagement.objects.filter(
            user=self.user1, target_user=self.user2, management=RelationManagementType.BLOCK
        ).exists())

    def test_list_friends_api(self):
        """フレンド一覧取得APIのテスト"""
        # 友達関係を作成
        if str(self.user1.id) < str(self.user2.id):
            Friend.objects.create(user1=self.user1, user2=self.user2)
        else:
            Friend.objects.create(user1=self.user2, user2=self.user1)
        
        if str(self.user1.id) < str(self.user3.id):
            Friend.objects.create(user1=self.user1, user2=self.user3)
        else:
            Friend.objects.create(user1=self.user3, user2=self.user1)
        
        url = '/relations/friends'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # 友達が2人返されることを確認
        friends_data = response_data.get('data', [])
        self.assertEqual(len(friends_data), 2)
        
        # 友達のIDが含まれていることを確認
        friend_ids = [friend['id'] for friend in friends_data]
        self.assertIn(str(self.user2.id), friend_ids)
        self.assertIn(str(self.user3.id), friend_ids)

    def test_list_friend_requests_api(self):
        """フレンドリクエスト一覧取得APIのテスト"""
        # フレンドリクエストを作成
        FriendRequest.send_friend_request(self.user2, self.user1)
        FriendRequest.send_friend_request(self.user3, self.user1)
        
        url = '/relations/requests'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # リクエストが2つ返されることを確認
        requests_data = response_data.get('data', [])
        self.assertEqual(len(requests_data), 2)

    def test_list_blocked_users_api(self):
        """ブロックユーザー一覧取得APIのテスト"""
        # ブロック関係を作成
        RelationManagement.block_user(self.user1, self.user2)
        RelationManagement.block_user(self.user1, self.user3)
        
        url = '/relations/management/blocked'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # ブロックユーザーが2人返されることを確認
        blocked_data = response_data.get('data', [])
        self.assertEqual(len(blocked_data), 2)

    def test_api_error_handling_invalid_user_id(self):
        """不正なユーザーIDに対するエラーハンドリングのテスト"""
        url = '/relations/request/send'
        data = {
            'to_user_id': str(uuid.uuid4())  # 存在しないUUID
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # エラーレスポンスが返されることを確認（実際のAPIの実装に合わせて調整が必要）
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'error')

    def test_api_error_handling_unauthorized(self):
        """認証なしアクセスのエラーハンドリングのテスト"""
        # ログアウト
        self.client.logout()
        
        url = '/relations/request/send'
        data = {
            'to_user_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # 認証エラーが返されることを確認
        self.assertIn(response.status_code, [401, 403])
    
    def test_cancel_friend_request_api(self):
        """フレンドリクエスト取り消しAPIのテスト"""
        # フレンドリクエストを作成
        friend_request = FriendRequest.send_friend_request(self.user1, self.user2)
        original_id = friend_request.id
        
        url = '/relations/request/cancel'
        data = {
            'friend_request_id': str(friend_request.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # フレンドリクエストが削除されたことを確認
        self.assertFalse(FriendRequest.objects.filter(id=original_id).exists())
        # 友達関係は作成されていないことを確認
        self.assertFalse(Friend.objects.check_friend(self.user1, self.user2))
    
    def test_cancel_friend_request_api_unauthorized(self):
        """他人のフレンドリクエスト取り消しのエラーテスト"""
        # user2がuser3にリクエストを送信
        friend_request = FriendRequest.send_friend_request(self.user2, self.user3)
        
        # user1が取り消しを試みる（権限なし）
        url = '/relations/request/cancel'
        data = {
            'friend_request_id': str(friend_request.id)
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'error')
        self.assertIn('You can only cancel your own friend requests', response_data.get('error'))
    
    def test_list_sent_friend_requests_api(self):
        """送信済みフレンドリクエスト一覧取得APIのテスト"""
        # フレンドリクエストを作成
        FriendRequest.send_friend_request(self.user1, self.user2)
        FriendRequest.send_friend_request(self.user1, self.user3)
        
        # 他のユーザーからのリクエスト（送信済みには含まれない）
        FriendRequest.send_friend_request(self.user2, self.user1)
        
        url = '/relations/requests/sent'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data.get('status'), 'success')
        
        # 送信済みリクエストが2つ返されることを確認
        sent_data = response_data.get('data', [])
        self.assertEqual(len(sent_data), 2)
        
        # 送信先のIDが含まれていることを確認
        sent_user_ids = [sent['id'] for sent in sent_data]
        self.assertIn(str(self.user2.id), sent_user_ids)
        self.assertIn(str(self.user3.id), sent_user_ids)
