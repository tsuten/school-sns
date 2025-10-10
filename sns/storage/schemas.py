from ninja import Schema, ModelSchema
from typing import Optional, List
from datetime import datetime
from .models import SharedFile, FileCategory
# from .models import FileAccess  # ログ履歴機能を一時的に無効化


class FileCategorySchema(ModelSchema):
    """ファイルカテゴリのスキーマ"""
    max_size_display: str
    
    class Config:
        model = FileCategory
        model_fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active']
    
    @staticmethod
    def resolve_max_size_display(obj):
        return obj.get_max_size_display()


class FileUploadSchema(Schema):
    """ファイルアップロード時のスキーマ"""
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    upload_target_type: str  # 'class', 'circle', etc.
    upload_target_id: int
    is_public: bool = False


class SharedFileListSchema(ModelSchema):
    """ファイル一覧用のスキーマ"""
    uploader_name: str
    category_name: Optional[str]
    file_size_display: str
    extension: str
    upload_target_name: str
    
    class Config:
        model = SharedFile
        model_fields = [
            'id', 'original_name', 'title', 'description', 
            'file_size', 'file_type', 'is_public', 'created_at'
        ]
    
    @staticmethod
    def resolve_uploader_name(obj):
        return obj.uploader.username
    
    @staticmethod
    def resolve_category_name(obj):
        return obj.category.name if obj.category else None
    
    @staticmethod
    def resolve_file_size_display(obj):
        return obj.get_file_size_display()
    
    @staticmethod
    def resolve_extension(obj):
        return obj.get_extension()
    
    @staticmethod
    def resolve_upload_target_name(obj):
        if hasattr(obj.upload_target, 'name'):
            return obj.upload_target.name
        return str(obj.upload_target)


class SharedFileDetailSchema(SharedFileListSchema):
    """ファイル詳細用のスキーマ"""
    checksum: str
    can_download: bool
    # download_count: int  # ログ履歴機能を一時的に無効化
    
    class Config:
        model = SharedFile
        model_fields = [
            'id', 'original_name', 'title', 'description', 
            'file_size', 'file_type', 'is_public', 'created_at', 'updated_at'
        ]
    
    @staticmethod
    def resolve_can_download(obj):
        # 実際の実装では request.user を使用
        return True  # TODO: 権限チェック
    
    # ログ履歴機能を一時的に無効化
    # @staticmethod
    # def resolve_download_count(obj):
    #     return obj.access_logs.filter(action='download').count()


# ログ履歴機能を一時的に無効化
# class FileAccessSchema(ModelSchema):
#     """ファイルアクセス履歴のスキーマ"""
#     username: str
#     file_name: str
#     
#     class Config:
#         model = FileAccess
#         model_fields = ['id', 'action', 'ip_address', 'created_at']
#     
#     @staticmethod
#     def resolve_username(obj):
#         return obj.user.username
#     
#     @staticmethod
#     def resolve_file_name(obj):
#         return obj.file.original_name


class FileStatsSchema(Schema):
    """ファイル統計のスキーマ"""
    total_files: int
    total_size: int
    total_size_display: str
    files_by_category: List[dict]
    recent_uploads: List[SharedFileListSchema]
    # popular_files: List[SharedFileListSchema]  # ログ履歴機能を一時的に無効化


class ErrorSchema(Schema):
    """エラーレスポンスのスキーマ"""
    error: str
    message: str
    details: Optional[dict] = None