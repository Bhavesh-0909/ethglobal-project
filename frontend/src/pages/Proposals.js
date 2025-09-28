import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useWeb3 } from '../contexts/Web3Context';
import { useAgent } from '../contexts/AgentContext';
import './Proposals.css';

const Proposals = () => {
  const { active, account, createProposal, getProposal } = useWeb3();
  const { submitProposal, getProposalAnalysis, loading: agentLoading } = useAgent();
  
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    orgId: '',
    title: '',
    description: '',
    requestedAmount: '',
    tokenAddress: '0x0000000000000000000000000000000000000000',
    recipientAddress: ''
  });

  useEffect(() => {
    if (active && account) {
      loadProposals();
    }
  }, [active, account]);

  const loadProposals = async () => {
    setLoading(true);
    try {
      // Mock data - in real app, fetch from contract
      const mockProposals = [
        {
          id: '1',
          title: 'Infrastructure Upgrade',
          description: 'Upgrade server infrastructure to improve performance',
          organization: 'TechDAO',
          proposer: account,
          requestedAmount: '50',
          tokenAddress: '0x0000000000000000000000000000000000000000',
          recipientAddress: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
          status: 'Active',
          votes: { for: 15, against: 3, abstain: 2 },
          deadline: '2024-01-15',
          createdAt: '2024-01-01'
        }
      ];
      setProposals(mockProposals);
    } catch (err) {
      setError('Failed to load proposals');
      console.error('Proposals error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProposal = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Create proposal on blockchain
      const tx = await createProposal(
        createForm.orgId,
        createForm.title,
        createForm.description,
        createForm.requestedAmount,
        createForm.tokenAddress,
        createForm.recipientAddress
      );

      // Submit to AI agents for analysis
      const proposalData = {
        proposal_id: tx.hash,
        title: createForm.title,
        description: createForm.description,
        requested_amount: parseFloat(createForm.requestedAmount),
        token_type: createForm.tokenAddress === '0x0000000000000000000000000000000000000000' ? 'ETH' : 'USDC',
        recipient_address: createForm.recipientAddress,
        submitter: account,
        category: 'funding'
      };

      await submitProposal(proposalData);
      
      setCreateForm({
        orgId: '',
        title: '',
        description: '',
        requestedAmount: '',
        tokenAddress: '0x0000000000000000000000000000000000000000',
        recipientAddress: ''
      });
      setShowCreateModal(false);
      await loadProposals();
    } catch (err) {
      setError('Failed to create proposal');
      console.error('Create proposal error:', err);
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
      case 'Executed': return 'status-executed';
      default: return 'status-pending';
    }
  };

  if (!active) {
    return (
      <div className="proposals">
        <div className="proposals-header">
          <h1>Proposals</h1>
          <p>Connect your wallet to view and create proposals</p>
        </div>
      </div>
    );
  }

  return (
    <div className="proposals">
      <div className="proposals-header">
        <div className="header-content">
          <div className="header-text">
            <h1>Proposals</h1>
            <p>Create and manage DAO proposals with AI-powered analysis</p>
          </div>
          <div className="header-actions">
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              Create Proposal
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

      <div className="proposals-content">
        {loading ? (
          <div className="loading-state">
            <span className="spinner"></span>
            <p>Loading proposals...</p>
          </div>
        ) : proposals.length > 0 ? (
          <div className="proposals-list">
            {proposals.map((proposal) => (
              <div key={proposal.id} className="proposal-card">
                <div className="proposal-header">
                  <div className="proposal-info">
                    <h3 className="proposal-title">{proposal.title}</h3>
                    <span className={`status-badge ${getStatusColor(proposal.status)}`}>
                      {proposal.status}
                    </span>
                  </div>
                  <div className="proposal-meta">
                    <span className="proposal-org">{proposal.organization}</span>
                    <span className="proposal-amount">{proposal.requestedAmount} ETH</span>
                  </div>
                </div>
                
                <p className="proposal-description">{proposal.description}</p>
                
                <div className="proposal-details">
                  <div className="detail-item">
                    <span className="detail-label">Proposer:</span>
                    <span className="detail-value">{proposal.proposer.slice(0, 6)}...{proposal.proposer.slice(-4)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Recipient:</span>
                    <span className="detail-value">{proposal.recipientAddress.slice(0, 6)}...{proposal.recipientAddress.slice(-4)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Deadline:</span>
                    <span className="detail-value">{proposal.deadline}</span>
                  </div>
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
            <p>Create your first proposal to get started</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              Create Proposal
            </button>
          </div>
        )}
      </div>

      {/* Create Proposal Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Create Proposal</h2>
              <button 
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleCreateProposal} className="modal-form">
              <div className="form-group">
                <label className="form-label">Organization ID</label>
                <input
                  type="number"
                  className="form-input"
                  value={createForm.orgId}
                  onChange={(e) => setCreateForm({...createForm, orgId: e.target.value})}
                  placeholder="Enter organization ID"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Proposal Title</label>
                <input
                  type="text"
                  className="form-input"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({...createForm, title: e.target.value})}
                  placeholder="Enter proposal title"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-textarea"
                  value={createForm.description}
                  onChange={(e) => setCreateForm({...createForm, description: e.target.value})}
                  placeholder="Describe your proposal"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Requested Amount (ETH)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  value={createForm.requestedAmount}
                  onChange={(e) => setCreateForm({...createForm, requestedAmount: e.target.value})}
                  placeholder="0.1"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Recipient Address</label>
                <input
                  type="text"
                  className="form-input"
                  value={createForm.recipientAddress}
                  onChange={(e) => setCreateForm({...createForm, recipientAddress: e.target.value})}
                  placeholder="0x..."
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
                  disabled={loading || agentLoading}
                >
                  {loading || agentLoading ? (
                    <>
                      <span className="spinner"></span>
                      Creating...
                    </>
                  ) : (
                    'Create Proposal'
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

export default Proposals;
