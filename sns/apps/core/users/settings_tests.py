from django.test import TestCase
from django.contrib.auth import get_user_model
from ninja.testing import TestClient
from .views import router
from .models import UserSettings

User = get_user_model()


class UserSettingsTestCase(TestCase):
    """ユーザー設定関連のテストケース"""
    
    def setUp(self):
        """テスト用データの初期化"""
        self.client = TestClient(router)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # UserSettingsは signals により自動作成される
        self.settings = UserSettings.objects.get(user=self.user)
        
    def get_auth_headers(self):
        """JWT認証ヘッダーを取得（簡易版）"""
        # 実際のプロジェクトではJWTトークン生成ロジックが必要
        return {"Authorization": f"Bearer test_token_{self.user.id}"}


class SettingsGetAPITest(UserSettingsTestCase):
    """設定取得APIのテスト"""
    
    def test_get_user_settings_success(self):
        """設定取得の成功ケース"""
        response = self.client.get(
            '/settings',
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # レスポンス構造の確認
        self.assertIn('theme', data)
        self.assertIn('notification', data)
        self.assertIn('privacy', data)
        
        # デフォルト値の確認
        self.assertEqual(data['theme']['darkmode'], False)
        self.assertEqual(data['notification']['notification'], True)
        self.assertEqual(data['privacy']['profile'], True)
        self.assertEqual(data['privacy']['birthday'], True)
        self.assertEqual(data['privacy']['location'], True)
        self.assertEqual(data['privacy']['activity'], True)
    
    def test_get_user_settings_unauthorized(self):
        """認証なしでの設定取得エラー"""
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 401)


