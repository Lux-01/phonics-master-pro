#!/usr/bin/env python3
"""
🎯 WALLET COPY TRADING STRATEGY
Buy when target wallet buys, sell when in profit

Strategy:
- Monitor specific wallet(s) via Helius/Helium API
- Detect BUY transactions
- Copy the buy (with configurable size)
- Sell when profit threshold reached (e.g., +10%, +20%)
- Hard stop loss (e.g., -15%)
"""

import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# CONFIGURATION
CONFIG = {
    "name": "WalletCopyTrader",
    "version": "1.0",
    
    # Target wallets to copy
    "target_wallets": [
        "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    ],
    
    # Mode
    "mode": "PAPER",                 # PAPER or LIVE (PAPER = track only, LIVE = execute)
    
    # Settings
    "position_size_sol": 0.01,      # Size to copy with
    "profit_target_pct": 15,         # Sell when +15% profit
    "stop_loss_pct": 15,             # Stop loss -15%
    "max_hold_hours": 4,             # Time stop (4 hours)
    "min_token_mc": 5000,            # Min market cap to trade
    "max_token_mc": 500000,          # Max market cap
    "slippage_bps": 150,             # 1.5% slippage
    
    # API Keys
    "helius_api_key": "350aa83c-44a4-4068-a511-580f82930d84",
    "birdeye_api_key": "6335463fca7340f9a2c73eacd5a37f64",
    
    # Files
    "state_file": "/home/skux/.openclaw/workspace/agents/wallet_tracker/wallet_tracker_state.json",
    "trade_log": "/home/skux/.openclaw/workspace/agents/wallet_tracker/wallet_tracker_trades.json",
    "log_file": "/home/skux/.openclaw/workspace/agents/wallet_tracker/wallet_tracker.log",
}

class TradeStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SOLD_PROFIT = "sold_profit"
    SOLD_LOSS = "sold_loss"
    SOLD_TIMEOUT = "sold_timeout"

@dataclass
class Position:
    position_id: str
    target_wallet: str
    token_address: str
    token_symbol: str
    entry_price: float
    entry_amount_sol: float
    entry_time: str
    target_tx: str
    status: TradeStatus = TradeStatus.ACTIVE
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    pnl_pct: float = 0.0
    pnl_sol: float = 0.0
    exit_reason: str = ""

class WalletCopyTrader:
    """Copy trades from target wallets"""
    
    def __init__(self):
        self.positions: List[Position] = []
        self.monitored_txs: set = set()
        self._ensure_dirs()
        self._load_state()
        
    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(CONFIG["state_file"]), exist_ok=True)
        
    def log(self, msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {msg}"
        print(log_line)
        with open(CONFIG["log_file"], "a") as f:
            f.write(log_line + "\n")
            
    def save_state(self):
        state = {
            "last_update": datetime.now().isoformat(),
            "positions": [asdict(p) for p in self.positions],
            "monitored_txs": list(self.monitored_txs)
        }
        with open(CONFIG["state_file"], "w") as f:
            json.dump(state, f, indent=2)
            
    def _load_state(self):
        if os.path.exists(CONFIG["state_file"]):
            with open(CONFIG["state_file"], "r") as f:
                state = json.load(f)
                for p_data in state.get("positions", []):
                    p_data["status"] = TradeStatus(p_data["status"])
                    self.positions.append(Position(**p_data))
                self.monitored_txs = set(state.get("monitored_txs", []))
                self.log(f"📂 Loaded {len(self.positions)} positions from state")
    
    def get_wallet_transactions(self, wallet: str, limit: int = 20) -> List[Dict]:
        """Get recent transactions for a wallet via Helius"""
        url = f"https://mainnet.helius-rpc.com/?api-key={CONFIG['helius_api_key']}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet, {"limit": limit}]
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("result", [])
        except Exception as e:
            self.log(f"⚠️ Helius error: {e}")
        return []
    
    def get_transaction_details(self, signature: str) -> Optional[Dict]:
        """Get detailed transaction info"""
        url = f"https://mainnet.helius-rpc.com/?api-key={CONFIG['helius_api_key']}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("result", {})
        except Exception as e:
            self.log(f"⚠️ Tx fetch error: {e}")
        return None
    
    def analyze_token(self, token_address: str) -> Optional[Dict]:
        """Quick token analysis via Birdeye"""
        url = f"https://public-api.birdeye.so/public/price?address={token_address}"
        headers = {"x-api-key": CONFIG['birdeye_api_key']}
        
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                
                # Get market cap from token list
                list_url = "https://public-api.birdeye.so/defi/tokenlist?sort_by=mc&sort_type=desc&offset=0&limit=500"
                list_resp = requests.get(list_url, headers=headers, timeout=5)
                
                mc = 0
                symbol = "?"
                if list_resp.status_code == 200:
                    list_data = list_resp.json()
                    for token in list_data.get("data", {}).get("tokens", []):
                        if token.get("address") == token_address:
                            mc = float(token.get("mc", 0) or 0)
                            symbol = token.get("symbol", "?")
                            break
                
                return {
                    "price": data.get("data", {}).get("value", 0),
                    "mc": mc,
                    "symbol": symbol,
                    "address": token_address
                }
        except Exception as e:
            self.log(f"⚠️ Birdeye error: {e}")
        return None
    
    def is_buy_transaction(self, tx: Dict, wallet: str) -> Optional[Dict]:
        """Check if transaction is a token buy"""
        if not tx:
            return None
            
        meta = tx.get("meta", {})
        pre_balances = meta.get("preTokenBalances", [])
        post_balances = meta.get("postTokenBalances", [])
        
        token_changes = {}
        
        # Track token balance changes for the wallet
        for pre in pre_balances:
            owner = pre.get("owner")
            if owner == wallet:
                mint = pre.get("mint")
                amount = pre.get("uiTokenAmount", {}).get("uiAmount", 0)
                token_changes[mint] = {"pre": amount, "post": 0}
        
        for post in post_balances:
            owner = post.get("owner")
            if owner == wallet:
                mint = post.get("mint")
                amount = post.get("uiTokenAmount", {}).get("uiAmount", 0)
                if mint in token_changes:
                    token_changes[mint]["post"] = amount
                else:
                    token_changes[mint] = {"pre": 0, "post": amount}
        
        # Find tokens where balance increased (buy)
        for mint, changes in token_changes.items():
            if changes["post"] > changes["pre"] and changes["post"] > 0:
                bought_amount = changes["post"] - changes["pre"]
                
                # Skip SOL/USDC/etc
                if mint in ["So11111111111111111111111111111111111111112", 
                           "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"]:
                    continue
                
                return {
                    "token_address": mint,
                    "amount_bought": bought_amount,
                    "signature": tx.get("transaction", {}).get("signatures", [""])[0]
                }
        
        return None
    
    def should_copy_buy(self, token_data: Dict) -> bool:
        """Check if we should copy this buy"""
        mc = token_data.get("mc", 0)
        
        if mc < CONFIG["min_token_mc"]:
            self.log(f"   ⛔ MC too low: ${mc:,.0f}")
            return False
            
        if mc > CONFIG["max_token_mc"]:
            self.log(f"   ⛔ MC too high: ${mc:,.0f}")
            return False
        
        # Check if already in this token
        for pos in self.positions:
            if pos.status == TradeStatus.ACTIVE and pos.token_address == token_data["address"]:
                self.log(f"   ⛔ Already holding {token_data['symbol']}")
                return False
        
        self.log(f"   ✅ Token qualifies: {token_data['symbol']} @ ${mc:,.0f} MC")
        return True
    
    def execute_buy(self, token_address: str, token_data: Dict, target_tx: str, wallet: str) -> Optional[Position]:
        """Execute a copy buy"""
        self.log(f"\n💰 EXECUTING COPY BUY")
        self.log(f"   Token: {token_data['symbol']}")
        self.log(f"   Amount: {CONFIG['position_size_sol']} SOL")
        self.log(f"   Entry Price: ${token_data['price']:.6f}")
        
        # In live mode, this would call Jupiter/Solana
        # For now, record the simulated position
        
        now = datetime.now().isoformat()
        position_id = f"COPY_{int(time.time())}"
        
        position = Position(
            position_id=position_id,
            target_wallet=wallet,
            token_address=token_address,
            token_symbol=token_data["symbol"],
            entry_price=token_data["price"],
            entry_amount_sol=CONFIG["position_size_sol"],
            entry_time=now,
            target_tx=target_tx,
            status=TradeStatus.ACTIVE
        )
        
        self.positions.append(position)
        self.save_state()
        
        self.log(f"   ✅ Position recorded: {position_id}")
        
        return position
    
    def check_exit_conditions(self, position: Position) -> Optional[str]:
        """Check if position should be closed"""
        # Get current price
        token_data = self.analyze_token(position.token_address)
        if not token_data:
            return None
            
        current_price = token_data["price"]
        if current_price <= 0:
            return None
        
        # Calculate P&L
        pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        
        # Check profit target
        if pnl_pct >= CONFIG["profit_target_pct"]:
            return f"PROFIT +{pnl_pct:.1f}%"
        
        # Check stop loss
        if pnl_pct <= -CONFIG["stop_loss_pct"]:
            return f"STOP_LOSS {pnl_pct:.1f}%"
        
        # Check time stop
        entry_time = datetime.fromisoformat(position.entry_time)
        hours_held = (datetime.now() - entry_time).total_seconds() / 3600
        if hours_held >= CONFIG["max_hold_hours"]:
            return f"TIME_STOP {hours_held:.1f}h"
        
        return None
    
    def execute_sell(self, position: Position, reason: str):
        """Execute sell"""
        self.log(f"\n🔴 EXECUTING SELL")
        self.log(f"   Position: {position.position_id}")
        self.log(f"   Token: {position.token_symbol}")
        self.log(f"   Reason: {reason}")
        
        # Get current price
        token_data = self.analyze_token(position.token_address)
        if token_data:
            exit_price = token_data["price"]
            pnl_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
            pnl_sol = position.entry_amount_sol * (pnl_pct / 100)
            
            position.exit_price = exit_price
            position.exit_time = datetime.now().isoformat()
            position.pnl_pct = pnl_pct
            position.pnl_sol = pnl_sol
            position.exit_reason = reason
            
            if "PROFIT" in reason:
                position.status = TradeStatus.SOLD_PROFIT
                self.log(f"   🎉 PROFIT: +{pnl_pct:.1f}% | +{pnl_sol:.4f} SOL")
            elif "STOP_LOSS" in reason:
                position.status = TradeStatus.SOLD_LOSS
                self.log(f"   😢 LOSS: {pnl_pct:.1f}% | {pnl_sol:.4f} SOL")
            else:
                position.status = TradeStatus.SOLD_TIMEOUT
                self.log(f"   ⏰ TIMEOUT: {pnl_pct:.1f}% | {pnl_sol:.4f} SOL")
            
            self.save_state()
            
            # Log to file
            with open(CONFIG["trade_log"], "a") as f:
                f.write(json.dumps(asdict(position), default=str) + "\n")
    
    def monitor_target_wallets(self):
        """Main monitoring loop"""
        self.log("\n" + "="*70)
        self.log("🎯 WALLET COPY TRADER")
        self.log("="*70)
        self.log(f"Monitoring {len(CONFIG['target_wallets'])} wallets")
        self.log(f"Position size: {CONFIG['position_size_sol']} SOL per trade")
        self.log(f"Profit target: +{CONFIG['profit_target_pct']}%")
        self.log(f"Stop loss: -{CONFIG['stop_loss_pct']}%")
        self.log(f"Time stop: {CONFIG['max_hold_hours']} hours")
        self.log("="*70)
        
        for wallet in CONFIG["target_wallets"]:
            self.log(f"\n📡 Checking wallet: {wallet[:8]}...{wallet[-8:]}")
            
            # Get recent transactions
            txs = self.get_wallet_transactions(wallet, limit=10)
            self.log(f"   Found {len(txs)} recent transactions")
            
            for tx_info in txs:
                sig = tx_info.get("signature")
                if sig in self.monitored_txs:
                    continue
                    
                self.monitored_txs.add(sig)
                
                # Get full transaction details
                tx = self.get_transaction_details(sig)
                if not tx:
                    continue
                
                # Check if it's a buy
                buy_info = self.is_buy_transaction(tx, wallet)
                if buy_info:
                    self.log(f"\n   🎯 BUY DETECTED!")
                    self.log(f"   Token: {buy_info['token_address'][:20]}...")
                    self.log(f"   Amount: {buy_info['amount_bought']:,.2f}")
                    
                    # Analyze the token
                    token_data = self.analyze_token(buy_info["token_address"])
                    if token_data:
                        if self.should_copy_buy(token_data):
                            self.execute_buy(
                                buy_info["token_address"],
                                token_data,
                                sig,
                                wallet
                            )
    
    def monitor_positions(self):
        """Check active positions for exit conditions"""
        self.log("\n📊 Monitoring active positions...")
        
        active_count = sum(1 for p in self.positions if p.status == TradeStatus.ACTIVE)
        self.log(f"   Active positions: {active_count}")
        
        for position in self.positions:
            if position.status != TradeStatus.ACTIVE:
                continue
            
            exit_reason = self.check_exit_conditions(position)
            if exit_reason:
                self.execute_sell(position, exit_reason)
    
    def run_cycle(self):
        """Run one full monitoring cycle"""
        self.monitor_target_wallets()
        self.monitor_positions()
        self.save_state()
    
    def get_summary(self) -> str:
        """Get trading summary"""
        total_trades = len(self.positions)
        active = sum(1 for p in self.positions if p.status == TradeStatus.ACTIVE)
        profit_sells = sum(1 for p in self.positions if p.status == TradeStatus.SOLD_PROFIT)
        loss_sells = sum(1 for p in self.positions if p.status == TradeStatus.SOLD_LOSS)
        
        total_pnl = sum(p.pnl_sol for p in self.positions if p.status != TradeStatus.ACTIVE)
        
        return f"""
📊 WALLET COPY TRADER SUMMARY
═══════════════════════════════════════
Total Trades: {total_trades}
Active: {active}
Profit Exits: {profit_sells}
Stop Loss: {loss_sells}
Total P&L: {total_pnl:+.4f} SOL
Win Rate: {(profit_sells/max(1, profit_sells+loss_sells))*100:.1f}%
"""


def main():
    trader = WalletCopyTrader()
    
    # Check if wallets configured
    if not CONFIG["target_wallets"]:
        print("⚠️ No target wallets configured!")
        print("Edit CONFIG['target_wallets'] in the script")
        return
    
    # Run one cycle
    trader.run_cycle()
    
    # Show summary
    print(trader.get_summary())
    
    print("\n✅ Cycle complete. Run again to continue monitoring.")
    print(f"State saved to: {CONFIG['state_file']}")


if __name__ == "__main__":
    main()
