from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..database import get_db
from ..agents.proposal_analyzer import ProposalAnalysisAgent
from ..agents.sentiment_predictor import VoterSentimentPredictionAgent
from ..agents.execution_automator import ExecutionAutomationAgent

router = APIRouter(
    prefix="/proposals",
    tags=["proposals"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.post("/", response_model=schemas.Proposal)
async def create_proposal(proposal: schemas.ProposalCreate, db: Session = Depends(get_db)):
    new_proposal = crud.create_proposal(db=db, proposal=proposal)
    await manager.broadcast(f"New Proposal Created: {new_proposal.title}")
    return new_proposal

@router.get("/", response_model=List[schemas.Proposal])
def read_proposals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    proposals = crud.get_proposals(db, skip=skip, limit=limit)
    return proposals

@router.get("/{proposal_id}", response_model=schemas.Proposal)
def read_proposal(proposal_id: int, db: Session = Depends(get_db)):
    db_proposal = crud.get_proposal(db, proposal_id=proposal_id)
    if db_proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return db_proposal

@router.post("/{proposal_id}/analyze", response_model=schemas.Proposal)
async def analyze_proposal(proposal_id: int, db: Session = Depends(get_db)):
    db_proposal = crud.get_proposal(db, proposal_id=proposal_id)
    if not db_proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Instantiate and run Agent 1
    analyzer = ProposalAnalysisAgent()
    analysis_report = analyzer.run_analysis(db_proposal.description, db_proposal.id)
    
    # Save results to the database
    updated_proposal = crud.save_agent_data(db, proposal_id, "analysis_report", analysis_report)
    crud.update_proposal_status(db, proposal_id, "analyzed")
    
    await manager.broadcast(f"Proposal {proposal_id} Analyzed: Risk score {analysis_report['risk_score']}")
    return updated_proposal

@router.post("/{proposal_id}/predict-sentiment", response_model=schemas.Proposal)
async def predict_sentiment(proposal_id: int, db: Session = Depends(get_db)):
    db_proposal = crud.get_proposal(db, proposal_id=proposal_id)
    if not db_proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Instantiate and run Agent 2
    predictor = VoterSentimentPredictionAgent()
    prediction_report = predictor.run_prediction(db_proposal.id, db_proposal.title)
    
    updated_proposal = crud.save_agent_data(db, proposal_id, "sentiment_prediction", prediction_report)
    
    await manager.broadcast(f"Sentiment for Proposal {proposal_id} Predicted: {prediction_report['predicted_outcome']}")
    return updated_proposal

@router.post("/{proposal_id}/execute", response_model=schemas.Proposal)
async def execute_proposal(proposal_id: int, db: Session = Depends(get_db)):
    db_proposal = crud.get_proposal(db, proposal_id=proposal_id)
    if not db_proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Simple check to ensure the proposal is in a state to be executed (e.g., 'passed')
    if db_proposal.status != "passed":
        raise HTTPException(status_code=400, detail="Proposal cannot be executed. It has not passed.")

    # Instantiate and run Agent 3
    executor = ExecutionAutomationAgent()
    execution_log = executor.run_execution(db_proposal.id, db_proposal.analysis_report)
    
    updated_proposal = crud.save_agent_data(db, proposal_id, "execution_log", execution_log)
    crud.update_proposal_status(db, proposal_id, "executed")

    await manager.broadcast(f"Proposal {proposal_id} Execution Status: {execution_log['status']}")
    return updated_proposal


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)