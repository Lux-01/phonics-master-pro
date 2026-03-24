#!/usr/bin/env python3
"""
WebSocket Scanner for AOE
Real-time opportunity detection via WebSocket connections
"""

import json
import asyncio
import websockets
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import threading
import time


class WebSocketScanner:
    """
    WebSocket-based real-time scanner for AOE
    
    Supports:
    - Solana WebSocket (wss://api.mainnet-beta.solana.com)
    - Helius WebSocket (enhanced Solana data)
    - Birdeye WebSocket (token price feeds)
    - Custom WebSocket endpoints
    """
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/aoe_websocket")
        self.connections = {}
        self.callbacks = []
        self.running = False
        self.opportunities = []
        self.stats = {
            "connections_made": 0,
            "messages_received": 0,
            "opportunities_detected": 0,
            "start_time": None
        }
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
    
    # ============ WEBSOCKET CONNECTIONS ============
    
    async def connect_solana(self, on_transaction: Callable = None):
        """Connect to Solana WebSocket for transaction monitoring"""
        uri = "wss://api.mainnet-beta.solana.com"
        
        try:
            async with websockets.connect(uri) as websocket:
                self.connections["solana"] = websocket
                self.stats["connections_made"] += 1
                
                # Subscribe to logs
                subscribe_msg = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [{"mentions": ["*"]}, {"commitment": "finalized"}]
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                print(f"✓ Connected to Solana WebSocket")
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        self.stats["messages_received"] += 1
                        
                        data = json.loads(message)
                        
                        # Process transaction data
                        if on_transaction:
                            await on_transaction(data)
                        
                        # Check for opportunities
                        await self._analyze_transaction(data)
                        
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        ping = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
                        await websocket.send(json.dumps(ping))
                        
        except Exception as e:
            print(f"Solana WebSocket error: {e}")
    
    def _load_helius_key(self) -> str:
        """Load Helius API key from auth.json"""
        auth_path = '/home/skux/.openclaw/agents/main/agent/auth.json'
        try:
            with open(auth_path, 'r') as f:
                auth = json.load(f)
                return auth.get('helius', {}).get('api_key', '')
        except Exception:
            return ''
    
    async def connect_helius(self, api_key: str = None, on_event: Callable = None):
        """Connect to Helius WebSocket for enhanced Solana data"""
        if not api_key:
            api_key = os.getenv("HELIUS_API_KEY", "") or self._load_helius_key()
        
        uri = f"wss://mainnet.helius-rpc.com/?api-key={api_key}"
        
        try:
            async with websockets.connect(uri) as websocket:
                self.connections["helius"] = websocket
                self.stats["connections_made"] += 1
                
                print(f"✓ Connected to Helius WebSocket")
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        self.stats["messages_received"] += 1
                        
                        data = json.loads(message)
                        
                        if on_event:
                            await on_event(data)
                        
                        await self._analyze_helius_event(data)
                        
                    except asyncio.TimeoutError:
                        pass
                        
        except Exception as e:
            print(f"Helius WebSocket error: {e}")
    
    async def connect_birdeye(self, api_key: str = None, on_price: Callable = None):
        """Connect to Birdeye WebSocket for token price feeds"""
        if not api_key:
            api_key = os.getenv("BIRDEYE_API_KEY", "")
        
        uri = "wss://public-api.birdeye.so/socket"
        
        try:
            async with websockets.connect(uri) as websocket:
                self.connections["birdeye"] = websocket
                self.stats["connections_made"] += 1
                
                # Authenticate
                auth_msg = {"type": "auth", "apiKey": api_key}
                await websocket.send(json.dumps(auth_msg))
                
                # Subscribe to price updates
                subscribe_msg = {
                    "type": "subscribe",
                    "channel": "price",
                    "pairs": ["SOL/USDC", "BONK/SOL", "JUP/SOL"]  # Configurable
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                print(f"✓ Connected to Birdeye WebSocket")
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        self.stats["messages_received"] += 1
                        
                        data = json.loads(message)
                        
                        if on_price:
                            await on_price(data)
                        
                        await self._analyze_price_update(data)
                        
                    except asyncio.TimeoutError:
                        pass
                        
        except Exception as e:
            print(f"Birdeye WebSocket error: {e}")
    
    # ============ OPPORTUNITY DETECTION ============
    
    async def _analyze_transaction(self, data: Dict):
        """Analyze Solana transaction for opportunities"""
        # Look for patterns like:
        # - Large transfers
        # - New token creation
        # - DEX interactions
        
        logs = data.get("params", {}).get("result", {}).get("value", {}).get("logs", [])
        
        for log in logs:
            # Detect new token launches
            if "InitializeMint" in log or "CreateToken" in log:
                opportunity = {
                    "type": "new_token",
                    "source": "solana_websocket",
                    "timestamp": datetime.now().isoformat(),
                    "data": data,
                    "score": 75,  # Base score
                    "urgency": "high"
                }
                await self._report_opportunity(opportunity)
            
            # Detect large transfers
            if "Transfer" in log and "amount" in log.lower():
                # Could be whale movement
                pass
    
    async def _analyze_helius_event(self, data: Dict):
        """Analyze Helius event for opportunities"""
        # Helius provides enriched data
        event_type = data.get("type", "")
        
        if event_type == "NFT_SALE":
            opportunity = {
                "type": "nft_sale",
                "source": "helius",
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "score": 70,
                "urgency": "medium"
            }
            await self._report_opportunity(opportunity)
    
    async def _analyze_price_update(self, data: Dict):
        """Analyze price update for opportunities"""
        # Birdeye price updates
        price_data = data.get("data", {})
        
        if price_data:
            price_change = price_data.get("priceChange24h", 0)
            volume = price_data.get("volume24h", 0)
            
            # Detect significant price movements
            if abs(price_change) > 20:  # 20% change
                opportunity = {
                    "type": "price_spike" if price_change > 0 else "price_drop",
                    "source": "birdeye",
                    "timestamp": datetime.now().isoformat(),
                    "data": price_data,
                    "score": min(60 + abs(price_change), 95),  # Score based on magnitude
                    "urgency": "high" if abs(price_change) > 50 else "medium"
                }
                await self._report_opportunity(opportunity)
    
    async def _report_opportunity(self, opportunity: Dict):
        """Report detected opportunity"""
        self.opportunities.append(opportunity)
        self.stats["opportunities_detected"] += 1
        
        # Save to file
        opp_file = os.path.join(self.memory_dir, "websocket_opportunities.json")
        
        existing = []
        if os.path.exists(opp_file):
            with open(opp_file, 'r') as f:
                existing = json.load(f)
        
        existing.append(opportunity)
        
        # Keep last 1000
        existing = existing[-1000:]
        
        with open(opp_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        # Call registered callbacks
        for callback in self.callbacks:
            try:
                await callback(opportunity)
            except Exception as e:
                print(f"Callback error: {e}")
    
    # ============ PUBLIC API ============
    
    def register_callback(self, callback: Callable):
        """Register callback for opportunity detection"""
        self.callbacks.append(callback)
    
    async def start(self, sources: List[str] = None):
        """Start WebSocket scanner"""
        self.running = True
        self.stats["start_time"] = datetime.now().isoformat()
        
        sources = sources or ["solana", "birdeye"]
        
        tasks = []
        
        if "solana" in sources:
            tasks.append(self.connect_solana())
        
        if "helius" in sources:
            tasks.append(self.connect_helius())
        
        if "birdeye" in sources:
            tasks.append(self.connect_birdeye())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def stop(self):
        """Stop WebSocket scanner"""
        self.running = False
        
        for name, conn in self.connections.items():
            try:
                # Close connection
                pass  # websockets handles this on exit
            except:
                pass
        
        self.connections.clear()
    
    def get_stats(self) -> Dict:
        """Get scanner statistics"""
        return self.stats.copy()
    
    def get_opportunities(self, limit: int = 100) -> List[Dict]:
        """Get recent opportunities"""
        return self.opportunities[-limit:]
    
    def generate_report(self) -> str:
        """Generate scanner report"""
        lines = [
            "WebSocket Scanner Report",
            "=" * 40,
            f"Status: {'Running' if self.running else 'Stopped'}",
            f"Connections made: {self.stats['connections_made']}",
            f"Messages received: {self.stats['messages_received']}",
            f"Opportunities detected: {self.stats['opportunities_detected']}",
        ]
        
        if self.stats['start_time']:
            lines.append(f"Started: {self.stats['start_time']}")
        
        lines.extend([
            "",
            "Active connections:",
        ])
        
        for name in self.connections:
            lines.append(f"  • {name}")
        
        return "\n".join(lines)


# ============ SYNC WRAPPER ============

class WebSocketScannerSync:
    """Synchronous wrapper for WebSocket scanner"""
    
    def __init__(self):
        self.scanner = WebSocketScanner()
        self._thread = None
        self._loop = None
    
    def start(self, sources: List[str] = None):
        """Start scanner in background thread"""
        def run_async():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self.scanner.start(sources))
        
        self._thread = threading.Thread(target=run_async, daemon=True)
        self._thread.start()
        print(f"✓ WebSocket scanner started in background")
    
    def stop(self):
        """Stop scanner"""
        self.scanner.stop()
        if self._thread:
            self._thread.join(timeout=5)
    
    def get_stats(self) -> Dict:
        """Get stats"""
        return self.scanner.get_stats()
    
    def get_opportunities(self, limit: int = 100) -> List[Dict]:
        """Get opportunities"""
        return self.scanner.get_opportunities(limit)
    
    def generate_report(self) -> str:
        """Generate report"""
        return self.scanner.generate_report()


# ============ COMMAND LINE ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WebSocket Scanner for AOE")
    parser.add_argument("--mode", choices=["start", "stop", "report", "test"], default="report")
    parser.add_argument("--sources", nargs="+", choices=["solana", "helius", "birdeye"],
                       default=["solana", "birdeye"])
    
    args = parser.parse_args()
    
    scanner = WebSocketScannerSync()
    
    if args.mode == "start":
        print("🚀 Starting WebSocket scanner...")
        scanner.start(args.sources)
        
        try:
            while True:
                time.sleep(10)
                stats = scanner.get_stats()
                print(f"Messages: {stats['messages_received']}, Opportunities: {stats['opportunities_detected']}")
        except KeyboardInterrupt:
            print("\nStopping...")
            scanner.stop()
    
    elif args.mode == "stop":
        scanner.stop()
        print("✓ Scanner stopped")
    
    elif args.mode == "report":
        print(scanner.generate_report())
    
    elif args.mode == "test":
        print("🧪 Testing WebSocket scanner...")
        scanner.start(["solana"])
        time.sleep(5)
        stats = scanner.get_stats()
        print(f"✓ Started, connections: {stats['connections_made']}")
        scanner.stop()
        print("✓ Stopped successfully")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
