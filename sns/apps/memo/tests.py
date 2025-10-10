from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Memo
from .schemas import MemoCreateSchema, MemoUpdateSchema
import json

class MemoModelTest(TestCase):
    """メモモデルのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.memo = Memo.objects.create(
            user=self.user,
            title='テストメモ',
            content='これはテスト用のメモです。'
        )
    
    def test_memo_creation(self):
        """メモ作成のテスト"""
        self.assertEqual(self.memo.title, 'テストメモ')
        self.assertEqual(self.memo.content, 'これはテスト用のメモです。')
        self.assertEqual(self.memo.user, self.user)
        self.assertFalse(self.memo.is_deleted)
    
    def test_memo_str_method(self):
        """__str__メソッドのテスト"""
        self.assertEqual(str(self.memo), 'テストメモ')
    
    def test_memo_soft_delete(self):
        """論理削除のテスト"""
        self.assertFalse(self.memo.is_deleted)
        self.memo.delete_object()
        self.assertTrue(self.memo.is_deleted)
        self.assertIsNotNone(self.memo.deleted_at)
    
    def test_memo_restore(self):
        """復元のテスト"""
        self.memo.delete_object()
        self.assertTrue(self.memo.is_deleted)
        self.memo.restore_object()
        self.assertFalse(self.memo.is_deleted)
        self.assertIsNone(self.memo.deleted_at)
    
    def test_memo_manager_ordering(self):
        """マネージャーの並び順テスト"""
        memo2 = Memo.objects.create(
            user=self.user,
            title='新しいメモ',
            content='2番目のメモ'
        )
        memos = Memo.objects.all()
        self.assertEqual(memos[0], memo2)  # 新しいものが先
        self.assertEqual(memos[1], self.memo)  # 古いものが後

class MemoViewTest(TestCase):
    """メモビューのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.memo = Memo.objects.create(
            user=self.user,
            title='テストメモ',
            content='これはテスト用のメモです。'
        )
    
    def test_memo_list_view_authenticated(self):
        """認証済みユーザーのメモ一覧表示テスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('memo:memo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テストメモ')
    
    def test_memo_list_view_unauthenticated(self):
        """未認証ユーザーのリダイレクトテスト"""
        response = self.client.get(reverse('memo:memo_list'))
        self.assertEqual(response.status_code, 302)  # リダイレクト
    
    def test_memo_detail_view(self):
        """メモ詳細表示のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('memo:memo_detail', args=[self.memo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テストメモ')
        self.assertContains(response, 'これはテスト用のメモです。')
    
    def test_memo_create_view(self):
        """メモ作成のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('memo:memo_create'), {
            'title': '新しいメモ',
            'content': '新しく作成されたメモです。'
        })
        self.assertEqual(response.status_code, 302)  # リダイレクト
        self.assertTrue(Memo.objects.filter(title='新しいメモ').exists())
    
    def test_memo_update_view(self):
        """メモ更新のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('memo:memo_update', args=[self.memo.id]), {
            'title': '更新されたメモ',
            'content': '内容が更新されました。'
        })
        self.assertEqual(response.status_code, 302)  # リダイレクト
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.title, '更新されたメモ')
        self.assertEqual(self.memo.content, '内容が更新されました。')
    
    def test_memo_delete_view(self):
        """メモ削除のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('memo:memo_delete', args=[self.memo.id]))
        self.assertEqual(response.status_code, 302)  # リダイレクト
        self.memo.refresh_from_db()
        self.assertTrue(self.memo.is_deleted)  # 論理削除

class MemoSchemaTest(TestCase):
    """メモスキーマのテスト"""
    
    def test_memo_create_schema_valid(self):
        """有効なメモ作成スキーマのテスト"""
        data = {
            'title': 'テストメモ',
            'content': 'これはテスト用のメモです。'
        }
        schema = MemoCreateSchema(**data)
        self.assertEqual(schema.title, 'テストメモ')
        self.assertEqual(schema.content, 'これはテスト用のメモです。')
    
    def test_memo_update_schema_partial(self):
        """部分更新スキーマのテスト"""
        data = {
            'title': '更新されたタイトル'
        }
        schema = MemoUpdateSchema(**data)
        self.assertEqual(schema.title, '更新されたタイトル')
        self.assertIsNone(schema.content)
    
    def test_memo_update_schema_empty(self):
        """空の更新スキーマのテスト"""
        schema = MemoUpdateSchema()
        self.assertIsNone(schema.title)
        self.assertIsNone(schema.content)

class MemoAPITest(TestCase):
    """メモAPIのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.memo = Memo.objects.create(
            user=self.user,
            title='テストメモ',
            content='これはテスト用のメモです。'
        )
    
    def test_api_get_memo_list(self):
        """API: メモ一覧取得のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/memo/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'テストメモ')
    
    def test_api_get_memo_detail(self):
        """API: メモ詳細取得のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/api/memo/{self.memo.id}/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'テストメモ')
        self.assertEqual(data['content'], 'これはテスト用のメモです。')
    
    def test_api_create_memo(self):
        """API: メモ作成のテスト"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'APIで作成されたメモ',
            'content': 'API経由で作成されました。'
        }
        response = self.client.post('/api/memo/', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Memo.objects.filter(title='APIで作成されたメモ').exists())
    
    def test_api_update_memo(self):
        """API: メモ更新のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.put(f'/api/memo/{self.memo.id}/',
                                 data=json.dumps({'title': 'APIで更新されたメモ'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.title, 'APIで更新されたメモ')
    
    def test_api_delete_memo(self):
        """API: メモ削除のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(f'/api/memo/{self.memo.id}/')
        self.assertEqual(response.status_code, 200)
        self.memo.refresh_from_db()
        self.assertTrue(self.memo.is_deleted)
    
    def test_api_search_memos(self):
        """API: メモ検索のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/memo/search/テスト/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'テストメモ')
    
    def test_api_recent_memos(self):
        """API: 最近のメモ取得のテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/memo/recent/?limit=5')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'テストメモ')
