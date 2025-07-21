from django.http import JsonResponse
from django.utils import timezone
from shared.base_schemas import Status
from ninja.errors import HttpError
from ninja.errors import ValidationError
from pydantic import ValidationError as PydanticValidationError

def custom_404_handler(request, exception=None):
    """
    カスタム404ハンドラー - BaseSchemaの構造で404エラーを返す
    """
    # APIエンドポイントの場合のみJSONレスポンスを返す
    if request.path.startswith('/api/'):
        return JsonResponse({
            'status': Status.ERROR.value,
            'timestamp': timezone.now(),
            'data': None,
            'error': 'No Resource Found',
            'not_found_error': 'The requested resource does not exist',
            'request_path': request.path,
            'request_method': request.method
        }, status=404)
    
    # その他の場合は標準の404ページを返す
    from django.shortcuts import render
    return render(request, '404.html', status=404)

def custom_500_handler(request, exception=None):
    """
    カスタム500ハンドラー - BaseSchemaの構造で500エラーを返す
    """
    return JsonResponse({
        'status': Status.ERROR.value,
        'timestamp': timezone.now(),
        'data': None,
        'error': 'Server Error',
        'server_error': 'An internal server error occurred'
    }, status=500)

def custom_403_handler(request, exception=None):
    """
    カスタム403ハンドラー - BaseSchemaの構造で403エラーを返す
    """
    return JsonResponse({
        'status': Status.ERROR.value,
        'timestamp': timezone.now(),
        'data': None,
        'error': 'Permission Error',
        'permission_error': 'You do not have permission to access this resource'
    }, status=403)

def api_exception_handler(request, exc):
    """API用の統一的な例外ハンドラー"""
    if isinstance(exc, (ValidationError, PydanticValidationError)) or (hasattr(exc, 'detail') and isinstance(exc.detail, list)):
        # バリデーションエラーとDjango Ninjaの型エラーを処理
        return JsonResponse({
            'status': Status.ERROR.value,
            'timestamp': timezone.now(),
            'data': None,
            'error': 'Validation Error'
        }, status=422)
    elif isinstance(exc, HttpError):
        return JsonResponse({
            'status': Status.ERROR.value,
            'timestamp': timezone.now(),
            'data': None,
            'error': str(exc)
        }, status=exc.status_code)
    else:
        return custom_500_handler(request, exc)

def api_404_handler(request, exception=None):
    """APIエンドポイント用の404ハンドラー"""
    # メディアファイルや静的ファイルの場合は標準の404ページを返す
    if request.path.startswith('/media/') or request.path.startswith('/static/'):
        from django.views.defaults import page_not_found
        return page_not_found(request, exception)
    
    # APIエンドポイントの場合のみJSONレスポンスを返す
    if request.path.startswith('/api/'):
        return custom_404_handler(request, exception)
    
    # その他の場合は標準の404ページを返す
    from django.views.defaults import page_not_found
    return page_not_found(request, exception) 