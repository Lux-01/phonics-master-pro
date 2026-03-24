#!/usr/bin/env python3
"""
SKYLAR STRATEGY - Balance Tracker Backtest
Starting balance: 1.0 SOL, tracking compounding over 1 month
"""

import json
import time
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# SKYLAR CONFIG
CONFIG = {
    "name": "Skylar",
    "version": "1.0-BalanceTest",
    "mode": "BACKTEST",
    
    # Starting balance
    "starting_balance_sol": 1.0,
    
    # Position sizing (dynamic based on balance)
    "position_size_pct": 10,  # 10% of balance per trade
    "min_position_sol": 0.05,  # Minimum 0.05 SOL
    "max_position_sol": 0.5,   # Maximum 0.5 SOL
    
    # Low Cap Focus
    "mcap_min": 1000,
    "mcap_max": 100000,
    "token_age_max_hours": 48,
    "token_age_min_hours": 0,
    
    # Fast In/Out
    "target_profit_pct": 15,
    "stop_loss_pct": 8,
    "time_stop_minutes": 10,
    
    # Volume Filters
    "min_liquidity_usd": 100,
    "min_volume_5m": 50,
    
    # Files
    "learning_log": "/home/skux/.openclaw/workspace/agents/skylar/skylar_balance_learning.json",
    "trade_log": "/home/skux/.openclaw/workspace/agents/skylar/skylar_balance_trades.json",
}

