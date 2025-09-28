// Network configurations
export const networkConfigs = {
  1: {
    name: 'Ethereum',
    rpcUrl: process.env.REACT_APP_ETHEREUM_RPC_URL,
    blockExplorer: 'https://etherscan.io',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
  },
  137: {
    name: 'Polygon',
    rpcUrl: process.env.REACT_APP_POLYGON_RPC_URL,
    blockExplorer: 'https://polygonscan.com',
    nativeCurrency: {
      name: 'MATIC',
      symbol: 'MATIC',
      decimals: 18,
    },
  },
  42161: {
    name: 'Arbitrum',
    rpcUrl: process.env.REACT_APP_ARBITRUM_RPC_URL,
    blockExplorer: 'https://arbiscan.io',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
  },
};

// Supported chain IDs
export const supportedChainIds = [1, 137, 42161]; // Ethereum, Polygon, Arbitrum

// Simple connector objects for compatibility
export const injected = {
  name: 'MetaMask',
  type: 'injected'
};

export const walletconnect = {
  name: 'WalletConnect',
  type: 'walletconnect'
};