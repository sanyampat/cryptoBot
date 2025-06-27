import React from 'react';
import './PortfolioGraph.css';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis
} from 'recharts';

const PortfolioGraph = () => {
  const portfolioData = [
    { date: '06-17', portfolio: 100000, benchmark: 100000, drawdown: 0 },
    { date: '06-18', portfolio: 102500, benchmark: 101200, drawdown: -0.5 },
    { date: '06-19', portfolio: 101800, benchmark: 100800, drawdown: -1.2 },
    { date: '06-20', portfolio: 105200, benchmark: 102100, drawdown: 0 },
    { date: '06-21', portfolio: 107800, benchmark: 103500, drawdown: 0 },
    { date: '06-22', portfolio: 110100, benchmark: 104200, drawdown: 0 },
    { date: '06-23', portfolio: 112400, benchmark: 105800, drawdown: 0 },
    { date: '06-24', portfolio: 115600, benchmark: 106500, drawdown: 0 }
  ];

  const performanceMetrics = [
    { label: 'Total Return', value: '+15.6%', color: 'green' },
    { label: 'Benchmark Return', value: '+6.5%', color: 'blue' },
    { label: 'Alpha', value: '+9.1%', color: 'purple' },
    { label: 'Max Drawdown', value: '-1.2%', color: 'red' },
    { label: 'Sharpe Ratio', value: '2.34', color: 'goldenrod' },
    { label: 'Volatility', value: '12.8%', color: 'orange' }
  ];

  const portfolioStats = [
    { label: 'Current Value', value: '₹115,600', change: '+15.6%', positive: true },
    { label: 'Daily P&L', value: '+₹3,200', change: '+2.8%', positive: true },
    { label: 'Active Positions', value: '8', change: '+2', positive: true },
    { label: 'Cash Available', value: '₹25,400', change: '-5.2%', positive: false }
  ];

  return (
    <div className="portfolio-card">
      <div className="portfolio-header">
        <span>Portfolio Performance</span>
        <span className="subdued">Last 7 days</span>
      </div>

      <div className="portfolio-stats">
        {portfolioStats.map((stat, i) => (
          <div className="stat-box" key={i}>
            <div className="stat-label">{stat.label}</div>
            <div className="stat-value">{stat.value}</div>
            <div className={`stat-change ${stat.positive ? 'positive' : 'negative'}`}>
              {stat.change}
            </div>
          </div>
        ))}
      </div>

      <div className="portfolio-chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={portfolioData} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
            <defs>
              <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4ade80" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#60a5fa" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#ccc" fontSize={12} />
            <YAxis
              stroke="#ccc"
              fontSize={12}
              domain={['dataMin - 1000', 'dataMax + 1000']}
              tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
            />
            <Area type="monotone" dataKey="benchmark" stroke="#60a5fa" strokeWidth={2} fill="url(#benchmarkGradient)" dot={false} />
            <Area type="monotone" dataKey="portfolio" stroke="#4ade80" strokeWidth={3} fill="url(#portfolioGradient)" dot={{ fill: '#4ade80', r: 4 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="performance-metrics">
        {performanceMetrics.map((metric, i) => (
          <div className="metric" key={i}>
            <div className="metric-label">{metric.label}</div>
            <div className="metric-value" style={{ color: metric.color }}>
              {metric.value}
            </div>
          </div>
        ))}
      </div>

      <div className="legend-container">
        <div className="legend-item">
          <span className="dot" style={{ backgroundColor: '#4ade80' }}></span>
          <span>Portfolio</span>
        </div>
        <div className="legend-item">
          <span className="dot" style={{ backgroundColor: '#60a5fa' }}></span>
          <span>Benchmark</span>
        </div>
      </div>
    </div>
  );
};

export default PortfolioGraph;
