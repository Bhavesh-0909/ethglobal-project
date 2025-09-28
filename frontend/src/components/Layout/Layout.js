import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useWeb3 } from '../../contexts/Web3Context';
import { usePyth } from '../../contexts/PythContext';
import WalletConnect from '../Wallet/WalletConnect';
import './Layout.css';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { account, active } = useWeb3();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Proposals', href: '/proposals', icon: '📝' },
    { name: 'Profile', href: '/profile', icon: '👤' }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="layout">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <Link to="/" className="logo">
              <span className="logo-icon">🤖</span>
              <span className="logo-text">DAO Governance</span>
            </Link>
          </div>
          
          
          <div className="header-right">
            <WalletConnect />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="main-content">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
          <div className="sidebar-content">
            <nav className="sidebar-nav">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`nav-item ${isActive(item.href) ? 'nav-item-active' : ''}`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-text">{item.name}</span>
                </Link>
              ))}
            </nav>
            
            {active && (
              <div className="sidebar-footer">
                <div className="user-info">
                  <div className="user-avatar">
                    {account ? account.slice(0, 2).toUpperCase() : '👤'}
                  </div>
                  <div className="user-details">
                    <div className="user-address">
                      {account ? `${account.slice(0, 6)}...${account.slice(-4)}` : 'Not connected'}
                    </div>
                    <div className="user-status">Connected</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div 
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Page Content */}
        <main className="page-content">
          <div className="page-header">
            <button 
              className="sidebar-toggle"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              ☰
            </button>
            <h1 className="page-title">
              {navigation.find(item => item.href === location.pathname)?.name || 'DAO Governance'}
            </h1>
          </div>
          
          <div className="page-body">
            {children}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <p>&copy; 2024 DAO Governance Platform. Powered by AI Agents.</p>
          </div>
          <div className="footer-right">
            <div className="footer-links">
              <a href="#" className="footer-link">Documentation</a>
              <a href="#" className="footer-link">Support</a>
              <a href="#" className="footer-link">GitHub</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
