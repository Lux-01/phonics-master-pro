#!/usr/bin/env python3
"""
🔥 STOCK PRICE FETCHER
Fetches real-time stock prices from Yahoo Finance API
Updates dashboard data files
"""

import requests
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/home/skux/.openclaw/workspace/market_dashboard/data")
DATA_DIR.mkdir(exist_ok=True)

# Stock symbols to track
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

def fetch_stock_price(symbol):
    """Fetch current price for a stock from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": "1d"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('chart') and data['chart'].get('result'):
                result = data['chart']['result'][0]
                meta = result['meta']
                
                price = meta.get('regularMarketPrice', 0)
                prev_close = meta.get('previousClose', price)
                change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
                
                return {
                    'price': price,
                    'change': change,
                    'prev_close': prev_close
                }
        return None
    except Exception as e:
        print(f"Exception fetching {symbol}: {e}")
        return None

def update_stock_prices():
    """Update all stock prices"""
    print("="*70)
    print("🔥 FETCHING REAL-TIME STOCK PRICES FROM YAHOO FINANCE")
    print("="*70)
    
    prices_data = {
        "timestamp": datetime.now().isoformat(),
        "source": "Yahoo Finance API",
        "prices": {}
    }
    
    for symbol, name in STOCKS.items():
        print(f"\n📊 Fetching {symbol} ({name})...")
        
        data = fetch_stock_price(symbol)
        
        if data:
            prices_data["prices"][symbol] = data
            
            trend_icon = "📈" if data['change'] >= 0 else "📉"
            print(f"   {trend_icon} ${data['price']:.2f} ({data['change']:+.2f}%)")
        else:
            print(f"   ❌ Failed to fetch")
    
    # Save to JSON
    output_file = DATA_DIR / "stock_prices.json"
    with open(output_file, 'w') as f:
        json.dump(prices_data, f, indent=2)
    
    print(f"\n💾 Prices saved to: {output_file}")
    print(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return prices_data

if __name__ == "__main__":
    prices = update_stock_prices()
    
    print("\n" + "="*70)
    print("✅ STOCK PRICE UPDATE COMPLETE")
    print("="*70)