class UnifiedSettingsAPITest(UserSettingsTestCase):
    """統合設定更新APIのテスト"""
    
    def test_update_unified_settings_success(self):
        """統合設定更新の成功ケース"""
        payload = {
            "settings": {
                "theme.darkmode": True,
                "notification.notification": False,
                "privacy.profile": False,
                "privacy.birthday": True
            }
        }
        
        response = self.client.post(
            '/settings',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # レスポンス確認
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], '設定が正常に更新されました')
        self.assertIn('updated_settings', data)
        
        # DB更新確認
        self.settings.refresh_from_db()
        self.assertTrue(self.settings.is_dark_mode_enabled)
        self.assertFalse(self.settings.is_notification_enabled)
        self.assertFalse(self.settings.is_profile_public)
        self.assertTrue(self.settings.is_birthday_public)
    
    def test_update_unified_settings_invalid_key_format(self):
        """不正なキー形式のエラー"""
        payload = {
            "settings": {
                "invalid_key": True
            }
        }
        
        response = self.client.post(
            '/settings',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('無効な設定事項です', str(response.content))
    
    def test_update_unified_settings_invalid_type(self):
        """不正な設定タイプのエラー"""
        payload = {
            "settings": {
                "invalid.setting": True
            }
        }
        
        response = self.client.post(
            '/settings',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('無効な設定事項です', str(response.content))
    
    def test_update_unified_settings_invalid_label(self):
        """不正なラベルのエラー"""
        payload = {
            "settings": {
                "theme.invalid_label": True
            }
        }
        
        response = self.client.post(
            '/settings',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('無効な設定事項です', str(response.content))
    
    def test_update_unified_settings_invalid_value_type(self):
        """非真偽値のエラー"""
        payload = {
            "settings": {
                "theme.darkmode": "invalid_string"
            }
        }
        
        response = self.client.post(
            '/settings',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('無効な設定事項です', str(response.content))


class IndividualSettingsAPITest(UserSettingsTestCase):
    """個別設定更新APIのテスト"""
    
    def test_update_theme_settings_success(self):
        """テーマ設定更新の成功ケース"""
        payload = {"darkmode": True}
        
        response = self.client.post(
            '/settings/theme',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['darkmode'])
        
        # DB更新確認
        self.settings.refresh_from_db()
        self.assertTrue(self.settings.is_dark_mode_enabled)
    
    def test_update_notification_settings_success(self):
        """通知設定更新の成功ケース"""
        payload = {"notification": False}
        
        response = self.client.post(
            '/settings/notification',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['notification'])
        
        # DB更新確認
        self.settings.refresh_from_db()
        self.assertFalse(self.settings.is_notification_enabled)
    
    def test_update_privacy_settings_success(self):
        """プライバシー設定更新の成功ケース"""
        payload = {
            "profile": False,
            "birthday": True,
            "location": False,
            "activity": True
        }
        
        response = self.client.post(
            '/settings/privacy',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['profile'])
        self.assertTrue(data['birthday'])
        self.assertFalse(data['location'])
        self.assertTrue(data['activity'])
        
        # DB更新確認
        self.settings.refresh_from_db()
        self.assertFalse(self.settings.is_profile_public)
        self.assertTrue(self.settings.is_birthday_public)
        self.assertFalse(self.settings.is_location_public)
        self.assertTrue(self.settings.is_activity_public)
    
    def test_update_privacy_settings_partial(self):
        """部分的なプライバシー設定更新"""
        payload = {
            "profile": False
            # 他の設定は None (現在の値を維持)
        }
        
        response = self.client.post(
            '/settings/privacy',
            json=payload,
            headers=self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, 200)
        
        # DB確認（profile のみ変更、他は初期値維持）
        self.settings.refresh_from_db()
        self.assertFalse(self.settings.is_profile_public)
        self.assertTrue(self.settings.is_birthday_public)  # 初期値維持
        self.assertTrue(self.settings.is_location_public)  # 初期値維持
        self.assertTrue(self.settings.is_activity_public)  # 初期値維持


class SettingsModelTest(UserSettingsTestCase):
    """UserSettingsモデルのテスト"""
    
    def test_user_settings_creation(self):
        """UserSettings作成のテスト"""
        # setUp で既に作成済みなので存在確認
        self.assertTrue(UserSettings.objects.filter(user=self.user).exists())
        
        settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(str(settings), self.user.username)
    
    def test_user_settings_defaults(self):
        """デフォルト値のテスト"""
        self.assertFalse(self.settings.is_dark_mode_enabled)
        self.assertTrue(self.settings.is_notification_enabled)
        self.assertTrue(self.settings.is_profile_public)
        self.assertTrue(self.settings.is_birthday_public)
        self.assertTrue(self.settings.is_location_public)
        self.assertTrue(self.settings.is_activity_public)
    
    def test_settings_manager_methods(self):
        """SettingsManagerのメソッドテスト"""
        # get_user_settings
        retrieved_settings = UserSettings.objects.get_user_settings(self.user.id)
        self.assertEqual(retrieved_settings, self.settings)
        
        # set_theme_settings
        updated_settings = UserSettings.objects.set_theme_settings(self.user.id, True)
        self.assertTrue(updated_settings.is_dark_mode_enabled)
        
        # set_notification_settings
        updated_settings = UserSettings.objects.set_notification_settings(self.user.id, False)
        self.assertFalse(updated_settings.is_notification_enabled)
        
        # set_privacy_settings
        updated_settings = UserSettings.objects.set_privacy_settings(
            self.user.id, False, True, False, True
        )
        self.assertFalse(updated_settings.is_profile_public)
        self.assertTrue(updated_settings.is_birthday_public)
        self.assertFalse(updated_settings.is_location_public)
        self.assertTrue(updated_settings.is_activity_public)


class SettingsAuthenticationTest(TestCase):
    """認証関連のテスト"""
    
    def setUp(self):
        self.client = TestClient(router)
    
    def test_settings_require_authentication(self):
        """設定関連APIが認証を要求することを確認"""
        # 認証なしでアクセス
        endpoints = [
            '/settings',
            '/settings/theme', 
            '/settings/notification',
            '/settings/privacy'
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                if endpoint == '/settings':
                    response = self.client.get(endpoint)
                else:
                    response = self.client.post(endpoint, json={})
                
                # 401 Unauthorized を期待
                self.assertEqual(response.status_code, 401)