#!/usr/bin/env python3
"""
ATS Optimizer Module
Optimizes CV content for Applicant Tracking Systems.
Matches CV to job posting keywords and improves ATS compatibility.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter


class ATSOptimizer:
    """
    ATS (Applicant Tracking System) content optimizer.
    
    Analyzes job postings and CV content to:
    - Match keywords for ATS compatibility
    - Suggest improvements for better screening scores
    - Reformat content for ATS parsing
    - Identify missing requirements
    """
    
    def __init__(self):
        self.common_header_fields = [
            'contact', 'summary', 'objective', 'experience', 'education',
            'skills', 'certifications', 'awards', 'publications'
        ]
        
        self.ats_stop_words = [
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would'
        ]
    
    def analyze_job_posting(self, job_text: str) -> Dict[str, Any]:
        """
        Extract keywords and requirements from job posting.
        
        Args:
            job_text: Raw job posting text
            
        Returns:
            Dict with keywords, requirements, and priority terms
        """
        analysis = {
            'keywords': [],
            'required_skills': [],
            'preferred_skills': [],
            'experience_requirements': [],
            'education_requirements': [],
            'certifications': [],
            'job_title': '',
            'company': '',
            'priority_keywords': []
        }
        
        # Extract job title (usually first line or in header)
        lines = job_text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith('http'):
                if not analysis['job_title']:
                    analysis['job_title'] = line
                break
        
        # Find company name
        company_patterns = [
            r'(?:at|with|join)\s+([A-Z][A-Za-z\s]+(?:Inc|LLC|Ltd|Corp|Company)?)',
            r'^([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*)\s+(?:is hiring|seeks|looking)'
        ]
        for pattern in company_patterns:
            match = re.search(pattern, job_text, re.IGNORECASE | re.MULTILINE)
            if match:
                analysis['company'] = match.group(1).strip()
                break
        
        # Extract required skills
        required_section = re.search(
            r'(?:requirements?|required|qualifications?):[\s\S]*?(?:preferred|responsibilities|about|\Z)',
            job_text, re.IGNORECASE
        )
        if required_section:
            req_text = required_section.group(0).lower()
            # Look for bullet points
            req_items = re.findall(r'[\-•]\s*([^.\n]+)', req_text)
            for item in req_items:
                if len(item) < 150:
                    analysis['required_skills'].append(item.strip())
        
        # Extract preferred skills
        preferred_section = re.search(
            r'(?:preferred|nice to have|bonus):[\s\S]*?(?:\n\n|\Z)',
            job_text, re.IGNORECASE
        )
        if preferred_section:
            pref_text = preferred_section.group(0).lower()
            pref_items = re.findall(r'[\-•]\s*([^.\n]+)', pref_text)
            for item in pref_items:
                if len(item) < 150:
                    analysis['preferred_skills'].append(item.strip())
        
        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:work\s+)?experience',
            r'(?:minimum|at least)\s+(\d+)\s+years'
        ]
        for pattern in exp_patterns:
            matches = re.finditer(pattern, job_text, re.IGNORECASE)
            for match in matches:
                years = match.group(1)
                analysis['experience_requirements'].append(f"{years} years")
        
        # Extract education requirements
        edu_patterns = [
            r'(bachelor|master|phd|doctorate|degree)',
            r'(bs?|ms?|mba|phd)\s+(?:in|degree|required)'
        ]
        for pattern in edu_patterns:
            matches = re.finditer(pattern, job_text, re.IGNORECASE)
            for match in matches:
                edu = match.group(1).strip()
                if edu not in analysis['education_requirements']:
                    analysis['education_requirements'].append(edu)
        
        # Generate keywords from posting
        analysis['keywords'] = self._extract_keywords(job_text)
        
        # Priority keywords (mentioned more frequently)
        word_freq = Counter(word.lower() for word in re.findall(r'\b[A-Za-z]+\b', job_text))
        priority = [word for word, count in word_freq.most_common(20) 
                   if len(word) > 3 and word not in self.ats_stop_words]
        analysis['priority_keywords'] = [p.title() for p in priority[:10]]
        
        return analysis
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Common technical and soft skills
        keywords = [
            'python', 'javascript', 'java', 'react', 'node', 'aws', 'azure',
            'docker', 'kubernetes', 'sql', 'nosql', 'mongodb', 'postgresql',
            'agile', 'scrum', 'kanban', 'ci/cd', 'devops', 'cloud',
            'leadership', 'management', 'communication', 'teamwork',
            'analytics', 'data', 'machine learning', 'ai', 'blockchain',
            'microservices', 'api', 'rest', 'graphql', 'frontend', 'backend'
        ]
        
        text_lower = text.lower()
        found = [kw for kw in keywords if kw in text_lower]
        return found
    
    def match_cv_to_job(self, cv_data: Dict, job_analysis: Dict) -> Dict[str, Any]:
        """
        Match CV data to job requirements.
        
        Returns:
            Match score and recommendations
        """
        cv_text = json.dumps(cv_data).lower()
        
        match_results = {
            'overall_match': 0,
            'keyword_score': 0,
            'experience_match': False,
            'education_match': False,
            'missing_keywords': [],
            'present_keywords': [],
            'recommendations': []
        }
        
        # Keyword matching
        job_keywords = set(kw.lower() for kw in job_analysis['keywords'])
        present = []
        missing = []
        
        for kw in job_keywords:
            if kw in cv_text:
                present.append(kw)
            else:
                missing.append(kw)
        
        match_results['present_keywords'] = present
        match_results['missing_keywords'] = missing
        match_results['keyword_score'] = int((len(present) / len(job_keywords)) * 100) if job_keywords else 100
        
        # Experience matching (simplified)
        cv_experience = cv_data.get('experience', [])
        years_pattern = r'(\d+)\s*years?'
        total_years = 0
        for exp in cv_experience:
            for match in re.finditer(years_pattern, str(exp).lower()):
                years = int(match.group(1))
                if years < 50:  # Sanity check
                    total_years += years
        
        req_exp = job_analysis.get('experience_requirements', [])
        if req_exp:
            req_years = 0
            for req in req_exp:
                match = re.search(r'(\d+)', req)
                if match:
                    req_years = int(match.group(1))
            match_results['experience_match'] = total_years >= req_years
        
        # Education matching (simplified)
        cv_education = cv_data.get('education', [])
        req_edu = job_analysis.get('education_requirements', [])
        if req_edu:
            edu_match = any(req.lower() in str(cv_education).lower() for req in req_edu)
            match_results['education_match'] = edu_match
        
        # Overall score
        scores = [match_results['keyword_score']]
        if match_results['experience_match']:
            scores.append(100)
        if match_results['education_match']:
            scores.append(100)
        
        match_results['overall_match'] = int(sum(scores) / len(scores))
        
        # Generate recommendations
        match_results['recommendations'] = self._generate_recommendations(
            match_results, job_analysis
        )
        
        return match_results
    
    def _generate_recommendations(self, match_results: Dict, job_analysis: Dict) -> List[str]:
        """Generate optimization recommendations."""
        recs = []
        
        # Keyword recommendations
        if match_results['missing_keywords']:
            recs.append(f"Add keywords: {', '.join(match_results['missing_keywords'][:5])}")
        
        # Experience recommendations
        if not match_results['experience_match']:
            req_years = 'X'
            for req in job_analysis.get('experience_requirements', []):
                match = re.search(r'\d+', req)
                if match:
                    req_years = match.group(0)
            recs.append(f"Highlight {req_years}+ years of relevant experience")
        
        # Education recommendations
        if not match_results['education_match'] and job_analysis.get('education_requirements'):
            recs.append(f"Mention degree: {', '.join(job_analysis['education_requirements'])}")
        
        # Formatting recommendations
        recs.append("Use standard section headers (Experience, Education, Skills)")
        recs.append("Avoid tables, headers/footers, and images")
        recs.append("Save as .docx or .pdf with selectable text")
        
        return recs
    
    def optimize_content(self, cv_data: Dict, job_analysis: Dict) -> Dict[str, Any]:
        """
        Generate optimized CV content for this job.
        
        Returns:
            Optimized content suggestions
        """
        optimization = {
            'suggested_summary': '',
            'skill_section': [],
            'experience_bullets': [],
            'key_achievements': [],
            'keyword_density': {}
        }
        
        # Suggest summary incorporating key requirements
        job_title = job_analysis.get('job_title', 'this position')
        skills = cv_data.get('skills', [])[:5]
        optimization['suggested_summary'] = (
            f"Experienced professional seeking {job_title}. "
            f"Expert in {', '.join(skills)}. "
            f"Proven track record of delivering results."
        )
        
        # Suggest skill section ordering
        priority_skills = job_analysis.get('priority_keywords', [])
        cv_skills = cv_data.get('skills', [])
        optimization['skill_section'] = [
            s for s in cv_skills if s.lower() in [k.lower() for k in priority_skills]
        ] + [s for s in cv_skills if s not in priority_skills]
        
        return optimization
    
    def check_ats_compatibility(self, cv_text: str) -> Dict[str, Any]:
        """
        Check CV format for ATS compatibility.
        
        Returns:
            Compatibility report with issues found
        """
        report = {
            'compatible': True,
            'issues': [],
            'recommendations': []
        }
        
        # Check for problematic formatting
        if re.search(r'\b[A-Z]{2,}\b', cv_text):
            # Might be headers
            pass
        
        # Check file format recommendation
        report['recommendations'].append("Use .docx or .pdf format")
        report['recommendations'].append("Ensure text is selectable (not image-based)")
        report['recommendations'].append("Use standard fonts: Arial, Calibri, Times New Roman")
        
        # Check for tables
        if '|' in cv_text or '\t\t' in cv_text:
            report['issues'].append("Tables detected - may not parse correctly in some ATS")
        
        # Check for images
        report['recommendations'].append("Avoid images and graphics")
        
        # Check section headers
        has_standard_headers = any(
            header in cv_text.lower() 
            for header in ['experience', 'education', 'skills']
        )
        if not has_standard_headers:
            report['issues'].append("Non-standard section headers may not parse correctly")
        
        report['compatible'] = len(report['issues']) == 0
        
        return report


def main():
    """CLI interface for ATS optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimize CV for ATS')
    parser.add_argument('--cv', required=True, help='Path to CV analysis JSON')
    parser.add_argument('--job', required=True, help='Path to job posting text file')
    parser.add_argument('--output', '-o', default='ats_report.json', help='Output file')
    args = parser.parse_args()
    
    # Load data
    cv_data = json.loads(Path(args.cv).read_text())
    job_text = Path(args.job).read_text()
    
    # Analyze
    optimizer = ATSOptimizer()
    job_analysis = optimizer.analyze_job_posting(job_text)
    match_results = optimizer.match_cv_to_job(cv_data, job_analysis)
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'job_analysis': job_analysis,
            'match_results': match_results
        }, f, indent=2)
    
    print(f"✓ ATS analysis complete. Results: {output_path}")
    print(f"  Match Score: {match_results['overall_match']}%")
    print(f"  Keywords Matched: {len(match_results['present_keywords'])}/{len(match_results['present_keywords']) + len(match_results['missing_keywords'])}")
    print(f"  Top Recommendations:")
    for rec in match_results['recommendations'][:3]:
        print(f"    - {rec}")
    
    return 0


if __name__ == '__main__':
    exit(main())
