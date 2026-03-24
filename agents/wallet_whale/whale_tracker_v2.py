#!/usr/bin/env python3
"""
WHALE WALLET TRACKER v2.0 - Multi-Wallet Copy Trading
Monitor multiple whale wallets for repeated buys and trigger Skylar purchases
"""

import json
import time
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import httpx
import subprocess

# Import Telegram alerts
try:
    from telegram_alerts import TelegramAlerter
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Telegram alerts not available")

# === CONFIG ===
CONFIG_FILE = "/home/skux/.openclaw/workspace/agents/wallet_whale/whale_config.json"

def load_config():
    """Load configuration from file"""
    with open(CONFIG_FILE) as f:
        return json.load(f)

CONFIG = load_config()

# === STATE MANAGEMENT ===
class MultiWhaleTracker:
    """Track multiple whale wallets and trigger Skylar trades"""
    
    def __init__(self):
        self.config = load_config()
        self.recent_buys = {}  # wallet -> {token_address: [timestamps]}
        self.triggered_tokens = set()
        self.last_trigger_time = None
        self.telegram = TelegramAlerter(self.config.get("telegram", {})) if TELEGRAM_AVAILABLE else None
        self._ensure_dirs()
        self._load_state()
        
    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.config["files"]["log_file"]), exist_ok=True)
        
    def _load_state(self):
        state_file = self.config["files"]["state_file"]
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.triggered_tokens = set(data.get("triggered_tokens", []))
                    self.last_trigger_time = data.get("last_trigger_time")
                    print(f"🔄 Loaded state: {len(self.triggered_tokens)} tokens tracked")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading state: {e}, starting fresh")
                self.triggered_tokens = set()
                self.last_trigger_time = None
        
    def save_state(self):
        state_file = self.config["files"]["state_file"]
        with open(state_file, 'w') as f:
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
        cooldown = timedelta(minutes=self.config["trigger_rules"]["cooldown_minutes_between_trades"])
        return datetime.now() - last > cooldown
    
    def get_enabled_wallets(self) -> List[Dict]:
        """Get list of enabled whale wallets"""
        return [w for w in self.config["target_wallets"] if w.get("enabled", True)]
    
    async def fetch_wallet_transactions(self, client: httpx.AsyncClient, wallet: Dict) -> List[Dict]:
        """Fetch recent transactions for a specific wallet"""
        wallet_address = wallet["address"]
        wallet_name = wallet.get("name", "Unknown")
        
        try:
            # Primary: Helius Enhanced API
            helius_key = os.getenv("HELIUS_API_KEY", "a2b25d8d-83d2-4d08-9ac5-87f50a3d40ce")
            url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
            params = {"api-key": helius_key, "limit": 20}
            resp = await client.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                txs = resp.json()
                return [{"wallet": wallet, "tx": tx} for tx in txs]
        except Exception as e:
            print(f"⚠️ Helius error for {wallet_name}: {e}")
        
        try:
            # Fallback: Birdeye
            birdeye_key = os.getenv("BIRDEYE_API_KEY", "6335463fca7340f9a2c73eacd5a37f64")
            url = f"https://public-api.birdeye.so/v1/wallet/tx_list"
            params = {
                "wallet": wallet_address,
                "limit": 20,
                "sort_by": "blockTime",
                "sort_order": "desc"
            }
            headers = {"X-API-KEY": birdeye_key}
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                txs = data.get("data", {}).get("txs", [])
                return [{"wallet": wallet, "tx": tx} for tx in txs]
        except Exception as e:
            print(f"⚠️ Birdeye error for {wallet_name}: {e}")
        
        return []
    
    def parse_token_buy(self, wallet_tx: Dict) -> Optional[Dict]:
        """Parse a transaction for token buy data"""
        wallet = wallet_tx["wallet"]
        tx = wallet_tx["tx"]
        wallet_address = wallet["address"]
        
        try:
            # Helius format
            if "nativeTransfers" in tx:
                transfers = tx.get("tokenTransfers", [])
                for transfer in transfers:
                    to = transfer.get("toUserAccount", "")
                    mint = transfer.get("mint", "")
                    if to == wallet_address and mint:
                        timestamp = tx.get("timestamp", int(time.time()))
                        if timestamp > 1e12:
                            timestamp = timestamp / 1000
                        return {
                            "token_address": mint,
                            "amount": float(transfer.get("tokenAmount", 0)),
                            "timestamp": int(timestamp),
                            "signature": tx.get("signature", ""),
                            "sol_amount": 0.1,
                            "source": "helius",
                            "wallet": wallet
                        }
            
            # Birdeye format
            if "tokenAddress" in tx:
                if tx.get("to") == wallet_address:
                    token_address = tx.get("tokenAddress", "")
                    if not token_address:
                        return None
                    timestamp = tx.get("blockTime", int(time.time()))
                    if timestamp > 1e12:
                        timestamp = timestamp / 1000
                    return {
                        "token_address": token_address,
                        "amount": float(tx.get("tokenAmount", 0)),
                        "timestamp": int(timestamp),
                        "signature": tx.get("txHash", ""),
                        "sol_amount": float(tx.get("solAmount", 0.1)),
                        "source": "birdeye",
                        "wallet": wallet
                    }
            
            return None
        except Exception as e:
            return None
    
    def check_buys_in_window(self, buys: List[Dict]) -> Optional[Dict]:
        """Check for trigger conditions across all wallets"""
        token_data = {}
        now = int(time.time())
        window = self.config["trigger_rules"]["time_window_seconds"]
        min_buys = self.config["trigger_rules"]["min_buys_to_trigger"]
        
        for buy in buys:
            token = buy.get("token_address", "")
            buy_time = buy.get("timestamp", 0)
            wallet = buy.get("wallet", {})
            
            # Skip invalid
            if not token or token == "So11111111111111111111111111111111111111112":
                continue
            if self.is_token_already_traded(token):
                continue
            if now - buy_time > window:
                continue
            
            if token not in token_data:
                token_data[token] = {
                    "buys": [],
                    "wallets": set(),
                    "total_sol": 0,
                    "wallet_buys": {}  # Track buys per wallet
                }
            
            token_data[token]["buys"].append(buy)
            token_data[token]["wallets"].add(wallet.get("address", ""))
            token_data[token]["total_sol"] += buy.get("sol_amount", 0.1)
            
            # Track per-wallet buy count
            wallet_addr = wallet.get("address", "")
            if wallet_addr not in token_data[token]["wallet_buys"]:
                token_data[token]["wallet_buys"][wallet_addr] = {
                    "count": 0,
                    "wallet": wallet
                }
            token_data[token]["wallet_buys"][wallet_addr]["count"] += 1
        
        # Check for triggers
        best_trigger = None
        best_score = 0
        
        for token, data in token_data.items():
            total_buys = len(data["buys"])
            unique_whales = len(data["wallets"])
            
            # Single whale with many buys
            single_whale_max = max(
                (wb["count"] for wb in data["wallet_buys"].values()),
                default=0
            )
            
            # Multi-whale signal (2+ whales buying same token)
            multi_whale_threshold = self.config["trigger_rules"].get("multi_whale_threshold", 2)
            
            score = 0
            trigger_type = None
            
            if single_whale_max >= min_buys:
                # Find the whale with most buys
                top_whale = max(
                    data["wallet_buys"].values(),
                    key=lambda x: x["count"]
                )
                score = single_whale_max * top_whale["wallet"].get("weight", 1.0)
                trigger_type = "single_whale"
            
            if unique_whales >= multi_whale_threshold:
                multi_score = unique_whales * 2.0  # Multi-whale bonus
                if multi_score > score:
                    score = multi_score
                    trigger_type = "multi_whale"
            
            if score > best_score:
                best_score = score
                best_trigger = {
                    "token_address": token,
                    "buys": data["buys"],
                    "total_buys": total_buys,
                    "unique_whales": unique_whales,
                    "total_sol": data["total_sol"],
                    "trigger_type": trigger_type,
                    "score": score
                }
        
        return best_trigger
    
    async def get_token_details(self, client: httpx.AsyncClient, token_address: str) -> Optional[Dict]:
        """Fetch token symbol and metadata"""
        try:
            birdeye_key = os.getenv("BIRDEYE_API_KEY", "6335463fca7340f9a2c73eacd5a37f64")
            url = f"https://public-api.birdeye.so/v1/summary"
            params = {"address": token_address}
            headers = {"X-API-KEY": birdeye_key}
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                token_data = data.get("data", {})
                return {
                    "symbol": token_data.get("symbol", "UNKNOWN"),
                    "name": token_data.get("name", "Unknown"),
                    "price": token_data.get("price", 0),
                    "mcap": token_data.get("mcap", 0)
                }
        except Exception as e:
            print(f"⚠️ Error fetching token details: {e}")
        
        return {"symbol": "UNKNOWN", "name": "Unknown", "price": 0, "mcap": 0}
    
    async def execute_skylar_trade(self, token_address: str, token_symbol: str) -> bool:
        """Execute trade via Skylar"""
        try:
            skylar_config = self.config["skylar_strategy"]
            
            # Import and execute
            sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')
            from full_auto_executor import execute_buy_auto
            
            wallet = self.config["skylar_wallet"]
            size = skylar_config["entry_size_sol"]
            
            print(f"🚀 Executing Skylar trade: {size} SOL -> {token_symbol}")
            
            result = execute_buy_auto(wallet, token_address, size, token_symbol)
            
            if result.get("status") == "executed":
                print(f"✅ Trade executed: {result.get('transaction_signature', 'N/A')}")
                
                # Telegram alert
                if self.telegram:
                    self.telegram.alert_trade_executed(
                        token_symbol, token_address, size,
                        result.get("transaction_signature", "")
                    )
                
                return True
            else:
                print(f"❌ Trade failed: {result.get('error', 'Unknown')}")
                
                if self.telegram:
                    self.telegram.alert_trade_failed(
                        token_symbol, result.get("error", "Unknown")
                    )
                
                return False
                
        except Exception as e:
            print(f"❌ Trade execution error: {e}")
            return False
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("🐳 MULTI-WHALE TRACKER v2.0")
        print("="*60)
        
        wallets = self.get_enabled_wallets()
        print(f"📊 Monitoring {len(wallets)} whale wallets:")
        for w in wallets:
            print(f"   • {w.get('name', 'Unknown')} (weight: {w.get('weight', 1.0)})")
        
        print(f"\n⏱️  Check interval: {self.config['monitoring']['check_interval_seconds']}s")
        print(f"🎯 Trigger: {self.config['trigger_rules']['min_buys_to_trigger']}+ buys in {self.config['trigger_rules']['time_window_seconds']}s")
        print(f"🔥 Multi-whale: {self.config['trigger_rules'].get('multi_whale_threshold', 2)}+ wallets on same token")
        print(f"⏳ Cooldown: {self.config['trigger_rules']['cooldown_minutes_between_trades']} min")
        print("="*60 + "\n")
        
        async with httpx.AsyncClient() as client:
            while self.config["monitoring"].get("enabled", True):
                try:
                    # Check cooldown
                    if not self.can_trigger():
                        if self.last_trigger_time:
                            last = datetime.fromisoformat(self.last_trigger_time)
                            elapsed = (datetime.now() - last).total_seconds() / 60
                            remaining = self.config["trigger_rules"]["cooldown_minutes_between_trades"] - elapsed
                            if remaining > 0:
                                print(f"⏳ Cooldown: {remaining:.1f} min remaining...")
                                if self.telegram:
                                    self.telegram.alert_cooldown_active(int(remaining))
                        await asyncio.sleep(self.config["monitoring"]["check_interval_seconds"])
                        continue
                    
                    # Fetch from all wallets
                    all_buys = []
                    for wallet in wallets:
                        wallet_txs = await self.fetch_wallet_transactions(client, wallet)
                        for wtx in wallet_txs:
                            buy = self.parse_token_buy(wtx)
                            if buy:
                                all_buys.append(buy)
                    
                    if all_buys:
                        print(f"📥 Found {len(all_buys)} recent buys across all wallets")
                        
                        # Check for triggers
                        trigger = self.check_buys_in_window(all_buys)
                        
                        if trigger:
                            token = trigger["token_address"]
                            print(f"\n🚨 TRIGGER DETECTED!")
                            print(f"   Token: {token}")
                            print(f"   Type: {trigger['trigger_type']}")
                            print(f"   Total buys: {trigger['total_buys']}")
                            print(f"   Unique whales: {trigger['unique_whales']}")
                            print(f"   Total SOL: {trigger['total_sol']:.2f}")
                            
                            # Get token details
                            details = await self.get_token_details(client, token)
                            symbol = details.get("symbol", "UNKNOWN")
                            
                            # Telegram alert
                            if self.telegram:
                                if trigger["trigger_type"] == "multi_whale":
                                    self.telegram.alert_multi_whale(
                                        symbol, token,
                                        trigger["unique_whales"],
                                        trigger["total_buys"]
                                    )
                                else:
                                    # Find top whale
                                    wallet_counts = {}
                                    for buy in trigger["buys"]:
                                        w_addr = buy["wallet"].get("address", "")
                                        wallet_counts[w_addr] = wallet_counts.get(w_addr, 0) + 1
                                    top_whale = max(wallet_counts.items(), key=lambda x: x[1])
                                    
                                    # Get wallet name
                                    wallet_name = "Unknown"
                                    for w in wallets:
                                        if w["address"] == top_whale[0]:
                                            wallet_name = w.get("name", "Unknown")
                                            break
                                    
                                    self.telegram.alert_whale_detected(
                                        wallet_name, symbol, token,
                                        top_whale[1], trigger["total_sol"],
                                        "HIGH" if trigger["score"] > 5 else "MEDIUM"
                                    )
                            
                            # Execute trade
                            success = await self.execute_skylar_trade(token, symbol)
                            
                            if success:
                                self.mark_token_traded(token)
                                print(f"✅ Token marked as traded")
                    
                    await asyncio.sleep(self.config["monitoring"]["check_interval_seconds"])
                    
                except Exception as e:
                    print(f"❌ Monitor loop error: {e}")
                    await asyncio.sleep(10)


# === MAIN ===
if __name__ == "__main__":
    import sys
    
    tracker = MultiWhaleTracker()
    
    try:
        asyncio.run(tracker.monitor_loop())
    except KeyboardInterrupt:
        print("\n👋 Tracker stopped by user")
        tracker.save_state()
