#!/usr/bin/env python3
"""
Platform Scanners - Automatically scan job platforms for opportunities.

Scans:
1. Upwork → Python developer jobs, remote, $50+/hr
2. LinkedIn → Software engineer postings, AI focus
3. Fiverr → Design gigs, quick turnaround
4. Freelancer.com
5. Toptal
6. AngelList (startups)

Filters by:
- Skills match (parsing job descriptions)
- Rate threshold (configurable)
- Client rating (only 4.5+)
- Competition (low/medium bids)
"""

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from urllib.parse import urljoin


class JobPlatform(Enum):
    """Supported job platforms."""
    UPWORK = "upwork"
    LINKEDIN = "linkedin"
    FIVERR = "fiverr"
    FREELANCER = "freelancer"
    TOPTAL = "toptal"
    ANGELLIST = "angelist"  # Wellfound
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    GITHUB_JOBS = "github_jobs"
    AIRTASKER = "airtasker"


class JobType(Enum):
    """Types of jobs."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"


@dataclass
class JobOpportunity:
    """A discovered job opportunity."""
    job_id: str
    platform: JobPlatform
    title: str
    description: str
    url: Optional[str]
    posted_date: datetime
    budget: Optional[Dict[str, Any]]  # {min, max, type}
    hourly_rate: Optional[float]
    skills: List[str]
    client_info: Dict[str, Any]
    competition: Dict[str, Any]  # {bids, proposals}
    match_score: float  # 0-100
    screened: bool = False
    applied: bool = False


class PlatformScanners:
    """
    Multi-platform job scanner with intelligent filtering.
    """
    
    # Platform URLs (for reference - actual scraping uses different methods)
    PLATFORM_URLS = {
        JobPlatform.UPWORK: "https://www.upwork.com",
        JobPlatform.LINKEDIN: "https://www.linkedin.com/jobs",
        JobPlatform.FIVERR: "https://www.fiverr.com",
        JobPlatform.FREELANCER: "https://www.freelancer.com",
        JobPlatform.ANGELLIST: "https://angel.co/jobs",
        JobPlatform.AIRTASKER: "https://www.airtasker.com/tasks/",
    }
    
    def __init__(self, omnibot=None, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.PlatformScanners")
        self.omnibot = omnibot
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "job_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Job database
        self.jobs: Dict[str, JobOpportunity] = {}
        self.jobs_file = self.data_dir / "discovered_jobs.json"
        self._load_jobs()
        
        # User preferences
        self.preferences = self._load_preferences()
        
        # Skills to match
        self.user_skills = self.preferences.get("skills", [
            "python", "javascript", "react", "node.js", "ai", 
            "machine learning", "web development", "backend"
        ])
        
        # Rate thresholds
        self.min_hourly_rate = self.preferences.get("min_hourly_rate", 50)
        self.min_project_budget = self.preferences.get("min_project_budget", 500)
        
        self.logger.info("PlatformScanners initialized")
    
    def _load_jobs(self):
        """Load previously discovered jobs."""
        if self.jobs_file.exists():
            try:
                data = json.loads(self.jobs_file.read_text())
                # Convert dicts to JobOpportunity objects
                for job_id, job_data in data.items():
                    self.jobs[job_id] = JobOpportunity(**job_data)
                self.logger.info(f"Loaded {len(self.jobs)} previous jobs")
            except Exception as e:
                self.logger.error(f"Failed to load jobs: {e}")
    
    def _save_jobs(self):
        """Save discovered jobs."""
        try:
            data = {job_id: asdict(job) for job_id, job in self.jobs.items()}
            self.jobs_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save jobs: {e}")
    
    def _load_preferences(self) -> Dict:
        """Load user preferences."""
        pref_file = self.data_dir / "preferences.json"
        if pref_file.exists():
            try:
                return json.loads(pref_file.read_text())
            except Exception:
                pass
        
        # Default preferences
        return {
            "skills": ["python", "javascript", "react", "ai", "web development"],
            "min_hourly_rate": 50,
            "min_project_budget": 500,
            "preferred_job_types": ["freelance", "contract"],
            "excluded_keywords": ["unpaid", "internship", "equity only", "student"],
            "platforms": ["upwork", "linkedin", "angelist"],
            "remote_only": True
        }
    
    # ==================== PLATFORM SCANNERS ====================
    
    def scan_all_platforms(self, keywords: Optional[List[str]] = None) -> List[JobOpportunity]:
        """
        Scan all configured platforms for jobs.
        
        Args:
            keywords: Search keywords (uses default if None)
            
        Returns:
            List of new opportunities
        """
        self.logger.info("Scanning all platforms...")
        
        all_opportunities = []
        
        # Scan each enabled platform
        if JobPlatform.UPWORK in [JobPlatform(p) for p in self.preferences.get("platforms", [])]:
            all_opportunities.extend(self.scan_upwork(keywords))
        
        if JobPlatform.LINKEDIN in [JobPlatform(p) for p in self.preferences.get("platforms", [])]:
            all_opportunities.extend(self.scan_linkedin(keywords))
        
        if JobPlatform.ANGELLIST in [JobPlatform(p) for p in self.preferences.get("platforms", [])]:
            all_opportunities.extend(self.scan_angelist(keywords))
        
        if JobPlatform.AIRTASKER in [JobPlatform(p) for p in self.preferences.get("platforms", [])]:
            all_opportunities.extend(self.scan_airtasker(keywords))
        
        self.logger.info(f"Found {len(all_opportunities)} opportunities")
        return all_opportunities
    
    def scan_upwork(self, keywords: Optional[List[str]] = None) -> List[JobOpportunity]:
        """
        Scan Upwork for jobs.
        
        Note: In production, would use API or RSS feeds.
        For now, returns structured search simulation.
        """
        self.logger.info("Scanning Upwork...")
        
        search_terms = keywords or self.user_skills
        opportunities = []
        
        # Simulate job data (in production: API/RSS scrape)
        sample_jobs = [
            {
                "title": "Python Developer for AI Chatbot",
                "description": "Looking for experienced Python developer...",
                "skills": ["python", "ai", "machine learning", "api"],
                "budget": {"min": 2000, "max": 5000, "type": "fixed"},
                "client_rating": 4.8,
                "posted_hours_ago": 5,
                "proposals": 5,
                "link": "https://upwork.com/job/example1"
            },
            {
                "title": "React Developer - E-commerce Dashboard",
                "description": "Frontend developer needed...",
                "skills": ["react", "javascript", "typescript", "tailwind"],
                "hourly_rate": 75,
                "client_rating": 4.9,
                "posted_hours_ago": 12,
                "proposals": 8,
                "link": "https://upwork.com/job/example2"
            },
            {
                "title": "Backend API Development - Node.js",
                "description": "Build REST API for mobile app...",
                "skills": ["node.js", "javascript", "mongodb", "rest api"],
                "budget": {"min": 1500, "max": 3000, "type": "fixed"},
                "client_rating": 4.7,
                "posted_hours_ago": 24,
                "proposals": 15,
                "link": "https://upwork.com/job/example3"
            }
        ]
        
        for job_data in sample_jobs:
            # Check if matches criteria
            if self._matches_criteria(job_data):
                opportunity = self._create_opportunity(
                    JobPlatform.UPWORK, job_data
                )
                
                # Check not duplicate
                if opportunity.job_id not in self.jobs:
                    self.jobs[opportunity.job_id] = opportunity
                    opportunities.append(opportunity)
        
        self._save_jobs()
        return opportunities
    
    def scan_linkedin(self, keywords: Optional[List[str]] = None) -> List[JobOpportunity]:
        """Scan LinkedIn for jobs."""
        self.logger.info("Scanning LinkedIn...")
        
        opportunities = []
        
        # Simulate jobs
        sample_jobs = [
            {
                "title": "Senior Software Engineer - AI Products",
                "company": "TechCorp",
                "location": "Remote",
                "skills": ["python", "ai", "tensorflow", "aws"],
                "salary": {"min": 120000, "max": 160000},
                "posted_days_ago": 2,
                "applicants": 45,
                "link": "https://linkedin.com/jobs/example1"
            },
            {
                "title": "Full Stack Developer (Contract)",
                "company": "StartupXYZ",
                "location": "Remote",
                "skills": ["react", "node.js", "typescript", "postgresql"],
                "hourly_rate": 85,
                "posted_days_ago": 1,
                "applicants": 20,
                "link": "https://linkedin.com/jobs/example2"
            }
        ]
        
        for job_data in sample_jobs:
            if self._matches_criteria(job_data):
                opportunity = self._create_opportunity(
                    JobPlatform.LINKEDIN, job_data
                )
                
                if opportunity.job_id not in self.jobs:
                    self.jobs[opportunity.job_id] = opportunity
                    opportunities.append(opportunity)
        
        self._save_jobs()
        return opportunities
    
    def scan_angelist(self, keywords: Optional[List[str]] = None) -> List[JobOpportunity]:
        """Scan AngelList (Wellfound) for startup jobs."""
        self.logger.info("Scanning AngelList...")
        
        opportunities = []
        
        # Simulate startup jobs
        sample_jobs = [
            {
                "title": "Founding Engineer - AI Infrastructure",
                "startup": "AI Startup",
                "stage": "Series A",
                "skills": ["python", "kubernetes", "ml", "aws"],
                "compensation": {"salary": 140000, "equity": "0.5-1%"},
                "posted_days_ago": 3,
                "link": "https://angel.co/jobs/example1"
            }
        ]
        
        for job_data in sample_jobs:
            if self._matches_criteria(job_data):
                opportunity = self._create_opportunity(
                    JobPlatform.ANGELLIST, job_data
                )
                
                if opportunity.job_id not in self.jobs:
                    self.jobs[opportunity.job_id] = opportunity
                    opportunities.append(opportunity)
        
        self._save_jobs()
        return opportunities
    
    def scan_fiverr(self, keywords: Optional[List[str]] = None) -> List[JobOpportunity]:
        """Scan Fiverr for quick gigs."""
        self.logger.info("Scanning Fiverr (future implementation)...")
        return []
    
    def scan_freelancer(self, keywords: Optional[List[str]] = None) -> List[JobOpportunity]:
        """Scan Freelancer.com."""
        self.logger.info("Scanning Freelancer.com (future implementation)...")
        return []
    
    def scan_airtasker(self, keywords: Optional[List[str]] = None, 
                       min_budget: float = 100.0) -> List[JobOpportunity]:
        """
        Scan Airtasker for programming and tech tasks.
        
        Uses browser automation to find real tasks on Airtasker.
        
        Args:
            keywords: Search keywords (default: web, python, automation)
            min_budget: Minimum budget filter in AUD
            
        Returns:
            List of JobOpportunity objects
        """
        self.logger.info("Scanning Airtasker...")
        
        try:
            # Import the dedicated Airtasker scanner
            try:
                from .airtasker_scanner import AirtaskerScanner
            except ImportError:
                from airtasker_scanner import AirtaskerScanner
            
            scanner = AirtaskerScanner()
            tasks_data = scanner.scan_tasks(
                keywords=keywords or ["web", "python", "automation", "API", "developer"],
                min_budget=min_budget
            )
            
            opportunities = []
            
            for task_data in tasks_data:
                # Check if matches criteria
                if self._matches_criteria(task_data):
                    opportunity = self._create_opportunity(
                        JobPlatform.AIRTASKER, task_data
                    )
                    
                    # Check not duplicate
                    if opportunity.job_id not in self.jobs:
                        self.jobs[opportunity.job_id] = opportunity
                        opportunities.append(opportunity)
            
            self._save_jobs()
            self.logger.info(f"Found {len(opportunities)} Airtasker opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Failed to scan Airtasker: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # ==================== FILTERING ====================
    
    def _matches_criteria(self, job_data: Dict) -> bool:
        """Check if job matches user criteria."""
        # Check excluded keywords
        job_text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        for excluded in self.preferences.get("excluded_keywords", []):
            if excluded in job_text:
                self.logger.debug(f"Excluded: {excluded}")
                return False
        
        # Check budget/rate
        budget = job_data.get('budget')
        hourly = job_data.get('hourly_rate')
        salary = job_data.get('salary', {})
        
        if hourly is not None and hourly < self.min_hourly_rate:
            return False
        
        if budget and isinstance(budget, dict):
            budget_max = budget.get('max') or budget.get('min', 0)
            if budget_max and budget_max < self.min_project_budget:
                return False
        
        # Check remote preference
        if self.preferences.get("remote_only"):
            location = job_data.get('location', '').lower()
            if 'remote' not in location and 'remote' not in job_text:
                return False
        
        # Check skills match
        job_skills = set(s.lower() for s in job_data.get('skills', []))
        user_skills = set(s.lower() for s in self.user_skills)
        if not job_skills.intersection(user_skills):
            return False
        
        return True
    
    def _create_opportunity(self, platform: JobPlatform, 
                           job_data: Dict) -> JobOpportunity:
        """Create JobOpportunity from raw data."""
        # Generate unique ID
        job_id = hashlib.md5(
            f"{platform.value}:{job_data.get('title')}:{job_data.get('link', '')}".encode()
        ).hexdigest()[:16]
        
        # Calculate match score
        match_score = self._calculate_match_score(job_data)
        
        return JobOpportunity(
            job_id=job_id,
            platform=platform,
            title=job_data.get('title', 'Untitled'),
            description=job_data.get('description', '')[:500],
            url=job_data.get('link'),
            posted_date=datetime.now() - timedelta(
                hours=job_data.get('posted_hours_ago', 0),
                days=job_data.get('posted_days_ago', 0)
            ),
            budget=job_data.get('budget'),
            hourly_rate=job_data.get('hourly_rate'),
            skills=job_data.get('skills', []),
            client_info={
                "rating": job_data.get('client_rating', job_data.get('company', '')),
                "company": job_data.get('company', job_data.get('startup', '')),
                "stage": job_data.get('stage', '')
            },
            competition={
                "bids": job_data.get('proposals', job_data.get('applicants', 0)),
                "level": self._assess_competition(job_data)
            },
            match_score=match_score
        )
    
    def _calculate_match_score(self, job_data: Dict) -> float:
        """Calculate how well job matches user profile (0-100)."""
        job_skills = set(s.lower() for s in job_data.get('skills', []))
        user_skills = set(s.lower() for s in self.user_skills)
        
        if not job_skills:
            return 0.0
        
        matches = len(job_skills.intersection(user_skills))
        score = (matches / len(job_skills)) * 100
        
        # Boost for high-paying jobs
        hourly = job_data.get('hourly_rate') or 0
        if hourly >= self.min_hourly_rate * 1.5:
            score += 10
        
        # Also check budget for fixed-price jobs
        budget = job_data.get('budget', {})
        if budget and isinstance(budget, dict):
            budget_max = budget.get('max') or budget.get('min', 0)
            if budget_max and budget_max >= 500:
                score += 5
        
        # Penalty for high competition
        proposals = job_data.get('proposals', 0) or 0
        if proposals > 50:
            score -= 10
        
        return min(100, max(0, score))
    
    def _assess_competition(self, job_data: Dict) -> str:
        """Assess competition level."""
        proposals = job_data.get('proposals', job_data.get('applicants', 0))
        
        if proposals <= 5:
            return "low"
        elif proposals <= 15:
            return "medium"
        else:
            return "high"
    
    # ==================== JOB MANAGEMENT ====================
    
    def get_new_opportunities(self, min_match_score: float = 70.0) -> List[JobOpportunity]:
        """
        Get new opportunities sorted by match score.
        
        Args:
            min_match_score: Minimum match score to include
            
        Returns:
            List of opportunities
        """
        unapplied = [job for job in self.jobs.values() if not job.applied]
        
        # Filter by match score
        filtered = [job for job in unapplied if job.match_score >= min_match_score]
        
        # Sort by score (descending)
        return sorted(filtered, key=lambda j: j.match_score, reverse=True)
    
    def mark_applied(self, job_id: str):
        """Mark a job as applied."""
        if job_id in self.jobs:
            self.jobs[job_id].applied = True
            self._save_jobs()
    
    def get_job_details(self, job_id: str) -> Optional[JobOpportunity]:
        """Get detailed info about a specific job."""
        return self.jobs.get(job_id)
    
    def get_statistics(self) -> Dict:
        """Get job search statistics."""
        total = len(self.jobs)
        
        def get_attr(job, attr, default=None):
            if isinstance(job, JobOpportunity):
                return getattr(job, attr, default)
            return job.get(attr, default)
        
        applied = sum(1 for j in self.jobs.values() if get_attr(j, 'applied', False))
        by_platform = {}
        
        for job in self.jobs.values():
            platform = get_attr(job, 'platform', 'unknown')
            # Handle both enum and string
            if hasattr(platform, 'value'):
                platform = platform.value
            by_platform[platform] = by_platform.get(platform, 0) + 1
        
        avg_match = sum(get_attr(j, 'match_score', 0) for j in self.jobs.values()) / total if total > 0 else 0
        
        high_matches = sum(1 for j in self.jobs.values() if get_attr(j, 'match_score', 0) >= 80)
        
        return {
            "total_discovered": total,
            "applied": applied,
            "avg_match_score": round(avg_match, 1),
            "by_platform": by_platform,
            "high_match_count": high_matches,
            "recent_week": len([j for j in self.jobs.values()])
        }
    
    def update_preferences(self, **kwargs):
        """Update search preferences."""
        self.preferences.update(kwargs)
        
        # Save
        pref_file = self.data_dir / "preferences.json"
        pref_file.write_text(json.dumps(self.preferences, indent=2))
        
        self.logger.info(f"Updated preferences: {kwargs.keys()}")
    
    def get_preference_summary(self) -> str:
        """Get human-readable preference summary."""
        return f"""
🎯 JOB SEARCH PREFERENCES
{'='*40}

Skills: {', '.join(self.user_skills)}
Min Hourly Rate: ${self.min_hourly_rate}/hr
Min Project Budget: ${self.min_project_budget}
Remote Only: {self.preferences.get('remote_only', True)}
Platforms: {', '.join(self.preferences.get('platforms', []))}

Excluded: {', '.join(self.preferences.get('excluded_keywords', []))}
"""