from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import enum

# Assuming 'database.py' contains your SessionLocal, engine, and Base
from database import SessionLocal, engine, Base
# Assuming 'models.py' contains all your SQLAlchemy ORM classes
import models
# Import Pydantic models for data validation and response shaping
import schema

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DAO Governance Swarm API",
    description="An API to manage DAO members, proposals, and votes.",
    version="1.0.0"
)

# --- Dependency ---
def get_db():
    """
    Dependency that provides a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

## DAO Members
@app.post("/members/", response_model=schemas.DAOMember, status_code=status.HTTP_201_CREATED)
def create_dao_member(member: schemas.DAOMemberCreate, db: Session = Depends(get_db)):
    """
    Create a new DAO member. Ensures wallet address is unique.
    """
    db_member = db.query(models.DAOMember).filter(models.DAOMember.wallet_address == member.wallet_address).first()
    if db_member:
        raise HTTPException(status_code=400, detail="A member with this wallet address already exists.")
    
    new_member = models.DAOMember(wallet_address=member.wallet_address)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@app.get("/members/", response_model=List[schemas.DAOMember])
def read_dao_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all DAO members with pagination.
    """
    members = db.query(models.DAOMember).offset(skip).limit(limit).all()
    return members

@app.get("/members/{member_id}", response_model=schemas.DAOMember)
def read_dao_member(member_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single DAO member by their ID.
    """
    db_member = db.query(models.DAOMember).filter(models.DAOMember.id == member_id).first()
    if db_member is None:
        raise HTTPException(status_code=404, detail="DAO Member not found.")
    return db_member


## Proposals
@app.post("/proposals/", response_model=schemas.Proposal, status_code=status.HTTP_201_CREATED)
def create_proposal(proposal: schemas.ProposalCreate, db: Session = Depends(get_db)):
    """
    Create a new governance proposal. The submitter must be a valid DAO member.
    """
    db_member = db.query(models.DAOMember).filter(models.DAOMember.id == proposal.submitted_by_member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Submitter (DAO Member) not found.")

    new_proposal = models.Proposal(
        title=proposal.title,
        description=proposal.description,
        submitted_by_member_id=proposal.submitted_by_member_id
    )
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)
    return new_proposal

@app.get("/proposals/", response_model=List[schemas.Proposal])
def read_proposals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all proposals with pagination.
    """
    proposals = db.query(models.Proposal).offset(skip).limit(limit).all()
    return proposals

@app.get("/proposals/{proposal_id}", response_model=schemas.Proposal)
def read_proposal(proposal_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single proposal by its ID.
    """
    db_proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if db_proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return db_proposal


## Votes
@app.post("/proposals/{proposal_id}/vote", response_model=schemas.Vote, status_code=status.HTTP_201_CREATED)
def cast_vote_on_proposal(proposal_id: int, vote: schemas.VoteCreate, db: Session = Depends(get_db)):
    """
    Cast a vote on a specific proposal. The voter must be a valid DAO member.
    """
    db_proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not db_proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    
    db_voter = db.query(models.DAOMember).filter(models.DAOMember.id == vote.voter_member_id).first()
    if not db_voter:
        raise HTTPException(status_code=404, detail="Voter (DAO Member) not found.")
        
    # Check if this member has already voted on this proposal
    existing_vote = db.query(models.Vote).filter(
        models.Vote.proposal_id == proposal_id,
        models.Vote.voter_member_id == vote.voter_member_id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="Member has already voted on this proposal.")

    new_vote = models.Vote(
        proposal_id=proposal_id,
        **vote.model_dump()
    )
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    return new_vote

@app.get("/proposals/{proposal_id}/votes", response_model=List[schemas.Vote])
def read_votes_for_proposal(proposal_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all votes cast for a specific proposal.
    """
    db_proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not db_proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return db_proposal.votes

@app.get("/")
def read_root():
    return {"message": "Welcome to the DAO Governance Swarm API!"}