import csv
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
CRYPTOPANIC_KEY = os.getenv("CRYPTOPANIC_KEY")
DEESEEK_URL = "http://localhost:11434/api/generate"
CSV_FILE = "news_cache.csv"

def fetch_newsapi(limit=5):
    url = f"https://newsapi.org/v2/everything?q=crypto&language=en&sortBy=publishedAt&pageSize={limit}&apiKey={NEWSAPI_KEY}"
    res = requests.get(url).json()
    articles = res.get("articles", [])[:limit]
    return [{
        "title": a["title"],
        "source": a["source"]["name"],
        "timestamp": a["publishedAt"],
        "sentiment": ""
    } for a in articles]

def fetch_cryptopanic(limit=5):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_KEY}&public=true"
    res = requests.get(url).json()
    results = res.get("results", [])[:limit]
    return [{
        "title": r["title"],
        "source": r.get("source", {}).get("title", "CryptoPanic"),
        "timestamp": r["published_at"],
        "sentiment": ""
    } for r in results]

def classify_sentiment(title):
    prompt = f"You are a crypto news sentiment analyzer.\nHeadline: \"{title}\"\n\nClassify the sentiment as Positive, Negative, or Neutral and briefly explain why."
    try:
        response = requests.post(
            DEESEEK_URL,
            json={"model": "deepseek-local", "prompt": prompt, "stream": False}
        )
        text = response.json().get("response", "").lower()
        if "positive" in text:
            return "Positive"
        elif "negative" in text:
            return "Negative"
        else:
            return "Neutral"
    except:
        return "Neutral"

def load_existing_titles():
    if not os.path.exists(CSV_FILE):
        return set()
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        return {row['title'] for row in csv.DictReader(f)}

def save_news_to_csv(news_list):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "source", "timestamp", "sentiment"])
        if not file_exists:
            writer.writeheader()
        for item in news_list:
            writer.writerow(item)

def run():
    print(f"[{datetime.now()}] Fetching news...")
    existing_titles = load_existing_titles()

    newsapi_data = fetch_newsapi(limit=5)
    cryptopanic_data = fetch_cryptopanic(limit=5)

    all_news = newsapi_data + cryptopanic_data
    new_items = [n for n in all_news if n['title'] not in existing_titles]

    if new_items:
        print(f"Classifying and saving {len(new_items)} new headlines...")
        for item in new_items:
            item["sentiment"] = classify_sentiment(item["title"])
            time.sleep(1)
        save_news_to_csv(new_items)
        print("Done.")
    else:
        print("No new headlines found.")

if __name__ == "__main__":
    run()
