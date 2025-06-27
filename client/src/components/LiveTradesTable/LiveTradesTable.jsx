import React from 'react';
import './LiveTradesTable.css';

const LiveTradesTable = () => {
  const trades = [
    {
      time: '14:32:15',
      asset: 'RELIANCE',
      action: 'BUY',
      confidence: 'High',
      price: '₹2,456.70',
      reason: 'Strong earnings beat + institutional buying',
      holdingPeriod: '2-3 days',
      taxCategory: 'STCG'
    },
    {
      time: '14:28:43',
      asset: 'HDFC BANK',
      action: 'SELL',
      confidence: 'Medium',
      price: '₹1,734.20',
      reason: 'Technical resistance at 1750 level',
      holdingPeriod: '1 day',
      taxCategory: 'STCG'
    },
    {
      time: '14:15:22',
      asset: 'TCS',
      action: 'BUY',
      confidence: 'High',
      price: '₹3,890.15',
      reason: 'Positive sector sentiment + AI narrative',
      holdingPeriod: '1 week',
      taxCategory: 'STCG'
    }
  ];

  const getActionClass = (action) => {
    return action === 'BUY' ? 'text-green' : 'text-red';
  };

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
            {trades.map((trade, index) => (
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
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LiveTradesTable;
