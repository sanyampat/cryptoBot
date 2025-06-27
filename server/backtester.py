# crypto_live_paper_trader.py
# Live 1-min paper trader with unified wallet using pretrained ML models

import joblib
import pandas as pd
import numpy as np
import ta
import time
from datetime import datetime, timezone
from binance.client import Client
from dotenv import load_dotenv
import os

# === Load Binance API ===
load_dotenv()
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

# === CONFIG ===
CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
INTERVAL = Client.KLINE_INTERVAL_1MINUTE
INITIAL_WALLET = 1000.0
MODEL_DIR = "models"

wallet = INITIAL_WALLET
in_position = False
position = {}
trade_log = []

# === Fetch latest data (live) ===
def fetch_live_data(symbol, limit=100):
    klines = client.get_klines(symbol=symbol, interval=INTERVAL, limit=limit)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume",
                                       "ct", "qav", "n", "tbv", "tqv", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

# === Add Features ===
def add_features(df):
    df["Returns"] = df["close"].pct_change()
    df["Volatility"] = df["Returns"].rolling(5).std()
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["EMA_10"] = ta.trend.EMAIndicator(df["close"], window=10).ema_indicator()
    df["EMA_50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    df["MACD"] = ta.trend.MACD(df["close"]).macd_diff()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    return df

# === Live Paper Trading Loop ===
def run_live_paper_trading():
    global wallet, in_position, position
    print(f"📡 Starting LIVE 1-min paper trader with ${INITIAL_WALLET:.2f}...")
    models = {}
    for symbol in CRYPTO_SYMBOLS:
        model_path = os.path.join(MODEL_DIR, f"{symbol}.joblib")
        if os.path.exists(model_path):
            models[symbol] = joblib.load(model_path)
        else:
            print(f"⚠️ Skipping {symbol}, no model found.")

    while True:
        best_candidate = None
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for symbol in models:
            df = fetch_live_data(symbol)
            df = add_features(df)
            if df.empty: continue

            latest = df.tail(1)[["Returns", "Volatility", "RSI", "EMA_10", "EMA_50", "MACD"]]
            p1 = models[symbol]['bot1'].predict_proba(latest)[0]
            p2 = models[symbol]['bot2'].predict_proba(latest)[0]

            if p1[2] > 0.5 and p2[2] > 0.5:
                best_candidate = (symbol, df["close"].iloc[-1])

        if in_position:
            # Exit logic
            symbol = position['symbol']
            exit_price = fetch_live_data(symbol).iloc[-1]['close']
            ret = (exit_price - position['entry_price']) / position['entry_price']
            wallet *= (1 + ret)
            trade_log.append({
                "timestamp": timestamp,
                "symbol": symbol,
                "signal": "EXIT",
                "entry_price": position['entry_price'],
                "exit_price": exit_price,
                "return": ret,
                "wallet": wallet
            })
            print(f"💼 EXIT {symbol} @ {exit_price:.2f} | Wallet: ${wallet:.2f}")
            in_position = False
            position = {}

        elif best_candidate:
            symbol, price = best_candidate
            in_position = True
            position = {"symbol": symbol, "entry_price": price}
            trade_log.append({
                "timestamp": timestamp,
                "symbol": symbol,
                "signal": "ENTRY",
                "entry_price": price,
                "wallet": wallet
            })
            print(f"🚀 ENTRY {symbol} @ {price:.2f} | Wallet: ${wallet:.2f}")

        pd.DataFrame(trade_log).to_csv("live_trades.csv", index=False)
        print("🕒 Waiting for next 1-min candle...")
        time.sleep(60)

if __name__ == "__main__":
    run_live_paper_trading()
