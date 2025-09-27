from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Optional
import json
import aiohttp
import asyncio
from openai import OpenAI
from uagents import Context, Protocol, Agent
from pydantic import BaseModel, Field
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key='Enter your api key here', #https://asi1.ai/dashboard/api-keys
)

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

class PythDataFetcher:
    PRICE_FEEDS = {
        'ETH/USD': '0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace',
        'BTC/USD': '0xe62df6c8b4c85fe1d94a3b9a2bfa2f2d84e5a7a8a6f9d8e1c3b2f4a5e3d2c1b0',
        'SOL/USD': '0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed5c810b9ed72e59516c35b8d',
        'USDC/USD': '0xeaa020adb5b0b6e61df6a2c3b8e9e2e9e1b5c2e2e0f2d3c4b5a6e7d8c9b0a1f0',
    }
    BASE_URL = 'https://hermes.pyth.network'
    async def get_latest_prices(self, symbols: List[str]) -> Dict:
        try:
            feed_ids = []
            for symbol in symbols:
                if symbol in self.PRICE_FEEDS:
                    feed_ids.append(self.PRICE_FEEDS[symbol])
            if not feed_ids:
                return {"error": "No valid symbols provided"}
            feed_ids_str = ','.join(feed_ids)
            url = f"{self.BASE_URL}/api/latest_price_feeds?ids={feed_ids_str}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_price_data(data, symbols)
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    def _parse_price_data(self, raw_data: dict, symbols: List[str]) -> Dict:
        parsed_data = {}
        if 'parsed' in raw_data:
            for i, price_feed in enumerate(raw_data['parsed']):
                if i < len(symbols):
                    symbol = symbols[i]
                    price_data = price_feed.get('price', {})
                    parsed_data[symbol] = {
                        'price': float(price_data.get('price', 0)) / (10 ** abs(price_data.get('expo', 0))),
                        'confidence': float(price_data.get('conf', 0)) / (10 ** abs(price_data.get('expo', 0))),
                        'timestamp': price_data.get('publish_time', 0),
                        'status': price_feed.get('status', 'unknown')
                    }
        return parsed_data

class ProposalAnalyzer:
    def __init__(self):
        self.pyth_fetcher = PythDataFetcher()
    async def analyze_financial_impact(self, proposal_data: dict, treasury_balance: float) -> dict:
        try:
            requested_amount = proposal_data.get('requested_amount', 0)
            token_type = proposal_data.get('token_type', 'ETH')
            fallback_prices = {
                'ETH': 2400.0,
                'BTC': 43000.0, 
                'SOL': 95.0,
                'USDC': 1.0
            }
            current_price = 0
            confidence = 0.5
            data_source = "fallback"
            try:
                market_data = await self.pyth_fetcher.get_latest_prices([f'{token_type}/USD'])
                if 'error' not in market_data and f'{token_type}/USD' in market_data:
                    price_info = market_data[f'{token_type}/USD']
                    if price_info.get('price', 0) > 0:
                        current_price = price_info['price']
                        confidence = price_info.get('confidence', 0.5)
                        data_source = "pyth_live"
            except:
                pass
            if current_price == 0:
                current_price = fallback_prices.get(token_type, 1000.0)
                data_source = "fallback_estimate"
            usd_value = requested_amount * current_price
            treasury_impact_percentage = (requested_amount / treasury_balance) * 100 if treasury_balance > 0 else 0
            return {
                "requested_amount": requested_amount,
                "token_type": token_type,
                "current_price_usd": round(current_price, 2),
                "price_confidence": round(confidence, 4),
                "total_usd_value": round(usd_value, 2),
                "treasury_impact_percentage": round(treasury_impact_percentage, 2),
                "risk_level": self._assess_financial_risk(treasury_impact_percentage, confidence),
                "data_source": data_source
            }
        except Exception as e:
            requested_amount = proposal_data.get('requested_amount', 0)
            token_type = proposal_data.get('token_type', 'ETH')
            estimated_price = 2400.0 if token_type == 'ETH' else 1000.0
            return {
                "requested_amount": requested_amount,
                "token_type": token_type,
                "current_price_usd": estimated_price,
                "total_usd_value": round(requested_amount * estimated_price, 2),
                "treasury_impact_percentage": round((requested_amount / treasury_balance) * 100, 2),
                "risk_level": "HIGH",
                "data_source": "error_fallback",
                "error": str(e)
            }
    def _assess_financial_risk(self, treasury_impact: float, price_confidence: float) -> str:
        if treasury_impact > 20 or price_confidence < 0.01:
            return "HIGH"
        elif treasury_impact > 10 or price_confidence < 0.05:
            return "MEDIUM"
        else:
            return "LOW"
    async def generate_market_context(self, proposal_text: str) -> dict:
        try:
            fallback_market = {
                'ETH/USD': {'price': 2400.0, 'confidence': 0.5, 'status': 'fallback'},
                'BTC/USD': {'price': 43000.0, 'confidence': 0.5, 'status': 'fallback'},
                'SOL/USD': {'price': 95.0, 'confidence': 0.5, 'status': 'fallback'}
            }
            market_data = fallback_market
            data_source = "fallback_prices"
            try:
                major_tokens = ['ETH/USD', 'BTC/USD', 'SOL/USD']
                live_data = await self.pyth_fetcher.get_latest_prices(major_tokens)
                if 'error' not in live_data and len(live_data) > 0:
                    market_data = live_data
                    data_source = "pyth_live"
            except:
                pass
            return {
                "market_snapshot": market_data,
                "timestamp": datetime.utcnow().isoformat(),
                "market_sentiment": self._derive_market_sentiment(market_data),
                "data_source": data_source
            }
        except Exception as e:
            return {
                "market_snapshot": {'ETH/USD': {'price': 2400.0, 'status': 'error_fallback'}},
                "timestamp": datetime.utcnow().isoformat(),
                "market_sentiment": "UNKNOWN",
                "data_source": "error_fallback",
                "error": str(e)
            }
    def _derive_market_sentiment(self, market_data: dict) -> str:
        avg_confidence = sum(
            data.get('confidence', 0) for data in market_data.values() 
            if isinstance(data, dict)
        ) / len(market_data) if market_data else 0
        if avg_confidence > 0.1:
            return "STABLE"
        elif avg_confidence > 0.05:
            return "VOLATILE"
        else:
            return "HIGHLY_VOLATILE"
    async def perform_comprehensive_analysis(self, request: ProposalAnalysisRequest) -> ProposalAnalysisResponse:
        try:
            proposal_data = {
                "requested_amount": request.requested_amount,
                "token_type": request.token_type,
                "category": request.category,
                "recipient_address": request.recipient_address
            }
            financial_analysis = await self.analyze_financial_impact(proposal_data, request.treasury_balance)
            market_context = await self.generate_market_context(request.proposal_text)
            system_prompt = f"""
            You are a DAO Proposal Analysis Expert with access to real-time market data.
            
            Analyze this proposal and return ONLY a JSON object:
            {{
                "compliance": boolean,
                "violations": [list of compliance issues],
                "reasoning_trace": "detailed analysis reasoning",
                "technical_assessment": {{
                    "feasibility": "HIGH|MEDIUM|LOW",
                    "complexity": "HIGH|MEDIUM|LOW",
                    "timeline_realistic": boolean
                }},
                "risk_factors": [list of identified risks],
                "recommendations": [list of actionable recommendations],
                "confidence_score": 0.0-1.0
            }}
            
            Market Data: {json.dumps(market_context)}
            Financial Analysis: {json.dumps(financial_analysis)}
            
            Consider: governance compliance, technical feasibility, market timing, financial impact.
            """
            response = client.chat.completions.create(
                model="asi1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Proposal: {request.proposal_text}"}
                ],
                max_tokens=1536,
                temperature=0.1
            )
            asi_analysis = json.loads(response.choices[0].message.content)
            return ProposalAnalysisResponse(
                proposal_id=request.proposal_id,
                compliance=asi_analysis.get("compliance", False),
                violations=asi_analysis.get("violations", []),
                reasoning_trace=asi_analysis.get("reasoning_trace", "Analysis completed"),
                financial_impact=financial_analysis,
                market_analysis=market_context,
                technical_assessment=asi_analysis.get("technical_assessment", {}),
                risk_assessment={
                    "overall_risk": financial_analysis.get("risk_level", "MEDIUM"),
                    "risk_factors": asi_analysis.get("risk_factors", [])
                },
                similar_proposals=[],
                recommendations=asi_analysis.get("recommendations", []),
                confidence_score=asi_analysis.get("confidence_score", 0.7)
            )
        except Exception as e:
            return ProposalAnalysisResponse(
                proposal_id=request.proposal_id,
                compliance=False,
                violations=[f"Analysis error: {str(e)}"],
                reasoning_trace=f"Analysis failed: {str(e)}",
                financial_impact={"error": str(e)},
                market_analysis={"error": str(e)},
                technical_assessment={"feasibility": "UNKNOWN"},
                risk_assessment={"overall_risk": "HIGH", "risk_factors": ["Analysis failure"]},
                recommendations=["Retry analysis with manual review"],
                confidence_score=0.1
            )

agent = Agent()
chat_protocol = Protocol(spec=chat_protocol_spec)
swarm_protocol = Protocol("ProposalAnalysisProtocol", version="1.0")
analyzer = ProposalAnalyzer()

@chat_protocol.on_message(ChatMessage)
async def handle_chat_proposal(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id))
    message_text = "".join(item.text for item in msg.content if isinstance(item, TextContent))
    try:
        request = ProposalAnalysisRequest(
            proposal_id=f"chat_{uuid4().hex[:8]}",
            proposal_text=message_text,
            requested_amount=100,
            token_type="ETH",
            submitter="chat_user",
            category="funding"
        )
        analysis = await analyzer.perform_comprehensive_analysis(request)
        parts = []
        parts.append("Proposal Analysis Complete:")
        parts.append("")
        compliance_text = "PASS" if analysis.compliance else "FAIL"
        parts.append(f"Compliance: {compliance_text}")
        financial = analysis.financial_impact
        if not financial.get('error'):
            usd_val = financial.get('total_usd_value', 0)
            price = financial.get('current_price_usd', 0)
            impact = financial.get('treasury_impact_percentage', 0)
            token = financial.get('token_type', 'ETH')
            amount = financial.get('requested_amount', 0)
            parts.append(f"Financial Impact: ${usd_val:,.2f} USD")
            parts.append(f"Amount: {amount} {token} at ${price:,.2f}")
            parts.append(f"Treasury Impact: {impact:.1f}%")
        else:
            parts.append("Financial Impact: Analysis failed")
        risk = analysis.risk_assessment.get('overall_risk', 'UNKNOWN')
        conf = analysis.confidence_score
        parts.append(f"Risk Level: {risk}")
        parts.append(f"Confidence: {conf:.2f}")
        source = financial.get('data_source', 'unknown')
        parts.append(f"Data Source: {source}")
        response_text = "\n".join(parts)
    except Exception as e:
        response_text = f"Analysis Error: {str(e)}"
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=response_text),
            EndSessionContent(type="end-session"),
        ]
    ))

@swarm_protocol.on_message(model=ProposalAnalysisRequest, replies={ProposalAnalysisResponse})
async def handle_swarm_analysis(ctx: Context, sender: str, msg: ProposalAnalysisRequest):
    try:
        ctx.logger.info(f"Processing analysis request for proposal {msg.proposal_id}")
        analysis = await analyzer.perform_comprehensive_analysis(msg)
        ctx.logger.info(f"Analysis complete for {msg.proposal_id}: compliance={analysis.compliance}, confidence={analysis.confidence_score:.2f}")
        await ctx.send(sender, analysis)
    except Exception as e:
        ctx.logger.error(f"Error processing analysis request: {e}")
        error_response = ProposalAnalysisResponse(
            proposal_id=msg.proposal_id,
            compliance=False,
            violations=[f"Processing error: {str(e)}"],
            reasoning_trace=f"Analysis failed: {str(e)}",
            financial_impact={"error": str(e)},
            market_analysis={"error": str(e)},
            technical_assessment={"feasibility": "UNKNOWN"},
            risk_assessment={"overall_risk": "HIGH", "risk_factors": ["Processing error"]},
            recommendations=["Retry analysis"],
            confidence_score=0.0
        )
        await ctx.send(sender, error_response)

@chat_protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Enhanced Proposal Analysis Agent starting up...")
    ctx.logger.info(f"Agent address: {ctx.address}")
    ctx.logger.info("Pyth Network integration ready")
    ctx.logger.info("Dual protocol support: Chat + Swarm")

agent.include(chat_protocol, publish_manifest=True)
agent.include(swarm_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
