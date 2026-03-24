#!/usr/bin/env python3
"""Debug version to test the breakout detection"""
import requests
import time

BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BASE_URL = "https://public-api.birdeye.so"
HEADERS = {"X-API-KEY": BIRDEYE_API_KEY, "accept": "application/json"}

# Test with Pippin
address = "Dfh5DzRgSvvCFDoYc2ciTkMrbDfRKybA4SoFbPmApump"
symbol = "pippin"

print(f"Testing breakout detection on {symbol}...")

# Get 8 hours of data
end = int(time.time())
start = end - (8 * 3600)

url = f"{BASE_URL}/defi/ohlcv"
params = {"address": address, "type": "15m", "time_from": start, "time_to": end}
resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
data = resp.json()

if data.get("success"):
    history = data["data"]["items"]
    print(f"Got {len(history)} candles")
    
    # Look for breakout signals
    for i in range(24, len(history) - 1):
        print("Keys:", history[0].keys())
        price_6h = history[i - 24]["c"]
        current = history[i]["c"]
        volume = history[i]["v"]
        
        # Calculate average volume
        avg_vol = sum(h["v"] for h in history[i-25:i]) / 25
        vol_ratio = volume / avg_vol if avg_vol > 0 else 0
        
        change = (current - price_6h) / price_6h
        
        if i == len(history) - 5 or i == 24:  # Check first and some middle values
            print(f"\nCandle {i}:")
            print(f"  Price 6h ago: {price_6h:.6f}")
            print(f"  Current: {current:.6f}")
            print(f"  Change: {change*100:.2f}%")
            print(f"  Volume: {volume:.0f}")
            print(f"  Avg Volume: {avg_vol:.0f}")
            print(f"  Volume Ratio: {vol_ratio:.2f}x")
            print(f"  Entry Signal: {change >= 0.05 and vol_ratio >= 2.0}")
else:
    print("Failed to get data:", data)
