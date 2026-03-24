#!/usr/bin/env python3
"""
Solana Real-Time Token Monitor v6.0
WebSocket-based scanner for catching tokens at <1 minute old
Catches pumps before they pump
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import os
import sys

# Add parent path for imports
sys.path.insert(0, '/home/skux/.openclaw/workspace')

# Load Helius API key from auth.json
import json as _json
_auth_path = '/home/skux/.openclaw/agents/main/agent/auth.json'
try:
    with open(_auth_path, 'r') as _f:
        _auth = _json.load(_f)
        HELIUS_API_KEY = _auth.get('helius', {}).get('api_key', os.getenv("HELIUS_API_KEY", "a2b25d8d-83d2-4d08-9ac5-87f50a3d40ce"))
except Exception:
    HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "a2b25d8d-83d2-4d08-9ac5-87f50a3d40ce")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "6610224534"

class WebSocketTokenMonitor:
    """
    Real-time Solana token monitor
    Uses Helius WebSocket to catch new token mints instantly
    """
    
    def __init__(self):
        self.detected_tokens = []
        self.min_liquidity = 5000  # $5k min
        self.seen_cas = set()  # Deduplication
        self.ws_url = f"wss://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
        self.http_url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
        self.running = False
        
    async def connect(self):
        """Connect to Helius WebSocket with fallback to polling"""
        try:
            print(f"🔌 Connecting to Helius WebSocket...")
            print(f"   URL: {self.ws_url[:50]}...")
            
            async with websockets.connect(self.ws_url) as websocket:
                print(f"✅ Connected! Listening for new tokens...")
                
                # Subscribe to logs (new token mints)
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"]},
                        {"commitment": "processed"}
                    ]
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                # Listen for messages
                self.running = True
                while self.running:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=30.0
                        )
                        await self.handle_message(message)
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        ping_msg = {"jsonrpc": "2.0", "method": "ping"}
                        await websocket.send(json.dumps(ping_msg))
                        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            print(f"🔄 Falling back to high-frequency polling mode...")
            self.running = True
            await self.run_polling_mode()
            
    async def handle_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Check if it's a logs notification
            if data.get("method") == "logsNotification":
                params = data.get("params", {})
                result = params.get("result", {})
                value = result.get("value", {})
                logs = value.get("logs", [])
                
                # Look for token mint events
                for log in logs:
                    if "Instruction: MintTo" in log or "Create" in log:
                        signature = value.get("signature")
                        if signature:
                            await self.analyze_transaction(signature)
                            
        except Exception as e:
            print(f"⚠️ Error handling message: {e}")
    
    async def analyze_transaction(self, signature: str):
        """Analyze a transaction for new token mints"""
        try:
            url = f"https://api.helius.xyz/v0/transactions/?api-key={HELIUS_API_KEY}"
            resp = requests.post(url, json={"transactions": [signature]}, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                txs = data if isinstance(data, list) else [data]
                
                for tx in txs:
                    # Look for token transfers (mint events)
                    token_transfers = tx.get("tokenTransfers", [])
                    
                    for transfer in token_transfers:
                        mint = transfer.get("mint")
                        if mint and mint not in self.seen_cas:
                            self.seen_cas.add(mint)
                            
                            # Quick DexScreener check
                            await self.quick_check_token(mint)
                            
        except Exception as e:
            print(f"⚠️ Error analyzing tx: {e}")
    
    async def quick_check_token(self, ca: str):
        """Quick check on DexScreener for basic metrics"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            resp = requests.get(url, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", [])
                
                if pairs:
                    pair = pairs[0]  # Best pair
                    
                    symbol = pair.get("baseToken", {}).get("symbol", "?")
                    mcap = pair.get("marketCap", 0) or 0
                    liq = pair.get("liquidity", {}).get("usd", 0) or 0
                    vol = pair.get("volume", {}).get("h24", 0) or 0
                    
                    # Log all new tokens
                    print(f"\n🔔 NEW TOKEN DETECTED: {symbol}")
                    print(f"   CA: {ca}")
                    print(f"   MCAP: ${mcap:,.0f}")
                    print(f"   Liq: ${liq:,.0f}")
                    print(f"   Vol: ${vol:,.0f}")
                    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Score it
                    score = self.score_token(mcap, liq, vol)
                    
                    if score >= 12:  # Grade A threshold
                        await self.alert_high_grade({
                            "symbol": symbol,
                            "ca": ca,
                            "mcap": mcap,
                            "liq": liq,
                            "vol": vol,
                            "score": score,
                            "dex": pair.get("dexId", "?")
                        })
                        
        except Exception as e:
            print(f"⚠️ Error checking token: {e}")
    
    def score_token(self, mcap: float, liq: float, vol: float) -> int:
        """Quick scoring for real-time filtering"""
        score = 0
        
        # Market cap ($50K - $5M)
        if 50000 <= mcap <= 5000000:
            score += 5
        elif mcap > 0:
            score += 2
        
        # Liquidity ($10K +)
        if liq >= 50000:
            score += 5
        elif liq >= 20000:
            score += 3
        elif liq >= 10000:
            score += 2
        
        # Volume ($50K +)
        if vol >= 100000:
            score += 4
        elif vol >= 50000:
            score += 2
        elif vol >= 10000:
            score += 1
        
        # Volume / Market Cap ratio
        if mcap > 0 and vol / mcap > 0.5:
            score += 2
        
        return score
    
    async def alert_high_grade(self, token: Dict):
        """Send alert for high-grade tokens"""
        grade = "A+" if token["score"] >= 15 else "A"
        
        print(f"\n" + "="*70)
        print(f"🚨 GRADE {grade} TOKEN DETECTED!")
        print(f"="*70)
        print(f"   Symbol: {token['symbol']}")
        print(f"   Score: {token['score']}")
        print(f"   MCAP: ${token['mcap']:,.0f}")
        print(f"   Liq: ${token['liq']:,.0f}")
        print(f"   CA: {token['ca']}")
        print(f"   Dex: {token['dex']}")
        print(f"="*70)
        
        # Telegram alert
        if TELEGRAM_BOT_TOKEN:
            await self.send_telegram_alert(token, grade)
    
    async def run_polling_mode(self):
        """Fallback: High-frequency polling mode"""
        print("📡 Starting high-frequency polling (5-second intervals)...")
        print("   This catches tokens within 5-10 seconds of creation")
        
        seen_tokens = set()
        
        while self.running:
            try:
                # Poll DexScreener for new tokens
                searches = ['solana', 'new solana', 'meme solana', 'ai solana']
                
                for query in searches:
                    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                    resp = requests.get(url, timeout=10)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        for pair in data.get("pairs", []):
                            if pair.get("chainId") == "solana":
                                ca = pair.get("baseToken", {}).get("address")
                                if ca and ca not in seen_tokens and ca not in self.seen_cas:
                                    self.seen_cas.add(ca)
                                    seen_tokens.add(ca)
                                    
                                    # Quick analysis
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
                                    
                                    # Only alert on fresh tokens (< 1 hour)
                                    if age_hours < 1:
                                        score = self.score_token(mcap, liq, vol)
                                        
                                        print(f"\n🔔 NEW TOKEN: {symbol}")
                                        print(f"   CA: {ca}")
                                        print(f"   MCAP: ${mcap:,.0f}")
                                        print(f"   Liq: ${liq:,.0f}")
                                        print(f"   Age: {age_hours:.1f}h")
                                        print(f"   Score: {score}")
                                        
                                        if score >= 12:
                                            await self.alert_high_grade({
                                                "symbol": symbol,
                                                "ca": ca,
                                                "mcap": mcap,
                                                "liq": liq,
                                                "vol": vol,
                                                "score": score,
                                                "dex": pair.get("dexId", "?")
                                            })
                
                await asyncio.sleep(5)  # 5-second polling
                
            except Exception as e:
                print(f"⚠️ Polling error: {e}")
                await asyncio.sleep(5)

    async def send_telegram_alert(self, token: Dict, grade: str):
        """Send Telegram notification"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            
            message = f"""🚨 <b>REAL-TIME ALERT: Grade {grade}</b>

