# Final Integrated AI Crypto Bot with Trading + Wallet + DeepSeek + Stop-loss

import os
import time
import warnings
import joblib
import requests
import numpy as np
import pandas as pd
import schedule
from dotenv import load_dotenv
from datetime import datetime
from binance.client import Client
from ta import add_all_ta_features
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
import json

# ---------- CONFIG ----------
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

model_dir = "models"
WALLET_FILE = "wallet.json"
symbols = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'DOGEUSDT', 'SHIBUSDT',
    'PEPEUSDT', 'FLOKIUSDT', 'MATICUSDT', 'XRPUSDT', 'LTCUSDT', 'BNBUSDT'
]

features = [
    'momentum_rsi', 'trend_macd', 'trend_ema_fast', 'volume_sma_em',
    'trend_adx', 'volatility_bbm', 'trend_ichimoku_a', 'trend_psar_up',
    'momentum_stoch_rsi'
]

lgb_models, lstm_models, scalers = {}, {}, {}

# ---------- MODEL LOADING ----------
def load_models():
    for symbol in symbols:
        lgb_models[symbol] = joblib.load(f"{model_dir}/{symbol}_lgb.pkl")
        lstm_models[symbol] = load_model(f"{model_dir}/{symbol}_lstm.h5")
        scalers[symbol] = joblib.load(f"{model_dir}/{symbol}_scaler.pkl")

# ---------- WALLET HANDLING ----------
def load_wallet():
    if not os.path.exists(WALLET_FILE):
        wallet = {"balance": 10000.0, "positions": {}, "trade_history": []}
    else:
        with open(WALLET_FILE, "r") as f:
            wallet = json.load(f)
    for symbol in symbols:
        if symbol not in wallet["positions"]:
            wallet["positions"][symbol] = {"amount": 0.0, "entry_price": 0.0}
    return wallet

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=2)

def log_to_live_trades(trade_log):
    path = "live_trades.json"
    trades = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                pass
    trades.insert(0, trade_log)
    with open(path, "w") as f:
        json.dump(trades[:10], f, indent=2)

# ---------- TRADE EXECUTION ----------
def execute_trade(symbol, signal, price, score):
    wallet = load_wallet()
    position = wallet["positions"].get(symbol, {"amount": 0.0, "entry_price": 0.0})
    confidence = "High" if score >= 0.75 else "Medium" if score >= 0.6 else "Low"
    timestamp = datetime.now().strftime("%H:%M:%S")

    trade_log = {
        "time": timestamp, "asset": symbol, "action": signal,
        "confidence": confidence, "price": f"${price:.2f}",
        "reason": "Triggered by AI ensemble + DeepSeek confirmation",
        "taxCategory": "STCG"
    }

    if signal == "BUY":
        if wallet["balance"] < 1:
            print(f"⚠️ Skipped BUY {symbol} — balance too low.")
            return
        qty = min(wallet["balance"], 10) / price
        total_qty = position["amount"] + qty
        total_cost = position["amount"] * position["entry_price"] + qty * price
        avg_price = total_cost / total_qty
        wallet["positions"][symbol] = {"amount": total_qty, "entry_price": avg_price}
        wallet["balance"] -= qty * price
    elif signal == "SELL" and position["amount"] > 0:
        proceeds = position["amount"] * price
        pnl = proceeds - (position["amount"] * position["entry_price"])
        wallet["balance"] += proceeds
        wallet["positions"][symbol] = {"amount": 0.0, "entry_price": 0.0}
        trade_log["pnl"] = f"{'Profit' if pnl >= 0 else 'Loss'}: ${abs(pnl):.2f}"

    wallet["trade_history"].append(trade_log)
    save_wallet(wallet)
    log_to_live_trades(trade_log)
    print("✅ Trade executed.")

# ---------- AI + TECHNICALS ----------
def ensemble_predict(row, lgb_model, lstm_model, scaler, features):
    X = pd.DataFrame([row[features].values], columns=features)
    lgb_score = lgb_model.predict_proba(X)[0][1]
    X_scaled = scaler.transform(X)
    lstm_input = np.reshape(X_scaled, (1, 1, len(features)))
    lstm_score = lstm_model.predict(lstm_input, verbose=0)[0][0]
    vote_score = 0.6 * lgb_score + 0.4 * lstm_score
    return int(vote_score > 0.6), vote_score

