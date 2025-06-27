import React from 'react';
import './NewsFeed.css';

const newsItems = [
  {
    title: "Asian Paints sees Rs 7,700 crore block deal",
    source: "Economic Times",
    time: "2 hours ago",
    sentiment: "Positive"
  },
  {
    title: "Axis Bank barred from Odisha govt funds",
    source: "New Indian Express",
    time: "5 hours ago",
    sentiment: "Negative"
  },
  {
    title: "Reliance gains 100% in 3 months amid bullish momentum",
    source: "Indian Express",
    time: "1 day ago",
    sentiment: "Positive"
  },
  {
    title: "Birla files antitrust case against Asian Paints",
    source: "Reuters",
    time: "1 day ago",
    sentiment: "Negative"
  }
];

const getSentimentColor = (sentiment) => {
  switch (sentiment) {
    case "Positive": return "positive";
    case "Negative": return "negative";
    default: return "neutral";
  }
};

const NewsFeed = () => {
  return (
    <div className="news-feed-container">
      <div className="news-header">Latest Market News</div>
      <ul className="news-list">
        {newsItems.map((news, index) => (
          <li key={index} className="news-item">
            <div className="news-title">{news.title}</div>
            <div className="news-meta">
              <span className="source">{news.source}</span>
              <span className={`sentiment ${getSentimentColor(news.sentiment)}`}>{news.sentiment}</span>
              <span className="time">{news.time}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NewsFeed;
