# DAO Governance Frontend

AI-Powered DAO Governance Platform with Real-time Market Data integration.

## Features

- 🔗 **Wallet Connection**: MetaMask and WalletConnect support
- 🤖 **AI Agent Integration**: Real-time proposal analysis and sentiment prediction
- 📊 **Live Market Data**: Pyth Network integration for real-time price feeds
- 🗳️ **Smart Voting**: Stake-weighted voting with AI recommendations
- 🏢 **Organization Management**: Create and join DAO organizations
- 📱 **Responsive Design**: Mobile-first design with modern UI/UX

## Tech Stack

- **React 18** - Modern React with hooks
- **Web3 Integration** - ethers.js for blockchain interactions
- **AI Agents** - Integration with ASI-1 API and custom agents
- **Real-time Data** - Pyth Network for live price feeds
- **Styling** - CSS3 with modern design patterns
- **Routing** - React Router for navigation

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- MetaMask or compatible wallet

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp env.example .env
```

3. Configure environment variables in `.env`:
```env
# Blockchain Configuration
REACT_APP_ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
REACT_APP_DAO_CONTRACT_ADDRESS=0x...

# AI Agent Configuration
REACT_APP_ASI1_API_KEY=your_asi1_api_key
REACT_APP_COORDINATION_AGENT_ADDRESS=agent1qw037h6333hn42ze6qtqu50hcpnz6pderfk3p3dw7djq08tgjnvfs9eqncv

# Pyth Network Configuration
REACT_APP_PYTH_BASE_URL=https://hermes.pyth.network
REACT_APP_ETH_USD_FEED_ID=0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace
```

4. Start development server:
```bash
npm start
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_ETHEREUM_RPC_URL` | Ethereum RPC endpoint | `https://mainnet.infura.io/v3/YOUR_KEY` |
| `REACT_APP_DAO_CONTRACT_ADDRESS` | Smart contract address | `0x742d35Cc6634C0532925a3b844Bc454e4438f44e` |
| `REACT_APP_ASI1_API_KEY` | ASI-1 API key | `sk_...` |
| `REACT_APP_COORDINATION_AGENT_ADDRESS` | Coordination agent address | `agent1qw037h6333hn42ze6qtqu50hcpnz6pderfk3p3dw7djq08tgjnvfs9eqncv` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_PYTH_BASE_URL` | Pyth Network API URL | `https://hermes.pyth.network` |
| `REACT_APP_DEBUG` | Enable debug mode | `false` |
| `REACT_APP_LOG_LEVEL` | Logging level | `info` |

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout/         # Layout components
│   ├── Wallet/         # Wallet connection components
│   └── PriceTicker/    # Price display components
├── contexts/           # React contexts for state management
│   ├── Web3Context.js  # Web3 and blockchain state
│   ├── AgentContext.js # AI agent integration
│   └── PythContext.js  # Pyth Network integration
├── pages/              # Page components
│   ├── Home.js         # Landing page
│   ├── Dashboard.js    # User dashboard
│   ├── Organizations.js # Organization management
│   ├── Proposals.js    # Proposal management
│   ├── Voting.js       # Voting interface
│   └── Profile.js      # User profile
├── utils/              # Utility functions
└── App.js              # Main application component
```

## Key Features

### 1. Wallet Integration
- MetaMask and WalletConnect support
- Multi-network support (Ethereum, Polygon, Arbitrum)
- Automatic network switching

### 2. AI Agent Integration
- **Coordination Agent**: Orchestrates the entire workflow
- **Proposal Analysis Agent**: Analyzes proposals with market data
- **Voter Sentiment Agent**: Predicts voting outcomes
- **Execution Agent**: Handles proposal execution

### 3. Real-time Market Data
- Live price feeds from Pyth Network
- ETH, BTC, SOL, USDC price tracking
- Market sentiment analysis
- USD value calculations

### 4. Smart Contract Integration
- Organization creation and management
- Proposal creation and voting
- Stake management
- Treasury operations

## Usage

### Creating an Organization
1. Connect your wallet
2. Navigate to Organizations page
3. Click "Create Organization"
4. Fill in organization details
5. Set minimum stake amount
6. Submit transaction

### Creating a Proposal
1. Join an organization
2. Navigate to Proposals page
3. Click "Create Proposal"
4. Fill in proposal details
5. AI agents will analyze the proposal
6. Proposal goes to voting phase

### Voting on Proposals
1. Navigate to a proposal
2. View AI analysis and recommendations
3. Cast your vote (For/Against/Abstain)
4. Vote is weighted by your stake

## AI Agent Workflow

1. **Proposal Submission** → Coordination Agent
2. **Analysis Phase** → Proposal Analysis Agent (with Pyth data)
3. **Sentiment Prediction** → Voter Sentiment Agent
4. **Execution Planning** → Execution Agent
5. **Final Recommendation** → Coordination Agent

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Style

- ESLint configuration included
- Prettier formatting
- Component-based architecture
- Custom hooks for state management

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify

```bash
npm run build
# Upload dist/ folder to Netlify
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- GitHub Issues
- Discord Community
- Documentation

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Enhanced AI agent capabilities
- [ ] Integration with more DeFi protocols
