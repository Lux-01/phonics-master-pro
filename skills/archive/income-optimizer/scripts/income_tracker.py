#!/usr/bin/env python3
"""
Income Tracker - Comprehensive income monitoring and optimization
Tracks MRR, ROI per skill, and generates monthly dashboards.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

class IncomeCategory(Enum):
    TRADING = "trading"
    PRODUCT = "product"
    SERVICE = "service"
    PASSIVE = "passive"
    AFFILIATE = "affiliate"
    OTHER = "other"

class Skill(Enum):
    ATS = "autonomous-trading-strategist"
    AOE = "autonomous-opportunity-engine"
    AWB = "autonomous-workflow-builder"
    ATSKILL = "autonomous-trading-strategist"
    SKYLAR = "skylar-trading-bot"
    WHALE = "wallet-whale-tracker"
    MANUAL = "manual-trading"
    RESEARCH = "research-synthesizer"
    NONE = "none"

@dataclass
class IncomeRecord:
    id: str
    date: datetime
    category: IncomeCategory
    skill: Skill
    source_name: str
    amount_usd: float
    description: str
    tags: List[str]
    verified: bool
    metadata: Dict

@dataclass
class IncomeStream:
    name: str
    category: IncomeCategory
    skill: Skill
    is_recurring: bool
    monthly_average: float
    confidence: float  # 0-1 confidence in monthly prediction
    last_updated: datetime

@dataclass
class SkillROI:
    skill: Skill
    monthly_income: float
    development_hours: float
    monthly_maintenance_hours: float
    hourly_rate: float
    total_investment: float
    total_return: float
    roi_percentage: float

class IncomeTracker:
    """Tracks and optimizes income across all sources."""
    
    def __init__(self, memory_path: str = "/home/skux/.openclaw/workspace/memory"):
        self.memory_path = Path(memory_path)
        self.income_path = self.memory_path / "income"
        self.transactions_path = self.income_path / "transactions"
        self.reports_path = self.income_path / "reports"
        self.streams_file = self.income_path / "streams" / "income_streams.json"
        
        self._ensure_directories()
        self._init_default_streams()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        directories = [
            self.income_path / "streams",
            self.income_path / "transactions",
            self.income_path / "reports" / "monthly",
            self.income_path / "reports" / "quarterly",
            self.income_path / "goals",
            self.income_path / "skills"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _init_default_streams(self):
        """Initialize default income streams if none exist."""
        if not self.streams_file.exists():
            default_streams = {
                "skylar-bot-trading": {
                    "name": "Skylar Bot Trading",
                    "category": "trading",
                    "skill": "skylar-trading-bot",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.6,
                    "last_updated": datetime.now().isoformat()
                },
                "manual-crypto-trading": {
                    "name": "Manual Crypto Trading",
                    "category": "trading",
                    "skill": "manual-trading",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.5,
                    "last_updated": datetime.now().isoformat()
                },
                "whale-copy-trading": {
                    "name": "Whale Copy Trading",
                    "category": "trading",
                    "skill": "wallet-whale-tracker",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.7,
                    "last_updated": datetime.now().isoformat()
                },
                "sol-staking": {
                    "name": "SOL Staking Rewards",
                    "category": "passive",
                    "skill": "none",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.9,
                    "last_updated": datetime.now().isoformat()
                },
                "defi-yield": {
                    "name": "DeFi Yield Farming",
                    "category": "passive",
                    "skill": "none",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.7,
                    "last_updated": datetime.now().isoformat()
                },
                "digital-products": {
                    "name": "Digital Products",
                    "category": "product",
                    "skill": "autonomous-workflow-builder",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.5,
                    "last_updated": datetime.now().isoformat()
                },
                "research-services": {
                    "name": "Research Services",
                    "category": "service",
                    "skill": "research-synthesizer",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.6,
                    "last_updated": datetime.now().isoformat()
                },
                "trading-alerts": {
                    "name": "AOE Trading Alerts",
                    "category": "trading",
                    "skill": "autonomous-opportunity-engine",
                    "is_recurring": True,
                    "monthly_average": 0,
                    "confidence": 0.6,
                    "last_updated": datetime.now().isoformat()
                }
            }
            self._save_json(self.streams_file, default_streams)
    
    def add_income(self, source_name: str, amount_usd: float, 
                   category: str = "trading", skill: str = "manual-trading",
                   description: str = "", tags: List[str] = None,
                   metadata: Dict = None) -> str:
        """Record a new income entry."""
        record_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        
        entry = {
            "id": record_id,
            "date": datetime.now().isoformat(),
            "category": category,
            "skill": skill,
            "source_name": source_name,
            "amount_usd": amount_usd,
            "description": description,
            "tags": tags or [],
            "verified": False,
            "metadata": metadata or {}
        }
        
        # Add to monthly file
        month_file = self.transactions_path / f"{datetime.now().strftime('%Y-%m')}.json"
        transactions = self._load_json(month_file, [])
        transactions.append(entry)
        self._save_json(month_file, transactions)
        
        # Update stream average
        self._update_stream_average(source_name, amount_usd)
        
        return record_id
    
    def _update_stream_average(self, source_name: str, amount: float):
        """Update rolling average for income stream."""
        streams = self._load_json(self.streams_file, {})
        
        # Find matching stream
        for stream_id, stream in streams.items():
            if stream.get("name") == source_name or stream_id == source_name.lower().replace(" ", "-"):
                # Update rolling average (last 3 months)
                old_avg = stream.get("monthly_average", 0)
                new_avg = (old_avg * 2 + amount) / 3  # Weight toward recent
                stream["monthly_average"] = round(new_avg, 2)
                stream["last_updated"] = datetime.now().isoformat()
                break
        else:
            # Create new stream
            stream_id = source_name.lower().replace(" ", "-").replace("_", "-")
            streams[stream_id] = {
                "name": source_name,
                "category": "other",
                "skill": "none",
                "is_recurring": False,
                "monthly_average": amount,
                "confidence": 0.5,
                "last_updated": datetime.now().isoformat()
            }
        
        self._save_json(self.streams_file, streams)
    
    def get_mrr(self) -> Dict:
        """Calculate Monthly Recurring Revenue."""
        streams = self._load_json(self.streams_file, {})
        
        stable = 0
        variable = 0
        opportunistic = 0
        
        for stream_id, stream in streams.items():
            avg = stream.get("monthly_average", 0)
            confidence = stream.get("confidence", 0.5)
            is_recurring = stream.get("is_recurring", False)
            
            if is_recurring and confidence >= 0.8:
                stable += avg
            elif is_recurring and confidence >= 0.5:
                variable += avg
            else:
                opportunistic += avg
        
        return {
            "stable_recurring": round(stable, 2),
            "variable_monthly": round(variable, 2),
            "mrr_total": round(stable + variable, 2),
            "opportunistic": round(opportunistic, 2),
            "total_monthly": round(stable + variable + opportunistic, 2),
            "confidence": round((stable * 1.0 + variable * 0.8 + opportunistic * 0.5) / max(stable + variable + opportunistic, 0.01), 2)
        }
    
    def get_skill_roi(self, skill_name: str, hourly_rate: float = 50.0) -> SkillROI:
        """Calculate ROI for a specific skill."""
        # Get income from this skill
        monthly_income = self._get_monthly_income_by_skill(skill_name)
        
        # Calculate time costs (simplified - would load from skill config)
        development_hours = self._get_skill_development_hours(skill_name)
        monthly_maintenance = self._get_skill_maintenance_hours(skill_name)
        
        total_investment = development_hours * hourly_rate
        monthly_investment = monthly_maintenance * hourly_rate
        
        # Annual projection
        annual_return = monthly_income * 12
        annual_investment = monthly_investment * 12
        
        # ROI calculation
        net_profit = annual_return - annual_investment
        roi = (net_profit / max(total_investment, 0.01)) * 100 if total_investment > 0 else 0
        
        return SkillROI(
            skill=Skill(skill_name) if skill_name in [s.value for s in Skill] else Skill.NONE,
            monthly_income=round(monthly_income, 2),
            development_hours=development_hours,
            monthly_maintenance_hours=monthly_maintenance,
            hourly_rate=hourly_rate,
            total_investment=round(total_investment, 2),
            total_return=round(annual_return, 2),
            roi_percentage=round(roi, 1)
        )
    
    def get_all_skill_roi(self, hourly_rate: float = 50.0) -> List[SkillROI]:
        """Get ROI for all skills."""
        skills = [
            "autonomous-trading-strategist",
            "autonomous-opportunity-engine",
            "autonomous-workflow-builder",
            "skylar-trading-bot",
            "wallet-whale-tracker",
            "research-synthesizer"
        ]
        
        return [self.get_skill_roi(skill, hourly_rate) for skill in skills]
    
    def _get_monthly_income_by_skill(self, skill_name: str) -> float:
        """Get monthly income for a specific skill."""
        # Load last 3 months of transactions
        total = 0
        for i in range(3):
            month = datetime.now() - timedelta(days=30*i)
            month_file = self.transactions_path / f"{month.strftime('%Y-%m')}.json"
            transactions = self._load_json(month_file, [])
            
            for t in transactions:
                if t.get("skill") == skill_name:
                    total += t.get("amount_usd", 0)
        
        # Average monthly
        return total / 3
    
    def _get_skill_development_hours(self, skill_name: str) -> float:
        """Get development hours for skill (from config or estimate)."""
        skill_hours = {
            "autonomous-trading-strategist": 20,
            "autonomous-opportunity-engine": 15,
            "autonomous-workflow-builder": 12,
            "skylar-trading-bot": 40,
            "wallet-whale-tracker": 8,
            "research-synthesizer": 10
        }
        return skill_hours.get(skill_name, 10)
    
    def _get_skill_maintenance_hours(self, skill_name: str) -> float:
        """Get monthly maintenance hours for skill."""
        maintenance = {
            "autonomous-trading-strategist": 2,
            "autonomous-opportunity-engine": 1,
            "autonomous-workflow-builder": 1,
            "skylar-trading-bot": 3,
            "wallet-whale-tracker": 0.5,
            "research-synthesizer": 1
        }
        return maintenance.get(skill_name, 1)
    
    def generate_monthly_dashboard(self, year: int = None, month: int = None) -> str:
        """Generate comprehensive monthly dashboard."""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        month_file = self.transactions_path / f"{year}-{month:02d}.json"
        transactions = self._load_json(month_file, [])
        
        # Calculate totals
        total_income = sum(t.get("amount_usd", 0) for t in transactions)
        
        # By category
        by_category = {}
        by_skill = {}
        
        for t in transactions:
            cat = t.get("category", "other")
            by_category[cat] = by_category.get(cat, 0) + t.get("amount_usd", 0)
            
            skill = t.get("skill", "none")
            by_skill[skill] = by_skill.get(skill, 0) + t.get("amount_usd", 0)
        
        # MRR
        mrr = self.get_mrr()
        
        # Skill ROI
        skill_roi = self.get_all_skill_roi()
        
        # Format report
        lines = [
            f"# Income Dashboard: {datetime(year, month, 1).strftime('%B %Y')}",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| **Monthly Income** | ${total_income:,.2f} |",
            f"| **MRR (Stable + Variable)** | ${mrr['mrr_total']:,.2f} |",
            f"| **Total w/ Opportunistic** | ${mrr['total_monthly']:,.2f} |",
            f"| **Confidence Score** | {mrr['confidence']*100:.0f}% |",
            "",
            "## Income by Category",
            "",
            "| Category | Amount | % of Total |",
            "|----------|--------|------------|"
        ]
        
        for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            pct = (amount / max(total_income, 0.01)) * 100
            lines.append(f"| {cat.title()} | ${amount:,.2f} | {pct:.1f}% |")
        
        lines.extend([
            "",
            "## Income by Skill",
            "",
            "| Skill | Monthly Income |",
            "|-------|---------------|"
        ])
        
        for skill, amount in sorted(by_skill.items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"| {skill} | ${amount:,.2f} |")
        
        lines.extend([
            "",
            "## Skill ROI Performance",
            "",
            "| Skill | Monthly Income | Investment | ROI | Status |",
            "|-------|---------------|------------|-----|--------|"
        ])
        
        for roi in sorted(skill_roi, key=lambda x: x.roi_percentage, reverse=True):
            status = "🟢" if roi.roi_percentage > 200 else "🟡" if roi.roi_percentage > 50 else "🔴"
            lines.append(
                f"| {roi.skill.value[:25]}... | ${roi.monthly_income:,.2f} | "
                f"${roi.total_investment:,.0f} | {roi.roi_percentage:.0f}% | {status} |"
            )
        
        lines.extend([
            "",
            "## MRR Breakdown",
            "",
            "| Type | Amount | Description |",
            "|------|--------|-------------|",
            f"| Stable Recurring | ${mrr['stable_recurring']:,.2f} | High confidence, recurring |",
            f"| Variable Monthly | ${mrr['variable_monthly']:,.2f} | Averaged over 3 months |",
            f"| Opportunistic | ${mrr['opportunistic']:,.2f} | One-time/irregular |",
            "",
            "## Active Income Streams",
            ""
        ])
        
        streams = self._load_json(self.streams_file, {})
        lines.append("| Stream | Category | Monthly Avg | Confidence |")
        lines.append("|--------|----------|-------------|------------|")
        
        for stream_id, stream in sorted(streams.items(), key=lambda x: x[1].get("monthly_average", 0), reverse=True):
            conf = stream.get("confidence", 0) * 100
            avg = stream.get("monthly_average", 0)
            lines.append(
                f"| {stream.get('name', stream_id)} | {stream.get('category', 'other')} | "
                f"${avg:,.2f} | {conf:.0f}% |"
            )
        
        lines.extend([
            "",
            "---",
            f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        ])
        
        report = "\n".join(lines)
        
        # Save report
        report_file = self.reports_path / "monthly" / f"{year}-{month:02d}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        return report
    
    def identify_opportunities(self) -> List[Dict]:
        """Identify income growth opportunities."""
        opportunities = []
        
        # Get current state
        mrr = self.get_mrr()
        streams = self._load_json(self.streams_file, {})
        
        # Check for concentration risk
        trading = sum(s.get("monthly_average", 0) for s in streams.values() if s.get("category") == "trading")
        total = mrr["mrr_total"]
        
        if total > 0 and trading / total > 0.4:
            opportunities.append({
                "opportunity": "Diversify Away from Trading",
                "description": "Trading is 40%+ of MRR - high volatility risk",
                "potential_monthly": round(trading * 0.2, 2),
                "action": "Increase stable/passive income streams",
                "priority": "high"
            })
        
        # Find underperforming skills
        skill_roi = self.get_all_skill_roi()
        for roi in skill_roi:
            if roi.roi_percentage < 100 and roi.monthly_income > 0:
                opportunities.append({
                    "opportunity": f"Optimize {roi.skill.value}",
                    "description": f"ROI {roi.roi_percentage:.0f}% - skill underperforming",
                    "potential_monthly": round(roi.monthly_income * 0.5, 2),
                    "action": "Review usage patterns and optimize triggers",
                    "priority": "medium"
                })
        
        # Check for zero streams with potential
        zero_streams = [s for s in streams.values() if s.get("monthly_average", 0) == 0]
        if len(zero_streams) > 0:
            opportunities.append({
                "opportunity": "Activate Dormant Streams",
                "description": f"{len(zero_streams)} income streams at $0",
                "potential_monthly": len(zero_streams) * 50,
                "action": "Focus on activating one stream",
                "priority": "medium"
            })
        
        return opportunities
    
    def get_income_trend(self, months: int = 6) -> List[Dict]:
        """Get income trend over time."""
        trends = []
        
        for i in range(months):
            month_date = datetime.now() - timedelta(days=30*i)
            month_file = self.transactions_path / f"{month_date.strftime('%Y-%m')}.json"
            transactions = self._load_json(month_file, [])
            
            total = sum(t.get("amount_usd", 0) for t in transactions)
            trends.append({
                "month": month_date.strftime("%Y-%m"),
                "total_income": round(total, 2)
            })
        
        return list(reversed(trends))
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON from file."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Save JSON to file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """CLI for income tracker."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Income Tracker")
    parser.add_argument('--dashboard', action='store_true', help='Generate monthly dashboard')
    parser.add_argument('--mrr', action='store_true', help='Show MRR breakdown')
    parser.add_argument('--roi', action='store_true', help='Show skill ROI')
    parser.add_argument('--add', nargs=4, metavar=('SOURCE', 'AMOUNT', 'CATEGORY', 'SKILL'),
                       help='Add income entry')
    parser.add_argument('--opportunities', action='store_true', help='Show growth opportunities')
    parser.add_argument('--trend', action='store_true', help='Show trend over time')
    
    args = parser.parse_args()
    tracker = IncomeTracker()
    
    if args.dashboard:
        print(tracker.generate_monthly_dashboard())
    elif args.mrr:
        mrr = tracker.get_mrr()
        print("Monthly Recurring Revenue:")
        print(f"  Stable Recurring: ${mrr['stable_recurring']:,.2f}")
        print(f"  Variable Monthly: ${mrr['variable_monthly']:,.2f}")
        print(f"  MRR Total: ${mrr['mrr_total']:,.2f}")
        print(f"  Total (w/ Opp): ${mrr['total_monthly']:,.2f}")
        print(f"  Confidence: {mrr['confidence']*100:.0f}%")
    elif args.roi:
        rois = tracker.get_all_skill_roi()
        print("Skill ROI (hourly rate: $50):")
        print(f"{'Skill':<30} {'Income':>10} {'ROI':>8}")
        print("-" * 50)
        for roi in sorted(rois, key=lambda x: x.roi_percentage, reverse=True):
            print(f"{roi.skill.value[:30]:<30} ${roi.monthly_income:>8.2f} {roi.roi_percentage:>7.0f}%")
    elif args.add:
        record_id = tracker.add_income(
            source_name=args.add[0],
            amount_usd=float(args.add[1]),
            category=args.add[2],
            skill=args.add[3]
        )
        print(f"Added income: {record_id}")
    elif args.opportunities:
        ops = tracker.identify_opportunities()
        print("Income Opportunities:")
        for i, op in enumerate(ops[:5], 1):
            print(f"\n{i}. {op['opportunity']} (Priority: {op['priority']})")
            print(f"   {op['description']}")
            print(f"   Potential: ${op['potential_monthly']:,.2f}/month")
            print(f"   Action: {op['action']}")
    elif args.trend:
        trends = tracker.get_income_trend()
        print("Income Trend (Last 6 Months):")
        for t in trends:
            print(f"  {t['month']}: ${t['total_income']:,.2f}")
    else:
        print("Income Tracker")
        print("Use --dashboard, --mrr, --roi, --add, --opportunities, or --trend")


if __name__ == "__main__":
    main()
