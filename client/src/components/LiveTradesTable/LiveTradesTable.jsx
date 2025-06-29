import React, { useEffect, useState } from 'react';
import './LiveTradesTable.css';

const LiveTradesTable = () => {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    fetchLiveTrades(); // initial load
    const interval = setInterval(fetchLiveTrades, 5000); // refresh every 5 sec
    return () => clearInterval(interval); // cleanup
  }, []);

  const fetchLiveTrades = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/live-trades');
      const data = await response.json();
      console.log("✅ Fetched live trades:", data);
      // Ensure trades is always an array
      setTrades(Array.isArray(data.trades) ? data.trades : []);
    } catch (err) {
      console.error('❌ Error fetching trades:', err);
      setTrades([]); // prevent crash if fetch fails
    }
  };

  const getActionClass = (action) => (action === 'BUY' ? 'text-green' : 'text-red');
  const getConfidenceClass = (confidence) => {
    switch (confidence) {
      case 'High': return 'text-green';
      case 'Medium': return 'text-yellow';
      case 'Low': return 'text-red';
      default: return 'text-white';
    }
  };

  return (
    <div className="live-trades-card">
      <div className="live-trades-title">Live Trades</div>
      <div className="live-trades-table-wrapper">
        <table className="live-trades-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Asset</th>
              <th>Action</th>
              <th>Confidence</th>
              <th>Price</th>
              <th>Reason</th>
              <th>Holding</th>
              <th>Tax</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center' }}>No live trades yet.</td>
              </tr>
            ) : (
              trades.map((trade, index) => (
                <tr key={index}>
                  <td>{trade.time}</td>
                  <td className="bold">{trade.asset}</td>
                  <td className={getActionClass(trade.action)}>{trade.action}</td>
                  <td className={getConfidenceClass(trade.confidence)}>{trade.confidence}</td>
                  <td>{trade.price}</td>
                  <td className="truncate" title={trade.reason}>{trade.reason}</td>
                  <td>{trade.holdingPeriod}</td>
                  <td>{trade.taxCategory}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LiveTradesTable;
