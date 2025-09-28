import React, { useState } from 'react';
import { useWeb3 } from '../../contexts/Web3Context';
import './WalletConnect.css';

const WalletConnect = () => {
  const { 
    account, 
    active, 
    chainId, 
    connectMetaMask, 
    connectWalletConnect, 
    disconnect, 
    switchNetwork,
    loading 
  } = useWeb3();
  
  const [showDropdown, setShowDropdown] = useState(false);

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getNetworkName = (chainId) => {
    switch (chainId) {
      case 1: return 'Ethereum';
      case 137: return 'Polygon';
      case 42161: return 'Arbitrum';
      default: return 'Unknown';
    }
  };

  const handleConnect = async (type) => {
    try {
      if (type === 'metamask') {
        await connectMetaMask();
      } else if (type === 'walletconnect') {
        await connectWalletConnect();
      }
      setShowDropdown(false);
    } catch (error) {
      console.error('Connection error:', error);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnect();
      setShowDropdown(false);
    } catch (error) {
      console.error('Disconnect error:', error);
    }
  };

  const handleSwitchNetwork = async (targetChainId) => {
    try {
      await switchNetwork(targetChainId);
    } catch (error) {
      console.error('Network switch error:', error);
    }
  };

  if (!active) {
    return (
      <div className="wallet-connect">
        <button 
          className="connect-button"
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Connecting...
            </>
          ) : (
            <>
              <span className="wallet-icon">🔗</span>
              Connect Wallet
            </>
          )}
        </button>
        
        {showDropdown && (
          <div className="wallet-dropdown">
            <div className="dropdown-header">
              <h3>Connect Wallet</h3>
              <button 
                className="close-button"
                onClick={() => setShowDropdown(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="wallet-options">
              <button 
                className="wallet-option"
                onClick={() => handleConnect('metamask')}
                disabled={loading}
              >
                <div className="wallet-option-icon">🦊</div>
                <div className="wallet-option-content">
                  <div className="wallet-option-name">MetaMask</div>
                  <div className="wallet-option-desc">Connect using MetaMask</div>
                </div>
              </button>
              
              <button 
                className="wallet-option"
                onClick={() => handleConnect('walletconnect')}
                disabled={loading}
              >
                <div className="wallet-option-icon">📱</div>
                <div className="wallet-option-content">
                  <div className="wallet-option-name">WalletConnect</div>
                  <div className="wallet-option-desc">Connect using WalletConnect</div>
                </div>
              </button>
            </div>
            
            <div className="dropdown-footer">
              <p>By connecting, you agree to our Terms of Service</p>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="wallet-connect">
      <div className="wallet-info">
        <div className="wallet-address">
          <span className="address-icon">👤</span>
          <span className="address-text">{formatAddress(account)}</span>
        </div>
        
        <div className="wallet-network">
          <span className="network-dot"></span>
          <span className="network-name">{getNetworkName(chainId)}</span>
        </div>
        
        <button 
          className="wallet-menu-button"
          onClick={() => setShowDropdown(!showDropdown)}
        >
          ⚙️
        </button>
      </div>
      
      {showDropdown && (
        <div className="wallet-dropdown">
          <div className="dropdown-header">
            <h3>Wallet Settings</h3>
            <button 
              className="close-button"
              onClick={() => setShowDropdown(false)}
            >
              ✕
            </button>
          </div>
          
          <div className="wallet-details">
            <div className="detail-item">
              <span className="detail-label">Address:</span>
              <span className="detail-value">{account}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Network:</span>
              <span className="detail-value">{getNetworkName(chainId)}</span>
            </div>
          </div>
          
          <div className="network-switcher">
            <h4>Switch Network</h4>
            <div className="network-options">
              <button 
                className="network-option"
                onClick={() => handleSwitchNetwork(1)}
                disabled={chainId === 1}
              >
                Ethereum
              </button>
              <button 
                className="network-option"
                onClick={() => handleSwitchNetwork(137)}
                disabled={chainId === 137}
              >
                Polygon
              </button>
              <button 
                className="network-option"
                onClick={() => handleSwitchNetwork(42161)}
                disabled={chainId === 42161}
              >
                Arbitrum
              </button>
            </div>
          </div>
          
          <div className="dropdown-actions">
            <button 
              className="disconnect-button"
              onClick={handleDisconnect}
            >
              Disconnect
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalletConnect;
