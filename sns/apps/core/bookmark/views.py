
from .models import BookmarkV2, BookmarkType
from ninja import Router
import uuid
from ninja_jwt.authentication import JWTAuth
from shared.decorators import with_base_schema
from shared.base_schemas import BaseSchema
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from .schemas import AddBookmarkSchema, DeleteBookmarkSchema, BookmarkV2Schema

router = Router(tags=['bookmark'])

@router.post('/add', auth=JWTAuth())
@with_base_schema
def add_bookmark(request, data: AddBookmarkSchema):
    try:
        # 新しいBookmarkV2モデルを使用
        bookmark, created = BookmarkV2.objects.get_or_create(
            user=request.user,
            bookmark_type=data.bookmark_type,
            object_id=data.object_id,
            defaults={
                'title': data.title,
                'description': data.description
            }
        )

        if not created:
            return {
                'status': 'success', 
                'message': 'Bookmark already exists.', 
                'bookmark_id': bookmark.id, 
                'timestamp': bookmark.created_at
            }

        return {
            'status': 'success', 
            'bookmark_id': bookmark.id, 
            'timestamp': bookmark.created_at
        }

    except IntegrityError:
        # unique_together制約違反の場合
        return {
            'status': 'error', 
            'error': 'このブックマークは既に存在します。', 
            'code': 'DUPLICATE_BOOKMARK'
        }
    except Exception as e:
        return {
            'status': 'error', 
            'error': f'ブックマークの追加中にエラーが発生しました: {e}'
        }
    
@router.delete('/delete', auth=JWTAuth())
@with_base_schema
def delete_bookmark(request, data: DeleteBookmarkSchema):
    try:
        bookmark = BookmarkV2.objects.get(id=data.bookmark_id)
        bookmark.delete_object()
        return {'message': 'Bookmark deleted successfully.'}
    except BookmarkV2.DoesNotExist:
        return {'error': 'Bookmark not found.'}
    
@router.get('/list', auth=JWTAuth(), response=BaseSchema)
@with_base_schema
def list_bookmark(request):
    try:
        bookmarks = BookmarkV2.objects.get_bookmarks(user=request.user)
        # dataフィールドにBookmarkV2Schemaのリストを格納
        return {
            'status': 'success', 
            'data': [BookmarkV2Schema(**bookmark.to_dict()) for bookmark in bookmarks]
        }
    except Exception as e:
        return {
            'status': 'error', 
            'error': f'ブックマークの取得中にエラーが発生しました: {e}'
        }

@router.get('/list/{bookmark_type}', auth=JWTAuth(), response=BaseSchema)
@with_base_schema
def list_bookmark_by_type(request, bookmark_type: str):
    """特定のタイプのブックマークを取得"""
    try:
        # 有効なブックマークタイプかチェック
        valid_types = [choice.value for choice in BookmarkType]
        if bookmark_type not in valid_types:
            return {
                'status': 'error',
                'error': f'無効なブックマークタイプです: {bookmark_type}'
            }
        
        bookmarks = BookmarkV2.objects.get_bookmarks(
            user=request.user, 
            bookmark_type=bookmark_type
        )
        
        return {
            'status': 'success', 
            'data': [BookmarkV2Schema(**bookmark.to_dict()) for bookmark in bookmarks]
        }
    except Exception as e:
        return {
            'status': 'error', 
            'error': f'ブックマークの取得中にエラーが発生しました: {e}'
        }
