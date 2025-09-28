import React, { useState, useEffect } from 'react';
import { useWeb3 } from '../contexts/Web3Context';
import { usePyth } from '../contexts/PythContext';
import './Profile.css';

const Profile = () => {
  const { account, active, getUserOrganizations } = useWeb3();
  const { prices, calculateUSDValue } = usePyth();
  
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalVotes: 0,
    proposalsCreated: 0,
    totalStaked: 0,
    organizationsJoined: 0
  });

  useEffect(() => {
    if (active && account) {
      loadProfileData();
    }
  }, [active, account]);

  const loadProfileData = async () => {
    setLoading(true);
    try {
      const userOrgs = await getUserOrganizations();
      setOrganizations(userOrgs);
      
      // Calculate stats
      const totalStaked = userOrgs.reduce((sum, org) => sum + parseFloat(org.userStake), 0);
      setStats({
        totalVotes: 12, // Mock data
        proposalsCreated: 3, // Mock data
        totalStaked,
        organizationsJoined: userOrgs.length
      });
    } catch (err) {
      setError('Failed to load profile data');
      console.error('Profile error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getUSDValue = (amount) => {
    const usdValue = calculateUSDValue(parseFloat(amount), 'ETH');
    return usdValue ? `$${usdValue.toFixed(2)}` : '';
  };

  if (!active) {
    return (
      <div className="profile">
        <div className="profile-header">
          <h1>Profile</h1>
          <p>Connect your wallet to view your profile</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="profile">
        <div className="profile-loading">
          <span className="spinner"></span>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="profile-header">
        <div className="header-content">
          <div className="user-info">
            <div className="user-avatar">
              {account ? account.slice(0, 2).toUpperCase() : '👤'}
            </div>
            <div className="user-details">
              <h1>User Profile</h1>
              <p className="user-address">{account}</p>
              <p className="user-status">Connected</p>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="profile-content">
        {/* Stats Overview */}
        <div className="stats-section">
          <h2>Your Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">🗳️</div>
              <div className="stat-content">
                <div className="stat-value">{stats.totalVotes}</div>
                <div className="stat-label">Total Votes</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📝</div>
              <div className="stat-content">
                <div className="stat-value">{stats.proposalsCreated}</div>
                <div className="stat-label">Proposals Created</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">💰</div>
              <div className="stat-content">
                <div className="stat-value">{stats.totalStaked.toFixed(2)} ETH</div>
                <div className="stat-label">Total Staked</div>
                {getUSDValue(stats.totalStaked) && (
                  <div className="stat-usd">{getUSDValue(stats.totalStaked)}</div>
                )}
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🏢</div>
              <div className="stat-content">
                <div className="stat-value">{stats.organizationsJoined}</div>
                <div className="stat-label">Organizations</div>
              </div>
            </div>
          </div>
        </div>

        {/* Organizations */}
        <div className="organizations-section">
          <h2>Your Organizations</h2>
          {organizations.length > 0 ? (
            <div className="organizations-list">
              {organizations.map((org) => (
                <div key={org.id} className="organization-item">
                  <div className="org-info">
                    <h3 className="org-name">{org.name}</h3>
                    <p className="org-description">{org.description}</p>
                  </div>
                  
                  <div className="org-stats">
                    <div className="org-stat">
                      <span className="stat-label">Your Stake</span>
                      <span className="stat-value">
                        {org.userStake} ETH
                        {getUSDValue(org.userStake) && (
                          <span className="stat-usd">({getUSDValue(org.userStake)})</span>
                        )}
                      </span>
                    </div>
                    <div className="org-stat">
                      <span className="stat-label">Total Members</span>
                      <span className="stat-value">{org.memberCount}</span>
                    </div>
                    <div className="org-stat">
                      <span className="stat-label">Total Staked</span>
                      <span className="stat-value">
                        {org.totalStaked} ETH
                        {getUSDValue(org.totalStaked) && (
                          <span className="stat-usd">({getUSDValue(org.totalStaked)})</span>
                        )}
                      </span>
                    </div>
                  </div>
                  
                  <div className="org-actions">
                    <button className="btn btn-outline btn-sm">
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🏢</div>
              <h3>No Organizations Yet</h3>
              <p>Join or create an organization to get started</p>
            </div>
          )}
        </div>

        {/* Activity History */}
        <div className="activity-section">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon">🗳️</div>
              <div className="activity-content">
                <div className="activity-title">Voted on "Infrastructure Upgrade"</div>
                <div className="activity-meta">2 hours ago • TechDAO</div>
              </div>
              <div className="activity-status">For</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon">📝</div>
              <div className="activity-content">
                <div className="activity-title">Created proposal "Marketing Campaign"</div>
                <div className="activity-meta">1 day ago • MarketingDAO</div>
              </div>
              <div className="activity-status">Pending</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon">🏢</div>
              <div className="activity-content">
                <div className="activity-title">Joined TechDAO</div>
                <div className="activity-meta">3 days ago</div>
              </div>
              <div className="activity-status">Active</div>
            </div>
          </div>
        </div>

        {/* Market Overview */}
        <div className="market-section">
          <h2>Market Overview</h2>
          <div className="market-card">
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
            
            <div className="market-summary">
              <div className="summary-item">
                <span className="summary-label">Portfolio Value</span>
                <span className="summary-value">
                  {getUSDValue(stats.totalStaked) || 'Calculating...'}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Staking Rewards</span>
                <span className="summary-value">+5.2% APY</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
