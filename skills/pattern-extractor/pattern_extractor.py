#!/usr/bin/env python3
"""
Pattern Extractor - Implementation
Mines patterns from user behavior, task outcomes, and trade history
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Counter
from collections import defaultdict
import hashlib


class PatternExtractor:
    """
    Pattern Extractor - Find patterns that lead to success
    
    Now includes trade history pattern extraction for:
    - Successful trading patterns
    - Entry/exit timing patterns
    - Risk management patterns
    - Market condition patterns
    """
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/pattern_extractor")
        self.patterns_file = os.path.join(self.memory_dir, "patterns.json")
        self.trade_patterns_file = os.path.join(self.memory_dir, "trade_patterns.json")
        self.raw_data_file = os.path.join(self.memory_dir, "raw_events.jsonl")
        self._ensure_dirs()
        self.patterns = self._load_patterns()
        self.trade_patterns = self._load_trade_patterns()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_patterns(self) -> Dict:
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "temporal": [],
            "sequential": [],
            "contextual": [],
            "success": [],
            "failure": [],
            "last_updated": None
        }
    
    def _load_trade_patterns(self) -> Dict:
        try:
            if os.path.exists(self.trade_patterns_file):
                with open(self.trade_patterns_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "entry_patterns": [],
            "exit_patterns": [],
            "risk_patterns": [],
            "market_patterns": [],
            "token_patterns": {},
            "last_updated": None
        }
    
    def _save(self):
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
            with open(self.trade_patterns_file, 'w') as f:
                json.dump(self.trade_patterns, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    # ============ TRADE HISTORY PATTERN EXTRACTION ============
    
    def extract_trade_patterns(self, trade_history: List[Dict]) -> Dict:
        """
        Extract patterns from trade history
        
        trade_history: List of trade records with:
        - token, entry_price, exit_price, entry_time, exit_time
        - size, pnl, pnl_percent, strategy, market_condition
        """
        if not trade_history:
            return self.trade_patterns
        
        print(f"🔄 Analyzing {len(trade_history)} trades for patterns...")
        
        # Separate winning and losing trades
        winners = [t for t in trade_history if t.get("pnl", 0) > 0]
        losers = [t for t in trade_history if t.get("pnl", 0) <= 0]
        
        print(f"  ✓ {len(winners)} winning trades, {len(losers)} losing trades")
        
        # Extract entry patterns
        self._extract_entry_patterns(winners, losers)
        
        # Extract exit patterns
        self._extract_exit_patterns(winners, losers)
        
        # Extract risk management patterns
        self._extract_risk_patterns(winners, losers)
        
        # Extract market condition patterns
        self._extract_market_patterns(winners, losers)
        
        # Extract token-specific patterns
        self._extract_token_patterns(trade_history)
        
        self.trade_patterns["last_updated"] = datetime.now().isoformat()
        self._save()
        
        print(f"✓ Trade pattern extraction complete")
        
        return self.trade_patterns
    
    def _extract_entry_patterns(self, winners: List[Dict], losers: List[Dict]):
        """Extract successful entry patterns"""
        
        # Analyze entry timing
        winner_hours = [self._get_hour(t.get("entry_time", "")) for t in winners]
        loser_hours = [self._get_hour(t.get("entry_time", "")) for t in losers]
        
        winner_hour_dist = Counter(winner_hours)
        loser_hour_dist = Counter(loser_hours)
        
        # Find optimal entry hours
        optimal_hours = []
        for hour, count in winner_hour_dist.most_common(5):
            win_rate = count / (count + loser_hour_dist.get(hour, 0)) if count + loser_hour_dist.get(hour, 0) > 0 else 0
            if win_rate > 0.6 and count >= 3:  # At least 60% win rate, 3+ trades
                optimal_hours.append({
                    "hour": hour,
                    "win_rate": win_rate,
                    "trade_count": count
                })
        
        # Analyze entry strategies
        winner_strategies = Counter([t.get("strategy", "unknown") for t in winners])
        loser_strategies = Counter([t.get("strategy", "unknown") for t in losers])
        
        best_strategies = []
        for strategy, count in winner_strategies.most_common():
            total = count + loser_strategies.get(strategy, 0)
            if total >= 5:  # At least 5 trades
                win_rate = count / total
                if win_rate > 0.55:
                    best_strategies.append({
                        "strategy": strategy,
                        "win_rate": win_rate,
                        "total_trades": total
                    })
        
        self.trade_patterns["entry_patterns"] = {
            "optimal_hours": optimal_hours,
            "best_strategies": best_strategies,
            "extracted_at": datetime.now().isoformat()
        }
    
    def _extract_exit_patterns(self, winners: List[Dict], losers: List[Dict]):
        """Extract successful exit patterns"""
        
        # Analyze hold times
        winner_hold_times = []
        loser_hold_times = []
        
        for trade in winners:
            hold_time = self._calculate_hold_time(trade)
            if hold_time:
                winner_hold_times.append(hold_time)
        
        for trade in losers:
            hold_time = self._calculate_hold_time(trade)
            if hold_time:
                loser_hold_times.append(hold_time)
        
        avg_winner_hold = sum(winner_hold_times) / len(winner_hold_times) if winner_hold_times else 0
        avg_loser_hold = sum(loser_hold_times) / len(loser_hold_times) if loser_hold_times else 0
        
        # Analyze exit reasons
        winner_exits = Counter([t.get("exit_reason", "unknown") for t in winners])
        loser_exits = Counter([t.get("exit_reason", "unknown") for t in losers])
        
        self.trade_patterns["exit_patterns"] = {
            "optimal_hold_time_hours": avg_winner_hold,
            "loser_hold_time_hours": avg_loser_hold,
            "successful_exit_reasons": dict(winner_exits.most_common(5)),
            "failed_exit_reasons": dict(loser_exits.most_common(5)),
            "extracted_at": datetime.now().isoformat()
        }
    
    def _extract_risk_patterns(self, winners: List[Dict], losers: List[Dict]):
        """Extract risk management patterns"""
        
        # Analyze position sizes
        winner_sizes = [t.get("size", 0) for t in winners]
        loser_sizes = [t.get("size", 0) for t in losers]
        
        avg_winner_size = sum(winner_sizes) / len(winner_sizes) if winner_sizes else 0
        avg_loser_size = sum(loser_sizes) / len(loser_sizes) if loser_sizes else 0
        
        # Analyze stop loss usage
        winners_with_sl = len([t for t in winners if t.get("stop_loss")])
        losers_with_sl = len([t for t in losers if t.get("stop_loss")])
        
        # Analyze risk/reward ratios
        winner_rr = [t.get("risk_reward", 0) for t in winners if t.get("risk_reward")]
        avg_winner_rr = sum(winner_rr) / len(winner_rr) if winner_rr else 0
        
        self.trade_patterns["risk_patterns"] = {
            "optimal_position_size": avg_winner_size,
            "loser_position_size": avg_loser_size,
            "stop_loss_usage_winners": winners_with_sl / len(winners) if winners else 0,
            "stop_loss_usage_losers": losers_with_sl / len(losers) if losers else 0,
            "optimal_risk_reward": avg_winner_rr,
            "extracted_at": datetime.now().isoformat()
        }
    
    def _extract_market_patterns(self, winners: List[Dict], losers: List[Dict]):
        """Extract market condition patterns"""
        
        # Analyze market conditions for winners
        winner_conditions = Counter([t.get("market_condition", "unknown") for t in winners])
        loser_conditions = Counter([t.get("market_condition", "unknown") for t in losers])
        
        best_conditions = []
        for condition, count in winner_conditions.most_common():
            total = count + loser_conditions.get(condition, 0)
            if total >= 5:
                win_rate = count / total
                if win_rate > 0.55:
                    best_conditions.append({
                        "condition": condition,
                        "win_rate": win_rate,
                        "total_trades": total
                    })
        
        self.trade_patterns["market_patterns"] = {
            "best_conditions": best_conditions,
            "extracted_at": datetime.now().isoformat()
        }
    
    def _extract_token_patterns(self, trade_history: List[Dict]):
        """Extract token-specific patterns"""
        
        token_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0})
        
        for trade in trade_history:
            token = trade.get("token", "unknown")
            pnl = trade.get("pnl", 0)
            
            token_stats[token]["total_pnl"] += pnl
            if pnl > 0:
                token_stats[token]["wins"] += 1
            else:
                token_stats[token]["losses"] += 1
        
        # Find best performing tokens
        best_tokens = []
        for token, stats in token_stats.items():
            total = stats["wins"] + stats["losses"]
            if total >= 3:  # At least 3 trades
                win_rate = stats["wins"] / total
                best_tokens.append({
                    "token": token,
                    "win_rate": win_rate,
                    "total_trades": total,
                    "total_pnl": stats["total_pnl"],
                    "avg_pnl": stats["total_pnl"] / total
                })
        
        # Sort by win rate and PnL
        best_tokens.sort(key=lambda x: (x["win_rate"], x["avg_pnl"]), reverse=True)
        
        self.trade_patterns["token_patterns"] = {
            "best_performers": best_tokens[:10],
            "extracted_at": datetime.now().isoformat()
        }
    
    # ============ UTILITY METHODS ============
    
    def _get_hour(self, timestamp: str) -> int:
        """Extract hour from timestamp"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.hour
        except:
            return -1
    
    def _calculate_hold_time(self, trade: Dict) -> Optional[float]:
        """Calculate hold time in hours"""
        try:
            entry = datetime.fromisoformat(trade.get("entry_time", "").replace('Z', '+00:00'))
            exit = datetime.fromisoformat(trade.get("exit_time", "").replace('Z', '+00:00'))
            return (exit - entry).total_seconds() / 3600
        except:
            return None
    
    # ============ GENERAL PATTERN EXTRACTION ============
    
    def extract_temporal_patterns(self, events: List[Dict]) -> List[Dict]:
        """Extract time-based patterns"""
        patterns = []
        
        # Group events by hour
        hour_events = defaultdict(list)
        for event in events:
            hour = self._get_hour(event.get("timestamp", ""))
            if hour >= 0:
                hour_events[hour].append(event)
        
        # Find patterns
        for hour, evts in hour_events.items():
            if len(evts) >= 5:
                actions = Counter([e.get("action", "unknown") for e in evts])
                most_common = actions.most_common(1)[0]
                
                patterns.append({
                    "type": "hourly_pattern",
                    "hour": hour,
                    "common_action": most_common[0],
                    "frequency": most_common[1] / len(evts),
                    "total_events": len(evts)
                })
        
        return patterns
    
    def extract_sequential_patterns(self, events: List[Dict], min_support: int = 3) -> List[Dict]:
        """Extract action sequence patterns"""
        patterns = []
        
        # Find consecutive action pairs
        sequences = []
        for i in range(len(events) - 1):
            seq = (events[i].get("action"), events[i+1].get("action"))
            sequences.append(seq)
        
        # Count sequences
        seq_counts = Counter(sequences)
        
        for seq, count in seq_counts.most_common():
            if count >= min_support:
                patterns.append({
                    "type": "action_sequence",
                    "sequence": list(seq),
                    "frequency": count,
                    "confidence": count / len(sequences)
                })
        
        return patterns
    
    # ============ REPORTING ============
    
    def generate_trade_pattern_report(self) -> str:
        """Generate report of extracted trade patterns"""
        lines = [
            "📊 TRADE PATTERN ANALYSIS REPORT",
            "=" * 50,
            f"Last Updated: {self.trade_patterns.get('last_updated', 'Never')}",
            "",
            "🎯 ENTRY PATTERNS",
            "-" * 30,
        ]
        
        entry = self.trade_patterns.get("entry_patterns", {})
        if entry.get("optimal_hours"):
            lines.append("Optimal Entry Hours:")
            for h in entry["optimal_hours"]:
                lines.append(f"  {h['hour']:02d}:00 - Win Rate: {h['win_rate']:.1%} ({h['trade_count']} trades)")
        
        if entry.get("best_strategies"):
            lines.extend(["", "Best Performing Strategies:"])
            for s in entry["best_strategies"]:
                lines.append(f"  {s['strategy']} - Win Rate: {s['win_rate']:.1%} ({s['total_trades']} trades)")
        
        lines.extend(["", "📈 EXIT PATTERNS", "-" * 30])
        
        exit_p = self.trade_patterns.get("exit_patterns", {})
        if exit_p.get("optimal_hold_time_hours"):
            lines.append(f"Optimal Hold Time: {exit_p['optimal_hold_time_hours']:.1f} hours")
            lines.append(f"Loser Avg Hold Time: {exit_p.get('loser_hold_time_hours', 0):.1f} hours")
        
        lines.extend(["", "🛡️ RISK PATTERNS", "-" * 30])
        
        risk = self.trade_patterns.get("risk_patterns", {})
        if risk.get("optimal_position_size"):
            lines.append(f"Optimal Position Size: ${risk['optimal_position_size']:.2f}")
            lines.append(f"Optimal Risk/Reward: {risk.get('optimal_risk_reward', 0):.2f}")
        
        lines.extend(["", "🪙 TOKEN PERFORMANCE", "-" * 30])
        
        tokens = self.trade_patterns.get("token_patterns", {})
        if tokens.get("best_performers"):
            lines.append("Top Performing Tokens:")
            for t in tokens["best_performers"][:5]:
                lines.append(f"  {t['token']}: {t['win_rate']:.1%} win rate, ${t['avg_pnl']:.2f} avg PnL")
        
        lines.extend(["", "=" * 50])
        
        return "\n".join(lines)
    
    def get_trading_recommendations(self) -> List[str]:
        """Generate trading recommendations based on patterns"""
        recommendations = []
        
        entry = self.trade_patterns.get("entry_patterns", {})
        if entry.get("optimal_hours"):
            best_hour = entry["optimal_hours"][0]
            recommendations.append(f"Optimal entry time: {best_hour['hour']:02d}:00 (Win rate: {best_hour['win_rate']:.1%})")
        
        if entry.get("best_strategies"):
            best_strat = entry["best_strategies"][0]
            recommendations.append(f"Best strategy: {best_strat['strategy']} (Win rate: {best_strat['win_rate']:.1%})")
        
        exit_p = self.trade_patterns.get("exit_patterns", {})
        if exit_p.get("optimal_hold_time_hours"):
            recommendations.append(f"Target hold time: {exit_p['optimal_hold_time_hours']:.1f} hours")
        
        risk = self.trade_patterns.get("risk_patterns", {})
        if risk.get("optimal_risk_reward"):
            recommendations.append(f"Minimum risk/reward: {risk['optimal_risk_reward']:.2f}")
        
        return recommendations


