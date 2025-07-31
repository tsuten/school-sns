from django.test import TestCase
from users.models import User
from .models import FriendRequest, FriendRequestStatus, RelationManagement, RelationManagementType
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
