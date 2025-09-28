import React, { useState, useEffect } from 'react';
import { useWeb3 } from '../contexts/Web3Context';
import { usePyth } from '../contexts/PythContext';
import './Organizations.css';

const Organizations = () => {
  const { 
    active, 
    account, 
    getUserOrganizations, 
    createOrganization, 
    joinOrganization 
  } = useWeb3();
  const { calculateUSDValue } = usePyth();
  
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [joinOrgId, setJoinOrgId] = useState('');

  // Form states
  const [createForm, setCreateForm] = useState({
    name: '',
    description: '',
    stakingToken: '0x0000000000000000000000000000000000000000', // ETH
    minStakeAmount: ''
  });

  const [joinForm, setJoinForm] = useState({
    stakeAmount: ''
  });

  useEffect(() => {
    if (active && account) {
      loadOrganizations();
    }
  }, [active, account]);

  const loadOrganizations = async () => {
    setLoading(true);
    try {
      const userOrgs = await getUserOrganizations();
      setOrganizations(userOrgs);
    } catch (err) {
      setError('Failed to load organizations');
      console.error('Organizations error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await createOrganization(
        createForm.name,
        createForm.description,
        createForm.stakingToken,
        createForm.minStakeAmount
      );
      
      setCreateForm({
        name: '',
        description: '',
        stakingToken: '0x0000000000000000000000000000000000000000',
        minStakeAmount: ''
      });
      setShowCreateModal(false);
      await loadOrganizations();
    } catch (err) {
      setError('Failed to create organization');
      console.error('Create organization error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinOrganization = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await joinOrganization(joinOrgId, joinForm.stakeAmount);
      
      setJoinForm({ stakeAmount: '' });
      setJoinOrgId('');
      setShowJoinModal(false);
      await loadOrganizations();
    } catch (err) {
      setError('Failed to join organization');
      console.error('Join organization error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getUSDValue = (amount, token = 'ETH') => {
    const usdValue = calculateUSDValue(parseFloat(amount), token);
    return usdValue ? `$${usdValue.toFixed(2)}` : '';
  };

  if (!active) {
    return (
      <div className="organizations">
        <div className="organizations-header">
          <h1>Organizations</h1>
          <p>Connect your wallet to view and manage organizations</p>
        </div>
      </div>
    );
  }

  return (
    <div className="organizations">
      <div className="organizations-header">
        <div className="header-content">
          <div className="header-text">
            <h1>Organizations</h1>
            <p>Create or join DAO organizations to participate in governance</p>
          </div>
          <div className="header-actions">
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              Create Organization
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowJoinModal(true)}
            >
              Join Organization
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Organizations List */}
      <div className="organizations-content">
        {loading ? (
          <div className="loading-state">
            <span className="spinner"></span>
            <p>Loading organizations...</p>
          </div>
        ) : organizations.length > 0 ? (
          <div className="organizations-grid">
            {organizations.map((org) => (
              <div key={org.id} className="organization-card">
                <div className="org-header">
                  <div className="org-info">
                    <h3 className="org-name">{org.name}</h3>
                    <span className="org-status">Active</span>
                  </div>
                  <div className="org-actions">
                    <button className="btn btn-outline btn-sm">
                      View Details
                    </button>
                  </div>
                </div>
                
                <p className="org-description">{org.description}</p>
                
                <div className="org-stats">
                  <div className="stat-item">
                    <span className="stat-label">Your Stake</span>
                    <span className="stat-value">
                      {org.userStake} ETH
                      {getUSDValue(org.userStake) && (
                        <span className="stat-usd">({getUSDValue(org.userStake)})</span>
                      )}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Total Staked</span>
                    <span className="stat-value">
                      {org.totalStaked} ETH
                      {getUSDValue(org.totalStaked) && (
                        <span className="stat-usd">({getUSDValue(org.totalStaked)})</span>
                      )}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Members</span>
                    <span className="stat-value">{org.memberCount}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Min Stake</span>
                    <span className="stat-value">
                      {org.minStakeAmount} ETH
                      {getUSDValue(org.minStakeAmount) && (
                        <span className="stat-usd">({getUSDValue(org.minStakeAmount)})</span>
                      )}
                    </span>
                  </div>
                </div>
                
                <div className="org-footer">
                  <span className="org-created">
                    Created {new Date(org.createdAt * 1000).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🏢</div>
            <h3>No Organizations Yet</h3>
            <p>Create your first organization or join an existing one</p>
            <div className="empty-actions">
              <button 
                className="btn btn-primary"
                onClick={() => setShowCreateModal(true)}
              >
                Create Organization
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => setShowJoinModal(true)}
              >
                Join Organization
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Create Organization Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Create Organization</h2>
              <button 
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleCreateOrganization} className="modal-form">
              <div className="form-group">
                <label className="form-label">Organization Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({...createForm, name: e.target.value})}
                  placeholder="Enter organization name"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-textarea"
                  value={createForm.description}
                  onChange={(e) => setCreateForm({...createForm, description: e.target.value})}
                  placeholder="Describe your organization's purpose"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Staking Token</label>
                <select
                  className="form-select"
                  value={createForm.stakingToken}
                  onChange={(e) => setCreateForm({...createForm, stakingToken: e.target.value})}
                >
                  <option value="0x0000000000000000000000000000000000000000">ETH</option>
                  <option value="0xA0b86a33E6441c8C06DdD4B4b8b8b8b8b8b8b8b8b8">USDC</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Minimum Stake Amount (ETH)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  value={createForm.minStakeAmount}
                  onChange={(e) => setCreateForm({...createForm, minStakeAmount: e.target.value})}
                  placeholder="0.1"
                  required
                />
              </div>
              
              <div className="modal-actions">
                <button 
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Creating...
                    </>
                  ) : (
                    'Create Organization'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Organization Modal */}
      {showJoinModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Join Organization</h2>
              <button 
                className="modal-close"
                onClick={() => setShowJoinModal(false)}
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleJoinOrganization} className="modal-form">
              <div className="form-group">
                <label className="form-label">Organization ID</label>
                <input
                  type="number"
                  className="form-input"
                  value={joinOrgId}
                  onChange={(e) => setJoinOrgId(e.target.value)}
                  placeholder="Enter organization ID"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Stake Amount (ETH)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  value={joinForm.stakeAmount}
                  onChange={(e) => setJoinForm({...joinForm, stakeAmount: e.target.value})}
                  placeholder="0.1"
                  required
                />
                {getUSDValue(joinForm.stakeAmount) && (
                  <div className="form-help">
                    ≈ {getUSDValue(joinForm.stakeAmount)} USD
                  </div>
                )}
              </div>
              
              <div className="modal-actions">
                <button 
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setShowJoinModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Joining...
                    </>
                  ) : (
                    'Join Organization'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Organizations;
