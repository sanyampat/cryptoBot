# Final Integrated AI Crypto Bot with Trading + Wallet + DeepSeek + Stop-loss (talib-free, v3)

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

# Constants for Risk Management
RISK_PER_TRADE = 0.02
STOP_LOSS_PCT = 0.05
TAKE_PROFIT_PCT = 0.15
MIN_TRADE_SIZE = 10

# API and Client Setup
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# File and Model Paths
model_dir = "models"
WALLET_FILE = "wallet.json"
LIVE_TRADES_FILE = "live_trades.json"
PERFORMANCE_FILE = "wallet_performance.json"

symbols = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'DOGEUSDT', 
    'MATICUSDT', 'XRPUSDT', 'BNBUSDT'
]

features = [
    'momentum_rsi', 'trend_macd', 'trend_ema_fast', 'volume_sma_em',
    'trend_adx', 'volatility_bbm', 'volatility_atr', 'volume_obv',
    'momentum_stoch_rsi'
]

lgb_models, lstm_models, scalers = {}, {}, {}

# ---------- MODEL LOADING ----------
def load_models():
    print("🔄 Loading AI models for all symbols...")
    loaded_count = 0
    for symbol in symbols:
        try:
            lgb_models[symbol] = joblib.load(f"{model_dir}/{symbol}_lgb.pkl")
            lstm_models[symbol] = load_model(f"{model_dir}/{symbol}_lstm.h5", compile=False)
            scalers[symbol] = joblib.load(f"{model_dir}/{symbol}_scaler.pkl")
            loaded_count += 1
        except Exception as e:
            print(f"⚠️ Failed to load models for {symbol}: {e}")
    print(f"✅ Models loaded for {loaded_count}/{len(symbols)} symbols.")

# ---------- UTILITY FUNCTIONS ----------
def log_to_live_trades(trade_log):
    trades = []
    if os.path.exists(LIVE_TRADES_FILE):
        with open(LIVE_TRADES_FILE, "r") as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError: pass
    trades.insert(0, trade_log)
    with open(LIVE_TRADES_FILE, "w") as f:
        json.dump(trades[:20], f, indent=2)

# FIX #3: Made wallet an argument and added robust JSON loading
def track_wallet_performance(wallet):
    try:
        prices = {}
        for symbol, position in wallet.data["positions"].items():
            if position["amount"] > 0:
                prices[symbol] = float(client.get_symbol_ticker(symbol=symbol)["price"])
        
        holdings_value = sum(pos["amount"] * prices.get(sym, 0) for sym, pos in wallet.data["positions"].items())
        total_value = wallet.data["balance"] + holdings_value

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_value": round(total_value, 2), "balance": round(wallet.data["balance"], 2),
            "holdings_value": round(holdings_value, 2)
        }
        
        data = []
        if os.path.exists(PERFORMANCE_FILE):
            with open(PERFORMANCE_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError: # Handles empty or corrupted file
                    data = []
        
        data.append(record)
        with open(PERFORMANCE_FILE, "w") as f: json.dump(data[-200:], f, indent=2)
        
        print(f"📊 Wallet performance tracked | Total Value: ${record['total_value']:.2f}")
    except Exception as e:
        print(f"⚠️ Failed to track wallet performance: {e}")

# ---------- ENHANCED WALLET HANDLING ----------
# FIX #1: Full wallet upgrade logic for backward compatibility
# ---------- ENHANCED WALLET HANDLING (v2 - Fully Backward-Compatible) ----------
class EnhancedWallet:
    def __init__(self):
        self.file = WALLET_FILE
        self.data = self._load()
        
    def _load(self):
        # Define the required structure for a position and stats
        default_position = {"amount": 0.0, "entry_price": 0.0, "stop_loss": 0.0, "take_profit": 0.0}
        default_stats = {"total_trades": 0, "winning_trades": 0, "losing_trades": 0, "total_pnl": 0.0, "profit_factor": 1.0}

        # If no wallet file exists, create a fresh one with the correct structure
        if not os.path.exists(self.file):
            return {"balance": 10000.0, "positions": {s: default_position.copy() for s in symbols}, "trade_history": [], "performance_stats": default_stats}
        
        # If a wallet file exists, load it and perform a robust upgrade check
        with open(self.file, "r") as f:
            try:
                wallet_data = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupt/empty, create a new one
                return {"balance": 10000.0, "positions": {s: default_position.copy() for s in symbols}, "trade_history": [], "performance_stats": default_stats}

        # --- ROBUST UPGRADE LOGIC ---
        upgraded = False
        
        # 1. Ensure top-level keys exist
        if 'positions' not in wallet_data:
            wallet_data['positions'] = {}
            upgraded = True
        if 'performance_stats' not in wallet_data:
            wallet_data['performance_stats'] = default_stats
            upgraded = True

        # 2. Upgrade every existing position found in the file
        for symbol_in_file, position_data in wallet_data["positions"].items():
            for key, default_value in default_position.items():
                if key not in position_data:
                    position_data[key] = default_value
                    upgraded = True

        # 3. Add any new symbols from the script's list that are not yet in the wallet
        for symbol_in_script in symbols:
            if symbol_in_script not in wallet_data["positions"]:
                wallet_data["positions"][symbol_in_script] = default_position.copy()
                upgraded = True

        if upgraded:
            print("✅ Wallet file format mismatch detected. Upgrading to the latest structure...")
            self.save_data(wallet_data) # Save the upgraded structure immediately

        return wallet_data
    
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)

    # Helper to save data during the load process if an upgrade happens
    def save_data(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)
    
    def update_stats(self, pnl):
        stats = self.data["performance_stats"]
        stats["total_trades"] += 1
        stats["total_pnl"] = stats.get("total_pnl", 0.0) + pnl
        if pnl >= 0:
            stats["winning_trades"] += 1
        else:
            stats["losing_trades"] += 1
        
        wins = sum(t.get('pnl', 0) for t in self.data["trade_history"] if t.get('pnl', 0) > 0)
        losses = abs(sum(t.get('pnl', 0) for t in self.data["trade_history"] if t.get('pnl', 0) < 0))
        stats["profit_factor"] = wins / losses if losses > 0 else float('inf')
        self.save()

