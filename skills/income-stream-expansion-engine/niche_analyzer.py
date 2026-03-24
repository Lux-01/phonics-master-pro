#!/usr/bin/env python3
"""
ISEE Niche Analyzer
Analyzes market niches for income opportunities.
"""

import logging
from typing import Dict, Any
from isee import Opportunity

logger = logging.getLogger('ISEE.NicheAnalyzer')


class NicheAnalyzer:
    """
    Analyzes market niches for income opportunities.
    Provides market sizing, growth trends, and barrier assessment.
    """
    
    def __init__(self):
        self.market_sizing_db = {
            'small': {'min': 1000, 'max': 10000, 'growth': 'niche'},
            'medium': {'min': 10000, 'max': 100000, 'growth': 'steady'},
            'large': {'min': 100000, 'max': 1000000, 'growth': 'strong'},
            'massive': {'min': 1000000, 'max': 10000000, 'growth': 'explosive'}
        }
    
    def analyze(self, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Analyze the niche for an opportunity.
        
        Args:
            opportunity: Opportunity to analyze
            
        Returns:
            Niche analysis data
        """
        logger.info(f"   Analyzing niche: {opportunity.name}")
        
        market_data = self.market_sizing_db.get(opportunity.market_size, {})
        
        # Calculate total addressable market
        tam = self._estimate_tam(opportunity)
        sam = tam * 0.1  # Serviceable addressable market
        som = sam * 0.05  # Serviceable obtainable market
        
        # Growth trajectory
        growth = self._estimate_growth(opportunity)
        
        # Market saturation
        saturation = self._estimate_saturation(opportunity)
        
        # Entry barriers
        barriers = self._analyze_barriers(opportunity)
        
        # Time to significant revenue
        time_to_significant = self._estimate_time_to_significant(opportunity)
        
        return {
            'market_size': {
                'category': opportunity.market_size,
                'tam': tam,
                'sam': sam,
                'som': som
            },
            'growth': {
                'rate': growth,
                'trajectory': 'upward' if growth > 10 else 'stable',
                'prediction': self._growth_prediction(growth)
            },
            'saturation': saturation,
            'barriers': barriers,
            'time_to_significant_revenue': time_to_significant,
            'profit_potential': self._estimate_profit_potential(opportunity),
            'recommendation': self._generate_recommendation(opportunity, saturation, barriers)
        }
    
    def _estimate_tam(self, opp: Opportunity) -> int:
        """Estimate Total Addressable Market."""
        base = {
            'small': 100000,
            'medium': 1000000,
            'large': 10000000,
            'massive': 100000000
        }
        return base.get(opp.market_size, 100000)
    
    def _estimate_growth(self, opp: Opportunity) -> int:
        """Estimate market growth rate (% per year)."""
        growth_rates = {
            'ai': 35,
            'crypto': 25,
            'content': 15,
            'digital-products': 20,
            'services': 18
        }
        return growth_rates.get(opp.category, 10)
    
    def _estimate_saturation(self, opp: Opportunity) -> str:
        """Estimate market saturation level."""
        if opp.competition == 'high':
            return 'high'
        if opp.barrier == 'low':
            return 'medium'
        return 'low'
    
    def _analyze_barriers(self, opp: Opportunity) -> Dict[str, Any]:
        """Analyze entry barriers."""
        barriers = {
            'technical': len([s for s in opp.skill_requirements if s in ['python', 'ai', 'programming']]),
            'capital': 'high' if opp.barrier == 'high' else 'low',
            'regulatory': 'medium' if opp.category == 'crypto' else 'low',
            'network': 'medium' if opp.category == 'services' else 'low',
            'time': opp.time_to_revenue
        }
        return barriers
    
    def _estimate_time_to_significant(self, opp: Opportunity) -> str:
        """Estimate time to significant revenue ($1000+/mo)."""
        if opp.potential_monthly >= 1000 and opp.time_to_revenue == 'weeks':
            return '1-3 months'
        if opp.time_to_revenue == 'months':
            return '3-6 months'
        return '1-2 months'
    
    def _estimate_profit_potential(self, opp: Opportunity) -> Dict[str, Any]:
        """Estimate profit margins and potential."""
        margins = {
            'digital-products': 0.85,
            'content': 0.80,
            'services': 0.70,
            'crypto': 0.50,
            'ai': 0.75
        }
        
        margin = margins.get(opp.category, 0.60)
        
        return {
            'gross_margin': int(margin * 100),
            'net_margin_estimate': int(margin * 0.7 * 100),
            'monthly_profit_potential': int(opp.potential_monthly * margin),
            'scaling_potential': 'high' if margin > 0.70 else 'medium'
        }
    
    def _growth_prediction(self, growth_rate: int) -> str:
        """Predict future growth trajectory."""
        if growth_rate > 30:
            return 'expanding rapidly'
        if growth_rate > 15:
            return 'growing steadily'
        return 'mature market'
    
    def _generate_recommendation(self, opp: Opportunity, saturation: str, barriers: Dict) -> str:
        """Generate strategic recommendation."""
        if opp.confidence >= 80 and opp.barrier == 'low':
            return 'PURSUE IMMEDIATELY - High confidence, low barrier'
        if opp.confidence >= 70 and saturation == 'low':
            return 'STRONG CANDIDATE - Underserved niche'
        if opp.barrier == 'high' and opp.potential_monthly < 1000:
            return 'LOW PRIORITY - High effort for low return'
        return 'EVALUATE - Consider against alternatives'