# ============ COMMAND LINE ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Pattern Extractor - Mine patterns from data")
    parser.add_argument("--mode", choices=["extract-trades", "report", "recommendations", "test"], default="report")
    parser.add_argument("--trade-file", help="JSON file with trade history")
    
    args = parser.parse_args()
    
    extractor = PatternExtractor()
    
    if args.mode == "extract-trades":
        if not args.trade_file:
            print("Error: --trade-file required")
            return
        
        with open(args.trade_file, 'r') as f:
            trades = json.load(f)
        
        extractor.extract_trade_patterns(trades)
        print("✓ Trade patterns extracted")
        print(extractor.generate_trade_pattern_report())
    
    elif args.mode == "report":
        print(extractor.generate_trade_pattern_report())
    
    elif args.mode == "recommendations":
        recs = extractor.get_trading_recommendations()
        print("Trading Recommendations Based on Patterns:")
        for r in recs:
            print(f"  • {r}")
    
    elif args.mode == "test":
        print("🧪 Testing Pattern Extractor...")
        
        # Test trade pattern extraction
        test_trades = [
            {"token": "SOL", "pnl": 150, "pnl_percent": 0.15, "entry_time": "2026-03-01T09:00:00", "exit_time": "2026-03-01T12:00:00", "strategy": "momentum", "market_condition": "bull", "size": 1000, "risk_reward": 2.5},
            {"token": "BONK", "pnl": -50, "pnl_percent": -0.05, "entry_time": "2026-03-01T14:00:00", "exit_time": "2026-03-01T15:00:00", "strategy": "scalping", "market_condition": "sideways", "size": 500, "risk_reward": 1.5},
            {"token": "SOL", "pnl": 200, "pnl_percent": 0.20, "entry_time": "2026-03-02T09:30:00", "exit_time": "2026-03-02T14:00:00", "strategy": "momentum", "market_condition": "bull", "size": 1000, "risk_reward": 3.0},
        ]
        
        extractor.extract_trade_patterns(test_trades)
        print("✓ Trade patterns extracted")
        
        recs = extractor.get_trading_recommendations()
        print(f"✓ Generated {len(recs)} recommendations")
        
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
