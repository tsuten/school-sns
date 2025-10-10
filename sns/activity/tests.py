from django.test import TestCase
from django.contrib.auth import get_user_model
from .views import get_user_activities, get_feed_activities

User = get_user_model()

class ActivityViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_get_user_activities_empty(self):
        """ユーザーにアクティビティがない場合のテスト"""
        activities = get_user_activities(str(self.user.id), limit=10, offset=0)
        self.assertEqual(len(activities), 0)
    
    def test_get_user_activities_with_posts(self):
        """投稿がある場合のアクティビティ取得テスト"""
        try:
            from posts.models import Post
            post = Post.objects.create(
                user=self.user,
                title="テスト投稿",
                content="テスト内容"
            )
            
            activities = get_user_activities(str(self.user.id), limit=10, offset=0)
            self.assertEqual(len(activities), 1)
            self.assertEqual(activities[0]['type'], 'post_created')
            self.assertEqual(activities[0]['description'], "投稿「テスト投稿」を作成しました")
            
        except ImportError:
            # postsモジュールが利用できない場合はスキップ
            self.skipTest("Posts module not available")
    
    def test_get_feed_activities(self):
        """フィードアクティビティの取得テスト"""
        activities = get_feed_activities(self.user, limit=10, offset=0)
        self.assertEqual(len(activities), 0)  # 初期状態ではアクティビティなし
    
    def test_get_user_activities_invalid_user(self):
        """存在しないユーザーIDでのアクティビティ取得テスト"""
        activities = get_user_activities("invalid-uuid", limit=10, offset=0)
        self.assertEqual(len(activities), 0)
