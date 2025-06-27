import React from 'react';
import './PerformanceCharts.css'; // Import custom CSS
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';

const PerformanceCharts = () => {
  const equityData = [
    { date: '06-17', value: 100000 },
    { date: '06-18', value: 102500 },
    { date: '06-19', value: 101800 },
    { date: '06-20', value: 105200 },
    { date: '06-21', value: 107800 },
    { date: '06-22', value: 110100 },
    { date: '06-23', value: 112400 }
  ];

  const pnlData = [
    { date: '06-17', pnl: 2500 },
    { date: '06-18', pnl: -700 },
    { date: '06-19', pnl: 3400 },
    { date: '06-20', pnl: 2600 },
    { date: '06-21', pnl: 2300 },
    { date: '06-22', pnl: 1800 },
    { date: '06-23', pnl: 2300 }
  ];

  const taxData = [
    { name: 'STCG', value: 18234, color: '#4ade80' },
    { name: 'LTCG', value: 6333, color: '#60a5fa' },
    { name: 'Speculative', value: 0, color: '#f87171' }
  ];

  return (
    <div className="charts-container">
      {/* Portfolio Value */}
      <div className="chart-card">
        <div className="card-header">Portfolio Value</div>
        <div className="card-content">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={equityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Line 
                type="monotone"
                dataKey="value"
                stroke="#4ade80"
                strokeWidth={2}
                dot={{ fill: '#4ade80', strokeWidth: 0, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily P&L */}
      <div className="chart-card">
        <div className="card-header">Daily P&L</div>
        <div className="card-content">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={pnlData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Bar dataKey="pnl" fill="#4ade80" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Tax Breakdown */}
      <div className="chart-card">
        <div className="card-header">Tax Breakdown</div>
        <div className="card-content">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={taxData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                dataKey="value"
              >
                {taxData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="tax-legend">
            {taxData.map((item, index) => (
              <div key={index} className="legend-row">
                <div className="legend-label">
                  <span className="legend-dot" style={{ backgroundColor: item.color }}></span>
                  <span>{item.name}</span>
                </div>
                <span>₹{item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceCharts;
