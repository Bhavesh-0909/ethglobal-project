import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AgentContext = createContext();

export const useAgent = () => {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgent must be used within an AgentProvider');
  }
  return context;
};

export const AgentProvider = ({ children }) => {
  const [agents, setAgents] = useState({
    coordination: null,
    proposalAnalysis: null,
    voterSentiment: null,
    execution: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Agent addresses from environment
  const agentAddresses = {
    coordination: process.env.REACT_APP_COORDINATION_AGENT_ADDRESS,
    proposalAnalysis: process.env.REACT_APP_PROPOSAL_ANALYSIS_AGENT_ADDRESS,
    voterSentiment: process.env.REACT_APP_VOTER_SENTIMENT_AGENT_ADDRESS,
    execution: process.env.REACT_APP_EXECUTION_AGENT_ADDRESS
  };

  // Initialize agents
  useEffect(() => {
    setAgents(agentAddresses);
  }, []);

  // Submit proposal for analysis
  const submitProposal = async (proposalData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/agents/submit-proposal', {
        agentAddress: agents.coordination,
        proposalData
      });
      
      return response.data;
    } catch (err) {
      console.error('Error submitting proposal:', err);
      setError('Failed to submit proposal for analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get proposal analysis
  const getProposalAnalysis = async (proposalId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/agents/analysis/${proposalId}`, {
        params: {
          agentAddress: agents.proposalAnalysis
        }
      });
      
      return response.data;
    } catch (err) {
      console.error('Error fetching proposal analysis:', err);
      setError('Failed to fetch proposal analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get voter sentiment prediction
  const getVoterSentiment = async (proposalId, userList) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/agents/voter-sentiment', {
        agentAddress: agents.voterSentiment,
        proposalId,
        userList
      });
      
      return response.data;
    } catch (err) {
      console.error('Error fetching voter sentiment:', err);
      setError('Failed to fetch voter sentiment');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get execution plan
  const getExecutionPlan = async (proposalId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/agents/execution/${proposalId}`, {
        params: {
          agentAddress: agents.execution
        }
      });
      
      return response.data;
    } catch (err) {
      console.error('Error fetching execution plan:', err);
      setError('Failed to fetch execution plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get comprehensive analysis
  const getComprehensiveAnalysis = async (proposalId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/agents/comprehensive/${proposalId}`, {
        params: {
          coordinationAgent: agents.coordination
        }
      });
      
      return response.data;
    } catch (err) {
      console.error('Error fetching comprehensive analysis:', err);
      setError('Failed to fetch comprehensive analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Chat with coordination agent
  const chatWithAgent = async (message) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/agents/chat', {
        agentAddress: agents.coordination,
        message
      });
      
      return response.data;
    } catch (err) {
      console.error('Error chatting with agent:', err);
      setError('Failed to communicate with agent');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get workflow status
  const getWorkflowStatus = async (proposalId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/agents/status/${proposalId}`, {
        params: {
          agentAddress: agents.coordination
        }
      });
      
      return response.data;
    } catch (err) {
      console.error('Error fetching workflow status:', err);
      setError('Failed to fetch workflow status');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Submit comment for sentiment analysis
  const submitComment = async (commentData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/agents/comment', {
        agentAddress: agents.voterSentiment,
        commentData
      });
      
      return response.data;
    } catch (err) {
      console.error('Error submitting comment:', err);
      setError('Failed to submit comment for analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    // State
    agents,
    loading,
    error,
    
    // Actions
    submitProposal,
    getProposalAnalysis,
    getVoterSentiment,
    getExecutionPlan,
    getComprehensiveAnalysis,
    chatWithAgent,
    getWorkflowStatus,
    submitComment
  };

  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
};
