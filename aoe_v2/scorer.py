#!/usr/bin/env python3
"""
AOE v2.0 - Opportunity Scorer
7-factor scoring algorithm for token opportunities.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import logging

from scanner_base import Token


@dataclass
class ScoreBreakdown:
    """Detailed scoring breakdown for a token."""
    potential: float      # 0-100
    probability: float    # 0-100  
    speed: float          # 0-100
    fit: float            # 0-100
    alpha: float          # 0-100
    risk: float           # 0-100 (subtracted)
    effort: float         # 0-100 (subtracted)
    
    total: float = 0.0
    
    def calculate_total(self, weights: Dict[str, float]) -> float:
        """Calculate weighted total score."""
        self.total = (
            self.potential * weights['potential'] +
            self.probability * weights['probability'] +
            self.speed * weights['speed'] +
            self.fit * weights['fit'] +
            self.alpha * weights['alpha'] -
            self.risk * weights['risk'] -
            self.effort * weights['effort']
        )
        return self.total
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "potential": round(self.potential, 1),
            "probability": round(self.probability, 1),
            "speed": round(self.speed, 1),
            "fit": round(self.fit, 1),
            "alpha": round(self.alpha, 1),
            "risk": round(self.risk, 1),
            "effort": round(self.effort, 1),
            "total": round(self.total, 1)
        }


class OpportunityScorer:
    """
    7-factor opportunity scoring engine.
    
    Factors:
    - Potential (25%): Market cap upside, narrative strength
    - Probability (25%): Volume/MC ratio, liquidity, transaction density
    - Speed (15%): Time sensitivity, age, momentum
    - Fit (15%): Strategy alignment (mean reversion)
    - Alpha (20%): Early detection, source diversity
    - Risk (-20%): Liquidity risk, contract age, volatility
    - Effort (-10%): Time to act, complexity
    """
    
    # Strategy-specific configurations
    STRATEGIES = {
        "mean_reversion_microcap": {
            "weights": {
                "potential": 0.25,
                "probability": 0.25,
                "speed": 0.15,
                "fit": 0.15,
                "alpha": 0.20,
                "risk": 0.20,  # Subtracted
                "effort": 0.10  # Subtracted
            },
            "mc_ideal": 500_000,  # Sweet spot
            "mc_max": 20_000_000,
            "dip_ideal": -12,  # Ideal dip percentage
            "volume_min": 1_000,
            "liquidity_min": 5_000
        },
        "momentum_breakout": {
            "weights": {
                "potential": 0.30,
                "probability": 0.20,
                "speed": 0.20,
                "fit": 0.10,
                "alpha": 0.20,
                "risk": 0.15,
                "effort": 0.10
            },
            "mc_ideal": 2_000_000,
            "volume_min": 100_000
        },
        "early_launch": {
            "weights": {
                "potential": 0.35,
                "probability": 0.15,
                "speed": 0.25,
                "fit": 0.10,
                "alpha": 0.35,
                "risk": 0.25,
                "effort": 0.15
            },
            "mc_max": 1_000_000,
            "age_max_hours": 6
        }
    }
    
    def __init__(self, strategy: str = "mean_reversion_microcap"):
        self.strategy = strategy
        self.config = self.STRATEGIES.get(strategy, self.STRATEGIES["mean_reversion_microcap"])
        self.weights = self.config["weights"]
        self.logger = logging.getLogger("aoe.scorer")
    
    def score(self, token: Token) -> Tuple[float, ScoreBreakdown]:
        """
        Score a single token opportunity.
        
        Args:
            token: Token to score
            
        Returns:
            Tuple of (total_score, breakdown)
        """
        breakdown = ScoreBreakdown(
            potential=self._score_potential(token),
            probability=self._score_probability(token),
            speed=self._score_speed(token),
            fit=self._score_fit(token),
            alpha=self._score_alpha(token),
            risk=self._score_risk(token),
            effort=self._score_effort(token)
        )
        
        total = breakdown.calculate_total(self.weights)
        
        # Save to token
        token.opportunity_score = total
        token.score_breakdown = breakdown.to_dict()
        
        return total, breakdown
    
    def score_batch(self, tokens: List[Token]) -> List[Tuple[Token, float, ScoreBreakdown]]:
        """
        Score a batch of tokens.
        
        Args:
            tokens: Tokens to score
            
        Returns:
            List of (token, score, breakdown) sorted by score
        """
        results = []
        
        for token in tokens:
            try:
                score, breakdown = self.score(token)
                results.append((token, score, breakdown))
            except Exception as e:
                self.logger.warning(f"Failed to score {token.symbol}: {e}")
                continue
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def _score_potential(self, token: Token) -> float:
        """Score upside potential (0-100)."""
        score = 50.0  # Base
        
        # Market cap tier
        mc = token.market_cap
        if mc < 500_000:
            score += 25  # High upside potential
        elif mc < 2_000_000:
            score += 15
        elif mc < 10_000_000:
            score += 5
        else:
            score -= 10  # Lower upside
        
        # FDV vs MC (dilution risk)
        if token.fdv > 0 and token.market_cap > 0:
            ratio = token.fdv / token.market_cap
            if ratio > 5:
                score -= 15  # High dilution risk
            elif ratio > 2:
                score -= 5
        
        # Liquidity depth (can you actually sell?)
        if token.liquidity > 0:
            liq_ratio = token.liquidity / token.market_cap
            if liq_ratio > 0.3:
                score += 10  # Deep liquidity
            elif liq_ratio < 0.05:
                score -= 20  # Shallow liquidity - hard to exit
        
        # Narrative bonus
        narratives = token.__dict__.get('narratives', [])
        if 'ai' in narratives:
            score += 10
        if 'meme' in narratives:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_probability(self, token: Token) -> float:
        """Score probability of success (0-100)."""
        score = 50.0  # Base
        
        # Volume to market cap ratio (interest level)
        if token.market_cap > 0:
            vol_mc_ratio = token.volume_24h / token.market_cap
            if vol_mc_ratio > 1.0:
                score += 20  # Very high interest
            elif vol_mc_ratio > 0.5:
                score += 15
            elif vol_mc_ratio > 0.1:
                score += 10
            elif vol_mc_ratio > 0.01:
                score += 5
            else:
                score -= 20  # Dead token
        
        # Transaction density
        if token.txns_24h > 1000:
            score += 15
        elif token.txns_24h > 500:
            score += 10
        elif token.txns_24h > 100:
            score += 5
        elif token.txns_24h < 10:
            score -= 15  # No activity
        
        # Buy/sell ratio
        if token.buys_24h + token.sells_24h > 0:
            buy_ratio = token.buys_24h / (token.buys_24h + token.sells_24h)
            if buy_ratio > 0.6:
                score += 10  # Buying pressure
            elif buy_ratio < 0.4:
                score -= 10  # Selling pressure
        
        # Holder count (community size)
        if token.holders > 5000:
            score += 10
        elif token.holders > 1000:
            score += 5
        elif token.holders < 50:
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_speed(self, token: Token) -> float:
        """Score time sensitivity (0-100)."""
        score = 50.0  # Base
        
        # Age (newer is more time-sensitive)
        age_hours = token.__dict__.get('age_hours')
        if age_hours is not None:
            if age_hours < 2:
                score += 30  # Very fresh - act fast
            elif age_hours < 6:
                score += 20
            elif age_hours < 24:
                score += 10
            elif age_hours > 72:
                score -= 10  # Older, less urgent
        else:
            score += 5  # Unknown age = assume newer
        
        # Momentum (5m price change)
        if token.price_change_5m > 20:
            score += 15  # Breaking out
        elif token.price_change_5m > 5:
            score += 10
        elif token.price_change_5m < -20:
            score += 10  # Sharp dip = mean reversion opportunity
        
        # 1h momentum
        if token.price_change_1h > 50:
            score -= 10  # Might be topping
        elif token.price_change_1h < -30:
            score += 15  # Deep dip opportunity
        
        # Volume spike
        vol_spike = token.__dict__.get('vol_spike_5m', 1.0)
        if vol_spike > 5:
            score += 15  # 5x volume spike
        elif vol_spike > 3:
            score += 10
        elif vol_spike > 2:
            score += 5
        
        return max(0, min(100, score))
    
    def _score_fit(self, token: Token) -> float:
        """Score strategy fit (0-100)."""
        score = 50.0  # Base
        
        if self.strategy == "mean_reversion_microcap":
            # Ideal dip range: -10% to -18%
            dip = token.price_change_1h
            if -18 <= dip <= -10:
                score += 30  # Perfect dip
            elif -25 <= dip <= -8:
                score += 20  # Good dip
            elif -5 <= dip <= 0:
                score += 10  # Small dip
            elif dip > 10:
                score -= 20  # Already pumped
            elif dip < -40:
                score -= 15  # Might be dead
            
            # Volume spike bonus for mean reversion
            vol_spike = token.__dict__.get('vol_spike_5m', 1.0)
            if vol_spike > 2 and dip < 0:
                score += 15  # High volume dip = reversal signal
            
            # Market cap in sweet spot
            if 100_000 <= token.market_cap <= 5_000_000:
                score += 10
        
        elif self.strategy == "momentum_breakout":
            if token.price_change_1h > 20 and token.price_change_5m > 5:
                score += 30  # Momentum building
        
        # Narrative fit
        dip_quality = token.__dict__.get('dip_quality', 0)
        if dip_quality > 50:
            score += dip_quality / 5  # Up to +20 points
        
        return max(0, min(100, score))
    
    def _score_alpha(self, token: Token) -> float:
        """Score early detection advantage (0-100)."""
        score = 30.0  # Base
        
        # Number of sources found this
        num_sources = len(token.sources)
        if num_sources >= 3:
            score += 25  # Multi-source discovery
        elif num_sources == 2:
            score += 15
        else:
            score += 5
        
        # Age (younger = more alpha)
        age_hours = token.__dict__.get('age_hours')
        if age_hours is not None:
            if age_hours < 1:
                score += 30  # First hour = highest alpha
            elif age_hours < 6:
                score += 20
            elif age_hours < 24:
                score += 10
        
        # Source diversity bonus
        unique_sources = set(token.sources)
        if 'pumpfun' in unique_sources and token.__dict__.get('age_hours', 0) < 6:
            score += 10  # Early PumpFun detection
        
        # Twitter/social not yet discovered (implied by low holders)
        if token.holders < 200:
            score += 10  # Potentially undiscovered
        
        return max(0, min(100, score))
    
    def _score_risk(self, token: Token) -> float:
        """Score risk level (0-100, subtracted from total)."""
        score = 30.0  # Base risk level
        
        # Liquidity risk
        if token.liquidity > 0:
            liq_ratio = token.liquidity / token.market_cap
            if liq_ratio < 0.03:
                score += 30  # High liquidity risk
            elif liq_ratio < 0.1:
                score += 15
        else:
            score += 25  # Unknown liquidity = higher risk
        
        # Extreme volatility
        if abs(token.price_change_24h) > 200:
            score += 20  # Very volatile
        elif abs(token.price_change_1h) > 100:
            score += 15
        
        # Low transaction count (dead token)
        if token.txns_24h < 10:
            score += 20
        elif token.txns_24h < 50:
            score += 10
        
        # Sell pressure
        if token.buys_24h + token.sells_24h > 0:
            sell_ratio = token.sells_24h / (token.buys_24h + token.sells_24h)
            if sell_ratio > 0.7:
                score += 15  # Heavy selling
        
        # Extreme MC (too small = risky)
        if token.market_cap < 50_000:
            score += 15  # Very small
        
        return max(0, min(100, score))
    
    def _score_effort(self, token: Token) -> float:
        """Score effort required to act (0-100, subtracted)."""
        score = 20.0  # Base effort
        
        # Time sensitivity (more urgent = higher effort to catch)
        age_hours = token.__dict__.get('age_hours')
        if age_hours is not None:
            if age_hours < 1:
                score += 10  # Need to act fast
            elif age_hours > 24:
                score -= 10  # Can research more
        
        # Complexity (fewer holders = easier research)
        if token.holders > 5000:
            score += 10  # More research needed
        
        # Unknown age = higher effort
        if age_hours is None:
            score += 5
        
        return max(0, min(100, score))
    
    def get_top_opportunities(self, 
                            scored_tokens: List[Tuple[Token, float, ScoreBreakdown]],
                            min_score: float = 75,
                            max_results: int = 10) -> List[Tuple[Token, float, ScoreBreakdown]]:
        """Get top opportunities above threshold."""
        filtered = [(t, s, b) for t, s, b in scored_tokens if s >= min_score]
        return filtered[:max_results]
    
    def explain_score(self, breakdown: ScoreBreakdown) -> str:
        """Generate human-readable explanation of score."""
        parts = []
        
        if breakdown.potential > 70:
            parts.append("High upside potential")
        if breakdown.probability > 70:
            parts.append("Strong volume/interest signals")
        if breakdown.speed > 70:
            parts.append("Time-sensitive opportunity")
        if breakdown.fit > 70:
            parts.append("Excellent strategy match")
        if breakdown.alpha > 70:
            parts.append("Early detection advantage")
        if breakdown.risk > 60:
            parts.append("⚠️ Higher risk - size carefully")
        
        return " | ".join(parts) if parts else "Moderate opportunity"


if __name__ == "__main__":
    # Test scorer
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Opportunity Scorer v2.0...")
    print("=" * 60)
    
    # Create test token
    test_token = Token(
        address="TEST123",
        symbol="TEST",
        name="Test Token AI",
        chain_id="solana",
        price=0.001,
        market_cap=500_000,
        liquidity=150_000,
        volume_24h=200_000,
        volume_1h=15_000,
        volume_5m=5_000,
        price_change_1h=-12,
        price_change_24h=45,
        price_change_5m=3,
        txns_24h=850,
        buys_24h=520,
        sells_24h=330,
        holders=1_200,
        source="test"
    )
    
    # Add enrichment data
    test_token.__dict__['age_hours'] = 3
    test_token.__dict__['vol_spike_5m'] = 4.0
    test_token.__dict__['narratives'] = ['ai', 'meme']
    test_token.__dict__['dip_quality'] = 60
    test_token.sources = ['dexscreener', 'birdeye']
    
    # Score
    scorer = OpportunityScorer(strategy="mean_reversion_microcap")
    score, breakdown = scorer.score(test_token)
    
    print(f"\n📊 Test Token Score: {score:.1f}/100")
    print(f"\nBreakdown:")
    for key, value in breakdown.to_dict().items():
        if key != 'total':
            weight = scorer.weights[key] * 100
            print(f"  {key:12} {value:5.1f} (weight: {weight:.0f}%)")
    
    print(f"\n✅ Total: {score:.1f}")
    print(f"📝 {scorer.explain_score(breakdown)}")
