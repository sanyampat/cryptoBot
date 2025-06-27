from binance.client import Client
from dotenv import load_dotenv
import os
import pandas as pd

# Load API keys from .env
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Initialize Binance client
client = Client(api_key, api_secret)

# Function to fetch historical data
def getHistoricalData(symbol, interval, start_date, end_date):
    print(f"📊 Fetching {symbol} data from {start_date} to {end_date}...")

    # Get klines
    klines = client.get_historical_klines(symbol, interval, start_date, end_date)

    # Create DataFrame
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])

    # Format columns
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

    # Save to CSV
    filename = f"{symbol}_{interval}_{start_date.replace(',', '').replace(' ', '_')}_to_{end_date.replace(',', '').replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)

    print(f"✅ Saved to: {filename}")
    return df
