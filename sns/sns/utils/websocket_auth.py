from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from ninja_jwt.tokens import UntypedToken
from ninja_jwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import jwt

User = get_user_model()

@database_sync_to_async
def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    WebSocket接続でJWT認証を行うミドルウェア
    クエリパラメータまたはヘッダーからトークンを取得
    """
    
    async def __call__(self, scope, receive, send):
        # HTTPヘッダーからトークンを取得（優先）
        token = None
        headers = dict(scope.get('headers', []))
        
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # クエリパラメータからトークンを取得（フォールバック）
        if not token:
            query_string = scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
        
        # トークンが存在しない場合は匿名ユーザー
        if not token:
            scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)
        
        try:
            # JWTトークンを検証
            decoded_token = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )
            user_id = decoded_token.get('user_id')
            
            if user_id:
                scope['user'] = await get_user_by_id(user_id)
            else:
                scope['user'] = AnonymousUser()
                
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, TokenError):
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner) 