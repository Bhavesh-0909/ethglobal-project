import React from 'react';
import { Link } from 'react-router-dom';
import { useWeb3 } from '../contexts/Web3Context';
import { usePyth } from '../contexts/PythContext';
import './Home.css';

const Home = () => {
  const { active, account } = useWeb3();
  const { prices, getMarketSentiment } = usePyth();

  const marketSentiment = getMarketSentiment();
  const sentimentColor = {
    'STABLE': '#10B981',
    'VOLATILE': '#F59E0B',
    'HIGHLY_VOLATILE': '#EF4444',
    'UNKNOWN': '#6B7280'
  };

  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Analysis',
      description: 'Advanced AI agents analyze proposals with real-time market data and social sentiment'
    },
    {
      icon: '📊',
      title: 'Real-time Data',
      description: 'Integrated with Pyth Network for live price feeds and market analysis'
    },
    {
      icon: '🗳️',
      title: 'Smart Voting',
      description: 'Predictive voting outcomes based on social graphs and historical patterns'
    },
    {
      icon: '⚡',
      title: 'Automated Execution',
      description: 'Safe and automated proposal execution with comprehensive safety checks'
    }
  ];

  const stats = [
    { label: 'Active Organizations', value: '12', icon: '🏢' },
    { label: 'Proposals Analyzed', value: '156', icon: '📝' },
    { label: 'AI Confidence', value: '94%', icon: '🎯' },
    { label: 'Success Rate', value: '87%', icon: '✅' }
  ];

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              AI-Powered DAO Governance
              <span className="hero-subtitle">with Real-time Market Intelligence</span>
            </h1>
            <p className="hero-description">
              Experience the future of decentralized governance with AI agents that analyze proposals, 
              predict voting outcomes, and execute decisions using live market data from Pyth Network.
            </p>
            
            <div className="hero-actions">
              {active ? (
                <Link to="/dashboard" className="btn btn-primary">
                  Go to Dashboard
                </Link>
              ) : (
                <div className="connect-prompt">
                  <p>Connect your wallet to get started</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="hero-visual">
            <div className="hero-cards">
              <div className="hero-card">
                <div className="card-header">
                  <span className="card-icon">📊</span>
                  <span className="card-title">Market Data</span>
                </div>
                <div className="card-content">
                  <div className="price-item">
                    <span>ETH</span>
                    <span>{prices['ETH/USD'] ? `$${prices['ETH/USD'].price.toFixed(2)}` : 'Loading...'}</span>
                  </div>
                  <div className="price-item">
                    <span>BTC</span>
                    <span>{prices['BTC/USD'] ? `$${prices['BTC/USD'].price.toFixed(2)}` : 'Loading...'}</span>
                  </div>
                </div>
              </div>
              
              <div className="hero-card">
                <div className="card-header">
                  <span className="card-icon">🤖</span>
                  <span className="card-title">AI Analysis</span>
                </div>
                <div className="card-content">
                  <div className="analysis-item">
                    <span>Market Sentiment</span>
                    <span 
                      className="sentiment-badge"
                      style={{ color: sentimentColor[marketSentiment] }}
                    >
                      {marketSentiment}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <span>Confidence</span>
                    <span className="confidence-value">94%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="section-header">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-description">
            Built with cutting-edge AI and blockchain technology
          </p>
        </div>
        
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats">
        <div className="section-header">
          <h2 className="section-title">Platform Statistics</h2>
          <p className="section-description">
            Real-time metrics from our AI-powered governance platform
          </p>
        </div>
        
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-icon">{stat.icon}</div>
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Transform Your DAO?</h2>
          <p className="cta-description">
            Join the future of decentralized governance with AI-powered decision making
          </p>
          
          <div className="cta-actions">
            {active ? (
              <Link to="/organizations" className="btn btn-primary">
                Create Organization
              </Link>
            ) : (
              <div className="cta-connect">
                <p>Connect your wallet to start creating organizations</p>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
