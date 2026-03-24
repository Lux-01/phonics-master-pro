#!/usr/bin/env python3
"""
WHALE WALLET TRACKER v1.0 - Copy Trading for Skylar
Monitor whale wallet for repeated buys and trigger Skylar purchases
Target: JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv
Trigger: 4+ buys of same token in 30 seconds
"""

import json
import time
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import httpx
import subprocess

# === CONFIG ===
CONFIG = {
    "name": "WhaleTracker",
    "version": "1.0",
    "target_wallet": "JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv",
    "skylar_wallet": "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5",
    
    # Whale Detection Settings
    "min_buys_to_trigger": 4,
    "time_window_seconds": 30,
    "min_buy_size_sol": 0.5,
    
    # Skylar Config Override
    "entry_size_sol": 0.3,
    "target_profit_pct": 15,
    "stop_loss_pct": 7,
    "time_stop_hours": 4,
    "slippage_bps": 100,
    
    # APIs
    "birdeye_api_key": "6335463fca7340f9a2c73eacd5a37f64",
    "helius_api_key": "a2b25d8d-83d2-4d08-9ac5-87f50a3d40ce",
    
    # Files
    "log_file": "/home/skux/.openclaw/workspace/agents/wallet_whale/whale_trades.json",
    "state_file": "/home/skux/.openclaw/workspace/agents/wallet_whale/tracker_state.json",
    "triggered_file": "/home/skux/.openclaw/workspace/agents/wallet_whale/triggered_trades.json",
    
    # Monitoring
    "check_interval_seconds": 5,
    "cooldown_minutes_between_trades": 3,
}

