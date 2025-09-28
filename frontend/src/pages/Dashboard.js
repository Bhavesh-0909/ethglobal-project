import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useWeb3 } from '../contexts/Web3Context';
import { useAgent } from '../contexts/AgentContext';
import { usePyth } from '../contexts/PythContext';
import './Dashboard.css';

const Dashboard = () => {
  const { account, active, getUserOrganizations } = useWeb3();
  const { getComprehensiveAnalysis, getWorkflowStatus } = useAgent();
  const { prices, getMarketSentiment } = usePyth();
  
  const [organizations, setOrganizations] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (active && account) {
      loadDashboardData();
    }
  }, [active, account]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const userOrgs = await getUserOrganizations();
      setOrganizations(userOrgs);
      
      // Mock proposals data - in real app, fetch from contract
      const mockProposals = [
        {
          id: '1',
          title: 'Infrastructure Upgrade',
          organization: 'TechDAO',
          status: 'Active',
          votes: { for: 15, against: 3, abstain: 2 },
          deadline: '2024-01-15',
          amount: '50 ETH'
        },
        {
          id: '2',
          title: 'Marketing Campaign',
          organization: 'MarketingDAO',
          status: 'Pending',
          votes: { for: 8, against: 1, abstain: 0 },
          deadline: '2024-01-20',
          amount: '25 ETH'
        }
      ];
      setProposals(mockProposals);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'status-active';
      case 'Pending': return 'status-pending';
      case 'Approved': return 'status-approved';
      case 'Rejected': return 'status-rejected';
      default: return 'status-pending';
    }
  };

  const marketSentiment = getMarketSentiment();

  if (!active) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Connect your wallet to view your dashboard</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-loading">
          <span className="spinner"></span>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome back! Here's your governance overview.</p>
      </div>

      {/* Stats Overview */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">🏢</div>
          <div className="stat-content">
            <div className="stat-value">{organizations.length}</div>
            <div className="stat-label">Organizations</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <div className="stat-value">{proposals.length}</div>
            <div className="stat-label">Active Proposals</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🗳️</div>
          <div className="stat-content">
            <div className="stat-value">12</div>
            <div className="stat-label">Votes Cast</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{marketSentiment}</div>
            <div className="stat-label">Market Sentiment</div>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Organizations */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Your Organizations</h2>
            <Link to="/organizations" className="btn btn-outline">
              View All
            </Link>
          </div>
          
          {organizations.length > 0 ? (
            <div className="organizations-grid">
              {organizations.map((org) => (
                <div key={org.id} className="organization-card">
                  <div className="org-header">
                    <h3 className="org-name">{org.name}</h3>
                    <span className="org-status">Active</span>
                  </div>
                  <p className="org-description">{org.description}</p>
                  <div className="org-stats">
                    <div className="org-stat">
                      <span className="stat-label">Your Stake</span>
                      <span className="stat-value">{org.userStake} ETH</span>
                    </div>
                    <div className="org-stat">
                      <span className="stat-label">Total Members</span>
                      <span className="stat-value">{org.memberCount}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🏢</div>
              <h3>No Organizations Yet</h3>
              <p>Join or create an organization to get started</p>
              <Link to="/organizations" className="btn btn-primary">
                Explore Organizations
              </Link>
            </div>
          )}
        </div>

        {/* Recent Proposals */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Recent Proposals</h2>
            <Link to="/proposals" className="btn btn-outline">
              View All
            </Link>
          </div>
          
          {proposals.length > 0 ? (
            <div className="proposals-list">
              {proposals.map((proposal) => (
                <div key={proposal.id} className="proposal-card">
                  <div className="proposal-header">
                    <h3 className="proposal-title">{proposal.title}</h3>
                    <span className={`status-badge ${getStatusColor(proposal.status)}`}>
                      {proposal.status}
                    </span>
                  </div>
                  
                  <div className="proposal-meta">
                    <span className="proposal-org">{proposal.organization}</span>
                    <span className="proposal-amount">{proposal.amount}</span>
                    <span className="proposal-deadline">Due: {proposal.deadline}</span>
                  </div>
                  
                  <div className="proposal-votes">
                    <div className="vote-item">
                      <span className="vote-label">For</span>
                      <span className="vote-value">{proposal.votes.for}</span>
                    </div>
                    <div className="vote-item">
                      <span className="vote-label">Against</span>
                      <span className="vote-value">{proposal.votes.against}</span>
                    </div>
                    <div className="vote-item">
                      <span className="vote-label">Abstain</span>
                      <span className="vote-value">{proposal.votes.abstain}</span>
                    </div>
                  </div>
                  
                  <div className="proposal-actions">
                    <Link 
                      to={`/voting/${proposal.id}`} 
                      className="btn btn-primary"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📝</div>
              <h3>No Proposals Yet</h3>
              <p>Create or join an organization to see proposals</p>
              <Link to="/organizations" className="btn btn-primary">
                Join Organization
              </Link>
            </div>
          )}
        </div>

        {/* Market Overview */}
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Market Overview</h2>
            <span className="market-status">
              <span className="status-dot"></span>
              Live Data
            </span>
          </div>
          
          <div className="market-overview">
            <div className="market-prices">
              <div className="price-item">
                <span className="price-symbol">ETH</span>
                <span className="price-value">
                  {prices['ETH/USD'] ? `$${prices['ETH/USD'].price.toFixed(2)}` : 'Loading...'}
                </span>
                <span className="price-change positive">+2.5%</span>
              </div>
              <div className="price-item">
                <span className="price-symbol">BTC</span>
                <span className="price-value">
                  {prices['BTC/USD'] ? `$${prices['BTC/USD'].price.toFixed(2)}` : 'Loading...'}
                </span>
                <span className="price-change positive">+1.8%</span>
              </div>
            </div>
            
            <div className="market-sentiment">
              <div className="sentiment-item">
                <span className="sentiment-label">Market Sentiment</span>
                <span className={`sentiment-value ${marketSentiment.toLowerCase()}`}>
                  {marketSentiment}
                </span>
              </div>
              <div className="sentiment-item">
                <span className="sentiment-label">AI Confidence</span>
                <span className="confidence-value">94%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
