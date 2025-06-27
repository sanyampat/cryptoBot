import React from 'react';
import './CurrentSignals.css'; // Link to your CSS file

const CurrentSignals = () => {
  const signals = [
    {
      asset: 'INFY',
      action: 'BUY',
      confidence: 'High',
      trigger: 'Golden cross formation + sector rotation'
    },
    {
      asset: 'ICICI BANK',
      action: 'SELL',
      confidence: 'Medium',
      trigger: 'Overbought RSI + profit booking'
    },
    {
      asset: 'WIPRO',
      action: 'BUY',
      confidence: 'Medium',
      trigger: 'Earnings surprise expected'
    },
    {
      asset: 'AXIS BANK',
      action: 'HOLD',
      confidence: 'Low',
      trigger: 'Mixed technical signals'
    }
  ];

  const getActionClass = (action) => {
    switch (action) {
      case 'BUY': return 'action buy';
      case 'SELL': return 'action sell';
      case 'HOLD': return 'action hold';
      default: return 'action';
    }
  };

  const getConfidenceClass = (confidence) => {
    switch (confidence) {
      case 'High': return 'confidence high';
      case 'Medium': return 'confidence medium';
      case 'Low': return 'confidence low';
      default: return 'confidence';
    }
  };

  return (
    <div className="card signal-card">
      <h2 className="card-title">Current Signals</h2>
      <div className="signals-list">
        {signals.map((signal, index) => (
          <div className="signal-box" key={index}>
            <div className="signal-header">
              <span className="asset">{signal.asset}</span>
              <span className={getActionClass(signal.action)}>{signal.action}</span>
            </div>
            <div className="signal-detail">
              <span className="label">Confidence:</span>
              <span className={getConfidenceClass(signal.confidence)}>{signal.confidence}</span>
            </div>
            <div className="trigger">
              <span className="label">Trigger: </span>{signal.trigger}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CurrentSignals;
