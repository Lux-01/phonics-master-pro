#!/usr/bin/env python3
"""
Genetic Trading System - Strategy Definitions
10 different memecoin trading strategies
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import random

@dataclass
class Trade:
    """Individual trade record"""
    token: str
    symbol: str
    entry_price: float
    entry_time: datetime
    amount_sol: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl_sol: Optional[float] = None
    pnl_pct: Optional[float] = None
    status: str = "open"  # open, closed, pending
    
    def close_trade(self, exit_price: float):
        self.exit_price = exit_price
        self.exit_time = datetime.now()
        self.pnl_sol = self.amount_sol * (exit_price - self.entry_price) / self.entry_price
        self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        self.status = "closed"
        return self.pnl_sol


@dataclass  
class Strategy:
    """Base strategy class"""
    id: int
    name: str
    description: str
    timeframe: str  # 5m, 15m, 30m, 1h
    risk_level: str  # very_low, low, medium, high, very_high
    
    # Strategy DNA (mutable parameters)
    dna: Dict = field(default_factory=dict)
    
    # Portfolio tracking
    initial_sol: float = 1.2  # ~$180 USD
    current_sol: float = 1.2
    total_pnl_sol: float = 0.0
    total_pnl_usd: float = 0.0
    win_count: int = 0
    loss_count: int = 0
    trades: List[Trade] = field(default_factory=list)
    
    # Generation tracking
    generation: int = 0
    parent_strategy: Optional[str] = None
    mutations: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_win_rate(self) -> float:
        total = self.win_count + self.loss_count
        return (self.win_count / total * 100) if total > 0 else 0
    
    def get_total_trades(self) -> int:
        return len(self.trades)
    
    def get_open_positions(self) -> int:
        return sum(1 for t in self.trades if t.status == "open")
    
    def get_invested_sol(self) -> float:
        return sum(t.amount_sol for t in self.trades if t.status == "open")
    
    def get_available_sol(self) -> float:
        return self.current_sol
    
    def get_performance_score(self) -> float:
        """Calculate performance score (0-100)"""
        score = 0
        
        # PnL contribution (50%)
        if self.total_pnl_sol > 0:
            pnl_score = min(50, (self.total_pnl_sol / self.initial_sol) * 100)
            score += pnl_score
        
        # Win rate contribution (30%)
        win_rate = self.get_win_rate()
        score += (win_rate / 100) * 30
        
        # Activity contribution (20%)
        if self.get_total_trades() > 0:
            score += 20
        
        return score

# =============================================================================
# STRATEGY 1: Momentum Surge
# =============================================================================
def create_strategy_1_momentum_surge():
    return Strategy(
        id=1,
        name="Momentum Surge",
        description="Buy on volume spike + price breakout. Ride momentum waves.",
        timeframe="1h",
        risk_level="high",
        dna={
            "volume_spike_threshold": 3.0,  # 3x average volume
            "price_breakout_threshold": 0.08,  # 8% above resistance
            "min_mcap": 50000,  # $50k minimum
            "max_mcap": 2000000,  # $2M maximum
            "entry_position_pct": 0.15,  # 15% of portfolio per trade
            "take_profit_pct": 0.25,  # +25%
            "stop_loss_pct": -0.08,  # -8%
            "time_stop_hours": 6,
            "indicators": ["volume", "price_change_1h", "breakout_level"]
        }
    )

# =============================================================================
# STRATEGY 2: Mean Reversion Dip
# =============================================================================
def create_strategy_2_mean_reversion():
    return Strategy(
        id=2,
        name="Mean Reversion Dip",
        description="Buy -10% to -15% dips, sell on bounce to mean.",
        timeframe="30m",
        risk_level="medium",
        dna={
            "dip_threshold_min": -0.15,  # Buy at -15%
            "dip_threshold_max": -0.08,  # Max -8% (don't chase)
            "mean_period": 20,  # 20-period moving average
            "bounce_target_pct": 0.12,  # Sell at +12%
            "min_liquidity": 10000,  # $10k minimum
            "max_slippage": 0.02,  # 2%
            "cooldown_minutes": 30,
            "indicators": ["price_vs_ma", "volume", "rsi"]
        }
    )

# =============================================================================
# STRATEGY 3: Whale Shadow
# =============================================================================
def create_strategy_3_whale_shadow():
    return Strategy(
        id=3,
        name="Whale Shadow",
        description="Copy trades from tracked whale wallets with slight delay.",
        timeframe="real-time",
        risk_level="medium",
        dna={
            "whale_wallets": [
                "JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv",
                # Add more tracked whales
            ],
            "max_delay_seconds": 60,  # Copy within 60s
            "min_whale_buys": 2,  # Need 2 buys from same whale
            "copy_size_pct": 0.10,  # Use 10% of our capital
            "max_position_hold_hours": 4,
            "profit_target_pct": 0.15,
            "stop_loss_pct": -0.07,
            "indicators": ["whale_flow", "copy_confidence"]
        }
    )

# =============================================================================
# STRATEGY 4: RSI Oversold
# =============================================================================
def create_strategy_4_rsi_oversold():
    return Strategy(
        id=4,
        name="RSI Oversold",
        description="Buy when RSI < 30 with volume confirmation. Classic technical.",
        timeframe="15m",
        risk_level="medium",
        dna={
            "rsi_period": 14,
            "rsi_entry_max": 30,  # Enter below RSI 30
            "rsi_exit_min": 65,  # Exit above RSI 65
            "volume_confirmation": True,  # Need volume spike
            "min_volume_spike": 1.5,  # 1.5x average
            "position_size_pct": 0.12,
            "take_profit_pct": 0.18,
            "stop_loss_pct": -0.06,
            "indicators": ["rsi", "volume", "trend"]
        }
    )

# =============================================================================
# STRATEGY 5: Breakout Hunter
# =============================================================================
def create_strategy_5_breakout_hunter():
    return Strategy(
        id=5,
        name="Breakout Hunter",
        description="Identify key resistance levels, buy on confirmed breakout.",
        timeframe="1h",
        risk_level="high",
        dna={
            "resistance_lookback": 24,  # 24 hours of data
            "breakout_confirmation_pct": 0.03,  # 3% above resistance
            "volume_confirmation": True,
            "min_breakout_volume": 2.0,  # 2x average
            "position_size_pct": 0.18,
            "take_profit_pct": 0.30,
            "stop_loss_pct": -0.10,
            "trailing_stop_pct": 0.15,  # Activate at +15%
            "indicators": ["resistance", "volume", "atr"]
        }
    )

# =============================================================================
# STRATEGY 6: Social Sentiment
# =============================================================================
def create_strategy_6_social_sentiment():
    return Strategy(
        id=6,
        name="Social Sentiment",
        description="Trade on Twitter mention spikes and social buzz.",
        timeframe="15m",
        risk_level="high",
        dna={
            "mention_spike_threshold": 5.0,  # 5x mentions
            "sentiment_threshold": 0.6,  # 60% positive
            "min_follower_count": 1000,  # Ignore micro-influencers
            "max_entry_delay_minutes": 15,
            "position_size_pct": 0.10,
            "momentum_hold_hours": 2,
            "profit_take_pct": 0.20,
            "stop_loss_pct": -0.10,
            "indicators": ["mentions", "sentiment", "trending"]
        }
    )

# =============================================================================
# STRATEGY 7: Liquidity Surfing
# =============================================================================
def create_strategy_7_liquidity_surfing():
    return Strategy(
        id=7,
        name="Liquidity Surfing",
        description="Ride liquidity waves - enter on inflow, exit before drain.",
        timeframe="30m",
        risk_level="medium",
        dna={
            "liquidity_inflow_threshold": 1.3,  # 30% increase
            "liquidity_drain_threshold": 0.8,  # Exit on 20% drain
            "min_liquidity_usd": 15000,
            "max_liquidity_usd": 500000,
            "position_size_pct": 0.15,
            "hold_max_hours": 8,
            "profit_target_pct": 0.12,
            "early_exit_if_drain": True,
            "indicators": ["liquidity", "volume", "holders"]
        }
    )

# =============================================================================
# STRATEGY 8: EMA Cross (Trend Following)
# =============================================================================
def create_strategy_8_ema_cross():
    return Strategy(
        id=8,
        name="EMA Cross",
        description="Golden cross entry (EMA 9 > EMA 21), death cross exit.",
        timeframe="1h",
        risk_level="low",
        dna={
            "fast_ema_period": 9,
            "slow_ema_period": 21,
            "signal_lookback": 2,  # 2 consecutive candles
            "trend_filter": True,  # Only trade with 1h trend
            "position_size_pct": 0.12,
            "take_profit_pct": 0.15,
            "stop_loss_pct": -0.07,
            "trailing_stop": True,
            "indicators": ["ema9", "ema21", "trend"]
        }
    )

# =============================================================================
# STRATEGY 9: Range Trader
# =============================================================================
def create_strategy_9_range_trader():
    return Strategy(
        id=9,
        name="Range Trader",
        description="Identify support/resistance ranges. Buy support, sell resistance.",
        timeframe="30m",
        risk_level="low",
        dna={
            "range_lookback_hours": 12,
            "support_buffer_pct": 0.02,  # 2% buffer below support
            "resistance_buffer_pct": 0.02,
            "min_range_width_pct": 0.10,  # At least 10% range
            "position_size_pct": 0.10,
            "max_trades_per_range": 3,
            "breakout_stop_loss": True,
            "indicators": ["support", "resistance", "range_width"]
        }
    )

# =============================================================================
# STRATEGY 10: News Arbitrage
# =============================================================================
def create_strategy_10_news_arbitrage():
    return Strategy(
        id=10,
        name="News Arbitrage",
        description="React to major news within 60 seconds. Lightning fast.",
        timeframe="5m",
        risk_level="very_high",
        dna={
            "max_reaction_seconds": 60,
            "news_sources": ["twitter", "telegram", "discord"],
            "sentiment_threshold": 0.75,
            "position_size_pct": 0.20,  # Larger - conviction
            "max_hold_minutes": 30,
            "profit_target_pct": 0.10,  # Quick 10% then out
            "stop_loss_pct": -0.05,
            "only_major_events": True,  # Filter for high-impact
            "indicators": ["news_velocity", "sentiment", "early_volume"]
        }
    )

# =============================================================================
# STRATEGY FACTORY
# =============================================================================

def get_all_strategies():
    """Return all 10 initial strategies"""
    return [
        create_strategy_1_momentum_surge(),
        create_strategy_2_mean_reversion(),
        create_strategy_3_whale_shadow(),
        create_strategy_4_rsi_oversold(),
        create_strategy_5_breakout_hunter(),
        create_strategy_6_social_sentiment(),
        create_strategy_7_liquidity_surfing(),
        create_strategy_8_ema_cross(),
        create_strategy_9_range_trader(),
        create_strategy_10_news_arbitrage(),
    ]

def create_random_strategy(generation: int = 0):
    """Create a completely new random strategy"""
    strategies = get_all_strategies()
    base = random.choice(strategies)
    
    # Mutate heavily
    new_dna = mutate_dna(base.dna, mutation_rate=0.5)
    
    return Strategy(
        id=random.randint(100, 999),
        name=f"Evolved_{generation}_{random.randint(1000,9999)}",
        description=base.description + " [EVOLVED]",
        timeframe=random.choice(["5m", "15m", "30m", "1h"]),
        risk_level=base.risk_level,
        dna=new_dna,
        generation=generation,
        parent_strategy=base.name
    )

def mutate_dna(dna: Dict, mutation_rate: float = 0.3) -> Dict:
    """Mutate strategy DNA with given rate"""
    new_dna = dna.copy()
    
    for key, value in new_dna.items():
        if isinstance(value, (int, float)) and random.random() < mutation_rate:
            if isinstance(value, int):
                # Integer mutation
                new_dna[key] = max(1, int(value * random.uniform(0.7, 1.3)))
            else:
                # Float mutation
                new_dna[key] = value * random.uniform(0.7, 1.3)
    
    return new_dna

def breed_strategies(strategy1: Strategy, strategy2: Strategy, generation: int) -> Strategy:
    """Create offspring from two parent strategies"""
    # DNA crossover
    child_dna = {}
    for key in strategy1.dna.keys():
        if key in strategy2.dna:
            # Average the values
            child_dna[key] = (strategy1.dna[key] + strategy2.dna[key]) / 2
        else:
            child_dna[key] = strategy1.dna[key]
    
    # Add mutations
    child_dna = mutate_dna(child_dna, mutation_rate=0.2)
    
    return Strategy(
        id=random.randint(100, 999),
        name=f"Hybrid_{strategy1.id}x{strategy2.id}_G{generation}",
        description=f"Hybrid of {strategy1.name} and {strategy2.name}",
        timeframe=random.choice([strategy1.timeframe, strategy2.timeframe]),
        risk_level=random.choice([strategy1.risk_level, strategy2.risk_level]),
        dna=child_dna,
        generation=generation,
        parent_strategy=f"{strategy1.name} + {strategy2.name}",
        mutations=["hybrid_crossover"]
    )

if __name__ == "__main__":
    # Test
    strategies = get_all_strategies()
    print(f"Created {len(strategies)} strategies:")
    for s in strategies:
        print(f"  {s.id}: {s.name} ({s.risk_level})")
        print(f"     DNA: {len(s.dna)} parameters")
    
    # Test mutation
    print("\n--- Testing Evolution ---")
    test_strategy = strategies[0]
    mutated = mutate_dna(test_strategy.dna)
    print(f"Original: {test_strategy.dna.get('take_profit_pct')}")
    print(f"Mutated: {mutated.get('take_profit_pct')}")
