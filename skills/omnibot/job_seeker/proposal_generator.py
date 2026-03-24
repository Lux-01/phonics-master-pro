#!/usr/bin/env python3
"""
Proposal Generator - Creates customized job proposals.

Workflow:
1. See job → Research client → Analyze requirements
2. Generate customized proposal
3. Queue for human approval

Research includes:
- Client history (past hires, payment record)
- Competition analysis (how many bids)
- Scope estimation (hours, complexity)
- Pricing recommendation (competitive but profitable)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ProposalStatus(Enum):
    """Status of proposal."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SENT = "sent"
    REJECTED = "rejected"


@dataclass
class Proposal:
    """A generated job proposal."""
    proposal_id: str
    job_id: str
    client_name: str
    platform: str
    content: str
    proposed_rate: Dict[str, Any]
    estimated_hours: int
    status: ProposalStatus
    created_at: str
    reviewed_at: Optional[str] = None
    sent_at: Optional[str] = None


@dataclass
class ClientProfile:
    """Researched client profile."""
    name: str
    platform: str
    rating: Optional[float]
    total_spent: Optional[float]
    hire_rate: Optional[float]
    past_projects: int
    payment_verified: bool
    preferred_skills: List[str]
    communication_style: str  # e.g., "detailed", "brief"
    responsiveness: str  # e.g., "fast", "slow"


class ClientResearcher:
    """Research clients before proposing."""
    
    def __init__(self):
        self.logger = logging.getLogger("Omnibot.ClientResearcher")
    
    def research_client(self, client_name: str, platform: str,
                       client_info: Dict) -> ClientProfile:
        """
        Research client history and characteristics.
        
        Args:
            client_name: Client/company name
            platform: Platform they're on
            client_info: Available client data
            
        Returns:
            ClientProfile
        """
        self.logger.info(f"Researching client: {client_name} on {platform}")
        
        # Simulated research (in production: API calls, scraping)
        return ClientProfile(
            name=client_name,
            platform=platform,
            rating=client_info.get('rating', 4.5),
            total_spent=client_info.get('total_spent', 0),
            hire_rate=client_info.get('hire_rate', 0.7),
            past_projects=client_info.get('past_projects', 5),
            payment_verified=client_info.get('payment_verified', True),
            preferred_skills=client_info.get('preferred_skills', []),
            communication_style="detailed" if "detailed" in str(client_info).lower() else "standard",
            responsiveness="fast" if platform in ['upwork', 'toptal'] else "standard"
        )
    
    def assess_client_quality(self, profile: ClientProfile) -> Dict:
        """
        Assess client quality for proposal risk.
        
        Returns quality score and red flags.
        """
        score = 50.0
        flags = []
        
        # Rating
        if profile.rating:
            if profile.rating >= 4.8:
                score += 20
            elif profile.rating >= 4.5:
                score += 10
            elif profile.rating < 4.0:
                score -= 20
                flags.append("Low client rating")
        
        # Payment verified
        if profile.payment_verified:
            score += 15
        else:
            score -= 15
            flags.append("Payment not verified")
        
        # Hire rate
        if profile.hire_rate and profile.hire_rate >= 0.5:
            score += 10
        elif profile.hire_rate and profile.hire_rate < 0.2:
            flags.append("Low hire rate - may not be serious")
        
        # Experience
        if profile.past_projects >= 10:
            score += 10
        elif profile.past_projects < 3:
            flags.append("New client - less history available")
        
        return {
            "quality_score": min(100, max(0, score)),
            "risk_level": "low" if score >= 70 else "medium" if score >= 50 else "high",
            "red_flags": flags,
            "recommendation": "Proceed" if score >= 60 else "Proceed with caution" if score >= 40 else "Consider declining"
        }


