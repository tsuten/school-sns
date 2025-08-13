from django.core.exceptions import ValidationError
from apps.core.organizations.models import OrganizationManager
from announcement.models import Announcement
import logging

logger = logging.getLogger(__name__)

class FeedService:
    """フィードサービスクラス"""

    def get_feed(self, user):
        """ユーザーのフィードを取得する"""
        try:
            # OrganizationManagerのインスタンスを作成
            org_manager = OrganizationManager()
            
            # ユーザーが所属する組織を取得
            organization = org_manager.get_organization_by_user(user.id)
            
            if organization is None:
                # 組織に所属していない場合は空のリストを返す
                logger.info(f"User {user.id} is not a member of any organization")
                return []
            
            # 組織に紐づくお知らせを取得し、シリアライズに備えてリスト化
            announcements_qs = Announcement.objects.get_announcements_by_organization(organization.id)
            return list(announcements_qs)
        except Exception as e:
            logger.error(f"Error getting feed for user {user.id}: {e}")
            raise ValidationError(f"フィードの取得に失敗しました: {str(e)}")
    
    def _get_class_feed(self, class_obj):
        """クラスのフィードを取得"""
        try:
            # クラス固有の投稿やお知らせを取得
            # ここでは基本的な実装として、クラス名を返す
            return {
                'type': 'class',
                'organization': class_obj.name,
                'feed_items': [],
                'total_count': 0
            }
        except Exception as e:
            logger.error(f"Error getting class feed: {e}")
            return {'type': 'class', 'organization': 'Unknown', 'feed_items': [], 'total_count': 0}
    
    def _get_school_feed(self, school_obj):
        """学校のフィードを取得"""
        try:
            # 学校固有の投稿やお知らせを取得
            # ここでは基本的な実装として、学校名を返す
            return {
                'type': 'school',
                'organization': school_obj.name,
                'feed_items': [],
                'total_count': 0
            }
        except Exception as e:
            logger.error(f"Error getting school feed: {e}")
            return {'type': 'school', 'organization': 'Unknown', 'feed_items': [], 'total_count': 0}