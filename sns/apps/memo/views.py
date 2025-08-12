from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from typing import List
from .models import Memo
from .schemas import (
    MemoCreateSchema, MemoUpdateSchema, MemoResponseSchema,
    MemoListResponseSchema, MemoDetailResponseSchema,
    MemoCreateResponseSchema, MemoUpdateResponseSchema,
    MemoDeleteResponseSchema
)
from shared.base_schemas import BaseResponseSchema

# Django Ninja Router インスタンス
router = Router(tags=['memo'])

@router.get("/", response=List[MemoResponseSchema], auth=JWTAuth())
def get_memo_list(request):
    """ユーザーのメモ一覧を取得"""
    try:
        memos = Memo.objects.filter(user=request.user, is_deleted=False)
        return memos
    except Exception as e:
        raise HttpError(500, f"メモ一覧の取得に失敗しました: {str(e)}")

@router.get("/{memo_id}", response=MemoResponseSchema, auth=JWTAuth())
def get_memo_detail(request, memo_id: str):
    """特定のメモの詳細を取得"""
    try:
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        return memo
    except Exception as e:
        raise HttpError(500, f"メモ詳細の取得に失敗しました: {str(e)}")

@router.post("/", response=MemoCreateResponseSchema, auth=JWTAuth())
def create_memo(request, payload: MemoCreateSchema):
    """新しいメモを作成"""
    try:
        memo = Memo.objects.create(
            user=request.user,
            title=payload.title,
            content=payload.content
        )
        
        return {
            'status': 'success',
            'timestamp': timezone.now(),
            'data': {
                'id': memo.id,
                'title': memo.title,
                'content': memo.content,
                'created_at': memo.created_at,
                'updated_at': memo.updated_at
            }
        }
    except Exception as e:
        raise HttpError(500, f"メモの作成に失敗しました: {str(e)}")

@router.put("/{memo_id}", response=MemoUpdateResponseSchema, auth=JWTAuth())
def update_memo(request, memo_id: str, payload: MemoUpdateSchema):
    """メモを更新"""
    try:
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        
        if payload.title is not None:
            memo.title = payload.title
        if payload.content is not None:
            memo.content = payload.content
        
        memo.save()
        
        return {
            'status': 'success',
            'timestamp': timezone.now(),
            'data': {
                'id': memo.id,
                'title': memo.title,
                'content': memo.content,
                'created_at': memo.created_at,
                'updated_at': memo.updated_at
            }
        }
    except Exception as e:
        raise HttpError(500, f"メモの更新に失敗しました: {str(e)}")

@router.delete("/{memo_id}", response=MemoDeleteResponseSchema, auth=JWTAuth())
def delete_memo(request, memo_id: str):
    """メモを削除（論理削除）"""
    try:
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        memo.delete_object()  # 論理削除
        
        return {
            'status': 'success',
            'timestamp': timezone.now(),
            'message': 'メモが正常に削除されました'
        }
    except Exception as e:
        raise HttpError(500, f"メモの削除に失敗しました: {str(e)}")

@router.get("/search/{query}", response=List[MemoResponseSchema], auth=JWTAuth())
def search_memos(request, query: str):
    """メモを検索"""
    try:
        memos = Memo.objects.search(query, request.user)
        return memos
    except Exception as e:
        raise HttpError(500, f"メモ検索に失敗しました: {str(e)}")

@router.get("/recent", response=List[MemoResponseSchema], auth=JWTAuth())
def get_recent_memos(request, limit: int = 5):
    """最近のメモを取得"""
    try:
        if limit > 20:  # 最大20件まで
            limit = 20
        
        memos = Memo.objects.get_recent_memos(request.user, limit)
        return memos
    except Exception as e:
        raise HttpError(500, f"最近のメモ取得に失敗しました: {str(e)}")

@router.post("/{memo_id}/duplicate", response=MemoCreateResponseSchema, auth=JWTAuth())
def duplicate_memo(request, memo_id: str, payload: MemoCreateSchema = None):
    """メモを複製"""
    try:
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        
        new_title = None
        if payload and payload.title:
            new_title = payload.title
        
        new_memo = memo.duplicate(new_title)
        
        return {
            'status': 'success',
            'timestamp': timezone.now(),
            'data': {
                'id': new_memo.id,
                'title': new_memo.title,
                'content': new_memo.content,
                'created_at': new_memo.created_at,
                'updated_at': new_memo.updated_at
            }
        }
    except Exception as e:
        raise HttpError(500, f"メモの複製に失敗しました: {str(e)}")

@router.post("/{memo_id}/archive", auth=JWTAuth())
def archive_memo(request, memo_id: str):
    """メモをアーカイブ"""
    try:
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        memo.archive()
        
        return {
            'status': 'success',
            'timestamp': timezone.now(),
            'message': 'メモがアーカイブされました'
        }
    except Exception as e:
        raise HttpError(500, f"メモのアーカイブに失敗しました: {str(e)}")

@router.post("/{memo_id}/unarchive", auth=JWTAuth())
def unarchive_memo(request, memo_id: str):
    """メモをアーカイブから復元"""
    try:
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        memo.unarchive()
        
        return {
            'status': 'success',
            'timestamp': timezone.now(),
            'message': 'メモがアーカイブから復元されました'
        }
    except Exception as e:
        raise HttpError(500, f"メモの復元に失敗しました: {str(e)}")

# 従来のDjangoビュー（必要に応じて）
@login_required
def memo_list_view(request):
    """メモ一覧ページ"""
    memos = Memo.objects.filter(user=request.user, is_deleted=False)
    return render(request, 'memo/memo_list.html', {'memos': memos})

@login_required
def memo_detail_view(request, memo_id):
    """メモ詳細ページ"""
    memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
    return render(request, 'memo/memo_detail.html', {'memo': memo})

@login_required
def memo_create_view(request):
    """メモ作成ページ"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Memo.objects.create(user=request.user, title=title, content=content)
            return redirect('memo:memo_list')
    
    return render(request, 'memo/memo_form.html')

@login_required
def memo_update_view(request, memo_id):
    """メモ更新ページ"""
    memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            memo.title = title
            memo.content = content
            memo.save()
            return redirect('memo:memo_detail', memo_id=memo.id)
    
    return render(request, 'memo/memo_form.html', {'memo': memo})

@login_required
def memo_delete_view(request, memo_id):
    """メモ削除処理"""
    if request.method == 'POST':
        memo = get_object_or_404(Memo, id=memo_id, user=request.user, is_deleted=False)
        memo.delete_object()
        return redirect('memo:memo_list')
    
    return redirect('memo:memo_list')