# crypto_auto_trader.py
# Full autonomous crypto trader pipeline

import os
import time
import joblib
import pandas as pd
import numpy as np
import ta
from binance.client import Client
from dotenv import load_dotenv
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from datetime import datetime

# === SETUP ===
load_dotenv()
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# === 1. Auto-Select Top Coins ===
def select_top_cryptos(limit=5, min_volume=100_000_000):
    tickers = client.get_ticker()
    df = pd.DataFrame(tickers)
    df["quoteVolume"] = df["quoteVolume"].astype(float)
    df = df[df["symbol"].str.endswith("USDT")]
    df = df[df["quoteVolume"] > min_volume]
    top = df.sort_values("quoteVolume", ascending=False).head(limit)
    return top["symbol"].tolist()

# === 2. Trainer ===
def fetch_data(symbol, interval="1h", lookback="365 days ago UTC"):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume",
                                       "close_time", "qav", "trades", "tb_base", "tb_quote", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

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

def label_data(df, horizon=5, threshold=0.01):
    future_return = df["close"].shift(-horizon) / df["close"] - 1
    df["Target"] = 0
    df.loc[future_return > threshold, "Target"] = 1
    df.loc[future_return < -threshold, "Target"] = -1
    df["Target_Mapped"] = df["Target"].map({-1: 0, 0: 1, 1: 2})
    return df

def train_models(symbol, df):
    features = ["Returns", "Volatility", "RSI", "EMA_10", "EMA_50", "MACD"]
    X = df[features]
    y = df["Target_Mapped"]
    if len(X) < 100 or y.nunique() < 3:
        print(f"⚠️ Skipping {symbol} — Not enough data or labels")
        return
    X_res, y_res = SMOTE(random_state=42).fit_resample(X, y)
    bot1 = LGBMClassifier(objective='multiclass', num_class=3, random_state=42)
    bot2 = XGBClassifier(objective='multi:softprob', num_class=3,
                         use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    bot1.fit(X_res, y_res)
    bot2.fit(X_res, y_res)
    joblib.dump({"bot1": bot1, "bot2": bot2}, f"{MODEL_DIR}/{symbol}.joblib")
    print(f"✅ Trained and saved model: {symbol}")

# === 3. Live Signal Generator ===
def generate_live_signal(symbol):
    model_path = f"{MODEL_DIR}/{symbol}.joblib"
    if not os.path.exists(model_path): return None
    try:
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=100)
        df = pd.DataFrame(klines, columns=["t", "o", "h", "l", "c", "v", "ct", "qav", "n", "tbv", "tqv", "i"])
        df = df[["o", "h", "l", "c", "v"]].astype(float)
        df.columns = ["open", "high", "low", "close", "volume"]
        df = add_features(df)
        latest = df.tail(1)[["Returns", "Volatility", "RSI", "EMA_10", "EMA_50", "MACD"]]
        bots = joblib.load(model_path)
        p1 = bots['bot1'].predict_proba(latest)[0]
        p2 = bots['bot2'].predict_proba(latest)[0]
        if p1[2] > 0.5 and p2[2] > 0.5:
            return "Buy"
        elif p1[0] > 0.5 and p2[0] > 0.5:
            return "Sell"
        else:
            return "Hold"
    except Exception as e:
        print(f"❌ Signal error for {symbol}: {e}")
        return None

# === RUN ALL ===
def run_autonomous_pipeline():
    symbols = select_top_cryptos(limit=5)
    print(f"📊 Selected: {symbols}")
    for symbol in symbols:
        df = fetch_data(symbol)
        df = add_features(df)
        df = label_data(df)
        train_models(symbol, df)
    print("🚀 Running Live Signals")
    while True:
        print("\n🕒", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for symbol in symbols:
            signal = generate_live_signal(symbol)
            if signal:
                print(f"📈 {symbol} ➤ {signal}")
        time.sleep(300)  # check every 5 minutes

if __name__ == "__main__":
    run_autonomous_pipeline()
