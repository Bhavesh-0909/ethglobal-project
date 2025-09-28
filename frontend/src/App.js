import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Web3Provider } from './contexts/Web3Context';
import { AgentProvider } from './contexts/AgentContext';
import { PythProvider } from './contexts/PythContext';
import Layout from './components/Layout/Layout';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Organizations from './pages/Organizations';
import Proposals from './pages/Proposals';
import Voting from './pages/Voting';
import Profile from './pages/Profile';
import './App.css';

function App() {
  return (
    <Web3Provider>
      <AgentProvider>
        <PythProvider>
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/organizations" element={<Organizations />} />
                <Route path="/proposals" element={<Proposals />} />
                <Route path="/voting/:proposalId" element={<Voting />} />
                <Route path="/profile" element={<Profile />} />
              </Routes>
            </Layout>
          </Router>
        </PythProvider>
      </AgentProvider>
    </Web3Provider>
  );
}

export default App;