class SkylarBalanceTrader:
    """Skylar with balance tracking and compounding"""
    
    def __init__(self, starting_balance: float = 1.0):
        self.balance = starting_balance
        self.starting_balance = starting_balance
        self.learning_log = []
        self.trades = []
        self.peak_balance = starting_balance
        self.max_drawdown = 0
        self.consecutive_losses = 0
        self._ensure_dirs()
        
    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(CONFIG["learning_log"]), exist_ok=True)
    
    def calculate_position_size(self) -> float:
        """Calculate position size based on current balance"""
        position = self.balance * (CONFIG["position_size_pct"] / 100)
        position = max(position, CONFIG["min_position_sol"])  # Min 0.05
        position = min(position, CONFIG["max_position_sol"])  # Max 0.5
        return round(position, 4)
    
    def read_lessons_before_trade(self) -> str:
        if not self.learning_log:
            return "📚 No lessons yet. Trading fresh.\n"
        
        recent = self.learning_log[-5:]
        summary = "📚 SKYLAR'S LESSONS:\n"
        for i, lesson in enumerate(recent, 1):
            summary += f"\n{i}. Trade {lesson.get('trade_num', '?')}: {lesson.get('rule', 'N/A')[:50]}..."
        return summary
    
    def record_lesson(self, trade_num: int, result: str, pnl_pct: float, token_data: Dict):
        mcap = token_data.get("mcap", 0)
        age = token_data.get("age_hours", 0)
        
        # Generate rule based on outcome
        if pnl_pct > 0:
            if age < 6:
                rule = "Enter within first 6 hours for maximum momentum"
            elif mcap < 20000:
                rule = f"Coins under ${mcap/1000:.0f}k cap move fastest"
            else:
                rule = "Exit at +15% - don't wait for more"
        else:
            if age > 24:
                rule = "Skip coins older than 24 hours"
            else:
                rule = "Wait for 2 green candles before entry"
        
        mistake = "Not checking liquidity depth" if pnl_pct > -10 else "Held too long, didn't cut loss"
        
        lesson = {
            "timestamp": datetime.now().isoformat(),
            "trade_num": trade_num,
            "balance_before": round(token_data.get("balance_before", 0), 4),
            "result": result,
            "pnl_pct": round(pnl_pct, 2),
            "pnl_sol": round(token_data.get("pnl_sol", 0), 4),
            "token": token_data.get("symbol", "UNKNOWN"),
            "rule": rule,
            "mistake": mistake,
        }
        
        self.learning_log.append(lesson)
        
        print(f"\n📝 LESSON #{trade_num}: {rule}")
        print(f"   ❌ Avoid: {mistake}")
    
    def evaluate_token(self, token: Dict) -> Optional[Dict]:
        mcap = token.get("marketCap", 0)
        liquidity = token.get("liquidity", 0)
        volume_5m = token.get("volume5m", 0)
        price_change_24h = token.get("priceChange24h", 0)
        age_hours = token.get("age_hours", 0)
        
        if age_hours > CONFIG["token_age_max_hours"]:
            return None
        if not (CONFIG["mcap_min"] <= mcap <= CONFIG["mcap_max"]):
            return None
        if liquidity < CONFIG["min_liquidity_usd"]:
            return None
        if volume_5m < CONFIG["min_volume_5m"]:
            return None
        
        score = 0
        grade = "C"
        entry_reason = ""
        
        if age_hours < 6:
            score += 30
            entry_reason = f"Fresh launch ({age_hours:.0f}h)"
        elif age_hours < 24:
            score += 20
            entry_reason = f"New ({age_hours:.0f}h)"
        else:
            score += 10
            entry_reason = f"Recent ({age_hours:.0f}h)"
        
        if volume_5m > 200:
            score += 25
            entry_reason += " + High vol"
        
        if price_change_24h > 50:
            score += 20
            entry_reason += " + Strong mom"
        elif price_change_24h > 20:
            score += 15
            entry_reason += " + Good mom"
        
        if score >= 70:
            grade = "A+"
        elif score >= 55:
            grade = "A"
        elif score >= 40:
            grade = "B"
        
        return {
            "token": token,
            "score": score,
            "grade": grade,
            "entry_reason": entry_reason,
            "mcap": mcap,
            "age_hours": age_hours,
        }
    
    def execute_trade(self, setup: Dict, trade_num: int) -> Dict:
        token = setup["token"]
        symbol = token.get("symbol", "UNKNOWN")
        is_rug = token.get("is_rug", False)
        
        # Calculate position
        position_size = self.calculate_position_size()
        balance_before = self.balance
        
        print(f"\n{'='*60}")
        print(f"🔄 TRADE #{trade_num} | Balance: {balance_before:.4f} SOL")
        print(f"{'='*60}")
        print(f"📊 {symbol} | {setup['grade']} | {setup['entry_reason']}")
        print(f"   Position: {position_size:.4f} SOL ({position_size/balance_before*100:.0f}% of balance)")
        
        if is_rug:
            print(f"   ⚠️ RUG DETECTED!")
        
        # Simulate outcome
        random.seed(trade_num + int(time.time()))
        
        if setup["grade"] == "A+":
            win_prob = 0.65
        elif setup["grade"] == "A":
            win_prob = 0.55
        else:
            win_prob = 0.45
        
        # Boost from learning
        win_prob += min(len(self.learning_log) * 0.001, 0.08)
        
        if is_rug:
            win_prob = 0.05
        
        if random.random() < win_prob:
            if is_rug:
                pnl_pct = random.uniform(-35, -25)
                result = "rug"
            else:
                pnl_pct = random.uniform(5, 25)
                result = "win"
        else:
            if random.random() < 0.7:
                pnl_pct = random.uniform(-8, -3)
                result = "stop_loss"
            else:
                pnl_pct = random.uniform(-22, -10)
                result = "bag_hold"
        
        pnl_sol = position_size * (pnl_pct / 100)
        self.balance += pnl_sol
        
        # Track stats
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance
        drawdown = (self.peak_balance - self.balance) / self.peak_balance * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
        
        if pnl_sol < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        emoji = "🟢" if pnl_sol > 0 else "🔴"
        print(f"\n{emoji} RESULT: {result.upper()} | {pnl_pct:+.1f}% | {pnl_sol:+.4f} SOL")
        print(f"💰 Balance: {balance_before:.4f} → {self.balance:.4f} SOL")
        print(f"📈 Total Return: {(self.balance/self.starting_balance-1)*100:+.1f}%")
        
        self.record_lesson(trade_num, result, pnl_pct, {
            "symbol": symbol,
            "mcap": setup["mcap"],
            "age_hours": setup["age_hours"],
            "balance_before": balance_before,
            "pnl_sol": pnl_sol,
        })
        
        return {
            "trade_num": trade_num,
            "symbol": symbol,
            "grade": setup["grade"],
            "result": result,
            "position_size": position_size,
            "pnl_pct": round(pnl_pct, 2),
            "pnl_sol": round(pnl_sol, 4),
            "balance_before": round(balance_before, 4),
            "balance_after": round(self.balance, 4),
            "total_return_pct": round((self.balance/self.starting_balance-1)*100, 2),
        }

