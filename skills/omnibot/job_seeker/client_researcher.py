#!/usr/bin/env python3
"""
Client Researcher - Analyze potential clients before proposing.

Research includes:
- Payment verification status
- Hiring history and rate
- Average project budgets
- Communication style (detailed vs brief)
- Responsiveness patterns
- Other freelancer feedback
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ClientProfile:
    """Comprehensive client profile."""
    client_id: str
    platform: str
    company_name: str

    # Verification & Trust
    payment_verified: bool
    email_verified: bool
    phone_verified: bool
    identity_verified: bool
    
    # Hiring History
    total_hires: int
    active_hires: int
    hire_rate: float  # 0-1, percentage of jobs that result in hire
    avg_project_budget: Optional[float]
    total_spent: float
    
    # Feedback & Ratings
    rating: Optional[float]  # Client rating from freelancers
    feedback_count: int
    top_review: Optional[str]
    
    # Communication
    communication_style: str  # "detailed", "brief", "mixed"
    responsiveness: str  # "fast", "standard", "slow"
    timezone: Optional[str]
    
    # Preferences
    preferred_skills: List[str]
    project_types: List[str]
    past_job_titles: List[str]
    
    # Red Flags
    disputes_count: int
    payment_delays: int
    communication_issues: int


@dataclass
class ResearchReport:
    """Complete research report for a client."""
    client_id: str
    company_name: str
    quality_score: int  # 0-100
    risk_level: str  # "low", "medium", "high"
    recommendations: List[str]
    red_flags: List[str]
    similar_clients: List[str]  # IDs of similar clients you've worked with
    confidence: float  # 0-1, how complete is this research
    research_date: str


class ClientResearcher:
    """
    Research clients before submitting proposals.
    Helps avoid bad clients and identify ideal matches.
    """
    
    # Quality thresholds
    MIN_HIRE_RATE = 0.4
    MIN_RATING = 4.0
    MIN_TOTAL_SPENT = 1000
    MAX_DISPUTES_RATIO = 0.1
    
    def __init__(self, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.ClientResearcher")
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "client_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Client database
        self.clients: Dict[str, ClientProfile] = {}
        self.clients_file = self.data_dir / "clients.json"
        self._load_clients()
        
        # Research history
        self.reports: Dict[str, ResearchReport] = {}
        self.reports_file = self.data_dir / "reports.json"
        self._load_reports()
        
        self.logger.info("ClientResearcher initialized")
    
    def _load_clients(self):
        """Load cached client profiles."""
        if self.clients_file.exists():
            try:
                data = json.loads(self.clients_file.read_text())
                for client_id, client_data in data.items():
                    self.clients[client_id] = ClientProfile(**client_data)
            except Exception as e:
                self.logger.error(f"Failed to load clients: {e}")
    
    def _save_clients(self):
        """Save client profiles."""
        try:
            data = {cid: asdict(client) for cid, client in self.clients.items()}
            self.clients_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save clients: {e}")
    
    def _load_reports(self):
        """Load research reports."""
        if self.reports_file.exists():
            try:
                data = json.loads(self.reports_file.read_text())
                for report_id, report_data in data.items():
                    self.reports[report_id] = ResearchReport(**report_data)
            except Exception as e:
                self.logger.error(f"Failed to load reports: {e}")
    
    def _save_reports(self):
        """Save research reports."""
        try:
            data = {rid: asdict(report) for rid, report in self.reports.items()}
            self.reports_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save reports: {e}")
    
    def research_client(self, client_name: str, platform: str,
                       client_info: Optional[Dict] = None) -> ResearchReport:
        """
        Research a potential client comprehensively.
        
        Args:
            client_name: Company or client name
            platform: Platform identifier (e.g., 'upwork', 'linkedin')
            client_info: Raw client data from platform (optional)
            
        Returns:
            ResearchReport with analysis
        """
        self.logger.info(f"Researching client: {client_name} on {platform}")
        
        client_id = f"{platform}_{client_name.lower().replace(' ', '_')}"
        
        # Check cache
        if client_id in self.clients:
            cached = self.clients[client_id]
            age_days = (datetime.now() - datetime.fromisoformat(cached.research_date)).days if hasattr(cached, 'research_date') else 30
            if age_days < 7:
                self.logger.debug(f"Using cached profile for {client_name}")
                return self.reports.get(client_id)
        
        # Simulate research (in production: platform API scraping)
        profile = self._simulate_research(client_name, platform, client_info or {})
        
        # Create report
        report = self._analyze_profile(profile)
        
        # Cache results
        self.clients[client_id] = profile
        self.reports[client_id] = report
        self._save_clients()
        self._save_reports()
        
        return report
    
    def _simulate_research(self, client_name: str, platform: str, 
                          client_info: Dict) -> ClientProfile:
        """Simulate client research (would be platform API in production)."""
        
        # Use provided info or generate realistic defaults
        return ClientProfile(
            client_id=f"{platform}_{client_name.lower().replace(' ', '_')}",
            platform=platform,
            company_name=client_name,
            payment_verified=client_info.get('payment_verified', True),
            email_verified=True,
            phone_verified=client_info.get('phone_verified', False),
            identity_verified=client_info.get('identity_verified', True),
            total_hires=client_info.get('total_hires', 15),
            active_hires=client_info.get('active_hires', 2),
            hire_rate=client_info.get('hire_rate', 0.7),
            avg_project_budget=client_info.get('avg_budget', 2500),
            total_spent=client_info.get('total_spent', 50000),
            rating=client_info.get('rating', 4.7),
            feedback_count=client_info.get('feedback_count', 45),
            top_review=client_info.get('top_review', "Great client to work with"),
            communication_style=client_info.get('communication_style', 'detailed'),
            responsiveness=client_info.get('responsiveness', 'fast'),
            timezone=client_info.get('timezone', 'America/New_York'),
            preferred_skills=client_info.get('preferred_skills', ['Python', 'React', 'API']),
            project_types=client_info.get('project_types', ['Web Development', 'API Integration']),
            past_job_titles=client_info.get('past_job_titles', ['Full Stack Developer', 'Backend Engineer']),
            disputes_count=client_info.get('disputes', 0),
            payment_delays=client_info.get('payment_delays', 0),
            communication_issues=client_info.get('communication_issues', 0)
        )
    
    def _analyze_profile(self, profile: ClientProfile) -> ResearchReport:
        """Analyze client profile and generate quality assessment."""
        
        score = 50.0  # Base score
        red_flags = []
        recommendations = []
        
        # Calculate quality score
        # Payment verification
        if profile.payment_verified:
            score += 15
            recommendations.append("✓ Payment verified - lower risk")
        else:
            red_flags.append("⚠ Payment not verified")
            score -= 20
        
        # Hire rate
        if profile.hire_rate >= 0.7:
            score += 15
            recommendations.append(f"✓ High hire rate ({profile.hire_rate:.0%}) - serious about hiring")
        elif profile.hire_rate >= self.MIN_HIRE_RATE:
            score += 5
        else:
            red_flags.append(f"⚠ Low hire rate ({profile.hire_rate:.0%}) - may not be serious")
            score -= 10
        
        # Rating
        if profile.rating:
            if profile.rating >= 4.8:
                score += 10
                recommendations.append(f"✓ Excellent client rating ({profile.rating}/5)")
            elif profile.rating >= self.MIN_RATING:
                score += 5
            else:
                red_flags.append(f"⚠ Low client rating ({profile.rating}/5)")
                score -= 15
        
        # Spending history
        if profile.total_spent >= 10000:
            score += 10
            recommendations.append(f"✓ High spender (${profile.total_spent:,.0f} total)")
        elif profile.total_spent >= self.MIN_TOTAL_SPENT:
            score += 5
        
        # Disputes
        if profile.disputes_count == 0:
            score += 10
            recommendations.append("✓ No disputes - clean record")
        elif profile.disputes_count / max(profile.total_hires, 1) < self.MAX_DISPUTES_RATIO:
            score += 0
        else:
            red_flags.append(f"⚠ High dispute ratio ({profile.disputes_count} disputes)")
            score -= 20
        
        # Communication
        if profile.communication_style == 'detailed':
            recommendations.append(f"✓ Detailed job descriptions - clear expectations")
        
        if profile.responsiveness == 'fast':
            score += 5
            recommendations.append("✓ Fast responder - quick feedback")
        
        # Determine risk level
        if score >= 75 and not red_flags:
            risk_level = "low"
        elif score >= 50:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Generate recommendation
        if not red_flags:
            recommendations.insert(0, "🟢 RECOMMENDED: Apply to this client")
        elif score > 60:
            recommendations.insert(0, "🟡 CAUTION: Proceed with standard precautions")
        else:
            recommendations.insert(0, "🔴 CONSIDER SKIPPING: Multiple red flags detected")
        
        return ResearchReport(
            client_id=profile.client_id,
            company_name=profile.company_name,
            quality_score=min(100, max(0, int(score))),
            risk_level=risk_level,
            recommendations=recommendations,
            red_flags=red_flags,
            similar_clients=[],  # Would match against past clients
            confidence=0.85,  # Based on available data
            research_date=datetime.now().isoformat()
        )
    
    def get_profile(self, client_id: str) -> Optional[ClientProfile]:
        """Get cached client profile."""
        return self.clients.get(client_id)
    
    def get_report(self, client_id: str) -> Optional[ResearchReport]:
        """Get research report for client."""
        return self.reports.get(client_id)
    
    def get_statistics(self) -> Dict:
        """Get research statistics."""
        if not self.reports:
            return {"total_researched": 0}
        
        quality_scores = [r.quality_score for r in self.reports.values()]
        
        return {
            "total_researched": len(self.reports),
            "avg_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "low_risk": sum(1 for r in self.reports.values() if r.risk_level == "low"),
            "medium_risk": sum(1 for r in self.reports.values() if r.risk_level == "medium"),
            "high_risk": sum(1 for r in self.reports.values() if r.risk_level == "high"),
            "red_flagged": sum(1 for r in self.reports.values() if r.red_flags)
        }
    
    def list_clients(self, min_quality: int = 0, max_risk: Optional[str] = None) -> List[ResearchReport]:
        """List all researched clients, optionally filtered."""
        reports = list(self.reports.values())
        
        if min_quality > 0:
            reports = [r for r in reports if r.quality_score >= min_quality]
        
        if max_risk:
            risk_order = {"low": 0, "medium": 1, "high": 2}
            max_val = risk_order.get(max_risk, 2)
            reports = [r for r in reports if risk_order.get(r.risk_level, 2) <= max_val]
        
        # Sort by quality score
        return sorted(reports, key=lambda r: r.quality_score, reverse=True)
    
    def export_report(self, client_id: str) -> str:
        """Export client report as formatted text."""
        report = self.get_report(client_id)
        if not report:
            return "Client not found"
        
        profile = self.get_profile(client_id)
        
        output = f"""
🔍 CLIENT RESEARCH REPORT
{'='*60}

Company: {report.company_name}
Quality Score: {report.quality_score}/100
Risk Level: {report.risk_level.upper()}
Researched: {report.research_date[:10]}

RECOMMENDATION
"""
        for rec in report.recommendations:
            output += f"• {rec}\n"
        
        if report.red_flags:
            output += "\n⚠️ RED FLAGS\n"
            for flag in report.red_flags:
                output += f"• {flag}\n"
        
        if profile:
            output += f"\n📊 DETAILED PROFILE\n"
            output += f"Hires: {profile.total_hires} ({profile.hire_rate:.0%} hire rate)\n"
            output += f"Total Spent: ${profile.total_spent:,.0f}\n"
            if profile.rating:
                output += f"Rating: {profile.rating}/5 ({profile.feedback_count} reviews)\n"
            output += f"Communication: {profile.communication_style}, {profile.responsiveness}\n"
            output += f"Preferred Skills: {', '.join(profile.preferred_skills[:5])}\n"
        
        return output
