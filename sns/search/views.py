from ninja import Router
from watson import search as watson
from ninja.errors import HttpError
from typing import Dict, Any, List
from django.apps import apps

router = Router(tags=["search"])

# 検索結果のモデル設定
SEARCH_MODEL_CONFIG = {
    'post': {
        'title_field': 'title',
        'description_field': 'content',
        'author_field': 'user.username',
        'date_field': 'created_at',
        'metadata_fields': ['is_public', 'tags'],
        'display_name': '投稿'
    },
    'user': {
        'title_field': 'username',
        'description_field': None,
        'author_field': 'username',
        'date_field': 'date_joined',
        'metadata_fields': ['is_active'],
        'display_name': 'ユーザー'
    },
    'event': {
        'title_field': 'title',
        'description_field': 'description',
        'author_field': 'organizer.username',
        'date_field': 'start_date',
        'metadata_fields': ['location', 'end_date', 'is_published'],
        'display_name': 'イベント'
    },
    'announcement': {
        'title_field': 'title',
        'description_field': 'content',
        'author_field': 'posted_by.username',
        'date_field': 'created_at',
        'metadata_fields': ['priority', 'post_to'],
        'display_name': 'お知らせ'
    },
    'circle': {
        'title_field': 'name',
        'description_field': 'description',
        'author_field': 'founder.username',
        'date_field': 'created_at',
        'metadata_fields': ['category', 'is_private'],
        'metadata_methods': ['members.count()'],
        'display_name': 'サークル'
    }
}


def get_nested_attr(obj, attr_path, default=None):
    """ネストした属性を安全に取得"""
    try:
        attrs = attr_path.split('.')
        current = obj
        for attr in attrs:
            if attr.endswith('()'):
                # メソッド呼び出し
                method_name = attr[:-2]
                current = getattr(current, method_name)()
            else:
                current = getattr(current, attr)
        return current
    except (AttributeError, TypeError):
        return default


def extract_search_result_data(obj, model_config, result_type='unified'):
    """検索結果オブジェクトからデータを動的に抽出"""
    try:
        # 基本情報の抽出
        title = get_nested_attr(obj, model_config['title_field'], str(obj.id))
        
        # description の処理
        description_field = model_config.get('description_field')
        if description_field:
            description = get_nested_attr(obj, description_field, '')
            if description and len(description) > 200:
                description = description[:200] + '...'
        else:
            description = f"{model_config['display_name']}の詳細"
        
        # 作成者と日付
        author = get_nested_attr(obj, model_config['author_field'], 'Unknown')
        date_value = get_nested_attr(obj, model_config['date_field'])
        created_at = date_value.isoformat() if hasattr(date_value, 'isoformat') else str(date_value)
        
        # 基本データ構造
        base_data = {
            'id': str(obj.id),
            'type': obj.__class__.__name__.lower(),
            'title': title,
            'description': description,
            'author': author,
            'created_at': created_at
        }
        
        # 統合ビュー用のメタデータ
        if result_type == 'unified':
            metadata = {}
            
            # 通常のフィールド
            for field in model_config.get('metadata_fields', []):
                value = get_nested_attr(obj, field)
                if hasattr(value, 'all'):  # ManyToManyField
                    if field == 'tags':
                        metadata[field] = [tag.name for tag in value.all()]
                    else:
                        metadata[field] = [str(item) for item in value.all()]
                else:
                    metadata[field] = value
            
            # メソッド呼び出し
            for method in model_config.get('metadata_methods', []):
                field_name = method.split('.')[0] + '_count'
                metadata[field_name] = get_nested_attr(obj, method, 0)
            
            base_data['metadata'] = metadata
        
        return base_data
        
    except Exception as e:
        # フォールバック
        return {
            'id': str(getattr(obj, 'id', 'unknown')),
            'type': obj.__class__.__name__.lower(),
            'title': str(obj),
            'description': f"{obj.__class__.__name__}の詳細",
            'author': 'Unknown',
            'created_at': '',
            'metadata': {} if result_type == 'unified' else None
        }


@router.get("")
def search_api(request, q: str = ""):
    """
    分類検索APIエンドポイント
    投稿、ユーザー、イベント、お知らせ、サークルを横断検索（分類別）
    """
    query = q.strip()
    
    if not query:
        raise HttpError(400, "検索クエリが空です")
    
    if len(query) < 2:
        raise HttpError(400, "検索クエリは2文字以上で入力してください")
    
    try:
        # watson で検索実行
        search_results = watson.search(query)
        
        # 結果を分類・整理
        results = {
            'posts': [],
            'users': [],
            'events': [],
            'announcements': [],
            'circles': [],
            'total_count': len(search_results)
        }
        
        for result in search_results:
            obj = result.object
            model_name = obj.__class__.__name__.lower()
            
            # 設定を取得
            model_config = SEARCH_MODEL_CONFIG.get(model_name)
            if not model_config:
                continue
            
            # データを動的に抽出
            data = extract_search_result_data(obj, model_config, 'classified')
            
            # 分類別に振り分け
            category_key = f"{model_name}s"
            if category_key in results:
                results[category_key].append(data)
        
        return {
            'status': 'success',
            'query': query,
            'results': results
        }
        
    except Exception as e:
        raise HttpError(500, f'検索中にエラーが発生しました: {str(e)}')


@router.get("/unified")
def search_unified_api(request, q: str = "", limit: int = 20):
    """
    統合検索APIエンドポイント（分類なし）
    すべての検索結果を統合して返す
    """
    query = q.strip()
    
    if not query:
        raise HttpError(400, "検索クエリが空です")
    
    if len(query) < 2:
        raise HttpError(400, "検索クエリは2文字以上で入力してください")
    
    try:
        # watson で検索実行
        search_results = watson.search(query)[:limit]
        
        # 統合された結果リスト
        unified_results = []
        
        for result in search_results:
            obj = result.object
            model_name = obj.__class__.__name__.lower()
            
            # 設定を取得
            model_config = SEARCH_MODEL_CONFIG.get(model_name)
            if not model_config:
                continue
            
            # データを動的に抽出
            data = extract_search_result_data(obj, model_config, 'unified')
            unified_results.append(data)
        
        return {
            'status': 'success',
            'query': query,
            'total_count': len(unified_results),
            'results': unified_results
        }
        
    except Exception as e:
        raise HttpError(500, f'検索中にエラーが発生しました: {str(e)}')


@router.get("/suggestions")
def search_suggestions_api(request, q: str = ""):
    """
    検索サジェスト機能
    """
    query = q.strip()
    
    if not query or len(query) < 1:
        return {
            'status': 'success',
            'suggestions': []
        }
    
    try:
        # 簡単なサジェスト（完全実装ではよりスマートにする）
        search_results = watson.search(query)[:5]  # 上位5件
        
        suggestions = []
        for result in search_results:
            obj = result.object
            model_name = obj.__class__.__name__.lower()
            
            # 設定を取得
            model_config = SEARCH_MODEL_CONFIG.get(model_name)
            if not model_config:
                continue
            
            # タイトルを動的に取得
            title = get_nested_attr(obj, model_config['title_field'], str(obj.id))
            display_name = model_config['display_name']
            
            suggestions.append(f"{display_name}: {title}")
        
        return {
            'status': 'success',
            'suggestions': suggestions
        }
        
    except Exception as e:
        raise HttpError(500, f'サジェスト取得中にエラーが発生しました: {str(e)}')