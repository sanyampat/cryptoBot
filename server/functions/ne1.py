import os
import time
import requests
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone
from binance.client import Client
from ta import add_all_ta_features
from sklearn.preprocessing import MinMaxScaler
from lightgbm import LGBMClassifier
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense

# -------------------- CONFIG --------------------

load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT']
split_date = "2022-01-01"
features = ['momentum_rsi', 'trend_macd', 'trend_ema_fast', 'volume_sma_em']

import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress TensorFlow logs
warnings.filterwarnings("ignore", category=FutureWarning)

# -------------------- HELPERS --------------------

def date_to_milliseconds(date_str):
    epoch = datetime.fromtimestamp(0, tz=timezone.utc)
    dt = datetime.strptime(date_str, "%d %b, %Y").replace(tzinfo=timezone.utc)
    return int((dt - epoch).total_seconds() * 1000.0)

def run_deepseek(prompt, model="deepseek-local"):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload)
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return "NO — DeepSeek failed"

def ask_deepseek_confirmation(coin, rsi, macd, ema_fast, volume_ema, price, signal_type="BUY"):
    prompt = f"""
You are a crypto trading assistant. The model has predicted a {signal_type} signal for {coin}.

Here are the technical indicators:
- RSI: {rsi:.2f}
- MACD: {macd:.4f}
- EMA Fast: {ema_fast:.2f}
- Volume SMA: {volume_ema:.2f}
- Price: {price:.2f}

Should we proceed with the {signal_type}?
Reply with 'YES' or 'NO' and a one-line reason.
"""
    return run_deepseek(prompt)

def fetch_binance_data(symbol, interval="1d", start_str="1 Jan, 2020", end_str=None):
    if end_str is None:
        end_str = datetime.today().strftime('%d %b, %Y')
    start_ts = date_to_milliseconds(start_str)
    end_ts = date_to_milliseconds(end_str)

    limit = 1000
    all_klines = []
    while True:
        klines = client.get_historical_klines(symbol, interval, start_ts, limit=limit)
        if not klines:
            break
        all_klines.extend(klines)
        last_ts = klines[-1][0]
        start_ts = last_ts + 1
        if last_ts >= end_ts:
            break
        time.sleep(0.1)

    df = pd.DataFrame(all_klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    print(f"📈 Loaded {len(df)} candles for {symbol}")
    return df

def preprocess(df):
    df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
    df['future_return'] = df['close'].shift(-3) / df['close'] - 1
    df['target'] = (df['future_return'] > 0.01).astype(int)
    needed_cols = list(set(features + ['future_return', 'target', 'close']))
    df = df[needed_cols].dropna()
    return df

def train_lgbm(train_df, features):
    X = train_df[features]
    y = train_df['target']
    model = LGBMClassifier()
    model.fit(X, y)
    return model

def train_lstm(train_df, features):
    X = train_df[features].values
    y = train_df['target'].values
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    X_lstm = np.reshape(X_scaled, (X_scaled.shape[0], 1, X_scaled.shape[1]))

    model = Sequential()
    model.add(LSTM(64, input_shape=(1, X_scaled.shape[1])))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_lstm, y, epochs=5, batch_size=16, verbose=0)
    return model, scaler

def ensemble_predict(row, lgb_model, lstm_model, scaler, features):
    # Convert row to DataFrame to retain feature names
    X_row_df = pd.DataFrame([row[features].values], columns=features)

    # LGBM prediction with feature names
    lgb_conf = lgb_model.predict_proba(X_row_df)[0][1]

    # LSTM needs scaled NumPy input
    X_scaled = scaler.transform(X_row_df)
    X_lstm = np.reshape(X_scaled, (1, 1, len(features)))
    lstm_conf = lstm_model.predict(X_lstm, verbose=0)[0][0]

    vote_score = 0.6 * lgb_conf + 0.4 * lstm_conf
    return int(vote_score > 0.6), vote_score


