#!/usr/bin/env python3
"""
V54 Scanner Bridge - Integration with Alpha Hunter v5.4

Connects Photon auto-sell system with v54 scanner signals:
- Receive Grade A+ token alerts
- Auto-setup profit targets/stop losses
- Grade-based position sizing
- Survivor tracking integration

Data Flow:
    v54 Scanner -> Grade A+ Token -> Bridge -> Photon Setup -> Auto-Monitor
"""
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class V54ScannerGrade:
    """Grade thresholds from v54 scanner"""
    A_PLUS = "A+"      # 10-12 criteria passed
    A = "A"            # 8-9 criteria passed
    B_PLUS = "B+"      # 6-7 criteria passed
    B = "B"            # 5 criteria passed
    C = "C"            # <5 criteria passed
    FAIL = "FAIL"      # Critical safety failures


class V54Bridge:
    """
    Bridge between v54 Alpha Hunter and Photon Trading System
    
    Responsibilities:
    1. Receive scanner alerts (Grade A+)
    2. Validate token for trading
    3. Calculate position size based on grade
    4. Setup sell rules via rule engine
    5. Initiate position tracking
    
    Integration Points:
    - v5.4 Scanner output (DexScreener, RugCheck, Helius)
    - Sell Rule Engine (profit/stop rules)
    - Position Manager (tracking)
    - Photon Client (execution)
    """
    
    def __init__(self, 
                 rule_engine=None,
                 position_manager=None,
                 photon_client=None):
        """
        Initialize V54 Bridge
        
        Args:
            rule_engine: SellRuleEngine instance
            position_manager: PositionManager instance  
            photon_client: PhotonAPIClient instance
        """
        self.rule_engine = rule_engine
        self.position_manager = position_manager
        self.photon_client = photon_client
        
        # Grade to strategy mapping
        self.grade_strategies = {
            V54ScannerGrade.A_PLUS: "default",      # Aggressive momentum
            V54ScannerGrade.A: "default",             # Standard setup
            V54ScannerGrade.B_PLUS: "conservative", # Tight stops
            V54ScannerGrade.B: "conservative",       # Very tight
            V54ScannerGrade.C: None,                # Don't trade
            V54ScannerGrade.FAIL: None               # Block
        }
        
        # Grade to confidence multiplier
        self.grade_confidence = {
            V54ScannerGrade.A_PLUS: 1.0,  # Full size
            V54ScannerGrade.A: 0.8,       # 80% size
            V54ScannerGrade.B_PLUS: 0.5,  # 50% size
            V54ScannerGrade.B: 0.3,       # 30% size
            V54ScannerGrade.C: 0.0,       # No trade
            V54ScannerGrade.FAIL: 0.0
        }
        
        # Statistics
        self.tokens_received = 0
        self.tokens_approved = 0
        self.tokens_rejected = 0
        self.rejection_reasons = {}
        
    def process_scanner_signal(self, signal: Dict) -> Optional[Dict]:
        """
        Process a v54 scanner signal and decide action
        
        Expected signal format:
        {
            "ca": "token_mint_address",
            "name": "Token Name",
            "symbol": "TKN",
            "grade": "A+",
            "score": 10,
            "price": 0.0001,
            "mcap": 50000,
            "liquidity": 20000,
            "age_hours": 0.5,
            "holders": 150,
            "volume_24h": 5000
        }
        
        Args:
            signal: Scanner output dictionary
        
        Returns:
            Action dict or None if rejected
        """
        self.tokens_received += 1
        
        ca = signal.get("ca", "")
        name = signal.get("name", "Unknown")
        symbol = signal.get("symbol", "???")
        grade = signal.get("grade", "")
        score = signal.get("score", 0)
        price = signal.get("price", 0)
        
        logger.info(f"\n🎯 Scanner Signal: {name} ({symbol})")
        logger.info(f"   Grade: {grade} | Score: {score}/12 | Price: ${price:.6f}")
        
        # Validate basics
        validation = self._validate_signal(signal)
        if not validation["valid"]:
            self.tokens_rejected += 1
            reason = validation["reason"]
            self.rejection_reasons[reason] = self.rejection_reasons.get(reason, 0) + 1
            logger.warning(f"❌ Rejected: {reason}")
            return None
        
        # Check liquidity
        liq = signal.get("liquidity", 0)
        if liq < 15000:
            self.tokens_rejected += 1
            self.rejection_reasons["low_liquidity"] = self.rejection_reasons.get("low_liquidity", 0) + 1
            logger.warning(f"❌ Rejected: Low liquidity (${liq:,.0f} < $15k)")
            return None
        
        # Check age (avoid brand new tokens for live trading)
        age_hours = signal.get("age_hours", 0)
        if age_hours < 0.25:  # Less than 15 minutes
            logger.warning(f"⚠️ Very new token ({age_hours:.2f}h), proceed with caution")
        
        # Get strategy for this grade
        strategy = self.grade_strategies.get(grade)
        if strategy is None:
            self.tokens_rejected += 1
            self.rejection_reasons["low_grade"] = self.rejection_reasons.get("low_grade", 0) + 1
            logger.warning(f"❌ Rejected: Grade {grade} below threshold")
            return None
        
        # Calculate position size
        confidence = self.grade_confidence.get(grade, 0)
        position_size = self._calculate_position_size(signal, confidence)
        
        if position_size["quantity"] <= 0:
            self.tokens_rejected += 1
            logger.warning(f"❌ Rejected: Position size too small")
            return None
        
        self.tokens_approved += 1
        
        # Build action
        action = {
            "action": "OPEN_POSITION",
            "token_address": ca,
            "token_symbol": symbol,
            "token_name": name,
            "grade": grade,
            "score": score,
            "entry_price": price,
            "quantity": position_size["quantity"],
            "position_value_usd": position_size["value_usd"],
            "strategy": strategy,
            "stop_loss_pct": position_size["stop_loss"],
            "take_profit_1_pct": position_size["tp1"],
            "take_profit_2_pct": position_size["tp2"],
            "time_limit_hours": 4,
            "reason": f"Grade {grade} signal with {score}/12 criteria"
        }
        
        logger.info(f"✅ APPROVED: {symbol}")
        logger.info(f"   Strategy: {strategy} | Confidence: {confidence*100:.0f}%")
        logger.info(f"   Size: ${position_size['value_usd']:.2f}")
        logger.info(f"   SL: -{position_size['stop_loss']*100:.0f}% | TP1: +{position_size['tp1']*100:.0f}%")
        
        return action
    
    def _validate_signal(self, signal: Dict) -> Dict:
        """
        Validate scanner signal has required fields
        
        Returns:
            {"valid": bool, "reason": str or None}
        """
        required = ["ca", "name", "symbol", "grade", "score", "price", "liquidity"]
        
        for field in required:
            if field not in signal or signal[field] is None:
                return {"valid": False, "reason": f"missing_{field}"}
        
        # Validate CA format (Solana base58)
        ca = signal.get("ca", "")
        if len(ca) < 32 or len(ca) > 44:
            return {"valid": False, "reason": "invalid_ca_format"}
        
        # Validate price > 0
        if signal.get("price", 0) <= 0:
            return {"valid": False, "reason": "invalid_price"}
        
        return {"valid": True, "reason": None}
    
    def _calculate_position_size(self, signal: Dict, confidence: float) -> Dict:
        """
        Calculate position size based on grade and signal strength
        
        Default sizing:
        - Base: 0.02 SOL (~$3-5 at current prices)
        - Grade A+: Full 0.02 SOL
        - Grade A: 0.016 SOL
        - Grade B+: 0.01 SOL
        - Grade B: 0.006 SOL
        
        Args:
            signal: Scanner signal
            confidence: Grade confidence multiplier
        
        Returns:
            Position sizing dict
        """
        # Base size in SOL
        base_sol = 0.02
        sol_size = base_sol * confidence
        
        # Get current SOL price (would fetch in production)
        sol_price = 140.0  # Approximate
        usd_size = sol_size * sol_price
        
        # Calculate token quantity
        token_price = signal.get("price", 0)
        quantity = usd_size / token_price if token_price > 0 else 0
        
        # Adjust targets based on volatility/grade
        grade = signal.get("grade", "")
        
        if grade == V54ScannerGrade.A_PLUS:
            # Wider targets for high confidence
            stop_loss = 0.07
            tp1 = 0.15
            tp2 = 0.30
        elif grade == V54ScannerGrade.A:
            # Standard targets
            stop_loss = 0.07
            tp1 = 0.15
            tp2 = 0.30
        else:
            # Tighter for lower grades
            stop_loss = 0.05
            tp1 = 0.10
            tp2 = 0.20
        
        return {
            "sol": sol_size,
            "value_usd": usd_size,
            "quantity": quantity,
            "token_price": token_price,
            "stop_loss": stop_loss,
            "tp1": tp1,
            "tp2": tp2
        }
    
    def execute_action(self, action: Dict) -> Dict:
        """
        Execute an approved action through the trading system
        
        Args:
            action: Action dict from process_scanner_signal
        
        Returns:
            Execution result
        """
        result = {
            "success": False,
            "position_id": None,
            "orders_created": [],
            "errors": []
        }
        
        try:
            token = action["token_address"]
            symbol = action["token_symbol"]
            
            # 1. Open position in manager
            if self.position_manager:
                position = self.position_manager.open_position(
                    token_address=token,
                    token_symbol=symbol,
                    entry_price=action["entry_price"],
                    quantity=action["quantity"],
                    scanner_grade=action["grade"],
                    scanner_score=action["score"],
                    time_limit_hours=action["time_limit_hours"]
                )
                result["position_id"] = position.position_id
            
            # 2. Create sell rules via rule engine
            if self.rule_engine:
                from ..core.sell_rule_engine import RuleSet
                
                ruleset = self.rule_engine.create_default_ruleset(
                    token_address=token,
                    token_symbol=symbol,
                    entry_price=action["entry_price"],
                    quantity=action["quantity"]
                )
                
                # Override defaults with action values
                for rule in ruleset.rules:
                    if rule.rule_type.value == "take_profit":
                        if not any(r.executed for r in ruleset.rules if r.rule_type.value == "take_profit"):
                            rule.trigger_pct = action["take_profit_1_pct"]
                    elif rule.rule_type.value == "stop_loss":
                        rule.trigger_pct = -action["stop_loss_pct"]
                
                result["orders_created"].append(f"ruleset_{token[:8]}")
            
            # 3. Setup Photon orders if wallet connected
            if self.photon_client and self.photon_client.is_connected():
                stop_order = self.photon_client.create_stop_loss_order(
                    token_address=token,
                    token_symbol=symbol,
                    quantity=action["quantity"],
                    stop_loss_pct=action["stop_loss_pct"],
                    entry_price=action["entry_price"]
                )
                if stop_order:
                    result["orders_created"].append(stop_order.order_id)
                
                tp_order = self.photon_client.create_take_profit_order(
                    token_address=token,
                    token_symbol=symbol,
                    quantity=action["quantity"] * 0.5,  # 50%
                    profit_target_pct=action["take_profit_1_pct"],
                    entry_price=action["entry_price"]
                )
                if tp_order:
                    result["orders_created"].append(tp_order.order_id)
            
            result["success"] = True
            logger.info(f"✅ Successfully executed action for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute action: {e}")
            result["errors"].append(str(e))
        
        return result
    
    def check_survivors(self) -> List[Dict]:
        """
        Check for tokens that survived >24h maintaining grade
        
        Returns:
            List of survivor tokens with stats
        """
        survivors = []
        
        # This would integrate with TokenTracker from v54
        # Check tracked_tokens.json for 24h survivors
        
        return survivors
    
    def simulate_scanner_output(self, 
                               ca: str,
                               name: str,
                               symbol: str,
                               grade: str = "A+",
                               score: int = 10) -> Dict:
        """
        Create mock scanner output for testing
        
        Args:
            ca: Token mint
            name: Full name
            symbol: Symbol
            grade: Scanner grade
            score: Criteria score
        
        Returns:
            Mock signal dict
        """
        return {
            "ca": ca,
            "name": name,
            "symbol": symbol,
            "grade": grade,
            "score": score,
            "price": 0.0001 + (0.00001 * hash(ca) % 100),  # Random-ish price
            "mcap": 50000 + (hash(ca) % 100000),
            "liquidity": 20000 + (hash(ca) % 30000),
            "age_hours": 0.5 + (hash(ca) % 24) / 10,
            "holders": 100 + (hash(ca) % 400),
            "volume_24h": 5000 + (hash(ca) % 15000)
        }
    
    def get_bridge_stats(self) -> Dict:
        """Get bridge statistics"""
        approval_rate = (self.tokens_approved / self.tokens_received * 100) if self.tokens_received > 0 else 0
        
        return {
            "tokens_received": self.tokens_received,
            "tokens_approved": self.tokens_approved,
            "tokens_rejected": self.tokens_rejected,
            "approval_rate_pct": approval_rate,
            "rejection_reasons": self.rejection_reasons,
            "integrations": {
                "rule_engine": self.rule_engine is not None,
                "position_manager": self.position_manager is not None,
                "photon_client": self.photon_client is not None
            }
        }


