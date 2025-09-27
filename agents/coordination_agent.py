import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from uagents import Agent, Context, Protocol
from pydantic import BaseModel, Field

class AgentAddresses:
    PROPOSAL_ANALYSIS = "agent1qw037h6333hn42ze6qtqu50hcpnz6pderfk3p3dw7djq08tgjnvfs9eqncv"
    VOTER_SENTIMENT = "agent1qgn3epnffmzs5dfyya33lluan8m6uvln8wrl2heef7dhas3vz9k2v8kmdet"
    EXECUTION_AUTOMATION = "agent1qdh8ce35zesj89978n5phrjvydzwfnnneyha2rjw5c9ezt6vs86a5nwj0dw"

class ProposalSubmission(BaseModel):
    proposal_id: str = Field(..., description="Unique proposal ID")
    title: str = Field(..., description="Proposal title")
    description: str = Field(..., description="Full proposal description")
    requested_amount: float = Field(..., ge=0, description="Requested funding amount")
    token_type: str = Field(default="ETH", description="Token type")
    recipient_address: Optional[str] = Field(default=None, description="Recipient address")
    submitter: str = Field(..., description="Proposal submitter")
    category: str = Field(default="funding", description="Proposal category")

class WorkflowStatus(BaseModel):
    proposal_id: str
    current_stage: str = Field(..., description="Current workflow stage")
    analysis_complete: bool = Field(default=False)
    sentiment_analysis_complete: bool = Field(default=False)
    execution_plan_ready: bool = Field(default=False)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

class ComprehensiveAnalysis(BaseModel):
    proposal_id: str
    proposal_analysis: Optional[Dict] = Field(default=None, description="From Proposal Analysis Agent")
    sentiment_prediction: Optional[Dict] = Field(default=None, description="From Voter Sentiment Agent") 
    execution_plan: Optional[Dict] = Field(default=None, description="From Execution Agent")
    final_recommendation: str = Field(..., description="Overall recommendation")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    risk_assessment: str = Field(..., description="Overall risk level")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class UserQuery(BaseModel):
    query: str = Field(..., description="Natural language query about proposals")
    proposal_id: Optional[str] = Field(default=None, description="Specific proposal ID if relevant")
    user_id: str = Field(..., description="User making the query")

class QueryResponse(BaseModel):
    query: str
    response: str = Field(..., description="Natural language response")
    data_sources: List[str] = Field(default_factory=list, description="Sources used for response")
    confidence: float = Field(..., ge=0.0, le=1.0)

class StatusRequest(BaseModel):
    proposal_id: str = Field(..., description="Proposal ID to check")

class ProposalAnalysisRequest(BaseModel):
    proposal_id: str = Field(..., description="Unique proposal identifier")
    proposal_text: str = Field(..., description="Full proposal text")
    requested_amount: float = Field(..., ge=0, description="Requested funding amount")
    token_type: str = Field(default="ETH", description="Token type")
    recipient_address: Optional[str] = Field(default=None, description="Recipient address")
    submitter: str = Field(..., description="Proposal submitter")
    category: str = Field(default="funding", description="Proposal category")
    treasury_balance: float = Field(default=1000.0, description="Current treasury balance")

class ProposalAnalysisResponse(BaseModel):
    proposal_id: str
    compliance: bool = Field(..., description="Governance compliance status")
    violations: List[str] = Field(default_factory=list, description="Compliance violations")
    reasoning_trace: str = Field(..., description="Analysis reasoning")
    financial_impact: Dict = Field(..., description="Financial impact analysis")
    market_analysis: Dict = Field(..., description="Market context analysis")
    technical_assessment: Dict = Field(..., description="Technical feasibility")
    risk_assessment: Dict = Field(..., description="Risk evaluation")
    similar_proposals: List[Dict] = Field(default_factory=list, description="Similar historical proposals")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ProposalRequest(BaseModel):
    proposal_id: str = Field(..., description="Proposal to analyze")
    user_list: List[str] = Field(..., description="List of users to predict votes for")
    proposal_text: Optional[str] = Field(default="", description="Full proposal text")

