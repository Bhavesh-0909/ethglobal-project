import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const PythContext = createContext();

export const usePyth = () => {
  const context = useContext(PythContext);
  if (!context) {
    throw new Error('usePyth must be used within a PythProvider');
  }
  return context;
};

export const PythProvider = ({ children }) => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Price feed IDs from environment
  const priceFeeds = {
    'ETH/USD': process.env.REACT_APP_ETH_USD_FEED_ID,
    'BTC/USD': process.env.REACT_APP_BTC_USD_FEED_ID,
    'SOL/USD': process.env.REACT_APP_SOL_USD_FEED_ID,
    'USDC/USD': process.env.REACT_APP_USDC_USD_FEED_ID
  };

  // Fetch latest prices from Pyth Network
  const fetchPrices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const feedIds = Object.values(priceFeeds).filter(Boolean);
      const response = await axios.get(process.env.REACT_APP_PYTH_PRICE_FEEDS_URL, {
        params: {
          ids: feedIds.join(',')
        }
      });
      
      if (response.data && response.data.parsed) {
        const priceData = {};
        const symbols = Object.keys(priceFeeds);
        
        response.data.parsed.forEach((feed, index) => {
          if (index < symbols.length) {
            const symbol = symbols[index];
            const priceInfo = feed.price;
            
            if (priceInfo) {
              priceData[symbol] = {
                price: parseFloat(priceInfo.price) / Math.pow(10, Math.abs(priceInfo.expo)),
                confidence: parseFloat(priceInfo.conf) / Math.pow(10, Math.abs(priceInfo.expo)),
                timestamp: priceInfo.publish_time,
                status: feed.status
              };
            }
          }
        });
        
        setPrices(priceData);
        setLastUpdate(new Date());
      }
    } catch (err) {
      console.error('Error fetching Pyth prices:', err);
      setError('Failed to fetch real-time prices');
      
      // Fallback to mock data in development
      if (process.env.NODE_ENV === 'development') {
        setPrices({
          'ETH/USD': { price: 2400.0, confidence: 0.5, status: 'fallback' },
          'BTC/USD': { price: 43000.0, confidence: 0.5, status: 'fallback' },
          'SOL/USD': { price: 95.0, confidence: 0.5, status: 'fallback' },
          'USDC/USD': { price: 1.0, confidence: 0.5, status: 'fallback' }
        });
        setLastUpdate(new Date());
      }
    } finally {
      setLoading(false);
    }
  };

  // Get specific price
  const getPrice = (symbol) => {
    return prices[symbol] || null;
  };

  // Get all prices
  const getAllPrices = () => {
    return prices;
  };

  // Calculate USD value
  const calculateUSDValue = (amount, tokenSymbol) => {
    const priceData = getPrice(`${tokenSymbol}/USD`);
    if (priceData && priceData.price) {
      return amount * priceData.price;
    }
    return null;
  };

  // Get price confidence
  const getPriceConfidence = (symbol) => {
    const priceData = getPrice(symbol);
    return priceData ? priceData.confidence : null;
  };

  // Check if price is reliable
  const isPriceReliable = (symbol, minConfidence = 0.01) => {
    const confidence = getPriceConfidence(symbol);
    return confidence && confidence >= minConfidence;
  };

  // Get market sentiment
  const getMarketSentiment = () => {
    const ethPrice = getPrice('ETH/USD');
    const btcPrice = getPrice('BTC/USD');
    
    if (!ethPrice || !btcPrice) return 'UNKNOWN';
    
    const avgConfidence = (ethPrice.confidence + btcPrice.confidence) / 2;
    
    if (avgConfidence > 0.1) return 'STABLE';
    if (avgConfidence > 0.05) return 'VOLATILE';
    return 'HIGHLY_VOLATILE';
  };

  // Auto-refresh prices every 30 seconds
  useEffect(() => {
    fetchPrices();
    
    const interval = setInterval(fetchPrices, 30000);
    return () => clearInterval(interval);
  }, []);

  // Format price for display
  const formatPrice = (symbol, decimals = 2) => {
    const priceData = getPrice(symbol);
    if (!priceData || !priceData.price) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(priceData.price);
  };

  // Get price change (mock implementation)
  const getPriceChange = (symbol) => {
    // This would typically compare with historical data
    // For now, return a mock change
    return {
      change: Math.random() * 10 - 5, // Random change between -5% and +5%
      changePercent: Math.random() * 2 - 1 // Random change between -1% and +1%
    };
  };

  const value = {
    // State
    prices,
    loading,
    error,
    lastUpdate,
    
    // Actions
    fetchPrices,
    getPrice,
    getAllPrices,
    calculateUSDValue,
    getPriceConfidence,
    isPriceReliable,
    getMarketSentiment,
    formatPrice,
    getPriceChange
  };

  return (
    <PythContext.Provider value={value}>
      {children}
    </PythContext.Provider>
  );
};
