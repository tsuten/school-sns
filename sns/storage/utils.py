import os
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
from django.conf import settings
from typing import Dict, Any


def validate_file_security(uploaded_file) -> Dict[str, Any]:
    """ファイルのセキュリティチェック"""
    try:
        # ファイルサイズチェック（デフォルト50MB）
        max_size = getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024)
        if uploaded_file.size > max_size:
            return {
                'is_valid': False,
                'error': f'ファイルサイズが制限を超えています（最大: {max_size // (1024*1024)}MB）'
            }
        
        # ファイル名の安全性チェック
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in uploaded_file.name for char in dangerous_chars):
            return {
                'is_valid': False,
                'error': 'ファイル名に使用できない文字が含まれています'
            }
        
        # 拡張子チェック
        allowed_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'txt', 'rtf', 'zip', 'rar', '7z',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
            'mp3', 'mp4', 'avi', 'mov', 'wmv', 'webm'
        ]
        
        file_ext = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
        if file_ext not in allowed_extensions:
            return {
                'is_valid': False,
                'error': f'このファイル形式（.{file_ext}）は許可されていません'
            }
        
        # MIMEタイプチェック（python-magicを使用）
        if HAS_MAGIC:
            try:
                uploaded_file.seek(0)
                file_content = uploaded_file.read(1024)  # 先頭1KBを読む
                uploaded_file.seek(0)
                
                mime = magic.Magic(mime=True)
                detected_mime = mime.from_buffer(file_content)
                
                # 危険なMIMEタイプをブロック
                dangerous_mimes = [
                    'application/x-executable',
                    'application/x-msdownload',
                    'application/x-msdos-program',
                    'application/x-sh',
                    'text/x-shellscript'
                ]
                
                if detected_mime in dangerous_mimes:
                    return {
                        'is_valid': False,
                        'error': '実行可能ファイルはアップロードできません'
                    }
                    
            except Exception:
                # python-magicでエラーが発生した場合は続行
                pass
        
        return {'is_valid': True, 'error': None}
        
    except Exception as e:
        return {
            'is_valid': False,
            'error': f'ファイルの検証中にエラーが発生しました: {str(e)}'
        }


def get_client_ip(request) -> str:
    """クライアントのIPアドレスを取得"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """ユーザーエージェントを取得"""
    return request.META.get('HTTP_USER_AGENT', '')


def format_file_size(size_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式で返す"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_icon(file_extension: str) -> str:
    """ファイル拡張子に応じたアイコンを返す"""
    extension = file_extension.lower().lstrip('.')
    
    icon_map = {
        # ドキュメント
        'pdf': '📄',
        'doc': '📝', 'docx': '📝',
        'xls': '📊', 'xlsx': '📊',
        'ppt': '📋', 'pptx': '📋',
        'txt': '📃', 'rtf': '📃',
        
        # 画像
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 
        'gif': '🖼️', 'bmp': '🖼️', 'svg': '🖼️', 'webp': '🖼️',
        
        # 動画
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 
        'wmv': '🎬', 'webm': '🎬',
        
        # 音声
        'mp3': '🎵', 'wav': '🎵', 'aac': '🎵',
        
        # アーカイブ
        'zip': '🗜️', 'rar': '🗜️', '7z': '🗜️',
    }
    
    return icon_map.get(extension, '📁')