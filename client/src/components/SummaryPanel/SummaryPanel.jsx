import React, { useEffect, useState } from 'react';
import './SummaryPanel.css';

const SummaryPanel = ({ isLiveMode }) => {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5002/api/portfolio-summary")
      .then((res) => res.json())
      .then((data) => setSummary(data));
  }, []);

  return (
    <div className="summary-card">
      <div className="summary-header">Portfolio Summary</div>

      <div className="summary-grid">
        <div className="summary-box center">
          <div className="summary-label">Bot Status</div>
          <div className={`summary-value ${isLiveMode ? 'green' : 'yellow'}`}>
            {isLiveMode ? 'LIVE' : 'PAPER'}
          </div>
        </div>

        <div className="summary-box center">
          <div className="summary-label">Last Trade</div>
          <div className="summary-value">
            {summary ? summary.last_trade : '—'}
          </div>
        </div>

        <div className="summary-box center">
          <div className="summary-label">Win Rate (7d)</div>
          <div className="summary-value green">
            {summary ? `${summary.win_rate}%` : '—'}
          </div>
        </div>

        <div className="summary-box center">
          <div className="summary-label">Total P&L</div>
          <div className={`summary-value ${summary?.total_pnl >= 0 ? 'green' : 'red'}`}>
            {summary ? `₹${summary.total_pnl.toLocaleString()}` : '—'}
          </div>
        </div>
      </div>

      <div className="tax-section">
        <div className="summary-label mb">Tax Split</div>
        <div className="tax-grid">
          <div className="tax-box">
            <div className="summary-label small">STCG</div>
            <div className="summary-value">
              ₹{summary?.tax_split?.short_term?.toLocaleString() || 0}
            </div>
          </div>
          <div className="tax-box">
            <div className="summary-label small">LTCG</div>
            <div className="summary-value">
              ₹{summary?.tax_split?.long_term?.toLocaleString() || 0}
            </div>
          </div>
          <div className="tax-box">
            <div className="summary-label small">Speculative</div>
            <div className="summary-value">₹0</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryPanel;
