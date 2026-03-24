#!/usr/bin/env python3
"""
WebSocket Token Monitor v6.0 - High-Frequency Scanner
Catches tokens within 5-10 seconds of creation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Set
import os
import sys

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "6610224534"

class HighFrequencyScanner:
    """
    High-frequency polling scanner
    Checks every 5 seconds for new tokens
    """
    
    def __init__(self):
        self.seen_cas: Set[str] = set()
        self.running = True
        self.check_count = 0
        
    def run(self):
        """Main scanning loop"""
        print("="*70)
        print("🚀 WebSocket Token Monitor v6.0")
        print("   High-Frequency Polling Mode (5-second intervals)")
        print("="*70)
        print(f"\n⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📡 Scanning for new tokens...")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                self.check_count += 1
                self.scan_cycle()
                
                # Show progress every 12 cycles (1 minute)
                if self.check_count % 12 == 0:
                    print(f"⏱️  {self.check_count} checks completed... {datetime.now().strftime('%H:%M:%S')}")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopping scanner...")
            self.print_summary()
    
    def scan_cycle(self):
        """Single scan cycle"""
        searches = ['solana', 'new solana', 'meme solana', 'ai solana']
        
        for query in searches:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                resp = requests.get(url, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    for pair in data.get("pairs", []):
                        if pair.get("chainId") == "solana":
                            self.process_pair(pair)
                            
            except Exception as e:
                pass  # Silent fail for individual requests
    
    def process_pair(self, pair: Dict):
        """Process a token pair"""
        ca = pair.get("baseToken", {}).get("address")
        if not ca or ca in self.seen_cas:
            return
        
        self.seen_cas.add(ca)
        
        # Get metrics
        symbol = pair.get("baseToken", {}).get("symbol", "?")
        mcap = pair.get("marketCap", 0) or 0
        liq = pair.get("liquidity", {}).get("usd", 0) or 0
        vol = pair.get("volume", {}).get("h24", 0) or 0
        
        # Calculate age
        pair_created = pair.get("pairCreatedAt", 0)
        if pair_created:
            age_hours = (time.time() * 1000 - pair_created) / (1000 * 3600)
        else:
            age_hours = 999
        
        # Only process fresh tokens (< 2 hours)
        if age_hours < 2:
            score = self.score_token(mcap, liq, vol)
            
            print(f"\n🔔 NEW TOKEN: {symbol}")
            print(f"   CA: {ca}")
            print(f"   MCAP: ${mcap:,.0f} | Liq: ${liq:,.0f}")
            print(f"   Age: {age_hours:.1f}h | Score: {score}")
            
            if score >= 12:
                self.alert_high_grade({
                    "symbol": symbol,
                    "ca": ca,
                    "mcap": mcap,
                    "liq": liq,
                    "vol": vol,
                    "score": score,
                    "dex": pair.get("dexId", "?"),
                    "age_hours": age_hours
                })
    
    def score_token(self, mcap: float, liq: float, vol: float) -> int:
        """Score a token"""
        score = 0
        
        # Market cap ($50K - $5M)
        if 50000 <= mcap <= 5000000:
            score += 5
        elif mcap > 0:
            score += 2
        
        # Liquidity
        if liq >= 50000:
            score += 5
        elif liq >= 20000:
            score += 3
        elif liq >= 10000:
            score += 2
        
        # Volume
        if vol >= 100000:
            score += 4
        elif vol >= 50000:
            score += 2
        elif vol >= 10000:
            score += 1
        
        # Volume/MC ratio
        if mcap > 0 and vol / mcap > 0.5:
            score += 2
        
        return score
    
    def alert_high_grade(self, token: Dict):
        """Alert for high-grade tokens"""
        grade = "A+" if token["score"] >= 15 else "A" if token["score"] >= 12 else "A-"
        
        print("\n" + "="*70)
        print(f"🚨 GRADE {grade} TOKEN DETECTED!")
        print("="*70)
        print(f"   Symbol: {token['symbol']}")
        print(f"   Score: {token['score']}")
        print(f"   MCAP: ${token['mcap']:,.0f}")
        print(f"   Liq: ${token['liq']:,.0f}")
        print(f"   Age: {token['age_hours']:.1f}h")
        print(f"   CA: {token['ca']}")
        print(f"   Dex: {token['dex']}")
        print("="*70)
        
        # Send Telegram alert
        if TELEGRAM_BOT_TOKEN:
            self.send_telegram_alert(token, grade)
    
    def send_telegram_alert(self, token: Dict, grade: str):
        """Send Telegram notification"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            
            message = f"""🚨 <b>REAL-TIME ALERT: Grade {grade}</b>

🔥 {token['symbol']} | Score: {token['score']}

📊 Metrics:
• MCAP: ${token['mcap']:,.0f}
• Liquidity: ${token['liq']:,.0f}
• Volume: ${token['vol']:,.0f}
• Age: {token['age_hours']:.1f}h
• Dex: {token['dex']}

⚡ <b>Detected at {datetime.now().strftime('%H:%M:%S')}</b>

<code>{token['ca']}</code>

<a href='https://dexscreener.com/solana/{token['ca']}'>📈 DexScreener</a>
<a href='https://jup.ag/swap/{token['ca']}-SOL'>🚀 Quick Buy</a>"""
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"   📱 Telegram alert sent!")
        except Exception as e:
            print(f"   ⚠️ Telegram error: {e}")
    
    def print_summary(self):
        """Print summary when stopping"""
        print("\n" + "="*70)
        print("📊 SCAN SUMMARY")
        print("="*70)
        print(f"   Total checks: {self.check_count}")
        print(f"   Unique tokens seen: {len(self.seen_cas)}")
        print(f"   Runtime: {self.check_count * 5 // 60} minutes")
        print("="*70)

if __name__ == "__main__":
    scanner = HighFrequencyScanner()
    scanner.run()
