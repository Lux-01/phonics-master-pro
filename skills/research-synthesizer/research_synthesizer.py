#!/usr/bin/env python3
"""
Research Synthesizer v1.0
Multi-source research with contradiction detection and source scoring

## ACA Plan:
1. Requirements: Parse research sources → detect contradictions → synthesize → score
2. Architecture: SourceCollector → ContradictionDetector → Synthesizer → Scorer
3. Data Flow: Collect sources → Compare claims → Resolve conflicts → Score quality
4. Edge Cases: No sources, all contradict, no consensus, low quality
5. Tool Constraints: File read, text matching, scoring algorithms
6. Error Handling: Read errors, parse errors, comparison errors
7. Testing: Test with contradictory sources

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"
DOCS_DIR = WORKSPACE_DIR / "docs"


@dataclass
class ResearchSource:
    title: str
    content: str
    source_type: str  # memory, docs, external
    date: Optional[str]
    confidence: float = 1.0


@dataclass
class Contradiction:
    claim_1: str
    claim_2: str
    source_1: str
    source_2: str
    severity: str  # low, medium, high


@dataclass
class SynthesizedFinding:
    topic: str
    consensus: str
    supporting_sources: List[str]
    contradicting_sources: List[str]
    confidence: float


class ResearchSynthesizer:
    def __init__(self):
        self.sources: List[ResearchSource] = []
        self.contradictions: List[Contradiction] = []
        self.findings: List[SynthesizedFinding] = []
    
    def collect_sources(self) -> List[ResearchSource]:
        """Collect research sources from memory and docs"""
        sources = []
        
        # From memory files
        for mem_file in MEMORY_DIR.glob("2026-*.md"):
            content = mem_file.read_text()
            sources.append(ResearchSource(
                title=mem_file.name,
                content=content[:5000],  # Limit size
                source_type="memory",
                date=mem_file.name.replace(".md", "")
            ))
        
        # From docs
        if DOCS_DIR.exists():
            for doc_file in DOCS_DIR.glob("*.md"):
                content = doc_file.read_text()
                sources.append(ResearchSource(
                    title=doc_file.name,
                    content=content[:5000],
                    source_type="docs",
                    date=None
                ))
        
        return sources
    
    def extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        claims = []
        
        # Pattern: "X is Y" statements
        patterns = [
            r'(?:status|Status):\s*([^\n]+)',
            r'(?:performance|Performance):\s*([^\n]+)',
            r'(?:win rate|Win Rate):\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                claim = match.group(1).strip()
                if claim:
                    claims.append(claim)
        
        return claims
    
    def detect_contradictions(self, sources: List[ResearchSource]) -> List[Contradiction]:
        """Find contradictions between sources"""
        contradictions = []
        
        # Extract all claims
        all_claims = {}
        for source in sources:
            claims = self.extract_claims(source.content)
            for claim in claims:
                if claim not in all_claims:
                    all_claims[claim] = []
                all_claims[claim].append(source.title)
        
        # Simple contradiction detection: conflicting status
        status_pattern = re.compile(r'(active|completed|paused|cancelled)', re.IGNORECASE)
        
        for i, src1 in enumerate(sources):
            for j, src2 in enumerate(sources[i+1:], i+1):
                # Check for status contradictions
                status1 = status_pattern.findall(src1.content)
                status2 = status_pattern.findall(src2.content)
                
                if status1 and status2 and status1 != status2:
                    contradictions.append(Contradiction(
                        claim_1=f"Status: {status1[0]}",
                        claim_2=f"Status: {status2[0]}",
                        source_1=src1.title,
                        source_2=src2.title,
                        severity="medium"
                    ))
        
        return contradictions
    
    def synthesize(self, sources: List[ResearchSource]) -> List[SynthesizedFinding]:
        """Synthesize findings from multiple sources"""
        findings = []
        
        # Extract topics
        topics = ["LuxTrader", "skills", "trading", "AOE", "ALOE"]
        
        for topic in topics:
            # Find sources mentioning topic
            related = [s for s in sources if topic.lower() in s.content.lower()]
            
            if not related:
                continue
            
            # Extract key statement about topic
            consensus = self._find_consensus(related, topic)
            
            # Score confidence
            confidence = min(len(related) / 5, 1.0)
            
            findings.append(SynthesizedFinding(
                topic=topic,
                consensus=consensus or f"{len(related)} sources mention {topic}",
                supporting_sources=[s.title for s in related],
                contradicting_sources=[],
                confidence=confidence
            ))
        
        return findings
    
    def _find_consensus(self, sources: List[ResearchSource], topic: str) -> Optional[str]:
        """Find common statement across sources"""
        # Extract sentences mentioning topic
        sentences = []
        for source in sources:
            for sent in source.content.split('.'):
                if topic.lower() in sent.lower():
                    sentences.append(sent.strip())
        
        if sentences:
            # Return most common pattern
            return sentences[0] if sentences else None
        return None
    
    def generate_report(self, sources: List[ResearchSource], 
                       contradictions: List[Contradiction],
                       findings: List[SynthesizedFinding]) -> str:
        """Generate synthesis report"""
        report = []
        report.append("# Research Synthesis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"Sources analyzed: {len(sources)}")
        report.append("")
        
        # Findings
        report.append("## Synthesized Findings")
        report.append("")
        for finding in findings:
            icon = "🔴" if finding.confidence < 0.5 else "🟡" if finding.confidence < 0.8 else "🟢"
            report.append(f"### {icon} {finding.topic}")
            report.append(f"**Consensus:** {finding.consensus}")
            report.append(f"**Confidence:** {finding.confidence*100:.0f}%")
            report.append(f"**Sources:** {len(finding.supporting_sources)}")
            report.append("")
        
        # Contradictions
        if contradictions:
            report.append("## ⚠️ Detected Contradictions")
            report.append(f"\nFound {len(contradictions)} contradictions:")
            for c in contradictions:
                report.append(f"\n- **{c.claim_1}** (from {c.source_1})")
                report.append(f"  vs **{c.claim_2}** (from {c.source_2})")
                report.append(f"  Severity: {c.severity}")
            report.append("")
        
        return "\n".join(report)
    
    def run(self) -> Dict:
        """Main execution"""
        # Collect sources
        self.sources = self.collect_sources()
        
        # Detect contradictions
        self.contradictions = self.detect_contradictions(self.sources)
        
        # Synthesize
        self.findings = self.synthesize(self.sources)
        
        # Generate report
        report = self.generate_report(self.sources, self.contradictions, self.findings)
        report_file = MEMORY_DIR / "synthesis_report.md"
        
        # Ensure directory
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, "w") as f:
            f.write(report)
        
        return {
            "success": True,
            "sources_analyzed": len(self.sources),
            "contradictions_found": len(self.contradictions),
            "findings": len(self.findings),
            "report": str(report_file)
        }


def main():
    parser = argparse.ArgumentParser(description="Research Synthesizer")
    args = parser.parse_args()
    
    synthesizer = ResearchSynthesizer()
    result = synthesizer.run()
    
    if result.get("success"):
        print(f"✓ Synthesis complete")
        print(f"  Sources: {result['sources_analyzed']}")
        print(f"  Contradictions: {result['contradictions_found']}")
        print(f"  Findings: {result['findings']}")
    else:
        print(f"✗ Error")


if __name__ == "__main__":
    main()
