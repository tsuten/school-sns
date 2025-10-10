from functools import wraps
from django.utils import timezone
from shared.base_schemas import Status
from ninja.errors import HttpError
from ninja.errors import ValidationError
from ninja_jwt.exceptions import InvalidToken, TokenError
from ninja_jwt.authentication import JWTAuth
from django.core.exceptions import PermissionDenied
from django.http import Http404
from pydantic import ValidationError as PydanticValidationError
import importlib

def with_base_schema(func):
    """
    レスポンスにBaseSchemaの構造（status, timestamp, data）を自動的に適用するデコレータ
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            result = func(request, *args, **kwargs)
            
            # ビュー関数の結果が辞書であり、かつ'status'キーが'error'である場合は、最上位のステータスもエラーにする
            if isinstance(result, dict) and result.get('status') == Status.ERROR.value:
                return {
                    'status': Status.ERROR.value,
                    'timestamp': timezone.now(),
                    'data': result.get('data'), # 内部エラーレスポンスのdataをそのまま渡す
                    'error': result.get('error') # 内部エラーレスポンスのerrorをそのまま渡す
                }
            else:
                return {
                    'status': Status.SUCCESS.value,
                    'timestamp': timezone.now(),
                    'data': result,
                }
        except (InvalidToken, TokenError) as e:
            # 認証エラーの場合はBaseSchemaの構造で返す
            return {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': None,
                'error': 'Authentication Error',
                'auth_error': 'Invalid token'
            }
        except PermissionDenied as e:
            # 権限エラーの場合はBaseSchemaの構造で返す
            return {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': None,
                'error': 'Permission Error',
                'permission_error': 'You do not have permission to perform this action'
            }
        except Http404 as e:
            # 404エラーの場合はBaseSchemaの構造で返す
            return {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': None,
                'error': 'No Resource Found',
                'not_found_error': 'The requested resource does not exist'
            }
        except PydanticValidationError as e:
            return {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': e.errors(),
                'error': 'Validation Error'
            }
        except ValidationError as e:
            # DjangoのValidationErrorはerrors属性を持たない場合があるため、str()で変換
            return {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': str(e),
                'error': 'Validation Error'
            }
        except Exception as e:
            # 予期せぬエラーの処理
            import traceback
            from django.conf import settings
            response_data = {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': None,
                'error': 'Internal Server Error',
                'detail': str(e),
            }
            if settings.DEBUG:
                response_data['traceback'] = traceback.format_exc()
            return response_data
        except HttpError as e:
            # HttpErrorの場合はBaseSchemaの構造で返す
            return {
                'status': Status.ERROR.value,
                'timestamp': timezone.now(),
                'data': None,
                'error': e.message
            }
    
    return wrapper 

def send_signal(signal_type, signal_module_path, model_class=None, signal_mapping=None):
    """
    汎用シグナル送信デコレーター
    
    Args:
        signal_type (str): シグナルの種類 ('post', 'update', 'delete')
        signal_module_path (str): シグナルが定義されているモジュールのパス (例: 'chat.signals')
        model_class: モデルクラス（Noneの場合は結果オブジェクトのクラスを使用）
        signal_mapping (dict): シグナルタイプとシグナル名のマッピング
                              {'post': 'message_post_signal', 'update': 'message_update_signal', ...}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 元のメソッドを実行
            result = func(self, *args, **kwargs)
            
            # シグナルを送信
            try:
                # シグナルモジュールを動的にインポート
                signal_module = importlib.import_module(signal_module_path)
                
                # シグナルマッピングが指定されていない場合はデフォルトを使用
                default_mapping = {
                    'post': 'message_post_signal',
                    'update': 'message_update_signal', 
                    'delete': 'message_delete_signal'
                }
                actual_signal_mapping = signal_mapping if signal_mapping is not None else default_mapping
                
                # シグナルを取得
                signal_name = actual_signal_mapping.get(signal_type)
                if signal_name and hasattr(signal_module, signal_name):
                    signal = getattr(signal_module, signal_name)
                    
                    # 結果オブジェクトから必要な情報を抽出
                    if hasattr(result, 'id'):
                        # モデルクラスを動的に取得
                        actual_model_class = model_class
                        if actual_model_class is None:
                            actual_model_class = result.__class__
                        
                        # 基本的なシグナル送信データ
                        signal_data = {
                            'sender': actual_model_class,
                            'action': signal_type,
                            'user_id': getattr(result, 'sender_id', None) or (result.sender.id if result.sender else None),
                        }
                        
                        # モデル固有のフィールドを追加
                        if hasattr(result, 'receiver_id'):
                            signal_data['receiver_id'] = result.receiver_id
                        elif hasattr(result, 'receiver') and result.receiver:
                            signal_data['receiver_id'] = result.receiver.id
                        
                        # メッセージオブジェクトを追加（存在する場合）
                        if hasattr(result, 'content'):
                            signal_data['message'] = result
                        
                        print(f"[GENERIC DECORATOR] {signal_type}シグナル送信: {actual_model_class.__name__} ID={result.id}")
                        signal.send(**signal_data)
                        
            except Exception as e:
                # シグナル送信エラーはログに記録するが、メソッドの実行は継続
                print(f"[SIGNAL ERROR] 汎用シグナル送信エラー: {e}")
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"汎用シグナル送信エラー: {e}")
            
            return result
        return wrapper
    return decorator


def unified_auth(response_schema=None):
    """
    統一認証デコレータ
    JWTAuth認証とBaseSchemaレスポンス形式を自動適用
    
    使用例:
    @router.get("/example", **unified_auth())
    def example_view(request):
        return {"message": "success"}
    """
    return {
        "auth": JWTAuth(),
        "response": {
            200: response_schema if response_schema else dict,
            401: dict,  # 認証エラー
            403: dict,  # 権限エラー
            500: dict   # サーバーエラー
        }
    }


def unified_auth_decorator(func):
    """
    統一認証＋レスポンス形式のデコレータ（関数用）
    JWTAuth + BaseSchema形式の統一を自動適用
    
    使用例:
    @unified_auth_decorator
    def my_view(request):
        return {"data": "success"}
    """
    return with_base_schema(func) 