#!/usr/bin/env python3
"""
🔥 UNIFIED PRICE FETCHER
Fetches both crypto and stock prices, saves to JSON
Dashboard loads from JSON (avoids CORS issues)
"""

import requests
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/home/skux/.openclaw/workspace/market_dashboard/data")
DATA_DIR.mkdir(exist_ok=True)

# Binance symbols
CRYPTO_SYMBOLS = {
    "XRP": "XRPUSDT",
    "ADA": "ADAUSDT",
    "SOL": "SOLUSDT",
    "ETH": "ETHUSDT",
    "BTC": "BTCUSDT",
    "SUI": "SUIUSDT",
    "TIA": "TIAUSDT"
}

# Stock symbols
STOCKS = {
    "TSLA": "Tesla Inc",
    "NVDA": "NVIDIA Corp",
    "AAPL": "Apple Inc",
    "MSFT": "Microsoft Corp",
    "AMZN": "Amazon.com Inc",
    "GOOGL": "Alphabet Inc",
    "META": "Meta Platforms",
    "AMD": "AMD Inc"
}

def fetch_crypto_prices():
    """Fetch crypto prices from Binance"""
    prices = {}
    
    for name, symbol in CRYPTO_SYMBOLS.items():
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices[name] = {
                    "price": float(data['lastPrice']),
                    "change": float(data['priceChangePercent']),
                    "high": float(data['highPrice']),
                    "low": float(data['lowPrice']),
                    "volume": float(data['volume'])
                }
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return prices

def fetch_stock_prices():
    """Fetch stock prices from Yahoo Finance"""
    prices = {}
    
    for symbol in STOCKS.keys():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {"interval": "1d", "range": "1d"}
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('chart') and data['chart'].get('result'):
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    price = meta.get('regularMarketPrice', 0)
                    prev_close = meta.get('previousClose', price)
                    change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
                    
                    prices[symbol] = {
                        "price": price,
                        "change": change,
                        "prev_close": prev_close
                    }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    
    return prices

def update_all_prices():
    """Update all prices and save to JSON"""
    print("="*70)
    print("🔥 FETCHING ALL PRICES")
    print("="*70)
    
    # Fetch crypto
    print("\n📊 Fetching Crypto from Binance...")
    crypto_prices = fetch_crypto_prices()
    for name, data in crypto_prices.items():
        trend = "📈" if data['change'] >= 0 else "📉"
        print(f"   {trend} {name}: ${data['price']:.4f} ({data['change']:+.2f}%)")
    
    # Fetch stocks
    print("\n📊 Fetching Stocks from Yahoo Finance...")
    stock_prices = fetch_stock_prices()
    for symbol, data in stock_prices.items():
        trend = "📈" if data['change'] >= 0 else "📉"
        print(f"   {trend} {symbol}: ${data['price']:.2f} ({data['change']:+.2f}%)")
    
    # Save unified data
    unified_data = {
        "timestamp": datetime.now().isoformat(),
        "crypto": crypto_prices,
        "stocks": stock_prices
    }
    
    output_file = DATA_DIR / "all_prices.json"
    with open(output_file, 'w') as f:
        json.dump(unified_data, f, indent=2)
    
    print(f"\n💾 All prices saved to: {output_file}")
    print(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return unified_data

if __name__ == "__main__":
    update_all_prices()
