from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Poll, Choice, Vote
from .schemas import PollSchema, CreatePollSchema, VoteSchema, ChoiceSchema, ErrorResponse
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import List, Union
from apps.core.organizations.utils import OrganizationManagerService
import uuid

router = Router(tags=["polls"])

@router.post("/create", response=PollSchema, auth=JWTAuth())
def create_poll(request, poll_data: CreatePollSchema):
    """新しい投票を作成"""
    poll = Poll.objects.create_poll(poll_data.question, poll_data.choices, request.user)
    return PollSchema(
        id=poll.id,
        question=poll.question,
        description=poll.description,
        choices=[
            ChoiceSchema(
                id=choice.id,
                choice_text=choice.choice_text,
                vote_count=choice.vote_count,
                is_voted_by_user=False  # 新規作成時は投票していない
            ) for choice in poll.poll_choices.all()
        ],
        organization_id=poll.organization.id,
        user_id=poll.user.id,
        username=poll.user.username,
        created_at=poll.created_at,
        updated_at=poll.updated_at
    )

@router.get("/", response=List[PollSchema], auth=JWTAuth())
def get_polls(request):
    """すべての投票を取得"""
    polls = Poll.objects.prefetch_related('poll_choices').all()
    
    # ユーザーがログインしている場合、投票履歴を取得
    user_votes = {}
    if request.user.is_authenticated:
        user_votes = {
            vote.choice.poll.id: vote.choice.id 
            for vote in Vote.objects.filter(user=request.user).select_related('choice__poll')
        }
    
    return [
        PollSchema(
            id=poll.id,
            question=poll.question,
            description=poll.description,
            choices=[
                ChoiceSchema(
                    id=choice.id,
                    choice_text=choice.choice_text,
                    vote_count=choice.vote_count,
                    is_voted_by_user=user_votes.get(poll.id) == choice.id
                ) for choice in poll.poll_choices.all()
            ],
            organization_id=poll.organization.id,
            user_id=poll.user.id,
            username=poll.user.username,
            created_at=poll.created_at,
            updated_at=poll.updated_at
        ) for poll in polls
    ]

@router.get("/{poll_id}", response=PollSchema, auth=JWTAuth())
def get_poll(request, poll_id: uuid.UUID):
    """特定の投票を取得"""
    poll = get_object_or_404(Poll.objects.prefetch_related('poll_choices'), id=poll_id)
    
    # ユーザーがログインしている場合、投票履歴を取得
    user_voted_choice_id = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(
            user=request.user, 
            choice__poll=poll
        ).select_related('choice').first()
        if user_vote:
            user_voted_choice_id = user_vote.choice.id
    
    return PollSchema(
        id=poll.id,
        question=poll.question,
        description=poll.description,
        choices=[
            ChoiceSchema(
                id=choice.id,
                choice_text=choice.choice_text,
                vote_count=choice.vote_count,
                is_voted_by_user=user_voted_choice_id == choice.id
            ) for choice in poll.poll_choices.all()
        ],
        organization_id=poll.organization.id,
        user_id=poll.user.id,
        username=poll.user.username,
        created_at=poll.created_at,
        updated_at=poll.updated_at
    )

@router.post("/choice/{choice_id}/vote", response=Union[VoteSchema, ErrorResponse], auth=JWTAuth())
def choice_vote(request, choice_id: str):
    """特定の選択肢に投票する"""
    choice = get_object_or_404(Choice, id=choice_id)
    
    try:
        # モデルのメソッドを使用して投票
        vote_obj = Vote.objects.vote_for_choice(request.user, choice)
        
        return VoteSchema(
            id=vote_obj.id,
            choice_id=vote_obj.choice.id,
            user_id=vote_obj.user.id,
            created_at=vote_obj.created_at,
            updated_at=vote_obj.updated_at
        )
    except (ValidationError, IntegrityError) as e:
        return ErrorResponse(error=str(e))

@router.delete("/{poll_id}/vote", response=dict, auth=JWTAuth())
def remove_vote(request, poll_id: str):
    """投票を取り消す"""
    poll = get_object_or_404(Poll, id=poll_id)
    Vote.objects.filter(user=request.user, choice__poll=poll).delete()
    return {"message": "投票が取り消されました"}