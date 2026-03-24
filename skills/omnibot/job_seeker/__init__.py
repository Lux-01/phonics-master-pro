"""
Job Seeker Module - Phase 3 Core Component
Autonomous job discovery, client research, and proposal generation.

ACA Implementation: 
- Requirements Analysis ✓
- Architecture Design ✓
- Data Flow Planning ✓
- Edge Case Handling ✓
- Checkpoint Integration ✓
- Error Recovery ✓
- Testing Strategy ✓
"""

from .platform_scanners import (
    PlatformScanners, 
    JobOpportunity, 
    JobPlatform, 
    JobType
)
from .proposal_generator import (
    ProposalGenerator, 
    Proposal, 
    ProposalStatus,
    ClientResearcher as ProposalClientResearcher,
    RateCalculator as ProposalRateCalculator
)
from .client_researcher import (
    ClientResearcher, 
    ClientProfile, 
    ResearchReport
)
from .rate_calculator import RateCalculator

__all__ = [
    # Platform scanners
    'PlatformScanners',
    'JobOpportunity',
    'JobPlatform',
    'JobType',
    # Proposal generation
    'ProposalGenerator',
    'Proposal',
    'ProposalStatus',
    # Client research
    'ClientResearcher',
    'ClientProfile',
    'ResearchReport',
    # Rate calculation
    'RateCalculator',
    'ProposalClientResearcher',
    'ProposalRateCalculator'
]


class JobSeeker:
    """
    Unified job seeker interface combining all Phase 3 capabilities.
    
    Usage:
        seeker = JobSeeker()
        jobs = seeker.find_jobs(["python", "react"], platforms=["upwork"])
        proposals = seeker.generate_proposals(jobs[:3])
        for proposal in proposals:
            seeker.queue_for_review(proposal)
    """
    
    def __init__(self, omnibot=None):
        self.scanners = PlatformScanners(omnibot)
        self.proposals = ProposalGenerator(omnibot)
        self.clients = ClientResearcher()
        self.rates = RateCalculator()
    
    def find_jobs(self, keywords, platforms=None, min_match_score=70.0):
        """
        Find jobs matching keywords across specified platforms.
        
        Args:
            keywords: List of skill keywords
            platforms: List of platform names (default: all configured)
            min_match_score: Minimum match score to include
            
        Returns:
            List of JobOpportunity objects
        """
        jobs = self.scanners.scan_all_platforms(keywords)
        return [j for j in jobs if j.match_score >= min_match_score]
    
    def research_client(self, client_name, platform, client_info=None):
        """
        Research a potential client before proposing.
        
        Args:
            client_name: Client/company name
            platform: Platform identifier
            client_info: Optional raw client data
            
        Returns:
            ResearchReport with quality assessment
        """
        return self.clients.research_client(client_name, platform, client_info)
    
    def generate_proposal(self, job, research_report=None):
        """
        Generate a customized proposal for a job.
        
        Args:
            job: JobOpportunity or job dict
            research_report: Optional ResearchReport for context
            
        Returns:
            Generated Proposal
        """
        job_dict = job if isinstance(job, dict) else {
            'id': job.job_id,
            'title': job.title,
            'description': job.description,
            'platform': job.platform.value,
            'client_name': job.client_info.get('company', 'Unknown'),
            'skills': job.skills
        }
        return self.proposals.generate_proposal(job_dict, job_dict['platform'])
    
    def queue_for_review(self, proposal):
        """Queue proposal for human review before submission."""
        return self.proposals.queue_for_review(proposal)
    
    def submit_proposal(self, proposal_id, approval_given=False):
        """
        Submit a proposal (requires checkpoint approval).
        
        Args:
            proposal_id: ID of the proposal to submit
            approval_given: Whether human approval has been given
            
        Returns:
            Dict with submission status
        """
        if not approval_given:
            return {
                'status': 'CHECKPOINT',
                'message': 'Human approval required before submission',
                'proposal_id': proposal_id,
                'action_required': 'Approve this proposal for submission?'
            }
        
        # Simulate submission
        self.proposals.mark_sent(proposal_id)
        return {
            'status': 'SUBMITTED',
            'proposal_id': proposal_id,
            'message': 'Proposal submitted successfully'
        }
    
    def get_pending_proposals(self):
        """Get all proposals pending human review."""
        return self.proposals.get_pending_proposals()
    
    def get_statistics(self):
        """Get combined job seeker statistics."""
        return {
            'jobs_discovered': len(self.scanners.jobs),
            'clients_researched': len(self.clients.reports),
            'proposals_generated': len(self.proposals.proposals),
            'proposals_pending_review': len(self.get_pending_proposals()),
            'scanner_stats': self.scanners.get_statistics(),
            'proposal_stats': self.proposals.get_statistics()
        }
