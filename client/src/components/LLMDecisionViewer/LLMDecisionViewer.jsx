import React, { useState } from 'react';
import './LLMDecisionViewer.css';

const LLMDecisionViewer = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const llmDecision = {
    timestamp: "2024-06-23T14:32:15.123Z",
    model: "DeepSeek v2",
    decision: {
      action: "BUY",
      asset: "RELIANCE",
      confidence: 0.87,
      quantity: 100,
      reasoning: {
        technical_analysis: {
          rsi: 45.2,
          macd: "bullish_crossover",
          support_level: 2420,
          resistance_level: 2480
        },
        fundamental_analysis: {
          pe_ratio: 15.2,
          earnings_growth: "positive",
          sector_sentiment: "bullish"
        },
        news_sentiment: {
          score: 0.72,
          headlines_analyzed: 15,
          key_themes: ["earnings_beat", "institutional_buying"]
        }
      },
      risk_assessment: {
        volatility: "medium",
        max_loss: "2.5%",
        stop_loss: 2395
      },
      holding_period: "2-3 days",
      tax_category: "STCG"
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>Latest LLM Decision</h3>
        <button className="toggle-btn" onClick={() => setIsExpanded(!isExpanded)}>
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      <div className="card-content">
        <div className="decision-box">
          <div className="meta">
            Model: {llmDecision.model} | Time: {new Date(llmDecision.timestamp).toLocaleTimeString()}
          </div>
          <pre className={`json-display ${isExpanded ? 'expanded' : 'collapsed'}`}>
            {JSON.stringify(llmDecision.decision, null, 2)}
          </pre>
        </div>

        <div className="info-grid">
          <div className="info-tile">
            <div className="label">Confidence</div>
            <div className="value green">{(llmDecision.decision.confidence * 100).toFixed(1)}%</div>
          </div>
          <div className="info-tile">
            <div className="label">Risk Level</div>
            <div className="value yellow">{llmDecision.decision.risk_assessment.volatility}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMDecisionViewer;
