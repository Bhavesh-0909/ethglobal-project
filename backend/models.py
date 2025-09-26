import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    Table,
    UniqueConstraint,
    Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base

class ProposalStatus(enum.Enum):
    submitted = "submitted"
    analyzing = "analyzing"
    analysis_failed = "analysis_failed"
    voting = "voting"
    approved = "approved"
    rejected = "rejected"
    executing = "executing"
    executed = "executed"
    execution_failed = "execution_failed"

class VoteChoice(enum.Enum):
    _for = "for"
    against = "against"
    abstain = "abstain"

class AgentName(enum.Enum):
    ProposalAnalysisAgent = "ProposalAnalysisAgent"
    VoterSentimentPredictionAgent = "VoterSentimentPredictionAgent"
    ExecutionAutomationAgent = "ExecutionAutomationAgent"

class StakeholderType(enum.Enum):
    CoreTeam = "CoreTeam"
    Investor = "Investor"
    CommunityMod = "CommunityMod"
    TokenHolder = "TokenHolder"
    Partner = "Partner"

proposal_stakeholders_table = Table(
    'proposal_stakeholders',
    Base.metadata,
    Column('proposal_id', Integer, ForeignKey('proposals.id'), primary_key=True),
    Column('stakeholder_id', Integer, ForeignKey('stakeholders.id'), primary_key=True),
    Column('role', String(100), nullable=False)
)

class DAOMember(Base):
    __tablename__ = 'dao_members'
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(42), unique=True, nullable=False, index=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(JSONB)
    proposals = relationship('Proposal', back_populates='submitter')
    votes = relationship('Vote', back_populates='voter')
    stakeholder_profile = relationship('Stakeholder', back_populates='member', uselist=False)

    def __repr__(self):
        return f"<DAOMember(id={self.id}, wallet='{self.wallet_address}')>"

class Stakeholder(Base):
    __tablename__ = 'stakeholders'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('dao_members.id'), unique=True, nullable=False)
    type = Column(Enum(StakeholderType, name="stakeholder_type"), nullable=False)
    details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    member = relationship('DAOMember', back_populates='stakeholder_profile')
    proposals = relationship('Proposal', secondary=proposal_stakeholders_table, back_populates='stakeholders')

    def __repr__(self):
        return f"<Stakeholder(id={self.id}, type='{self.type.name}')>"

class Proposal(Base):
    __tablename__ = 'proposals'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ProposalStatus, name="proposal_status"), nullable=False, default=ProposalStatus.submitted)
    submitted_by_member_id = Column(Integer, ForeignKey('dao_members.id'))
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    voting_starts_at = Column(DateTime(timezone=True))
    voting_ends_at = Column(DateTime(timezone=True))
    analysis_results = Column(JSONB)
    sentiment_prediction = Column(JSONB)
    execution_plan = Column(JSONB)
    submitter = relationship('DAOMember', back_populates='proposals')
    votes = relationship('Vote', back_populates='proposal', cascade="all, delete-orphan")
    execution_steps = relationship('ExecutionStep', back_populates='proposal', cascade="all, delete-orphan")
    stakeholders = relationship('Stakeholder', secondary=proposal_stakeholders_table, back_populates='proposals')

    def __repr__(self):
        return f"<Proposal(id={self.id}, title='{self.title[:30]}...')>"

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey('proposals.id'), nullable=False)
    voter_member_id = Column(Integer, ForeignKey('dao_members.id'), nullable=False)
    choice = Column(Enum(VoteChoice, name="vote_choice"), nullable=False)
    voting_power = Column(Numeric(78, 0), nullable=False)
    cast_at = Column(DateTime(timezone=True), server_default=func.now())
    proposal = relationship('Proposal', back_populates='votes')
    voter = relationship('DAOMember', back_populates='votes')
    __table_args__ = (UniqueConstraint('proposal_id', 'voter_member_id', name='_proposal_voter_uc'),)

    def __repr__(self):
        return f"<Vote(proposal_id={self.proposal_id}, voter_id={self.voter_member_id}, choice='{self.choice.name}')>"

class ExecutionStep(Base):
    __tablename__ = 'execution_steps'
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey('proposals.id'), nullable=False)
    step_order = Column(Integer, nullable=False)
    description = Column(Text)
    action_type = Column(String(100))
    parameters = Column(JSONB)
    status = Column(String(50), default='pending')
    transaction_hash = Column(String(66))
    metta_reasoning_trace = Column(Text)
    executed_at = Column(DateTime(timezone=True))
    proposal = relationship('Proposal', back_populates='execution_steps')

    def __repr__(self):
        return f"<ExecutionStep(id={self.id}, proposal_id={self.proposal_id}, order={self.step_order})>"

class CommunitySentiment(Base):
    __tablename__ = 'community_sentiments'
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    source_platform = Column(String(50))
    author_id = Column(String(255))
    content = Column(Text)
    sentiment_analysis = Column(JSONB)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<CommunitySentiment(id={self.id}, source='{self.source_platform}')>"

class AgentLog(Base):
    __tablename__ = 'agent_logs'
    id = Column(Integer, primary_key=True)
    agent = Column(Enum(AgentName, name="agent_name"), nullable=False)
    action = Column(String(255), nullable=False)
    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    details = Column(JSONB)
    status = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AgentLog(id={self.id}, agent='{self.agent.name}', action='{self.action}')>"
