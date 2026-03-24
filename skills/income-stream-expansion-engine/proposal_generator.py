#!/usr/bin/env python3
"""
ISEE Proposal Generator
Generates complete income stream proposals with business cases.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from isee import Opportunity, IncomeProposal

logger = logging.getLogger('ISEE.ProposalGenerator')


class ProposalGenerator:
    """
    Generates complete income proposals with business cases.
    Uses strategic frameworks for ROI projections and timelines.
    """
    
    def create(self, opportunity: Opportunity, analysis: Dict[str, Any]) -> IncomeProposal:
        """
        Create complete proposal for opportunity.
        
        Args:
            opportunity: The opportunity
            analysis: Niche and competition analysis
            
        Returns:
            Complete IncomeProposal
        """
        logger.info(f"   Generating proposal for: {opportunity.name}")
        
        proposal_id = f"ISEE-PROP-{datetime.now().strftime('%Y%m%d')}-{hash(opportunity.name) % 10000:04d}"
        
        # Build proposal components
        business_case = self._generate_business_case(opportunity, analysis)
        roi = self._calculate_roi(opportunity, analysis)
        timeline = self._generate_timeline(opportunity)
        resources = self._identify_resources(opportunity)
        risks = self._identify_risks(opportunity, analysis)
        metrics = self._define_success_metrics(opportunity)
        
        proposal = IncomeProposal(
            id=proposal_id,
            opportunity_id=opportunity.id,
            title=f"{opportunity.name} Income Stream",
            business_case=business_case,
            roi_projection=roi,
            timeline=timeline,
            resources=resources,
            workflow={},
            risks=risks,
            metrics=metrics,
            created_at=datetime.now().isoformat()
        )
        
        return proposal
    
    def _generate_business_case(self, opp: Opportunity, analysis: Dict) -> str:
        """Generate business case narrative."""
        niche = analysis.get('niche_analysis', {})
        comp = analysis.get('competition', {})
        
        case_parts = [
            f"## Executive Summary",
            f"",
            f"**Opportunity:** {opp.name}",
            f"**Category:** {opp.category}",
            f"**Market Size:** {niche.get('market_size', {}).get('category', 'unknown')}",
            f"**Competition:** {opp.competition}",
            f"",
            f"## Value Proposition",
            f"",
            opp.description,
            f"",
            f"## Market Analysis",
            f"",
            f"- **Total Addressable Market:** ${niche.get('market_size', {}).get('tam', 0):,}",
            f"- **Market Growth:** {niche.get('growth', {}).get('rate', 0)}% annually",
            f"- **Market Saturation:** {niche.get('saturation', 'medium')}",
            f"- **Competitive Landscape:** {comp.get('competition_level', 'medium')}",
            f"",
            f"## Financial Projections",
            f"",
            f"- **Monthly Revenue Potential:** ${opp.potential_monthly:,}",
            f"- **Time to Revenue:** {opp.time_to_revenue}",
            f"- **Confidence Level:** {opp.confidence}%",
            f"",
            f"## Strategic Fit",
            f"",
            f"This opportunity aligns with existing capabilities and represents a "
            f"{opp.market_size} market with {opp.competition} competition. "
            f"The {opp.barrier} barrier to entry provides a defensible position."
        ]
        
        return '\n'.join(case_parts)
    
    def _calculate_roi(self, opp: Opportunity, analysis: Dict) -> Dict[str, Any]:
        """Calculate ROI projections."""
        profit = analysis.get('niche_analysis', {}).get('profit_potential', {})
        
        monthly = opp.potential_monthly
        margin = profit.get('gross_margin', 70) / 100
        net_monthly = int(monthly * margin * 0.7)  # Account for taxes
        
        # Time to break even
        setup_cost = self._estimate_setup_cost(opp)
        break_even_months = max(1, setup_cost // net_monthly) if net_monthly > 0 else 12
        
        # Year projections
        year_1 = net_monthly * 12 * 0.5  # Ramp up
        year_2 = net_monthly * 12 * 0.9  # Steady state
        year_3 = net_monthly * 12  # Optimized
        
        return {
            'monthly_gross': monthly,
            'monthly_net_estimate': net_monthly,
            'margin': profit.get('gross_margin', 70),
            'setup_cost': setup_cost,
            'break_even_months': break_even_months,
            'year_1': int(year_1),
            'year_2': int(year_2),
            'year_3': int(year_3),
            'roi_3_year': int(year_1 + year_2 + year_3 - setup_cost),
            'roi_percentage': int((year_1 + year_2 + year_3 - setup_cost) / max(1, setup_cost) * 100)
        }
    
    def _estimate_setup_cost(self, opp: Opportunity) -> int:
        """Estimate initial setup cost."""
        base_costs = {
            'digital-products': 100,
            'services': 500,
            'content': 200,
            'crypto': 1000,
            'ai': 300
        }
        
        base = base_costs.get(opp.category, 500)
        
        if opp.barrier == 'high':
            base *= 3
        elif opp.barrier == 'medium':
            base *= 2
        
        return int(base)
    
    def _generate_timeline(self, opp: Opportunity) -> Dict[str, Any]:
        """Generate implementation timeline."""
        # Weekly breakdown based on category
        category_weeks = {
            'digital-products': 4,
            'services': 3,
            'content': 6,
            'crypto': 1,
            'ai': 4
        }
        
        total_weeks = category_weeks.get(opp.category, 4)
        
        timeline = {
            'total_weeks': total_weeks,
            'phases': []
        }
        
        # Phase 1: Setup
        timeline['phases'].append({
            'name': 'Setup & Validation',
            'weeks': 1,
            'deliverables': [
                'Market validation confirmed',
                'Resources gathered',
                'Initial workflow created'
            ]
        })
        
        # Phase 2: Build
        timeline['phases'].append({
            'name': 'Build & Create',
            'weeks': max(1, total_weeks - 2),
            'deliverables': [
                f'{opp.category} created',
                'Systems configured',
                'Documentation complete'
            ]
        })
        
        # Phase 3: Launch
        timeline['phases'].append({
            'name': 'Launch & Iterate',
            'weeks': 1,
            'deliverables': [
                'First revenue event',
                'Feedback collected',
                'Iteration plan created'
            ]
        })
        
        return timeline
    
    def _identify_resources(self, opp: Opportunity) -> Dict[str, Any]:
        """Identify required resources."""
        return {
            'skills': opp.skill_requirements,
            'time_commitment': self._estimate_time(opp),
            'tools': self._identify_tools(opp),
            'capital': self._estimate_setup_cost(opp),
            'dependencies': self._identify_dependencies(opp)
        }
    
    def _estimate_time(self, opp: Opportunity) -> str:
        """Estimate weekly time commitment."""
        if opp.effort_required == 'high':
            return '20+ hours/week'
        if opp.effort_required == 'low':
            return '5-10 hours/week'
        return '10-20 hours/week'
    
    def _identify_tools(self, opp: Opportunity) -> List[str]:
        """Identify required tools/software."""
        tools_by_category = {
            'digital-products': ['Notion/Figma', 'Gumroad', 'Email platform'],
            'services': ['Calendly', 'Stripe', 'Project management tool'],
            'content': ['YouTube/Substack', 'Canva', 'Analytics'],
            'crypto': ['Wallet', 'Exchange', 'Monitoring tools'],
            'ai': ['OpenAI API', 'Automation tools', 'Hosting']
        }
        return tools_by_category.get(opp.category, ['Basic tools'])
    
    def _identify_dependencies(self, opp: Opportunity) -> List[str]:
        """Identify external dependencies."""
        deps = []
        if opp.category == 'services':
            deps.append('Client acquisition')
        if opp.category == 'content':
            deps.append('Platform reach (subscribers/followers)')
        if opp.category == 'crypto':
            deps.append('Market conditions')
        return deps if deps else ['None critical']
    
    def _identify_risks(self, opp: Opportunity, analysis: Dict) -> List[str]:
        """Identify risks and mitigations."""
        risks = []
        
        # Market risks
        if opp.market_size == 'small':
            risks.append('Limited market size')
        if opp.competition == 'high':
            risks.append('High competition - price pressure')
        
        # Execution risks
        if opp.barrier == 'high':
            risks.append('Technical complexity')
        if len(opp.skill_requirements) > 3:
            risks.append('Skill gap - may need to outsource')
        
        # Timing risks
        if opp.time_to_revenue == 'months':
            risks.append('Long time to first revenue')
        
        # Market risks  
        risks.append('Market conditions may change')
        risks.append('Execution risk')
        
        return risks if risks else ['Standard execution risk']
    
    def _define_success_metrics(self, opp: Opportunity) -> Dict[str, Any]:
        """Define KPIs for the income stream."""
        return {
            'primary': {
                'metric': 'Monthly Revenue',
                'target': f'${opp.potential_monthly}',
                'timeline': opp.time_to_revenue
            },
            'secondary': [
                'Customer satisfaction (NPS)', 
                'Operational efficiency',
                'Time investment per $ earned'
            ],
            'milestones': [
                {'name': 'First $1', 'timeline': f'{opp.time_to_revenue}'},
                {'name': '$100/month', 'timeline': '2x time to revenue'},
                {'name': '$1000/month', 'timeline': '3x time to revenue'},
                {'name': 'Full target', 'timeline': '6 months'}
            ]
        }
