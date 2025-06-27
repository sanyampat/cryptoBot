import React from 'react';
import './SummaryPanel.css';

const SummaryPanel = ({ isLiveMode }) => {
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
          <div className="summary-value">14:32:15</div>
        </div>
        <div className="summary-box center">
          <div className="summary-label">Win Rate (7d)</div>
          <div className="summary-value green">73.2%</div>
        </div>
        <div className="summary-box center">
          <div className="summary-label">Total P&L</div>
          <div className="summary-value green">+₹24,567</div>
        </div>
      </div>

      <div className="tax-section">
        <div className="summary-label mb">Tax Split</div>
        <div className="tax-grid">
          <div className="tax-box">
            <div className="summary-label small">STCG</div>
            <div className="summary-value">₹18,234</div>
          </div>
          <div className="tax-box">
            <div className="summary-label small">LTCG</div>
            <div className="summary-value">₹6,333</div>
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
