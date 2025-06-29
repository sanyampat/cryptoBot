import React, { useEffect, useState } from 'react';
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
  const [portfolioStats, setPortfolioStats] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [graphData, setGraphData] = useState([]);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/portfolio-stats');
      const data = await res.json();

      // Use fallback values with || and ternaries
      const currentValue = data.currentValue ?? 0;
      const returnPercent = data.returnPercent ?? 0;
      const dailyPL = data.dailyPL ?? 0;
      const dailyChangePercent = data.dailyChangePercent ?? 0;
      const positions = data.positions ?? 0;
      const positionsChange = data.positionsChange ?? 0;
      const cash = data.cash ?? 0;
      const cashChangePercent = data.cashChangePercent ?? 0;

      const benchmarkReturn = data.benchmarkReturn ?? 0;
      const alpha = data.alpha ?? 0;
      const sharpeRatio = data.sharpeRatio ?? "0.00";
      const maxDrawdown = data.maxDrawdown ?? 0;
      const volatility = data.volatility ?? 0;

      setPortfolioStats([
        { label: 'Current Value', value: `₹${currentValue}`, change: `${returnPercent}%`, positive: returnPercent >= 0 },
        { label: 'Daily P&L', value: `₹${dailyPL}`, change: `${dailyChangePercent}%`, positive: dailyChangePercent >= 0 },
        { label: 'Active Positions', value: `${positions}`, change: `+${positionsChange}`, positive: true },
        { label: 'Cash Available', value: `₹${cash}`, change: `${cashChangePercent}%`, positive: cashChangePercent >= 0 }
      ]);

      setMetrics([
        { label: 'Total Return', value: `${returnPercent}%`, color: 'green' },
        { label: 'Benchmark Return', value: `${benchmarkReturn}%`, color: 'blue' },
        { label: 'Alpha', value: `${alpha}%`, color: 'purple' },
        { label: 'Max Drawdown', value: `${maxDrawdown}%`, color: 'red' },
        { label: 'Sharpe Ratio', value: sharpeRatio, color: 'goldenrod' },
        { label: 'Volatility', value: `${volatility}%`, color: 'orange' }
      ]);

      setGraphData(Array.isArray(data.graph) ? data.graph : []);
    } catch (err) {
      console.error('Error loading portfolio data:', err);
    }
  };

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
          <AreaChart data={graphData} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
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
        {metrics.map((metric, i) => (
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
