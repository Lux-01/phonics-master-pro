#!/usr/bin/env python3
"""
🎯 Photon Bridge Sell Rule Engine
Manages automated sell rules for LuxTrader positions

Features:
- Profit target management (+15%, +30%)
- Stop loss execution (-7%)
- Time-based exits (4h)
- Breakeven stop adjustment
- Dynamic rule evaluation
- Integration with Photon client
"""
import json
import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of sell rules"""
    TAKE_PROFIT_1 = "take_profit_1"     # +15%, sell 50%
    TAKE_PROFIT_2 = "take_profit_2"     # +30%, sell remaining
    STOP_LOSS = "stop_loss"             # -7%, sell 100%
    TIME_STOP = "time_stop"             # 4 hours, sell 100%
    EMERGENCY_RUG = "emergency_rug"     # Immediate exit
    MANUAL = "manual"                   # User-initiated


class RuleStatus(Enum):
    """Rule execution status"""
    PENDING = "pending"         # Active, waiting for trigger
    TRIGGERED = "triggered"     # Condition met, executing
    EXECUTED = "executed"       # Successfully executed
    FAILED = "failed"         # Execution failed
    CANCELLED = "cancelled"     # Rule cancelled
    DISABLED = "disabled"       # Rule disabled


@dataclass
class SellRule:
    """
    Individual sell rule configuration
    
    Attributes:
        rule_id: Unique identifier
        rule_type: Type of rule
        name: Human-readable name
        trigger_pct: Price change % to trigger (-0.07 = -7%)
        trigger_hours: Hours for time-based triggers
        sell_pct: % of position to sell (0.5 = 50%)
        requires_tier_1: Requires TP1 to execute first
        move_stop_to_breakeven: After execution, move SL to entry
        order_type: market/limit
        slippage_bps: Slippage tolerance in basis points
        status: Current rule status
        enabled: Whether rule is active
        created_at: Creation timestamp
        triggered_at: When rule was triggered
        executed_at: When rule was executed
        trigger_price: Price at which rule triggers
        execution_price: Actual execution price
        notes: Additional notes
    """
    rule_id: str
    rule_type: str
    name: str
    trigger_pct: float = 0.0
    trigger_hours: Optional[int] = None
    sell_pct: float = 1.0
    requires_tier_1: bool = False
    move_stop_to_breakeven: bool = False
    order_type: str = "market"
    slippage_bps: int = 100
    status: str = "pending"
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    triggered_at: Optional[str] = None
    executed_at: Optional[str] = None
    trigger_price: float = 0.0
    execution_price: float = 0.0
    notes: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SellRule':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class PositionRules:
    """All sell rules for a specific position"""
    position_id: str
    token_address: str
    token_symbol: str
    entry_price: float
    entry_time: str
    current_price: float = 0.0
    highest_price: float = 0.0
    current_pnl_pct: float = 0.0
    rules: Dict[str, SellRule] = field(default_factory=dict)
    breakeven_stop_active: bool = False
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "position_id": self.position_id,
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "current_price": self.current_price,
            "highest_price": self.highest_price,
            "current_pnl_pct": self.current_pnl_pct,
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
            "breakeven_stop_active": self.breakeven_stop_active,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PositionRules':
        """Create from dictionary"""
        position_rules = cls(
            position_id=data["position_id"],
            token_address=data["token_address"],
            token_symbol=data["token_symbol"],
            entry_price=data["entry_price"],
            entry_time=data["entry_time"],
            current_price=data.get("current_price", 0.0),
            highest_price=data.get("highest_price", 0.0),
            current_pnl_pct=data.get("current_pnl_pct", 0.0),
            breakeven_stop_active=data.get("breakeven_stop_active", False),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat())
        )
        position_rules.rules = {
            k: SellRule.from_dict(v) for k, v in data.get("rules", {}).items()
        }
        return position_rules


class SellRuleEngine:
    """
    Core engine for managing and evaluating sell rules
    
    Responsibilities:
    - Create default rules for new positions
    - Evaluate rules against current prices
    - Handle rule dependencies (e.g., TP2 requires TP1)
    - Update breakeven stops
    - Trigger executions
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize rule engine
        
        Args:
            config_file: Path to sell rules JSON config
        """
        self.config_file = config_file or Path(__file__).parent.parent / "config" / "photon_sell_rules.json"
        self.config = self._load_config()
        self.positions: Dict[str, PositionRules] = {}
        self.callbacks: List[Callable] = []
        
        logger.info(f"🎯 SellRuleEngine initialized with config: {self.config_file}")
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Could not load config, using defaults: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "default_rules": {
                "profit_target_1": {
                    "trigger_pct": 0.15,
                    "sell_pct": 0.50,
                    "move_stop_to_breakeven": True
                },
                "profit_target_2": {
                    "trigger_pct": 0.30,
                    "sell_pct": 1.0,
                    "requires_tier_1_executed": True
                },
                "stop_loss": {
                    "trigger_pct": -0.07,
                    "sell_pct": 1.0
                },
                "time_stop": {
                    "trigger_hours": 4,
                    "sell_pct": 1.0
                }
            }
        }
    
    def create_rules_for_position(self, 
                                  position_id: str,
                                  token_address: str,
                                  token_symbol: str,
                                  entry_price: float,
                                  stage: int = 9) -> PositionRules:
        """
        Create default sell rules for a new position
        
        Args:
            position_id: Unique position identifier
            token_address: Token CA
            token_symbol: Token symbol
            entry_price: Entry price in SOL
            stage: Trading stage
            
        Returns:
            PositionRules with default rules configured
        """
        entry_time = datetime.utcnow().isoformat()
        
        position_rules = PositionRules(
            position_id=position_id,
            token_address=token_address,
            token_symbol=token_symbol,
            entry_price=entry_price,
            entry_time=entry_time
        )
        
        # Get default rule config
        defaults = self.config.get("default_rules", {})
        
        # Rule 1: Take Profit 1 (+15%, sell 50%)
        tp1_config = defaults.get("profit_target_1", {})
        position_rules.rules["take_profit_1"] = SellRule(
            rule_id=f"{position_id}_tp1",
            rule_type=RuleType.TAKE_PROFIT_1.value,
            name="First Profit Target",
            trigger_pct=tp1_config.get("trigger_pct", 0.15),
            sell_pct=tp1_config.get("sell_pct", 0.50),
            move_stop_to_breakeven=tp1_config.get("move_stop_to_breakeven", True),
            trigger_price=entry_price * (1 + tp1_config.get("trigger_pct", 0.15)),
            notes="Sell 50% at +15%, move stop to breakeven"
        )
        
        # Rule 2: Take Profit 2 (+30%, sell remaining)
        tp2_config = defaults.get("profit_target_2", {})
        position_rules.rules["take_profit_2"] = SellRule(
            rule_id=f"{position_id}_tp2",
            rule_type=RuleType.TAKE_PROFIT_2.value,
            name="Second Profit Target",
            trigger_pct=tp2_config.get("trigger_pct", 0.30),
            sell_pct=tp2_config.get("sell_pct", 1.0),
            requires_tier_1=tp2_config.get("requires_tier_1_executed", True),
            trigger_price=entry_price * (1 + tp2_config.get("trigger_pct", 0.30)),
            notes="Sell remaining at +30%, requires TP1 executed"
        )
        
        # Rule 3: Stop Loss (-7%, sell 100%)
        sl_config = defaults.get("stop_loss", {})
        position_rules.rules["stop_loss"] = SellRule(
            rule_id=f"{position_id}_sl",
            rule_type=RuleType.STOP_LOSS.value,
            name="Stop Loss",
            trigger_pct=sl_config.get("trigger_pct", -0.07),
            sell_pct=sl_config.get("sell_pct", 1.0),
            trigger_price=entry_price * (1 + sl_config.get("trigger_pct", -0.07)),
            notes="Hard stop at -7%"
        )
        
        # Rule 4: Time Stop (4 hours)
        ts_config = defaults.get("time_stop", {})
        position_rules.rules["time_stop"] = SellRule(
            rule_id=f"{position_id}_ts",
            rule_type=RuleType.TIME_STOP.value,
            name="Time-Based Exit",
            trigger_hours=ts_config.get("trigger_hours", 4),
            sell_pct=ts_config.get("sell_pct", 1.0),
            notes="Exit after 4 hours max hold time"
        )
        
        # Store position rules
        self.positions[position_id] = position_rules
        
        logger.info(f"✅ Created rules for {token_symbol} at {entry_price:.6f} SOL")
        logger.info(f"   TP1: +15% at {position_rules.rules['take_profit_1'].trigger_price:.6f}")
        logger.info(f"   TP2: +30% at {position_rules.rules['take_profit_2'].trigger_price:.6f}")
        logger.info(f"   SL: -7% at {position_rules.rules['stop_loss'].trigger_price:.6f}")
        
        return position_rules
    
    def update_price(self, position_id: str, current_price: float) -> List[SellRule]:
        """
        Update position with new price and evaluate rules
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            
        Returns:
            List of triggered rules
        """
        if position_id not in self.positions:
            logger.warning(f"⚠️ Position {position_id} not found")
            return []
        
        position = self.positions[position_id]
        
        # Update price tracking
        position.current_price = current_price
        position.highest_price = max(position.highest_price, current_price)
        position.current_pnl_pct = (current_price - position.entry_price) / position.entry_price
        position.last_updated = datetime.utcnow().isoformat()
        
        # Evaluate rules
        triggered = self._evaluate_rules(position)
        
        return triggered
    
    def _evaluate_rules(self, position: PositionRules) -> List[SellRule]:
        """
        Evaluate all rules for a position
        
        Args:
            position: PositionRules to evaluate
            
        Returns:
            List of triggered rules
        """
        triggered = []
        now = datetime.utcnow()
        
        for rule_name, rule in position.rules.items():
            # Skip non-active rules
            if rule.status != RuleStatus.PENDING.value or not rule.enabled:
                continue
            
            # Check dependencies
            if rule.requires_tier_1:
                tp1 = position.rules.get("take_profit_1")
                if not tp1 or tp1.status != RuleStatus.EXECUTED.value:
                    continue
            
            # Check rule conditions
            is_triggered = False
            
            if rule.rule_type == RuleType.TAKE_PROFIT_1.value:
                # Price >= trigger price
                if position.current_price >= rule.trigger_price:
                    is_triggered = True
            
            elif rule.rule_type == RuleType.TAKE_PROFIT_2.value:
                # Price >= trigger price
                if position.current_price >= rule.trigger_price:
                    is_triggered = True
            
            elif rule.rule_type == RuleType.STOP_LOSS.value:
                # Check if breakeven stop is active
                if position.breakeven_stop_active:
                    if position.current_price <= position.entry_price:
                        is_triggered = True
                else:
                    # Normal stop loss
                    if position.current_price <= rule.trigger_price:
                        is_triggered = True
            
            elif rule.rule_type == RuleType.TIME_STOP.value:
                # Check time elapsed
                entry_time = datetime.fromisoformat(position.entry_time)
                elapsed_hours = (now - entry_time).total_seconds() / 3600
                if elapsed_hours >= rule.trigger_hours:
                    is_triggered = True
            
            if is_triggered:
                rule.status = RuleStatus.TRIGGERED.value
                rule.triggered_at = now.isoformat()
                triggered.append(rule)
                
                logger.info(f"⚡ Rule triggered: {rule.name} for {position.token_symbol}")
                logger.info(f"   Trigger price: {rule.trigger_price:.6f}, Current: {position.current_price:.6f}")
        
        return triggered
    
    def execute_rule(self, position_id: str, rule_name: str, 
                    execution_price: float, tx_signature: str = None) -> bool:
        """
        Mark a rule as executed
        
        Args:
            position_id: Position identifier
            rule_name: Name of rule (e.g., "take_profit_1")
            execution_price: Actual execution price
            tx_signature: Transaction signature
            
        Returns:
            True if successful
        """
        if position_id not in self.positions:
            logger.warning(f"⚠️ Position {position_id} not found")
            return False
        
        position = self.positions[position_id]
        
        if rule_name not in position.rules:
            logger.warning(f"⚠️ Rule {rule_name} not found")
            return False
        
        rule = position.rules[rule_name]
        rule.status = RuleStatus.EXECUTED.value
        rule.execution_price = execution_price
        rule.executed_at = datetime.utcnow().isoformat()
        
        # Handle breakeven stop
        if rule.move_stop_to_breakeven:
            position.breakeven_stop_active = True
            # Update stop loss trigger price to breakeven
            if "stop_loss" in position.rules:
                sl_rule = position.rules["stop_loss"]
                sl_rule.trigger_price = position.entry_price
                sl_rule.notes = "Moved to breakeven after TP1"
                logger.info(f"🛡️ Stop loss moved to breakeven: {position.entry_price:.6f}")
        
        logger.info(f"✅ Rule executed: {rule.name} at {execution_price:.6f}")
        
        # Call callbacks
        for callback in self.callbacks:
            try:
                callback(position, rule, execution_price)
            except Exception as e:
                logger.error(f"❌ Callback error: {e}")
        
        return True
    
    def mark_rule_failed(self, position_id: str, rule_name: str, error: str) -> bool:
        """Mark a rule as failed"""
        if position_id not in self.positions:
            return False
        
        position = self.positions[position_id]
        if rule_name not in position.rules:
            return False
        
        position.rules[rule_name].status = RuleStatus.FAILED.value
        logger.error(f"❌ Rule failed: {rule_name} - {error}")
        
        return True
    
    def register_callback(self, callback: Callable):
        """
        Register a callback for rule executions
        
        Args:
            callback: Function(position_rules, rule, execution_price)
        """
        self.callbacks.append(callback)
    
    def get_position_rules(self, position_id: str) -> Optional[PositionRules]:
        """Get rules for a position"""
        return self.positions.get(position_id)
    
    def get_all_positions(self) -> Dict[str, PositionRules]:
        """Get all tracked positions"""
        return self.positions.copy()
    
    def remove_position(self, position_id: str):
        """Remove a position (when fully closed)"""
        if position_id in self.positions:
            del self.positions[position_id]
            logger.info(f"🗑️ Removed position: {position_id}")
    
    def get_triggered_rules(self) -> List[Tuple[str, SellRule]]:
        """Get all currently triggered rules across all positions"""
        triggered = []
        for position_id, position in self.positions.items():
            for rule in position.rules.values():
                if rule.status == RuleStatus.TRIGGERED.value:
                    triggered.append((position_id, rule))
        return triggered
    
    def save_state(self, filepath: str = None):
        """Save current state to file"""
        filepath = filepath or "/tmp/photon_rule_engine_state.json"
        state = {
            "saved_at": datetime.utcnow().isoformat(),
            "positions": {k: v.to_dict() for k, v in self.positions.items()}
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"💾 Saved state to {filepath}")
    
    def load_state(self, filepath: str):
        """Load state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.positions = {
                k: PositionRules.from_dict(v) 
                for k, v in state.get("positions", {}).items()
            }
            logger.info(f"📂 Loaded state from {filepath}: {len(self.positions)} positions")
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")


if __name__ == "__main__":
    # Demo/test
    engine = SellRuleEngine()
    
    # Create rules for a test position
    position = engine.create_rules_for_position(
        position_id="test_001",
        token_address="GiFoBEGnHGXmJdpaNqjMHBkYP5QcyPYqutwREiec3RBi",
        token_symbol="TEST",
        entry_price=0.01
    )
    
    # Simulate price updates
    test_prices = [0.0105, 0.011, 0.0115, 0.012, 0.0113, 0.009]
    
    for price in test_prices:
        print(f"\n📈 Price: {price:.6f}")
        triggered = engine.update_price("test_001", price)
        
        if triggered:
            for rule in triggered:
                print(f"   ⚡ Triggered: {rule.name}")
                # Simulate execution
                engine.execute_rule("test_001", rule.rule_id.split("_")[-1], price, "tx_123")
    
    print("\n✅ Rule engine test complete")