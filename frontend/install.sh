#!/bin/bash

echo "🚀 Installing DAO Governance Frontend Dependencies..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Install dependencies
echo "📦 Installing npm packages..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Copy env.example to .env:"
    echo "   cp env.example .env"
    echo ""
    echo "2. Edit .env with your configuration:"
    echo "   - Add your Infura/Alchemy RPC URLs"
    echo "   - Add your smart contract address"
    echo "   - Add your AI agent addresses"
    echo ""
    echo "3. Start the development server:"
    echo "   npm start"
    echo ""
    echo "🎉 Happy coding!"
else
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi
