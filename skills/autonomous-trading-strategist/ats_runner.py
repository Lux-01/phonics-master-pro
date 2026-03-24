#!/usr/bin/env python3
"""
Autonomous Trading Strategist (ATS)
24/7 crypto research and analysis engine.
Market structure, liquidity, volume patterns, narrative mapping, risk scoring.
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Paths
ATS_DIR = Path("/home/skux/.openclaw/workspace/skills/autonomous-trading-strategist")
DATA_DIR = ATS_DIR / "data"
THESIS_DIR = DATA_DIR / "theses"
ALERTS_DIR = DATA_DIR / "alerts"

for d in [ATS_DIR, DATA_DIR, THESIS_DIR, ALERTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class TokenMetrics:
    address: str
    symbol: str
    price: float
    market_cap: float
    volume_24h: float
    volume_vs_avg: float
    price_change_24h: float
    liquidity_usd: float
    liquidity_locked: bool
    holders: int
    top10_pct: float
    age_hours: float


@dataclass
class RiskScore:
    contract: int
    liquidity: int
    holder: int
    volume: int
    narrative: int
    overall: int


@dataclass
class TradingSignal:
    token: TokenMetrics
    risk: RiskScore
    grade: str
    entry_price: float
    target_price: float
    stop_loss: float
    position_size: float
    confidence: float
    thesis: str


class AutonomousTradingStrategist:
    """
    24/7 autonomous crypto analyst.
    Generates theses, scores risks, creates signals.
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.thesis_dir = THESIS_DIR
        self.alerts_dir = ALERTS_DIR
        self.tracked_tokens: List[Dict] = []
        self.active_signals: List[TradingSignal] = []
        
    async def analyze_token(self, address: str, symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """Analyze a single token comprehensively."""
        
        # Fetch data from multiple sources
        metrics = await self._fetch_token_metrics(address, symbol)
        
        if not metrics:
            return {"error": "Could not fetch token data"}
        
        # Risk scoring
        risk = self._calculate_risk_score(metrics)
        
        # Narrative detection
        narrative = self._detect_narrative(metrics)
        
        # Grade calculation
        grade = self._calculate_grade(metrics, risk)
        
        # Thesis generation
        thesis = self._generate_thesis(metrics, risk, narrative, grade)
        
        # Signal generation (if passing grade)
        signal = None
        if grade in ['A+', 'A', 'A-']:
            signal = self._generate_signal(metrics, risk, grade, thesis)
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "token_address": address,
            "token_symbol": metrics.symbol,
            "metrics": {
                "price": metrics.price,
                "market_cap": metrics.market_cap,
                "volume_24h": metrics.volume_24h,
                "volume_vs_avg": round(metrics.volume_vs_avg, 2),
                "price_change_24h": round(metrics.price_change_24h, 2),
                "liquidity_usd": metrics.liquidity_usd,
                "liquidity_locked": metrics.liquidity_locked,
                "holders": metrics.holders,
                "top10_pct": metrics.top10_pct,
                "age_hours": round(metrics.age_hours, 1)
            },
            "risk_score": {
                "contract": risk.contract,
                "liquidity": risk.liquidity,
                "holder": risk.holder,
                "volume": risk.volume,
                "narrative": risk.narrative,
                "overall": risk.overall
            },
            "narrative": narrative,
            "grade": grade,
            "thesis": thesis
        }
        
        if signal:
            analysis["signal"] = {
                "entry": signal.entry_price,
                "target": signal.target_price,
                "stop": signal.stop_loss,
                "position_size": signal.position_size,
                "confidence": signal.confidence
            }
            self.active_signals.append(signal)
            await self._send_alert(signal)
        
        # Save thesis
        self._save_thesis(analysis)
        
        return analysis
    
    async def _fetch_token_metrics(self, address: str, symbol: str) -> Optional[TokenMetrics]:
        """Fetch token data from multiple sources."""
        
        # Simulated data - in production would call real APIs
        # This is a scaffold for the actual implementation
        
        metrics = TokenMetrics(
            address=address,
            symbol=symbol,
            price=0.045,
            market_cap=450000,
            volume_24h=120000,
            volume_vs_avg=3.2,
            price_change_24h=23.0,
            liquidity_usd=200000,
            liquidity_locked=True,
            holders=1250,
            top10_pct=35.4,
            age_hours=4.5
        )
        
        return metrics
    
    def _calculate_risk_score(self, metrics: TokenMetrics) -> RiskScore:
        """Calculate comprehensive risk score."""
        
        # Contract risk (30%)
        contract_risk = 85 if metrics.liquidity_locked else 50
        
        # Liquidity risk (25%)
        liq_risk = min(100, int(metrics.liquidity_usd / 5000))
        
        # Holder risk (20%)
        holder_risk = max(0, 100 - int(metrics.top10_pct * 2))
        
        # Volume risk (15%)
        vol_risk = min(100, int(metrics.volume_vs_avg * 20))
        
        # Narrative risk (10%)
        narrative_risk = 80  # Default
        
        # Overall weighted average
        overall = int(
            contract_risk * 0.30 +
            liq_risk * 0.25 +
            holder_risk * 0.20 +
            vol_risk * 0.15 +
            narrative_risk * 0.10
        )
        
        return RiskScore(
            contract=contract_risk,
            liquidity=liq_risk,
            holder=holder_risk,
            volume=vol_risk,
            narrative=narrative_risk,
            overall=overall
        )
    
    def _detect_narrative(self, metrics: TokenMetrics) -> Dict[str, Any]:
        """Detect which narrative the token belongs to."""
        
        narratives = {
            "AI Agents": ["AI16Z", "ZEREBRO", "GRIFFAIN"],
            "Meme Coins": ["BONK", "WIF", "POPCAT"],
            "DeFi": ["JUP", "RAY", "ORCA"],
            "Gaming": ["PRIME", "BEAM", "ATLAS"]
        }
        
        # Simple detection based on symbol (in production: social analysis)
        detected = "Unknown"
        confidence = 0.7
        
        for narrative, tokens in narratives.items():
            if metrics.symbol in tokens:
                detected = narrative
                confidence = 0.9
                break
        
        return {
            "detected": detected,
            "confidence": confidence,
            "trending": metrics.volume_vs_avg > 3
        }
    
    def _calculate_grade(self, metrics: TokenMetrics, risk: RiskScore) -> str:
        """Calculate token grade A+ to D."""
        
        score = 0
        
        # Market cap tier
        if metrics.market_cap >= 10000000:  # $10M+
            score += 10
        elif metrics.market_cap >= 1000000:  # $1M+
            score += 8
        elif metrics.market_cap >= 500000:  # $500K+
            score += 6
        elif metrics.market_cap >= 100000:  # $100K+
            score += 4
        else:
            score += 2
        
        # Volume vs average
        if metrics.volume_vs_avg >= 5:
            score += 5
        elif metrics.volume_vs_avg >= 3:
            score += 4
        elif metrics.volume_vs_avg >= 2:
            score += 3
        else:
            score += 1
        
        # Liquidity
        if metrics.liquidity_usd >= 500000:
            score += 5
        elif metrics.liquidity_usd >= 100000:
            score += 4
        elif metrics.liquidity_usd >= 50000:
            score += 3
        else:
            score += 1
        
        # Risk score
        if risk.overall >= 80:
            score += 5
        elif risk.overall >= 70:
            score += 4
        elif risk.overall >= 60:
            score += 3
        else:
            score += 1
        
        # Age (apply Phase 1 protections)
        if metrics.age_hours < 0.5:  # < 30 min - REJECT
            score = 0
        elif metrics.age_hours < 2:  # < 2h - DEMOTE
            score -= 2
        elif metrics.age_hours >= 6:
            score += 1
        
        # Holder concentration (apply Phase 1 protection)
        if metrics.top10_pct > 70:  # REJECT
            score = 0
        elif metrics.top10_pct > 50:  # DEMOTE
            score -= 2
        
        # Assign grade
        if score >= 22:
            return "A+"
        elif score >= 18:
            return "A"
        elif score >= 15:
            return "A-"
        elif score >= 12:
            return "B+"
        elif score >= 10:
            return "B"
        elif score >= 8:
            return "C"
        elif score > 0:
            return "D"
        else:
            return "F"
    
    def _generate_thesis(self, metrics: TokenMetrics, risk: RiskScore, 
                         narrative: Dict, grade: str) -> str:
        """Generate investment thesis."""
        
        thesis = f"""# {metrics.symbol} Investment Thesis

## Executive Summary
{metrics.symbol} is graded **{grade}** with an overall risk score of {risk.overall}/100.

## Market Context
- Market Cap: ${metrics.market_cap:,.0f}
- Price: ${metrics.price:.6f} ({metrics.price_change_24h:+.1f}% 24h)
- Volume: ${metrics.volume_24h:,.0f} ({metrics.volume_vs_avg:.1f}x average)

## Token Analysis
**Liquidity:** ${metrics.liquidity_usd:,.0f} {'(locked ✅)' if metrics.liquidity_locked else '(unlocked ⚠️)'}
**Holders:** {metrics.holders:,} (Top 10%: {metrics.top10_pct:.1f}%)
**Age:** {metrics.age_hours:.1f} hours

## Risk Assessment
| Category | Score |
|----------|-------|
| Contract Risk | {risk.contract}/100 |
| Liquidity Risk | {risk.liquidity}/100 |
| Holder Risk | {risk.holder}/100 |
| Volume Risk | {risk.volume}/100 |
| Narrative Risk | {risk.narrative}/100 |
| **Overall** | **{risk.overall}/100** |

## Narrative
{narrative['detected']} {'(trending 🔥)' if narrative['trending'] else '(stable)'}

## Conclusion
{'✅ Strong buy signal' if grade in ['A+', 'A', 'A-'] else '⚠️ Proceed with caution' if grade in ['B+', 'B'] else '❌ Avoid'}
"""
        
        return thesis
    
    def _generate_signal(self, metrics: TokenMetrics, risk: RiskScore, 
                         grade: str, thesis: str) -> TradingSignal:
        """Generate trading signal."""
        
        # Position sizing based on Phase 1
        if grade == "A+":
            position_size = 0.02  # SOL
        elif grade == "A":
            position_size = 0.02
        elif grade == "A-":
            position_size = 0.015
        else:
            position_size = 0.01
        
        # Entry/exit logic
        entry = metrics.price
        target = entry * 1.15  # +15% target
        stop = entry * 0.93    # -7% stop
        
        confidence = min(95, risk.overall + 10)
        
        return TradingSignal(
            token=metrics,
            risk=risk,
            grade=grade,
            entry_price=entry,
            target_price=target,
            stop_loss=stop,
            position_size=position_size,
            confidence=round(confidence, 1),
            thesis=thesis
        )
    
    async def _send_alert(self, signal: TradingSignal):
        """Send high-priority alert."""
        
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "URGENT_SIGNAL",
            "token": signal.token.symbol,
            "address": signal.token.address,
            "grade": signal.grade,
            "entry": signal.entry_price,
            "target": signal.target_price,
            "stop": signal.stop_loss,
            "position_size": signal.position_size,
            "confidence": signal.confidence,
            "risk_score": signal.risk.overall
        }
        
        alert_file = self.alerts_dir / f"alert_{signal.token.address[:8]}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
    
    def _save_thesis(self, analysis: Dict):
        """Save thesis to disk."""
        
        filename = f"{analysis['token_symbol']}_{analysis['token_address'][:8]}_{datetime.now().strftime('%Y%m%d')}.json"
        thesis_file = self.thesis_dir / filename
        
        with open(thesis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
    
    def get_active_signals(self) -> List[TradingSignal]:
        """Get current active signals."""
        return self.active_signals
    
    def get_signal_stats(self) -> Dict:
        """Get signal statistics."""
        
        if not self.active_signals:
            return {"count": 0, "avg_confidence": 0}
        
        return {
            "count": len(self.active_signals),
            "avg_confidence": round(sum(s.confidence for s in self.active_signals) / len(self.active_signals), 1),
            "grade_distribution": self._count_grades(self.active_signals)
        }
    
    def _count_grades(self, signals: List[TradingSignal]) -> Dict[str, int]:
        """Count grades in signals."""
        counts = {}
        for s in signals:
            counts[s.grade] = counts.get(s.grade, 0) + 1
        return counts


# Global instance
ats = AutonomousTradingStrategist()


async def analyze_token(address: str, symbol: str = "UNKNOWN") -> Dict:
    """Quick analyze function."""
    return await ats.analyze_token(address, symbol)


def get_active_signals() -> List[TradingSignal]:
    """Quick get signals function."""
    return ats.get_active_signals()


def get_stats() -> Dict:
    """Quick get stats function."""
    return ats.get_signal_stats()


if __name__ == "__main__":
    print("🎯 Autonomous Trading Strategist (ATS)")
    print("=" * 60)
    
    # Example: Analyze a token
    print("\n🔍 Analyzing example token...")
    
    async def demo():
        result = await analyze_token(
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "EXAMPLE"
        )
        
        print(f"\n📊 Analysis Complete:")
        print(f"   Token: {result['token_symbol']}")
        print(f"   Grade: {result['grade']}")
        print(f"   Risk Score: {result['risk_score']['overall']}/100")
        
        if 'signal' in result:
            print(f"\n🎯 TRADING SIGNAL:")
            print(f"   Entry: ${result['signal']['entry']:.6f}")
            print(f"   Target: ${result['signal']['target']:.6f} (+15%)")
            print(f"   Stop: ${result['signal']['stop']:.6f} (-7%)")
            print(f"   Size: {result['signal']['position_size']} SOL")
            print(f"   Confidence: {result['signal']['confidence']}%")
        else:
            print(f"\n⛔ No signal - grade too low")
    
    asyncio.run(demo())
    
    print(f"\n📈 Stats: {get_stats()}")
    print(f"\n✅ ATS ready for 24/7 operation!")
