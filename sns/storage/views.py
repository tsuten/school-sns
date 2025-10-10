import os
from typing import List
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum, Q
from ninja import Router, File, UploadedFile
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

from .models import SharedFile, FileCategory
# from .models import FileAccess  # ログ履歴機能を一時的に無効化
from .schemas import (
    FileCategorySchema, FileUploadSchema, SharedFileListSchema, 
    SharedFileDetailSchema, FileStatsSchema, ErrorSchema
)
# from .schemas import FileAccessSchema  # ログ履歴機能を一時的に無効化
from .utils import validate_file_security
# from .utils import get_client_ip, get_user_agent  # ログ履歴機能を一時的に無効化

router = Router(tags=["storage"])


@router.get("/categories", response=List[FileCategorySchema])
def list_categories(request):
    """ファイルカテゴリ一覧を取得"""
    return FileCategory.objects.filter(is_active=True)


@router.post("/upload", response={200: SharedFileDetailSchema, 400: ErrorSchema}, auth=JWTAuth())
def upload_file(request, file: UploadedFile = File(...), data: FileUploadSchema = None):
    """ファイルをアップロード"""
    try:
        # セキュリティチェック
        security_result = validate_file_security(file)
        if not security_result['is_valid']:
            raise HttpError(400, security_result['error'])
        
        # アップロード先の検証
        try:
            content_type = ContentType.objects.get(model=data.upload_target_type.lower())
            upload_target = content_type.get_object_for_this_type(id=data.upload_target_id)
        except ContentType.DoesNotExist:
            raise HttpError(400, "無効なアップロード先タイプです")
        except content_type.model_class().DoesNotExist:
            raise HttpError(400, "指定されたアップロード先が見つかりません")
        
        # カテゴリの検証
        category = None
        if data.category_id:
            try:
                category = FileCategory.objects.get(id=data.category_id, is_active=True)
                
                # ファイルサイズチェック
                if file.size > category.max_file_size:
                    raise HttpError(400, f"ファイルサイズが制限を超えています（最大: {category.get_max_size_display()}）")
                
                # 拡張子チェック
                if category.allowed_extensions:
                    file_ext = os.path.splitext(file.name)[1].lower().lstrip('.')
                    if file_ext not in category.allowed_extensions:
                        raise HttpError(400, f"このファイル形式（.{file_ext}）は許可されていません")
                        
            except FileCategory.DoesNotExist:
                raise HttpError(400, "指定されたカテゴリが見つかりません")
        
        # SharedFileオブジェクトを作成
        shared_file = SharedFile(
            file=file,
            title=data.title or file.name,
            description=data.description or "",
            category=category,
            uploader=request.user,
            upload_target=upload_target,
            is_public=data.is_public
        )
        shared_file.save()
        
        # アクセスログを記録（一時的に無効化）
        # FileAccess.objects.create(
        #     file=shared_file,
        #     user=request.user,
        #     action='view',
        #     ip_address=get_client_ip(request),
        #     user_agent=get_user_agent(request)
        # )
        
        return shared_file
        
    except Exception as e:
        return 400, {"error": "upload_failed", "message": str(e)}


