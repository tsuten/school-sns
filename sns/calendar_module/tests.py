from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import NewSchedule
from datetime import datetime, timezone
import uuid

User = get_user_model()

class NewScheduleCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # テスト用のスケジュールを作成
        self.schedule = NewSchedule.objects.create(
            user=self.user,
            title='Test Schedule',
            description='Test Description',
            is_all_day=False,
            start_time=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc)
        )

    def test_get_new_schedules(self):
        """NewSchedule一覧取得のテスト"""
        response = self.client.get('/api/calendar/new-schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Schedule')

    def test_get_new_schedule(self):
        """特定のNewSchedule取得のテスト"""
        response = self.client.get(f'/api/calendar/new-schedules/{self.schedule.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Schedule')

    def test_create_new_schedule(self):
        """NewSchedule作成のテスト"""
        data = {
            'title': 'New Test Schedule',
            'description': 'New Test Description',
            'is_all_day': True,
            'start_time': '2024-01-02T10:00:00Z',
            'end_time': '2024-01-02T11:00:00Z'
        }
        response = self.client.post('/api/calendar/new-schedules/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Test Schedule')
        self.assertTrue(response.data['is_all_day'])

    def test_update_new_schedule(self):
        """NewSchedule更新のテスト"""
        data = {
            'title': 'Updated Schedule',
            'description': 'Updated Description'
        }
        response = self.client.put(f'/api/calendar/new-schedules/{self.schedule.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Schedule')
        self.assertEqual(response.data['description'], 'Updated Description')

    def test_delete_new_schedule(self):
        """NewSchedule削除のテスト"""
        response = self.client.delete(f'/api/calendar/new-schedules/{self.schedule.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        
        # 論理削除されていることを確認
        schedule = NewSchedule.objects.get(id=self.schedule.id)
        self.assertTrue(schedule.is_deleted)

    def test_unauthorized_access(self):
        """認証されていないユーザーのアクセス制限テスト"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/calendar/new-schedules/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_isolation(self):
        """ユーザー間のデータ分離テスト"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # 他のユーザーのスケジュールにアクセスできないことを確認
        response = self.client.get(f'/api/calendar/new-schedules/{self.schedule.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 自分のスケジュールはアクセス可能
        
        # 他のユーザーでログイン
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f'/api/calendar/new-schedules/{self.schedule.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # 他のユーザーのスケジュールはアクセス不可
