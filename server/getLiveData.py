from binance.client import Client
from dotenv import load_dotenv
import os

# Load API keys
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key, api_secret)

def get_live_data(symbol="BTCUSDT", show_order_book=False):
    """
    Fetches live market data from Binance.
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
        show_order_book (bool): If True, includes top 5 bids/asks.

    Returns:
        dict: Contains live price, last 1m candle, and optionally order book.
    """
    try:
        # Latest price
        price = client.get_symbol_ticker(symbol=symbol)

        # Last 1m candle
        candle = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)[0]
        candle_data = {
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "timestamp": candle[0]
        }

        # Optional: Order book
        order_book = {}
        if show_order_book:
            depth = client.get_order_book(symbol=symbol, limit=5)
            order_book = {
                "bids": depth["bids"],
                "asks": depth["asks"]
            }

        return {
            "symbol": symbol,
            "price": float(price["price"]),
            "last_candle": candle_data,
            "order_book": order_book
        }

    except Exception as e:
        print(f"❌ Error fetching live data: {e}")
        return None


data = get_live_data("BTCUSDT", show_order_book=True)

if data:
    print("💰 Price:", data["price"])
    print("🕒 Last 1m Candle:", data["last_candle"])
    print("📘 Order Book Bids:", data["order_book"].get("bids"))