@router.get("/list", response=List[SharedFileListSchema], auth=JWTAuth())
def list_files(request, 
               target_type: str = None, 
               target_id: int = None,
               category_id: int = None,
               search: str = None,
               limit: int = 20,
               offset: int = 0):
    """ファイル一覧を取得"""
    queryset = SharedFile.objects.for_user(request.user)
    
    # フィルタリング
    if target_type and target_id:
        content_type = get_object_or_404(ContentType, model=target_type.lower())
        queryset = queryset.filter(
            upload_target_type=content_type,
            upload_target_id=target_id
        )
    
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    if search:
        queryset = queryset.filter(
            Q(original_name__icontains=search) |
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    return queryset[offset:offset + limit]


@router.get("/detail/{file_id}", response={200: SharedFileDetailSchema, 404: ErrorSchema}, auth=JWTAuth())
def get_file_detail(request, file_id: str):
    """ファイル詳細を取得"""
    try:
        file_obj = get_object_or_404(SharedFile, id=file_id)
        
        # アクセス権限チェック
        if not file_obj.can_access(request.user):
            raise HttpError(403, "このファイルにアクセスする権限がありません")
        
        # 閲覧ログを記録（一時的に無効化）
        # FileAccess.objects.create(
        #     file=file_obj,
        #     user=request.user,
        #     action='view',
        #     ip_address=get_client_ip(request),
        #     user_agent=get_user_agent(request)
        # )
        
        return file_obj
        
    except Http404:
        return 404, {"error": "not_found", "message": "ファイルが見つかりません"}


@router.get("/download/{file_id}", auth=JWTAuth())
def download_file(request, file_id: str):
    """ファイルをダウンロード"""
    file_obj = get_object_or_404(SharedFile, id=file_id)
    
    # アクセス権限チェック
    if not file_obj.can_access(request.user):
        raise HttpError(403, "このファイルにアクセスする権限がありません")
    
    # ダウンロードログを記録（一時的に無効化）
    # FileAccess.objects.create(
    #     file=file_obj,
    #     user=request.user,
    #     action='download',
    #     ip_address=get_client_ip(request),
    #     user_agent=get_user_agent(request)
    # )
    
    # ファイルレスポンスを返す
    try:
        response = FileResponse(
            file_obj.file.open('rb'),
            as_attachment=True,
            filename=file_obj.original_name
        )
        response['Content-Length'] = file_obj.file_size
        response['Content-Type'] = file_obj.file_type
        return response
    except FileNotFoundError:
        raise HttpError(404, "ファイルが見つかりません")


@router.delete("/delete/{file_id}", response={200: dict, 403: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth())
def delete_file(request, file_id: str):
    """ファイルを削除（論理削除）"""
    try:
        file_obj = get_object_or_404(SharedFile, id=file_id)
        
        # 削除権限チェック（アップロード者のみ）
        if file_obj.uploader != request.user:
            return 403, {"error": "permission_denied", "message": "このファイルを削除する権限がありません"}
        
        # 論理削除
        file_obj.is_active = False
        file_obj.save()
        
        return {"message": "ファイルが削除されました"}
        
    except Http404:
        return 404, {"error": "not_found", "message": "ファイルが見つかりません"}


# ログ履歴機能を一時的に無効化
# @router.get("/access-logs/{file_id}", response=List[FileAccessSchema], auth=JWTAuth())
# def get_file_access_logs(request, file_id: str, limit: int = 50):
#     """ファイルのアクセス履歴を取得（アップロード者のみ）"""
#     file_obj = get_object_or_404(SharedFile, id=file_id)
#     
#     # 権限チェック（アップロード者のみ）
#     if file_obj.uploader != request.user:
#         raise HttpError(403, "このファイルのアクセス履歴を見る権限がありません")
#     
#     return file_obj.access_logs.all()[:limit]


@router.get("/stats", response=FileStatsSchema, auth=JWTAuth())
def get_file_stats(request):
    """ファイル統計を取得"""
    user_files = SharedFile.objects.filter(uploader=request.user)
    
    # 基本統計
    total_files = user_files.count()
    total_size = user_files.aggregate(Sum('file_size'))['file_size__sum'] or 0
    
    # カテゴリ別統計
    files_by_category = list(
        user_files.values('category__name', 'category__icon')
        .annotate(count=Count('id'), size=Sum('file_size'))
        .order_by('-count')
    )
    
    # 最近のアップロード
    recent_uploads = user_files.order_by('-created_at')[:5]
    
    # 人気ファイル（ダウンロード数順）- ログ履歴機能を一時的に無効化
    # popular_files = user_files.annotate(
    #     download_count=Count('access_logs', filter=Q(access_logs__action='download'))
    # ).order_by('-download_count')[:5]
    
    return {
        'total_files': total_files,
        'total_size': total_size,
        'total_size_display': _get_size_display(total_size),
        'files_by_category': files_by_category,
        'recent_uploads': recent_uploads,
        # 'popular_files': popular_files  # ログ履歴機能を一時的に無効化
    }


def _get_size_display(size_bytes):
    """ファイルサイズを人間が読みやすい形式で返す"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"