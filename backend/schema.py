# schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import enum

# --- ENUMs for API Schemas ---
# These ensure that clients can only send valid choices.

class VoteChoice(str, enum.Enum):
    _for = "for"
    against = "against"
    abstain = "abstain"

class ProposalStatus(str, enum.Enum):
    submitted = "submitted"
    analyzing = "analyzing"
    voting = "voting"
    approved = "approved"
    rejected = "rejected"
    executing = "executing"
    executed = "executed"

# --- Base Models ---

class VoteBase(BaseModel):
    choice: VoteChoice
    voting_power: int
    voter_member_id: int

class VoteCreate(VoteBase):
    pass

class Vote(VoteBase):
    id: int
    proposal_id: int
    cast_at: datetime

    class Config:
        from_attributes = True

class ProposalBase(BaseModel):
    title: str
    description: str

class ProposalCreate(ProposalBase):
    submitted_by_member_id: int

class Proposal(ProposalBase):
    id: int
    status: ProposalStatus
    submitted_by_member_id: int
    submitted_at: datetime
    votes: List[Vote] = []

    class Config:
        from_attributes = True
        
class DAOMemberBase(BaseModel):
    wallet_address: str

class DAOMemberCreate(DAOMemberBase):
    pass

class DAOMember(DAOMemberBase):
    id: int
    first_seen: datetime
    # You can choose to include proposals submitted by the member
    # proposals: List[Proposal] = [] 

    class Config:
        from_attributes = True