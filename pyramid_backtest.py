#!/usr/bin/env python3
"""
Pyramid Dip Strategy Backtest for PUNCH Token
Strategy: Average-Down Entry with Pyramid Position Building
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

@dataclass
class PricePoint:
    time: str
    price: float
    notes: str = ""

@dataclass
class Trade:
    entry_time: str
    exit_time: Optional[str]
    entry_price: float
    exit_price: Optional[float]
    positions: List[Dict[str, Any]]  # List of {sol_amount, price, timestamp}
    status: str  # "open", "closed_profit", "closed_loss"
    pnl_usd: float = 0.0
    pnl_percent: float = 0.0
    exit_reason: str = ""

@dataclass
class BacktestResult:
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl_usd: float
    win_rate: float
    avg_profit_per_trade: float
    trades: List[Trade]

class PyramidStrategy:
    def __init__(self):
        self.first_entry_size = 0.1  # SOL
        self.second_entry_size = 0.2  # SOL
        self.third_entry_size = 0.4  # SOL
        self.max_position = 0.7  # SOL
        self.dip_threshold = 0.10  # 10% below 2h high
        self.profit_threshold = 0.02  # 2% within 2h high
        self.stop_loss = 0.10  # 10% below entry
        self.pyramid_drop = 0.05  # 5% drop triggers next entry
        
    def get_two_hour_high(self, prices: List[PricePoint], current_idx: int) -> float:
        """Get the highest price in the last 2 hours (8 data points, 15min intervals)"""
        start_idx = max(0, current_idx - 8)
        window = prices[start_idx:current_idx]
        if not window:
            return prices[0].price
        return max(p.price for p in window)
    
    def calculate_avg_entry(self, positions: List[Dict]) -> float:
        """Calculate weighted average entry price"""
        if not positions:
            return 0.0
        total_sol = sum(p['sol_amount'] for p in positions)
        total_cost = sum(p['sol_amount'] * p['price'] for p in positions)
        return total_cost / total_sol if total_sol > 0 else 0.0
    
    def calculate_position_value(self, positions: List[Dict], current_price: float) -> float:
        """Calculate current value of position in USD"""
        total_sol = sum(p['sol_amount'] for p in positions)
        return total_sol * current_price
    
    def calculate_pnl(self, positions: List[Dict], current_price: float) -> float:
        """Calculate P&L in USD"""
        avg_entry = self.calculate_avg_entry(positions)
        total_sol = sum(p['sol_amount'] for p in positions)
        entry_value = total_sol * avg_entry
        current_value = total_sol * current_price
        return current_value - entry_value

def run_backtest():
    """Run the pyramid strategy backtest on provided price data"""
    
    # Price timeline data (15-minute intervals from 00:00 to 03:30)
    price_data = [
        ("00:00", 0.022, "opening"),
        ("00:15", 0.024, "+9% pump"),
        ("00:30", 0.026, "+18% pump"),
        ("00:45", 0.025, "-4% pullback - ENTRY HERE: 0.1 SOL at $0.025"),
        ("01:00", 0.028, "+27% total"),
        ("01:15", 0.032, "+45% total"),
        ("01:30", 0.035, "+59% total, peak forming"),
        ("01:45", 0.034, "-3% from peak"),
        ("02:00", 0.033, "+50% total, lower high"),
        ("02:15", 0.034, "lower high - EXIT HERE: Sell at $0.034"),
        ("02:30", 0.032, "-6% pullback"),
        ("02:45", 0.030, "-9% pullback, find support"),
        ("03:00", 0.031, "-3% bounce"),
        ("03:15", 0.029, "-7% dip - NEW ENTRY: 0.1 SOL at $0.029"),
        ("03:30", 0.031, "+7% bounce"),
    ]
    
    prices = [PricePoint(time=t, price=p, notes=n) for t, p, n in price_data]
    strategy = PyramidStrategy()
    
    trades: List[Trade] = []
    current_trade: Optional[Trade] = None
    
    print("=" * 80)
    print("PYRAMID DIP STRATEGY BACKTEST - PUNCH TOKEN")
    print("=" * 80)
    print(f"{'Time':<8} {'Price':<8} {'2H High':<8} {'Action':<50}")
    print("-" * 80)
    
    for i, point in enumerate(prices):
        two_hour_high = strategy.get_two_hour_high(prices, i)
        dip_from_high = (two_hour_high - point.price) / two_hour_high if two_hour_high > 0 else 0
        
        action = ""
        
        # Check if we have an open trade
        if current_trade:
            avg_entry = strategy.calculate_avg_entry(current_trade.positions)
            total_sol = sum(p['sol_amount'] for p in current_trade.positions)
            pnl = strategy.calculate_pnl(current_trade.positions, point.price)
            pnl_pct = (point.price - avg_entry) / avg_entry * 100
            
            # Check for pyramid entry (5% drop from avg entry)
            drop_from_avg = (avg_entry - point.price) / avg_entry if avg_entry > 0 else 0
            
            # Exit conditions
            profit_target_hit = (two_hour_high - point.price) / two_hour_high <= strategy.profit_threshold
            stop_loss_hit = (avg_entry - point.price) / avg_entry >= strategy.stop_loss
            
            if profit_target_hit and point.price >= avg_entry:
                # Take profit
                current_trade.exit_time = point.time
                current_trade.exit_price = point.price
                current_trade.status = "closed_profit"
                current_trade.pnl_usd = pnl
                current_trade.pnl_percent = pnl_pct
                current_trade.exit_reason = f"Profit target: within {strategy.profit_threshold*100:.0f}% of 2H high"
                trades.append(current_trade)
                action = f"EXIT at ${point.price:.4f} | P&L: ${pnl:.4f} ({pnl_pct:+.2f}%) | {current_trade.exit_reason}"
                current_trade = None
                
            elif stop_loss_hit:
                # Stop loss
                current_trade.exit_time = point.time
                current_trade.exit_price = point.price
                current_trade.status = "closed_loss"
                current_trade.pnl_usd = pnl
                current_trade.pnl_percent = pnl_pct
                current_trade.exit_reason = f"Stop loss: below entry by {strategy.stop_loss*100:.0f}%"
                trades.append(current_trade)
                action = f"STOP LOSS at ${point.price:.4f} | P&L: ${pnl:.4f} ({pnl_pct:+.2f}%) | {current_trade.exit_reason}"
                current_trade = None
                
            elif drop_from_avg >= strategy.pyramid_drop and total_sol < strategy.max_position - 0.001:
                # Pyramid entry
                remaining_capacity = strategy.max_position - total_sol
                if remaining_capacity >= strategy.second_entry_size and len(current_trade.positions) == 1:
                    current_trade.positions.append({
                        'sol_amount': strategy.second_entry_size,
                        'price': point.price,
                        'timestamp': point.time
                    })
                    new_avg = strategy.calculate_avg_entry(current_trade.positions)
                    action = f"PYRAMID +0.2 SOL at ${point.price:.4f} | New avg: ${new_avg:.4f}"
                elif remaining_capacity >= strategy.third_entry_size and len(current_trade.positions) == 2:
                    current_trade.positions.append({
                        'sol_amount': strategy.third_entry_size,
                        'price': point.price,
                        'timestamp': point.time
                    })
                    new_avg = strategy.calculate_avg_entry(current_trade.positions)
                    action = f"PYRAMID +0.4 SOL at ${point.price:.4f} | New avg: ${new_avg:.4f}"
            else:
                action = f"Holding | Avg: ${avg_entry:.4f} | P&L: ${pnl:.4f} ({pnl_pct:+.2f}%)"
        else:
            # Look for entry (10% dip from 2H high)
            if dip_from_high >= strategy.dip_threshold:
                current_trade = Trade(
                    entry_time=point.time,
                    exit_time=None,
                    entry_price=point.price,
                    exit_price=None,
                    positions=[{
                        'sol_amount': strategy.first_entry_size,
                        'price': point.price,
                        'timestamp': point.time
                    }],
                    status="open"
                )
                action = f"ENTRY: 0.1 SOL at ${point.price:.4f} | Dip: {dip_from_high*100:.1f}% from 2H high"
            else:
                action = f"Waiting | Dip: {dip_from_high*100:.1f}% (need {strategy.dip_threshold*100:.0f}%)"
        
        print(f"{point.time:<8} ${point.price:<7.4f} ${two_hour_high:<7.4f} {action}")
    
    # Close any open trade at final price
    if current_trade:
        final_price = prices[-1].price
        avg_entry = strategy.calculate_avg_entry(current_trade.positions)
        pnl = strategy.calculate_pnl(current_trade.positions, final_price)
        pnl_pct = (final_price - avg_entry) / avg_entry * 100
        current_trade.exit_time = prices[-1].time
        current_trade.exit_price = final_price
        current_trade.status = "closed_eod"
        current_trade.pnl_usd = pnl
        current_trade.pnl_percent = pnl_pct
        current_trade.exit_reason = "End of simulation"
        trades.append(current_trade)
        print(f"\n{'':<8} {'':<8} {'':<8} CLOSED OPEN POSITION AT EOD: ${final_price:.4f} | P&L: ${pnl:.4f}")
    
    print("\n" + "=" * 80)
    print("TRADE SUMMARY")
    print("=" * 80)
    
    for j, trade in enumerate(trades, 1):
        print(f"\nTrade #{j}:")
        print(f"  Entry: {trade.entry_time} @ ${trade.entry_price:.4f}")
        total_sol = sum(p['sol_amount'] for p in trade.positions)
        avg_entry = sum(p['sol_amount'] * p['price'] for p in trade.positions) / total_sol
        print(f"  Position: {total_sol:.1f} SOL (avg entry: ${avg_entry:.4f})")
        for p in trade.positions:
            print(f"    - {p['sol_amount']} SOL @ ${p['price']:.4f} at {p['timestamp']}")
        print(f"  Exit: {trade.exit_time} @ ${trade.exit_price:.4f}")
        print(f"  P&L: ${trade.pnl_usd:.4f} ({trade.pnl_percent:+.2f}%)")
        print(f"  Reason: {trade.exit_reason}")
    
    # Calculate statistics
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.pnl_usd > 0)
    losing_trades = sum(1 for t in trades if t.pnl_usd < 0)
    total_pnl = sum(t.pnl_usd for t in trades)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    avg_profit = total_pnl / total_trades if total_trades > 0 else 0
    
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Total P&L: ${total_pnl:.4f}")
    print(f"Avg Profit per Trade: ${avg_profit:.4f}")
    
    # Save results to JSON
    result_data = {
        "strategy": "Pyramid Average-Down Entry",
        "token": "PUNCH",
        "timeframe": "15min intervals (00:00 - 03:30)",
        "parameters": {
            "first_entry_size_sol": strategy.first_entry_size,
            "second_entry_size_sol": strategy.second_entry_size,
            "third_entry_size_sol": strategy.third_entry_size,
            "max_position_sol": strategy.max_position,
            "dip_threshold_pct": strategy.dip_threshold * 100,
            "profit_threshold_pct": strategy.profit_threshold * 100,
            "stop_loss_pct": strategy.stop_loss * 100,
            "pyramid_drop_pct": strategy.pyramid_drop * 100
        },
        "summary": {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate_pct": round(win_rate, 2),
            "total_pnl_usd": round(total_pnl, 4),
            "avg_profit_per_trade_usd": round(avg_profit, 4)
        },
        "trades": [
            {
                "trade_number": i + 1,
                "entry_time": t.entry_time,
                "entry_price": t.entry_price,
                "exit_time": t.exit_time,
                "exit_price": t.exit_price,
                "positions": [
                    {
                        "sol_amount": p['sol_amount'],
                        "price": p['price'],
                        "timestamp": p['timestamp']
                    } for p in t.positions
                ],
                "total_sol": round(sum(p['sol_amount'] for p in t.positions), 1),
                "avg_entry_price": round(
                    sum(p['sol_amount'] * p['price'] for p in t.positions) / 
                    sum(p['sol_amount'] for p in t.positions), 4
                ) if t.positions else 0,
                "pnl_usd": round(t.pnl_usd, 4),
                "pnl_percent": round(t.pnl_percent, 2),
                "status": t.status,
                "exit_reason": t.exit_reason
            }
            for i, t in enumerate(trades)
        ],
        "price_data": [
            {"time": p.time, "price": p.price, "notes": p.notes}
            for p in prices
        ]
    }
    
    with open('/home/skux/.openclaw/workspace/pyramid_results.json', 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\nResults saved to: /home/skux/.openclaw/workspace/pyramid_results.json")
    
    return BacktestResult(
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        total_pnl_usd=total_pnl,
        win_rate=win_rate,
        avg_profit_per_trade=avg_profit,
        trades=trades
    )

if __name__ == "__main__":
    result = run_backtest()
