import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useWeb3 } from '../contexts/Web3Context';
import { useAgent } from '../contexts/AgentContext';
import { usePyth } from '../contexts/PythContext';
import './Voting.css';

const Voting = () => {
  const { proposalId } = useParams();
  const { active, account, vote, getProposal } = useWeb3();
  const { getComprehensiveAnalysis, getVoterSentiment, chatWithAgent } = useAgent();
  const { prices, calculateUSDValue } = usePyth();
  
  const [proposal, setProposal] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(false);
  const [error, setError] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');

  useEffect(() => {
    if (active && account && proposalId) {
      loadProposalData();
    }
  }, [active, account, proposalId]);

  const loadProposalData = async () => {
    setLoading(true);
    try {
      // Load proposal details
      const proposalData = await getProposal(proposalId);
      setProposal(proposalData);
      
      // Load AI analysis
      const comprehensiveAnalysis = await getComprehensiveAnalysis(proposalId);
      setAnalysis(comprehensiveAnalysis);
      
      // Load voter sentiment
      const sentimentData = await getVoterSentiment(proposalId, ['alice', 'bob', 'charlie']);
      setSentiment(sentimentData);
    } catch (err) {
      setError('Failed to load proposal data');
      console.error('Voting error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (voteType) => {
    setVoting(true);
    setError(null);
    
    try {
      await vote(proposalId, voteType);
      await loadProposalData(); // Refresh data
    } catch (err) {
      setError('Failed to cast vote');
      console.error('Vote error:', err);
    } finally {
      setVoting(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;
    
    try {
      const response = await chatWithAgent(chatMessage);
      setChatResponse(response.response);
    } catch (err) {
      setError('Failed to get AI response');
    }
  };

  const getVoteTypeName = (voteType) => {
    switch (voteType) {
      case 1: return 'For';
      case 2: return 'Against';
      case 3: return 'Abstain';
      default: return 'None';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return '#10B981';
      case 'MEDIUM': return '#F59E0B';
      case 'HIGH': return '#EF4444';
      default: return '#6B7280';
    }
  };

  if (!active) {
    return (
      <div className="voting">
        <div className="voting-header">
          <h1>Voting</h1>
          <p>Connect your wallet to participate in voting</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="voting">
        <div className="voting-loading">
          <span className="spinner"></span>
          <p>Loading proposal details...</p>
        </div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="voting">
        <div className="voting-error">
          <h2>Proposal Not Found</h2>
          <p>The requested proposal could not be found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="voting">
      <div className="voting-header">
        <h1>Proposal Voting</h1>
        <p>Cast your vote and view AI-powered analysis</p>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="voting-content">
        {/* Proposal Details */}
        <div className="proposal-section">
          <div className="section-header">
            <h2>Proposal Details</h2>
            <span className={`status-badge ${proposal.status}`}>
              {proposal.status}
            </span>
          </div>
          
          <div className="proposal-card">
            <h3 className="proposal-title">{proposal.title}</h3>
            <p className="proposal-description">{proposal.description}</p>
            
            <div className="proposal-meta">
              <div className="meta-item">
                <span className="meta-label">Proposer:</span>
                <span className="meta-value">{proposal.proposer}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Amount:</span>
                <span className="meta-value">{proposal.requestedAmount} ETH</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Recipient:</span>
                <span className="meta-value">{proposal.recipientAddress}</span>
              </div>
            </div>
          </div>
        </div>

        {/* AI Analysis */}
        {analysis && (
          <div className="analysis-section">
            <div className="section-header">
              <h2>AI Analysis</h2>
              <span className="analysis-confidence">
                Confidence: {Math.round(analysis.confidence_score * 100)}%
              </span>
            </div>
            
            <div className="analysis-grid">
              <div className="analysis-card">
                <h4>Financial Impact</h4>
                <div className="analysis-content">
                  <div className="impact-item">
                    <span>USD Value:</span>
                    <span>{calculateUSDValue(proposal.requestedAmount) || 'N/A'}</span>
                  </div>
                  <div className="impact-item">
                    <span>Risk Level:</span>
                    <span 
                      className="risk-badge"
                      style={{ color: getRiskColor(analysis.risk_assessment) }}
                    >
                      {analysis.risk_assessment}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="analysis-card">
                <h4>Recommendation</h4>
                <div className="analysis-content">
                  <div className="recommendation">
                    {analysis.final_recommendation}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Voter Sentiment */}
        {sentiment && (
          <div className="sentiment-section">
            <div className="section-header">
              <h2>Voter Sentiment</h2>
              <span className="sentiment-prediction">
                Prediction: {sentiment.prediction}
              </span>
            </div>
            
            <div className="sentiment-card">
              <div className="sentiment-breakdown">
                <div className="sentiment-item">
                  <span className="sentiment-label">For:</span>
                  <span className="sentiment-value">{sentiment.vote_breakdown.For}</span>
                </div>
                <div className="sentiment-item">
                  <span className="sentiment-label">Against:</span>
                  <span className="sentiment-value">{sentiment.vote_breakdown.Against}</span>
                </div>
                <div className="sentiment-item">
                  <span className="sentiment-label">Abstain:</span>
                  <span className="sentiment-value">{sentiment.vote_breakdown.Neutral}</span>
                </div>
              </div>
              
              <div className="key-influencers">
                <h4>Key Influencers</h4>
                <div className="influencers-list">
                  {sentiment.key_influencers.map((influencer, index) => (
                    <span key={index} className="influencer-tag">
                      {influencer}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Voting Interface */}
        <div className="voting-section">
          <div className="section-header">
            <h2>Cast Your Vote</h2>
            <span className="voting-deadline">
              Deadline: {new Date(proposal.votingEndTime * 1000).toLocaleString()}
            </span>
          </div>
          
          <div className="voting-interface">
            <div className="vote-options">
              <button 
                className="vote-button vote-for"
                onClick={() => handleVote(1)}
                disabled={voting}
              >
                {voting ? (
                  <span className="spinner"></span>
                ) : (
                  <>
                    <span className="vote-icon">👍</span>
                    <span>Vote For</span>
                  </>
                )}
              </button>
              
              <button 
                className="vote-button vote-against"
                onClick={() => handleVote(2)}
                disabled={voting}
              >
                {voting ? (
                  <span className="spinner"></span>
                ) : (
                  <>
                    <span className="vote-icon">👎</span>
                    <span>Vote Against</span>
                  </>
                )}
              </button>
              
              <button 
                className="vote-button vote-abstain"
                onClick={() => handleVote(3)}
                disabled={voting}
              >
                {voting ? (
                  <span className="spinner"></span>
                ) : (
                  <>
                    <span className="vote-icon">🤷</span>
                    <span>Abstain</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* AI Chat */}
        <div className="chat-section">
          <div className="section-header">
            <h2>Ask AI Assistant</h2>
            <span className="chat-status">Powered by AI Agents</span>
          </div>
          
          <div className="chat-interface">
            <form onSubmit={handleChat} className="chat-form">
              <input
                type="text"
                className="chat-input"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Ask about this proposal..."
                required
              />
              <button type="submit" className="chat-submit">
                Send
              </button>
            </form>
            
            {chatResponse && (
              <div className="chat-response">
                <div className="response-header">
                  <span className="response-label">AI Response:</span>
                </div>
                <div className="response-content">
                  {chatResponse}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Voting;