class ProposalResponse(BaseModel):
    proposal_id: str
    prediction: str = Field(..., description="Overall prediction")
    confidence: float = Field(..., ge=0.0, le=1.0)
    vote_breakdown: Dict[str, int] = Field(..., description="Vote count breakdown")
    key_influencers: List[str] = Field(..., description="Most influential users")
    risk_factors: List[str] = Field(..., description="Identified risks")

class ApprovedProposal(BaseModel):
    proposal_id: str = Field(..., description="Unique proposal identifier")
    proposal_text: str = Field(..., description="Full proposal text")
    execution_instructions: str = Field(..., description="Specific execution steps")
    budget_amount: float = Field(..., ge=0, description="Approved budget amount")
    token_type: str = Field(default="ETH", description="Token for execution")
    recipient_address: Optional[str] = Field(default=None, description="Recipient wallet address")
    deadline: Optional[str] = Field(default=None, description="Execution deadline")

class ExecutionResponse(BaseModel):
    proposal_id: str
    success: bool
    message: str
    execution_status: Optional[Dict] = None
    safety_check: Optional[Dict] = None
    execution_plan: Optional[Dict] = None

class WorkflowOrchestrator:
    def __init__(self):
        self.workflows: Dict[str, WorkflowStatus] = {}
        self.analysis_results: Dict[str, ComprehensiveAnalysis] = {}
        self.pending_responses: Dict[str, Dict] = {}
        
    def start_workflow(self, proposal: ProposalSubmission) -> WorkflowStatus:
        status = WorkflowStatus(
            proposal_id=proposal.proposal_id,
            current_stage="proposal_analysis",
            progress_percentage=10.0
        )
        self.workflows[proposal.proposal_id] = status
        self.analysis_results[proposal.proposal_id] = ComprehensiveAnalysis(
            proposal_id=proposal.proposal_id,
            final_recommendation="Analysis in progress...",
            confidence_score=0.0,
            risk_assessment="Unknown"
        )
        self.pending_responses[proposal.proposal_id] = {
            "proposal_analysis": False,
            "sentiment_analysis": False,
            "execution_planning": False
        }
        return status
    
    def complete_analysis_stage(self, proposal_id: str, stage: str, success: bool, data: Dict):
        if proposal_id not in self.workflows:
            return
        workflow = self.workflows[proposal_id]
        if stage == "proposal_analysis":
            workflow.analysis_complete = success
            if success:
                workflow.progress_percentage = 40.0
                workflow.current_stage = "sentiment_analysis"
                self.analysis_results[proposal_id].proposal_analysis = data
                self.pending_responses[proposal_id]["proposal_analysis"] = True
        elif stage == "sentiment_analysis":
            workflow.sentiment_analysis_complete = success
            if success:
                workflow.progress_percentage = 70.0
                workflow.current_stage = "execution_planning"
                self.analysis_results[proposal_id].sentiment_prediction = data
                self.pending_responses[proposal_id]["sentiment_analysis"] = True
        elif stage == "execution_planning":
            workflow.execution_plan_ready = success
            if success:
                workflow.progress_percentage = 100.0
                workflow.current_stage = "completed"
                self.analysis_results[proposal_id].execution_plan = data
                self.pending_responses[proposal_id]["execution_planning"] = True
                self.generate_final_recommendation(proposal_id)
    
    def generate_final_recommendation(self, proposal_id: str):
        if proposal_id not in self.analysis_results:
            return
        analysis = self.analysis_results[proposal_id]
        confidence_scores = []
        risk_factors = []
        if analysis.proposal_analysis:
            if analysis.proposal_analysis.get("compliance", False):
                confidence_scores.append(0.8)
            else:
                confidence_scores.append(0.2)
                risk_factors.append("Compliance issues")
            financial_risk = analysis.proposal_analysis.get("risk_assessment", {}).get("overall_risk", "MEDIUM")
            if financial_risk == "HIGH":
                risk_factors.append("High financial risk")
        if analysis.sentiment_prediction:
            pred_confidence = analysis.sentiment_prediction.get("confidence", 0.0)
            confidence_scores.append(pred_confidence)
            prediction = analysis.sentiment_prediction.get("prediction", "Uncertain")
            if prediction == "Fail":
                risk_factors.append("Negative voter sentiment")
            sentiment_risks = analysis.sentiment_prediction.get("risk_factors", [])
            risk_factors.extend(sentiment_risks)
        if analysis.execution_plan:
            safety_check = analysis.execution_plan.get("safety_check", {})
            if not safety_check.get("is_safe", False):
                risk_factors.append("Execution safety concerns")
                confidence_scores.append(0.3)
            else:
                confidence_scores.append(0.7)
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        if overall_confidence > 0.7 and len(risk_factors) == 0:
            recommendation = "APPROVE - High confidence, low risk"
            risk_level = "LOW"
        elif overall_confidence > 0.5 and len(risk_factors) <= 1:
            recommendation = "APPROVE WITH CONDITIONS - Moderate confidence"
            risk_level = "MEDIUM" 
        elif overall_confidence > 0.3:
            recommendation = "DEFER - Requires additional review"
            risk_level = "MEDIUM"
        else:
            recommendation = "REJECT - Low confidence or high risk"
            risk_level = "HIGH"
        analysis.final_recommendation = recommendation
        analysis.confidence_score = overall_confidence
        analysis.risk_assessment = risk_level

