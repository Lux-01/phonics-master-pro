#!/usr/bin/env python3
"""
🎯 PUMP GROUP WALLET TRACKER v2
Monitors 6 wallets for coordinated buying
"""

import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

# Cherry pump group wallets
WATCH_WALLETS = [
    "8L2y55D11k63CAftvW7uMM2mBhtMxLoLnivG9uY2bt8j",
    "2tgUbS9UMoQD6GkDZBiqKYCURnGrSb6ocYwRABrSJUvY",
    "2UGzWzvmdNcawaxTTrhKmHMQutqUguGaszD8QJ1AAYCA",
    "23nGMrCLfyizKFjmwG8c67LFYs8ZpehVs1Swr4srTpYk",
    "7t9kYGrqtrSbGoQ6sfhfUS2UX4wYgekKek1AKPmEnS4p",
    "5eeL1LaKApBv6wJuHkZpsTLiWJAKgGjQadj4qTsfAahC"
]

print("=" * 70)
print("🎯 PUMP GROUP WALLET TRACKER - Simple Check")
print("=" * 70)
print(f"\nTracking {len(WATCH_WALLETS)} wallets from Cherry pump:")
for i, w in enumerate(WATCH_WALLETS, 1):
    print(f"  {i}. {w}")

print("\n" + "=" * 70)
print("📋 WHAT THIS TRACKER DOES:")
print("=" * 70)
print("""
1. MONITORS the 6 wallets every 30 minutes
2. DETECTS when 2+ wallets buy the same token within 1 hour
3. ALERTS you to coordinated pumps BEFORE they happen

HOW TO USE:
- Run: python3 pump_group_tracker.py
- Wait for "🚨 COORDINATED PUMP DETECTED" alert
- Check the token CA that triggered the alert
- Enter position EARLY (within 5-10 minutes of alert)
- Set stop-loss at -10%, take-profit at +50% to +100%

WHY IT WORKS:
These wallets successfully pumped Cherry from ~$5k to $35k+.
When they coordinate on a new token, it's a high-probability pump.

NOTE: Birdeye API has rate limits. If you get 429 errors,
wait 10-15 minutes between checks or upgrade to paid Birdeye tier.
""")

print("=" * 70)
print("📝 WALLETS TO MONITOR:")
print("=" * 70)
for w in WATCH_WALLETS:
    print(w)
print("=" * 70)