class RateCalculator:
    """Calculate optimal rates for proposals."""
    
    def __init__(self, base_rate: float = 75.0):
        self.logger = logging.getLogger("Omnibot.RateCalculator")
        self.base_rate = base_rate
    
    def calculate_rate(self, job_data: Dict, client_quality: Dict,
                      complexity: str = "medium") -> Dict:
        """
        Calculate optimal rate for a job.
        
        Args:
            job_data: Job information
            client_quality: Client quality assessment
            complexity: Job complexity
            
        Returns:
            Rate recommendation
        """
        # Base calculation
        hourly_rate = self.base_rate
        
        # Adjust for complexity
        complexity_multipliers = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3,
            "expert": 1.5
        }
        hourly_rate *= complexity_multipliers.get(complexity, 1.0)
        
        # Adjust for client quality
        quality_score = client_quality.get("quality_score", 70)
        if quality_score >= 80:
            hourly_rate *= 1.1  # Premium clients can pay more
        elif quality_score < 60:
            hourly_rate *= 0.95  # Risk discount
        
        # Market adjustment
        platform = job_data.get('platform', '')
        if platform == 'toptal':
            hourly_rate *= 1.2
        elif platform == 'fiverr':
            hourly_rate *= 0.7
        
        return {
            "suggested_hourly": round(hourly_rate, 2),
            "suggested_range": {
                "min": round(hourly_rate * 0.9, 2),
                "max": round(hourly_rate * 1.15, 2)
            },
            "estimated_total": None,  # Would calculate from scope
            "factors_applied": {
                "base": self.base_rate,
                "complexity": complexity,
                "client_quality": quality_score
            }
        }
    
    def estimate_scope(self, description: str) -> Dict:
        """
        Estimate project scope from description.
        
        Returns estimated hours and complexity.
        """
        desc_lower = description.lower()
        
        # Complexity indicators
        complexity_indicators = {
            "high": ["complex", "enterprise", "architecture", "scalable", "microservices"],
            "medium": ["integration", "api", "dashboard", "authentication"],
            "low": ["simple", "basic", "landing page", "static"]
        }
        
        complexity = "medium"
        for level, indicators in complexity_indicators.items():
            if any(ind in desc_lower for ind in indicators):
                complexity = level
                break
        
        # Hour estimates by complexity
        hour_estimates = {
            "low": (10, 20),
            "medium": (20, 60),
            "high": (60, 200)
        }
        
        min_hours, max_hours = hour_estimates.get(complexity, (20, 60))
        
        return {
            "complexity": complexity,
            "estimated_hours": round((min_hours + max_hours) / 2),
            "hour_range": {"min": min_hours, "max": max_hours},
            "confidence": "medium"
        }


