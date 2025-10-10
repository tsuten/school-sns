from ninja import Router
from feed.services import FeedService
from feed.schemas import FeedResponseSchema, ErrorResponseSchema, ClassFeedSchema, SchoolFeedSchema
from announcement.schemas import AnnouncementResponseSchema
from ninja_jwt.authentication import JWTAuth
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)
router = Router(tags=["feed"])

@router.get("/", response={200: FeedResponseSchema, 400: ErrorResponseSchema, 500: ErrorResponseSchema}, auth=JWTAuth())
def get_feed(request):
    """フィードを取得する"""
    try:
        # FeedServiceのインスタンスを作成
        feed_service = FeedService()
        feed_data = feed_service.get_feed(request.user)
        
        # レスポンスデータを構築
        if isinstance(feed_data, dict):
            if feed_data.get('type') == 'class':
                response_data = ClassFeedSchema(
                    type=feed_data['type'],
                    organization=feed_data['organization'],
                    feed_items=feed_data.get('feed_items', []),
                    total_count=len(feed_data.get('feed_items', []))
                )
            elif feed_data.get('type') == 'school':
                response_data = SchoolFeedSchema(
                    type=feed_data['type'],
                    organization=feed_data['organization'],
                    feed_items=feed_data.get('feed_items', []),
                    total_count=len(feed_data.get('feed_items', []))
                )
            else:
                response_data = feed_data
        else:
            # リストの場合（お知らせ一覧想定）は各要素をAnnouncementResponseSchemaに変換
            if isinstance(feed_data, list):
                response_data = [AnnouncementResponseSchema.from_announcement(a) for a in feed_data]
            else:
                response_data = feed_data
        
        return FeedResponseSchema(
            success=True,
            data=response_data,
            message="フィードの取得に成功しました"
        )
        
    except ValidationError as e:
        logger.warning(f"Feed validation error for user {request.user.id}: {e}")
        return ErrorResponseSchema(
            success=False,
            error=str(e),
            message="フィードの検証エラーが発生しました"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_feed for user {request.user.id}: {e}")
        return ErrorResponseSchema(
            success=False,
            error="フィードの取得中にエラーが発生しました",
            message="予期しないエラーが発生しました"
        )