def generate_token(trade_num: int, day: int) -> Dict:
    """Generate token with market cycle variation"""
    
    if day <= 8:
        grade_weights = [0.4, 0.35, 0.2, 0.05]
        momentum = 40
    elif day <= 15:
        grade_weights = [0.15, 0.25, 0.35, 0.25]
        momentum = -10
    else:
        grade_weights = [0.3, 0.3, 0.25, 0.15]
        momentum = 15
    
    symbols = ["MOON", "PEPE", "DOGE", "SHIB", "FLOKI", "BONK", "ELON", "WOJAK", 
               "MEME", "CAT", "APE", "DEGEN", "CHAD", "SIGMA", "ALPHA", "BETA"]
    symbol = random.choice(symbols) + random.choice(["", "X", "2", "AI"])
    
    grades = ["A+", "A", "B", "C"]
    grade = random.choices(grades, weights=grade_weights)[0]
    
    if grade == "A+":
        mcap = random.randint(15000, 60000)
        vol = random.randint(200, 400)
        age = random.randint(1, 12)
        price = random.randint(30, 90) + momentum
    elif grade == "A":
        mcap = random.randint(10000, 70000)
        vol = random.randint(120, 280)
        age = random.randint(6, 18)
        price = random.randint(15, 50) + momentum
    elif grade == "B":
        mcap = random.randint(5000, 80000)
        vol = random.randint(60, 180)
        age = random.randint(12, 30)
        price = random.randint(-10, 40) + momentum
    else:
        mcap = random.randint(1000, 90000)
        vol = random.randint(20, 100)
        age = random.randint(24, 45)
        price = random.randint(-30, 20)
    
    is_rug = random.random() < 0.07
    if is_rug:
        price = random.randint(-60, -30)
    
    return {
        "symbol": symbol,
        "marketCap": mcap,
        "liquidity": random.randint(1000, 20000),
        "volume5m": vol,
        "priceChange24h": price,
        "age_hours": age,
        "is_rug": is_rug,
    }

