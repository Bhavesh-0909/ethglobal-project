from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="pending")  # e.g., pending, analyzed, voting, passed, failed, executed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # JSON columns to store agent-generated data
    analysis_report = Column(JSON) # To store Agent 1's report [cite: 28]
    sentiment_prediction = Column(JSON) # To store Agent 2's prediction [cite: 72]
    execution_log = Column(JSON) # To store Agent 3's execution trace [cite: 107]