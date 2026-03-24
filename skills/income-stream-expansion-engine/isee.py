#!/usr/bin/env python3
"""
ISEE - Income Stream Expansion Engine v1.0
The "find new money" engine that continuously expands income portfolios.

Architecture:
    Market Scanner → Niche Analyzer → Competition Evaluator → 
    Workflow Builder → Proposal Generator

Integration:
    ISEE → ARAS (scoring) → ACA (building) → ALOE (learning) → SEE (optimizing)
"""

import json
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Paths - must exist before logging
def setup_logging():
    """Setup logging after paths exist."""
    workspace_dir = Path('/home/skux/.openclaw/workspace')
    memory_dir = workspace_dir / 'memory' / 'isee'
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/home/skux/.openclaw/workspace/memory/isee/isee.log')
        ]
    )
    return memory_dir

MEMORY_DIR = setup_logging()
logger = logging.getLogger('ISEE')

# Paths
WORKSPACE_DIR = Path('/home/skux/.openclaw/workspace')
SKILL_DIR = WORKSPACE_DIR / 'skills' / 'income-stream-expansion-engine'


@dataclass
class Opportunity:
    """Income opportunity data structure."""
    id: str
    name: str
    category: str
    description: str
    market_size: str
    competition: str
    barrier: str
    time_to_revenue: str
    effort_required: str
    skill_requirements: List[str]
    potential_monthly: int
    confidence: int
    source: str
    discovered_at: str
    status: str = 'discovered'
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IncomeProposal:
    """Complete income stream proposal."""
    id: str
    opportunity_id: str
    title: str
    business_case: str
    roi_projection: Dict[str, Any]
    timeline: Dict[str, Any]
    resources: Dict[str, Any]
    workflow: Dict[str, Any]
    risks: List[str]
    metrics: Dict[str, Any]
    created_at: str
    status: str = 'pending'
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IncomeStreamExpansionEngine:
    """Main ISEE engine that discovers and builds new income streams."""
    
    def __init__(self):
        self.opportunities: List[Opportunity] = []
        self.proposals: List[IncomeProposal] = []
        self.load_state()
        
        # Initialize sub-modules
        from market_scanner import MarketScanner
        from niche_analyzer import NicheAnalyzer
        from competition_evaluator import CompetitionEvaluator
        from workflow_builder import WorkflowBuilder
        from proposal_generator import ProposalGenerator
        
        self.market_scanner = MarketScanner()
        self.niche_analyzer = NicheAnalyzer()
        self.competition_evaluator = CompetitionEvaluator()
        self.workflow_builder = WorkflowBuilder()
        self.proposal_generator = ProposalGenerator()
    
    def load_state(self):
        """Load existing opportunities and proposals."""
        opp_file = MEMORY_DIR / 'opportunities.json'
        if opp_file.exists():
            with open(opp_file) as f:
                data = json.load(f)
                self.opportunities = [Opportunity(**opp) for opp in data.get('opportunities', [])]
                logger.info(f"Loaded {len(self.opportunities)} existing opportunities")
        
        prop_file = MEMORY_DIR / 'proposals.json'
        if prop_file.exists():
            with open(prop_file) as f:
                data = json.load(f)
                self.proposals = [IncomeProposal(**prop) for prop in data.get('proposals', [])]
                logger.info(f"Loaded {len(self.proposals)} existing proposals")
    
    def save_state(self):
        """Save current state to disk."""
        opp_file = MEMORY_DIR / 'opportunities.json'
        with open(opp_file, 'w') as f:
            json.dump({
                'updated_at': datetime.now().isoformat(),
                'opportunities': [opp.to_dict() for opp in self.opportunities]
            }, f, indent=2)
        
        prop_file = MEMORY_DIR / 'proposals.json'
        with open(prop_file, 'w') as f:
            json.dump({
                'updated_at': datetime.now().isoformat(),
                'proposals': [prop.to_dict() for prop in self.proposals]
            }, f, indent=2)
    
    def scan_markets(self, focus: Optional[str] = None) -> List[Opportunity]:
        """Scan all markets for new income opportunities."""
        logger.info("=" * 70)
        logger.info("🔥 ISEE - INCOME STREAM EXPANSION ENGINE")
        logger.info("=" * 70)
        logger.info(f"\n📡 Starting market scan (focus: {focus or 'all'})...")
        
        discovered = self.market_scanner.scan(focus=focus)
        
        existing_ids = {opp.id for opp in self.opportunities}
        new_opportunities = [opp for opp in discovered if opp.id not in existing_ids]
        
        logger.info(f"\n✅ Scan complete!")
        logger.info(f"   Discovered: {len(discovered)} opportunities")
        logger.info(f"   New (unique): {len(new_opportunities)} opportunities")
        
        self.opportunities.extend(new_opportunities)
        self.save_state()
        
        if new_opportunities:
            logger.info(f"\n🎯 TOP NEW OPPORTUNITIES:")
            for opp in sorted(new_opportunities, key=lambda x: x.confidence, reverse=True)[:5]:
                logger.info(f"   [{opp.category.upper()}] {opp.name}")
                logger.info(f"      Potential: ${opp.potential_monthly}/mo | Confidence: {opp.confidence}%")
        
        return new_opportunities
    
    def analyze_opportunity(self, opportunity_id: str) -> Dict[str, Any]:
        """Deep analysis of a specific opportunity."""
        opp = next((o for o in self.opportunities if o.id == opportunity_id), None)
        if not opp:
            logger.error(f"Opportunity {opportunity_id} not found")
            return {}
        
        logger.info(f"\n🔍 Analyzing opportunity: {opp.name}")
        
        niche_data = self.niche_analyzer.analyze(opp)
        competition_data = self.competition_evaluator.evaluate(opp)
        
        analysis = {
            'opportunity': opp.to_dict(),
            'niche_analysis': niche_data,
            'competition': competition_data,
            'arass_score': self._calculate_arass_score(opp, niche_data, competition_data),
            'analyzed_at': datetime.now().isoformat()
        }
        
        opp.status = 'analyzed'
        self.save_state()
        
        logger.info(f"✅ Analysis complete for {opp.name}")
        logger.info(f"   ARAS Score: {analysis['arass_score']}/100")
        
        return analysis
    
    def _calculate_arass_score(self, opp: Opportunity, niche: Dict, comp: Dict) -> int:
        """Calculate ARAS-style score for opportunity."""
        score = 0
        
        # Potential (30 points)
        if opp.potential_monthly >= 5000:
            score += 30
        elif opp.potential_monthly >= 2000:
            score += 20
        elif opp.potential_monthly >= 500:
            score += 10
        
        # Probability (25 points)
        if opp.confidence >= 80:
            score += 25
        elif opp.confidence >= 60:
            score += 15
        else:
            score += 5
        
        # Speed (20 points)
        if opp.time_to_revenue == 'days':
            score += 20
        elif opp.time_to_revenue == 'weeks':
            score += 15
        elif opp.time_to_revenue == 'months':
            score += 10
        
        # Fit (15 points)
        required_skills = len(opp.skill_requirements)
        if required_skills <= 3:
            score += 15
        elif required_skills <= 5:
            score += 10
        else:
            score += 5
        
        # Alpha (10 points)
        if opp.competition == 'low':
            score += 10
        elif opp.competition == 'medium':
            score += 5
        
        return min(score, 100)
    
    def generate_proposal(self, opportunity_id: str) -> Optional[IncomeProposal]:
        """Generate complete income proposal for opportunity."""
        opp = next((o for o in self.opportunities if o.id == opportunity_id), None)
        if not opp:
            logger.error(f"Opportunity {opportunity_id} not found")
            return None
        
        logger.info(f"\n📋 Generating proposal for: {opp.name}")
        
        analysis = self.analyze_opportunity(opportunity_id)
        if not analysis:
            return None
        
        proposal = self.proposal_generator.create(opp, analysis)
        workflow = self.workflow_builder.build(opp, proposal)
        proposal.workflow = workflow
        
        self.proposals.append(proposal)
        opp.status = 'proposed'
        self.save_state()
        
        logger.info(f"✅ Proposal generated: {proposal.id}")
        logger.info(f"   Projected monthly: ${proposal.roi_projection.get('monthly', 0)}")
        
        return proposal
    
    def build_workflow(self, proposal_id: str) -> bool:
        """Execute ACA to build the actual workflow."""
        proposal = next((p for p in self.proposals if p.id == proposal_id), None)
        if not proposal:
            logger.error(f"Proposal {proposal_id} not found")
            return False
        
        logger.info(f"\n🔨 Building workflow for: {proposal.title}")
        
        success = self.workflow_builder.execute(proposal)
        
        if success:
            proposal.status = 'building'
            opp = next((o for o in self.opportunities if o.id == proposal.opportunity_id), None)
            if opp:
                opp.status = 'building'
            self.save_state()
            logger.info(f"✅ Workflow built successfully")
        else:
            logger.error(f"❌ Workflow build failed")
        
        return success
    
    def get_portfolio_report(self) -> Dict[str, Any]:
        """Generate complete income portfolio report."""
        active = [o for o in self.opportunities if o.status in ['building', 'active']]
        proposed = [o for o in self.opportunities if o.status == 'proposed']
        discovered = [o for o in self.opportunities if o.status == 'discovered']
        
        by_category = {}
        for opp in self.opportunities:
            cat = opp.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(opp)
        
        total_potential = sum(o.potential_monthly for o in active)
        
        return {
            'summary': {
                'total_opportunities': len(self.opportunities),
                'active_streams': len(active),
                'proposed': len(proposed),
                'discovered': len(discovered),
                'total_proposals': len(self.proposals),
                'monthly_potential': total_potential
            },
            'by_category': {k: len(v) for k, v in by_category.items()},
            'top_opportunities': [
                o.to_dict() for o in sorted(
                    self.opportunities,
                    key=lambda x: x.confidence * x.potential_monthly,
                    reverse=True
                )[:10]
            ]
        }
    
    def run_full_cycle(self):
        """Run complete ISEE cycle: Scan → Analyze → Propose."""
        logger.info("\n" + "=" * 70)
        logger.info("🔄 RUNNING FULL ISEE CYCLE")
        logger.info("=" * 70)
        
        new_opps = self.scan_markets()
        
        if not new_opps:
            logger.info("\n⚠️  No new opportunities discovered")
            return
        
        top_opps = sorted(new_opps, key=lambda x: x.confidence, reverse=True)[:3]
        
        for opp in top_opps:
            self.analyze_opportunity(opp.id)
        
        best = top_opps[0]
        proposal = self.generate_proposal(best.id)
        
        if proposal:
            logger.info("\n" + "=" * 70)
            logger.info("🎯 TOP PROPOSAL READY")
            logger.info("=" * 70)
            logger.info(f"   Proposal ID: {proposal.id}")
            logger.info(f"   Run: python3 isee.py --mode build --id {proposal.id}")
        
        self.save_state()
        report = self.get_portfolio_report()
        
        logger.info("\n📊 PORTFOLIO STATUS")
        logger.info(f"   Total: {report['summary']['total_opportunities']}")
        logger.info(f"   Active: {report['summary']['active_streams']}")
        logger.info(f"   Monthly Potential: ${report['summary']['monthly_potential']:,}")


