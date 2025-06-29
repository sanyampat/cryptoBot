import React, { useEffect, useState } from 'react';
import './NewsFeed.css';

const getSentimentColor = (sentiment) => {
  switch (sentiment.toLowerCase()) {
    case "positive": return "positive";
    case "negative": return "negative";
    default: return "neutral";
  }
};

const getTimeAgo = (timestamp) => {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
  const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

  if (diffHrs >= 24) return `${Math.floor(diffHrs / 24)} day${diffHrs >= 48 ? 's' : ''} ago`;
  if (diffHrs > 0) return `${diffHrs} hour${diffHrs > 1 ? 's' : ''} ago`;
  return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
};

const NewsFeed = () => {
  const [newsItems, setNewsItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchNews = () => {
    fetch("http://localhost:5002/api/news-sentiment")
      .then(res => res.json())
      .then(data => {
        setNewsItems(data);
        setLoading(false);
        setError(false);
      })
      .catch(err => {
        console.error("❌ Failed to fetch news:", err);
        setError(true);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 5 * 60 * 1000); // refresh every 5 min
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="news-feed-container">
      <h2 className="news-header">Latest Market News</h2>

      {loading && <div className="loading-text">Loading news...</div>}
      {error && <div className="error-text">Failed to load news. Please try again later.</div>}

      {!loading && !error && (
        <ul className="news-list">
          {newsItems.slice(0, 15).map((news, index) => (
            <li key={index} className="news-item">
              <div className="news-title">{news.title.length > 150 ? news.title.slice(0, 147) + '...' : news.title}</div>
              <div className="news-meta">
                <span className="source">{news.source}</span>
                <span className={`sentiment ${getSentimentColor(news.sentiment)}`}>
                  {news.sentiment}
                </span>
                <span className="time">{getTimeAgo(news.timestamp)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};

export default NewsFeed;