# Survivor tracking helper
class SurvivorTracker:
    """
    Track tokens that survive multiple days at Grade A
    """
    
    SURVIVOR_THRESHOLDS = [6, 12, 24, 48, 72]  # Hours
    
    def __init__(self, tracker_file: str = "/home/skux/.openclaw/workspace/tracked_tokens.json"):
        self.tracker_file = tracker_file
    
    def load_tracking(self) -> Dict:
        """Load survivor tracking data"""
        try:
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def get_24h_survivors(self) -> List[Dict]:
        """Get tokens that maintained A+ for 24h+"""
        tracked = self.load_tracking()
        survivors = []
        
        for ca, data in tracked.items():
            checkpoints = data.get("checkpoints", {})
            if "24" in checkpoints and data.get("current_grade", "").startswith("A"):
                survivors.append({
                    "ca": ca,
                    "name": data["data"].get("name", "?"),
                    "age_hours": data.get("age_hours", 0),
                    "mcap_change": data["current_mcap"] / max(data["data"].get("mcap", 1), 1) - 1
                })
        
        return sorted(survivors, key=lambda x: x.get("mcap_change", 0), reverse=True)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🌉 V54 Scanner Bridge")
    print("=" * 60)
    print("\nConnecting v54 Alpha Hunter -> Photon Integration")
    
    bridge = V54Bridge()
    
    # Mock scanner signal
    test_signal = bridge.simulate_scanner_output(
        ca="MockToken12345678900000000000",
        name="Moon Shot Token",
        symbol="MOON",
        grade="A+",
        score=10
    )
    
    print("\n📥 Scanner Signal Received:")
    print(f"   Token: {test_signal['name']} ({test_signal['symbol']})")
    print(f"   Grade: {test_signal['grade']} | Score: {test_signal['score']}/12")
    print(f"   Price: ${test_signal['price']:.6f}")
    print(f"   Liquidity: ${test_signal['liquidity']:,.0f}")
    
    print("\n🔄 Processing...")
    action = bridge.process_scanner_signal(test_signal)
    
    if action:
        print(f"\n✅ Action Generated:")
        print(f"   Strategy: {action['strategy']}")
        print(f"   Position Size: ${action['position_value_usd']:.2f}")
        print(f"   SL: -{action['stop_loss_pct']*100:.0f}% | TP1: +{action['take_profit_1_pct']*100:.0f}%")
    else:
        print("\n❌ Signal rejected")
    
    print("\n📊 Statistics:")
    stats = bridge.get_bridge_stats()
    print(f"   Approval Rate: {stats['approval_rate_pct']:.1f}%")
    print(f"   Approved/Rejected: {stats['tokens_approved']}/{stats['tokens_rejected']}")
    
    print("\n✅ V54 Bridge ready")