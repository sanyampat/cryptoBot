import os
import pandas as pd
import numpy as np
import joblib
from ta import add_all_ta_features
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

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

data_dir = "historical_data"
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

lookahead = 10  # candles to look ahead for price drop
drop_threshold = 0.03  # 3% drop
features = [
    'momentum_rsi', 'trend_macd', 'trend_ema_fast',
    'volume_sma_em', 'trend_adx', 'volatility_bbm',
    'trend_ichimoku_a', 'trend_psar_up', 'momentum_stoch_rsi'
]

def generate_target(df):
    close_prices = df['close'].values
    targets = np.zeros(len(df))
    for i in range(len(df) - lookahead):
        future_window = close_prices[i + 1:i + 1 + lookahead]
        if len(future_window) == 0:
            continue
        min_future_price = np.min(future_window)
        if (close_prices[i] - min_future_price) / close_prices[i] >= drop_threshold:
            targets[i] = 1
    df['stoploss_target'] = targets
    return df

for symbol in symbols:
    path = os.path.join(data_dir, f"{symbol}.csv")
    if not os.path.exists(path):
        print(f"❌ Missing data for {symbol}")
        continue

    print(f"📊 Processing {symbol}")
    df = pd.read_csv(path, parse_dates=['timestamp'], index_col='timestamp')
    df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
    df = generate_target(df)
    df = df.dropna(subset=features + ['stoploss_target'])
    
    X = df[features]
    y = df['stoploss_target']
    
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print(f"\n📈 {symbol} Stop-Loss Model Performance:\n")
    print(classification_report(y_test, y_pred, digits=3))

    joblib.dump(clf, f"{model_dir}/{symbol}_stoploss.pkl")
    joblib.dump(scaler, f"{model_dir}/{symbol}_stoploss_scaler.pkl")
    print(f"✅ Saved model and scaler for {symbol}\n")
