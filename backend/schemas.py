from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ProposalBase(BaseModel):
    title: str
    description: str

class ProposalCreate(ProposalBase):
    pass

class Proposal(ProposalBase):
    id: int
    status: str
    created_at: datetime
    analysis_report: Optional[Dict[str, Any]] = None
    sentiment_prediction: Optional[Dict[str, Any]] = None
    execution_log: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True # Pydantic v2