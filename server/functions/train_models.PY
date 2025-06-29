import os
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from ta import add_all_ta_features
from lightgbm import LGBMClassifier
from binance.client import Client

# -------------------- CONFIG --------------------
load_dotenv()
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

symbols = [
    'BTCUSDT',  # Bitcoin
    'ETHUSDT',  # Ethereum
    'SOLUSDT',  # Solana
    'AVAXUSDT', # Avalanche
    'DOGEUSDT', # Dogecoin (meme)
    'SHIBUSDT', # Shiba Inu (meme)
    'PEPEUSDT', # PEPE (meme)
    'FLOKIUSDT',# Floki (meme)
    'MATICUSDT',# Polygon
    'XRPUSDT',  # Ripple
    'LTCUSDT',  # Litecoin
    'BNBUSDT',  # Binance Coin
]

features = [
    'momentum_rsi',
    'trend_macd',
    'trend_ema_fast',
    'volume_sma_em',
    'trend_adx',
    'volatility_bbm',  # Bollinger Band middle
    'trend_ichimoku_a',  # Ichimoku cloud A
    'trend_psar_up',     # Parabolic SAR
    'momentum_stoch_rsi'
]

split_date = "2022-01-01"
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# -------------------- HELPERS --------------------

def fetch_binance_data(symbol, interval="1d", start_str="1 Jan, 2020"):
    klines = client.get_historical_klines(symbol, interval, start_str)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

def preprocess(df):
    df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
    df['future_return'] = df['close'].shift(-3) / df['close'] - 1
    df['target'] = (df['future_return'] > 0.01).astype(int)
    df = df[features + ['target']].dropna()
    return df

def train_lgbm(X, y):
    model = LGBMClassifier()
    model.fit(X, y)
    return model

def train_lstm(X, y):
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    X_seq = np.reshape(X_scaled, (X_scaled.shape[0], 1, X_scaled.shape[1]))

    model = Sequential()
    model.add(LSTM(64, input_shape=(1, X.shape[1])))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_seq, y, epochs=5, batch_size=16, verbose=1)

    return model, scaler

# -------------------- MAIN --------------------

# ... [same imports and config above]

# -------------------- MAIN --------------------

for symbol in symbols:
    print(f"\n🔄 Training models for {symbol}...")
    try:
        df = fetch_binance_data(symbol)
        df = preprocess(df)
    except Exception as e:
        print(f"❌ Error fetching or preprocessing {symbol}: {e}")
        continue

    # Try to get data before split_date
    train_df = df[df.index < split_date]

    if len(train_df) < 100:
        print(f"⚠️ Not enough data before {split_date}, using oldest {min(300, len(df))} rows instead.")
        train_df = df.head(min(300, len(df)))

    if len(train_df) < 50:
        print(f"❌ Skipping {symbol} — Insufficient data ({len(train_df)} rows)")
        continue

    try:
        X = train_df[features]
        y = train_df['target']

        # Train & Save LGBM
        lgb_model = train_lgbm(X, y)
        joblib.dump(lgb_model, f"{model_dir}/{symbol}_lgb.pkl")

        # Train & Save LSTM + Scaler
        lstm_model, scaler = train_lstm(X, y)
        lstm_model.save(f"{model_dir}/{symbol}_lstm.h5")
        joblib.dump(scaler, f"{model_dir}/{symbol}_scaler.pkl")

        print(f"✅ Saved models for {symbol} in '{model_dir}/'")
    except Exception as e:
        print(f"❌ Training failed for {symbol}: {e}")
