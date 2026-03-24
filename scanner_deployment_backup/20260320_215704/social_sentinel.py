#!/usr/bin/env python3
"""
Social Sentinel Strategy
Uses sentiment/social indicators simulated from trade metadata
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Any
import statistics

@dataclass
class Trade:
    symbol: str
    pnl_pct: float
    pnl_sol: float
    entry_reason: str
    exit_reason: str
    sentiment_score: float
    day: int
    position_size: float

@dataclass
class StrategyState:
    balance: float = 1.0
    trades: List[Trade] = None
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    
    def __post_init__(self):
        if self.trades is None:
            self.trades = []

class SocialSentinel:
    """
    Analyzes social sentiment from trade metadata:
    - Entry reason keywords (momentum, volume signals)
    - Grade-based sentiment (A+ = very bullish)
    - Token name patterns (viral/memetic indicators)
    - Market phase confidence
    """
    
    def __init__(self, initial_balance: float = 1.0):
        self.state = StrategyState(balance=initial_balance)
        self.learning_params = {
            'sentiment_threshold': 0.6,   # Minimum sentiment to enter
            'bullish_boost': 1.2,          # Multiplier in bull markets
            'bearish_filter': 0.3,         # Reduced entry threshold in bear
            'momentum_weight': 0.4,        # Weight for momentum signals
            'grade_weight': 0.3,           # Weight for grade signals
            'freshness_weight': 0.3,       # Weight for token age
            'profit_target': 0.12,         # 12% take profit
            'stop_loss': 0.07,            # 7% stop loss
            'position_size': 0.08          # 8% per trade
        }
        self.sentiment_history = []
        self.performance_history = []
        
    def calculate_sentiment(self, trade_data: Dict) -> float:
        """
        Calculate social sentiment score from trade metadata
        Returns 0-1 score where 1 = very bullish
        """
        score = 0.0
        
        # Grade-based sentiment
        grade = trade_data.get('grade', 'C')
        grade_scores = {'A+': 1.0, 'A': 0.9, 'B': 0.7, 'C': 0.5, 'D': 0.3, 'F': 0.1}
        grade_score = grade_scores.get(grade, 0.5) * self.learning_params['grade_weight']
        
        # Momentum signals in entry reason
        entry_reason = trade_data.get('entry_reason', '').lower()
        momentum_score = 0.0
        bullish_keywords = ['strong momentum', 'high 5m volume', 'ultra fresh']
        for keyword in bullish_keywords:
            if keyword in entry_reason:
                momentum_score += 0.33
        momentum_score = min(momentum_score, 1.0) * self.learning_params['momentum_weight']
        
        # Token freshness (newer = more social hype)
        age_hours = trade_data.get('age_hours', 999)
        freshness_score = 1.0 if age_hours < 6 else (0.7 if age_hours < 12 else 0.4)
        freshness_score *= self.learning_params['freshness_weight']
        
        # Market phase adjustment
        phase = trade_data.get('market_phase', trade_data.get('phase', 'NEUTRAL'))
        if phase == 'BULL':
            phase_multiplier = self.learning_params['bullish_boost']
        elif phase == 'BEAR':
            phase_multiplier = self.learning_params['bearish_filter']
        else:
            phase_multiplier = 1.0
            
        score = (grade_score + momentum_score + freshness_score) * phase_multiplier
        return min(score, 1.0)
    
    def analyze_token_name(self, symbol: str) -> float:
        """
        Viral potential from token name (meme indicators)
        """
        symbol_lower = symbol.lower()
        viral_patterns = [
            r'(inu|doge|shib|floki)',  # Dog meme
            r'(ai|gpt|llm)',            # AI hype
            r'(pepe|wojak|chad)',       # Meme characters
            r'(moon|mars|galaxy)',      # Space themes
            r'(420|69)',                # Meme numbers
        ]
        
        viral_score = 0.0
        for pattern in viral_patterns:
            if re.search(pattern, symbol_lower):
                viral_score += 0.2
                
        return min(viral_score, 1.0)
    
    def should_enter(self, trade_data: Dict) -> tuple[bool, float]:
        """
        Entry logic: Enter when social sentiment is high
        """
        sentiment = self.calculate_sentiment(trade_data)
        viral_boost = self.analyze_token_name(trade_data.get('symbol', ''))
        
        # Combine scores
        final_score = sentiment * (1 + viral_boost * 0.5)
        
        # Only enter if sentiment meets threshold
        if final_score >= self.learning_params['sentiment_threshold']:
            return True, final_score
        return False, final_score
    
    def execute_trade(self, trade_data: Dict, sentiment: float) -> Dict[str, Any]:
        """
        Execute trade based on sentiment
        """
        result = trade_data.get('result', 'unknown')
        pnl_pct = trade_data.get('pnl_pct', 0)
        pnl_sol = trade_data.get('pnl_sol', 0)
        
        # Adjust position size based on sentiment confidence
        position_multiplier = min(sentiment * 1.5, 1.0)
        position_size = min(
            self.state.balance * self.learning_params['position_size'] * position_multiplier,
            self.state.balance * 0.15  # Max 15% per trade
        )
        
        trade = Trade(
            symbol=trade_data.get('symbol', 'UNKNOWN'),
            pnl_pct=pnl_pct,
            pnl_sol=pnl_sol,
            entry_reason=trade_data.get('entry_reason', 'Social sentiment'),
            exit_reason=trade_data.get('exit_reason', 'Sentiment exit'),
            sentiment_score=sentiment,
            day=trade_data.get('day', 0),
            position_size=position_size
        )
        
        self.state.trades.append(trade)
        self.state.total_trades += 1
        
        # Update balance
        if result == 'win':
            self.state.wins += 1
            self.state.balance += pnl_sol
        else:
            self.state.losses += 1
            self.state.balance += pnl_sol  # pnl_sol already negative
        
        # Track sentiment-performance correlation
        self.sentiment_history.append({
            'sentiment': sentiment,
            'pnl': pnl_pct,
            'result': result
        })
            
        return trade_data
    
    def evolve_parameters(self):
        """
        Learning: Adjust sentiment weights based on what works
        """
        if len(self.state.trades) < 15:
            return
            
        recent = self.state.trades[-15:]
        
        # Analyze correlation between sentiment and returns
        high_sentiment = [t for t in recent if t.sentiment_score > 0.7]
        low_sentiment = [t for t in recent if t.sentiment_score < 0.7]
        
        if high_sentiment and low_sentiment:
            high_avg = statistics.mean([t.pnl_pct for t in high_sentiment])
            low_avg = statistics.mean([t.pnl_pct for t in low_sentiment])
            
            # If high sentiment trades perform better, lower threshold slightly
            if high_avg > low_avg:
                self.learning_params['sentiment_threshold'] = max(
                    0.4, self.learning_params['sentiment_threshold'] * 0.98
                )
            else:
                self.learning_params['sentiment_threshold'] = min(
                    0.8, self.learning_params['sentiment_threshold'] * 1.02
                )
        
        # Adjust momentum weight based on win rate of momentum trades
        momentum_wins = [t for t in recent if 'momentum' in t.entry_reason.lower() and t.pnl_pct > 0]
        momentum_total = [t for t in recent if 'momentum' in t.entry_reason.lower()]
        
        if momentum_total:
            momentum_wr = len(momentum_wins) / len(momentum_total)
            if momentum_wr > 0.55:
                self.learning_params['momentum_weight'] = min(0.6, self.learning_params['momentum_weight'] * 1.05)
            elif momentum_wr < 0.4:
                self.learning_params['momentum_weight'] = max(0.2, self.learning_params['momentum_weight'] * 0.95)
        
        win_rate = self.state.wins / max(self.state.total_trades, 1)
        avg_return = statistics.mean([t.pnl_pct for t in recent])
        
        self.performance_history.append({
            'trade_count': len(self.state.trades),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'params': self.learning_params.copy()
        })
    
    def run_backtest(self, data_path: str) -> Dict[str, Any]:
        """
        Run full backtest
        """
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        trades = data.get('trades', [])
        
        print(f"📊 Social Sentinel: Processing {len(trades)} trades...")
        
        for i, trade_data in enumerate(trades):
            should_enter, sentiment = self.should_enter(trade_data)
            if should_enter:
                self.execute_trade(trade_data, sentiment)
                
                if self.state.total_trades % 25 == 0:
                    self.evolve_parameters()
        
        # Calculate sentiment correlation
        if self.sentiment_history:
            sentiments = [s['sentiment'] for s in self.sentiment_history]
            pnls = [s['pnl'] for s in self.sentiment_history]
            
            # Simple correlation calculation
            if len(sentiments) > 1:
                mean_s = statistics.mean(sentiments)
                mean_p = statistics.mean(pnls)
                numerator = sum((s - mean_s) * (p - mean_p) for s, p in zip(sentiments, pnls))
                denom_s = sum((s - mean_s) ** 2 for s in sentiments) ** 0.5
                denom_p = sum((p - mean_p) ** 2 for p in pnls) ** 0.5
                
                correlation = numerator / (denom_s * denom_p) if denom_s * denom_p > 0 else 0
            else:
                correlation = 0
        else:
            correlation = 0
        
        results = {
            'strategy': 'Social Sentinel',
            'description': 'Uses sentiment/social indicators from trade metadata',
            'initial_balance': 1.0,
            'final_balance': round(self.state.balance, 6),
            'total_return_pct': round((self.state.balance - 1.0) * 100, 2),
            'total_trades': self.state.total_trades,
            'wins': self.state.wins,
            'losses': self.state.losses,
            'win_rate_pct': round(self.state.wins / max(self.state.total_trades, 1) * 100, 2),
            'avg_trade_return_pct': round(
                sum(t.pnl_pct for t in self.state.trades) / max(len(self.state.trades), 1), 2
            ),
            'sentiment_correlation': round(correlation, 4),
            'learning_history': self.performance_history,
            'final_params': self.learning_params,
            'sentiment_stats': {
                'avg_sentiment': round(statistics.mean([t.sentiment_score for t in self.state.trades]) if self.state.trades else 0, 3),
                'high_sentiment_wins': len([t for t in self.state.trades if t.sentiment_score > 0.7 and t.pnl_pct > 0]),
                'total_high_sentiment': len([t for t in self.state.trades if t.sentiment_score > 0.7])
            },
            'trades': [{
                'symbol': t.symbol,
                'pnl_pct': round(t.pnl_pct, 2),
                'pnl_sol': round(t.pnl_sol, 6),
                'sentiment': round(t.sentiment_score, 3),
                'day': t.day
            } for t in self.state.trades]
        }
        
        return results


def main():
    sentinel = SocialSentinel(initial_balance=1.0)
    results = sentinel.run_backtest('/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json')
    
    output_path = '/home/skux/.openclaw/workspace/social_sentinel_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Social Sentinel Results:")
    print(f"   Initial: 1.0 SOL")
    print(f"   Final: {results['final_balance']:.6f} SOL")
    print(f"   Return: {results['total_return_pct']:+.2f}%")
    print(f"   Trades: {results['total_trades']} (Win rate: {results['win_rate_pct']}%)")
    print(f"   Avg Sentiment: {results['sentiment_stats']['avg_sentiment']}")
    print(f"   Results saved to: {output_path}")


if __name__ == '__main__':
    main()