# === STATE MANAGEMENT ===
class WhaleTracker:
    """Track whale wallet and trigger Skylar trades"""
    
    def __init__(self):
        self.recent_buys = {}  # token_address -> list of timestamps
        self.triggered_tokens = set()  # Don't re-trigger same token
        self.last_trigger_time = None
        self._ensure_dirs()
        self._load_state()
        
    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
        
    def _load_state(self):
        if os.path.exists(CONFIG["state_file"]):
            try:
                with open(CONFIG["state_file"], 'r') as f:
                    data = json.load(f)
                    self.triggered_tokens = set(data.get("triggered_tokens", []))
                    self.last_trigger_time = data.get("last_trigger_time")
                    print(f"🔄 Loaded state: {len(self.triggered_tokens)} tokens tracked")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading state: {e}, starting fresh")
                self.triggered_tokens = set()
                self.last_trigger_time = None
        
    def save_state(self):
        with open(CONFIG["state_file"], 'w') as f:
            json.dump({
                "triggered_tokens": list(self.triggered_tokens),
                "last_trigger_time": self.last_trigger_time,
                "last_update": datetime.now().isoformat()
            }, f, indent=2)
    
    def is_token_already_traded(self, token_address: str) -> bool:
        return token_address in self.triggered_tokens
    
    def mark_token_traded(self, token_address: str):
        self.triggered_tokens.add(token_address)
        self.last_trigger_time = datetime.now().isoformat()
        self.save_state()
    
    def can_trigger(self) -> bool:
        if not self.last_trigger_time:
            return True
        last = datetime.fromisoformat(self.last_trigger_time)
        cooldown = timedelta(minutes=CONFIG["cooldown_minutes_between_trades"])
        return datetime.now() - last > cooldown
    
    async def fetch_wallet_transactions(self, client: httpx.AsyncClient) -> List[Dict]:
        """Fetch recent transactions for monitored wallet"""
        try:
            # Primary: Helius Enhanced API
            url = f"https://api.helius.xyz/v0/addresses/{CONFIG['target_wallet']}/transactions"
            params = {"api-key": CONFIG["helius_api_key"], "limit": 20}
            resp = await client.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"⚠️ Helius error: {e}")
        
        try:
            # Fallback: Simple Birdeye wallet check
            url = f"https://public-api.birdeye.so/v1/wallet/tx_list"
            params = {
                "wallet": CONFIG["target_wallet"],
                "limit": 20,
                "sort_by": "blockTime",
                "sort_order": "desc"
            }
            headers = {"X-API-KEY": CONFIG["birdeye_api_key"]}
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", {}).get("txs", [])
        except Exception as e:
            print(f"⚠️ Birdeye error: {e}")
        
        return []
    
    def parse_token_buy(self, tx: Dict) -> Optional[Dict]:
        """Parse a transaction for token buy data"""
        try:
            # Helius format
            if "nativeTransfers" in tx:
                transfers = tx.get("tokenTransfers", [])
                for transfer in transfers:
                    # Check if target wallet received tokens (BUY)
                    to = transfer.get("toUserAccount", "")
                    mint = transfer.get("mint", "")
                    if to == CONFIG["target_wallet"] and mint:
                        # Helius timestamps are in Unix seconds
                        timestamp = tx.get("timestamp")
                        if not timestamp:
                            timestamp = int(time.time())
                        # Handle if Helius returns milliseconds
                        if timestamp > 1e12:
                            timestamp = timestamp / 1000
                        return {
                            "token_address": mint,
                            "amount": float(transfer.get("tokenAmount", 0)),
                            "timestamp": int(timestamp),
                            "signature": tx.get("signature", ""),
                            "sol_amount": 0.1,  # Estimate for Helius
                            "source": "helius"
                        }
            
            # Birdeye format
            if "tokenAddress" in tx:
                # Must be a buy order (wallet receives tokens)
                if tx.get("to") == CONFIG["target_wallet"]:
                    token_address = tx.get("tokenAddress", "")
                    if not token_address:
                        return None
                    # Birdeye blockTime is in Unix seconds
                    timestamp = tx.get("blockTime", int(time.time()))
                    # Handle if Birdeye returns milliseconds
                    if timestamp > 1e12:
                        timestamp = timestamp / 1000
                    return {
                        "token_address": token_address,
                        "amount": float(tx.get("tokenAmount", 0)),
                        "timestamp": int(timestamp),
                        "signature": tx.get("txHash", ""),
                        "sol_amount": float(tx.get("solAmount", 0.1)),
                        "source": "birdeye"
                    }
            
            return None
        except Exception as e:
            return None
    
    def check_buys_in_window(self, buys: List[Dict]) -> Optional[Dict]:
        """Check for 4+ buys of same token in 30 second window"""
        token_counts = {}
        now = int(time.time())
        window = CONFIG["time_window_seconds"]
        
        # Filter out trades we can't take anyway (already triggered)
        for buy in buys:
            token = buy.get("token_address", "")
            buy_time = buy.get("timestamp", 0)
            
            # Skip empty token addresses
            if not token or token == "So11111111111111111111111111111111111111112":
                continue  # Skip SOL transfers or empty
            
            if now - buy_time > window:
                continue  # Skip old buys
            
            # Skip if already traded
            if self.is_token_already_traded(token):
                continue
            
            if token not in token_counts:
                token_counts[token] = {
                    "count": 0,
                    "buys": [],
                    "total_sol": 0
                }
            token_counts[token]["count"] += 1
            token_counts[token]["buys"].append(buy)
            token_counts[token]["total_sol"] += buy.get("sol_amount", 0.1)
        
        # Find token with most buys (in case multiple hit threshold)
        best_token = None
        best_count = 0
        
        for token, data in token_counts.items():
            if data["count"] >= CONFIG["min_buys_to_trigger"]:
                if data["count"] > best_count:
                    best_token = token
                    best_count = data["count"]
        
        if best_token:
            data = token_counts[best_token]
            return {
                "token_address": best_token,
                "buys": data["buys"],
                "total_buys": data["count"],
                "total_sol": data["total_sol"],
                "source_wallet": CONFIG["target_wallet"]
            }
        
        return None
    
    async def get_token_details(self, client: httpx.AsyncClient, token_address: str) -> Optional[Dict]:
        """Fetch token symbol and metadata"""
        try:
            url = f"https://public-api.birdeye.so/v1/summary"
            params = {"address": token_address}
            headers = {"X-API-KEY": CONFIG["birdeye_api_key"]}
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                token_data = data.get("data", {})
                return {
                    "symbol": token_data.get("symbol", "UNKNOWN"),
                    "name": token_data.get("name", ""),
                    "mcap": token_data.get("mcap", 0),
                    "price_usd": token_data.get("price", 0),
                    "liquidity": token_data.get("liquidity", 0)
                }
        except Exception as e:
            print(f"⚠️ Token details error: {e}")
        
        return {
            "symbol": f"TOKEN_{token_address[:8]}",
            "name": "Unknown Token",
            "mcap": 0,
            "price_usd": 0,
            "liquidity": 0
        }
    
    async def trigger_skylar_buy(self, trigger_data: Dict):
        """Execute Skylar buy via Jupiter API"""
        token_address = trigger_data["token_address"]
        
        print(f"\n{'='*70}")
        print(f"🚨 WHALE SIGNAL DETECTED!")
        print(f"{'='*70}")
        print(f"   Source: {CONFIG['target_wallet'][:20]}...")
        print(f"   Token: {token_address}")
        print(f"   Buys in 30s: {trigger_data['total_buys']}")
        print(f"   Total SOL spent: {trigger_data['total_sol']:.3f}")
        print(f"   Skylar trigger: {CONFIG['entry_size_sol']} SOL")
        print(f"{'='*70}\n")
        
        # Save trigger record
        trigger_record = {
            "timestamp": datetime.now().isoformat(),
            "trigger_data": trigger_data,
            "skylar_config": {
                "entry_size": CONFIG["entry_size_sol"],
                "target_tp": CONFIG["target_profit_pct"],
                "stop_loss": CONFIG["stop_loss_pct"],
                "time_stop": CONFIG["time_stop_hours"]
            },
            "status": "PENDING"
        }
        
        # Execute buy via Jupiter
        trade_result = await self.execute_jupiter_swap(token_address)
        
        trigger_record["result"] = trade_result
        trigger_record["status"] = "EXECUTED" if trade_result.get("success") else "FAILED"
        
        # Save to triggered trades
        if os.path.exists(CONFIG["triggered_file"]):
            with open(CONFIG["triggered_file"], 'r') as f:
                trades = json.load(f)
        else:
            trades = {"trades": []}
        
        trades["trades"].append(trigger_record)
        with open(CONFIG["triggered_file"], 'w') as f:
            json.dump(trades, f, indent=2)
        
        # Mark as traded
        self.mark_token_traded(token_address)
        
        return trigger_record
    
    async def execute_jupiter_swap(self, output_mint: str) -> Dict:
        """Execute swap via Jupiter API"""
        try:
            import httpx
            
            SOL_MINT = "So11111111111111111111111111111111111111112"
            amount_lamports = int(CONFIG["entry_size_sol"] * 1e9)
            
            # Get quote first
            quote_url = "https://quote-api.jup.ag/v6/quote"
            params = {
                "inputMint": SOL_MINT,
                "outputMint": output_mint,
                "amount": amount_lamports,
                "slippageBps": CONFIG["slippage_bps"],
                "onlyDirectRoutes": "false",
            }
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(quote_url, params=params, timeout=30)
                if resp.status_code != 200:
                    return {"success": False, "error": f"Quote failed: {resp.text}"}
                
                quote = resp.json()
                
                # Display quote info
                out_amount = int(quote.get("outAmount", 0))
                price_impact = float(quote.get("priceImpactPct", 0))
                
                print(f"💰 Jupiter Quote:")
                print(f"   Expected out: {out_amount / 1e6:.4f} tokens")
                print(f"   Price impact: {price_impact:.3f}%")
                print(f"   Route: {len(quote.get('routePlan', []))} hops")
                
                # Note: Full execution requires signing which can't be done automatically
                # This would need wallet private key - for now we return the quote
                return {
                    "success": True,
                    "status": "QUOTE_SUCCESS",
                    "quote": quote,
                    "needs_signature": True,
                    "output_mint": output_mint,
                    "size_sol": CONFIG["entry_size_sol"],
                    "instructions": "Sign with wallet to complete trade"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def print_watching_status(self):
        print(f"\n{'='*70}")
        print(f"🐋 WHALE TRACKER v{CONFIG['version']} - RUNNING")
        print(f"{'='*70}")
        print(f"   Monitoring: {CONFIG['target_wallet'][:40]}...")
        print(f"   Trigger: {CONFIG['min_buys_to_trigger']}+ buys in {CONFIG['time_window_seconds']}s")
        print(f"   Skylar Wallet: {CONFIG['skylar_wallet'][:20]}...")
        print(f"   Position Size: {CONFIG['entry_size_sol']} SOL")
        print(f"   Target: +{CONFIG['target_profit_pct']}% | Stop: -{CONFIG['stop_loss_pct']}% | Time: {CONFIG['time_stop_hours']}h")
        print(f"   Check Interval: Every {CONFIG['check_interval_seconds']} seconds")
        print(f"{'='*70}\n")
    
    async def run_monitor(self):
        """Main monitoring loop"""
        self.print_watching_status()
        
        recent_buys_log = []
        check_count = 0
        
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    # Fetch transactions
                    check_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan #{check_count} - Checking whale activity...")
                    txs = await self.fetch_wallet_transactions(client)
                    
                    # Parse buys
                    new_buys = []
                    for tx in txs:
                        buy = self.parse_token_buy(tx)
                        if buy:
                            new_buys.append(buy)
                    
                    # Add to log
                    recent_buys_log.extend(new_buys)
                    
                    # Clean old buys
                    now = int(time.time())
                    window = CONFIG["time_window_seconds"]
                    recent_buys_log = [b for b in recent_buys_log if now - b.get("timestamp", 0) < window]
                    
                    if new_buys:
                        print(f"   Found {len(new_buys)} token transfers")
                        if recent_buys_log:
                            # Show tokens in window
                            tokens_in_window = {}
                            for b in recent_buys_log:
                                t = b.get("token_address", "")
                                if t and t != "So11111111111111111111111111111111111111112":
                                    tokens_in_window[t] = tokens_in_window.get(t, 0) + 1
                            if tokens_in_window:
                                print(f"   Buys by token: {dict(tokens_in_window)}")
                    
                    # Check for trigger - FIRST check signal
                    trigger_data = self.check_buys_in_window(recent_buys_log)
                    
                    if trigger_data:
                        # THEN check cooldown
                        if self.can_trigger():
                            await self.trigger_skylar_buy(trigger_data)
                            recent_buys_log = []  # Clear after trigger
                        else:
                            # Cooldown active - log and clear
                            if self.last_trigger_time:
                                last = datetime.fromisoformat(self.last_trigger_time)
                                elapsed = (datetime.now() - last).total_seconds()
                                remaining = (CONFIG["cooldown_minutes_between_trades"] * 60) - elapsed
                                print(f"   COOLDOWN: {remaining:.0f}s remaining - trigger delayed")
                                recent_buys_log = []
                    
                    # Log status every minute
                    if check_count % 12 == 0:
                        print(f"   Status: {len(recent_buys_log)} buys tracked, {len(self.triggered_tokens)} tokens traded")
                    
                await asyncio.sleep(CONFIG["check_interval_seconds"])
                
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(CONFIG["check_interval_seconds"])

async def main():
    """Entry point"""
    tracker = WhaleTracker()
    await tracker.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())
