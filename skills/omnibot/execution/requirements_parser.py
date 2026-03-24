#!/usr/bin/env python3
"""
Requirements Parser - Extract structured requirements from client text.

Workflow:
1. Parse client requirements text
2. Extract deliverables, timelines, constraints
3. Identify ambiguous areas needing clarification
4. Generate task breakdown
5. Estimate effort and complexity
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set


@dataclass
class ParsedRequirement:
    """A single parsed requirement."""
    requirement_id: str
    type: str  # 'functional', 'technical', 'design', 'constraint'
    description: str
    priority: str  # 'must_have', 'should_have', 'nice_to_have'
    complexity: str  # 'low', 'medium', 'high', 'unknown'
    depends_on: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ParsedProject:
    """Complete parsed project structure."""
    project_title: str
    description: str
    domain: str  # 'web', 'mobile', 'data', 'api', etc.
    scope: Dict[str, Any]
    timeline: Dict[str, Any]
    tech_stack: List[str]
    deliverables: List[ParsedRequirement]
    constraints: List[ParsedRequirement]
    ambiguities: List[str]
    confidence: float  # 0-1


class AmbiguityDetector:
    """Detect ambiguous requirements."""
    
    AMBIGUOUS_TERMS = [
        "etc", "and so on", "something like", "maybe", "probably",
        "user-friendly", "easy to use", "modern", "professional",
        "etc.", "...", "similar to", "like", "etcetera",
        "fast", "quick", "simple", "advanced"
    ]
    
    VAGUE_QUANTIFIERS = [
        "some", "a few", "several", "many", "most", "few",
        "more", "less", "better", "improved"
    ]
    
    def find_ambiguities(self, text: str) -> List[Dict[str, Any]]:
        """Find ambiguous phrases in text."""
        ambiguities = []
        text_lower = text.lower()
        lines = text.split('\n')
        
        for term in self.AMBIGUOUS_TERMS:
            if term.lower() in text_lower:
                # Find line number
                for i, line in enumerate(lines):
                    if term.lower() in line.lower():
                        ambiguities.append({
                            'term': term,
                            'line': i + 1,
                            'context': line.strip()[:100],
                            'severity': 'medium'
                        })
                        break
        
        # Check for missing numbers/quantities
        number_pattern = re.compile(r'\$?\d+')
        if not number_pattern.search(text) and 'budget' in text_lower:
            ambiguities.append({
                'term': 'budget',
                'line': 0,
                'context': 'No budget specified',
                'severity': 'high'
            })
        
        return ambiguities


class TechnologyExtractor:
    """Extract technology mentions from requirements."""
    
    TECH_PATTERNS = {
        'languages': ['python', 'javascript', 'typescript', 'java', 'c#', 'c++', 'go', 'rust', 'php', 'ruby'],
        'frontend': ['react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt', 'html', 'css', 'tailwind', 'bootstrap'],
        'backend': ['node.js', 'django', 'flask', 'fastapi', 'express', 'spring', 'laravel'],
        'databases': ['postgresql', 'mysql', 'mongodb', 'sqlite', 'redis', 'dynamodb', 'firebase'],
        'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'vercel', 'netlify'],
        'ai_ml': ['tensorflow', 'pytorch', 'scikit-learn', 'hugging face', 'openai', 'llm', 'ai', 'ml'],
        'mobile': ['react native', 'flutter', 'ios', 'android', 'swift', 'kotlin'],
        'devops': ['docker', 'kubernetes', 'jenkins', 'github actions', 'ci/cd', 'terraform']
    }
    
    def extract(self, text: str) -> Dict[str, Set[str]]:
        """Extract technologies mentioned in text."""
        found = {category: set() for category in self.TECH_PATTERNS.keys()}
        text_lower = text.lower()
        
        for category, technologies in self.TECH_PATTERNS.items():
            for tech in technologies:
                # Check for exact match or word boundary match
                tech_pattern = re.compile(r'\b' + re.escape(tech) + r'\b', re.IGNORECASE)
                if tech_pattern.search(text):
                    found[category].add(tech)
        
        return {k: list(v) for k, v in found.items()}


class ScopeEstimator:
    """Estimate project scope from requirements."""
    
    COMPLEXITY_INDICATORS = {
        'high': [
            'microservices', 'distributed', 'scalable', 'real-time', 'machine learning',
            'ai', 'blockchain', 'payment processing', 'authentication', 'sso',
            'integrat', 'third-party', 'api', 'data pipeline', 'etl'
        ],
        'medium': [
            'dashboard', 'api', 'database', 'user management', 'authentication',
            'responsive', 'mobile', 'email', 'notifications', 'reports'
        ],
        'low': [
            'landing page', 'static', 'brochure', 'simple', 'basic',
            'contact form', 'gallery', 'portfolio'
        ]
    }
    
    def estimate_complexity(self, text: str, features: List[str]) -> Dict[str, Any]:
        """Estimate project complexity."""
        text_lower = text.lower()
        
        complexity_score = 0
        reasons = []
        
        # Check for complexity indicators
        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if level == 'high':
                        complexity_score += 3
                        reasons.append(f"Advanced feature: {indicator}")
                    elif level == 'medium':
                        complexity_score += 1
                        reasons.append(f"Mid-complexity: {indicator}")
                    else:
                        complexity_score -= 0.5
        
        # Estimate by feature count
        if len(features) <= 3:
            complexity_score += 1
        elif len(features) <= 7:
            complexity_score += 2
        else:
            complexity_score += 3
            reasons.append(f"High feature count ({len(features)} features)")
        
        # Determine level
        if complexity_score >= 6:
            level = 'high'
            estimated_hours = (80, 200)
            estimated_weeks = (4, 10)
        elif complexity_score >= 3:
            level = 'medium'
            estimated_hours = (30, 80)
            estimated_weeks = (2, 4)
        else:
            level = 'low'
            estimated_hours = (10, 30)
            estimated_weeks = (1, 2)
        
        return {
            'level': level,
            'score': complexity_score,
            'reasons': reasons[:5],  # Top 5
            'estimated_hours': estimated_hours,
            'estimated_weeks': estimated_weeks
        }


class RequirementsParser:
    """
    Parse client requirements into structured project definition.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.RequirementsParser")
        
        # Data directory for any caching
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "parser_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-components
        self.ambiguity_detector = AmbiguityDetector()
        self.tech_extractor = TechnologyExtractor()
        self.scope_estimator = ScopeEstimator()
        
        self.logger.info("RequirementsParser initialized")
    
    def parse(self, requirements_text: str, project_title: str = "Untitled Project") -> ParsedProject:
        """
        Parse requirements text into structured project.
        
        Args:
            requirements_text: Raw requirements from client
            project_title: Project title or name
            
        Returns:
            ParsedProject with all extracted information
        """
        self.logger.info(f"Parsing requirements for project: {project_title}")
        
        if not requirements_text or not requirements_text.strip():
            raise ValueError("Requirements text cannot be empty")
        
        # Extract domain
        domain = self._detect_domain(requirements_text)
        
        # Extract features/deliverables
        deliverables = self._extract_deliverables(requirements_text)
        
        # Extract constraints
        constraints = self._extract_constraints(requirements_text)
        
        # Detect ambiguities
        ambiguities = self.ambiguity_detector.find_ambiguities(requirements_text)
        
        # Extract technologies
        tech_stack_info = self.tech_extractor.extract(requirements_text)
        tech_stack = []
        for category, items in tech_stack_info.items():
            tech_stack.extend(items)
        
        # Estimate scope
        feature_list = [d.description for d in deliverables]
        scope = self.scope_estimator.estimate_complexity(requirements_text, feature_list)
        
        # Extract timeline hints
        timeline = self._extract_timeline(requirements_text)
        
        # Calculate confidence
        confidence = self._calculate_confidence(ambiguities, scope['level'])
        
        project = ParsedProject(
            project_title=project_title,
            description=requirements_text[:500],
            domain=domain,
            scope=scope,
            timeline=timeline,
            tech_stack=tech_stack,
            deliverables=deliverables,
            constraints=constraints,
            ambiguities=[a['term'] for a in ambiguities],
            confidence=confidence
        )
        
        return project
    
    def _detect_domain(self, text: str) -> str:
        """Detect the project domain."""
        text_lower = text.lower()
        
        # Check patterns
        domain_scores = {
            'web': 0,
            'mobile': 0,
            'api': 0,
            'data': 0,
            'ai_ml': 0,
            'ecommerce': 0
        }
        
        # Web indicators
        if any(w in text_lower for w in ['website', 'web app', 'frontend', 'ui', 'dashboard']):
            domain_scores['web'] += 1
        
        # Mobile indicators
        if any(m in text_lower for m in ['mobile', 'ios', 'android', 'app', 'react native', 'flutter']):
            domain_scores['mobile'] += 1
        
        # API indicators
        if any(a in text_lower for a in ['api', 'rest', 'graphql', 'endpoint', 'backend']):
            domain_scores['api'] += 1
        
        # Data indicators
        if any(d in text_lower for d in ['data', 'pipeline', 'etl', 'analytics', 'report']):
            domain_scores['data'] += 1
        
        # AI/ML indicators
        if any(ai in text_lower for ai in ['ai', 'ml', 'machine learning', 'model', 'predict']):
            domain_scores['ai_ml'] += 1
        
        # E-commerce indicators
        if any(e in text_lower for e in ['e-commerce', 'shop', 'payment', 'cart', 'checkout']):
            domain_scores['ecommerce'] += 1
        
        # Get highest scoring domain
        max_domain = max(domain_scores, key=domain_scores.get)
        if domain_scores[max_domain] > 0:
            return max_domain
        
        return 'web'  # Default
    
    def _extract_deliverables(self, text: str) -> List[ParsedRequirement]:
        """Extract deliverables from requirements text."""
        deliverables = []
        req_id = 0
        
        # Look for bullet points and numbered lists
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for requirement-like statements
            # Bullet points, dashes, numbers
            if re.match(r'^[\•\-\*\d\.)]+\s+', line) and len(line) > 10:
                req_id += 1
                
                # Determine priority
                priority = 'must_have'
                if any(m in line.lower() for m in ['optional', 'if time', 'nice']):
                    priority = 'nice_to_have'
                elif any(s in line.lower() for s in ['should', 'prefer', 'ideally']):
                    priority = 'should_have'
                
                # Determine complexity
                complexity = 'medium'
                line_lower = line.lower()
                if any(c in line_lower for c in ['simple', 'basic', 'easy']):
                    complexity = 'low'
                elif any(c in line_lower for c in ['complex', 'advanced', 'difficult', 'integration']):
                    complexity = 'high'
                
                deliverables.append(ParsedRequirement(
                    requirement_id=f"REQ-{req_id:03d}",
                    type='functional',
                    description=line[:200],
                    priority=priority,
                    complexity=complexity
                ))
        
        # If no structured requirements found, create a single one
        if not deliverables:
            deliverables.append(ParsedRequirement(
                requirement_id="REQ-001",
                type='functional',
                description=text[:200],
                priority='must_have',
                complexity='unknown'
            ))
        
        return deliverables
    
    def _extract_constraints(self, text: str) -> List[ParsedRequirement]:
        """Extract constraints from text."""
        constraints = []
        constraint_patterns = [
            r'budget\s*(?:is|:)?\s*\$?\d+(?:\s*-\s*\$?\d+)?',
            r'deadline\s*(?:is|:)?\s*\w+',
            r'(by|before)\s+(?:the\s+)?(?:end\s+of\s+)?\w+',
            r'must\s+use\s+\w+',
            r'compatible\s+with\s+\w+',
            r'only\s+\w+',
        ]
        
        lines = text.split('\n')
        req_id = 0
        
        for line in lines:
            line_lower = line.lower()
            
            for pattern in constraint_patterns:
                if re.search(pattern, line_lower):
                    req_id += 1
                    constraints.append(ParsedRequirement(
                        requirement_id=f"CON-{req_id:03d}",
                        type='constraint',
                        description=line.strip()[:200],
                        priority='must_have',
                        complexity='unknown'
                    ))
                    break  # Don't double-count
        
        return constraints
    
    def _extract_timeline(self, text: str) -> Dict[str, Any]:
        """Extract timeline hints from text."""
        timeline_hints = {
            'has_deadline': False,
            'deadline_date': None,
            'urgency': 'normal'  # 'low', 'normal', 'high'
        }
        
        text_lower = text.lower()
        
        # Check for urgency words
        if any(u in text_lower for u in ['urgent', 'asap', 'immediately', 'rush']):
            timeline_hints['urgency'] = 'high'
        elif any(u in text_lower for u in ['flexible', 'no rush', 'whenever']):
            timeline_hints['urgency'] = 'low'
        
        # Check for timeframes
        timeframes = re.findall(r'(\d+)\s*(day|week|month)', text_lower)
        if timeframes:
            timeline_hints['suggested_duration'] = ' '.join(timeframes[0])
        
        return timeline_hints
    
    def _calculate_confidence(self, ambiguities: List[Dict], complexity: str) -> float:
        """Calculate parsing confidence."""
        confidence = 1.0
        
        # Reduce confidence for ambiguities
        confidence -= len(ambiguities) * 0.1
        
        # Reduce confidence for high complexity
        if complexity == 'high':
            confidence -= 0.1
        
        # Reduce confidence for unknown
        if complexity == 'unknown':
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def generate_clarification_questions(self, project: ParsedProject) -> List[str]:
        """Generate questions to clarify ambiguities."""
        questions = []
        
        for ambiguity in project.ambiguities:
            if ambiguity == 'budget':
                questions.append("What is your budget range for this project?")
            else:
                questions.append(f"Could you clarify what you mean by '{ambiguity}'?")
        
        # Add domain-specific questions
        if project.domain == 'web' and not any('responsive' in d.description.lower() for d in project.deliverables):
            questions.append("Should the website be responsive/mobile-friendly?")
        
        if project.scope['level'] == 'high' and 'timeline' not in project.timeline:
            questions.append("What is your expected timeline for this project?")
        
        return questions
    
    def generate_summary(self, project: ParsedProject) -> str:
        """Generate human-readable project summary."""
        output = f"""
📋 PARSED PROJECT REQUIREMENTS
{'='*50}

Title: {project.project_title}
Domain: {project.domain.upper()}
Complexity: {project.scope['level'].upper()}
Confidence: {project.confidence:.0%}

⏱️ ESTIMATED SCOPE
"""
        output += f"Estimated Hours: {project.scope['estimated_hours'][0]}-{project.scope['estimated_hours'][1]}\n"
        output += f"Estimated Duration: {project.scope['estimated_weeks'][0]}-{project.scope['estimated_weeks'][1]} weeks\n\n"
        
        if project.scope['reasons']:
            output += "Complexity Factors:\n"
            for reason in project.scope['reasons'][:5]:
                output += f"  • {reason}\n"
        
        output += f"\n🔧 TECH STACK\n"
        if project.tech_stack:
            output += f"  {', '.join(project.tech_stack[:8])}\n"
        else:
            output += "  (No specific technologies mentioned)\n"
        
        output += f"\n📦 DELIVERABLES ({len(project.deliverables)} found)\n"
        for i, req in enumerate(project.deliverables[:10], 1):
            prio_icon = {"must_have": "🔴", "should_have": "🟡", "nice_to_have": "🟢"}.get(req.priority, "⚪")
            output += f"  {prio_icon} {req.requirement_id}: {req.description[:60]}...\n"
        
        if project.ambiguities:
            output += f"\n⚠️ AMBIGUITIES ({len(project.ambiguities)})\n"
            for amb in project.ambiguities[:5]:
                output += f"  • {amb}\n"
        
        questions = self.generate_clarification_questions(project)
        if questions:
            output += f"\n❓ CLARIFICATION QUESTIONS ({len(questions)})\n"
            for i, q in enumerate(questions[:5], 1):
                output += f"  {i}. {q}\n"
        
        return output
    
    def export_to_json(self, project: ParsedProject, filepath: str) -> str:
        """Export parsed project to JSON file."""
        data = {
            "project_title": project.project_title,
            "description": project.description,
            "domain": project.domain,
            "scope": project.scope,
            "timeline": project.timeline,
            "tech_stack": project.tech_stack,
            "deliverables": [
                {
                    "id": d.requirement_id,
                    "type": d.type,
                    "description": d.description,
                    "priority": d.priority,
                    "complexity": d.complexity,
                    "depends_on": d.depends_on,
                    "notes": d.notes
                }
                for d in project.deliverables
            ],
            "constraints": [
                {
                    "id": c.requirement_id,
                    "description": c.description,
                    "priority": c.priority
                }
                for c in project.constraints
            ],
            "ambiguities": project.ambiguities,
            "confidence": project.confidence
        }
        
        Path(filepath).write_text(json.dumps(data, indent=2))
        return filepath