orchestrator = WorkflowOrchestrator()

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)
from uuid import uuid4

agent = Agent()
coordinator_protocol = Protocol("DAOCoordinatorProtocol", version="1.0")
chat_protocol = Protocol(spec=chat_protocol_spec)

@coordinator_protocol.on_message(model=ProposalSubmission, replies={WorkflowStatus})
async def handle_proposal_submission(ctx: Context, sender: str, msg: ProposalSubmission):
    try:
        ctx.logger.info(f"Starting real agent workflow for proposal {msg.proposal_id}")
        status = orchestrator.start_workflow(msg)
        analysis_request = ProposalAnalysisRequest(
            proposal_id=msg.proposal_id,
            proposal_text=f"Title: {msg.title}\nDescription: {msg.description}",
            requested_amount=msg.requested_amount,
            token_type=msg.token_type,
            recipient_address=msg.recipient_address,
            submitter=msg.submitter,
            category=msg.category,
            treasury_balance=1000.0
        )
        await ctx.send(AgentAddresses.PROPOSAL_ANALYSIS, analysis_request)
        ctx.logger.info(f"Sent analysis request to {AgentAddresses.PROPOSAL_ANALYSIS}")
        await ctx.send(sender, status)
    except Exception as e:
        ctx.logger.error(f"Error starting workflow: {e}")
        error_status = WorkflowStatus(
            proposal_id=msg.proposal_id,
            current_stage="error",
            errors=[str(e)],
            progress_percentage=0.0
        )
        await ctx.send(sender, error_status)

@coordinator_protocol.on_message(model=ProposalAnalysisResponse)
async def handle_proposal_analysis_response(ctx: Context, sender: str, msg: ProposalAnalysisResponse):
    try:
        ctx.logger.info(f"Received proposal analysis for {msg.proposal_id}")
        analysis_data = {
            "compliance": msg.compliance,
            "violations": msg.violations,
            "reasoning_trace": msg.reasoning_trace,
            "financial_impact": msg.financial_impact,
            "risk_assessment": msg.risk_assessment,
            "confidence_score": msg.confidence_score
        }
        orchestrator.complete_analysis_stage(msg.proposal_id, "proposal_analysis", True, analysis_data)
        voter_request = ProposalRequest(
            proposal_id=msg.proposal_id,
            user_list=["alice", "bob", "charlie", "dave", "eve"],
            proposal_text=f"Analysis: {msg.reasoning_trace}"
        )
        await ctx.send(AgentAddresses.VOTER_SENTIMENT, voter_request)
        ctx.logger.info(f"Sent to voter sentiment agent: {AgentAddresses.VOTER_SENTIMENT}")
    except Exception as e:
        ctx.logger.error(f"Error processing proposal analysis response: {e}")
        if msg.proposal_id in orchestrator.workflows:
            orchestrator.workflows[msg.proposal_id].errors.append(str(e))

