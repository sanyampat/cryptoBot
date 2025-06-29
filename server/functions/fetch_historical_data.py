import os
import time
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load API keys
load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# Config
symbols = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'DOGEUSDT',
    'SHIBUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'MATICUSDT', 'XRPUSDT',
    'LTCUSDT', 'BNBUSDT'
]

interval = '15m'  # can be '1m', '15m', '1h', etc.
preferred_start = '1 Jan, 2022'
fallback_start = '1 Jan, 2020'
output_dir = 'historical_data'
os.makedirs(output_dir, exist_ok=True)

def date_to_milliseconds(date_str):
    epoch = datetime.fromtimestamp(0, tz=timezone.utc)
    dt = datetime.strptime(date_str, "%d %b, %Y").replace(tzinfo=timezone.utc)
    return int((dt - epoch).total_seconds() * 1000.0)

def fetch_data(symbol, interval, start_str):
    print(f"📥 Fetching {symbol} data starting from {start_str}...")
    start_ts = date_to_milliseconds(start_str)
    limit = 1000
    all_klines = []

    while True:
        try:
            klines = client.get_historical_klines(symbol, interval, start_ts, limit=limit)
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            break

        if not klines:
            break

        all_klines.extend(klines)
        start_ts = klines[-1][0] + 1
        if len(klines) < limit:
            break
        time.sleep(0.1)

    if not all_klines:
        return None

    df = pd.DataFrame(all_klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

# Run for each symbol
for symbol in symbols:
    file_path = os.path.join(output_dir, f"{symbol}.csv")
    if os.path.exists(file_path):
        print(f"⏩ Skipping {symbol} — data file already exists.")
        continue

    df = fetch_data(symbol, interval, preferred_start)
    if df is None or df.empty:
        print(f"⚠️ No data from {preferred_start}. Trying fallback date: {fallback_start}...")
        df = fetch_data(symbol, interval, fallback_start)

    if df is not None and not df.empty:
        df.to_csv(file_path)
        print(f"✅ Saved {symbol} data to {file_path}")
    else:
        print(f"❌ Skipping {symbol} — no data available even after fallback.")
