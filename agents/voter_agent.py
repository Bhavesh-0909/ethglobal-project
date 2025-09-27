import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from uagents import Agent, Context, Protocol
from pydantic import BaseModel, Field
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscussionComment(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    proposal_id: str = Field(..., description="Proposal being discussed")
    raw_comment: str = Field(..., description="The actual comment text")
    timestamp: Optional[str] = Field(default=None, description="When comment was made")
    platform: Optional[str] = Field(default="discord", description="Platform where comment was made")

class ProposalRequest(BaseModel):
    proposal_id: str = Field(..., description="Proposal to analyze")
    user_list: List[str] = Field(..., description="List of users to predict votes for")
    proposal_text: Optional[str] = Field(default="", description="Full proposal text")

class SentimentOutput(BaseModel):
    user_id: str
    proposal_id: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment from -1 to 1")
    influence_level: str = Field(..., description="User influence level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    timestamp: str

class VotePrediction(BaseModel):
    user_id: str
    proposal_id: str
    stance: str = Field(..., description="Predicted vote stance")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Explanation of prediction")

class ProposalResponse(BaseModel):
    proposal_id: str
    prediction: str = Field(..., description="Overall prediction")
    confidence: float = Field(..., ge=0.0, le=1.0)
    vote_breakdown: Dict[str, int] = Field(..., description="Vote count breakdown")
    key_influencers: List[str] = Field(..., description="Most influential users")
    risk_factors: List[str] = Field(..., description="Identified risks")

class CommentResponse(BaseModel):
    status: str = Field(..., description="Processing status")
    user_id: str
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    error: Optional[str] = Field(default=None, description="Error message if any")

class SentimentAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url='https://api.asi1.ai/v1',
            api_key='Enter your api key here', #https://asi1.ai/dashboard/api-keys
        )
    
    async def analyze_sentiment(self, comment: DiscussionComment) -> SentimentOutput:
        try:
            prompt = f"""
            Analyze the sentiment and influence level of this DAO proposal comment:
            
            Comment: "{comment.raw_comment}"
            User: {comment.user_id}
            Proposal: {comment.proposal_id}
            
            Return JSON with:
            - sentiment_score: float (-1 to 1, where -1 is very negative, 1 is very positive)
            - influence_level: string ("low", "medium", "high" based on comment quality and conviction)
            - confidence: float (0 to 1, confidence in the analysis)
            
            Consider:
            - Technical depth of arguments
            - Emotional tone
            - Constructiveness of criticism
            - Evidence provided
            """
            
            response = self.client.chat.completions.create(
                model="asi1-mini",
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert for DAO governance. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return SentimentOutput(
                user_id=comment.user_id,
                proposal_id=comment.proposal_id,
                sentiment_score=float(result.get("sentiment_score", 0.0)),
                influence_level=result.get("influence_level", "low"),
                confidence=float(result.get("confidence", 0.5)),
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentOutput(
                user_id=comment.user_id,
                proposal_id=comment.proposal_id,
                sentiment_score=0.0,
                influence_level="low",
                confidence=0.1,
                timestamp=datetime.utcnow().isoformat()
            )

class VoterKnowledgeGraph:
    def __init__(self):
        self.kg: Dict[str, Dict] = {
            "sentiments": {},      
            "votes": {},           
            "follows": {},        
            "predictions": {},     
            "user_influence": {},   
            "proposal_topics": {}, 
            "voting_patterns": {}  
        }
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        self.kg["votes"] = {
            ("alice", "prop_001"): "For",
            ("bob", "prop_001"): "Against",
            ("charlie", "prop_001"): "For",
            ("alice", "prop_002"): "For", 
            ("bob", "prop_002"): "For",
            ("dave", "prop_001"): "Neutral",
            ("eve", "prop_002"): "Against"
        }
        
        self.kg["follows"] = {
            "alice": ["bob", "charlie"],
            "bob": ["charlie", "dave"],
            "charlie": ["alice"],
            "dave": ["alice", "bob"],
            "eve": ["alice"]
        }
        
        self.kg["user_influence"] = {
            "alice": 0.8,
            "bob": 0.6,
            "charlie": 0.4,
            "dave": 0.3,
            "eve": 0.5
        }
    
    def assert_sentiment(self, sentiment: SentimentOutput):
        key = (sentiment.user_id, sentiment.proposal_id)
        self.kg["sentiments"][key] = sentiment
        logger.info(f"Stored sentiment for {sentiment.user_id} on {sentiment.proposal_id}")
    
    def get_user_influence(self, user_id: str) -> float:
        return self.kg["user_influence"].get(user_id, 0.2)
    
    def get_historical_votes(self, user_id: str) -> List[Tuple[str, str]]:
        return [(prop_id, vote) for (uid, prop_id), vote in self.kg["votes"].items() if uid == user_id]
    
    def get_social_connections(self, user_id: str) -> List[str]:
        return self.kg["follows"].get(user_id, [])

class VotingPredictor:
    def __init__(self, kg: VoterKnowledgeGraph, sentiment_analyzer: SentimentAnalyzer):
        self.kg = kg
        self.sentiment_analyzer = sentiment_analyzer
    
    def predict_user_vote(self, user_id: str, proposal_id: str) -> VotePrediction:
        sentiment_key = (user_id, proposal_id)
        sentiment_data = self.kg.kg["sentiments"].get(sentiment_key)
        sentiment_score = sentiment_data.sentiment_score if sentiment_data else 0.0
        
        user_influence = self.kg.get_user_influence(user_id)
        
        connections = self.kg.get_social_connections(user_id)
        social_influence_score = 0.0
        social_votes = []
        
        for connection in connections:
            connection_vote = self.kg.kg["votes"].get((connection, proposal_id))
            if connection_vote:
                connection_influence = self.kg.get_user_influence(connection)
                vote_weight = 1 if connection_vote == "For" else -1 if connection_vote == "Against" else 0
                social_influence_score += vote_weight * connection_influence * 0.3
                social_votes.append(connection_vote)
        
        total_score = sentiment_score * 0.6 + social_influence_score * 0.4
        
        if total_score > 0.2:
            stance = "For"
        elif total_score < -0.2:
            stance = "Against"
        else:
            stance = "Neutral"
        
        confidence = min(abs(total_score) + user_influence * 0.2, 1.0)
        
        reasoning_parts = []
        if sentiment_data:
            reasoning_parts.append(f"Sentiment: {sentiment_score:.2f}")
        if social_votes:
            for_count = len([v for v in social_votes if v == 'For'])
            against_count = len([v for v in social_votes if v == 'Against'])
            reasoning_parts.append(f"Social network: {for_count} For, {against_count} Against")
        reasoning_parts.append(f"User influence: {user_influence:.2f}")
        
        return VotePrediction(
            user_id=user_id,
            proposal_id=proposal_id,
            stance=stance,
            confidence=confidence,
            reasoning="; ".join(reasoning_parts) if reasoning_parts else "No data available"
        )
    
    def calculate_voting_outcome(self, proposal_id: str, user_list: List[str]) -> ProposalResponse:
        predictions = []
        
        for user_id in user_list:
            prediction = self.predict_user_vote(user_id, proposal_id)
            self.kg.kg["predictions"][(user_id, proposal_id)] = prediction
            predictions.append(prediction)
        
        weighted_score = 0.0
        vote_counts = {"For": 0, "Against": 0, "Neutral": 0}
        
        for pred in predictions:
            user_influence = self.kg.get_user_influence(pred.user_id)
            vote_weight = pred.confidence * user_influence
            
            if pred.stance == "For":
                weighted_score += vote_weight
                vote_counts["For"] += 1
            elif pred.stance == "Against":
                weighted_score -= vote_weight
                vote_counts["Against"] += 1
            else:
                vote_counts["Neutral"] += 1
        
        total_voting_power = sum(self.kg.get_user_influence(uid) for uid in user_list)
        confidence_threshold = total_voting_power * 0.1
        
        if weighted_score > confidence_threshold:
            outcome = "Pass"
        elif weighted_score < -confidence_threshold:
            outcome = "Fail"
        else:
            outcome = "Uncertain"
        
        key_influencers = sorted(
            user_list, 
            key=lambda u: self.kg.get_user_influence(u), 
            reverse=True
        )[:3]
        
        risk_factors = []
        if vote_counts["Neutral"] > len(user_list) * 0.3:
            risk_factors.append("High voter apathy")
        if abs(vote_counts["For"] - vote_counts["Against"]) <= 2:
            risk_factors.append("Very close margin")
        if len(user_list) < 5:
            risk_factors.append("Small sample size")
        
        overall_confidence = min(abs(weighted_score) / max(total_voting_power, 1), 1.0)
        
        return ProposalResponse(
            proposal_id=proposal_id,
            prediction=outcome,
            confidence=overall_confidence,
            vote_breakdown=vote_counts,
            key_influencers=key_influencers,
            risk_factors=risk_factors
        )

API_KEY = "sk_42c1b4efbd0a4e299e25898bdb151d29aebba1181f964cf19f225f6446f5cd60"

sentiment_analyzer = SentimentAnalyzer(API_KEY)
knowledge_graph = VoterKnowledgeGraph()
predictor = VotingPredictor(knowledge_graph, sentiment_analyzer)

agent = Agent()

voter_protocol = Protocol("VoterSentimentProtocol", version="1.0")

@voter_protocol.on_message(model=DiscussionComment, replies={CommentResponse})
async def handle_discussion_comment(ctx: Context, sender: str, msg: DiscussionComment):
    try:
        ctx.logger.info(f"Processing comment from {msg.user_id} on proposal {msg.proposal_id}")
        sentiment = await sentiment_analyzer.analyze_sentiment(msg)
        knowledge_graph.assert_sentiment(sentiment)
        response = CommentResponse(
            status="processed",
            user_id=msg.user_id,
            sentiment_score=sentiment.sentiment_score
        )
        await ctx.send(sender, response)
        ctx.logger.info(f"Successfully processed comment with sentiment score: {sentiment.sentiment_score}")
    except Exception as e:
        ctx.logger.error(f"Error processing comment: {e}")
        error_response = CommentResponse(
            status="error",
            user_id=msg.user_id,
            error=str(e)
        )
        await ctx.send(sender, error_response)

@voter_protocol.on_message(model=ProposalRequest, replies={ProposalResponse})
async def handle_proposal_request(ctx: Context, sender: str, msg: ProposalRequest):
    try:
        ctx.logger.info(f"Processing proposal prediction for {msg.proposal_id} with {len(msg.user_list)} users")
        result = predictor.calculate_voting_outcome(msg.proposal_id, msg.user_list)
        ctx.logger.info(f"Prediction: {result.prediction} (confidence: {result.confidence:.2f})")
        ctx.logger.info(f"Vote breakdown: {result.vote_breakdown}")
        await ctx.send(sender, result)
    except Exception as e:
        ctx.logger.error(f"Error processing proposal request: {e}")
        error_response = ProposalResponse(
            proposal_id=msg.proposal_id,
            prediction="Error",
            confidence=0.0,
            vote_breakdown={"For": 0, "Against": 0, "Neutral": 0},
            key_influencers=[],
            risk_factors=[f"Processing error: {str(e)}"]
        )
        await ctx.send(sender, error_response)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Voter Sentiment Agent starting up...")
    ctx.logger.info(f"Agent address: {ctx.address}")
    ctx.logger.info("Knowledge graph initialized with sample data")
    ctx.logger.info(f"Sample users: {list(knowledge_graph.kg['user_influence'].keys())}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("Voter Sentiment Agent shutting down...")

agent.include(voter_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
