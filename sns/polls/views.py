from django.shortcuts import render, get_object_or_404
from .models import Poll, Choice, Vote
from .schemas import PollSchema, CreatePollSchema, VoteSchema, ChoiceSchema
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import List

router = Router(tags=["polls"])

@router.post("/create", response=PollSchema, auth=JWTAuth())
def create_poll(request, poll_data: CreatePollSchema):
    """新しい投票を作成"""
    poll = Poll.objects.create_poll(poll_data.question, poll_data.choices)
    return PollSchema(
        id=poll.id,
        question=poll.question,
        choices=[
            ChoiceSchema(
                id=choice.id,
                choice_text=choice.choice_text,
                vote_count=choice.vote_count
            ) for choice in poll.poll_choices.all()
        ],
        created_at=poll.created_at,
        updated_at=poll.updated_at
    )

@router.get("/", response=List[PollSchema])
def get_polls(request):
    """すべての投票を取得"""
    polls = Poll.objects.all()
    return [
        PollSchema(
            id=poll.id,
            question=poll.question,
            choices=[
                ChoiceSchema(
                    id=choice.id,
                    choice_text=choice.choice_text,
                    vote_count=choice.vote_count
                ) for choice in poll.poll_choices.all()
            ],
            created_at=poll.created_at,
            updated_at=poll.updated_at
        ) for poll in polls
    ]

@router.get("/{poll_id}", response=PollSchema)
def get_poll(request, poll_id: str):
    """特定の投票を取得"""
    poll = get_object_or_404(Poll, id=poll_id)
    return PollSchema(
        id=poll.id,
        question=poll.question,
        choices=[
            ChoiceSchema(
                id=choice.id,
                choice_text=choice.choice_text,
                vote_count=choice.vote_count
            ) for choice in poll.poll_choices.all()
        ],
        created_at=poll.created_at,
        updated_at=poll.updated_at
    )

@router.post("/{poll_id}/vote", response=VoteSchema, auth=JWTAuth())
def vote(request, poll_id: str, choice_id: str):
    """投票する"""
    poll = get_object_or_404(Poll, id=poll_id)
    choice = get_object_or_404(Choice, id=choice_id, poll=poll)
    
    # 同じ投票内での既存の投票をチェック
    existing_vote = Vote.objects.filter(
        user=request.user, 
        choice__poll=poll
    ).first()
    
    if existing_vote:
        # 既存の投票を更新
        existing_vote.choice = choice
        existing_vote.save()
        vote_obj = existing_vote
    else:
        # 新しい投票を作成
        vote_obj = Vote.objects.create(user=request.user, choice=choice)
    
    return VoteSchema(
        id=vote_obj.id,
        choice_id=vote_obj.choice.id,
        user_id=vote_obj.user.id,
        created_at=vote_obj.created_at
    )

@router.post("/vote/{choice_id}", response=VoteSchema, auth=JWTAuth())
def vote_by_choice(request, choice_id: str):
    """選択肢IDで直接投票する（よりシンプルなAPI）"""
    choice = get_object_or_404(Choice, id=choice_id)
    poll = choice.poll
    
    # 同じ投票内での既存の投票をチェック
    existing_vote = Vote.objects.filter(
        user=request.user, 
        choice__poll=poll
    ).first()
    
    if existing_vote:
        # 既存の投票を更新
        existing_vote.choice = choice
        existing_vote.save()
        vote_obj = existing_vote
    else:
        # 新しい投票を作成
        vote_obj = Vote.objects.create(user=request.user, choice=choice)
    
    return VoteSchema(
        id=vote_obj.id,
        choice_id=vote_obj.choice.id,
        user_id=vote_obj.user.id,
        created_at=vote_obj.created_at
    )