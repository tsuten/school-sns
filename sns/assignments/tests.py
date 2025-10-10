from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Assignment

User = get_user_model()

class AssignmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assignment = Assignment.objects.create(
            title='テスト課題',
            description='テスト課題の概要',
            created_by=self.user,
            due_date=timezone.now() + timedelta(days=7)
        )
        self.assignment.assigned_to.add(self.user)

    def test_assignment_creation(self):
        """課題の作成テスト"""
        self.assertEqual(self.assignment.title, 'テスト課題')
        self.assertEqual(self.assignment.description, 'テスト課題の概要')
        self.assertFalse(self.assignment.is_deleted)

    def test_assignment_str_representation(self):
        """課題の文字列表現テスト"""
        self.assertEqual(str(self.assignment), 'テスト課題')

    def test_assignment_manager_methods(self):
        """課題マネージャーのメソッドテスト"""
        # アクティブな課題の取得
        active_assignments = Assignment.objects.get_active_assignments()
        self.assertIn(self.assignment, active_assignments)
        
        # ユーザーに割り当てられた課題の取得
        user_assignments = Assignment.objects.get_assignments_by_user(self.user)
        self.assertIn(self.assignment, user_assignments)
        
        # 作成者による課題の取得
        created_assignments = Assignment.objects.get_created_by_user(self.user)
        self.assertIn(self.assignment, created_assignments)

    def test_assignment_overdue_detection(self):
        """課題の期限切れ判定テスト"""
        # 期限を過去に設定
        self.assignment.due_date = timezone.now() - timedelta(days=1)
        self.assignment.save()
        
        # 期限切れの判定
        self.assertTrue(self.assignment.is_overdue())

    def test_assignment_remaining_time(self):
        """課題の残り時間取得テスト"""
        # 期限を明日に設定
        tomorrow = timezone.now() + timedelta(days=1)
        self.assignment.due_date = tomorrow
        self.assignment.save()
        
        remaining = self.assignment.get_remaining_time()
        self.assertIsInstance(remaining, timedelta)
        self.assertGreater(remaining.total_seconds(), 0)

    def test_assignment_logical_delete(self):
        """課題の論理削除テスト"""
        self.assignment.delete()
        self.assertTrue(self.assignment.is_deleted)
        self.assertIsNotNone(self.assignment.deleted_at)
