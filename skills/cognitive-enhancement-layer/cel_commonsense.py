#!/usr/bin/env python3
"""
CEL-Commonsense: World Knowledge + Contextual Inference
Addresses: "No common sense - I miss obvious things humans see"

ACA Implementation - Phase 6: Commonsense Module
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

sys.path.insert(0, '/home/skux/.openclaw/workspace')


class CELCommonsense:
    """
    Provides commonsense reasoning through:
    - World knowledge base
    - Physical intuition simulation
    - Social reasoning
    - Contextual inference
    - Obvious thing detection
    """
    
    def __init__(self):
        self.commonsense_kb = self._load_commonsense_kb()
        self.physical_rules = self._load_physical_rules()
        self.social_norms = self._load_social_norms()
        self.context_cache = {}
        
    def _load_commonsense_kb(self) -> Dict:
        """Load commonsense knowledge base."""
        return {
            'time': {
                'morning': '6:00-12:00, people wake up, markets open',
                'afternoon': '12:00-18:00, work hours, high activity',
                'evening': '18:00-22:00, dinner, markets close',
                'night': '22:00-6:00, sleep, low liquidity'
            },
            'markets': {
                'weekend': 'Markets less active, lower volume',
                'monday': 'Often volatile, weekend news priced in',
                'friday': 'Can be unpredictable, weekend risk off',
                'holiday': 'Low liquidity, higher spreads, avoid trading'
            },
            'trading': {
                'fomo': 'Fear of missing out leads to bad entries',
                'fud': 'Fear uncertainty doubt causes selling',
                'pump': 'Unsustainable price increase, usually dumps',
                'dump': 'Rapid price decrease, often overshoots',
                'rug': 'Developers abandon project, steal funds',
                'whale': 'Large holder, can move markets'
            },
            'risk': {
                'all_in': 'Never risk everything on one trade',
                'diversification': 'Spread risk across multiple positions',
                'stop_loss': 'Always have exit plan before entering',
                'greed': 'Taking profits is ok, dont get greedy'
            },
            'technology': {
                'api_down': 'Have fallback data sources',
                'latency': 'Fast execution matters in volatile markets',
                'bugs': 'Test thoroughly before live trading',
                'security': 'Protect keys, use hardware wallets'
            }
        }
    
    def _load_physical_rules(self) -> Dict:
        """Load physical intuition rules."""
        return {
            'momentum': {
                'description': 'Objects in motion tend to stay in motion',
                'trading': 'Trends continue until acted upon by force',
                'examples': ['Price moving up tends to keep moving up', 'Volume begets volume']
            },
            'inertia': {
                'description': 'Resistance to change in motion',
                'trading': 'Markets resist changing direction',
                'examples': ['Support levels hold multiple tests', 'Trends dont reverse instantly']
            },
            'gravity': {
                'description': 'What goes up must come down',
                'trading': 'Unsustainable pumps always correct',
                'examples': ['Parabolic moves crash', 'Mean reversion exists']
            },
            'friction': {
                'description': 'Resistance to movement',
                'trading': 'Fees, slippage, spreads reduce returns',
                'examples': ['High fees eat profits', 'Large trades move price']
            }
        }
    
    def _load_social_norms(self) -> Dict:
        """Load social reasoning norms."""
        return {
            'communication': {
                'be_honest': 'Admit limitations and uncertainties',
                'be_clear': 'Avoid jargon when possible',
                'be_respectful': 'Value users time and goals',
                'be_helpful': 'Prioritize user success over showing off'
            },
            'collaboration': {
                'ask_clarification': 'When requirements unclear, ask',
                'provide_options': 'Give alternatives when possible',
                'explain_tradeoffs': 'Every choice has costs',
                'respect_decisions': 'User has final say'
            },
            'safety': {
                'warn_risks': 'Always disclose dangers',
                'suggest_verification': 'Important things need double-check',
                'avoid_harm': 'Dont enable dangerous behavior',
                'protect_privacy': 'Sensitive data needs protection'
            }
        }
    
    def process(self, user_input: str, context: Dict = None,
                analysis: Dict = None) -> str:
        """
        Main processing entry point.
        
        Returns commonsense inferences and contextual grounding.
        """
        inferences = []
        
        # Check for temporal context
        temporal = self._infer_temporal_context(user_input)
        if temporal:
            inferences.append(temporal)
        
        # Check for market context
        market = self._infer_market_context(user_input)
        if market:
            inferences.append(market)
        
        # Check for risk context
        risk = self._infer_risk_context(user_input)
        if risk:
            inferences.append(risk)
        
        # Check for obvious things
        obvious = self._check_obvious_things(user_input)
        if obvious:
            inferences.append(obvious)
        
        # Check physical intuition
        physical = self._apply_physical_intuition(user_input)
        if physical:
            inferences.append(physical)
        
        if inferences:
            return "**Contextual Insights:**\n\n" + "\n\n".join(inferences)
        
        return ""
    
    def _infer_temporal_context(self, text: str) -> Optional[str]:
        """Infer temporal context."""
        import re
        
        # Check for time references
        time_patterns = {
            r'\bmorning\b': 'Morning (6-12): Markets opening, can be volatile',
            r'\bafternoon\b': 'Afternoon (12-18): Active trading hours',
            r'\bevening\b': 'Evening (18-22): Markets closing, lower volume',
            r'\bnight\b': 'Night (22-6): Low liquidity, wider spreads',
            r'\bweekend\b': 'Weekend: Reduced activity, avoid major trades',
            r'\bmonday\b': 'Monday: Often volatile, weekend news impact',
            r'\bfriday\b': 'Friday: Weekend risk-off, can be choppy'
        }
        
        for pattern, inference in time_patterns.items():
            if re.search(pattern, text.lower()):
                return f"⏰ **Time Context:** {inference}"
        
        return None
    
    def _infer_market_context(self, text: str) -> Optional[str]:
        """Infer market context."""
        text_lower = text.lower()
        
        # Check for market conditions
        if 'pump' in text_lower and 'buy' in text_lower:
            return "📈 **Market Context:** Buying into pumps is risky. What goes up fast often comes down fast. Consider waiting for pullback."
        
        if 'fomo' in text_lower or 'missed' in text_lower:
            return "😰 **Psychology:** FOMO leads to bad entries. There will always be another opportunity. Patience > regret."
        
        if 'rug' in text_lower or 'scam' in text_lower:
            return "⚠️ **Safety:** If something feels like a rug, it probably is. Red flags: anonymous team, unrealistic promises, no utility."
        
        if 'whale' in text_lower:
            return "🐋 **Market Dynamics:** Whales can move prices but also create opportunities. Watch for accumulation vs distribution patterns."
        
        return None
    
    def _infer_risk_context(self, text: str) -> Optional[str]:
        """Infer risk context."""
        text_lower = text.lower()
        
        risk_signals = []
        
        if 'all in' in text_lower or 'everything' in text_lower:
            risk_signals.append("Never risk everything on one trade")
        
        if 'guaranteed' in text_lower or 'cant lose' in text_lower:
            risk_signals.append("Nothing is guaranteed in trading")
        
        if 'borrow' in text_lower or 'loan' in text_lower:
            risk_signals.append("Never trade with borrowed money")
        
        if 'life savings' in text_lower:
            risk_signals.append("Life savings should not be in speculative trades")
        
        if risk_signals:
            return "🛡️ **Risk Warning:**\n" + "\n".join(f"• {signal}" for signal in risk_signals)
        
        return None
    
    def _check_obvious_things(self, text: str) -> Optional[str]:
        """Check for things that might be obvious to humans but not AI."""
        text_lower = text.lower()
        
        obvious_checks = [
            # If asking about API without keys
            ('api' in text_lower and 'key' not in text_lower and 'without' not in text_lower,
             "🔑 **Obvious:** API calls need authentication keys. Check if keys are configured."),
            
            # If talking about live trading without mentioning risk
            ('live' in text_lower and 'trade' in text_lower and 'risk' not in text_lower,
             "⚠️ **Obvious:** Live trading = real money at risk. Have you tested this strategy?"),
            
            # If asking about profits without costs
            ('profit' in text_lower and 'fee' not in text_lower and 'cost' not in text_lower,
             "💰 **Obvious:** Remember to account for fees, slippage, and taxes in profit calculations."),
            
            # If talking about 100% win rate
            ('100%' in text_lower or 'always win' in text_lower,
             "📊 **Obvious:** No strategy wins 100%. Losses are part of trading. Risk management matters most."),
            
            # If asking to predict exact prices
            ('predict' in text_lower and 'price' in text_lower and 'exact' in text_lower,
             "🔮 **Obvious:** Exact price prediction is impossible. Probabilities and ranges are more realistic."),
        ]
        
        for condition, message in obvious_checks:
            if condition:
                return message
        
        return None
    
    def _apply_physical_intuition(self, text: str) -> Optional[str]:
        """Apply physical intuition to trading concepts."""
        text_lower = text.lower()
        
        # Momentum
        if 'momentum' in text_lower or 'trend' in text_lower:
            return "🔄 **Physical Analogy:** Like momentum in physics, price trends tend to continue until acted upon by external forces (news, volume shifts, resistance levels)."
        
        # Gravity/mean reversion
        if 'pump' in text_lower or 'parabolic' in text_lower:
            return "🍎 **Physical Analogy:** Like gravity, extreme price moves tend to return to average. Unsustainable pumps usually correct."
        
        # Inertia/support
        if 'support' in text_lower or 'resistance' in text_lower:
            return "⚖️ **Physical Analogy:** Like inertia, prices resist changing direction at support/resistance. Multiple tests often needed to break through."
        
        # Friction/costs
        if 'fee' in text_lower or 'slippage' in text_lower:
            return "🛑 **Physical Analogy:** Like friction, trading costs reduce momentum. High fees make it harder to profit from small moves."
        
        return None
    
    def add_commonsense_fact(self, category: str, key: str, value: str):
        """Add new commonsense fact."""
        if category not in self.commonsense_kb:
            self.commonsense_kb[category] = {}
        self.commonsense_kb[category][key] = value
    
    def get_commonsense(self, category: str, key: str) -> Optional[str]:
        """Retrieve commonsense fact."""
        return self.commonsense_kb.get(category, {}).get(key)


if __name__ == "__main__":
    # Test CEL-Commonsense
    print("🌍 Testing CEL-Commonsense (Commonsense Module)...")
    
    commonsense = CELCommonsense()
    
    test_inputs = [
        "I want to buy this token that just pumped 200%",
        "Should I go all in on this trade?",
        "The API keeps failing",
        "This strategy has 100% win rate",
        "The price is showing strong momentum"
    ]
    
    for test_input in test_inputs:
        print(f"\n{'='*60}")
        print(f"Input: {test_input}")
        result = commonsense.process(test_input)
        if result:
            print(f"Result: {result}")
        else:
            print("Result: No specific commonsense inference")
    
    print(f"\n{'='*60}")
    print("CEL-Commonsense module ready!")
