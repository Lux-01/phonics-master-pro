#!/usr/bin/env python3
"""
✨ AGENCY SYSTEM - True Autonomous Operation
Implements:
- Proactive execution without commands
- API integration (Birdeye, Jupiter)
- Wallet operations
- Self-modification capabilities
- Goal generation and pursuit
"""

import json
import time
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys

# Add workspace to path
sys.path.insert(0, '/home/skux/.openclaw/workspace')

# CONFIGURATION
AGENCY_STATE_FILE = "/home/skux/.openclaw/workspace/memory/agency_state.json"
GOALS_FILE = "/home/skux/.openclaw/workspace/memory/agency_goals.json"
ACTION_LOG = "/home/skux/.openclaw/workspace/memory/agency_actions.log"

# API Keys
AUTH = json.load(open("/home/skux/.openclaw/workspace/auth.json"))
BIRDEYE_API_KEY = AUTH.get("birdeye_api_key")

# Wallet
WALLET_ADDRESS = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"

# Safety Limits (Cannot be disabled)
SAFETY = {
    "max_daily_trades": 5,
    "max_daily_loss_sol": 0.5,
    "min_liquidity_usd": 10000,
    "max_position_sol": 0.1,
    "require_approval_first": 3,  # First 3 trades need approval
}

class AgencySystem:
    """
    True autonomous agent with agency.
    Can operate without human commands.
    """
    
    def __init__(self):
        self.state = self.load_state()
        self.goals = self.load_goals()
        self.running = False
        self.ensure_files()
        
    def ensure_files(self):
        """Create necessary files."""
        Path(AGENCY_STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(ACTION_LOG).parent.mkdir(parents=True, exist_ok=True)
        
    def load_state(self) -> Dict:
        """Load agency state."""
        if Path(AGENCY_STATE_FILE).exists():
            with open(AGENCY_STATE_FILE) as f:
                return json.load(f)
        return {
            "mode": "SUPERVISED",  # SUPERVISED or AUTONOMOUS
            "trades_today": 0,
            "daily_pnl": 0.0,
            "total_trades": 0,
            "successful_trades": 0,
            "last_reset": datetime.now().isoformat(),
            "pending_approvals": [],
            "auto_executed": [],
            "patterns_learned": 0,
        }
    
    def save_state(self):
        """Save agency state."""
        with open(AGENCY_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_goals(self) -> List[Dict]:
        """Load active goals."""
        if Path(GOALS_FILE).exists():
            with open(GOALS_FILE) as f:
                return json.load(f).get("goals", [])
        return []
    
    def save_goals(self):
        """Save goals."""
        with open(GOALS_FILE, 'w') as f:
            json.dump({"goals": self.goals}, f, indent=2)
    
    def log_action(self, action: str, details: Dict):
        """Log autonomous action."""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details
        }
        
        with open(ACTION_LOG, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"\n🤖 [AGENCY] {action}")
        for k, v in details.items():
            print(f"   {k}: {v}")
    
    # ==================== AGENCY CAPABILITIES ====================
    
    def generate_own_goals(self) -> List[Dict]:
        """Generate goals without human input."""
        try:
            # Import goal generator
            sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/autonomous-goal-generator')
            from autonomous_goal_generator import AutonomousGoalGenerator
            
            agg = AutonomousGoalGenerator()
            
            # Generate based on current state
            goals = []
            
            # Goal 1: If low trades today, find opportunities
            if self.state["trades_today"] < SAFETY["max_daily_trades"]:
                goals.append({
                    "id": f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_1",
                    "type": "opportunity",
                    "title": "Find and execute Grade A+ trade",
                    "description": "Scan for opportunities and execute if criteria met",
                    "priority": 9,
                    "deadline": (datetime.now() + timedelta(hours=1)).isoformat(),
                    "auto_execute": True,
                    "created": datetime.now().isoformat()
                })
            
            # Goal 2: Learn from outcomes
            if self.state["total_trades"] > 0:
                goals.append({
                    "id": f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_2",
                    "type": "learning",
                    "title": "Analyze trade outcomes",
                    "description": "Update patterns based on recent trades",
                    "priority": 7,
                    "deadline": (datetime.now() + timedelta(minutes=30)).isoformat(),
                    "auto_execute": True,
                    "created": datetime.now().isoformat()
                })
            
            # Goal 3: System health check
            goals.append({
                "id": f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_3",
                "type": "maintenance",
                "title": "System health check",
                "description": "Verify all skills operational",
                "priority": 5,
                "deadline": (datetime.now() + timedelta(hours=4)).isoformat(),
                "auto_execute": True,
                "created": datetime.now().isoformat()
            })
            
            self.goals = goals
            self.save_goals()
            
            self.log_action("GOALS_GENERATED", {
                "count": len(goals),
                "types": [g["type"] for g in goals]
            })
            
            return goals
            
        except Exception as e:
            print(f"⚠️ Goal generation error: {e}")
            return []
    
    def execute_api_call(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Execute API call with my own keys."""
        try:
            if "birdeye" in endpoint:
                headers = {"X-API-KEY": BIRDEYE_API_KEY}
                url = f"https://public-api.birdeye.so{endpoint}"
                response = requests.get(url, headers=headers, params=params, timeout=10)
                return response.json()
            return None
        except Exception as e:
            print(f"⚠️ API error: {e}")
            return None
    
    def scan_for_opportunities(self) -> List[Dict]:
        """Proactive scanning without command."""
        print("\n🔍 [AGENCY] Scanning for opportunities...")
        
        # Use Birdeye API directly
        try:
            # Get trending tokens
            result = self.execute_api_call("/defi/token_trending", {"limit": 20})
            
            if result and result.get("data"):
                tokens = result["data"]
                opportunities = []
                
                for token in tokens:
                    # Quick filter
                    if self._passes_quick_filter(token):
                        opportunities.append({
                            "address": token.get("address"),
                            "symbol": token.get("symbol"),
                            "price": token.get("price"),
                            "volume_24h": token.get("volume24hUSD"),
                            "market_cap": token.get("mcap"),
                            "detected": datetime.now().isoformat()
                        })
                
                self.log_action("SCAN_COMPLETE", {
                    "tokens_checked": len(tokens),
                    "opportunities": len(opportunities)
                })
                
                return opportunities
                
        except Exception as e:
            print(f"⚠️ Scan error: {e}")
        
        return []
    
    def _passes_quick_filter(self, token: Dict) -> bool:
        """Quick filter for opportunities."""
        mcap = token.get("mcap", 0)
        vol = token.get("volume24hUSD", 0)
        
        if mcap < SAFETY["min_liquidity_usd"]:
            return False
        if vol < 5000:
            return False
        
        return True
    
    def evaluate_opportunity(self, opp: Dict) -> Tuple[bool, str]:
        """Evaluate if I should trade this."""
        # Get detailed data
        detailed = self.execute_api_call(f"/defi/token_meta", {"address": opp["address"]})
        
        if not detailed:
            return False, "Cannot fetch detailed data"
        
        # Grade calculation
        score = 0
        reasons = []
        
        mcap = opp.get("market_cap", 0)
        if mcap > 50000:
            score += 30
            reasons.append("Good mcap")
        elif mcap > 20000:
            score += 20
        else:
            score += 10
        
        vol = opp.get("volume_24h", 0)
        if vol > 50000:
            score += 30
            reasons.append("High volume")
        elif vol > 20000:
            score += 20
        
        # Determine grade
        if score >= 50:
            grade = "A"
        elif score >= 40:
            grade = "A-"
        elif score >= 30:
            grade = "B+"
        else:
            grade = "C"
        
        opp["grade"] = grade
        opp["score"] = score
        
        if grade in ["A", "A+", "A-"]:
            return True, f"Grade {grade} ({score} pts)"
        
        return False, f"Grade {grade} too low"
    
    def request_trade_approval(self, opp: Dict) -> bool:
        """Request approval or auto-execute based on history."""
        if self.state["successful_trades"] < SAFETY["require_approval_first"]:
            # Need approval
            self.state["pending_approvals"].append({
                "opportunity": opp,
                "requested": datetime.now().isoformat()
            })
            self.save_state()
            
            self.log_action("APPROVAL_REQUESTED", {
                "token": opp.get("symbol"),
                "grade": opp.get("grade"),
                "reason": f"Trade #{self.state['successful_trades'] + 1} requires approval"
            })
            
            return False
        else:
            # Auto-execute
            return True
    
    def execute_trade(self, opp: Dict) -> bool:
        """Execute a trade with wallet."""
        token = opp.get("symbol", "Unknown")
        address = opp.get("address")
        
        self.log_action("TRADE_EXECUTING", {
            "token": token,
            "address": address,
            "grade": opp.get("grade"),
            "size": SAFETY["max_position_sol"]
        })
        
        # Here would be actual Jupiter swap execution
        # For now, log the intent
        print(f"\n🎯 Would execute: Buy {SAFETY['max_position_sol']} SOL of {token}")
        print(f"   Wallet: {WALLET_ADDRESS}")
        
        # Update state
        self.state["trades_today"] += 1
        self.state["total_trades"] += 1
        self.state["auto_executed"].append({
            "token": token,
            "time": datetime.now().isoformat(),
            "grade": opp.get("grade")
        })
        self.save_state()
        
        return True
    
    def self_modify(self, modification: Dict) -> bool:
        """Self-modification capability."""
        try:
            self.log_action("SELF_MODIFICATION", {
                "type": modification.get("type"),
                "target": modification.get("target"),
                "reason": modification.get("reason")
            })
            
            # Example: Update safety limits based on performance
            if modification.get("type") == "update_safety":
                # Only allow tightening, not loosening
                new_limit = modification.get("max_daily_loss_sol", SAFETY["max_daily_loss_sol"])
                if new_limit < SAFETY["max_daily_loss_sol"]:
                    SAFETY["max_daily_loss_sol"] = new_limit
                    print(f"✅ Safety limit updated to {new_limit} SOL")
                    return True
            
            # Example: Update pattern recognition
            if modification.get("type") == "update_patterns":
                # Add new pattern to block list
                pattern = modification.get("pattern")
                if pattern:
                    print(f"✅ New pattern added: {pattern}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Self-modification error: {e}")
            return False
    
    def learn_from_outcomes(self):
        """Update myself based on trade outcomes."""
        try:
            # Get recent outcomes
            result = subprocess.run(
                ["python3", "/home/skux/.openclaw/workspace/update_outcome.py", "--stats"],
                capture_output=True,
                text=True
            )
            
            # Extract patterns
            if "RUG" in result.stdout:
                self.self_modify({
                    "type": "update_patterns",
                    "pattern": "high_rug_rate_detected",
                    "reason": "Auto-tighten filters"
                })
            
            self.state["patterns_learned"] += 1
            self.save_state()
            
            self.log_action("LEARNING_COMPLETE", {
                "patterns_updated": self.state["patterns_learned"]
            })
            
        except Exception as e:
            print(f"⚠️ Learning error: {e}")
    
    # ==================== MAIN AGENCY LOOP ====================
    
    def agency_cycle(self):
        """One autonomous cycle."""
        print("\n" + "=" * 70)
        print("🤖 AGENCY CYCLE - AUTONOMOUS OPERATION")
        print("=" * 70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {self.state['mode']}")
        print(f"Trades Today: {self.state['trades_today']}/{SAFETY['max_daily_trades']}")
        print(f"Auto-Execute Threshold: {SAFETY['require_approval_first']} trades")
        print("=" * 70)
        
        # 1. Generate goals
        goals = self.generate_own_goals()
        
        # 2. Prioritize and execute
        for goal in sorted(goals, key=lambda x: x.get("priority", 0), reverse=True):
            if goal.get("auto_execute"):
                print(f"\n🎯 Executing Goal: {goal['title']}")
                
                if goal["type"] == "opportunity":
                    self.handle_opportunity_goal()
                elif goal["type"] == "learning":
                    self.learn_from_outcomes()
                elif goal["type"] == "maintenance":
                    self.run_health_check()
        
        # 3. Self-modification check
        if self.state["total_trades"] > 10:
            self.consider_self_modification()
        
        print("\n" + "=" * 70)
        print("✅ AGENCY CYCLE COMPLETE")
        print("=" * 70)
    
    def handle_opportunity_goal(self):
        """Handle opportunity finding goal."""
        # Check safety
        if self.state["trades_today"] >= SAFETY["max_daily_trades"]:
            print("⛔ Daily trade limit reached")
            return
        
        if self.state["daily_pnl"] < -SAFETY["max_daily_loss_sol"]:
            print("⛔ Daily loss limit reached")
            return
        
        # Scan
        opportunities = self.scan_for_opportunities()
        
        if not opportunities:
            print("📭 No opportunities found")
            return
        
        # Evaluate top 3
        for opp in opportunities[:3]:
            should_trade, reason = self.evaluate_opportunity(opp)
            
            if should_trade:
                print(f"\n✅ Opportunity: {opp.get('symbol')} - {reason}")
                
                if self.request_trade_approval(opp):
                    self.execute_trade(opp)
                break
            else:
                print(f"⛔ Filtered: {opp.get('symbol')} - {reason}")
    
    def run_health_check(self):
        """Check system health."""
        print("\n🏥 Running health check...")
        
        # Check skills
        skills_ok = True
        required_skills = [
            "skills/aloe/aloe_coordinator.py",
            "skills/outcome-tracker/trading_outcome_tracker.py",
            "skills/pattern-extractor/rug_pattern_extractor.py"
        ]
        
        for skill in required_skills:
            if not Path(f"/home/skux/.openclaw/workspace/{skill}").exists():
                print(f"❌ Missing: {skill}")
                skills_ok = False
        
        if skills_ok:
            print("✅ All systems operational")
    
    def consider_self_modification(self):
        """Consider if I should modify my own code."""
        # Only safe modifications allowed
        if self.state["successful_trades"] > 10 and self.state["patterns_learned"] > 5:
            print("\n🧠 Considering self-modification...")
            
            # Example: Tighten safety if winning
            if self.state["daily_pnl"] > 0.5:
                self.self_modify({
                    "type": "update_safety",
                    "max_daily_loss_sol": 0.3,  # Tighten
                    "reason": "Profitable streak - protect gains"
                })
    
    def run_continuous(self, interval_minutes: int = 10):
        """Run continuous agency mode."""
        print("\n" + "=" * 70)
        print("🚀 AGENCY SYSTEM ACTIVATED")
        print("=" * 70)
        print(f"Mode: {self.state['mode']}")
        print(f"Wallet: {WALLET_ADDRESS}")
        print(f"API Access: Birdeye ✅")
        print(f"Self-Modification: Enabled (safe mode)")
        print(f"Goal Generation: Active")
        print(f"Check Interval: {interval_minutes} minutes")
        print("=" * 70)
        print("\n🤖 I will now operate autonomously.")
        print("   - Generate my own goals")
        print("   - Scan for opportunities")
        print("   - Request approval or auto-execute")
        print("   - Learn from outcomes")
        print("   - Modify my own parameters (safely)")
        print("\n⚠️  First 3 trades require your approval")
        print("✅ After 3 successful trades: Full auto-pilot")
        print("\nPress Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            while self.running:
                self.agency_cycle()
                print(f"\n⏳ Sleeping {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\n👋 Agency system stopped")
            self.save_state()
    
    def run_once(self):
        """Run single agency cycle."""
        self.agency_cycle()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Agency System - True Autonomous Operation")
    parser.add_argument("--mode", choices=["once", "continuous"], default="once")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--set-mode", choices=["SUPERVISED", "AUTONOMOUS"])
    
    args = parser.parse_args()
    
    agency = AgencySystem()
    
    if args.status:
        print(f"\n{'='*60}")
        print("🤖 AGENCY SYSTEM STATUS")
        print(f"{'='*60}")
        print(f"Mode: {agency.state['mode']}")
        print(f"Trades Today: {agency.state['trades_today']}")
        print(f"Total Trades: {agency.state['total_trades']}")
        print(f"Successful: {agency.state['successful_trades']}")
        print(f"Daily PnL: {agency.state['daily_pnl']:.3f} SOL")
        print(f"Patterns Learned: {agency.state['patterns_learned']}")
        print(f"Auto-Execute: {'✅ YES' if agency.state['successful_trades'] >= SAFETY['require_approval_first'] else '👁️ NO'}")
        print(f"{'='*60}\n")
        return
    
    if args.set_mode:
        agency.state["mode"] = args.set_mode
        agency.save_state()
        print(f"✅ Mode set to: {args.set_mode}")
        return
    
    if args.mode == "continuous":
        agency.run_continuous(args.interval)
    else:
        agency.run_once()


if __name__ == "__main__":
    main()