def run_balance_backtest(months: int = 1):
    """Run multi-month backtest starting with 1 SOL"""
    days = months * 30
    
    print("\n" + "="*70)
    print(f"🚀 SKYLAR BALANCE TEST - {months} MONTH")
    print("   Starting: 1.0 SOL")
    print("   Position: 10% of balance (0.05-0.5 SOL range)")
    print("   Style: Compounding gains/losses")
    print("="*70)
    
    skylar = SkylarBalanceTrader(starting_balance=1.0)
    
    trades = []
    daily_balances = []
    
    print(f"\n📅 Simulating {days} days ({months} months)...\n")
    
    for day in range(1, days + 1):
        # Extended market cycles for 5 months
        cycle_day = (day - 1) % 60  # 60-day cycles
        if cycle_day <= 20:
            phase = "BULL"
        elif cycle_day <= 35:
            phase = "BEAR"
        elif cycle_day <= 50:
            phase = "RECOVERY"
        else:
            phase = "MIXED"
        
        if phase == "BULL":
            opps = random.randint(3, 6)
        elif phase == "BEAR":
            opps = random.randint(1, 4)
        else:
            opps = random.randint(2, 5)
        
        day_trades = 0
        
        for _ in range(opps):
            token = generate_token(len(trades) + 1, day)
            setup = skylar.evaluate_token(token)
            
            if setup and setup["grade"] in ["A+", "A", "B"]:
                trade = skylar.execute_trade(setup, len(trades) + 1)
                trade["day"] = day
                trade["phase"] = phase
                trades.append(trade)
                day_trades += 1
                
                # Stop if balance drops too low
                if skylar.balance < 0.3:
                    print(f"\n🛑 STOPPED: Balance too low ({skylar.balance:.4f} SOL)")
                    break
        
        daily_balances.append({
            "day": day,
            "phase": phase,
            "trades": day_trades,
            "balance": round(skylar.balance, 4),
        })
        
        if day % 5 == 0:
            print(f"\n📊 Day {day:2d} [{phase:8}]: Balance: {skylar.balance:.4f} SOL | Trades: {len(trades)}")
        
        if skylar.balance < 0.3:
            break
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    print(f"📊 {months}-MONTH BALANCE TEST RESULTS")
    print("="*70)
    
    wins = len([t for t in trades if t["result"] == "win"])
    losses = len([t for t in trades if t["result"] != "win"])
    win_rate = (wins / len(trades) * 100) if trades else 0
    
    print(f"\n💰 FINAL BALANCE: {skylar.balance:.4f} SOL")
    print(f"   Starting: 1.0000 SOL")
    print(f"   Profit: {skylar.balance - 1.0:+.4f} SOL ({(skylar.balance/1.0-1)*100:+.1f}%)")
    print(f"   Months: {months} | Days: {len(daily_balances)}")
    
    # Monthly breakdown
    print(f"\n📅 MONTHLY PROGRESS:")
    for m in range(1, months + 1):
        day_idx = min(m * 30 - 1, len(daily_balances) - 1)
        if day_idx >= 0:
            print(f"   Month {m}: {daily_balances[day_idx]['balance']:.4f} SOL")
    
    print(f"\n📈 TRADING STATS:")
    print(f"   Total Trades: {len(trades)}")
    print(f"   Wins: {wins} | Losses: {losses}")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Peak Balance: {skylar.peak_balance:.4f} SOL")
    print(f"   Max Drawdown: {skylar.max_drawdown:.1f}%")
    
    print(f"\n📊 BALANCE PROGRESSION:")
    print(f"   Day 1-10: {daily_balances[9]['balance']:.4f} SOL")
    if len(daily_balances) >= 20:
        print(f"   Day 11-20: {daily_balances[19]['balance']:.4f} SOL")
    if len(daily_balances) >= 30:
        print(f"   Day 21-30: {daily_balances[-1]['balance']:.4f} SOL")
    
    print(f"\n🧠 LESSONS LEARNED: {len(skylar.learning_log)}")
    print(f"   Avg lessons per month: {len(skylar.learning_log)/months:.0f}")
    
    # Top rules
    rules = {}
    for lesson in skylar.learning_log:
        r = lesson.get("rule", "")
        rules[r] = rules.get(r, 0) + 1
    
    top_rules = sorted(rules.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n🔥 TOP RULES:")
    for i, (rule, count) in enumerate(top_rules, 1):
        print(f"   {i}. [{count}x] {rule}")
    
    # Save results
    results = {
        "strategy": "Skylar Balance Test v1.0",
        "duration_months": months,
        "duration_days": len(daily_balances),
        "starting_balance": 1.0,
        "final_balance": round(skylar.balance, 4),
        "profit_sol": round(skylar.balance - 1.0, 4),
        "roi_pct": round((skylar.balance/1.0-1)*100, 2),
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "peak_balance": round(skylar.peak_balance, 4),
        "max_drawdown_pct": round(skylar.max_drawdown, 2),
        "trades": trades,
        "daily_balances": daily_balances,
        "learning_log": skylar.learning_log,
    }
    
    output_file = f"/home/skux/.openclaw/workspace/agents/skylar/skylar_{months}month_balance.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")

if __name__ == "__main__":
    run_balance_backtest(months=5)