@coordinator_protocol.on_message(model=ProposalResponse)
async def handle_voter_sentiment_response(ctx: Context, sender: str, msg: ProposalResponse):
    try:
        ctx.logger.info(f"Received voter sentiment analysis for {msg.proposal_id}")
        sentiment_data = {
            "prediction": msg.prediction,
            "confidence": msg.confidence,
            "vote_breakdown": msg.vote_breakdown,
            "key_influencers": msg.key_influencers,
            "risk_factors": msg.risk_factors
        }
        orchestrator.complete_analysis_stage(msg.proposal_id, "sentiment_analysis", True, sentiment_data)
        if msg.proposal_id in orchestrator.analysis_results:
            proposal_analysis = orchestrator.analysis_results[msg.proposal_id].proposal_analysis
            execution_request = ApprovedProposal(
                proposal_id=msg.proposal_id,
                proposal_text="Approved proposal for execution planning",
                execution_instructions=f"Execute as planned with {msg.prediction} voter sentiment",
                budget_amount=proposal_analysis.get("financial_impact", {}).get("requested_amount", 0),
                token_type=proposal_analysis.get("financial_impact", {}).get("token_type", "ETH")
            )
            await ctx.send(AgentAddresses.EXECUTION_AUTOMATION, execution_request)
            ctx.logger.info(f"Sent to execution agent: {AgentAddresses.EXECUTION_AUTOMATION}")
    except Exception as e:
        ctx.logger.error(f"Error processing voter sentiment response: {e}")
        if msg.proposal_id in orchestrator.workflows:
            orchestrator.workflows[msg.proposal_id].errors.append(str(e))

@coordinator_protocol.on_message(model=ExecutionResponse)
async def handle_execution_response(ctx: Context, sender: str, msg: ExecutionResponse):
    try:
        ctx.logger.info(f"Received execution plan for {msg.proposal_id}")
        execution_data = {
            "success": msg.success,
            "message": msg.message,
            "execution_status": msg.execution_status,
            "safety_check": msg.safety_check,
            "execution_plan": msg.execution_plan
        }
        orchestrator.complete_analysis_stage(msg.proposal_id, "execution_planning", msg.success, execution_data)
        ctx.logger.info(f"Workflow completed for {msg.proposal_id}")
    except Exception as e:
        ctx.logger.error(f"Error processing execution response: {e}")
        if msg.proposal_id in orchestrator.workflows:
            orchestrator.workflows[msg.proposal_id].errors.append(str(e))