class ProposalGenerator:
    """
    Generate customized job proposals.
    """
    
    def __init__(self, omnibot=None, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.ProposalGenerator")
        self.omnibot = omnibot
        
        # Components
        self.client_researcher = ClientResearcher()
        self.rate_calculator = RateCalculator()
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "proposals"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.proposals: Dict[str, Proposal] = {}
        self.proposals_file = self.data_dir / "generated_proposals.json"
        self._load_proposals()
        
        # Templates
        self.templates = self._load_templates()
    
    def _load_proposals(self):
        """Load existing proposals."""
        if self.proposals_file.exists():
            try:
                data = json.loads(self.proposals_file.read_text())
                for pid, pdata in data.items():
                    pdata['status'] = ProposalStatus(pdata['status'])
                    self.proposals[pid] = Proposal(**pdata)
            except Exception as e:
                self.logger.error(f"Failed to load proposals: {e}")
    
    def _save_proposals(self):
        """Save proposals."""
        try:
            data = {pid: asdict(prop) for pid, prop in self.proposals.items()}
            for pdata in data.values():
                pdata['status'] = pdata['status'].value
            self.proposals_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save proposals: {e}")
    
    def _load_templates(self) -> Dict[str, str]:
        """Load proposal templates."""
        templates = {
            "upwork_development": """
Hi {client_name},

I noticed your posting for "{job_title}" and I'm excited about this opportunity. 

**Why I'm a great fit:**
{skills_match}

**My approach:**
1. {approach_step_1}
2. {approach_step_2}
3. {approach_step_3}

**Relevant experience:**
{experience}

I'm available to start immediately and can commit {availability} per week to this project.

My rate is ${rate}/hour, and I estimate this will take approximately {estimated_hours} hours.

Looking forward to discussing this further!

Best regards,
[Your Name]
""",
            "linkedin_professional": """
Dear Hiring Manager,

I'm writing to express my strong interest in the {job_title} position at {company}.

**Key qualifications:**
{qualifications}

**What I bring:**
- {skill_1}
- {skill_2}
- {skill_3}

**Recent achievement:**
{achievement}

I'm excited about {company}'s mission and believe my background aligns well with your needs.

I'd welcome the opportunity to discuss how I can contribute to your team.

Best regards,
[Your Name]
"""
        }
        return templates
    
    def generate_proposal(self, job: Dict, platform: str) -> Proposal:
        """
        Generate a proposal for a job.
        
        Args:
            job: Job opportunity data
            platform: Platform name
            
        Returns:
            Generated Proposal
        """
        self.logger.info(f"Generating proposal for {job.get('title', 'Unknown')}")
        
        # Step 1: Research client
        client_name = job.get('client_name', job.get('company', 'Unknown'))
        client_profile = self.client_researcher.research_client(
            client_name, platform, job.get('client_info', {})
        )
        
        # Step 2: Assess client quality
        client_quality = self.client_researcher.assess_client_quality(client_profile)
        
        # Step 3: Estimate scope
        scope = self.rate_calculator.estimate_scope(job.get('description', ''))
        
        # Step 4: Calculate rate
        rate = self.rate_calculator.calculate_rate(
            job, client_quality, scope['complexity']
        )
        
        # Step  5: Generate content
        content = self._write_proposal_content(
            job, client_profile, platform, scope, rate
        )
        
        # Create proposal
        proposal_id = f"prop_{datetime.now().timestamp()}"
        proposal = Proposal(
            proposal_id=proposal_id,
            job_id=job.get('id', 'unknown'),
            client_name=client_name,
            platform=platform,
            content=content,
            proposed_rate=rate,
            estimated_hours=scope['estimated_hours'],
            status=ProposalStatus.DRAFT,
            created_at=datetime.now().isoformat()
        )
        
        self.proposals[proposal_id] = proposal
        self._save_proposals()
        
        return proposal
    
    def _write_proposal_content(self, job: Dict, client: ClientProfile,
                               platform: str, scope: Dict, rate: Dict) -> str:
        """Write customized proposal content."""
        # Select template
        template_key = f"{platform}_development"
        template = self.templates.get(template_key, self.templates.get("upwork_development"))
        
        # Extract matching skills
        job_skills = set(s.lower() for s in job.get('skills', []))
        your_skills = set(["python", "javascript", "react", "ai"])  # From preferences
        matches = job_skills.intersection(your_skills)
        
        skills_match = "• " + "\n• ".join(matches) if matches else "Full-stack development expertise"
        
        # Fill template
        content = template.format(
            client_name=client.name or "there",
            job_title=job.get('title', 'this project'),
            company=job.get('company', 'your company'),
            skills_match=skills_match,
            approach_step_1="Initial analysis and architecture planning",
            approach_step_2="Iterative development with regular check-ins",
            approach_step_3="Thorough testing and documentation",
            experience="5+ years developing similar applications with excellent client feedback",
            availability="30+ hours",
            rate=rate['suggested_hourly'],
            estimated_hours=scope['estimated_hours'],
            qualifications="\n".join([f"- {s}" for s in matches]) if matches else "Full-stack expertise",
            skill_1="Strong problem-solving abilities",
            skill_2="Clear communication",
            skill_3="Delivering on time",
            achievement="Successfully delivered 20+ projects with 95% client satisfaction"
        )
        
        return content
    
    def queue_for_review(self, proposal: Proposal) -> Proposal:
        """Queue proposal for human review."""
        proposal.status = ProposalStatus.PENDING_REVIEW
        self._save_proposals()
        self.logger.info(f"Proposal {proposal.proposal_id} queued for review")
        return proposal
    
    def approve_proposal(self, proposal_id: str) -> Proposal:
        """Mark proposal as approved."""
        if proposal_id in self.proposals:
            self.proposals[proposal_id].status = ProposalStatus.APPROVED
            self.proposals[proposal_id].reviewed_at = datetime.now().isoformat()
            self._save_proposals()
            self.logger.info(f"Proposal {proposal_id} approved")
        return self.proposals.get(proposal_id)
    
    def mark_sent(self, proposal_id: str) -> Proposal:
        """Mark proposal as sent."""
        if proposal_id in self.proposals:
            self.proposals[proposal_id].status = ProposalStatus.SENT
            self.proposals[proposal_id].sent_at = datetime.now().isoformat()
            self._save_proposals()
        return self.proposals.get(proposal_id)
    
    def get_pending_proposals(self) -> List[Proposal]:
        """Get proposals pending human review."""
        return [p for p in self.proposals.values() if p.status == ProposalStatus.PENDING_REVIEW]
    
    def get_proposal_summary(self, proposal_id: str) -> str:
        """Get human-readable proposal summary."""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return "Proposal not found"
        
        return f"""
📝 PROPOSAL SUMMARY
{'='*50}

Client: {proposal.client_name}
Platform: {proposal.platform}
Status: {proposal.status.value}

Proposed Rate: ${proposal.proposed_rate.get('suggested_hourly', 0)}/hr
Estimated Hours: {proposal.estimated_hours}

---
{proposal.content[:500]}...

[Full proposal ready for review]
"""
    
    def get_statistics(self) -> Dict:
        """Get proposal statistics."""
        total = len(self.proposals)
        by_status = {}
        for prop in self.proposals.values():
            status = prop.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total_generated": total,
            "by_status": by_status,
            "pending_review": len(self.get_pending_proposals()),
            "sent": by_status.get("sent", 0),
            "conversion_rate": "N/A"  # Would track actual results
        }