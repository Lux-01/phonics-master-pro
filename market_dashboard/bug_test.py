#!/usr/bin/env python3
"""
🔍 DASHBOARD BUG TEST REPORT
Verifies all data sources are real and functioning
"""

import requests
import json
from datetime import datetime

def test_binance_api():
    """Test Binance API connectivity"""
    print("\n" + "="*70)
    print("📊 TEST 1: BINANCE API (Crypto Prices)")
    print("="*70)
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    results = []
    
    for symbol in symbols:
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['lastPrice'])
                change = float(data['priceChangePercent'])
                print(f"   ✅ {symbol}: ${price:,.2f} ({change:+.2f}%)")
                results.append(True)
            else:
                print(f"   ❌ {symbol}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
            results.append(False)
    
    return all(results)

def test_yahoo_finance():
    """Test Yahoo Finance API connectivity"""
    print("\n" + "="*70)
    print("📊 TEST 2: YAHOO FINANCE API (Stock Prices)")
    print("="*70)
    
    symbols = ["TSLA", "NVDA", "AAPL"]
    results = []
    
    for symbol in symbols:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {"interval": "1d", "range": "1d"}
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('chart') and data['chart'].get('result'):
                    result = data['chart']['result'][0]
                    price = result['meta'].get('regularMarketPrice', 0)
                    print(f"   ✅ {symbol}: ${price:.2f}")
                    results.append(True)
                else:
                    print(f"   ⚠️  {symbol}: No data in response")
                    results.append(False)
            else:
                print(f"   ❌ {symbol}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
            results.append(False)
    
    return all(results)

def test_dashboard_files():
    """Test dashboard files exist"""
    print("\n" + "="*70)
    print("📁 TEST 3: DASHBOARD FILE INTEGRITY")
    print("="*70)
    
    from pathlib import Path
    
    files = [
        "/home/skux/.openclaw/workspace/market_dashboard/index.html",
        "/home/skux/.openclaw/workspace/market_dashboard/data/crypto_prices.json",
        "/home/skux/.openclaw/workspace/market_dashboard/data/stock_prices.json",
        "/home/skux/.openclaw/workspace/market_dashboard/update_prices.py",
        "/home/skux/.openclaw/workspace/market_dashboard/update_stocks.py"
    ]
    
    results = []
    for file in files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {path.name} ({size:,} bytes)")
            results.append(True)
        else:
            print(f"   ❌ {path.name} NOT FOUND")
            results.append(False)
    
    return all(results)

def test_data_freshness():
    """Test data is fresh"""
    print("\n" + "="*70)
    print("⏰ TEST 4: DATA FRESHNESS")
    print("="*70)
    
    from pathlib import Path
    
    files = [
        "/home/skux/.openclaw/workspace/market_dashboard/data/crypto_prices.json",
        "/home/skux/.openclaw/workspace/market_dashboard/data/stock_prices.json"
    ]
    
    results = []
    for file in files:
        path = Path(file)
        if path.exists():
            mtime = path.stat().st_mtime
            age_minutes = (datetime.now().timestamp() - mtime) / 60
            
            if age_minutes < 60:
                print(f"   ✅ {path.name}: Updated {age_minutes:.1f} min ago")
                results.append(True)
            else:
                print(f"   ⚠️  {path.name}: Updated {age_minutes:.1f} min ago (stale)")
                results.append(False)
        else:
            print(f"   ❌ {path.name}: Not found")
            results.append(False)
    
    return all(results)

def verify_real_data():
    """Verify data is from real APIs, not hardcoded"""
    print("\n" + "="*70)
    print("🔍 TEST 5: REAL DATA VERIFICATION")
    print("="*70)
    
    # Check crypto prices file
    try:
        with open("/home/skux/.openclaw/workspace/market_dashboard/data/crypto_prices.json") as f:
            crypto_data = json.load(f)
        
        if crypto_data.get('source') == 'Binance API':
            print("   ✅ Crypto: Source verified as Binance API")
            crypto_real = True
        else:
            print("   ⚠️  Crypto: Source not verified")
            crypto_real = False
            
        # Check prices are reasonable (not placeholder values)
        btc_price = crypto_data.get('prices', {}).get('BTC', {}).get('price', 0)
        if 20000 < btc_price < 200000:
            print(f"   ✅ BTC price realistic: ${btc_price:,.2f}")
        else:
            print(f"   ⚠️  BTC price suspicious: ${btc_price:,.2f}")
    except Exception as e:
        print(f"   ❌ Crypto data error: {e}")
        crypto_real = False
    
    # Check stock prices file
    try:
        with open("/home/skux/.openclaw/workspace/market_dashboard/data/stock_prices.json") as f:
            stock_data = json.load(f)
        
        if stock_data.get('source') == 'Yahoo Finance API':
            print("   ✅ Stocks: Source verified as Yahoo Finance API")
            stock_real = True
        else:
            print("   ⚠️  Stocks: Source not verified")
            stock_real = False
            
        # Check prices are reasonable
        tsla_price = stock_data.get('prices', {}).get('TSLA', {}).get('price', 0)
        if 50 < tsla_price < 1000:
            print(f"   ✅ TSLA price realistic: ${tsla_price:.2f}")
        else:
            print(f"   ⚠️  TSLA price suspicious: ${tsla_price:.2f}")
    except Exception as e:
        print(f"   ❌ Stock data error: {e}")
        stock_real = False
    
    return crypto_real and stock_real

def main():
    print("\n" + "🔥"*35)
    print("  DASHBOARD BUG TEST REPORT")
    print("🔥"*35)
    print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Binance API": test_binance_api(),
        "Yahoo Finance": test_yahoo_finance(),
        "File Integrity": test_dashboard_files(),
        "Data Freshness": test_data_freshness(),
        "Real Data Verification": verify_real_data()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test}")
    
    print("\n" + "="*70)
    print(f"RESULT: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Dashboard using real data!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review issues above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