@coordinator_protocol.on_message(model=UserQuery, replies={QueryResponse})
async def handle_user_query(ctx: Context, sender: str, msg: UserQuery):
    try:
        ctx.logger.info(f"Processing query from {msg.user_id}: {msg.query}")
        query_lower = msg.query.lower()
        response_text = "Query processed successfully"
        data_sources = []
        confidence = 0.5
        if "status" in query_lower and msg.proposal_id:
            if msg.proposal_id in orchestrator.workflows:
                workflow = orchestrator.workflows[msg.proposal_id]
                response_text = f"Proposal {msg.proposal_id} is in '{workflow.current_stage}' stage. Progress: {workflow.progress_percentage:.1f}%"
                if workflow.analysis_complete:
                    response_text += " Analysis: Complete."
                if workflow.sentiment_analysis_complete:
                    response_text += " Sentiment: Complete."
                if workflow.execution_plan_ready:
                    response_text += " Execution plan: Ready."
                if workflow.errors:
                    response_text += f" Errors: {', '.join(workflow.errors)}"
                data_sources = ["workflow_tracker"]
                confidence = 0.9
            else:
                response_text = f"No workflow found for proposal {msg.proposal_id}"
                confidence = 0.8
        elif "recommendation" in query_lower and msg.proposal_id:
            if msg.proposal_id in orchestrator.analysis_results:
                analysis = orchestrator.analysis_results[msg.proposal_id]
                response_text = f"Recommendation for {msg.proposal_id}: {analysis.final_recommendation}"
                response_text += f" Confidence: {analysis.confidence_score:.2f}"
                response_text += f" Risk: {analysis.risk_assessment}"
                data_sources = ["comprehensive_analysis"]
                confidence = analysis.confidence_score
            else:
                response_text = f"Analysis not complete for proposal {msg.proposal_id}"
                confidence = 0.3
        elif "summary" in query_lower:
            total_proposals = len(orchestrator.workflows)
            completed_workflows = len([w for w in orchestrator.workflows.values() if w.progress_percentage == 100.0])
            in_progress = total_proposals - completed_workflows
            response_text = f"DAO Summary: {total_proposals} total proposals, {completed_workflows} completed, {in_progress} in progress"
            data_sources = ["workflow_tracker"]
            confidence = 0.9
        else:
            response_text = "I can help with: proposal status, recommendations, summary. Try asking 'What is the status of prop_123?'"
            confidence = 0.7
        response = QueryResponse(
            query=msg.query,
            response=response_text,
            data_sources=data_sources,
            confidence=confidence
        )
        await ctx.send(sender, response)
    except Exception as e:
        ctx.logger.error(f"Error processing query: {e}")
        error_response = QueryResponse(
            query=msg.query,
            response=f"Error processing query: {str(e)}",
            data_sources=[],
            confidence=0.0
        )
        await ctx.send(sender, error_response)

@coordinator_protocol.on_message(model=StatusRequest, replies={ComprehensiveAnalysis})
async def handle_status_request(ctx: Context, sender: str, msg: StatusRequest):
    try:
        if msg.proposal_id in orchestrator.analysis_results:
            analysis = orchestrator.analysis_results[msg.proposal_id]
            await ctx.send(sender, analysis)
            ctx.logger.info(f"Sent analysis for {msg.proposal_id}")
        else:
            empty_analysis = ComprehensiveAnalysis(
                proposal_id=msg.proposal_id,
                final_recommendation="Analysis not yet available",
                confidence_score=0.0,
                risk_assessment="Unknown"
            )
            await ctx.send(sender, empty_analysis)
    except Exception as e:
        ctx.logger.error(f"Error getting analysis: {e}")

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("DAO Governance Coordinator starting up...")
    ctx.logger.info(f"Agent address: {ctx.address}")
    ctx.logger.info(f"Proposal Agent: {AgentAddresses.PROPOSAL_ANALYSIS}")
    ctx.logger.info(f"Voter Agent: {AgentAddresses.VOTER_SENTIMENT}")
    ctx.logger.info(f"Execution Agent: {AgentAddresses.EXECUTION_AUTOMATION}")
    ctx.logger.info("Ready to coordinate real agent workflows")

