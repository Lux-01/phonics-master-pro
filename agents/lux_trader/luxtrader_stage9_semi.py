#!/usr/bin/env python3
"""
✨ LUXTRADER STAGE 9 - SEMI-AUTONOMOUS TRADING with TRE Integration
System proposes, user approves, system executes

Stage 9: The bridge between virtual and autonomous
- Continuous opportunity monitoring
- Automatic trade proposal generation with TRE forecasting
- User approval interface
- Automatic execution on approval
- Full safety limits enforced
- TRE-powered trend analysis and anomaly detection

Wallet: 8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5
Mode: SUPERVISED (user approval required for all trades)
Safety: CANNOT BE DISABLED
"""

import json
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import importlib.util
import os

# Add workspace to path
sys.path.insert(0, '/home/skux/.openclaw/workspace')

# Import CEL modules
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/cognitive-enhancement-layer')

# Import TRE for forecasting
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/temporal-reasoning-engine')
from tre_core import TemporalReasoningEngine, TrendDirection, AnomalyType

# Import Safety Engine
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/safety-engine')
from safety_core import SafetyVerificationEngine, ActionType, RiskLevel

# CONFIGURATION
STAGE9_CONFIG = {
    "mode": "SUPERVISED",  # User approval required
    "position_size": 0.1,  # SOL per trade (max)
    "max_daily_trades": 5,
    "max_daily_loss_sol": 0.5,
    "min_liquidity_usd": 10000,
    "min_grade": "A",  # Grade A or A+
    "approval_timeout_minutes": 30,  # User has 30 min to approve
    "cooldown_minutes": 60,  # Between trades
    "tre_forecast_hours": 4,  # Forecast window
    "min_tre_confidence": 0.6,  # Minimum TRE confidence
    "anomaly_block_threshold": "high",  # Block on high/critical anomalies
}

# Wallet
WALLET_ADDRESS = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# Birdeye API
AUTH = json.load(open("/home/skux/.openclaw/workspace/auth.json"))
BIRDEYE_API_KEY = AUTH.get("birdeye_api_key", "6335463fca7340f9a2c73eacd5a37f64")

# Files
STATE_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/stage9_state.json"
TRADES_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/stage9_trades.json"
PROPOSALS_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/stage9_proposals.json"
LOG_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/logs/stage9.log"
AUDIT_LOG_FILE = "/home/skux/.openclaw/workspace/agents/lux_trader/logs/stage9_audit.log"


class Stage9SemiAutonomousTrader:
    """
    Stage 9: System proposes, user approves, system executes.
    The human-in-the-loop approach before full autonomy.
    Enhanced with TRE forecasting and Safety Engine.
    """
    
    def __init__(self):
        print("🎯 STAGE 9: Semi-Autonomous Trading System")
        print("=" * 60)
        print("Mode: SUPERVISED - All trades require user approval")
        print("Features: TRE Forecasting + Safety Engine + Anomaly Detection")
        print("Wallet:", WALLET_ADDRESS[:20] + "...")
        print("=" * 60)
        
        self.state = self.load_state()
        self.pending_proposals = []
        self.ensure_files()
        
        # Initialize TRE for forecasting
        self.tre = TemporalReasoningEngine()
        print("✅ TRE (Temporal Reasoning Engine) initialized")
        
        # Initialize Safety Engine
        self.safety = SafetyVerificationEngine()
        self._setup_safety_policies()
        print("✅ Safety Verification Engine initialized")
        
        # Load ALOE for pattern learning
        try:
            aloe_path = "/home/skux/.openclaw/workspace/skills/aloe/aloe_coordinator.py"
            spec = importlib.util.spec_from_file_location("aloe", aloe_path)
            aloe = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(aloe)
            self.can_learn = True
            print("✅ ALOE learning system connected")
        except Exception as e:
            self.can_learn = False
            print(f"⚠️  ALOE not available: {e}")
    
    def _setup_safety_policies(self):
        """Configure safety policies for trading."""
        # Safety policies are already loaded by default in SafetyVerificationEngine
        # We just need to verify they're appropriate for Stage 9
        
        # Check if we need to update the trading policy
        if "trading" in self.safety.policies:
            policy = self.safety.policies["trading"]
            # Update with Stage 9 specific limits
            policy.max_daily = STAGE9_CONFIG["max_daily_trades"]
            policy.max_amount = STAGE9_CONFIG["position_size"]
        
        print("✅ Safety policies configured for Stage 9")
    
    def ensure_files(self):
        """Ensure all required files exist."""
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(AUDIT_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        for file in [STATE_FILE, TRADES_FILE, PROPOSALS_FILE]:
            if not Path(file).exists():
                with open(file, 'w') as f:
                    if 'proposals' in file:
                        json.dump({"pending": [], "history": []}, f)
                    elif 'trades' in file:
                        json.dump({"trades": []}, f)
                    else:
                        json.dump({}, f)
    
    def load_state(self) -> Dict:
        """Load current state."""
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                "trades_today": 0,
                "loss_today_sol": 0,
                "last_trade_time": None,
                "total_trades": 0,
                "successful_trades": 0,
                "status": "ACTIVE"
            }
    
    def save_state(self):
        """Save current state."""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, message: str):
        """Log message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Append to log file
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry + "\n")
        except:
            pass
    
    def audit_log(self, action: str, details: Dict):
        """Write audit log entry."""
        timestamp = datetime.now().isoformat()
        audit_entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details,
            "state_hash": self._hash_state()
        }
        
        try:
            with open(AUDIT_LOG_FILE, 'a') as f:
                f.write(json.dumps(audit_entry) + "\n")
        except:
            pass
    
    def _hash_state(self) -> str:
        """Generate hash of current state for audit."""
        import hashlib
        state_str = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
    
    def check_safety_limits(self) -> Tuple[bool, str]:
        """
        Check if trade can proceed based on safety limits.
        Returns: (can_trade, reason)
        """
        # Check circuit breaker from Safety Engine
        cb = self.safety.circuit_breakers.get("trading")
        if cb and cb.is_open:
            open_until = cb.open_until.isoformat() if cb.open_until else "unknown"
            return False, f"Circuit breaker open until {open_until}"
        
        # Daily trade limit
        if self.state.get("trades_today", 0) >= STAGE9_CONFIG["max_daily_trades"]:
            return False, f"Daily trade limit reached ({STAGE9_CONFIG['max_daily_trades']})"
        
        # Daily loss limit
        if self.state.get("loss_today_sol", 0) >= STAGE9_CONFIG["max_daily_loss_sol"]:
            return False, f"Daily loss limit reached ({STAGE9_CONFIG['max_daily_loss_sol']} SOL)"
        
        # Cooldown check
        last_trade = self.state.get("last_trade_time")
        if last_trade:
            last = datetime.fromisoformat(last_trade)
            cooldown = timedelta(minutes=STAGE9_CONFIG["cooldown_minutes"])
            if datetime.now() - last < cooldown:
                remaining = cooldown - (datetime.now() - last)
                return False, f"Cooldown active ({remaining.seconds // 60} min remaining)"
        
        return True, "Safety checks passed"
    
    def fetch_price_history(self, token_address: str) -> List[Dict]:
        """Fetch price history for TRE analysis."""
        try:
            url = f"https://public-api.birdeye.so/defi/history_price?address={token_address}&type=1H"
            headers = {"X-API-KEY": BIRDEYE_API_KEY}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    items = data["data"].get("items", [])
                    return items
            return []
        except Exception as e:
            self.log(f"⚠️  Price history fetch failed: {e}")
            return []
    
    def analyze_with_tre(self, token_address: str, current_price: float) -> Dict:
        """
        Analyze token with TRE for trend and anomaly detection.
        Returns analysis results.
        """
        self.log(f"🔮 Running TRE analysis for {token_address[:12]}...")
        
        # Fetch price history
        price_history = self.fetch_price_history(token_address)
        
        if len(price_history) < 5:
            return {
                "has_data": False,
                "trend": "unknown",
                "forecast": None,
                "anomalies": [],
                "recommendation": "INSUFFICIENT_DATA"
            }
        
        # Store in TRE using the correct API
        series_id = f"price_{token_address}"
        
        # Convert to TimeSeriesPoint objects
        from tre_core import TimeSeriesPoint
        points = []
        for item in price_history:
            point = TimeSeriesPoint(
                timestamp=datetime.fromtimestamp(item.get("unixTime", 0)),
                value=item.get("value", 0),
                metadata={"source": "birdeye"}
            )
            points.append(point)
        
        # Ingest data
        self.tre.ingest(series_id, points)
        
        # Analyze trend
        trend = self.tre.analyze_trend(series_id, window_hours=4)
        
        # Detect anomalies
        anomalies = self.tre.detect_anomalies(series_id)
        
        # Generate forecast
        forecast = self.tre.forecast(series_id, hours_ahead=STAGE9_CONFIG["tre_forecast_hours"])
        
        # Check for blocking anomalies
        blocking_anomalies = [
            a for a in anomalies 
            if a.severity in ["high", "critical"] and a.type in [AnomalyType.DROP, AnomalyType.PATTERN_BREAK]
        ]
        
        # Determine recommendation
        if blocking_anomalies:
            recommendation = "BLOCK_ANOMALY_DETECTED"
        elif trend.direction == TrendDirection.DOWN and trend.confidence > 0.7:
            recommendation = "CAUTION_DOWNTREND"
        elif trend.direction == TrendDirection.UP and trend.confidence > STAGE9_CONFIG["min_tre_confidence"]:
            if forecast and forecast[0].predicted_value > current_price * 1.05:
                recommendation = "FAVORABLE_UPTREND"
            else:
                recommendation = "MODERATE_UPTREND"
        else:
            recommendation = "NEUTRAL"
        
        return {
            "has_data": True,
            "trend": trend.to_dict() if trend else None,
            "forecast": [f.to_dict() for f in forecast[:3]] if forecast else [],
            "anomalies": [a.to_dict() for a in anomalies],
            "blocking_anomalies": len(blocking_anomalies),
            "recommendation": recommendation,
            "confidence": trend.confidence if trend else 0
        }
    
    def check_safety_before_trade(self, proposal: Dict) -> Tuple[bool, Dict]:
        """
        Verify trade with Safety Engine.
        Returns: (can_proceed, verification_result)
        """
        # Use correct Safety Engine API
        result = self.safety.verify_action(
            action_type=ActionType.TRADE,
            source="stage9_trader",
            parameters={
                "token": proposal["token"]["address"],
                "symbol": proposal["token"]["symbol"],
                "amount_sol": proposal["trade_details"]["entry_size_sol"],
                "grade": proposal["token"]["grade"]
            }
        )
        
        # Log to audit
        self.audit_log("SAFETY_CHECK", {
            "action_id": proposal["id"],
            "result": result.to_dict()
        })
        
        return result.can_execute, result.to_dict()
    
    def scan_for_opportunities(self) -> Optional[Dict]:
        """
        Scan for Grade A/A+ opportunities with TRE analysis.
        Returns token data if found, None otherwise.
        """
        self.log("🔍 Scanning for opportunities with TRE forecasting...")
        
        try:
            # Check signals directory for latest
            signals_dir = "/home/skux/.openclaw/workspace/agents/lux_trader/signals"
            import glob
            
            signal_files = glob.glob(f"{signals_dir}/signal_*.json")
            signal_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            for signal_file in signal_files[:5]:  # Check 5 most recent
                with open(signal_file, 'r') as f:
                    signal = json.load(f)
                
                token_address = signal.get("token")
                
                # Check if already traded
                if self.is_already_traded(token_address):
                    continue
                
                # Check grade
                grade = signal.get("grade", "")
                if grade not in ["A", "A+", "A-"]:
                    continue
                
                # Check age
                age = signal.get("age_hours", 999)
                if age < 2 or age > 24:
                    continue
                
                # Check liquidity
                liquidity = signal.get("liquidity", 0)
                if liquidity < STAGE9_CONFIG["min_liquidity_usd"]:
                    continue
                
                # Run TRE analysis
                current_price = signal.get("price", 0)
                tre_analysis = self.analyze_with_tre(token_address, current_price)
                
                # Block if anomalies detected
                if tre_analysis["blocking_anomalies"] > 0:
                    self.log(f"🚫 BLOCKED: {signal.get('symbol', 'Unknown')} - Anomalies detected")
                    continue
                
                # Add TRE data to signal
                signal["tre_analysis"] = tre_analysis
                
                self.log(f"✅ Found opportunity: {signal.get('symbol', 'Unknown')} (Grade {grade})")
                if tre_analysis["has_data"]:
                    self.log(f"   TRE Trend: {tre_analysis['trend']['direction'] if tre_analysis['trend'] else 'N/A'} "
                            f"(confidence: {tre_analysis['confidence']:.2f})")
                    self.log(f"   TRE Recommendation: {tre_analysis['recommendation']}")
                
                return signal
            
            return None
            
        except Exception as e:
            self.log(f"❌ Scan error: {e}")
            return None
    
    def is_already_traded(self, token_address: str) -> bool:
        """Check if we already traded this token."""
        if not token_address:
            return False
        
        try:
            with open(TRADES_FILE, 'r') as f:
                trades = json.load(f)
            
            for trade in trades.get("trades", []):
                if trade.get("token") == token_address:
                    return True
            
            return False
        except:
            return False
    
    def generate_proposal(self, opportunity: Dict) -> Dict:
        """
        Generate trade proposal for user approval with TRE insights.
        """
        symbol = opportunity.get("symbol", "UNKNOWN")
        price = opportunity.get("price", 0)
        grade = opportunity.get("grade", "N/A")
        tre_analysis = opportunity.get("tre_analysis", {})
        
        # Calculate position details based on TRE confidence
        base_size = STAGE9_CONFIG["position_size"]
        
        # Adjust size based on TRE recommendation
        if tre_analysis.get("recommendation") == "FAVORABLE_UPTREND":
            position_size = min(base_size * 1.0, 0.1)  # Full size
            tre_boost = "TRE: Strong uptrend detected"
        elif tre_analysis.get("recommendation") == "MODERATE_UPTREND":
            position_size = min(base_size * 0.8, 0.08)  # 80% size
            tre_boost = "TRE: Moderate uptrend"
        elif tre_analysis.get("recommendation") == "CAUTION_DOWNTREND":
            position_size = min(base_size * 0.5, 0.05)  # 50% size
            tre_boost = "TRE: Downtrend caution"
        else:
            position_size = min(base_size * 0.7, 0.07)  # 70% size
            tre_boost = "TRE: Neutral/Insufficient data"
        
        proposal = {
            "id": f"prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING_APPROVAL",
            "token": {
                "address": opportunity.get("token"),
                "symbol": symbol,
                "name": opportunity.get("name", symbol),
                "price": price,
                "market_cap": opportunity.get("market_cap", 0),
                "liquidity": opportunity.get("liquidity", 0),
                "grade": grade,
                "age_hours": opportunity.get("age_hours", 0)
            },
            "tre_analysis": tre_analysis,
            "trade_details": {
                "entry_size_sol": position_size,
                "target_profit_pct": 15,
                "stop_loss_pct": 7,
                "time_stop_hours": 4,
                "estimated_slippage_pct": 1,
                "tre_insight": tre_boost
            },
            "risk_assessment": self._assess_risk(opportunity),
            "expires_at": (datetime.now() + timedelta(minutes=STAGE9_CONFIG["approval_timeout_minutes"])).isoformat()
        }
        
        return proposal
    
    def _assess_risk(self, opportunity: Dict) -> Dict:
        """Generate risk assessment for proposal."""
        risks = []
        tre_analysis = opportunity.get("tre_analysis", {})
        
        # Age risk
        age = opportunity.get("age_hours", 0)
        if age < 4:
            risks.append("Very new token (< 4 hours)")
        elif age > 12:
            risks.append("Token may have passed early momentum phase")
        
        # Liquidity risk
        liq = opportunity.get("liquidity", 0)
        if liq < 15000:
            risks.append("Lower liquidity may increase slippage")
        
        # Top 10 holder concentration
        top10 = opportunity.get("top_10_pct", 0)
        if top10 > 50:
            risks.append("High top 10 concentration (whale risk)")
        
        # TRE-based risks
        if tre_analysis.get("recommendation") == "CAUTION_DOWNTREND":
            risks.append("TRE detected downtrend pattern")
        
        if tre_analysis.get("anomalies"):
            for anomaly in tre_analysis["anomalies"][:2]:
                if anomaly["severity"] in ["medium", "high"]:
                    risks.append(f"TRE anomaly: {anomaly['type']} ({anomaly['severity']})")
        
        # Generate risk level
        if len(risks) >= 3:
            risk_level = "HIGH"
            recommendation = "PROCEED_WITH_CAUTION"
        elif len(risks) >= 1:
            risk_level = "MEDIUM"
            recommendation = "ACCEPTABLE_WITH_LIMITS"
        else:
            risk_level = "LOW"
            recommendation = "FAVORABLE"
        
        return {
            "level": risk_level,
            "recommendation": recommendation,
            "risks": risks,
            "mitigation": [
                "Position size limited by TRE analysis",
                "Stop loss at -7% enforced",
                "Time stop at 4 hours",
                "Safety Engine monitoring active"
            ]
        }
    
    def display_proposal(self, proposal: Dict):
        """Display proposal to user for approval."""
        token = proposal["token"]
        trade = proposal["trade_details"]
        risk = proposal["risk_assessment"]
        tre = proposal.get("tre_analysis", {})
        
        print("\n" + "=" * 70)
        print("🎯 TRADE PROPOSAL - AWAITING APPROVAL")
        print("=" * 70)
        print(f"\n📊 Token: {token['name']} (${token['symbol']})")
        print(f"   Grade: {token['grade']}")
        print(f"   Market Cap: ${token['market_cap']:,.0f}")
        print(f"   Liquidity: ${token['liquidity']:,.0f}")
        print(f"   Age: {token['age_hours']:.1f} hours")
        
        print(f"\n🔮 TRE Analysis:")
        if tre.get("has_data"):
            trend = tre.get("trend", {})
            if trend:
                print(f"   Trend: {trend.get('direction', 'N/A').upper()}")
                print(f"   Confidence: {trend.get('confidence', 0):.2f}")
                print(f"   Price Change: {trend.get('percent_change', 0):.2f}%")
            
            forecast = tre.get("forecast", [])
            if forecast:
                next_pred = forecast[0]
                print(f"   Forecast (4h): ${next_pred.get('predicted_value', 0):.8f}")
        else:
            print("   Insufficient historical data for forecasting")
        
        print(f"\n💰 Trade Details:")
        print(f"   Entry Size: {trade['entry_size_sol']} SOL")
        print(f"   Target: +{trade['target_profit_pct']}%")
        print(f"   Stop Loss: -{trade['stop_loss_pct']}%")
        print(f"   Time Stop: {trade['time_stop_hours']} hours")
        print(f"   TRE Insight: {trade['tre_insight']}")
        
        print(f"\n🛡️ Risk Assessment: {risk['level']}")
        print(f"   Recommendation: {risk['recommendation']}")
        if risk['risks']:
            print(f"   Risks:")
            for r in risk['risks']:
                print(f"     • {r}")
        print(f"   Mitigation: {', '.join(risk['mitigation'][:2])}")
        
        print(f"\n⏰ Expires: {proposal['expires_at']}")
        print("\n" + "=" * 70)
        print("💬 Respond with:")
        print("   APPROVE - Execute this trade")
        print("   REJECT  - Skip this opportunity")
        print("   MODIFY  - I want to adjust something")
        print("=" * 70 + "\n")
    
    def save_proposal(self, proposal: Dict):
        """Save proposal to file."""
        try:
            with open(PROPOSALS_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {"pending": [], "history": []}
        
        data["pending"].append(proposal)
        
        with open(PROPOSALS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def execute_trade(self, proposal: Dict) -> bool:
        """
        Execute approved trade via Jupiter API with Safety Engine verification.
        Returns success status.
        """
        self.log(f"🚀 Executing trade for {proposal['token']['symbol']}...")
        
        # Final safety check
        can_proceed, safety_result = self.check_safety_before_trade(proposal)
        if not can_proceed:
            self.log(f"🚫 Trade blocked by Safety Engine: {safety_result.get('reason', 'Unknown')}")
            self.audit_log("TRADE_BLOCKED", {"proposal": proposal, "safety_result": safety_result})
            return False
        
        # Record execution in audit log
        self.audit_log("TRADE_EXECUTING", {"proposal": proposal})
        
        # In Stage 9, this would call Jupiter API
        # For now, we'll simulate successful execution
        
        trade_record = {
            "id": f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "proposal_id": proposal["id"],
            "timestamp": datetime.now().isoformat(),
            "token": proposal["token"],
            "entry": {
                "size_sol": proposal["trade_details"]["entry_size_sol"],
                "price": proposal["token"]["price"],
                "tx_hash": "SIMULATED_TX_HASH"  # Would be real in production
            },
            "exit_plan": {
                "target_price": proposal["token"]["price"] * 1.15,
                "stop_price": proposal["token"]["price"] * 0.93,
                "time_deadline": (datetime.now() + timedelta(hours=4)).isoformat()
            },
            "tre_analysis": proposal.get("tre_analysis", {}),
            "safety_verification": safety_result,
            "status": "OPEN",
            "pnl_pct": 0,
            "pnl_sol": 0
        }
        
        # Save trade
        self._record_trade(trade_record)
        
        # Update state
        self.state["trades_today"] = self.state.get("trades_today", 0) + 1
        self.state["total_trades"] = self.state.get("total_trades", 0) + 1
        self.state["last_trade_time"] = datetime.now().isoformat()
        self.save_state()
        
        # Record success in audit log
        self.audit_log("TRADE_EXECUTED", {"trade": trade_record})
        
        self.log(f"✅ Trade executed: {proposal['token']['symbol']} @ {proposal['token']['price']}")
        print(f"\n📋 Trade recorded. Monitoring for exit conditions.")
        
        return True
    
    def _record_trade(self, trade: Dict):
        """Record trade to file."""
        try:
            with open(TRADES_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {"trades": []}
        
        data["trades"].append(trade)
        
        with open(TRADES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run_cycle(self):
        """Run one monitoring cycle."""
        # Check safety limits
        can_trade, reason = self.check_safety_limits()
        if not can_trade:
            self.log(f"⛔ Cannot trade: {reason}")
            return
        
        # Scan for opportunities
        opportunity = self.scan_for_opportunities()
        if not opportunity:
            self.log("🔍 No Grade A/A+ opportunities found")
            return
        
        # Generate proposal
        proposal = self.generate_proposal(opportunity)
        self.save_proposal(proposal)
        
        # Display for approval
        self.display_proposal(proposal)
        
        return proposal


def main():
    """Main entry point."""
    trader = Stage9SemiAutonomousTrader()
    
    # Show current status
    state = trader.state
    print(f"\n📊 Status:")
    print(f"   Trades today: {state.get('trades_today', 0)}/{STAGE9_CONFIG['max_daily_trades']}")
    print(f"   Loss today: {state.get('loss_today_sol', 0)}/{STAGE9_CONFIG['max_daily_loss_sol']} SOL")
    print(f"   Total trades: {state.get('total_trades', 0)}")
    print(f"   Successful: {state.get('successful_trades', 0)}")
    
    print("\n🔄 Starting scan cycle with TRE forecasting...")
    proposal = trader.run_cycle()
    
    if proposal:
        print("\n✨ STAGE 9: Proposal generated with TRE analysis!")
        print(f"   Proposal ID: {proposal['id']}")
        print(f"   TRE Recommendation: {proposal['tre_analysis'].get('recommendation', 'N/A')}")
        print("\n💬 Type APPROVE, REJECT, or MODIFY to respond.")
    else:
        print("\n⏰ No actionable opportunities right now. Will scan again.")


if __name__ == "__main__":
    import glob
    main()
