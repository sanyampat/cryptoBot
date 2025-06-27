import React, { useState } from 'react';
import './ControlPanel.css'; // Custom CSS

const ControlPanel = () => {
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [selectedModel, setSelectedModel] = useState('DeepSeek v1');
  const [emailSchedule, setEmailSchedule] = useState('18:00');

  const handleExportLogs = () => {
    console.log('Exporting logs to CSV...');
  };

  const handleManualEmail = () => {
    console.log('Triggering manual email summary...');
  };

  return (
    <div className="card">
      <h2 className="card-title">Control Panel</h2>

      {/* Trading Mode Toggle */}
      <div className="setting-row">
        <div>
          <div className="label">Trading Mode</div>
          <div className="sublabel">
            {isLiveMode ? 'Live trading enabled' : 'Paper trading mode'}
          </div>
        </div>
        <label className="switch">
          <input type="checkbox" checked={isLiveMode} onChange={(e) => setIsLiveMode(e.target.checked)} />
          <span className="slider" />
        </label>
      </div>

      {/* Model Selection */}
      <div className="setting-row">
        <label className="label">LLM Model</label>
        <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)} className="select">
          <option>DeepSeek v1</option>
          <option>DeepSeek v2</option>
          <option>Rule-Based Fallback</option>
        </select>
      </div>

      {/* Export & Email */}
      <button className="btn" onClick={handleExportLogs}>Export Logs to CSV</button>
      <button className="btn" onClick={handleManualEmail}>Send Email Summary</button>

      {/* Email Schedule */}
      <div className="setting-row">
        <label className="label">Email Schedule</label>
        <select value={emailSchedule} onChange={(e) => setEmailSchedule(e.target.value)} className="select">
          <option value="09:00">09:00 AM</option>
          <option value="15:30">03:30 PM (Market Close)</option>
          <option value="18:00">06:00 PM</option>
          <option value="21:00">09:00 PM</option>
        </select>
      </div>
    </div>
  );
};

export default ControlPanel;
