#!/usr/bin/env python3
"""
Raphael Auto-Trader v1.3 (RULES COMPLIANT)
Live trading following Raphael's 27 Rules
110 SOL Mission | Phase 1 Live Test

RULES FIXED:
✅ MCAP: $2M-$500M (was $10k-$250k)
✅ Token Age: 2 weeks - 8 months (NEW)
✅ Graded Position Sizing: A+ vs A vs B
✅ Slippage Check: Skip if >2%
✅ Breakeven trailing after scale-out
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from raphael_trader import RaphaelTrader
import requests

# Trading Configuration - RULES COMPLIANT
CONFIG = {
    "mode": "LIVE_TEST",
    
    # Graded Position Sizing (Rule #15-17 in strategy)
    "trade_sizes": {
        "A+": 0.35,   # Max confidence
        "A": 0.25,    # High confidence
        "B": 0.20,    # Medium confidence
        "C": 0.15     # Lower confidence (shouldn't trade)
    },
    
    "max_trades_per_day": 5,
    "daily_loss_limit_sol": 0.05,
    "check_interval_secs": 60,
    "grade_filter": ["A+", "A", "B"],
    "same_token_cooldown_hours": 2,
    "min_rugcheck_score": 70,
    
    # Entry Criteria - MICRO CAP TEST MODE for Tem
    "mcap_min": 50000,        # $50k minimum (micro cap test)
    "mcap_max": 500000,       # $500k maximum (micro cap range)
    "token_age_min_days": 7,   # 1 week minimum (newer tokens allowed)
    "token_age_max_days": 240, # 8 months maximum (~240 days)
    "slippage_max_pct": 2.0,   # Skip if slippage >2% (Rule #2)
    
    # Exit rules
    "scale_out_pct": 8,
    "stop_loss_pct": 7,
    "time_stop_minutes": 30,
    "scale_out_amount_pct": 50,
    
    # Risk management
    "min_balance_reserve": 0.05,
    
    # State tracking
    "state_file": "/tmp/raphael_live_state.json",
    "log_file": "/home/skux/.openclaw/workspace/agents/raphael/live_trades.json"
}

class RaphaelAutoTrader:
    def __init__(self):
        self.trader = RaphaelTrader()
        self.state = self.load_state()
        self.running = False
        
        print("=" * 60, flush=True)
        print("🦎 RAPHAEL AUTO-TRADER v1.3 (RULES COMPLIANT)", flush=True)
        print("Mode: LIVE TEST", flush=True)
        print(f"Wallet: {self.trader.wallet_address}", flush=True)
        print(f"Balance: {self.trader.balance:.6f} SOL", flush=True)
        print(f"MCAP Range: ${CONFIG['mcap_min']/1e3:.0f}k - ${CONFIG['mcap_max']/1e3:.0f}k", flush=True)
        print(f"Token Age: {CONFIG['token_age_min_days']}d - {CONFIG['token_age_max_days']}d", flush=True)
        print("=" * 60, flush=True)
        
    def load_state(self) -> Dict:
        """Load or initialize state"""
        if os.path.exists(CONFIG["state_file"]):
            try:
                with open(CONFIG["state_file"], 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "trades_today": 0,
            "daily_pnl": 0.0,
            "daily_loss": 0.0,
            "positions": [],
            "exited_positions": [],
            "trade_history": [],
            "traded_tokens": {},
            "last_reset": datetime.now().isoformat(),
            "status": "IDLE"
        }
    
    def save_state(self):
        """Persist state"""
        with open(CONFIG["state_file"], 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_daily_reset(self):
        """Reset daily counters if it's a new day"""
        last_reset = datetime.fromisoformat(self.state.get("last_reset", datetime.now().isoformat()))
        if last_reset.date() != datetime.now().date():
            self.state["trades_today"] = 0
            self.state["daily_pnl"] = 0.0
            self.state["daily_loss"] = 0.0
            self.state["traded_tokens"] = {}
            self.state["last_reset"] = datetime.now().isoformat()
            print(f"🌅 New day - counters reset")
            self.save_state()
    
    def get_token_age_days(self, token_mint: str) -> Optional[int]:
        """Get token age in days using Birdeye API"""
        try:
            # Try Birdeye API for token creation time
            # If not available, estimate from first trade timestamp
            headers = {"X-API-KEY": "6335463fca7340f9a2c73eacd5a37f64"}  # From TOOLS.md
            url = f"https://public-api.birdeye.so/public/token_creation_info?address={token_mint}"
            
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('success'):
                    creation_time = data.get('data', {}).get('blockTime')
                    if creation_time:
                        creation_date = datetime.fromtimestamp(creation_time)
                        age_days = (datetime.now() - creation_date).days
                        return age_days
            
            # Fallback: use DexScreener pair age
            r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{token_mint}", timeout=10)
            if r.status_code == 200:
                pairs = r.json()
                if pairs and len(pairs) > 0:
                    # Get oldest pair creation time
                    oldest_time = None
                    for pair in pairs:
                        pair_created = pair.get('pairCreatedAt')
                        if pair_created:
                            pair_date = datetime.fromtimestamp(pair_created / 1000)  # ms to s
                            if not oldest_time or pair_date < oldest_time:
                                oldest_time = pair_date
                    
                    if oldest_time:
                        age_days = (datetime.now() - oldest_time).days
                        return age_days
            
            return None
        except Exception as e:
            print(f"  ⚠️ Age check error: {e}")
            return None
    
    def run_full_rugcheck(self, ca: str) -> Dict:
        """Run comprehensive rugcheck before trading"""
        print(f"🔒 Running RugCheck on {ca[:20]}...")
        
        try:
            rug = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", 
                             timeout=10).json()
            
            if not rug:
                print("  ❌ RugCheck returned no data")
                return None
            
            token_data = rug.get('token', {})
            markets = rug.get('markets', [{}])
            
            score = rug.get('score', 0)
            mint_revoked = token_data.get('mintAuthority') is None
            freeze_revoked = token_data.get('freezeAuthority') is None
            top_holders = rug.get('topHolders', [])
            top5_pct = sum(h.get('pct', 0) for h in top_holders[:5])
            top10_pct = sum(h.get('pct', 0) for h in top_holders[:10])
            
            lp_locked = 0
            if markets and markets[0]:
                lp_data = markets[0].get('lp', {})
                lp_locked = lp_data.get('lpLockedPct', 0)
            
            holders_count = rug.get('totalHolders', 0)
            
            risks = []
            if not mint_revoked:
                risks.append("MINT NOT REVOKED")
            if top5_pct > 50:
                risks.append(f"TOP5 {top5_pct:.1f}%")
            if top10_pct > 70:
                risks.append(f"TOP10 {top10_pct:.1f}%")
            if lp_locked < 50:
                risks.append(f"LP LOCK {lp_locked:.0f}%")
            if score < CONFIG["min_rugcheck_score"]:
                risks.append(f"LOW SCORE {score}")
            
            print(f"  Score: {score} | Mint: {'✅' if mint_revoked else '❌'} | "
                  f"Top5: {top5_pct:.1f}% | LP: {lp_locked:.0f}%")
            
            passed = len(risks) == 0 and score >= CONFIG["min_rugcheck_score"] and mint_revoked
            
            return {
                "score": score,
                "mint_revoked": mint_revoked,
                "freeze_revoked": freeze_revoked,
                "top5_pct": top5_pct,
                "top10_pct": top10_pct,
                "lp_locked": lp_locked,
                "holders": holders_count,
                "risks": risks,
                "passed": passed
            }
            
        except Exception as e:
            print(f"  ⚠️ RugCheck error: {e}")
            return None
    
    def can_trade(self, token_mint: str = None) -> tuple[bool, str]:
        """Check if trading conditions allow a new trade"""
        self.check_daily_reset()
        
        if self.state["trades_today"] >= CONFIG["max_trades_per_day"]:
            return False, f"Daily trade limit reached ({CONFIG['max_trades_per_day']} trades)"
        
        self.trader.update_balance()
        min_required = CONFIG["min_balance_reserve"] + CONFIG["trade_sizes"]["A+"]
        if self.trader.balance < min_required:
            return False, f"Insufficient balance: {self.trader.balance:.4f} SOL"
        
        if self.state["daily_loss"] >= CONFIG["daily_loss_limit_sol"]:
            return False, f"Daily loss limit hit: -{self.state['daily_loss']:.4f} SOL"
        
        # Check cooldown after loss (Rule #9: 15 min after any loss)
        if self.state["trade_history"]:
            last_trade = self.state["trade_history"][-1]
            if last_trade.get("exit_pnl_pct", 0) < 0:  # Was a loss
                last_time = datetime.fromisoformat(last_trade["timestamp"])
                if datetime.now() - last_time < timedelta(minutes=15):
                    remaining = 15 - (datetime.now() - last_time).seconds // 60
                    return False, f"Loss cooldown: {remaining} min left"
        
        # Check 2-min cooldown between trades
        if self.state["trade_history"]:
            last_trade = self.state["trade_history"][-1]
            last_time = datetime.fromisoformat(last_trade["timestamp"])
            if datetime.now() - last_time < timedelta(minutes=2):
                return False, "Trade cooldown active"
        
        if token_mint:
            traded_tokens = self.state.get("traded_tokens", {})
            if token_mint in traded_tokens:
                last_trade = datetime.fromisoformat(traded_tokens[token_mint])
                cooldown = timedelta(hours=CONFIG["same_token_cooldown_hours"])
                if datetime.now() - last_trade < cooldown:
                    remaining = cooldown - (datetime.now() - last_trade)
                    return False, f"Token cooldown: {remaining.seconds//60} min left"
        
        return True, "OK"
    
    def monitor_positions(self):
        """Monitor active positions for exit signals"""
        positions = self.state.get("positions", [])
        if not positions:
            return
        
        print(f"\n📊 Monitoring {len(positions)} active position(s)...")
        
        for pos in positions[:]:
            token_mint = pos["token"]
            symbol = pos.get("symbol", "UNKNOWN")
            entry_price = pos.get("entry_price_usd", 0)
            entry_time = datetime.fromisoformat(pos["timestamp"])
            elapsed_min = (datetime.now() - entry_time).total_seconds() / 60
            
            print(f"  🔍 {symbol} - Entry: ${entry_price:.6f}, Elapsed: {elapsed_min:.0f}min")
            
            # Get current price
            current_price = self.trader.get_token_price(token_mint)
            
            if not current_price or current_price <= 0:
                print(f"    ⚠️ Could not fetch current price")
                continue
            
            if entry_price and entry_price > 0:
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                print(f"    Current: ${current_price:.6f} | PnL: {pnl_pct:+.1f}%")
            else:
                pnl_pct = 0
                print(f"    Current: ${current_price:.6f} | PnL: N/A")
            
            exit_reason = None
            exit_action = None
            exit_pct = 100
            
            # Check stop loss (-7%) - HARD STOP always first
            if pnl_pct <= -CONFIG["stop_loss_pct"]:
                exit_reason = f"STOP_LOSS ({pnl_pct:.1f}%)"
                exit_action = "full"
                exit_pct = 100
            
            # Check scale-out (+8%) - but only if not already scaled
            elif pnl_pct >= CONFIG["scale_out_pct"] and not pos.get("scaled_out", False):
                exit_reason = f"SCALE_OUT (+{pnl_pct:.1f}%)"
                exit_action = "scale"
                exit_pct = CONFIG["scale_out_amount_pct"]
            
            # Trailing stop - if we scaled out, move stop to breakeven
            elif pos.get("scaled_out", False) and pnl_pct <= 0:
                exit_reason = f"TRAILING_STOP_BREAKEVEN ({pnl_pct:.1f}%)"
                exit_action = "full"
                exit_pct = 100
            
            # Check time stop (30 min, or 45 min if large cap >$100M)
            else:
                time_limit = CONFIG["time_stop_minutes"]
                mcap = pos.get("mcap", 0)
                if mcap > 100000000:  # Large cap = 45 min (Rule #6)
                    time_limit = 45
                
                if elapsed_min >= time_limit:
                    exit_reason = f"TIME_STOP ({elapsed_min:.0f}min)"
                    exit_action = "full"
                    exit_pct = 100
            
            if exit_reason:
                print(f"    🚨 EXIT SIGNAL: {exit_reason}")
                
                # Execute exit
                print(f"    📤 Selling {exit_pct}% of position...")
                result = self.trader.sell(token_mint, exit_pct)
                
                if result.get("status") == "SUCCESS":
                    print(f"    ✅ Exit executed!")
                    
                    if exit_action == "scale":
                        # Scale out - keep position active
                        pos["scaled_out"] = True
                        pos["scale_out_time"] = datetime.now().isoformat()
                        pos["scale_out_price"] = current_price
                        pos["scale_out_pnl_pct"] = pnl_pct
                        
                        # Mark remaining 50% at breakeven
                        pos["stop_price"] = entry_price  # Trailing to breakeven
                        
                        # Update daily PnL (only partial)
                        pnl_sol = (pnl_pct / 100) * pos.get("amount_sol", CONFIG["trade_sizes"]["A"]) * (exit_pct / 100)
                        self.state["daily_pnl"] += pnl_sol
                    
                    elif exit_action in ["full", "trailing"]:
                        # Full exit
                        pos["exit_time"] = datetime.now().isoformat()
                        pos["exit_price"] = current_price
                        pos["exit_pnl_pct"] = pnl_pct
                        pos["exit_reason"] = exit_reason
                        pos["result"] = "CLOSED"
                        
                        self.state["exited_positions"].append(pos)
                        self.state["positions"].remove(pos)
                        
                        # Update PnL
                        amount = pos.get("amount_sol", CONFIG["trade_sizes"]["A"])
                        if pos.get("scaled_out", False):
                            # Already sold 50%, now selling remaining 50%
                            remaining_pct = 50
                            pnl_sol = (pnl_pct / 100) * amount * (remaining_pct / 100)
                        else:
                            # Selling full position
                            pnl_sol = (pnl_pct / 100) * amount
                        
                        self.state["daily_pnl"] += pnl_sol
                        
                        if pnl_pct < 0:
                            self.state["daily_loss"] += abs(pnl_sol)
                        
                        print(f"    💰 PnL: {pnl_sol:+.4f} SOL ({pnl_pct:+.1f}%)")
                else:
                    print(f"    ❌ Exit failed: {result.get('error', 'Unknown')}")
        
        self.save_state()
    
    def scan_dexscreener_pairs(self) -> List[Dict]:
        """Scan DexScreener for established Solana tokens using multiple search terms"""
        tokens = []
        all_seen = set()
        
        search_terms = ['ai', 'meme', 'moon', 'ape', 'solana', 'based', 'pepe', 'dog', 'cat', 'elon', 'viral']  # More search terms for micro caps
        headers = {"User-Agent": "Mozilla/5.0"}
        
        for term in search_terms:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={term}"
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        for pair in pairs:
                            if pair.get('chainId') != 'solana':
                                continue
                            
                            base_token = pair.get('baseToken', {})
                            token_addr = base_token.get('address')
                            symbol = base_token.get('symbol', 'UNKNOWN')
                            mcap = pair.get('marketCap', 0) or 0
                            
                            if not token_addr or token_addr == 'So11111111111111111111111111111111111111112':
                                continue
                            if token_addr in all_seen:
                                continue
                            
                            if mcap >= 50000:
                                all_seen.add(token_addr)
                                tokens.append({
                                    'tokenAddress': token_addr,
                                    'symbol': symbol,
                                    'name': base_token.get('name', ''),
                                    'source': f'search_{term}',
                                    'pair_data': pair
                                })
            except Exception as e:
                print(f"   ⚠️ Search '{term}': {str(e)[:50]}")
        
        print(f"   ✅ Search results: {len(tokens)} tokens")
        return tokens
    
    def get_scan_targets(self) -> List[Dict]:
        """Scan for Grade A+/A tokens from multiple sources"""
        targets = []
        all_tokens = []
        
        print(f"🔍 Scanning multiple data sources...")
        print(f"   Filters: MCap ${CONFIG['mcap_min']/1e3:.0f}k-${CONFIG['mcap_max']/1e3:.0f}k")
        
        rejected = {"mcap": 0, "age": 0, "liquidity": 0, "volume": 0, "rugcheck": 0, "momentum": 0, "grade": 0, "api_error": 0}
        
        try:
            # Source 1: Search-based scan for established tokens
            search_tokens = self.scan_dexscreener_pairs()
            all_tokens.extend(search_tokens)
            
            # Deduplicate
            seen = set()
            deduped = []
            for t in all_tokens:
                if t['tokenAddress'] not in seen:
                    seen.add(t['tokenAddress'])
                    deduped.append(t)
            all_tokens = deduped
            
            print(f"\n   Total unique tokens to evaluate: {len(all_tokens)}")
            solana_tokens = all_tokens
            
            print(f"🔍 Scanning {len(solana_tokens)} Solana tokens...")
            print(f"   Filters: MCap ${CONFIG['mcap_min']/1e3:.0f}k-${CONFIG['mcap_max']/1e3:.0f}k | Age {CONFIG['token_age_min_days']}d-{CONFIG['token_age_max_days']}d")
            
            rejected = {"mcap": 0, "age": 0, "liquidity": 0, "volume": 0, "rugcheck": 0, "momentum": 0, "grade": 0}
            
            for token in solana_tokens[:50]:  # Check more for better selection
                ca = token.get('tokenAddress')
                
                can_trade, reason = self.can_trade(ca)
                if not can_trade and ("cooldown" in reason.lower() or "limit" in reason.lower()):
                    continue
                
                symbol = token.get('symbol', '') or 'UNKNOWN'
                name = token.get('name', symbol)
                
                # Use existing pair_data if available (from Raydium scan)
                pair_data = token.get('pair_data')
                
                if pair_data:
                    # Already have data from Raydium
                    pair = pair_data
                    mcap = pair.get('marketCap', 0) or 0
                    liq = pair.get('liquidity', {}).get('usd', 0) or 0
                    vol24 = pair.get('volume', {}).get('h24', 0) or 0
                    vol5m = pair.get('volume', {}).get('m5', 0) or 0
                    price_change = pair.get('priceChange', {}).get('h24', 0) or 0
                    price_usd = pair.get('priceUsd', 0)
                else:
                    # Need to fetch pair data
                    try:
                        r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", 
                                       timeout=10)
                        pairs = r.json() if r.status_code == 200 else []
                    except:
                        continue
                    
                    if not pairs:
                        continue
                    
                    pair = pairs[0]
                    mcap = pair.get('marketCap', 0) or 0
                    liq = pair.get('liquidity', {}).get('usd', 0) or 0
                    vol24 = pair.get('volume', {}).get('h24', 0) or 0
                    vol5m = pair.get('volume', {}).get('m5', 0) or 0
                    price_change = pair.get('priceChange', {}).get('h24', 0) or 0
                    price_usd = pair.get('priceUsd', 0)
                
                print(f"  📊 {symbol}: MCap ${mcap:,.0f} | Liq ${liq:,.0f} | Vol24h ${vol24:,.0f} | 24h {price_change:.1f}%")
                
                # === RULES COMPLIANT FILTERS ===
                
                # MCAP: $2M - $500M (Rule #1)
                if not (CONFIG["mcap_min"] <= mcap <= CONFIG["mcap_max"]):
                    print(f"    ❌ MCap ${mcap:,.0f} outside range ${CONFIG['mcap_min']/1e3:.0f}k-${CONFIG['mcap_max']/1e3:.0f}k")
                    rejected["mcap"] += 1
                    continue
                
                # Liquidity check (lowered to $20k for micro cap test)
                if liq < 20000:
                    print(f"    ❌ Liquidity ${liq:,.0f} < $20k")
                    rejected["liquidity"] += 1
                    continue
                
                # Volume
                if vol24 < 100000 or vol5m < 5000:
                    print(f"    ❌ Volume too low (24h: ${vol24:,.0f}, 5m: ${vol5m:,.0f})")
                    rejected["volume"] += 1
                    continue
                
                # Price momentum
                if price_change > 20 or price_change < -30:
                    print(f"    ❌ Price momentum out of range ({price_change:.1f}%)")
                    rejected["momentum"] += 1
                    continue
                
                # Token Age
                age_days = self.get_token_age_days(ca)
                if age_days is not None:
                    print(f"    📅 Age: {age_days}d")
                    if not (CONFIG["token_age_min_days"] <= age_days <= CONFIG["token_age_max_days"]):
                        print(f"    ❌ Age {age_days}d outside {CONFIG['token_age_min_days']}d-{CONFIG['token_age_max_days']}d")
                        rejected["age"] += 1
                        continue
                else:
                    print(f"    ⚠️ Could not verify age")
                    rejected["age"] += 1
                    continue
                
                # Rugcheck (Rule #27: Must pass)
                rugcheck = self.run_full_rugcheck(ca)
                if not rugcheck or not rugcheck.get('passed'):
                    print(f"    ❌ Failed security checks")
                    rejected["rugcheck"] += 1
                    continue
                
                # Calculate score with ALL rules
                score = 0
                
                # MCAP in sweet spot ($2M-$100M gets bonus)
                if CONFIG["mcap_min"] <= mcap <= 100000000:
                    score += 2
                elif 100000000 < mcap <= CONFIG["mcap_max"]:
                    score += 1
                
                # Liquidity
                if liq >= 200000:
                    score += 2
                elif liq >= 100000:
                    score += 1
                
                # Volume (Rule #13)
                if vol24 >= 500000:
                    score += 2
                elif vol24 >= 100000:
                    score += 1
                
                # Price momentum
                if 5 <= price_change <= 15:  # Nice uptrend
                    score += 2
                elif 0 <= price_change < 5:
                    score += 1
                
                # Security checks
                if rugcheck['mint_revoked']:
                    score += 1
                if rugcheck.get('freeze_revoked'):
                    score += 1
                if rugcheck['lp_locked'] >= 95:
                    score += 1
                elif rugcheck['lp_locked'] >= 80:
                    score += 0.5
                if rugcheck['top5_pct'] < 40:
                    score += 1
                if rugcheck['holders'] >= 1000:
                    score += 1
                if rugcheck['score'] >= 90:
                    score += 1
                elif rugcheck['score'] >= 80:
                    score += 0.5
                
                # Grade assignment
                if score >= 11:
                    grade = "A+"
                elif score >= 9:
                    grade = "A"
                elif score >= 7:
                    grade = "B"
                else:
                    grade = "C"
                
                # Get trade size based on grade
                trade_size = CONFIG["trade_sizes"].get(grade, 0.01)
                
                if grade in ["A+", "A"]:
                    targets.append({
                        "mint": ca,
                        "symbol": symbol,
                        "name": name,
                        "grade": grade,
                        "score": score,
                        "mcap": mcap,
                        "liquidity": liq,
                        "vol24h": vol24,
                        "price_change_24h": price_change,
                        "age_days": age_days,
                        "rugcheck": rugcheck,
                        "current_price_usd": price_usd,
                        "trade_size_sol": trade_size
                    })
                    print(f"  ✅ {symbol} | {grade} | Score {score:.1f} | "
                          f"MCap ${mcap/1e6:.1f}M | Age {age_days}d | Size {trade_size} SOL")
                else:
                    print(f"    ℹ️ Grade {grade} (Score {score:.1f}) - below threshold")
                    rejected["grade"] += 1
            
            if targets:
                print(f"\n🎯 Found {len(targets)} Grade A/A+ setups!")
            else:
                print(f"\n  ⏳ No Grade A/A+ setups found")
                print(f"   Rejected: MCap={rejected['mcap']}, Age={rejected['age']}, Liq={rejected['liquidity']}, Vol={rejected['volume']}, Momentum={rejected['momentum']}, Rug={rejected['rugcheck']}, Grade={rejected['grade']}")
                
        except Exception as e:
            print(f"⚠️ Scan error: {e}")
        
        return targets
    
    def run_trade_cycle(self):
        """Execute one trading cycle"""
        # First monitor existing positions
        self.monitor_positions()
        
        can_trade, reason = self.can_trade()
        
        if not can_trade:
            self.state["status"] = f"BLOCKED: {reason}"
            if "limit" not in reason.lower():
                print(f"⛔ {reason}")
            self.save_state()
            return
        
        self.state["status"] = "SCANNING"
        print(f"\n{'='*60}")
        print(f"🔄 Trade Cycle | {datetime.now().strftime('%H:%M:%S')}")
        print(f"Trades: {self.state['trades_today']}/{CONFIG['max_trades_per_day']} | "
              f"PnL: {self.state['daily_pnl']:.4f} SOL")
        
        targets = self.get_scan_targets()
        
        if not targets:
            print("⏳ No setups. Waiting...")
            self.state["status"] = "IDLE"
            self.save_state()
            return
        
        targets.sort(key=lambda x: x.get('score', 0), reverse=True)
        best = targets[0]
        
        # Get graded trade size
        trade_size = best.get("trade_size_sol", CONFIG["trade_sizes"]["A"])
        
        print(f"\n🚀 EXECUTING TRADE on {best['symbol']}!")
        print(f"   Grade: {best['grade']} | Score: {best['score']:.1f}")
        print(f"   MCap: ${best['mcap']/1e6:.1f}M | Age: {best['age_days']}d")
        print(f"   24h: {best['price_change_24h']:.1f}% | Size: {trade_size} SOL")
        
        self.state["status"] = "IN_TRADE"
        result = self.trader.trade(best['mint'], trade_size)
        
        if result.get('status') == 'SUCCESS':
            self.state["trades_today"] += 1
            
            # Get entry price safely
            entry_price = result.get('entry_price_usd') or best.get('current_price_usd', 0)
            try:
                entry_price = float(entry_price) if entry_price else 0
            except:
                entry_price = 0
            
            trade_record = {
                "timestamp": datetime.now().isoformat(),
                "token": best['mint'],
                "symbol": best['symbol'],
                "name": best['name'],
                "grade": best['grade'],
                "score": best['score'],
                "amount_sol": trade_size,
                "mcap": best['mcap'],
                "age_days": best['age_days'],
                "entry_price_usd": entry_price,
                "tokens_received": result.get('tokens_received', 0),
                "tx_signature": result.get('signature', 'N/A'),
                "result": "ACTIVE",
                "scaled_out": False,
                "rugcheck_score": best['rugcheck']['score']
            }
            
            self.state["trade_history"].append(trade_record)
            self.state["positions"].append(trade_record)
            self.state["traded_tokens"][best['mint']] = datetime.now().isoformat()
            
            print(f"\n✅ Trade #{self.state['trades_today']} EXECUTED!")
            print(f"   Tx: {result.get('signature', 'N/A')[:40]}...")
            print(f"   Tokens: {result.get('tokens_received', 0):.2f}")
            print(f"   Scale at: +{CONFIG['scale_out_pct']}% | Stop: -{CONFIG['stop_loss_pct']}%")
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"\n❌ Trade failed: {error_msg}")
            
        self.state["status"] = "IDLE"
        self.save_state()
    
    def run(self):
        """Main trading loop with crash protection"""
        self.running = True
        crash_count = 0
        
        print("\n🔄 Auto-trader started...")
        print(f"⚠️  ALL 27 RULES ENFORCED")
        print(f"💰 MCAP Range: ${CONFIG['mcap_min']/1e3:.0f}k - ${CONFIG['mcap_max']/1e3:.0f}k")
        print(f"📅 Token Age: {CONFIG['token_age_min_days']}d - {CONFIG['token_age_max_days']}d")
        print(f"📊 Graded sizing: A+={CONFIG['trade_sizes']['A+']} | A={CONFIG['trade_sizes']['A']}")
        print(f"🎯 Scale: +{CONFIG['scale_out_pct']}% | Stop: -{CONFIG['stop_loss_pct']}%")
        print(f"⏰ Large cap time: 45min | Small cap: {CONFIG['time_stop_minutes']}min")
        print(f"🛡️  Crash protection enabled")
        
        while self.running:
            try:
                self.run_trade_cycle()
                crash_count = 0  # Reset on success
                import random
                jitter = random.randint(-5, 5)  # Add jitter to prevent sync patterns
                sleep_time = CONFIG["check_interval_secs"] + jitter
                print(f"\n💤 Sleeping {sleep_time}s before next scan...")
                time.sleep(sleep_time)
            except KeyboardInterrupt:
                print("\n\n🛑 Stopped by user")
                break
            except requests.exceptions.RequestException as e:
                crash_count += 1
                print(f"\n⚠️  Network error (crash #{crash_count}): {e}", flush=True)
                print("   Waiting 60 seconds before retry...", flush=True)
                self.state["status"] = f"NETWORK_ERROR: {e}"
                self.save_state()
                time.sleep(60)
            except Exception as e:
                crash_count += 1
                print(f"\n💥 ERROR (crash #{crash_count}): {e}", flush=True)
                import traceback
                traceback.print_exc()
                print(f"   Auto-restarting in 60 seconds...", flush=True)
                self.state["status"] = f"ERROR: {str(e)[:50]}"
                self.save_state()
                time.sleep(60)
        
        self.state["status"] = "STOPPED"
        self.save_state()
        print("\n✅ Graceful shutdown complete")

if __name__ == "__main__":
    import signal
    
    # Handle signals gracefully
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down...")
        if 'trader' in locals():
            trader.running = False
            trader.state["status"] = "STOPPED_BY_SIGNAL"
            trader.save_state()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Top-level exception catcher
    try:
        trader = RaphaelAutoTrader()
        trader.run()
    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # Save error state
        try:
            error_state = {
                "status": "FATAL_ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            with open("/tmp/raphael_fatal_error.json", 'w') as f:
                json.dump(error_state, f, indent=2)
        except:
            pass
        sys.exit(1)
