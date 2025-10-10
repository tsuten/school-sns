from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any

router = Router(tags=['admin'])

@router.get("/test", auth=JWTAuth())
def test_endpoint(request) -> Dict[str, Any]:
    """テスト用エンドポイント - 基本的な動作確認"""
    try:
        return {
            "message": "Admin module is working",
            "user_id": str(request.user.id) if request.user.is_authenticated else "anonymous",
            "is_staff": request.user.is_staff if request.user.is_authenticated else False,
            "timestamp": timezone.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": timezone.now().isoformat()
        }

@router.get("/stats", auth=JWTAuth())
def get_admin_stats(request) -> Dict[str, Any]:
    """管理者用の統計情報を取得"""
    
    try:
        # 権限チェック（管理者のみ）
        if not request.user.is_staff:
            raise HttpError(403, "管理者権限が必要です")
        
        # カスタムユーザーモデルをインポート
        from apps.core.users.models import User, UserProfile
        
        # 現在の日時
        now = timezone.now()
        # 30日前
        thirty_days_ago = now - timedelta(days=30)
        
        # 総ユーザー数
        total_users = User.objects.count()
        
        # アクティブユーザー数（30日以内にログインしたユーザー）
        active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
        
        # 今月の新規ユーザー数（UserProfileのcreated_atを使用）
        new_users_this_month = UserProfile.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # 投稿数（postsアプリが存在する場合）
        try:
            from sns.posts.models import Post
            total_posts = Post.objects.count()
            posts_this_month = Post.objects.filter(created_at__gte=thirty_days_ago).count()
        except ImportError:
            total_posts = 0
            posts_this_month = 0
        
        # サークル数（circleアプリが存在する場合）
        try:
            from sns.circle.models import Circle
            total_circles = Circle.objects.count()
            active_circles = Circle.objects.filter(is_active=True).count()
        except ImportError:
            total_circles = 0
            active_circles = 0
        
        # システムヘルス（仮の計算）
        system_health = min(100, max(0, 100 - (total_users // 100)))
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_this_month": new_users_this_month,
            "total_posts": total_posts,
            "posts_this_month": posts_this_month,
            "total_circles": total_circles,
            "active_circles": active_circles,
            "system_health": system_health,
            "active_sessions": min(500, active_users * 2),  # 仮の値
            "last_updated": now.isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": timezone.now().isoformat()
        }

@router.get("/users/stats", auth=JWTAuth())
def get_users_stats(request) -> Dict[str, Any]:
    """ユーザー関連の統計情報のみを取得"""
    
    try:
        # 権限チェック（管理者のみ）
        if not request.user.is_staff:
            raise HttpError(403, "管理者権限が必要です")
        
        # カスタムユーザーモデルをインポート
        from apps.core.users.models import User, UserProfile
        
        # 現在の日時
        now = timezone.now()
        # 30日前
        thirty_days_ago = now - timedelta(days=30)
        
        # 総ユーザー数
        total_users = User.objects.count()
        
        # アクティブユーザー数（30日以内にログインしたユーザー）
        active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
        
        # 今月の新規ユーザー数（UserProfileのcreated_atを使用）
        new_users_this_month = UserProfile.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # ユーザー登録の月別統計（過去6ヶ月、UserProfileのcreated_atを使用）
        monthly_stats = []
        for i in range(6):
            month_start = now.replace(day=1) - timedelta(days=i*30)
            month_end = month_start + timedelta(days=30)
            count = UserProfile.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_stats.append({
                "month": month_start.strftime("%Y-%m"),
                "count": count
            })
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_this_month": new_users_this_month,
            "monthly_stats": monthly_stats,
            "last_updated": now.isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": timezone.now().isoformat()
        }
