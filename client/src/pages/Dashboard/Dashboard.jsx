import React, { useState } from 'react';
import './Dashboard.css';

import ControlPanel from '../../components/ControlPanel/ControlPanel';
import CurrentSignals from '../../components/CurrentSignals/CurrentSignals';
import EmailLogsViewer from '../../components/EmailLogsViewer/EmailLogsViewer';
import LLMDecisionViewer from '../../components/LLMDecisionViewer/LLMDecisionViewer';
import LiveTradesTable from '../../components/LiveTradesTable/LiveTradesTable';
import PerformanceCharts from '../../components/PerformanceCharts/PerformanceCharts';
import PortfolioGraph from '../../components/PortfolioGraph/PortfolioGraph';
import SummaryPanel from '../../components/SummaryPanel/SummaryPanel';
import NewsFeed from '../../components/NewsFeed/NewsFeed.jsx';

const Dashboard = () => {
  const [isLiveMode, setIsLiveMode] = useState(true);
  const [selectedModel, setSelectedModel] = useState("DeepSeek v2");

  return (
    <div className="dashboard-layout">
  {/* Title */}
  <div className="dashboard-title-area">
    <h2 className="dashboard-title">Trading Dashboard</h2>
    <p className="dashboard-subtitle">Hedge Fund-Style Analytics & Execution Platform</p>
  </div>

  {/* Flex row layout */}
  <div className="dashboard-flex">
    <div className="dashboard-left">
      <SummaryPanel isLiveMode={isLiveMode} />
      <NewsFeed />
      <LiveTradesTable />
    </div>

    <div className="dashboard-right">
      <div className="dashboard-card-group">
        <ControlPanel
          isLiveMode={isLiveMode}
          setIsLiveMode={setIsLiveMode}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        />
        <CurrentSignals />
      </div>
      
    </div>
  </div>

  {/* Full-width section for graph */}
  <div className="dashboard-full-width">
    <PortfolioGraph />
  </div>

  {/* Remaining full-width panels */}
  <div className="dashboard-full-width">
    <PerformanceCharts />
    <div style={{ display: 'flex', gap: '1.5rem' }}>
  <div style={{ flex: 1 }}>
    <LLMDecisionViewer />
  </div>
  <div style={{ flex: 1 }}>
    <EmailLogsViewer />
  </div>
</div>
    
    
  </div>
</div>

  );
};

export default Dashboard;