def get_daily_candidates(lgb_model, lstm_model, scaler, df, symbol, features):
    results = []
    for i in range(len(df)):
        row = df.iloc[i]
        if row.name < pd.to_datetime(split_date):
            continue
        try:
            pred, vote_score = ensemble_predict(row, lgb_model, lstm_model, scaler, features)
        except Exception as e:
            print(f"⚠️ Ensemble error on {symbol} {row.name.date()}: {e}")
            continue
        if vote_score < 0.6:
            continue
        confirm = ask_deepseek_confirmation(symbol, row.get('momentum_rsi', 0), row.get('trend_macd', 0),
                                            row.get('trend_ema_fast', 0), row.get('volume_sma_em', 0),
                                            row['close'])
        print(f"[DeepSeek] {symbol} {row.name.date()}: {confirm} | Score: {vote_score:.4f}")
        if "yes" in confirm.lower():
            score = row.get('momentum_rsi', 0) + row.get('trend_macd', 0) * 100
            results.append({
                "date": row.name,
                "symbol": symbol,
                "price": row['close'],
                "score": score,
                "confirmation": confirm
            })
    return results

def simulate_trading(best_trades, initial_usdt=1000):
    usdt = initial_usdt
    coin = 0
    portfolio = []

    for trade in best_trades.itertuples():
        if usdt > 0:
            amount = usdt / trade.price
            coin = amount
            usdt = 0
            portfolio.append({**trade._asdict(), "type": "BUY"})
        elif coin > 0:
            usdt = coin * trade.price
            pnl = (trade.price - portfolio[-1]['price']) / portfolio[-1]['price']
            coin = 0
            portfolio.append({**trade._asdict(), "type": "SELL", "pnl": pnl})

    final_value = usdt if coin == 0 else coin * best_trades.iloc[-1]['price']
    print(f"\n💰 Final Value: ${final_value:.2f}")
    print(f"📊 Return: {((final_value - initial_usdt) / initial_usdt) * 100:.2f}%")

    df_trades = pd.DataFrame(portfolio)
    df_trades.to_csv("multi_coin_trades.csv", index=False)
    return df_trades

# -------------------- MAIN --------------------

model_dir = "models"  # Make sure this contains your .joblib, .h5, and .pkl files

if __name__ == "__main__":
    all_candidates = []

    for symbol in symbols:
        print(f"\n🔍 Checking {symbol} using pretrained models...")

        try:
            df = fetch_binance_data(symbol)
            df = preprocess(df)
        except Exception as e:
            print(f"⚠️ Error fetching data for {symbol}: {e}")
            continue

        available_features = [f for f in features if f in df.columns]
        if len(available_features) < 2:
            print(f"⚠️ Skipping {symbol} — missing features")
            continue

        # Load pretrained models
        try:
            from keras.models import load_model
            import joblib

            lgb_model = joblib.load(f"{model_dir}/{symbol}_lgb.pkl")
            lstm_model = load_model(f"{model_dir}/{symbol}_lstm.h5")
            scaler = joblib.load(f"{model_dir}/{symbol}_scaler.pkl")
        except Exception as e:
            print(f"❌ Missing or failed to load model for {symbol}: {e}")
            continue

        # Use only test (after split_date) data for signal detection
        test_df = df[df.index > split_date]
        print(f"🧪 {symbol} — Test samples: {len(test_df)}")

        try:
            candidates = get_daily_candidates(lgb_model, lstm_model, scaler, test_df, symbol, available_features)
            all_candidates.extend(candidates)
        except Exception as e:
            print(f"⚠️ Error predicting {symbol}: {e}")

    # Evaluate and simulate trades
    df_candidates = pd.DataFrame(all_candidates)
    if df_candidates.empty:
        print("❌ No confirmed signals from DeepSeek.")
    else:
        best_trades = df_candidates.sort_values("score", ascending=False).drop_duplicates("date")
        simulate_trading(best_trades)
        print("✅ Done — Results saved to multi_coin_trades.csv")
