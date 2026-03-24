#!/usr/bin/env python3
"""
🔄 DUPLICATE CHECKER
Prevents buying the same token multiple times
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

TRADE_LOG = "/home/skux/.openclaw/workspace/agents/lux_trader/live_trades.json"
STATE_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/luxtrader_state.json"
COOLDOWN_HOURS = 24  # Don't rebuy within 24 hours

class DuplicateChecker:
    """Check for duplicate trades"""
    
    def __init__(self):
        self.cooldown_hours = COOLDOWN_HOURS
    
    def load_trade_history(self) -> List[Dict]:
        """Load trade history from log"""
        if os.path.exists(TRADE_LOG):
            try:
                with open(TRADE_LOG, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def load_active_positions(self) -> Dict[str, Dict]:
        """Load active positions from state"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    return state.get("positions", {})
            except:
                return {}
        return {}
    
    def is_in_portfolio(self, token_address: str) -> Tuple[bool, str]:
        """Check if token is currently held"""
        positions = self.load_active_positions()
        
        if token_address in positions:
            position = positions[token_address]
            symbol = position.get("symbol", "UNKNOWN")
            entry_time = position.get("entry_time", "unknown")
            return True, f"Already in portfolio: {symbol} (bought {entry_time})"
        
        return False, ""
    
    def was_recently_traded(self, token_address: str, hours: int = None) -> Tuple[bool, str]:
        """Check if token was traded recently"""
        if hours is None:
            hours = self.cooldown_hours
        
        trades = self.load_trade_history()
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for trade in trades:
            # Check if trade is for this token
            if trade.get("address") == token_address:
                # Check timestamp
                trade_time_str = trade.get("timestamp", "")
                try:
                    trade_time = datetime.fromisoformat(trade_time_str)
                    if trade_time > cutoff_time:
                        symbol = trade.get("symbol", "UNKNOWN")
                        time_ago = datetime.now() - trade_time
                        hours_ago = time_ago.total_seconds() / 3600
                        return True, f"Traded {hours_ago:.1f}h ago: {symbol}"
                except:
                    # If we can't parse time, assume it's old
                    continue
        
        return False, ""
    
    def can_buy(self, token_address: str, symbol: str = "") -> Tuple[bool, str]:
        """
        Comprehensive check if token can be bought
        Returns: (can_buy, reason)
        """
        # Check 1: Already in portfolio
        in_portfolio, reason = self.is_in_portfolio(token_address)
        if in_portfolio:
            return False, reason
        
        # Check 2: Recently traded
        recently_traded, reason = self.was_recently_traded(token_address)
        if recently_traded:
            return False, reason
        
        # Check 3: Blacklist (optional)
        if self.is_blacklisted(token_address):
            return False, "Token is blacklisted"
        
        return True, "OK to buy"
    
    def is_blacklisted(self, token_address: str) -> bool:
        """Check if token is blacklisted"""
        # Could load from file or hardcode known scams
        blacklist = self.load_blacklist()
        return token_address in blacklist
    
    def load_blacklist(self) -> List[str]:
        """Load blacklist of known scam tokens"""
        blacklist_file = "/home/skux/.openclaw/workspace/agents/lux_trader/token_blacklist.json"
        if os.path.exists(blacklist_file):
            try:
                with open(blacklist_file, 'r') as f:
                    data = json.load(f)
                    return data.get("blacklist", [])
            except:
                pass
        return []
    
    def add_to_blacklist(self, token_address: str, reason: str = ""):
        """Add token to blacklist"""
        blacklist_file = "/home/skux/.openclaw/workspace/agents/lux_trader/token_blacklist.json"
        
        blacklist = self.load_blacklist()
        if token_address not in blacklist:
            blacklist.append(token_address)
            
            data = {
                "blacklist": blacklist,
                "updated": datetime.now().isoformat(),
                "reasons": {token_address: reason}
            }
            
            with open(blacklist_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def get_trade_count_24h(self) -> int:
        """Get number of trades in last 24 hours"""
        trades = self.load_trade_history()
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        count = 0
        for trade in trades:
            trade_time_str = trade.get("timestamp", "")
            try:
                trade_time = datetime.fromisoformat(trade_time_str)
                if trade_time > cutoff_time:
                    count += 1
            except:
                continue
        
        return count
    
    def get_unique_tokens_24h(self) -> List[str]:
        """Get list of unique tokens traded in last 24 hours"""
        trades = self.load_trade_history()
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        tokens = set()
        for trade in trades:
            trade_time_str = trade.get("timestamp", "")
            try:
                trade_time = datetime.fromisoformat(trade_time_str)
                if trade_time > cutoff_time:
                    token = trade.get("address", "")
                    if token:
                        tokens.add(token)
            except:
                continue
        
        return list(tokens)
    
    def print_status(self):
        """Print duplicate checker status"""
        print("\n" + "="*60)
        print("🔄 DUPLICATE CHECKER STATUS")
        print("="*60)
        
        # Active positions
        positions = self.load_active_positions()
        print(f"\n📊 Active Positions: {len(positions)}")
        for addr, pos in positions.items():
            print(f"   • {pos.get('symbol', 'UNKNOWN')}: {addr[:20]}...")
        
        # Recent trades
        trades_24h = self.get_trade_count_24h()
        unique_tokens = self.get_unique_tokens_24h()
        print(f"\n📈 Trades (24h): {trades_24h}")
        print(f"   Unique tokens: {len(unique_tokens)}")
        
        # Blacklist
        blacklist = self.load_blacklist()
        print(f"\n🚫 Blacklisted tokens: {len(blacklist)}")
        
        print("="*60)


# Convenience functions
def can_buy_token(token_address: str, symbol: str = "") -> Tuple[bool, str]:
    """Check if token can be bought"""
    checker = DuplicateChecker()
    return checker.can_buy(token_address, symbol)


def is_duplicate(token_address: str) -> bool:
    """Quick check if token is duplicate"""
    can_buy, _ = can_buy_token(token_address)
    return not can_buy


if __name__ == "__main__":
    # Test
    checker = DuplicateChecker()
    checker.print_status()
    
    # Test checks
    test_token = "TEST_TOKEN_ADDRESS_123"
    can_buy, reason = can_buy_token(test_token, "TEST")
    print(f"\nCan buy {test_token}: {'✅' if can_buy else '❌'} {reason}")
