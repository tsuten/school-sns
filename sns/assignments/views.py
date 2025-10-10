from .models import Assignment
from ninja import Router
from .schemas import AssignmentSchema, CreateAssignmentSchema, UpdateAssignmentSchema
from typing import List
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404

router = Router(tags=['assignments'])

def serialize_assignment(assignment):
    """AssignmentモデルをAssignmentSchemaに変換する"""
    return {
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'due_date': assignment.due_date,
        'assigned_to_ids': [user.id for user in assignment.assigned_to.all()],
        'created_by_id': assignment.created_by.id,
        'created_at': assignment.created_at,
        'updated_at': assignment.updated_at,
    }

# 課題関連
@router.get('', response=List[AssignmentSchema])
def get_assignments(request):
    """課題一覧を取得"""
    assignments = Assignment.objects.all()
    return [serialize_assignment(assignment) for assignment in assignments]

@router.get('/my-assignments', response=List[AssignmentSchema], auth=JWTAuth())
def get_my_assignments(request):
    """ログインユーザーに割り当てられた課題を取得"""
    assignments = Assignment.objects.get_assignments_by_user(request.auth)
    return [serialize_assignment(assignment) for assignment in assignments]

@router.get('/created-by-me', response=List[AssignmentSchema], auth=JWTAuth())
def get_created_assignments(request):
    """ログインユーザーが作成した課題を取得"""
    assignments = Assignment.objects.get_assignments_by_creator(request.user)
    return [serialize_assignment(assignment) for assignment in assignments]

@router.get('/overdue', response=List[AssignmentSchema])
def get_overdue_assignments(request):
    """期限切れの課題を取得"""
    assignments = Assignment.objects.get_overdue_assignments()
    return [serialize_assignment(assignment) for assignment in assignments]

@router.get('/{assignment_id}', response=AssignmentSchema)
def get_assignment(request, assignment_id: str):
    """特定の課題を取得"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    return serialize_assignment(assignment)

@router.post('', response=AssignmentSchema, auth=JWTAuth())
def create_assignment(request, assignment: CreateAssignmentSchema):
    """課題を作成"""
    assignment_obj = Assignment.objects.create(
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        created_by=request.auth
    )
    
    if assignment.assigned_to_ids:
        assignment_obj.assigned_to.set(assignment.assigned_to_ids)
    
    assignment_obj.save()
    return serialize_assignment(assignment_obj)

@router.put('/{assignment_id}', response=AssignmentSchema, auth=JWTAuth())
def update_assignment(request, assignment_id: str, assignment: UpdateAssignmentSchema):
    """課題を更新"""
    assignment_obj = get_object_or_404(Assignment, id=assignment_id)
    
    # 作成者のみ更新可能
    if assignment_obj.created_by != request.auth:
        raise PermissionError("この課題を更新する権限がありません")
    
    for field, value in assignment.dict(exclude_unset=True).items():
        if field == 'assigned_to_ids' and value is not None:
            assignment_obj.assigned_to.set(value)
        else:
            setattr(assignment_obj, field, value)
    
    assignment_obj.save()
    return serialize_assignment(assignment_obj)

@router.delete('/{assignment_id}', auth=JWTAuth())
def delete_assignment(request, assignment_id: str):
    """課題を削除（論理削除）"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # 作成者のみ削除可能
    if assignment.created_by != request.auth:
        raise PermissionError("この課題を削除する権限がありません")
    
    assignment.delete()
    return {"success": True}
