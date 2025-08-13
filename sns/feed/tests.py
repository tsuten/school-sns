from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from feed.services import FeedService
from apps.core.organizations.models import OrganizationType

User = get_user_model()

class FeedServiceTest(TestCase):
    """FeedServiceのテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.feed_service = FeedService()

    @patch('feed.services.OrganizationManager')
    def test_get_feed_with_class_organization(self, mock_org_manager):
        """クラス組織のフィード取得テスト"""
        # モックの設定
        mock_org = Mock()
        mock_org.id = 1
        mock_org.name = 'テストクラス'
        
        mock_manager_instance = Mock()
        mock_manager_instance.get_organization_by_user.return_value = mock_org
        mock_manager_instance.get_organization_type_by_id.return_value = OrganizationType.CLASS
        
        mock_org_manager.return_value = mock_manager_instance
        
        # テスト実行
        result = self.feed_service.get_feed(self.user)
        
        # 検証
        self.assertEqual(result['type'], 'class')
        self.assertEqual(result['organization'], 'テストクラス')
        self.assertEqual(result['feed_items'], [])
        self.assertEqual(result['total_count'], 0)

    @patch('feed.services.OrganizationManager')
    def test_get_feed_with_school_organization(self, mock_org_manager):
        """学校組織のフィード取得テスト"""
        # モックの設定
        mock_org = Mock()
        mock_org.id = 1
        mock_org.name = 'テスト学校'
        
        mock_manager_instance = Mock()
        mock_manager_instance.get_organization_by_user.return_value = mock_org
        mock_manager_instance.get_organization_type_by_id.return_value = OrganizationType.SCHOOL
        
        mock_org_manager.return_value = mock_manager_instance
        
        # テスト実行
        result = self.feed_service.get_feed(self.user)
        
        # 検証
        self.assertEqual(result['type'], 'school')
        self.assertEqual(result['organization'], 'テスト学校')
        self.assertEqual(result['feed_items'], [])
        self.assertEqual(result['total_count'], 0)

    @patch('feed.services.OrganizationManager')
    def test_get_feed_no_organization(self, mock_org_manager):
        """組織に所属していない場合のテスト"""
        # モックの設定
        mock_manager_instance = Mock()
        mock_manager_instance.get_organization_by_user.return_value = None
        
        mock_org_manager.return_value = mock_manager_instance
        
        # テスト実行
        result = self.feed_service.get_feed(self.user)
        
        # 検証
        self.assertEqual(result, [])

    @patch('feed.services.OrganizationManager')
    def test_get_feed_unknown_organization_type(self, mock_org_manager):
        """不明な組織タイプの場合のテスト"""
        # モックの設定
        mock_org = Mock()
        mock_org.id = 1
        mock_org.name = 'テスト組織'
        
        mock_manager_instance = Mock()
        mock_manager_instance.get_organization_by_user.return_value = mock_org
        mock_manager_instance.get_organization_type_by_id.return_value = 'unknown'
        
        mock_org_manager.return_value = mock_manager_instance
        
        # テスト実行
        result = self.feed_service.get_feed(self.user)
        
        # 検証
        self.assertEqual(result, [])

    def test_get_class_feed(self):
        """クラスフィード取得のテスト"""
        mock_class = Mock()
        mock_class.name = 'テストクラス'
        
        result = self.feed_service._get_class_feed(mock_class)
        
        self.assertEqual(result['type'], 'class')
        self.assertEqual(result['organization'], 'テストクラス')
        self.assertEqual(result['feed_items'], [])
        self.assertEqual(result['total_count'], 0)

    def test_get_school_feed(self):
        """学校フィード取得のテスト"""
        mock_school = Mock()
        mock_school.name = 'テスト学校'
        
        result = self.feed_service._get_school_feed(mock_school)
        
        self.assertEqual(result['type'], 'school')
        self.assertEqual(result['organization'], 'テスト学校')
        self.assertEqual(result['feed_items'], [])
        self.assertEqual(result['total_count'], 0) 