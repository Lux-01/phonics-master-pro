"""
Company Researcher Module
==========================
Step 2 of ACA Workflow: Research target company using SIL + stealth browser.

This module gathers intelligence on target companies:
- Company overview and mission
- Culture and values
- Tech stack and tools
- Recent news and developments
- Job requirements analysis
- Hiring trends
"""

import json
import re
import asyncio
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CompanyInfo:
    """Company intelligence data structure."""
    name: str
    website: str = ""
    description: str = ""
    industry: str = ""
    size: str = ""  # e.g., "100-500 employees"
    founded: str = ""
    headquarters: str = ""
    mission: str = ""
    values: List[str] = field(default_factory=list)
    culture_description: str = ""
    benefits: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    recent_news: List[Dict[str, str]] = field(default_factory=list)
    linkedin_url: str = ""
    glassdoor_url: str = ""
    crunchbase_url: str = ""
    funding_stage: str = ""
    revenue_range: str = ""
    glassdoor_rating: Optional[float] = None
    research_date: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobRequirements:
    """Job posting requirements analysis."""
    job_title: str = ""
    company: str = ""
    department: str = ""
    location: str = ""
    employment_type: str = ""  # Full-time, Contract, etc.
    remote_policy: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    years_experience: str = ""
    education_required: str = ""
    certifications_preferred: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    key_keywords: List[str] = field(default_factory=list)
    soft_skills_emphasized: List[str] = field(default_factory=list)
    salary_range: str = ""
    posting_date: str = ""
    application_url: str = ""
    description_full: str = ""
    raw_text: str = ""


class CompanyResearcher:
    """
    Research target companies using web scraping and browser automation.
    
    Features:
    - Company profile extraction
    - Job posting analysis
    - Tech stack identification
    - Culture research
    """
    
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        # Common job board patterns
        self.job_board_patterns = {
            'linkedin': r'linkedin\.com/jobs',
            'indeed': r'indeed\.com/viewjob',
            'glassdoor': r'glassdoor\.com/job',
            'greenhouse': r'boards\.greenhouse\.io',
            'lever': r'jobs\.lever\.co',
            'workday': r'\.(wd\d+\.myworkdayjobs|myworkdayjobs\.com)',
            'monster': r'monster\.com/job',
            'ziprecruiter': r'ziprecruiter\.com/job',
            'ashby': r'jobs\.ashbyhq\.com',
            'breezy': r'breezy\.hr/p',
            'recruitee': r'recruitee\.com',
            'careers_page': r'/careers?/job'
        }
        
        # Tech stack keywords
        self.tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#',
            'react', 'vue', 'angular', 'next.js', 'node.js', 'django', 'flask',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'tensorflow', 'pytorch', 'pandas', 'numpy',
            'git', 'jenkins', 'github actions', 'gitlab ci',
            'microservices', 'rest api', 'graphql', 'grpc',
            'kafka', 'rabbitmq', 'redis', 'elasticsearch',
            'react native', 'flutter', 'ios', 'android', 'swift', 'kotlin'
        ]
        
        # Soft skills keywords
        self.soft_skills_keywords = [
            'communication', 'leadership', 'collaboration', 'teamwork', 'problem-solving',
            'analytical', 'creativity', 'adaptability', 'time management', 'organizational',
            'detail-oriented', 'self-motivated', 'autonomous', 'proactive', 'results-driven',
            'customer-focused', 'stakeholder management', 'mentoring', 'coaching'
        ]
    
    async def research_company(
        self, 
        company_name: str, 
        company_website: Optional[str] = None,
        use_browser: bool = True
    ) -> CompanyInfo:
        """
        Research a company comprehensively.
        
        Args:
            company_name: Company name
            company_website: Optional company website
            use_browser: Whether to use browser automation
            
        Returns:
            CompanyInfo object with research results
            
        Example:
            researcher = CompanyResearcher()
            info = await researcher.research_company("TechCorp", "https://techcorp.com")
        """
        info = CompanyInfo(name=company_name)
        
        try:
            logger.info(f"Starting company research for: {company_name}")
            
            # Search for company website if not provided
            if not company_website:
                company_website = await self._find_company_website(company_name)
            
            if company_website:
                info.website = company_website
                
                # Research company website
                if use_browser:
                    website_data = await self._scrape_with_browser(company_website)
                else:
                    website_data = await self._scrape_static(company_website)
                
                info = self._extract_company_info(website_data, info)
            
            # Research LinkedIn
            linkedin_data = await self._research_linkedin(company_name)
            if linkedin_data:
                info = self._merge_linkedin_data(info, linkedin_data)
            
            # Research Glassdoor
            glassdoor_data = await self._research_glassdoor(company_name)
            if glassdoor_data:
                info = self._merge_glassdoor_data(info, glassdoor_data)
            
            # Research Crunchbase
            crunchbase_data = await self._research_crunchbase(company_name)
            if crunchbase_data:
                info = self._merge_crunchbase_data(info, crunchbase_data)
            
            # Identify tech stack from various sources
            info.tech_stack = await self._identify_tech_stack(company_name, info.website)
            
            # Get recent news
            info.recent_news = await self._get_recent_news(company_name)
            
            logger.info(f"Company research complete for: {company_name}")
            return info
            
        except Exception as e:
            logger.error(f"Error researching company {company_name}: {e}")
            # Return partial data if available
            return info
    
    async def analyze_job_posting(
        self,
        job_url: Optional[str] = None,
        job_description: Optional[str] = None,
        use_browser: bool = True
    ) -> JobRequirements:
        """
        Analyze a job posting or description.
        
        Args:
            job_url: URL of job posting (optional if job_description provided)
            job_description: Raw job description text (optional if URL provided)
            use_browser: Whether to use browser automation for URL
            
        Returns:
            JobRequirements object
            
        Example:
            requirements = await researcher.analyze_job_posting(
                job_url="https://company.com/jobs/123"
            )
        """
        requirements = JobRequirements()
        
        try:
            if job_url:
                logger.info(f"Analyzing job posting: {job_url}")
                requirements.application_url = job_url
                
                if use_browser:
                    content = await self._scrape_job_with_browser(job_url)
                else:
                    content = await self._scrape_job_static(job_url)
                
                job_description = content.get('text', '')
                requirements.raw_text = job_description
                
                # Extract structured data
                requirements = self._parse_job_posting(job_description, requirements)
                
                # Try to extract company name from page
                if not requirements.company:
                    requirements.company = self._extract_company_from_job(content)
            
            elif job_description:
                logger.info("Analyzing job description text")
                requirements.description_full = job_description
                requirements.raw_text = job_description
                requirements = self._parse_job_posting(job_description, requirements)
            
            else:
                raise ValueError("Either job_url or job_description must be provided")
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error analyzing job posting: {e}")
            return requirements
    
    async def _find_company_website(self, company_name: str) -> Optional[str]:
        """Find company website through search."""
        # Use web_fetch or browser to search
        search_query = f"{company_name} official website"
        # This would integrate with search capabilities
        # For now, return common pattern
        domain = company_name.lower().replace(' ', '').replace(',', '').replace('.', '')
        return f"https://www.{domain}.com"
    
    async def _scrape_with_browser(self, url: str) -> Dict[str, Any]:
        """Scrape website using stealth browser."""
        # Integration with browser tool
        # This is a placeholder - actual implementation uses the browser automation
        return {
            'url': url,
            'text': '',
            'html': '',
            'title': ''
        }
    
    async def _scrape_static(self, url: str) -> Dict[str, Any]:
        """Scrape website using static requests."""
        # Use web_fetch tool
        return {
            'url': url,
            'text': '',
            'html': '',
            'title': ''
        }
    
    async def _scrape_job_with_browser(self, url: str) -> Dict[str, Any]:
        """Scrape job posting using browser automation."""
        # Placeholder for browser integration
        return {
            'text': '',
            'title': '',
            'structured_data': {}
        }
    
    async def _scrape_job_static(self, url: str) -> Dict[str, Any]:
        """Scrape job posting using static requests."""
        return {
            'text': '',
            'title': '',
            'structured_data': {}
        }
    
    def _extract_company_info(self, data: Dict, info: CompanyInfo) -> CompanyInfo:
        """Extract company information from scraped data."""
        text = data.get('text', '').lower()
        html = data.get('html', '').lower()
        
        # Extract mission/vision
        mission_patterns = [
            r'(?:our mission|mission statement|mission:?)\s*[.:–-]\s*([^\n]+(?:\n[^\n]+){0,5})',
            r'(?:we believe|we exist to)\s+([^\n]+(?:\n[^\n]+){0,5})'
        ]
        for pattern in mission_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info.mission = match.group(1).strip()
                break
        
        # Extract company size
        size_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s+(?:employees?|people|staff)',
            r'(\d{1,4}[\+\-]?)[\s-]*(employees?|people)',
            r'((?:\d+\s*-\s*\d+|\d+)\s+(?:employees?|people))'
        ]
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info.size = match.group(0)
                break
        
        # Extract founded year
        founded_pattern = r'(?:founded|established)\s+(?:in\s+)?(\d{4})'
        match = re.search(founded_pattern, text, re.IGNORECASE)
        if match:
            info.founded = match.group(1)
        
        # Extract headquarters
        hq_patterns = [
            r'(?:headquarters|hq|based in|located in)\s*[.:–-]\s*([^,\n]+(?:,\s*[^,\n]+))',
            r'(?:located in|based in)\s+([A-Za-z\s,]+?)(?:,|\s|$)'
        ]
        for pattern in hq_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info.headquarters = match.group(1).strip()
                break
        
        # Extract company values
        values_section = self._extract_section(text, ['values', 'our values', 'core values', 'principles'])
        if values_section:
            info.values = self._extract_list_items(values_section)[:10]
        
        # Extract benefits
        benefits_section = self._extract_section(text, ['benefits', 'perks', 'compensation', 'we offer'])
        if benefits_section:
            info.benefits = self._extract_list_items(benefits_section)[:15]
        
        return info
    
    def _extract_section(self, text: str, section_names: List[str]) -> str:
        """Extract a section from text."""
        for section_name in section_names:
            pattern = rf'(?:^|\n)(?:#{0,3}\s*)?{re.escape(section_name)}[:\s]*\n(.*?)(?:\n(?:#{1,3}|{re.escape(section_name)}|$)'
            for i in range(3):
                pattern = pattern.replace(f'#{i+1}', '#'*i)
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text."""
        items = []
        # Bullet points
        bullet_matches = re.findall(r'[•\-\*]\s*([^\n]+)', text)
        items.extend([m.strip() for m in bullet_matches if len(m.strip()) > 3])
        # Numbered lists
        numbered_matches = re.findall(r'\d+\.\s*([^\n]+)', text)
        items.extend([m.strip() for m in numbered_matches if len(m.strip()) > 3])
        # Comma-separated
        if len(items) < 3:
            items = [s.strip() for s in re.split(r'[,;]', text) if len(s.strip()) > 3]
        return items
    
    async def _research_linkedin(self, company_name: str) -> Optional[Dict]:
        """Research company on LinkedIn."""
        # Placeholder for LinkedIn research
        return {
            'url': f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}",
            'description': '',
            'size': '',
            'industry': ''
        }
    
    def _merge_linkedin_data(self, info: CompanyInfo, data: Dict) -> CompanyInfo:
        """Merge LinkedIn data into company info."""
        if data.get('url'):
            info.linkedin_url = data['url']
        if data.get('description') and not info.description:
            info.description = data['description']
        if data.get('industry') and not info.industry:
            info.industry = data['industry']
        if data.get('size') and not info.size:
            info.size = data['size']
        return info
    
    async def _research_glassdoor(self, company_name: str) -> Optional[Dict]:
        """Research company on Glassdoor."""
        return {
            'url': f"https://www.glassdoor.com/Overview/Working-at-{company_name.replace(' ', '-')}",
            'rating': None,
            'culture_description': ''
        }
    
    def _merge_glassdoor_data(self, info: CompanyInfo, data: Dict) -> CompanyInfo:
        """Merge Glassdoor data into company info."""
        if data.get('url'):
            info.glassdoor_url = data['url']
        if data.get('rating'):
            info.glassdoor_rating = data['rating']
        if data.get('culture_description') and not info.culture_description:
            info.culture_description = data['culture_description']
        return info
    
    async def _research_crunchbase(self, company_name: str) -> Optional[Dict]:
        """Research company on Crunchbase."""
        return {
            'url': f"https://www.crunchbase.com/organization/{company_name.lower().replace(' ', '-')}",
            'funding_stage': '',
            'revenue_range': ''
        }
    
    def _merge_crunchbase_data(self, info: CompanyInfo, data: Dict) -> CompanyInfo:
        """Merge Crunchbase data into company info."""
        if data.get('url'):
            info.crunchbase_url = data['url']
        if data.get('funding_stage'):
            info.funding_stage = data['funding_stage']
        if data.get('revenue_range'):
            info.revenue_range = data['revenue_range']
        return info
    
    async def _identify_tech_stack(self, company_name: str, website: str) -> List[str]:
        """Identify company tech stack from various sources."""
        tech_stack = []
        # This would analyze job postings, GitHub, StackShare, etc.
        return tech_stack
    
    async def _get_recent_news(self, company_name: str) -> List[Dict[str, str]]:
        """Get recent news about the company."""
        news = []
        # This would integrate with news search
        return news
    
    def _extract_company_from_job(self, data: Dict) -> str:
        """Extract company name from job posting."""
        # Try common patterns
        patterns = [
            r'(?:at|with)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s*-|\s*\||\s*$)',
            r'([A-Z][A-Za-z0-9\s&]{2,30})(?:\s*-|\s*is\s+hiring|\s*\|)'
        ]
        for pattern in patterns:
            match = re.search(pattern, data.get('title', ''), re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
    
    def _parse_job_posting(self, text: str, requirements: JobRequirements) -> JobRequirements:
        """Parse job posting text into structured requirements."""
        text_lower = text.lower()
        
        # Extract job title
        title_patterns = [
            r'^\s*([A-Za-z\s]+(?:Engineer|Developer|Manager|Director|Analyst|Designer|Specialist|Lead|Architect)[^\n]*)'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements.job_title = match.group(1).strip()
                break
        
        # Extract years of experience
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)-(\d+)\s*years?\s*(?:of\s*)?experience',
            r'(?:minimum|at least)\s*(\d+)\s*years?'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1 and match.group(2):
                    requirements.years_experience = f"{match.group(1)}-{match.group(2)}"
                else:
                    requirements.years_experience = match.group(1)
                break
        
        # Extract required skills
        req_section = self._extract_requirement_section(text, ['requirements', 'required', 'qualifications', 'must have'])
        if req_section:
            requirements.required_skills = self._extract_skills_from_text(req_section)
        
        # Extract preferred skills
        pref_section = self._extract_requirement_section(text, ['preferred', 'nice to have', 'bonus', 'plus'])
        if pref_section:
            requirements.preferred_skills = self._extract_skills_from_text(pref_section)
        
        # Extract responsibilities
        resp_section = self._extract_requirement_section(text, ['responsibilities', 'what you\'ll do', 'role', 'the job'])
        if resp_section:
            requirements.responsibilities = self._extract_list_items(resp_section)[:10]
        
        # Extract education
        edu_patterns = [
            r'(bachelor|master|phd|doctorate)[\'s]?\s*(?:degree)?\s*(?:in\s+([A-Za-z\s]+))?',
            r'degree\s+in\s+([A-Za-z\s]+)'
        ]
        for pattern in edu_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements.education_required = match.group(0)
                break
        
        # Extract employment type
        type_patterns = [
            r'\b(full-time|part-time|contract|contractor|freelance|internship)\b'
        ]
        for pattern in type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements.employment_type = match.group(1).capitalize()
                break
        
        # Extract remote policy
        remote_patterns = [
            r'\b(remote|hybrid|on-site|onsite|in-office)\b'
        ]
        for pattern in remote_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements.remote_policy = match.group(1).capitalize()
                break
        
        # Extract all key keywords
        requirements.key_keywords = self._extract_all_keywords(text)
        
        # Extract emphasized soft skills
        requirements.soft_skills_emphasized = self._extract_soft_skills(text)
        
        return requirements
    
    def _extract_requirement_section(self, text: str, section_names: List[str]) -> str:
        """Extract a requirements section."""
        return self._extract_section(text, section_names)
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text."""
        skills = []
        text_lower = text.lower()
        
        for skill in self.tech_keywords + self.soft_skills_keywords:
            if skill in text_lower:
                # Check if standalone word
                if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                    if skill not in skills:
                        skills.append(skill)
        
        return skills
    
    def _extract_all_keywords(self, text: str) -> List[str]:
        """Extract all keywords from job description."""
        keywords = []
        
        # Technical skills
        for skill in self.tech_keywords:
            if re.search(rf'\b{re.escape(skill.lower())}\b', text.lower()):
                if skill not in keywords:
                    keywords.append(skill)
        
        # Action verbs and keywords
        action_words = [
            'build', 'design', 'implement', 'optimize', 'lead', 'collaborate',
            'analyze', 'develop', 'maintain', 'scale', 'deploy', 'automate',
            'integrate', 'architect', 'mentor', 'manage', 'monitor'
        ]
        
        for word in action_words:
            if re.search(rf'\b{word}[sedimg]*\b', text, re.IGNORECASE):
                if word not in keywords:
                    keywords.append(word)
        
        return keywords[:20]
    
    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract emphasized soft skills."""
        skills = []
        text_lower = text.lower()
        
        for skill in self.soft_skills_keywords:
            if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                skills.append(skill)
        
        return skills
    
    def to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        return asdict(obj)
    
    def to_json(self, obj: Any, indent: int = 2) -> str:
        """Convert object to JSON string."""
        return json.dumps(self.to_dict(obj), indent=indent, default=str)


class CompanyResearchError(Exception):
    """Custom exception for company research errors."""
    pass


async def research_company(
    company_name: str,
    company_website: Optional[str] = None
) -> CompanyInfo:
    """
    Convenience function to research a company.
    
    Args:
        company_name: Company name
        company_website: Optional company website
        
    Returns:
        CompanyInfo object
    """
    researcher = CompanyResearcher()
    return await researcher.research_company(company_name, company_website)


async def analyze_job_posting(job_url: Optional[str] = None, job_description: Optional[str] = None) -> JobRequirements:
    """
    Convenience function to analyze a job posting.
    
    Args:
        job_url: URL of job posting
        job_description: Raw job description text
        
    Returns:
        JobRequirements object
    """
    researcher = CompanyResearcher()
    return await researcher.analyze_job_posting(job_url, job_description)


if __name__ == "__main__":
    # Example usage
    async def main():
        researcher = CompanyResearcher()
        
        # Research example company
        company = await researcher.research_company("Example Tech Corp")
        print(researcher.to_json(company))
        
        # Analyze example job posting
        job_desc = """
        Senior Software Engineer - Machine Learning Platform
        
        TechCorp Inc. is looking for a Senior Software Engineer to join our ML Platform team.
        
        Requirements:
        • 5+ years of software engineering experience
        • Strong Python skills and experience with TensorFlow or PyTorch
        • Experience with cloud platforms (AWS, GCP)
        • Knowledge of Docker and Kubernetes
        
        Preferred:
        • Experience with Kafka and data streaming
        • Familiarity with MLOps practices
        
        Responsibilities:
        • Build and maintain ML infrastructure
        • Collaborate with data scientists to deploy models
        • Optimize model performance and scalability
        
        We offer:
        • Competitive salary
        • Remote-first culture
        • Professional development budget
        • Comprehensive health benefits
        """
        
        requirements = await researcher.analyze_job_posting(job_description=job_desc)
        print(researcher.to_json(requirements))
    
    asyncio.run(main())
