
from .models import Bookmark
from ninja import Router
import uuid
from django.contrib.contenttypes.models import ContentType
from ninja_jwt.authentication import JWTAuth
from shared.decorators import with_base_schema
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from .schemas import AddBookmarkSchema, DeleteBookmarkSchema, BookmarkSchema
from shared.base_schemas import BaseSchema # BaseSchemaをインポート

router = Router(tags=['bookmark'])

@router.post('/add', auth=JWTAuth())
@with_base_schema
def add_bookmark(request, data: AddBookmarkSchema):
    try:
        # `content_type_str`はスキーマで文字列として渡されるモデル名です
        model_class = apps.get_model(app_label=data.app_label, model_name=data.model_name)
        item_obj = model_class.objects.get(id=data.post_id)
        content_type_obj = ContentType.objects.get_for_model(item_obj)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type=content_type_obj,
            object_id=data.post_id,
            defaults={'item': item_obj} # itemはGenericForeignKeyなので、作成時に指定
        )

        if not created:
            return {'status': 'success', 'message': 'Bookmark already exists.', 'bookmark_id': bookmark.id, 'timestamp': bookmark.created_at}

        return {'status': 'success', 'bookmark_id': bookmark.id, 'timestamp': bookmark.created_at}

    except ObjectDoesNotExist as e:
        return {'status': 'error', 'error': f'指定された対象が見つかりません: {e}'}
    except LookupError as e:
        return {'status': 'error', 'error': f'無効なコンテンツタイプが指定されました: {e}'}
    except IntegrityError:
        # unique_together制約違反の場合
        return {'status': 'error', 'error': 'このブックマークは既に存在します。', 'code': 'DUPLICATE_BOOKMARK'}
    except Exception as e:
        return {'status': 'error', 'error': f'ブックマークの追加中にエラーが発生しました: {e}'}
    
@router.delete('/delete', auth=JWTAuth())
@with_base_schema
def delete_bookmark(request, data: DeleteBookmarkSchema):
    try:
        bookmark = Bookmark.objects.get(id=data.bookmark_id)
        bookmark.delete_object()
        return {'message': 'Bookmark deleted successfully.'}
    except Bookmark.DoesNotExist:
        return {'error': 'Bookmark not found.'}
    
@router.get('/list', auth=JWTAuth(), response=BaseSchema) # responseをBaseSchemaに変更
@with_base_schema
def list_bookmark(request):
    try:
        bookmarks = Bookmark.objects.get_bookmarks(user=request.user)
        # dataフィールドにBookmarkSchemaのリストを格納
        return {'status': 'success', 'data': [BookmarkSchema(**bookmark.to_dict()) for bookmark in bookmarks]}
    except Exception as e:
        return {'status': 'error', 'error': f'ブックマークの取得中にエラーが発生しました: {e}'}