def fetch_binance_data(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval="5m", limit=300)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return pd.DataFrame()

def preprocess(df):
    df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
    return df.dropna(subset=features)

def predict_stoploss_risk(row, symbol):
    try:
        model_path = f"{model_dir}/{symbol}_stoploss.pkl"
        scaler_path = f"{model_dir}/{symbol}_stoploss_scaler.pkl"
        if not os.path.exists(model_path): return False
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        X = pd.DataFrame([row[features].values], columns=features)
        X_scaled = scaler.transform(X)
        return bool(model.predict(X_scaled)[0])
    except Exception as e:
        print(f"❌ Stop-loss prediction error for {symbol}: {e}")
        return False

# ---------- DEEPSEEK ----------
def run_deepseek(prompt):
    try:
        r = requests.post("http://localhost:11434/api/generate", json={"model": "deepseek-local", "prompt": prompt, "stream": False})
        return r.json().get("response", "").strip()
    except: return ""

def ask_deepseek_confirmation(symbol, rsi, macd, ema, vol, price, signal):
    prompt = f"""
The AI predicted a {signal} signal for {symbol}. 
- RSI: {rsi:.2f} \n- MACD: {macd:.4f} \n- EMA: {ema:.2f} \n- Volume EMA: {vol:.2f} \n- Price: {price:.2f}.
Should we proceed with {signal}? Reply YES - reason or NO - reason.
"""
    res = run_deepseek(prompt)
    if '-' in res:
        p = res.split('-', 1)
        return p[0].strip().upper(), p[1].strip()
    return "NO", "Invalid DeepSeek response"

# ---------- LIVE LOOP ----------
def live_mode_loop():
    print(f"\n🔁 Checking live data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for symbol in symbols:
        try:
            df = fetch_binance_data(symbol)
            if df.empty: continue
            df = preprocess(df)
            row = df.iloc[-1]
            pred, score = ensemble_predict(row, lgb_models[symbol], lstm_models[symbol], scalers[symbol], features)
            signal = "BUY" if score > 0.6 else "SELL" if score < 0.4 else None
            if not signal:
                print(f"⏳ {symbol}: No strong signal ({score:.2f})")
                continue
            decision, reason = ask_deepseek_confirmation(symbol, row['momentum_rsi'], row['trend_macd'], row['trend_ema_fast'], row['volume_sma_em'], row['close'], signal)
            print(f"🔔 {symbol} SIGNAL | {signal} | Score: {score:.4f} | DeepSeek: {decision} - {reason}")
            if decision == "YES":
                if signal == "BUY" and predict_stoploss_risk(row, symbol):
                    print(f"🛑 STOP-LOSS WARNING: Skipping {symbol} BUY")
                    continue
                execute_trade(symbol, signal, float(row['close']), score)
            else:
                print(f"⏳ {symbol}: DeepSeek rejected: {reason}")
        except Exception as e:
            print(f"⚠️ Error in loop for {symbol}: {e}")
def track_wallet_performance():
    try:
        wallet = load_wallet()
        prices = {}
        for symbol in wallet["positions"]:
            if wallet["positions"][symbol]["amount"] > 0:
                price = float(client.get_symbol_ticker(symbol=symbol)["price"])
                prices[symbol] = price
        value = wallet["balance"]
        for sym, data in wallet["positions"].items():
            amount = data["amount"]
            if amount > 0:
                value += amount * prices.get(sym, 0)
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_value": round(value, 2),
            "balance": round(wallet["balance"], 2),
            "holdings_value": round(value - wallet["balance"], 2)
        }
        file_path = "wallet_performance.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(record)
        data = data[-100:]  # keep last 100 entries
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"📊 Wallet tracked @ {record['timestamp']} | Total: ${record['total_value']}")
    except Exception as e:
        print(f"⚠️ Failed to track wallet performance: {e}")

# ---------- RUN ----------
if __name__ == "__main__":
    print("🚀 Live Crypto Signal Bot Started...")
    load_models()
    live_mode_loop()
    schedule.every(5).minutes.do(live_mode_loop)
    while True:
        schedule.run_pending()
        time.sleep(1)
