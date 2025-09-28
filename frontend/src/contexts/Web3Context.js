import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers } from 'ethers';

const Web3Context = createContext();

export const useWeb3 = () => {
  const context = useContext(Web3Context);
  if (!context) {
    throw new Error('useWeb3 must be used within a Web3Provider');
  }
  return context;
};

export const Web3Provider = ({ children }) => {
  const [account, setAccount] = useState(null);
  const [library, setLibrary] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [active, setActive] = useState(false);
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Contract ABI and address
  const contractAddress = process.env.REACT_APP_DAO_CONTRACT_ADDRESS;
  const contractABI = require('../contracts/ABI.json');

  // Check if wallet is connected
  useEffect(() => {
    const checkConnection = async () => {
      if (typeof window.ethereum !== 'undefined') {
        try {
          const accounts = await window.ethereum.request({ method: 'eth_accounts' });
          if (accounts.length > 0) {
            setAccount(accounts[0]);
            setActive(true);
            
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            setLibrary(provider);
            
            const network = await provider.getNetwork();
            setChainId(network.chainId);
            
            // Initialize contract
            if (contractAddress && contractABI) {
              const signer = provider.getSigner();
              const contractInstance = new ethers.Contract(contractAddress, contractABI, signer);
              setContract(contractInstance);
            }
          }
        } catch (err) {
          console.error('Error checking wallet connection:', err);
        }
      }
    };

    checkConnection();

    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          setActive(true);
        } else {
          setAccount(null);
          setActive(false);
          setContract(null);
        }
      });

      window.ethereum.on('chainChanged', (chainId) => {
        setChainId(parseInt(chainId, 16));
        window.location.reload();
      });
    }
  }, [contractAddress, contractABI]);

  // Connect to MetaMask
  const connectMetaMask = async () => {
    setLoading(true);
    setError(null);
    try {
      if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setAccount(accounts[0]);
        setActive(true);
        
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        setLibrary(provider);
        
        const network = await provider.getNetwork();
        setChainId(network.chainId);
        
        // Initialize contract
        if (contractAddress && contractABI) {
          const signer = provider.getSigner();
          const contractInstance = new ethers.Contract(contractAddress, contractABI, signer);
          setContract(contractInstance);
        }
      } else {
        throw new Error('MetaMask not installed');
      }
    } catch (err) {
      console.error('Error connecting to MetaMask:', err);
      setError('Failed to connect to MetaMask');
    } finally {
      setLoading(false);
    }
  };

  // Connect to WalletConnect
  const connectWalletConnect = async () => {
    setLoading(true);
    setError(null);
    try {
      // For now, redirect to MetaMask
      // In a full implementation, you'd integrate WalletConnect here
      await connectMetaMask();
    } catch (err) {
      console.error('Error connecting to WalletConnect:', err);
      setError('Failed to connect to WalletConnect');
    } finally {
      setLoading(false);
    }
  };

  // Disconnect wallet
  const disconnect = async () => {
    setLoading(true);
    try {
      setAccount(null);
      setActive(false);
      setContract(null);
      setLibrary(null);
      setChainId(null);
    } catch (err) {
      console.error('Error disconnecting:', err);
      setError('Failed to disconnect');
    } finally {
      setLoading(false);
    }
  };

  // Switch network
  const switchNetwork = async (targetChainId) => {
    if (!library) return;
    
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${targetChainId.toString(16)}` }],
      });
    } catch (err) {
      console.error('Error switching network:', err);
      setError('Failed to switch network');
    }
  };

  // Get user's organizations
  const getUserOrganizations = async () => {
    if (!contract || !account) return [];
    
    try {
      const orgCount = await contract.organizationCount();
      const organizations = [];
      
      for (let i = 1; i <= orgCount; i++) {
        const orgInfo = await contract.getOrganizationInfo(i);
        const memberStake = await contract.getMemberStake(i, account);
        
        if (memberStake.gt(0)) {
          organizations.push({
            id: i,
            name: orgInfo[0],
            description: orgInfo[1],
            owner: orgInfo[2],
            stakingToken: orgInfo[3],
            minStakeAmount: orgInfo[4],
            totalStaked: orgInfo[5],
            memberCount: orgInfo[6],
            isActive: orgInfo[7],
            createdAt: orgInfo[8],
            userStake: memberStake.toString()
          });
        }
      }
      
      return organizations;
    } catch (err) {
      console.error('Error fetching user organizations:', err);
      setError('Failed to fetch organizations');
      return [];
    }
  };

  // Create organization
  const createOrganization = async (name, description, stakingToken, minStakeAmount) => {
    if (!contract) throw new Error('Contract not initialized');
    
    try {
      const tx = await contract.createOrganization(
        name,
        description,
        stakingToken,
        ethers.utils.parseEther(minStakeAmount.toString())
      );
      await tx.wait();
      return tx;
    } catch (err) {
      console.error('Error creating organization:', err);
      throw new Error('Failed to create organization');
    }
  };

  // Join organization
  const joinOrganization = async (orgId, stakeAmount) => {
    if (!contract) throw new Error('Contract not initialized');
    
    try {
      const tx = await contract.joinOrganization(
        orgId,
        ethers.utils.parseEther(stakeAmount.toString()),
        { value: ethers.utils.parseEther(stakeAmount.toString()) }
      );
      await tx.wait();
      return tx;
    } catch (err) {
      console.error('Error joining organization:', err);
      throw new Error('Failed to join organization');
    }
  };

  // Create proposal
  const createProposal = async (orgId, title, description, requestedAmount, tokenAddress, recipientAddress) => {
    if (!contract) throw new Error('Contract not initialized');
    
    try {
      const tx = await contract.createProposal(
        orgId,
        title,
        description,
        ethers.utils.parseEther(requestedAmount.toString()),
        tokenAddress,
        recipientAddress
      );
      await tx.wait();
      return tx;
    } catch (err) {
      console.error('Error creating proposal:', err);
      throw new Error('Failed to create proposal');
    }
  };

  // Vote on proposal
  const vote = async (proposalId, voteType) => {
    if (!contract) throw new Error('Contract not initialized');
    
    try {
      const tx = await contract.vote(proposalId, voteType);
      await tx.wait();
      return tx;
    } catch (err) {
      console.error('Error voting:', err);
      throw new Error('Failed to vote');
    }
  };

  // Get proposal details
  const getProposal = async (proposalId) => {
    if (!contract) return null;
    
    try {
      const basic = await contract.getProposalBasic(proposalId);
      const voting = await contract.getProposalVoting(proposalId);
      const analysis = await contract.getProposalAnalysis(proposalId);
      
      return {
        id: basic[0].toString(),
        organizationId: basic[1].toString(),
        title: basic[2],
        proposer: basic[3],
        status: basic[4],
        forVotes: voting[0].toString(),
        againstVotes: voting[1].toString(),
        abstainVotes: voting[2].toString(),
        votingEndTime: voting[3].toString(),
        analysisHash: analysis[0],
        riskLevel: analysis[1].toString(),
        confidenceScore: analysis[2].toString(),
        executionApproved: analysis[3]
      };
    } catch (err) {
      console.error('Error fetching proposal:', err);
      return null;
    }
  };

  const value = {
    // State
    account,
    library,
    chainId,
    active,
    contract,
    loading,
    error,
    
    // Actions
    connectMetaMask,
    connectWalletConnect,
    disconnect,
    switchNetwork,
    
    // Contract methods
    getUserOrganizations,
    createOrganization,
    joinOrganization,
    createProposal,
    vote,
    getProposal
  };

  return (
    <Web3Context.Provider value={value}>
      {children}
    </Web3Context.Provider>
  );
};