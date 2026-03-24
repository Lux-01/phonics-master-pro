#!/usr/bin/env python3
"""
ISEE Competition Evaluator
Analyzes competitive landscape for opportunities.
"""

import logging
from typing import Dict, Any, List
from isee import Opportunity

logger = logging.getLogger('ISEE.CompetitionEvaluator')


class CompetitionEvaluator:
    """
    Evaluates competitive landscape for income opportunities.
    Identifies differentiation opportunities and underserved segments.
    """
    
    def __init__(self):
        self.competition_db = self._load_competition_data()
    
    def _load_competition_data(self) -> Dict[str, Dict]:
        """Load competitive landscape data."""
        return {
            'digital-products': {
                'notion-templates': {
                    'competitors': 5000,
                    'leaders': ['Notion.so', 'Template Market'],
                    'price_point': '10-50 USD',
                    'saturation': 'high'
                },
                'ai-scripts': {
                    'competitors': 200,
                    'leaders': ['OpenAI marketplace', 'Custom dev shops'],
                    'price_point': '50-500 USD',
                    'saturation': 'medium'
                }
            },
            'services': {
                'ai-consulting': {
                    'competitors': 10000,
                    'leaders': ['Big 4 consultancies', 'AI agencies'],
                    'price_point': '150-500/hr',
                    'saturation': 'medium'
                },
                'cv-optimization': {
                    'competitors': 50000,
                    'leaders': ['TopResume', 'LinkedIn ProFinder'],
                    'price_point': '50-200 USD',
                    'saturation': 'high'
                }
            }
        }
    
    def evaluate(self, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Evaluate competition for an opportunity.
        
        Args:
            opportunity: Opportunity to evaluate
            
        Returns:
            Competition analysis
        """
        logger.info(f"   Evaluating competition: {opportunity.name}")
        
        # Get competition data
        comp_data = self._get_competition_data(opportunity)
        
        # Calculate differentiation opportunities
        differentiation = self._find_differentiation(opportunity, comp_data)
        
        # Identify underserved segments
        gaps = self._find_gaps(opportunity, comp_data)
        
        # Price positioning
        pricing = self._analyze_pricing(opportunity, comp_data)
        
        # Competitive advantage assessment
        advantages = self._assess_advantages(opportunity, comp_data)
        
        return {
            'competition_level': opportunity.competition,
            'competitor_count': comp_data.get('competitors', 'unknown'),
            'market_leaders': comp_data.get('leaders', []),
            'saturation': comp_data.get('saturation', 'unknown'),
            'differentiation_opportunities': differentiation,
            'market_gaps': gaps,
            'pricing_analysis': pricing,
            'competitive_advantages': advantages,
            'recommendation': self._competitive_recommendation(
                opportunity, comp_data, differentiation
            )
        }
    
    def _get_competition_data(self, opp: Opportunity) -> Dict:
        """Get competition data for opportunity."""
        # Simplified lookup - would use SIL in production
        defaults = {
            'competitors': 1000,
            'leaders': ['Various providers'],
            'price_point': 'variable',
            'saturation': 'medium'
        }
        
        # Check if we have specific data
        cat_data = self.competition_db.get(opp.category, {})
        for key in cat_data:
            if key.lower() in opp.name.lower():
                return cat_data[key]
        
        return defaults
    
    def _find_differentiation(self, opp: Opportunity, comp: Dict) -> List[str]:
        """Find differentiation opportunities."""
        opportunities = []
        
        # AI angle
        if 'ai' in str(opp.skill_requirements).lower():
            opportunities.append('AI-powered automation and personalization')
        
        # Automation angle
        if opp.category in ['services', 'digital-products']:
            opportunities.append('Fully automated delivery vs manual')
        
        # Niche angle
        if opp.market_size == 'small':
            opportunities.append('Hyper-specialization in underserved sub-niche')
        
        # Speed angle
        if opp.time_to_revenue == 'days':
            opportunities.append('Rapid turnaround time')
        
        return opportunities if opportunities else ['Price competition (race to bottom)']
    
    def _find_gaps(self, opp: Opportunity, comp: Dict) -> List[str]:
        """Find market gaps and underserved segments."""
        gaps = []
        
        # SMB gap
        gaps.append('Small-to-medium business segment (underserved)')
        
        # Geographic gaps
        gaps.append('Non-US English speaking markets')
        
        # Integration gaps
        if opp.category == 'ai':
            gaps.append('Enterprise integration services')
        
        # Educational gaps
        if opp.category == 'digital-products':
            gaps.append('Done-with-you vs done-for-you')
        
        return gaps[:3]
    
    def _analyze_pricing(self, opp: Opportunity, comp: Dict) -> Dict[str, Any]:
        """Analyze pricing strategy."""
        current_price = opp.potential_monthly
        
        return {
            'market_range': comp.get('price_point', 'unknown'),
            'recommended_strategy': 'value-based' if opp.barrier == 'high' else 'volume-based',
            'premium_potential': current_price * 1.5 if opp.barrier == 'high' else current_price,
            'lowest_viable': current_price * 0.7
        }
    
    def _assess_advantages(self, opp: Opportunity, comp: Dict) -> List[str]:
        """Assess competitive advantages based on skills."""
        advantages = []
        
        skill_set = set(s.lower() for s in opp.skill_requirements)
        
        if 'ai' in skill_set:
            advantages.append('AI/automation capabilities (technical moat)')
        
        if 'python' in skill_set or 'programming' in skill_set:
            advantages.append('Custom development capacity')
        
        if opp.confidence >= 80:
            advantages.append('High execution confidence')
        
        if opp.time_to_revenue == 'days':
            advantages.append('Speed to market')
        
        return advantages if advantages else ['Learning curve as temporary moat']
    
    def _competitive_recommendation(self, opp: Opportunity, comp: Dict, diff: List) -> str:
        """Generate competitive strategy recommendation."""
        if opp.competition == 'low':
            return 'FIRST-MOVER ADVANTAGE - Establish position before competition'
        
        if len(diff) >= 2:
            return 'DIFFERENTIATED PLAY - Emphasize unique capabilities'
        
        if opp.barrier == 'high':
            return 'BARRIER DEFENSE - Compete on quality not price'
        
        return 'PRICE COMPETITION - Only if you have cost advantage'
