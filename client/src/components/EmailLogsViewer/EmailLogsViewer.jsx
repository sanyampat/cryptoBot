import React, { useState } from 'react';
import './EmailLogsViewer.css';

const EmailLogsViewer = () => {
  const [selectedEmail, setSelectedEmail] = useState(null);

  const emailLogs = [
    {
      id: 1,
      timestamp: '2024-06-23 18:00:00',
      tradeCount: 5,
      subject: 'Daily Trading Summary - Jun 23',
      body: `Daily Trading Summary for June 23, 2024

Total Trades: 5
Win Rate: 80%
Net P&L: +₹4,567

Top Performers:
- RELIANCE: +₹2,345
- TCS: +₹1,890

Risk Metrics:
- Max Drawdown: 1.2%
- Sharpe Ratio: 2.34

Next Day Outlook:
- Bullish sentiment on IT sector
- Watch for RBI policy announcements`
    },
    {
      id: 2,
      timestamp: '2024-06-22 18:00:00',
      tradeCount: 3,
      subject: 'Daily Trading Summary - Jun 22',
      body: `Daily Trading Summary for June 22, 2024

Total Trades: 3
Win Rate: 66.7%
Net P&L: +₹2,234

Details available in the dashboard.`
    },
    {
      id: 3,
      timestamp: '2024-06-21 18:00:00',
      tradeCount: 7,
      subject: 'Daily Trading Summary - Jun 21',
      body: `Daily Trading Summary for June 21, 2024

Total Trades: 7
Win Rate: 71.4%
Net P&L: +₹3,456

Market was volatile due to global cues.`
    }
  ];

  return (
    <div className="email-card">
      <h2 className="email-title">Email Logs</h2>
      <div className="email-list">
        {emailLogs.map((email) => (
          <div key={email.id} className="email-entry">
            <div className="email-header">
              <div>
                <div className="subject">{email.subject}</div>
                <div className="timestamp">{email.timestamp}</div>
              </div>
              <div className="trades">{email.tradeCount} trades</div>
            </div>
            <button
              className="toggle-button"
              onClick={() =>
                setSelectedEmail(selectedEmail === email.id ? null : email.id)
              }
            >
              {selectedEmail === email.id ? 'Hide' : 'View'} Details
            </button>
            {selectedEmail === email.id && (
              <div className="email-body">
                <pre>{email.body}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmailLogsViewer;
