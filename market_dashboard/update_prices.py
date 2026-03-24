#!/usr/bin/env python3
"""
🔥 BINANCE PRICE FETCHER
Fetches real-time crypto prices from Binance API
Updates dashboard data files
"""

import requests
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/home/skux/.openclaw/workspace/market_dashboard/data")
DATA_DIR.mkdir(exist_ok=True)

# Binance API endpoints
BINANCE_BASE = "https://api.binance.com"

def fetch_ticker_price(symbol):
    """Fetch current price for a symbol from Binance"""
    try:
        url = f"{BINANCE_BASE}/api/v3/ticker/price"
        params = {"symbol": symbol}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
        else:
            print(f"Error fetching {symbol}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching {symbol}: {e}")
        return None

def fetch_24h_stats(symbol):
    """Fetch 24h change stats from Binance"""
    try:
        url = f"{BINANCE_BASE}/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'high': float(data['highPrice']),
                'low': float(data['lowPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume'])
            }
        return None
    except Exception as e:
        print(f"Exception fetching 24h stats for {symbol}: {e}")
        return None

def update_crypto_prices():
    """Update all crypto prices"""
    print("="*70)
    print("🔥 FETCHING REAL-TIME PRICES FROM BINANCE")
    print("="*70)
    
    # Symbol mapping (Binance uses USDT pairs)
    symbols = {
        "XRP": "XRPUSDT",
        "ADA": "ADAUSDT",
        "SOL": "SOLUSDT",
        "ETH": "ETHUSDT",
        "BTC": "BTCUSDT",
        "SUI": "SUIUSDT",
        "TIA": "TIAUSDT"
    }
    
    prices_data = {
        "timestamp": datetime.now().isoformat(),
        "source": "Binance API",
        "prices": {}
    }
    
    for name, symbol in symbols.items():
        print(f"\n📊 Fetching {name} ({symbol})...")
        
        price = fetch_ticker_price(symbol)
        stats = fetch_24h_stats(symbol)
        
        if price and stats:
            prices_data["prices"][name] = {
                "price": price,
                "price_formatted": f"${price:,.2f}" if price > 100 else f"${price:.4f}",
                "change_24h": stats['price_change'],
                "change_percent_24h": stats['price_change_percent'],
                "high_24h": stats['high'],
                "low_24h": stats['low'],
                "volume": stats['volume'],
                "trend": "UP" if stats['price_change_percent'] > 0 else "DOWN"
            }
            
            trend_icon = "📈" if stats['price_change_percent'] > 0 else "📉"
            print(f"   {trend_icon} ${price:,.4f} ({stats['price_change_percent']:+.2f}%)")
        else:
            print(f"   ❌ Failed to fetch")
    
    # Save to JSON
    output_file = DATA_DIR / "crypto_prices.json"
    with open(output_file, 'w') as f:
        json.dump(prices_data, f, indent=2)
    
    print(f"\n💾 Prices saved to: {output_file}")
    print(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return prices_data

def generate_dashboard_js():
    """Generate JavaScript file for dashboard to load prices"""
    
    js_content = """
// Auto-generated price loader for Market Dashboard
// Fetches real-time prices from Binance

const BINANCE_SYMBOLS = {
    "XRP": "XRPUSDT",
    "ADA": "ADAUSDT", 
    "SOL": "SOLUSDT",
    "ETH": "ETHUSDT",
    "BTC": "BTCUSDT",
    "SUI": "SUIUSDT",
    "TIA": "TIAUSDT"
};

// Fetch prices from Binance API
async function fetchBinancePrices() {
    const prices = {};
    
    for (const [name, symbol] of Object.entries(BINANCE_SYMBOLS)) {
        try {
            const response = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol}`);
            const data = await response.json();
            
            prices[name] = {
                price: parseFloat(data.lastPrice),
                change: parseFloat(data.priceChangePercent),
                high: parseFloat(data.highPrice),
                low: parseFloat(data.lowPrice),
                volume: parseFloat(data.volume)
            };
        } catch (e) {
            console.error(`Failed to fetch ${name}:`, e);
        }
    }
    
    return prices;
}

// Update dashboard with real prices
async function updateDashboardPrices() {
    console.log('🔄 Fetching real-time prices from Binance...');
    
    const prices = await fetchBinancePrices();
    
    // Update each asset card
    for (const [name, data] of Object.entries(prices)) {
        // Find asset card by name
        const assetCards = document.querySelectorAll('.asset-card');
        
        assetCards.forEach(card => {
            const assetName = card.querySelector('.asset-name');
            if (assetName && assetName.textContent === name) {
                // Update price
                const priceEl = card.querySelector('.asset-price-value');
                if (priceEl) {
                    const formattedPrice = data.price > 100 
                        ? `$${data.price.toLocaleString('en-US', {maximumFractionDigits: 2})}`
                        : `$${data.price.toFixed(4)}`;
                    priceEl.textContent = formattedPrice;
                    priceEl.style.color = data.change >= 0 ? '#10b981' : '#ef4444';
                }
                
                // Update change
                const changeEl = card.querySelector('.asset-price-change');
                if (changeEl) {
                    const sign = data.change >= 0 ? '+' : '';
                    changeEl.textContent = `${sign}${data.change.toFixed(2)}% (24h)`;
                    changeEl.className = `asset-price-change ${data.change >= 0 ? 'positive' : 'negative'}`;
                }
                
                // Add live indicator
                card.style.borderColor = data.change >= 0 ? '#10b981' : '#ef4444';
                setTimeout(() => {
                    card.style.borderColor = '';
                }, 1000);
            }
        });
    }
    
    // Update timestamp
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    console.log('✅ Prices updated from Binance');
}

// Auto-update every 30 seconds
setInterval(updateDashboardPrices, 30000);

// Initial load
document.addEventListener('DOMContentLoaded', updateDashboardPrices);
"""
    
    js_file = DATA_DIR / "price_loader.js"
    with open(js_file, 'w') as f:
        f.write(js_content)
    
    print(f"💾 JavaScript loader saved to: {js_file}")

if __name__ == "__main__":
    prices = update_crypto_prices()
    generate_dashboard_js()
    
    print("\n" + "="*70)
    print("✅ PRICE UPDATE COMPLETE")
    print("="*70)
    print("\nTo use in dashboard:")
    print("1. Include in HTML: <script src='data/price_loader.js'></script>")
    print("2. Or run: python3 update_prices.py (updates JSON file)")
    print("3. Prices auto-refresh every 30 seconds")
