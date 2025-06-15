from ninja import Schema
from typing import List
import uuid
from datetime import datetime

# need to refactor later, naming rule not regularized

class ChoiceSchema(Schema):
    id: uuid.UUID
    choice_text: str
    vote_count: int

class CreateChoiceSchema(Schema):
    choice_text: str

class PollSchema(Schema):
    id: uuid.UUID
    question: str
    choices: List[ChoiceSchema]
    created_at: datetime
    updated_at: datetime

class CreatePollSchema(Schema):
    question: str
    choices: List[str]  # 選択肢のテキストのリスト

class VoteSchema(Schema):
    id: uuid.UUID
    choice_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime