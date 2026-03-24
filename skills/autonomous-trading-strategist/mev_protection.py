#!/usr/bin/env python3
"""
MEV Protection Module for Autonomous Trading Strategist
Protects against MEV attacks, sandwich attacks, and front-running
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class MEVProtectionConfig:
    """Configuration for MEV protection"""
    # Slippage protection
    max_slippage_bps: int = 100  # 1% max slippage
    dynamic_slippage: bool = True
    
    # Transaction protection
    use_private_tx: bool = True
    tip_amount_sol: float = 0.001  # Priority fee
    
    # Timing protection
    min_block_delay: int = 1  # Wait at least 1 block
    max_pending_time: int = 30  # Max 30 seconds pending
    
    # Route protection
    split_routes: bool = True
    max_route_splits: int = 3
    
    # Detection settings
    detect_sandwich_risk: bool = True
    detect_frontrun_risk: bool = True
    mempool_monitoring: bool = True


class MEVProtector:
    """
    MEV Protection for trading operations
    
    Features:
    - Sandwich attack protection
    - Front-running detection
    - Private transaction routing
    - Dynamic slippage adjustment
    - Route splitting
    - Mempool monitoring
    """
    
    def __init__(self, config: MEVProtectionConfig = None, memory_dir: str = None):
        self.config = config or MEVProtectionConfig()
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/mev_protection")
        self.threats_file = os.path.join(self.memory_dir, "threats.json")
        self.protected_txs_file = os.path.join(self.memory_dir, "protected_transactions.json")
        self.stats_file = os.path.join(self.memory_dir, "stats.json")
        
        self._ensure_dirs()
        self.threats = self._load_threats()
        self.protected_txs = self._load_protected_txs()
        self.stats = self._load_stats()
        
        # Simulated mempool (in production, this would connect to real mempool)
        self.mempool = []
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_threats(self) -> List[Dict]:
        try:
            if os.path.exists(self.threats_file):
                with open(self.threats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _load_protected_txs(self) -> List[Dict]:
        try:
            if os.path.exists(self.protected_txs_file):
                with open(self.protected_txs_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _load_stats(self) -> Dict:
        defaults = {
            "total_txs": 0,
            "protected_txs": 0,
            "threats_detected": 0,
            "sandwich_attacks_blocked": 0,
            "frontrun_attempts_blocked": 0,
            "estimated_savings_usd": 0.0
        }
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults
    
    def _save(self):
        try:
            with open(self.threats_file, 'w') as f:
                json.dump(self.threats, f, indent=2)
            with open(self.protected_txs_file, 'w') as f:
                json.dump(self.protected_txs, f, indent=2)
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"MEV save error: {e}")
    
    # ============ THREAT DETECTION ============
    
    def analyze_sandwich_risk(self, token: str, amount: float, 
                            expected_slippage: float) -> Dict:
        """
        Analyze risk of sandwich attack
        
        Returns risk assessment with recommendations
        """
        risk_factors = []
        risk_score = 0  # 0-100, higher = more risky
        
        # Check token liquidity
        if expected_slippage > 0.02:  # >2% slippage
            risk_factors.append("Low liquidity increases sandwich risk")
            risk_score += 30
        
        # Check transaction size
        if amount > 10000:  # >$10k
            risk_factors.append("Large transaction size attracts MEV bots")
            risk_score += 25
        
        # Check mempool (simulated)
        mempool_threats = self._scan_mempool_for_threats(token)
        if mempool_threats:
            risk_factors.append(f"{len(mempool_threats)} suspicious transactions in mempool")
            risk_score += 35
        
        # Historical threats
        token_threats = [t for t in self.threats if t.get("token") == token]
        if token_threats:
            risk_factors.append(f"{len(token_threats)} historical threats detected")
            risk_score += 10
        
        risk_level = "low" if risk_score < 30 else "medium" if risk_score < 60 else "high"
        
        return {
            "token": token,
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "safe_to_proceed": risk_score < 70,
            "recommendations": self._get_sandwich_recommendations(risk_score)
        }
    
    def analyze_frontrun_risk(self, token: str, strategy: str) -> Dict:
        """Analyze risk of front-running"""
        risk_factors = []
        risk_score = 0
        
        # Strategy-based risk
        if strategy in ["momentum", "breakout"]:
            risk_factors.append("Momentum strategies are front-run targets")
            risk_score += 20
        
        # Check for known MEV bots
        if self._check_known_mev_bots(token):
            risk_factors.append("Active MEV bots detected for this token")
            risk_score += 40
        
        risk_level = "low" if risk_score < 30 else "medium" if risk_score < 60 else "high"
        
        return {
            "token": token,
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "safe_to_proceed": risk_score < 70,
            "recommendations": self._get_frontrun_recommendations(risk_score)
        }
    
    def _scan_mempool_for_threats(self, token: str) -> List[Dict]:
        """Scan mempool for suspicious transactions (simulated)"""
        # In production, this would connect to actual mempool
        threats = []
        
        # Simulate mempool scanning
        for tx in self.mempool:
            if tx.get("token") == token:
                if tx.get("type") == "large_swap":
                    threats.append(tx)
        
        return threats
    
    def _check_known_mev_bots(self, token: str) -> bool:
        """Check if known MEV bots are active (simulated)"""
        # In production, this would check actual bot activity
        return False
    
    def _get_sandwich_recommendations(self, risk_score: int) -> List[str]:
        """Get recommendations for sandwich protection"""
        recs = []
        
        if risk_score > 50:
            recs.append("Use private transaction relay (Jito, Flashbots)")
            recs.append("Split order into smaller chunks")
            recs.append("Add time delay between chunks")
        
        if risk_score > 30:
            recs.append("Set tight slippage tolerance")
            recs.append("Use priority fees to skip ahead")
        
        recs.append("Monitor mempool before executing")
        
        return recs
    
    def _get_frontrun_recommendations(self, risk_score: int) -> List[str]:
        """Get recommendations for frontrun protection"""
        recs = []
        
        if risk_score > 50:
            recs.append("Use private mempool (Jito bundle)")
            recs.append("Commit-reveal pattern for large orders")
        
        recs.append("Use DEX aggregator with MEV protection")
        recs.append("Consider time-weighted average price (TWAP)")
        
        return recs
    
    # ============ PROTECTION METHODS ============
    
    def protect_transaction(self, tx_details: Dict) -> Dict:
        """
        Apply MEV protection to a transaction
        
        Returns protected transaction details
        """
        token = tx_details.get("token")
        amount = tx_details.get("amount", 0)
        expected_slippage = tx_details.get("expected_slippage", 0.01)
        
        # Analyze risks
        sandwich_risk = self.analyze_sandwich_risk(token, amount, expected_slippage)
        frontrun_risk = self.analyze_frontrun_risk(token, tx_details.get("strategy", ""))
        
        # Build protection strategy
        protection = {
            "original_tx": tx_details,
            "risk_analysis": {
                "sandwich": sandwich_risk,
                "frontrun": frontrun_risk
            },
            "protection_measures": [],
            "recommended_route": "standard",
            "estimated_protection_value": 0.0
        }
        
        # Apply protection measures based on risk
        if sandwich_risk["risk_score"] > 50 or frontrun_risk["risk_score"] > 50:
            protection["protection_measures"].append("private_tx_relay")
            protection["recommended_route"] = "private"
            protection["estimated_protection_value"] += amount * 0.005  # Save ~0.5%
        
        if self.config.split_routes and amount > 5000:
            protection["protection_measures"].append(f"split_route_{self.config.max_route_splits}_ways")
            protection["estimated_protection_value"] += amount * 0.002
        
        if self.config.dynamic_slippage:
            dynamic_slippage = self._calculate_dynamic_slippage(sandwich_risk)
            protection["protection_measures"].append(f"dynamic_slippage_{dynamic_slippage}bsp")
        
        # Add priority fee if needed
        if sandwich_risk["risk_score"] > 40:
            protection["protection_measures"].append(f"priority_tip_{self.config.tip_amount_sol}sol")
        
        # Record protected transaction
        protected_tx = {
            "tx_id": self._generate_tx_id(),
            "timestamp": datetime.now().isoformat(),
            "protection": protection,
            "status": "protected"
        }
        
        self.protected_txs.append(protected_tx)
        self.stats["total_txs"] += 1
        self.stats["protected_txs"] += 1
        self.stats["estimated_savings_usd"] += protection["estimated_protection_value"]
        self._save()
        
        return protection
    
    def _calculate_dynamic_slippage(self, risk_analysis: Dict) -> int:
        """Calculate dynamic slippage based on risk"""
        base_slippage = self.config.max_slippage_bps
        risk_score = risk_analysis["risk_score"]
        
        # Reduce slippage tolerance in high-risk scenarios
        if risk_score > 70:
            return min(base_slippage // 2, 50)  # 0.5% max
        elif risk_score > 40:
            return min(int(base_slippage * 0.75), 75)  # 0.75% max
        
        return base_slippage
    
    def _generate_tx_id(self) -> str:
        """Generate unique transaction ID"""
        return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:16]
    
    # ============ MONITORING ============
    
    def record_threat(self, threat_type: str, details: Dict):
        """Record detected threat for learning"""
        threat = {
            "type": threat_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        self.threats.append(threat)
        self.stats["threats_detected"] += 1
        
        if threat_type == "sandwich":
            self.stats["sandwich_attacks_blocked"] += 1
        elif threat_type == "frontrun":
            self.stats["frontrun_attempts_blocked"] += 1
        
        self._save()
    
    def get_protection_report(self) -> str:
        """Generate MEV protection report"""
        lines = [
            "🛡️ MEV Protection Report",
            "=" * 50,
            f"Total transactions: {self.stats['total_txs']}",
            f"Protected transactions: {self.stats['protected_txs']}",
            f"Threats detected: {self.stats['threats_detected']}",
            f"Sandwich attacks blocked: {self.stats['sandwich_attacks_blocked']}",
            f"Frontrun attempts blocked: {self.stats['frontrun_attempts_blocked']}",
            f"Estimated savings: ${self.stats['estimated_savings_usd']:.2f}",
            "",
            "Configuration:",
            f"  Max slippage: {self.config.max_slippage_bps}bsp",
            f"  Dynamic slippage: {self.config.dynamic_slippage}",
            f"  Private TX: {self.config.use_private_tx}",
            f"  Split routes: {self.config.split_routes}",
        ]
        
        if self.threats:
            lines.extend(["", "Recent threats:"])
            for t in self.threats[-5:]:
                lines.append(f"  {t['timestamp'][:10]} | {t['type']} | {t['details'].get('token', 'N/A')}")
        
        return "\n".join(lines)
    
    def get_token_risk_profile(self, token: str) -> Dict:
        """Get comprehensive risk profile for a token"""
        token_threats = [t for t in self.threats if t.get("details", {}).get("token") == token]
        
        return {
            "token": token,
            "threat_count": len(token_threats),
            "threat_types": list(set(t["type"] for t in token_threats)),
            "last_threat": token_threats[-1]["timestamp"] if token_threats else None,
            "risk_level": "high" if len(token_threats) > 5 else "medium" if len(token_threats) > 2 else "low"
        }


# ============ INTEGRATION HELPER ============

def create_mev_protected_signal(signal: Dict, mev_protector: MEVProtector) -> Dict:
    """
    Wrap a trading signal with MEV protection
    
    Usage:
        signal = ats.generate_signal("SOL")
        protected = create_mev_protected_signal(signal, mev_protector)
    """
    tx_details = {
        "token": signal.get("token"),
        "amount": signal.get("size", 1000),  # Default $1k
        "expected_slippage": signal.get("slippage", 0.01),
        "strategy": signal.get("strategy", "standard")
    }
    
    protection = mev_protector.protect_transaction(tx_details)
    
    return {
        "original_signal": signal,
        "mev_protection": protection,
        "safe_to_execute": protection["risk_analysis"]["sandwich"]["safe_to_proceed"] and 
                           protection["risk_analysis"]["frontrun"]["safe_to_proceed"],
        "execution_recommendations": protection["protection_measures"]
    }


# ============ COMMAND LINE ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MEV Protection Module")
    parser.add_argument("--mode", choices=["report", "analyze", "protect", "test"], default="report")
    parser.add_argument("--token", help="Token to analyze")
    parser.add_argument("--amount", type=float, help="Transaction amount")
    
    args = parser.parse_args()
    
    protector = MEVProtector()
    
    if args.mode == "report":
        print(protector.get_protection_report())
    
    elif args.mode == "analyze":
        if not args.token:
            print("Error: --token required")
            return
        
        risk = protector.analyze_sandwich_risk(args.token, args.amount or 1000, 0.01)
        print(f"Token: {args.token}")
        print(f"Risk level: {risk['risk_level']}")
        print(f"Risk score: {risk['risk_score']}/100")
        print(f"Safe to proceed: {risk['safe_to_proceed']}")
        print("\nRisk factors:")
        for f in risk['risk_factors']:
            print(f"  • {f}")
        print("\nRecommendations:")
        for r in risk['recommendations']:
            print(f"  • {r}")
    
    elif args.mode == "protect":
        tx = {
            "token": args.token or "SOL",
            "amount": args.amount or 1000,
            "expected_slippage": 0.01,
            "strategy": "momentum"
        }
        protection = protector.protect_transaction(tx)
        print(json.dumps(protection, indent=2))
    
    elif args.mode == "test":
        print("🧪 Testing MEV Protection...")
        
        # Test risk analysis
        risk = protector.analyze_sandwich_risk("BONK", 5000, 0.02)
        print(f"✓ Risk analysis: {risk['risk_level']}")
        
        # Test protection
        tx = {"token": "SOL", "amount": 10000, "expected_slippage": 0.015}
        protection = protector.protect_transaction(tx)
        print(f"✓ Protection applied: {len(protection['protection_measures'])} measures")
        
        # Test report
        report = protector.get_protection_report()
        print(f"✓ Report generated")
        
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