@chat_protocol.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    message_text = "".join(item.text for item in msg.content if isinstance(item, TextContent))
    response_text = ""
    try:
        if message_text.startswith("submit:"):
            parts = message_text.replace("submit:", "").strip().split(" | ")
            if len(parts) >= 3:
                proposal = ProposalSubmission(
                    proposal_id=f"chat_{uuid4().hex[:8]}",
                    title=parts[0].strip(),
                    description=parts[1].strip(),
                    requested_amount=float(parts[2].strip()),
                    token_type=parts[3].strip() if len(parts) > 3 else "ETH",
                    submitter=parts[4].strip() if len(parts) > 4 else "chat_user",
                    category="chat_submission"
                )
                status = orchestrator.start_workflow(proposal)
                analysis_request = ProposalAnalysisRequest(
                    proposal_id=proposal.proposal_id,
                    proposal_text=f"Title: {proposal.title}\nDescription: {proposal.description}",
                    requested_amount=proposal.requested_amount,
                    token_type=proposal.token_type,
                    submitter=proposal.submitter,
                    category=proposal.category,
                    treasury_balance=1000.0
                )
                await ctx.send(AgentAddresses.PROPOSAL_ANALYSIS, analysis_request)
                response_text = f"✅ Proposal {proposal.proposal_id} submitted!\n"
                response_text += f"📊 Title: {proposal.title}\n"  
                response_text += f"💰 Amount: {proposal.requested_amount} {proposal.token_type}\n"
                response_text += f"⏳ Status: {status.current_stage}\n"
                response_text += f"📈 Progress: {status.progress_percentage}%\n\n"
                response_text += f"Ask 'status {proposal.proposal_id}' to check progress!"
            else:
                response_text = "❌ Invalid format. Use: submit: Title | Description | Amount | Token | Submitter"
        elif message_text.startswith("status"):
            parts = message_text.split()
            if len(parts) > 1:
                proposal_id = parts[1]
                if proposal_id in orchestrator.workflows:
                    workflow = orchestrator.workflows[proposal_id]
                    analysis = orchestrator.analysis_results.get(proposal_id)
                    response_text = f"📋 **Status for {proposal_id}**\n\n"
                    response_text += f"🎯 Stage: {workflow.current_stage}\n"
                    response_text += f"📊 Progress: {workflow.progress_percentage:.1f}%\n"
                    if workflow.analysis_complete:
                        response_text += "✅ Proposal Analysis: Complete\n"
                    if workflow.sentiment_analysis_complete:
                        response_text += "✅ Sentiment Analysis: Complete\n"  
                    if workflow.execution_plan_ready:
                        response_text += "✅ Execution Plan: Ready\n"
                    if workflow.errors:
                        response_text += f"❌ Errors: {'; '.join(workflow.errors)}\n"
                    if analysis and workflow.progress_percentage == 100.0:
                        response_text += f"\n🎯 **Final Recommendation:** {analysis.final_recommendation}\n"
                        response_text += f"🎲 Confidence: {analysis.confidence_score:.2f}\n"
                        response_text += f"⚠️ Risk: {analysis.risk_assessment}"
                else:
                    response_text = f"❌ Proposal {proposal_id} not found"
            else:
                response_text = "❌ Please specify proposal ID. Example: 'status prop_123'"
        elif "help" in message_text.lower():
            response_text = """🤖 **DAO Coordinator Chat Commands**

📝 **Submit Proposal:**
`submit: Title | Description | Amount | Token | Submitter`
Example: `submit: DeFi Integration | Fund 50 ETH for yield farming | 50.0 | ETH | alice`

📊 **Check Status:**
`status [proposal_id]`
Example: `status chat_abc123`

📈 **Get Summary:**
`summary`

❓ **Help:**
`help`

The coordinator will automatically process proposals through all three specialized agents:
1. 🔍 Proposal Analysis (with Pyth market data)
2. 🗳️ Voter Sentiment Prediction
3. ⚡ Execution Planning & Safety Checks"""
        elif "summary" in message_text.lower():
            total = len(orchestrator.workflows)
            completed = len([w for w in orchestrator.workflows.values() if w.progress_percentage == 100.0])
            in_progress = total - completed
            response_text = f"📊 **DAO Governance Summary**\n\n"
            response_text += f"📝 Total Proposals: {total}\n"
            response_text += f"✅ Completed: {completed}\n"
            response_text += f"⏳ In Progress: {in_progress}\n"
            if orchestrator.analysis_results:
                approved = len([a for a in orchestrator.analysis_results.values() if "APPROVE" in a.final_recommendation])
                rejected = len([a for a in orchestrator.analysis_results.values() if "REJECT" in a.final_recommendation])
                response_text += f"👍 Approved: {approved}\n"
                response_text += f"👎 Rejected: {rejected}"
        else:
            response_text = "🤖 I'm the DAO Governance Coordinator!\n\nType 'help' for commands or try:\n• submit: Your Proposal | Description | Amount | ETH | your_name\n• status [proposal_id]\n• summary"
    except Exception as e:
        response_text = f"❌ Error: {str(e)}\n\nType 'help' for valid commands."
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=response_text),
            EndSessionContent(type="end-session"),
        ]
    ))

@chat_protocol.on_message(ChatAcknowledgement)
async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass

agent.include(coordinator_protocol, publish_manifest=True)
agent.include(chat_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
