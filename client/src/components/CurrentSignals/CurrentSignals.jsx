import React, { useEffect, useState } from 'react';
import './CurrentSignals.css';

const CurrentSignals = () => {
  const [signals, setSignals] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5002/api/live-signals")
      .then(res => res.json())
      .then(data => {
        const topFive = data.slice(0, 5);
        setSignals(topFive);
      })
      .catch(err => {
        console.error("Error fetching signals:", err);
      });
  }, []);

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
        {signals.length === 0 ? (
          <p>Loading or no signals available.</p>
        ) : (
          signals.map((signal, index) => (
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
          ))
        )}
      </div>
    </div>
  );
};

export default CurrentSignals;
