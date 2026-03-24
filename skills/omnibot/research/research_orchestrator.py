"""
Research Orchestrator Module - Omnibot Phase 2
Coordinates multi-source research with parallel sub-agents.
ACA Methodology: Analyze-Construct-Audit
"""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


@dataclass
class ResearchFinding:
    """Single research finding from a source."""
    claim: str
    source: str
    confidence: float  # 0.0 to 1.0
    category: str  # e.g., "trend", "color", "layout", "typography"
    evidence: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __hash__(self):
        return hash((self.claim, self.source))


@dataclass
class Contradiction:
    """Detected contradiction between findings."""
    finding_a: ResearchFinding
    finding_b: ResearchFinding
    severity: str  # "high", "medium", "low"
    explanation: str


@dataclass
class ResearchResult:
    """Complete research result with synthesis."""
    query: str
    sources_used: List[str]
    findings: List[ResearchFinding]
    contradictions: List[Contradiction]
    synthesized_report: str
    confidence_score: float  # Overall confidence
    execution_time_seconds: float
    agent_logs: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'sources_used': self.sources_used,
            'findings': [asdict(f) for f in self.findings],
            'contradictions': [
                {
                    'finding_a': asdict(c.finding_a),
                    'finding_b': asdict(c.finding_b),
                    'severity': c.severity,
                    'explanation': c.explanation
                }
                for c in self.contradictions
            ],
            'synthesized_report': self.synthesized_report,
            'confidence_score': self.confidence_score,
            'execution_time_seconds': self.execution_time_seconds,
            'agent_logs': self.agent_logs,
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class ResearchOrchestrator:
    """
    Orchestrates multi-source research with parallel sub-agents.
    
    Features:
    - Spawns parallel research agents for multiple sources
    - Synthesizes findings with confidence scoring
    - Detects contradictions between sources
    - Cites all claims with sources
    - Anti-hallucination: every claim must have source
    """
    
    # Available research sources
    SOURCES = {
        'dribbble': 'UI/UX design trends and inspiration',
        'behance': 'Professional design portfolios',
        'material_design': 'Google Material Design guidelines',
        'awwwards': 'Award-winning website designs',
        'css_tricks': 'CSS techniques and trends',
        'smashing_magazine': 'Web design articles',
        'web_designer_depot': 'Design resources',
        'design_week': 'Industry news and trends',
        'color_theory': 'Color psychology and palettes',
        'typography': 'Font trends and recommendations',
    }
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize Research Orchestrator.
        
        Args:
            max_workers: Maximum parallel research agents
        """
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self._agent_logs: List[Dict[str, Any]] = []
    
    def _log_agent_action(self, agent_id: str, source: str, action: str, details: Dict):
        """Log an agent action for audit trail."""
        with self._lock:
            self._agent_logs.append({
                'agent_id': agent_id,
                'source': source,
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'details': details,
            })
    
    def _spawn_research_agent(self, agent_id: str, query: str, source: str) -> List[ResearchFinding]:
        """
        Simulates a research agent that queries a specific source.
        
        In production, this would make actual API calls or web scrape.
        For now, returns simulated findings based on source type.
        """
        import time
        import random
        
        self._log_agent_action(agent_id, source, 'start', {'query': query})
        
        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.3))
        
        findings = []
        
        # Generate findings based on source and query
        source_findings = self._get_source_findings(query, source)
        
        for finding_data in source_findings:
            findings.append(ResearchFinding(
                claim=finding_data['claim'],
                source=source,
                confidence=finding_data.get('confidence', 0.7),
                category=finding_data.get('category', 'general'),
                evidence=finding_data.get('evidence'),
            ))
        
        self._log_agent_action(
            agent_id, source, 'complete',
            {'findings_count': len(findings)}
        )
        
        return findings
    
    def _get_source_findings(self, query: str, source: str) -> List[Dict[str, Any]]:
        """Generate findings for a specific source based on query."""
        query_lower = query.lower()
        
        # Design trends 2026
        if 'web design' in query_lower or 'ui' in query_lower:
            if source == 'dribbble':
                return [
                    {'claim': 'Glassmorphism remains popular in 2026', 'confidence': 0.85, 'category': 'trend', 'evidence': 'Featured in 40% of trending shots'},
                    {'claim': '3D elements with subtle animation are trending', 'confidence': 0.78, 'category': 'trend', 'evidence': '35% increase in 3D UI posts'},
                    {'claim': 'Dark mode is now default for web apps', 'confidence': 0.92, 'category': 'trend', 'evidence': '72% of new designs have dark mode'},
                ]
            elif source == 'behance':
                return [
                    {'claim': 'Bold typography with serifs is returning', 'confidence': 0.88, 'category': 'typography', 'evidence': 'Top 100 portfolios showcase serifs'},
                    {'claim': 'Split-screen layouts are popular', 'confidence': 0.75, 'category': 'layout', 'evidence': 'Featured in editorial web designs'},
                    {'claim': 'Pastel gradients are trending', 'confidence': 0.82, 'category': 'trend', 'evidence': 'Common in fashion brand sites'},
                ]
            elif source == 'material_design':
                return [
                    {'claim': 'Material 3 emphasizes expressive typography', 'confidence': 0.95, 'category': 'typography', 'evidence': 'Official Material 3 guidelines'},
                    {'claim': 'Dynamic color schemes based on wallpaper', 'confidence': 0.90, 'category': 'color', 'evidence': 'Material You specification'},
                ]
            elif source == 'awwwards':
                return [
                    {'claim': 'Scroll-triggered animations increase engagement', 'confidence': 0.87, 'category': 'trend', 'evidence': 'Site of the Day winners analysis'},
                    {'claim': 'Minimalist navigation with hamburger menus', 'confidence': 0.65, 'category': 'layout', 'evidence': 'Declining in desktop, mobile still uses'},
                    {'claim': 'Video backgrounds with overlay text', 'confidence': 0.80, 'category': 'layout', 'evidence': 'Hero section trends'},
                ]
            elif source == 'css_tricks':
                return [
                    {'claim': 'CSS Container Queries are now standard', 'confidence': 0.96, 'category': 'trend', 'evidence': '94% browser support'},
                    {'claim': 'CSS nesting provides cleaner code', 'confidence': 0.93, 'category': 'trend', 'evidence': 'Native nesting support'},
                ]
        
        # Color research
        if 'color' in query_lower:
            if source == 'dribbble':
                return [
                    {'claim': 'Neon gradients combined with dark themes', 'confidence': 0.83, 'category': 'color', 'evidence': 'Gaming and crypto sites'},
                    {'claim': 'Monochromatic schemes with accent colors', 'confidence': 0.79, 'category': 'color', 'evidence': 'SaaS dashboard designs'},
                ]
            elif source == 'color_theory':
                return [
                    {'claim': 'Blue evokes trust and professionalism', 'confidence': 0.94, 'category': 'color', 'evidence': 'Psychology studies'},
                    {'claim': 'Orange creates urgency for CTAs', 'confidence': 0.88, 'category': 'color', 'evidence': 'Conversion optimization research'},
                ]
        
        # Typography research
        if 'typography' in query_lower or 'font' in query_lower:
            if source == 'smashing_magazine':
                return [
                    {'claim': 'Variable fonts improve performance', 'confidence': 0.91, 'category': 'typography', 'evidence': 'Performance metrics comparison'},
                    {'claim': 'Sans-serif remains dominant for body text', 'confidence': 0.89, 'category': 'typography', 'evidence': 'Readability studies'},
                ]
        
        # Generic findings for unknown queries
        return [
            {'claim': f'Research on "{query}" requires specific domain knowledge', 'confidence': 0.5, 'category': 'general'},
            {'claim': f'Consider consulting {source} directly for detailed insights', 'confidence': 0.7, 'category': 'general'},
        ]
    
    def spawn_research_agents(self, query: str, sources: Optional[List[str]] = None) -> List[ResearchFinding]:
        """
        Spawn parallel research agents for multiple sources.
        
        Args:
            query: Research query (e.g., "2026 web design trends")
            sources: List of source names (default: all sources)
            
        Returns:
            Combined list of findings from all sources
        """
        sources = sources or list(self.SOURCES.keys())
        
        all_findings: List[ResearchFinding] = []
        completed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all research tasks
            future_to_source = {
                executor.submit(
                    self._spawn_research_agent,
                    f"agent_{i}",
                    query,
                    source
                ): source
                for i, source in enumerate(sources)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    findings = future.result()
                    all_findings.extend(findings)
                    completed_count += 1
                except Exception as e:
                    self._log_agent_action(
                        f"agent_{sources.index(source)}",
                        source,
                        'error',
                        {'error': str(e)}
                    )
        
        return all_findings
    
    def detect_contradictions(self, findings: List[ResearchFinding]) -> List[Contradiction]:
        """
        Detect contradictions between research findings.
        
        Args:
            findings: List of research findings
            
        Returns:
            List of Contradiction objects
        """
        contradictions = []
        
        # Known contradiction patterns
        contradiction_patterns = [
            (r'dark mode', r'light mode'),
            (r'minimal', r'complex'),
            (r'static', r'animated'),
            (r'serif', r'sans-serif'),
            (r'bright colors', r'muted tones'),
            (r'large typography', r'small typography'),
        ]
        
        for i, finding_a in enumerate(findings):
            for finding_b in findings[i+1:]:
                if finding_a.source == finding_b.source:
                    continue  # Skip same-source contradictions
                
                # Check for direct negation
                claim_a_lower = finding_a.claim.lower()
                claim_b_lower = finding_b.claim.lower()
                
                for pattern_a, pattern_b in contradiction_patterns:
                    if (pattern_a in claim_a_lower and pattern_b in claim_b_lower) or \
                       (pattern_b in claim_a_lower and pattern_a in claim_b_lower):
                        
                        severity = 'medium'
                        if finding_a.confidence > 0.8 and finding_b.confidence > 0.8:
                            severity = 'high'
                        elif finding_a.confidence < 0.6 or finding_b.confidence < 0.6:
                            severity = 'low'
                        
                        contradictions.append(Contradiction(
                            finding_a=finding_a,
                            finding_b=finding_b,
                            severity=severity,
                            explanation=f"Conflicting trends: '{finding_a.source}' vs '{finding_b.source}'"
                        ))
                        break
                
                # Check for numeric contradictions
                nums_a = re.findall(r'(\d+)%', finding_a.claim)
                nums_b = re.findall(r'(\d+)%', finding_b.claim)
                if nums_a and nums_b:
                    diff = abs(int(nums_a[0]) - int(nums_b[0]))
                    if diff > 20:  # 20%+ difference
                        contradictions.append(Contradiction(
                            finding_a=finding_a,
                            finding_b=finding_b,
                            severity='high' if diff > 40 else 'medium',
                            explanation=f"Statistical discrepancy: {nums_a[0]}% vs {nums_b[0]}%"
                        ))
        
        return contradictions
    
    def synthesize_findings(self, query: str, findings: List[ResearchFinding],
                          contradictions: List[Contradiction]) -> str:
        """
        Synthesize findings into unified report with citations.
        
        Args:
            query: Original research query
            findings: List of research findings
            contradictions: List of contradictions detected
            
        Returns:
            Synthesized report as markdown string
        """
        # Group findings by category
        by_category: Dict[str, List[ResearchFinding]] = {}
        for finding in findings:
            by_category.setdefault(finding.category, []).append(finding)
        
        # Sort by confidence
        for category in by_category:
            by_category[category].sort(key=lambda x: x.confidence, reverse=True)
        
        # Build report
        report_parts = [
            f"# Research Report: {query}",
            f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            f"\n*Sources analyzed: {len(set(f.source for f in findings))}*",
            f"\n*Total findings: {len(findings)}*",
        ]
        
        # Summary section
        report_parts.append("\n## Summary\n")
        
        # Find most confident finding per category
        top_findings = []
        for category, category_findings in by_category.items():
            if category_findings:
                top = category_findings[0]
                top_findings.append(f"- **{category.title()}:** {top.claim} (confidence: {top.confidence:.0%})")
        
        if top_findings:
            report_parts.append("Key findings by category:")
            report_parts.extend(top_findings)
        
        # Detailed findings by category
        report_parts.append("\n## Detailed Findings\n")
        
        for category, category_findings in sorted(by_category.items()):
            if not category_findings:
                continue
            
            report_parts.append(f"\n### {category.title().replace('_', ' ')}")
            
            for finding in category_findings:
                confidence_indicator = "🔴" if finding.confidence < 0.7 else "🟡" if finding.confidence < 0.85 else "🟢"
                report_parts.append(
                    f"\n- {confidence_indicator} **{finding.claim}**"
                )
                report_parts.append(f"  - Source: `{finding.source}`")
                report_parts.append(f"  - Confidence: {finding.confidence:.0%}")
                if finding.evidence:
                    report_parts.append(f"  - Evidence: {finding.evidence}")
        
        # Contradictions section
        if contradictions:
            report_parts.append("\n## ⚠️ Contradictions Detected\n")
            report_parts.append(f"Found {len(contradictions)} potential contradictions:\n")
            
            for c in contradictions:
                emoji = "🔴" if c.severity == 'high' else "🟡" if c.severity == 'medium' else "🟠"
                report_parts.append(
                    f"\n{emoji} **[{c.severity.upper()}]** {c.explanation}"
                )
                report_parts.append(f"  - **{c.finding_a.source}:** {c.finding_a.claim}")
                report_parts.append(f"  - **{c.finding_b.source}:** {c.finding_b.claim}")
        
        # Sources section
        report_parts.append("\n## Sources Cited\n")
        unique_sources = sorted(set(f.source for f in findings))
        for source in unique_sources:
            description = self.SOURCES.get(source, 'Research source')
            report_parts.append(f"- `{source}`: {description}")
        
        return '\n'.join(report_parts)
    
    def research(self, query: str, sources: Optional[List[str]] = None) -> ResearchResult:
        """
        Execute full research pipeline.
        
        Args:
            query: Research query
            sources: Specific sources to query (default: all)
            
        Returns:
            Complete ResearchResult with synthesis and citations
        """
        import time
        start_time = time.time()
        
        # Reset logs for this research session
        self._agent_logs = []
        
        # Phase 1: Parallel research
        findings = self.spawn_research_agents(query, sources)
        
        # Phase 2: Detect contradictions
        contradictions = self.detect_contradictions(findings)
        
        # Phase 3: Synthesize
        report = self.synthesize_findings(query, findings, contradictions)
        
        # Calculate overall confidence
        if findings:
            avg_confidence = sum(f.confidence for f in findings) / len(findings)
            # Reduce confidence if contradictions exist
            confidence_penalty = len(contradictions) * 0.05
            confidence_score = max(0.0, avg_confidence - confidence_penalty)
        else:
            confidence_score = 0.0
        
        execution_time = time.time() - start_time
        
        return ResearchResult(
            query=query,
            sources_used=sources or list(self.SOURCES.keys()),
            findings=findings,
            contradictions=contradictions,
            synthesized_report=report,
            confidence_score=confidence_score,
            execution_time_seconds=execution_time,
            agent_logs=self._agent_logs,
        )
    
    def cite_sources(self, finding: ResearchFinding) -> str:
        """
        Generate citation for a finding.
        
        Args:
            finding: Research finding
            
        Returns:
            Citation string
        """
        return f"[{finding.source}, {finding.timestamp}] {finding.claim}"


# === AUDIT CHECK: Validate module structure ===
if __name__ == "__main__":
    import time
    
    # Test basic functionality
    orchestrator = ResearchOrchestrator()
    
    print("Testing Research Orchestrator...")
    print(f"✓ Available sources: {len(orchestrator.SOURCES)}")
    
    # Test research execution
    result = orchestrator.research(
        "2026 web design trends",
        sources=['dribbble', 'behance', 'material_design']
    )
    
    assert result.confidence_score > 0, "Confidence score should be > 0"
    assert len(result.findings) > 0, "Should have findings"
    assert len(result.sources_used) == 3, "Should use 3 sources"
    print(f"✓ Research completed: {len(result.findings)} findings from {len(result.sources_used)} sources")
    print(f"✓ Confidence score: {result.confidence_score:.2%}")
    print(f"✓ Execution time: {result.execution_time_seconds:.2f}s")
    
    if result.contradictions:
        print(f"✓ Contradictions detected: {len(result.contradictions)}")
    
    print("\n✅ All audits passed - Research Orchestrator ready!")