from sqlalchemy.orm import Session
from . import models, schemas

def get_proposal(db: Session, proposal_id: int):
    return db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()

def get_proposals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Proposal).offset(skip).limit(limit).all()

def create_proposal(db: Session, proposal: schemas.ProposalCreate):
    db_proposal = models.Proposal(title=proposal.title, description=proposal.description)
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

def update_proposal_status(db: Session, proposal_id: int, status: str):
    db_proposal = get_proposal(db, proposal_id)
    if db_proposal:
        db_proposal.status = status
        db.commit()
        db.refresh(db_proposal)
    return db_proposal

def save_agent_data(db: Session, proposal_id: int, report_type: str, data: dict):
    """Saves data from an agent (analysis, sentiment, etc.) to the proposal."""
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        return None
    
    setattr(db_proposal, report_type, data)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal