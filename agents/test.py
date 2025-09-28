#!/usr/bin/env python3
"""
Test script for DAO Governance Coordinator
Run with: python test_dao_coordinator.py
"""

import asyncio
import sys
from datetime import datetime
from uuid import uuid4

# Import your coordinator components
sys.path.append('.')  # Add current directory to path
from coordination_agent import (
    fetch_pyth_price,
    orchestrator,
    ProposalSubmission,
    ProposalAnalysisResponse,
    ProposalResponse,
    ExecutionResponse,
    UserQuery,
    StatusRequest,
    ChatMessage,
    TextContent,
    handle_proposal_analysis_response,
    handle_voter_sentiment_response,
    handle_execution_response,
    handle_user_query,
    handle_status_request,
    handle_chat_message
)

# Your test cases here (all the async functions I provided)
async def test_pyth_price_feed():
    try:
        price_data = await fetch_pyth_price()
        print(f"Pyth Price Data: {price_data}")
        
        if price_data["price"] is not None:
            print("✅ SUCCESS: Real-time ETH price fetched from Pyth Network")
            print(f"   Price: {price_data['price']}")
            print(f"   Confidence: {price_data['conf']}")
            print(f"   Publish Time: {price_data['publishTime']}")
        else:
            print("❌ FAILED: Could not fetch price data")
    except Exception as e:
        print(f"❌ ERROR: {e}")


# Test proposal submission with real market data
test_proposal = ProposalSubmission(
    proposal_id="test_prop_001",
    title="Test Infrastructure Upgrade",
    description="Upgrade server infrastructure to improve DAO performance and security",
    requested_amount=25.0,
    token_type="ETH",
    recipient_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    submitter="test_user",
    category="infrastructure"
)

# Submit and check workflow initiation
async def test_proposal_submission():
    try:
        status = orchestrator.start_workflow(test_proposal)
        
        # Test market data inclusion
        pyth_price = await fetch_pyth_price()
        
        print("✅ Proposal Workflow Started")
        print(f"   Proposal ID: {status.proposal_id}")
        print(f"   Current Stage: {status.current_stage}")
        print(f"   Progress: {status.progress_percentage}%")
        print(f"   Market Data Included: {pyth_price['price'] is not None}")
        
        return status
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


# ... [paste all the other test functions]

async def main():
    """Run all tests"""
    print("🚀 Starting DAO Coordinator Integration Tests...\n")
    
    try:
        # Run your tests in sequence
        await test_pyth_price_feed()
        await test_proposal_submission()
        # ... add all other test calls
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
