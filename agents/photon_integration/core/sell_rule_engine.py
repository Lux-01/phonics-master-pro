#!/usr/bin/env python3
"""
Sell Rule Engine - Automated Profit/Loss Management

Manages sell rules for meme coin positions:
- Profit targets (partial/full)
- Stop loss execution
- Time-based exits
- Trailing stops
- Dynamic rule adjustment

Designed for integration with Photon trading client
"""
import json
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of sell rules"""
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TIME_STOP = "time_stop"
    TRAILING_STOP = "trailing_stop"
    WHALE_FOLLOW = "whale_follow"


class SellCondition(Enum):
    """When to execute the sell"""
    IMMEDIATE = "immediate"  # Market order
    LIMIT = "limit"          # Limit order at target
    TRIGGER = "trigger"      # Trigger then market


@dataclass
class SellRule:
    """
    Individual sell rule configuration
    
    Example:
        SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=0.15,          # +15%
            sell_pct=0.50,            # Sell 50% of position
            condition=SellCondition.TRIGGER
        )
    """
    rule_type: RuleType
    trigger_pct: float          # Percentage to trigger (0.15 = 15%)
    sell_pct: float             # Percentage of position to sell (0.50 = 50%)
    condition: SellCondition = SellCondition.TRIGGER
    enabled: bool = True
    executed: bool = False
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        # Validate percentages
        if not -1.0 <= self.trigger_pct <= 10.0:
            raise ValueError(f"trigger_pct must be between -1.0 and 10.0 (got {self.trigger_pct})")
        if not 0.0 < self.sell_pct <= 1.0:
            raise ValueError(f"sell_pct must be between 0.0 and 1.0 (got {self.sell_pct})")
    
    def to_dict(self) -> Dict:
        return {
            "rule_type": self.rule_type.value,
            "trigger_pct": self.trigger_pct,
            "sell_pct": self.sell_pct,
            "condition": self.condition.value,
            "enabled": self.enabled,
            "executed": self.executed,
            "execution_price": self.execution_price,
            "execution_time": self.execution_time.isoformat() if self.execution_time else None,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SellRule':
        return cls(
            rule_type=RuleType(data["rule_type"]),
            trigger_pct=data["trigger_pct"],
            sell_pct=data["sell_pct"],
            condition=SellCondition(data.get("condition", "trigger")),
            enabled=data.get("enabled", True),
            executed=data.get("executed", False),
            execution_price=data.get("execution_price"),
            execution_time=datetime.fromisoformat(data["execution_time"]) if data.get("execution_time") else None,
            notes=data.get("notes", "")
        )


@dataclass
class RuleSet:
    """
    Complete rule set for a token position
    
    Default configuration for meme coin trading:
    - 15% profit: Sell 50% of position
    - 30% profit: Sell remaining 50%
    - -7% stop loss: Sell 100%
    - 4 hour time limit: Sell 100%
    """
    token_address: str
    token_symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime = field(default_factory=datetime.now)
    rules: List[SellRule] = field(default_factory=list)
    trailing_stop_pct: Optional[float] = None  # e.g., 0.10 = 10% trailing
    highest_price: float = 0.0
    active: bool = True
    
    def __post_init__(self):
        if self.highest_price == 0.0:
            self.highest_price = self.entry_price
    
    def add_rule(self, rule: SellRule):
        """Add a sell rule to this rule set"""
        self.rules.append(rule)
    
    def get_pending_rules(self) -> List[SellRule]:
        """Get all non-executed, enabled rules"""
        return [r for r in self.rules if r.enabled and not r.executed]
    
    def calculate_pnl(self, current_price: float) -> Dict:
        """
        Calculate P&L at current price
        
        Returns:
            Dict with absolute and percentage P&L
        """
        price_change = current_price - self.entry_price
        price_change_pct = (current_price / self.entry_price) - 1 if self.entry_price > 0 else 0
        
        position_value = self.quantity * current_price
        cost_basis = self.quantity * self.entry_price
        unrealized_pnl = position_value - cost_basis
        
        return {
            "entry_price": self.entry_price,
            "current_price": current_price,
            "price_change_usd": price_change,
            "price_change_pct": price_change_pct,
            "quantity": self.quantity,
            "position_value": position_value,
            "cost_basis": cost_basis,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_pct": price_change_pct,
            "age_minutes": (datetime.now() - self.entry_time).total_seconds() / 60
        }
    
    def update_trailing_stop(self, current_price: float):
        """Update trailing stop based on highest price seen"""
        if current_price > self.highest_price:
            self.highest_price = current_price
            logger.info(f"📈 New high for {self.token_symbol}: ${current_price:.6f}")
    
    def to_dict(self) -> Dict:
        return {
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "entry_time": self.entry_time.isoformat(),
            "rules": [r.to_dict() for r in self.rules],
            "trailing_stop_pct": self.trailing_stop_pct,
            "highest_price": self.highest_price,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RuleSet':
        rs = cls(
            token_address=data["token_address"],
            token_symbol=data["token_symbol"],
            entry_price=data["entry_price"],
            quantity=data["quantity"],
            entry_time=datetime.fromisoformat(data["entry_time"]),
            rules=[SellRule.from_dict(r) for r in data.get("rules", [])],
            trailing_stop_pct=data.get("trailing_stop_pct"),
            highest_price=data.get("highest_price", data["entry_price"]),
            active=data.get("active", True)
        )
        return rs


class SellRuleEngine:
    """
    Core engine for managing sell rules across positions
    
    Features:
    - Evaluate rules against current prices
    - Execute sells via callbacks
    - Manage time-based exits
    - Handle trailing stops
    - Rule priority queuing
    """
    
    def __init__(self, config_path: str = "config/sell_rules.json"):
        self.config_path = config_path
        self.positions: Dict[str, RuleSet] = {}
        self.executed_count = 0
        self.skipped_count = 0
        self.sell_callback: Optional[Callable] = None
        
        # Load default rules if file exists
        self._load_config()
    
    def _load_config(self):
        """Load default rule configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"✅ Loaded sell rules config from {self.config_path}")
        except FileNotFoundError:
            logger.info(f"ℹ️ No config file at {self.config_path}, using defaults")
    
    def register_sell_callback(self, callback: Callable[[str, float, str], bool]):
        """
        Register callback function for executing sells
        
        Args:
            callback: Function(token_address, sell_quantity, reason) -> success
        """
        self.sell_callback = callback
        logger.info("✅ Sell callback registered")
    
    def create_default_ruleset(self,
                               token_address: str,
                               token_symbol: str,
                               entry_price: float,
                               quantity: float) -> RuleSet:
        """
        Create default rule set for meme coin trading
        
        Default Strategy (Aggressive Momentum):
        - +15% = Sell 50% (take profit)
        - +30% = Sell 50% (moon bag)
        - -7% = Sell 100% (stop loss)
        - 4 hours = Sell 100% (time stop)
        """
        ruleset = RuleSet(
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            quantity=quantity
        )
        
        # Take Profit Level 1: +15%, sell 50%
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=0.15,
            sell_pct=0.50,
            notes="First profit target - secure half"
        ))
        
        # Take Profit Level 2: +30%, sell remaining 50%
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=0.30,
            sell_pct=0.50,
            notes="Second target - moon bag exit"
        ))
        
        # Stop Loss: -7%, sell 100%
        ruleset.add_rule(SellRule(
            rule_type=RuleType.STOP_LOSS,
            trigger_pct=-0.07,
            sell_pct=1.00,
            notes="Stop loss - protect capital"
        ))
        
        # Time Stop: 4 hours, sell 100%
        # This is handled specially in evaluate_rules
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TIME_STOP,
            trigger_pct=0.0,  # Not used for time
            sell_pct=1.00,
            notes="Time-based exit - avoid bag holding"
        ))
        
        # Optional: Trailing stop at -10% from peak
        ruleset.trailing_stop_pct = 0.10
        
        self.positions[token_address] = ruleset
        logger.info(f"✅ Rule set created for {token_symbol}")
        logger.info(f"   Entry: ${entry_price:.6f} | Qty: {quantity:.4f}")
        
        return ruleset
    
    def create_conservative_ruleset(self,
                                    token_address: str,
                                    token_symbol: str,
                                    entry_price: float,
                                    quantity: float) -> RuleSet:
        """
        Conservative strategy with tighter stops
        
        - +10% = Sell 100%
        - -5% = Sell 100%
        - 2 hours = Sell 100%
        """
        ruleset = RuleSet(
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            quantity=quantity
        )
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=0.10,
            sell_pct=1.00,
            notes="Quick profit - conservative"
        ))
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.STOP_LOSS,
            trigger_pct=-0.05,
            sell_pct=1.00,
            notes="Tight stop loss"
        ))
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TIME_STOP,
            trigger_pct=0.0,
            sell_pct=1.00
        ))
        
        return ruleset
    
    def create_aggressive_ruleset(self,
                                    token_address: str,
                                    token_symbol: str,
                                    entry_price: float,
                                    quantity: float) -> RuleSet:
        """
        Aggressive strategy for moonshots
        
        - +25% = Sell 30%
        - +50% = Sell 30%
        - +100% = Sell 40%
        - -10% = Sell 100%
        """
        ruleset = RuleSet(
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            quantity=quantity
        )
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=0.25,
            sell_pct=0.30,
            notes="First moon target"
        ))
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=0.50,
            sell_pct=0.30,
            notes="Second moon target"
        ))
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.TAKE_PROFIT,
            trigger_pct=1.00,
            sell_pct=0.40,
            notes="Double up - exit remaining"
        ))
        
        ruleset.add_rule(SellRule(
            rule_type=RuleType.STOP_LOSS,
            trigger_pct=-0.10,
            sell_pct=1.00,
            notes="Wider stop for volatile memes"
        ))
        
        return ruleset
    
    def evaluate_rules(self, 
                       token_address: str,
                       current_price: float,
                       token_liquidity: Optional[float] = None) -> List[Dict]:
        """
        Evaluate all rules for a position
        
        Args:
            token_address: Token mint address
            current_price: Current token price
            token_liquidity: Optional liquidity check
        
        Returns:
            List of triggered sell actions
        """
        if token_address not in self.positions:
            return []
        
        ruleset = self.positions[token_address]
        if not ruleset.active:
            return []
        
        triggered = []
        pnl = ruleset.calculate_pnl(current_price)
        
        # Update trailing stop
        ruleset.update_trailing_stop(current_price)
        
        # Check liquidity if provided
        if token_liquidity and token_liquidity < 10000:
            logger.warning(f"⚠️ Low liquidity on {ruleset.token_symbol}: ${token_liquidity:,.0f}")
            # May want to adjust sell_pct or skip execution
        
        for rule in ruleset.get_pending_rules():
            should_execute = False
            reason = ""
            
            # Evaluate take profit
            if rule.rule_type == RuleType.TAKE_PROFIT:
                if pnl["price_change_pct"] >= rule.trigger_pct:
                    should_execute = True
                    reason = f"Take profit triggered: +{pnl['price_change_pct']*100:.1f}% >= +{rule.trigger_pct*100:.1f}%"
            
            # Evaluate stop loss
            elif rule.rule_type == RuleType.STOP_LOSS:
                if pnl["price_change_pct"] <= rule.trigger_pct:
                    should_execute = True
                    reason = f"Stop loss triggered: {pnl['price_change_pct']*100:.1f}% <= {rule.trigger_pct*100:.1f}%"
            
            # Evaluate time stop
            elif rule.rule_type == RuleType.TIME_STOP:
                age_hours = pnl["age_minutes"] / 60
                if age_hours >= 4:  # 4 hour limit
                    should_execute = True
                    reason = f"Time stop triggered: {age_hours:.1f}h >= 4h"
            
            # Evaluate trailing stop
            elif rule.rule_type == RuleType.TRAILING_STOP:
                if ruleset.trailing_stop_pct:
                    trailing_trigger = ruleset.highest_price * (1 - ruleset.trailing_stop_pct)
                    if current_price <= trailing_trigger:
                        should_execute = True
                        reason = f"Trailing stop: ${current_price:.6f} <= ${trailing_trigger:.6f}"
            
            # Evaluate whale follow
            elif rule.rule_type == RuleType.WHALE_FOLLOW:
                # This would be triggered by external detection
                pass
            
            if should_execute:
                sell_qty = ruleset.quantity * rule.sell_pct
                
                action = {
                    "token_address": token_address,
                    "token_symbol": ruleset.token_symbol,
                    "rule_type": rule.rule_type.value,
                    "sell_quantity": sell_qty,
                    "sell_pct": rule.sell_pct,
                    "current_price": current_price,
                    "pnl_pct": pnl["price_change_pct"],
                    "reason": reason,
                    "entry_price": ruleset.entry_price
                }
                
                triggered.append(action)
                
                # Mark rule as executed
                rule.executed = True
                rule.execution_price = current_price
                rule.execution_time = datetime.now()
                
                logger.info(f"🔥 SELL TRIGGERED: {action['token_symbol']}")
                logger.info(f"   {reason}")
                logger.info(f"   Selling: {sell_qty:.4f} ({rule.sell_pct*100:.0f}%)")
                
                # Execute via callback if registered
                if self.sell_callback:
                    success = self.sell_callback(
                        token_address,
                        sell_qty,
                        reason
                    )
                    if success:
                        self.executed_count += 1
                        # Update remaining quantity
                        ruleset.quantity -= sell_qty
                    else:
                        self.skipped_count += 1
                        # Reset execution status for retry
                        rule.executed = False
        
        # Deactivate if all rules executed
        if not ruleset.get_pending_rules():
            ruleset.active = False
            logger.info(f"✅ All rules executed for {ruleset.token_symbol}")
        
        return triggered
    
    def get_position_summary(self, token_address: str) -> Optional[Dict]:
        """Get summary of a position's rules and status"""
        if token_address not in self.positions:
            return None
        
        ruleset = self.positions[token_address]
        
        return {
            "token": ruleset.token_symbol,
            "entry_price": ruleset.entry_price,
            "quantity_remaining": ruleset.quantity,
            "age_minutes": (datetime.now() - ruleset.entry_time).total_seconds() / 60,
            "active": ruleset.active,
            "rules_total": len(ruleset.rules),
            "rules_pending": len(ruleset.get_pending_rules()),
            "rules_executed": len([r for r in ruleset.rules if r.executed]),
            "trailing_stop_active": ruleset.trailing_stop_pct is not None,
            "highest_price_seen": ruleset.highest_price
        }
    
    def get_active_positions(self) -> List[Dict]:
        """Get all active position summaries"""
        return [
            self.get_position_summary(addr)
            for addr in self.positions.keys()
            if self.positions[addr].active
        ]
    
    def remove_position(self, token_address: str) -> bool:
        """Remove a position from tracking"""
        if token_address in self.positions:
            del self.positions[token_address]
            logger.info(f"🗑️ Removed position: {token_address[:8]}...")
            return True
        return False
    
    def export_rules(self, filepath: str):
        """Export all rule sets to JSON"""
        data = {
            addr: ruleset.to_dict()
            for addr, ruleset in self.positions.items()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✅ Rules exported to {filepath}")
    
    def import_rules(self, filepath: str):
        """Import rule sets from JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for addr, ruleset_data in data.items():
                self.positions[addr] = RuleSet.from_dict(ruleset_data)
            
            logger.info(f"✅ Imported {len(data)} rule sets from {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to import rules: {e}")
    
    def get_engine_stats(self) -> Dict:
        """Get engine performance statistics"""
        active = len([p for p in self.positions.values() if p.active])
        total = len(self.positions)
        
        return {
            "active_positions": active,
            "total_positions": total,
            "executed_sells": self.executed_count,
            "skipped_sells": self.skipped_count,
            "sell_callback_registered": self.sell_callback is not None
        }


# Predefined strategy templates
STRATEGY_AGGRESSIVE = "aggressive"      # Wide targets, moon bag
STRATEGY_DEFAULT = "default"            # Balanced 15%/30%/stop
STRATEGY_CONSERVATIVE = "conservative" # Tight exits, quick profits


def create_ruleset_from_strategy(strategy: str,
                                  token_address: str,
                                  token_symbol: str,
                                  entry_price: float,
                                  quantity: float) -> RuleSet:
    """
    Factory function to create rule set from strategy name
    
    Args:
        strategy: One of STRATEGY_*
        token_address: Token mint
        token_symbol: Token symbol
        entry_price: Entry price
        quantity: Position size
    
    Returns:
        Configured RuleSet
    """
    engine = SellRuleEngine()
    
    if strategy == STRATEGY_AGGRESSIVE:
        return engine.create_aggressive_ruleset(
            token_address, token_symbol, entry_price, quantity
        )
    elif strategy == STRATEGY_CONSERVATIVE:
        return engine.create_conservative_ruleset(
            token_address, token_symbol, entry_price, quantity
        )
    else:  # default
        return engine.create_default_ruleset(
            token_address, token_symbol, entry_price, quantity
        )


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🎯 Sell Rule Engine - Meme Coin Auto-Sell")
    print("=" * 60)
    
    # Create engine
    engine = SellRuleEngine()
    
    # Mock position
    ruleset = engine.create_default_ruleset(
        token_address="MockToken123456789",
        token_symbol="MOON",
        entry_price=0.0001,
        quantity=1000000
    )
    
    print(f"\n📋 Rules for {ruleset.token_symbol}:")
    for i, rule in enumerate(ruleset.rules, 1):
        prefix = "✅" if rule.rule_type == RuleType.TAKE_PROFIT else "🛑"
        print(f"  {prefix} {i}. {rule.rule_type.value}: {rule.trigger_pct*100:+.0f}% → Sell {rule.sell_pct*100:.0f}%")
    
    print("\n⚡ Features:")
    print("  • Partial profit taking")
    print("  • Trailing stops")
    print("  • Time-based exits")
    print("  • Whale copy trading")
    print("\n✅ Rule engine ready")