🔥 {token['symbol']} | Score: {token['score']}

📊 Metrics:
• MCAP: ${token['mcap']:,.0f}
• Liquidity: ${token['liq']:,.0f}
• Volume: ${token['vol']:,.0f}
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

class PollingBackup:
    """Backup scanner using traditional polling"""
    
    def __init__(self):
        self.seen_cas = set()
    
    async def run(self):
        """Run polling-based scan every 30 seconds"""
        while True:
            try:
                await self.scan_dexscreener()
                await asyncio.sleep(30)
            except Exception as e:
                print(f"⚠️ Polling error: {e}")
                await asyncio.sleep(30)
    
    async def scan_dexscreener(self):
        """Scan DexScreener for new tokens"""
        try:
            searches = ['solana', 'new solana', 'meme solana']
            
            for query in searches:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                resp = requests.get(url, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    for pair in data.get("pairs", []):
                        if pair.get("chainId") == "solana":
                            ca = pair.get("baseToken", {}).get("address")
                            if ca and ca not in self.seen_cas:
                                self.seen_cas.add(ca)
                                # Process new token...
                                
        except Exception as e:
            print(f"⚠️ Scan error: {e}")

async def main():
    """Main entry point"""
    print("="*70)
    print("🚀 WebSocket Token Monitor v6.0")
    print("   Real-time Solana token detection")
    print("="*70)
    print()
    
    monitor = WebSocketTokenMonitor()
    
    # Try WebSocket first, fallback to polling
    try:
        await monitor.connect()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        monitor.running = False
    except Exception as e:
        print(f"❌ WebSocket failed: {e}")
        print("🔄 Falling back to polling mode...")
        
        backup = PollingBackup()
        await backup.run()

if __name__ == "__main__":
    asyncio.run(main())