def main():
    """CLI interface for ISEE."""
    parser = argparse.ArgumentParser(description='Income Stream Expansion Engine')
    parser.add_argument('--mode', choices=['scan', 'analyze', 'propose', 'build', 'portfolio', 'cycle'], 
                       default='scan')
    parser.add_argument('--focus', help='Focus on specific category')
    parser.add_argument('--id', help='Opportunity or proposal ID')
    parser.add_argument('--auto-select', action='store_true')
    args = parser.parse_args()
    
    engine = IncomeStreamExpansionEngine()
    
    if args.mode == 'scan':
        engine.scan_markets(focus=args.focus)
    elif args.mode == 'analyze':
        if args.id:
            engine.analyze_opportunity(args.id)
        elif args.auto_select:
            unanalyzed = [o for o in engine.opportunities if o.status == 'discovered']
            if unanalyzed:
                engine.analyze_opportunity(sorted(unanalyzed, key=lambda x: x.confidence, reverse=True)[0].id)
    elif args.mode == 'propose':
        if args.id:
            engine.generate_proposal(args.id)
        elif args.auto_select:
            analyzed = [o for o in engine.opportunities if o.status == 'analyzed']
            if analyzed:
                engine.generate_proposal(sorted(analyzed, key=lambda x: x.confidence, reverse=True)[0].id)
    elif args.mode == 'build':
        if args.id:
            engine.build_workflow(args.id)
    elif args.mode == 'portfolio':
        print(json.dumps(engine.get_portfolio_report(), indent=2))
    elif args.mode == 'cycle':
        engine.run_full_cycle()
    
    return 0


if __name__ == '__main__':
    exit(main())