# ---------- DATA & AI ----------
def fetch_binance_data(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval="15m", limit=300)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return pd.DataFrame()

def enhanced_preprocess(df):
    df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
    df['market_regime'] = 'neutral'
    df.loc[(df['trend_adx'] > 20) & (df['close'] > df['trend_ema_fast']), 'market_regime'] = 'bullish'
    df.loc[(df['trend_adx'] > 20) & (df['close'] < df['trend_ema_fast']), 'market_regime'] = 'bearish'
    return df.dropna()

def ensemble_predict(row, symbol, features):
    X = pd.DataFrame([row[features].values], columns=features)
    lgb_score = lgb_models[symbol].predict_proba(X)[0][1]
    X_scaled = scalers[symbol].transform(X)
    lstm_input = np.reshape(X_scaled, (1, 1, len(features)))
    lstm_score = lstm_models[symbol].predict(lstm_input, verbose=0)[0][0]
    return 0.6 * lgb_score + 0.4 * lstm_score

def predict_stoploss_risk(row, symbol, features):
    try:
        model_path = f"{model_dir}/{symbol}_stoploss.pkl"
        if not os.path.exists(model_path): return False
        model = joblib.load(model_path)
        scaler = joblib.load(f"{model_dir}/{symbol}_stoploss_scaler.pkl")
        X = pd.DataFrame([row[features].values], columns=features)
        X_scaled = scaler.transform(X)
        return bool(model.predict(X_scaled)[0])
    except Exception as e:
        print(f"❌ Stop-loss prediction error for {symbol}: {e}")
        return False

# ---------- DEEPSEEK ----------
def ask_deepseek_confirmation(symbol, rsi, macd, adx, price, signal):
    prompt = f"As a crypto analyst, is a {signal} on {symbol} at ${price:.2f} wise given: RSI={rsi:.2f}, MACD={macd:.4f}, ADX={adx:.2f}? Reply: YES - reason or NO - reason."
    try:
        response = requests.post("http://localhost:11434/api/generate", json={"model": "deepseek-coder", "prompt": prompt, "stream": False}, timeout=20)
        response.raise_for_status()
        res = response.json().get("response", "").strip()
        print(f"🧠 DeepSeek says for {symbol}: '{res}'")
        if res.upper().startswith("YES"): return "YES", res
        if res.upper().startswith("NO"): return "NO", res
        return "NO", "Unclear response from LLM."
    except requests.exceptions.RequestException as e:
        print(f"❌ DeepSeek connection error: {e}")
        return "NO", "LLM connection failed."

# ---------- TRADING & RISK MANAGEMENT ----------
# FIX #2: Wallet object is now passed as an argument
def execute_trade(wallet, symbol, signal, price, score):
    position = wallet.data["positions"][symbol]
    trade_log = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "asset": symbol, "action": signal, "price": price, "confidence": f"{score:.2%}", "reason": "AI ensemble + DeepSeek"}

    if signal == "BUY":
        risk_capital = wallet.data["balance"] * RISK_PER_TRADE
        position_size_usd = min(risk_capital, wallet.data["balance"])
        if position_size_usd < MIN_TRADE_SIZE: return
        qty_to_buy = position_size_usd / price
        avg_price = ((position["amount"] * position["entry_price"]) + (qty_to_buy * price)) / (position["amount"] + qty_to_buy)
        wallet.data["positions"][symbol].update({"amount": position["amount"] + qty_to_buy, "entry_price": avg_price, "stop_loss": price * (1 - STOP_LOSS_PCT), "take_profit": price * (1 + TAKE_PROFIT_PCT)})
        wallet.data["balance"] -= position_size_usd
        trade_log["size_usd"] = position_size_usd
    elif signal == "SELL" and position["amount"] > 0:
        proceeds = position["amount"] * price
        pnl = proceeds - (position["amount"] * position["entry_price"])
        trade_log.update({"pnl": round(pnl, 2), "pnl_pct": (pnl / (position["amount"] * position["entry_price"])) * 100 if position["entry_price"] > 0 else 0})
        wallet.data["balance"] += proceeds
        wallet.data["positions"][symbol].update({"amount": 0.0, "entry_price": 0.0, "stop_loss": 0.0, "take_profit": 0.0})
        wallet.update_stats(pnl)

    wallet.data["trade_history"].insert(0, trade_log)
    wallet.save()
    log_to_live_trades(trade_log)
    print(f"✅ {signal} executed for {symbol} @ ${price:.4f} | Size: ${trade_log.get('size_usd', proceeds):.2f}")

