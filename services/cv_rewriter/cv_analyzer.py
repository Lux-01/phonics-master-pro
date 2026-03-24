#!/usr/bin/env python3
"""
CV Analyzer Module
Extracts structured data from CV text using pattern matching and NLP.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CVData:
    """Structured CV data."""
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    summary: str = ""
    skills: List[str] = None
    experience: List[Dict] = None
    education: List[Dict] = None
    certifications: List[str] = None
    achievements: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []
        if self.achievements is None:
            self.achievements = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CVAnalyzer:
    """Analyzes CV text and extracts structured information."""
    
    def __init__(self):
        self.skill_keywords = self._load_skill_keywords()
    
    def _load_skill_keywords(self) -> set:
        """Load common technical and soft skills."""
        return {
            'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++', 'c#',
            'react', 'vue', 'angular', 'node.js', 'django', 'flask', 'fastapi',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            'ci/cd', 'jenkins', 'github actions', 'gitlab', 'git',
            'machine learning', 'deep learning', 'ai', 'data science',
            'leadership', 'management', 'communication', 'teamwork', 'agile'
        }
    
    def analyze(self, cv_text: str) -> CVData:
        """
        Analyze CV text and extract all relevant information.
        
        Args:
            cv_text: Raw CV text content
            
        Returns:
            CVData object with extracted information
        """
        data = CVData()
        
        # Extract contact info
        data.name = self._extract_name(cv_text)
        data.email = self._extract_email(cv_text)
        data.phone = self._extract_phone(cv_text)
        data.linkedin = self._extract_linkedin(cv_text)
        
        # Extract sections
        data.summary = self._extract_summary(cv_text)
        data.skills = self._extract_skills(cv_text)
        data.experience = self._extract_experience(cv_text)
        data.education = self._extract_education(cv_text)
        data.certifications = self._extract_certifications(cv_text)
        data.achievements = self._extract_achievements(cv_text)
        
        return data
    
    def _extract_name(self, text: str) -> str:
        """Extract name from CV header."""
        lines = text.strip().split('\n')
        # First non-empty line is usually the name
        for line in lines[:5]:
            line = line.strip()
            if line and not any(x in line.lower() for x in ['@', 'http', 'phone', 'email']):
                if len(line.split()) <= 4:  # Name is usually 2-4 words
                    return line
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number."""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+\d{1,3}\s?\d{4,}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL."""
        pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        match = re.search(pattern, text)
        return f"https://www.{match.group(0)}" if match else ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective."""
        patterns = [
            r'(?:Summary|Profile|Objective|About Me)[\s\S]*?(?=\n\n|\n[A-Z]|$)',
            r'(?:PROFESSIONAL SUMMARY|PROFILE)[\s\S]*?(?=\n\n|\n[A-Z]{2,}|$)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                summary = match.group(0).replace('Summary', '').replace('Profile', '').strip(': \n')
                if len(summary) > 50:
                    return summary[:500]
        return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills section and find keyword matches."""
        skills = []
        
        # Look for skills section
        skill_section_match = re.search(
            r'(?:Skills|Technical Skills|Core Competencies)[\s\S]*?(?=\n\n|\n[A-Z]{2,}|$)',
            text, re.IGNORECASE
        )
        
        if skill_section_match:
            section = skill_section_match.group(0).lower()
            for skill in self.skill_keywords:
                if skill in section:
                    skills.append(skill.title())
        
        # Also search entire text for skill keywords
        text_lower = text.lower()
        for skill in self.skill_keywords:
            if skill in text_lower and skill.title() not in skills:
                skills.append(skill.title())
        
        return sorted(list(set(skills)))
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience."""
        experiences = []
        
        # Find experience section
        exp_match = re.search(
            r'(?:Experience|Work Experience|Professional Experience)[\s\S]*?(?=\n\n[A-Z]|Education|Skills|$)',
            text, re.IGNORECASE
        )
        
        if exp_match:
            section = exp_match.group(0)
            # Split by job entries (title + company pattern)
            job_entries = re.split(r'\n(?=[A-Z][a-z]+.*?\n[A-Z])', section)
            
            for entry in job_entries[1:]:  # Skip header
                exp = self._parse_job_entry(entry)
                if exp.get('title') or exp.get('company'):
                    experiences.append(exp)
        
        return experiences
    
    def _parse_job_entry(self, entry: str) -> Dict:
        """Parse individual job entry."""
        lines = entry.strip().split('\n')
        job = {
            'title': '',
            'company': '',
            'duration': '',
            'description': []
        }
        
        if lines:
            # First line usually has title
            job['title'] = lines[0].strip()
            if len(lines) > 1:
                job['company'] = lines[1].strip()
            # Look for date patterns
            date_pattern = r'(?:19|20)\d{2}[-\s]?(?:Present|(?:19|20)\d{2})'
            for line in lines:
                if re.search(date_pattern, line):
                    job['duration'] = line.strip()
                    break
            # Remaining lines are description
            job['description'] = [l.strip() for l in lines[2:] if l.strip()]
        
        return job
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education history."""
        education = []
        
        edu_match = re.search(
            r'(?:Education|Academic Background)[\s\S]*?(?=\n\n[A-Z]|Experience|Skills|$)',
            text, re.IGNORECASE
        )
        
        if edu_match:
            section = edu_match.group(0)
            lines = section.split('\n')
            
            edu = {}
            for line in lines[1:]:  # Skip header
                line = line.strip()
                if not line:
                    if edu:
                        education.append(edu)
                        edu = {}
                    continue
                    
                # Look for degree patterns
                if any(x in line.lower() for x in ['bachelor', 'master', 'phd', 'degree']):
                    edu['degree'] = line
                elif 'university' in line.lower() or 'college' in line.lower():
                    edu['institution'] = line
                elif re.search(r'(?:19|20)\d{2}', line):
                    edu['year'] = line
            
            if edu:
                education.append(edu)
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications."""
        certs = []
        
        cert_match = re.search(
            r'(?:Certifications?|Licenses?|Training)[\s\S]*?(?=\n\n[A-Z]|$)',
            text, re.IGNORECASE
        )
        
        if cert_match:
            section = cert_match.group(0)
            lines = section.split('\n')[1:]  # Skip header
            for line in lines:
                line = line.strip('- •\n ')
                if line and len(line) > 5:
                    certs.append(line)
        
        return certs
    
    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and accomplishments."""
        achievements = []
        
        # Look for achievement patterns in descriptions
        achievement_patterns = [
            r'(?:achieved|improved|increased|decreased|reduced|grew|delivered).*?(?:\d+%|\$\d+|by \d+)',
            r'(?:led|managed|developed|created|built).*?(?:\d+).*?(?:team|project|system)',
            r'(?:won|awarded|recognized|featured|published|speaking)'
        ]
        
        for pattern in achievement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                achievement = match.group(0).strip()
                if len(achievement) > 20 and achievement not in achievements:
                    achievements.append(achievement)
        
        return achievements[:10]  # Limit to 10 achievements


def main():
    """CLI interface for CV analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze CV and extract data')
    parser.add_argument('--input', '-i', required=True, help='Path to CV file')
    parser.add_argument('--output', '-o', default='cv_analysis.json', help='Output JSON file')
    args = parser.parse_args()
    
    # Read CV file
    cv_path = Path(args.input)
    if not cv_path.exists():
        print(f"Error: File not found: {cv_path}")
        return 1
    
    cv_text = cv_path.read_text(encoding='utf-8')
    
    # Analyze
    analyzer = CVAnalyzer()
    cv_data = analyzer.analyze(cv_text)
    
    # Save results
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data.to_dict(), f, indent=2)
    
    print(f"✓ Analysis complete. Results saved to: {output_path}")
    print(f"  Name: {cv_data.name}")
    print(f"  Email: {cv_data.email}")
    print(f"  Skills found: {len(cv_data.skills)}")
    print(f"  Experience entries: {len(cv_data.experience)}")
    
    return 0


if __name__ == '__main__':
    exit(main())
