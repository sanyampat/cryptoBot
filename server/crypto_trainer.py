import pandas as pd
import numpy as np
import os, joblib
import ta
from binance.client import Client
from imblearn.over_sampling import SMOTE
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from dotenv import load_dotenv

# Load API keys
load_dotenv()
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

CRYPTO_UNIVERSE = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def fetch_data(symbol, interval="1h", lookback="365 days ago UTC"):
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
    df["Target_Mapped"] = df["Target"].map({-1: 0, 0: 1, 1: 2})  # For 3-class
    return df

def train_models(symbol, df):
    features = ["Returns", "Volatility", "RSI", "EMA_10", "EMA_50", "MACD"]
    X = df[features]
    y = df["Target_Mapped"]
    
    if len(X) < 100 or y.nunique() < 3:
        print(f"⚠️ Skipping {symbol} — Not enough data or label diversity")
        return

    X_resampled, y_resampled = SMOTE(random_state=42).fit_resample(X, y)

    bot1 = LGBMClassifier(objective='multiclass', num_class=3, random_state=42)
    bot2 = XGBClassifier(objective='multi:softprob', num_class=3,
                         use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    bot1.fit(X_resampled, y_resampled)
    bot2.fit(X_resampled, y_resampled)

    joblib.dump({"bot1": bot1, "bot2": bot2}, f"{MODEL_DIR}/{symbol}.joblib")
    print(f"✅ Saved model: {symbol}.joblib")

def main():
    for symbol in CRYPTO_UNIVERSE:
        try:
            print(f"📈 Training {symbol}...")
            df = fetch_data(symbol)
            df = add_features(df)
            df = label_data(df)
            train_models(symbol, df)
        except Exception as e:
            print(f"❌ Error training {symbol}: {e}")

if __name__ == "__main__":
    main()
