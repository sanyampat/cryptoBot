from flask import Flask, jsonify
from flask_cors import CORS
from binance.client import Client
from dotenv import load_dotenv
import requests
import os
import time
import pandas as pd
from datetime import datetime, timedelta
import json

# Load environment
load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Setup Flask
app = Flask(__name__)
CORS(app)

# Setup Binance Client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# USD to INR conversion
def get_usdt_to_inr_rate():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTINR")
        return float(r.json().get("price", 83.0))
    except:
        return 83.0

@app.route("/api/balance", methods=["GET"])
def get_balance():
    try:
        account = client.get_account()
        balances = account['balances']
        tickers = {item['symbol']: float(item['price']) for item in client.get_all_tickers()}
        usdt_inr = get_usdt_to_inr_rate()

        portfolio = []
        total_usdt = 0

        for b in balances:
            asset = b['asset']
            free = float(b['free'])
            locked = float(b['locked'])
            total = free + locked
            if total == 0:
                continue

            price_usdt = 1 if asset == "USDT" else tickers.get(asset + "USDT", 0)
            value_usdt = total * price_usdt
            total_usdt += value_usdt

            portfolio.append({
                "asset": asset,
                "free": free,
                "locked": locked,
                "total": total,
                "price_usdt": round(price_usdt, 4),
                "value_usdt": round(value_usdt, 2),
                "value_inr": round(value_usdt * usdt_inr, 2)
            })

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_usdt": round(total_usdt, 2),
            "total_inr": round(total_usdt * usdt_inr, 2)
        }

        import csv
        log_file = "portfolio_history.csv"
        file_exists = os.path.isfile(log_file)
        with open(log_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)

        return jsonify({
            "portfolio": portfolio,
            "total_value_usdt": log_entry["total_usdt"],
            "total_value_inr": log_entry["total_inr"],
            "usdt_inr_rate": round(usdt_inr, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/portfolio-history", methods=["GET"])
def get_portfolio_history():
    try:
        df = pd.read_csv("portfolio_history.csv")
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/portfolio-summary", methods=["GET"])
def get_portfolio_summary():
    try:
        trade_file = "multi_coin_trades.csv"
        if not os.path.exists(trade_file):
            return jsonify({
                "bot_status": "OFFLINE",
                "last_trade": None,
                "win_rate": 0,
                "total_pnl": 0,
                "tax_split": {"short_term": 0, "long_term": 0}
            })

        df = pd.read_csv(trade_file)
        df['date'] = pd.to_datetime(df['date'])
        last_trade_time = df['date'].max().strftime('%H:%M:%S')
        df_recent = df[df['date'] >= datetime.now() - timedelta(days=7)]
        df_sells = df_recent[df_recent['type'] == 'SELL']

        wins = df_sells[df_sells['pnl'] > 0].shape[0]
        total = df_sells.shape[0]
        win_rate = (wins / total) * 100 if total > 0 else 0

        total_pnl_usdt = df_sells['pnl'].sum() * 1000
        total_pnl_inr = round(total_pnl_usdt * 83, 2)

        tax_split = {
            "short_term": round(total_pnl_inr * 0.8, 2),
            "long_term": round(total_pnl_inr * 0.2, 2)
        }

        return jsonify({
            "bot_status": "LIVE",
            "last_trade": last_trade_time,
            "win_rate": round(win_rate, 2),
            "total_pnl": total_pnl_inr,
            "tax_split": tax_split
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/news-sentiment")
def news_sentiment_api():
    try:
        import pandas as pd
        df = pd.read_csv("news_cache.csv")
        if "sentiment" not in df.columns:
            raise ValueError("CSV is missing 'sentiment' column")
        df = df[df["sentiment"].notna()]
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/live-signals", methods=["GET"])
def get_live_signals():
    try:
        signals = []
        if not os.path.exists("live_signals.log"):
            return jsonify(signals)

        with open("live_signals.log", "r") as f:
            lines = f.readlines()[-100:]

        for line in reversed(lines):
            try:
                log = json.loads(line)
                score = float(log["score"])
                decision = log.get("decision", "NO")
                reason = log.get("reason", "")

                if decision != "YES":
                    continue

                # Score → confidence
                if score >= 0.75:
                    confidence = "High"
                elif score >= 0.6:
                    confidence = "Medium"
                else:
                    confidence = "Low"

                signals.append({
                    "asset": log["symbol"],
                    "action": log["signal"],
                    "confidence": confidence,
                    "trigger": reason
                })

            except Exception as e:
                continue

            if len(signals) >= 10:
                break

        return jsonify(signals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/live-trades", methods=["GET"])
def get_live_trades():
    try:
        with open("live_trades.json", "r") as f:
            trades = json.load(f)
        # ✅ Ensure output is always a list
        if isinstance(trades, dict):
            trades = [trades]
        return jsonify({"trades": trades})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5002)