def check_position_health(wallet):
    print("🩺 Checking health of open positions...")
    something_changed = False
    for symbol, position in wallet.data["positions"].items():
        if position["amount"] > 0:
            try:
                current_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
                if current_price <= position["stop_loss"]:
                    print(f"🛑 STOP-LOSS triggered for {symbol} at ${current_price:.4f}")
                    execute_trade(wallet, symbol, "SELL", current_price, 1.0)
                    something_changed = True
                elif current_price >= position["take_profit"]:
                    print(f"🎯 TAKE-PROFIT triggered for {symbol} at ${current_price:.4f}")
                    execute_trade(wallet, symbol, "SELL", current_price, 1.0)
                    something_changed = True
            except Exception as e: print(f"⚠️ Could not check health for {symbol}: {e}")
    if not something_changed: print("👍 All positions are within risk parameters.")

def generate_signal(score, row):
    if row['volume'] < row['volume_sma_em']: return None, "Low volume"
    if row['market_regime'] == 'neutral': return None, "Neutral market regime"
    if row['trend_adx'] < 20: return None, f"Weak trend (ADX: {row['trend_adx']:.2f})"
    if score > 0.65 and row['market_regime'] == 'bullish': return "BUY", "Strong bullish score in uptrend"
    if score < 0.35 and row['market_regime'] == 'bearish': return "SELL", "Strong bearish score in downtrend"
    return None, f"Score ({score:.2f}) not strong enough"

# ---------- MAIN TRADING CYCLE ----------
def trading_cycle():
    print(f"\n{'='*20} 🔁 Trading Cycle Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {'='*20}")
    # FIX #2: Create ONE wallet instance per cycle
    wallet = EnhancedWallet()
    check_position_health(wallet)

    print("\n🔍 Analyzing market for new opportunities...")
    for symbol in symbols:
        if wallet.data["positions"][symbol]["amount"] > 0:
            print(f" holdings {symbol}, skipping analysis.")
            continue
        try:
            df = fetch_binance_data(symbol)
            if df.empty or len(df) < 50: continue
            
            df = enhanced_preprocess(df)
            if df.empty: continue
            row = df.iloc[-1]
            
            score = ensemble_predict(row, symbol, features)
            signal, reason = generate_signal(score, row)
            if not signal:
                print(f"⏳ {symbol}: No qualified signal. Reason: {reason}")
                continue
            
            print(f"🔔 POTENTIAL SIGNAL: {symbol} | {signal} | Score: {score:.2f} | Reason: {reason}")
            decision, ds_reason = ask_deepseek_confirmation(symbol, row['momentum_rsi'], row['trend_macd'], row['trend_adx'], row['close'], signal)
            
            if decision == "YES":
                if signal == "BUY" and predict_stoploss_risk(row, symbol, features):
                    print(f"🛑 High stop-loss risk predicted. Skipping BUY for {symbol}.")
                    continue
                execute_trade(wallet, symbol, signal, float(row['close']), score)
            else:
                print(f"❌ {symbol}: Trade rejected by DeepSeek. Reason: {ds_reason}")
                
        except Exception as e:
            print(f"⚠️ Critical error processing {symbol}: {e}")
    
    track_wallet_performance(wallet)
    print(f"{'='*20} ✅ Trading Cycle Finished {'='*26}\n")

# ---------- MAIN EXECUTION ----------
if __name__ == "__main__":
    print("🚀 Final Integrated Crypto Trading Bot (talib-free, v3)")
    print(f"📅 Initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    load_models()
    
    wallet = EnhancedWallet()
    stats = wallet.data['performance_stats']
    win_rate = (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0
    print(f"\n💰 Initial Balance: ${wallet.data['balance']:.2f}")
    print(f"📊 Lifetime Stats: {stats['total_trades']} Trades | {win_rate:.1f}% Win Rate | PnL: ${stats.get('total_pnl', 0.0):.2f} | Profit Factor: {stats['profit_factor']:.2f}\n")
    
    trading_cycle()
    schedule.every(15).minutes.do(trading_cycle)
    
    print("⏳ Bot is now running. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        EnhancedWallet().save() # Save final state
        print("👋 Bot shutdown complete.")