import pandas as pd
import numpy as np
import ta
import joblib
from binance.client import Client
from dotenv import load_dotenv
import os

# Load Binance API keys
load_dotenv()
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

# Your crypto universe
CRYPTO_UNIVERSE = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
MODEL_DIR = "models"

def get_historical_klines(symbol, interval="1h", lookback="7 day ago UTC"):
    try:
        klines = client.get_historical_klines(symbol, interval, lookback)
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df
    except Exception as e:
        print(f"❌ Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()

def generate_crypto_features(df):
    df["Returns"] = df["close"].pct_change()
    df["Volatility"] = df["Returns"].rolling(5).std()
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["EMA_10"] = ta.trend.EMAIndicator(df["close"], window=10).ema_indicator()
    df["EMA_50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    df["MACD"] = ta.trend.MACD(df["close"]).macd_diff()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    return df

def get_crypto_ml_signals():
    signals = []
    for symbol in CRYPTO_UNIVERSE:
        model_path = os.path.join(MODEL_DIR, f"{symbol}.joblib")
        if not os.path.exists(model_path):
            print(f"⚠️ No model for {symbol}, skipping.")
            continue

        df = get_historical_klines(symbol)
        if df.empty or len(df) < 60:
            continue

        df = generate_crypto_features(df)
        features = ['Returns', 'Volatility', 'RSI', 'EMA_10', 'EMA_50', 'MACD']
        X_latest = df[features].tail(1)

        try:
            bots = joblib.load(model_path)
            bot1 = bots['bot1']
            bot2 = bots['bot2']
            pred1 = bot1.predict_proba(X_latest)[0]
            pred2 = bot2.predict_proba(X_latest)[0]

            # Logic: 2-agree high confidence
            if pred1[2] > 0.5 and pred2[2] > 0.5:
                signal = "Buy"
            elif pred1[0] > 0.5 and pred2[0] > 0.5:
                signal = "Sell"
            else:
                signal = "Hold"

            signals.append({
                "symbol": symbol,
                "price": float(df["close"].iloc[-1]),
                "signal": signal
            })
        except Exception as e:
            print(f"❌ Prediction error for {symbol}: {e}")
            continue

    return signals
if __name__ == "__main__":
    crypto_signals = get_crypto_ml_signals()
    for s in crypto_signals:
        print(f"{s['symbol']} ➤ {s['signal']} at ${s['price']}")
