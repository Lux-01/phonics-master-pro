#!/usr/bin/env python3
"""
Skill Evolution Engine (SEE) - Tier 4 Meta-System
Self-improving skill analyzer that evolves the entire OpenClaw ecosystem.

## ACA Workflow Implementation
- Step 1: Requirements Analysis ✓
- Step 2: Architecture Design ✓
- Step 3: Data Flow Planning ✓
- Step 4: Edge Case Planning ✓
- Step 5: Tool Constraints ✓
- Step 6: Error Handling ✓
- Step 7: Testing Strategy ✓

Author: Autonomous Code Architect (ACA)
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple, TypeVar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/skux/.openclaw/workspace/memory/see/see.log')
    ]
)
logger = logging.getLogger('SEE')

# ============================================================================
# CONFIGURATION
# ============================================================================

class SEEConfig:
    """Configuration constants for SEE."""
    # Paths
    SKILLS_DIR = Path('/home/skux/.openclaw/workspace/skills')
    MEMORY_DIR = Path('/home/skux/.openclaw/workspace/memory/see')
    MEMORY_ACA_DIR = Path('/home/skux/.openclaw/workspace/memory/aca')
    ALOE_MEMORY_DIR = Path('/home/skux/.openclaw/workspace/memory/aloe')
    
    # State files
    SKILL_HEALTH_FILE = MEMORY_DIR / 'skill_health' / 'all_skills.json'
    PERFORMANCE_METRICS_FILE = MEMORY_DIR / 'skill_health' / 'performance_metrics.json'
    IMPROVEMENT_BACKLOG_FILE = MEMORY_DIR / 'skill_health' / 'improvement_backlog.json'
    PROPOSALS_FILE = MEMORY_DIR / 'proposals' / 'proposals.json'
    BUSINESS_MODEL_FILE = MEMORY_DIR / 'business_model' / 'income_streams.json'
    PATTERNS_FILE = MEMORY_DIR / 'patterns' / 'success_patterns.json'
    AUDIT_HISTORY_FILE = MEMORY_DIR / 'audit_history.json'
    
    # Settings
    MAX_AUDIT_AGE_DAYS = 30
    MIN_HEALTH_SCORE = 60
    ARCHIVE_THRESHOLD_DAYS = 90
    
    # Health scoring weights
    WEIGHT_INSTRUCTIONS = 0.25
    WEIGHT_TOOLS = 0.20
    WEIGHT_INTEGRATION = 0.20
    WEIGHT_PERFORMANCE = 0.20
    WEIGHT_DOCUMENTATION = 0.15

# Ensure directories exist
for subdir in ['skill_health', 'proposals', 'refactors', 'business_model', 
               'patterns', 'audit_history']:
    (SEEConfig.MEMORY_DIR / subdir).mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA MODELS
# ============================================================================

class FindingType(Enum):
    """Types of findings during skill analysis."""
    OUTDATED = auto()
    INEFFICIENT = auto()
    MISSING = auto()
    CONTRADICTING = auto()
    REDUNDANT = auto()
    SECURITY = auto()
    PERFORMANCE = auto()
    DOCUMENTATION = auto()
    INTEGRATION = auto()

class Priority(Enum):
    """Priority levels for improvements."""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

@dataclass
class Finding:
    """Represents a finding from skill analysis."""
    type: FindingType
    description: str
    severity: Priority
    location: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type.name,
            'description': self.description,
            'severity': self.severity.value,
            'location': self.location,
            'suggestion': self.suggestion,
            'confidence': self.confidence
        }

@dataclass
class SkillMetrics:
    """Performance metrics for a skill."""
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    error_rate: float = 0.0
    usage_count: int = 0
    last_execution: Optional[str] = None
    tool_calls: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SkillHealth:
    """Health report for a skill."""
    skill_id: str
    name: str
    health_score: int
    last_audit: str
    findings: List[Finding] = field(default_factory=list)
    metrics: SkillMetrics = field(default_factory=SkillMetrics)
    version: str = '1.0.0'
    status: str = 'active'  # active, deprecated, archived
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'health_score': self.health_score,
            'last_audit': self.last_audit,
            'findings': [f.to_dict() for f in self.findings],
            'metrics': self.metrics.to_dict(),
            'version': self.version,
            'status': self.status,
            'recommendations': self.recommendations
        }

@dataclass
class ImprovementProposal:
    """Proposal for skill improvement."""
    id: str
    target_skill: str
    priority: Priority
    type: str
    current_state: Dict[str, Any] = field(default_factory=dict)
    proposed_change: Dict[str, Any] = field(default_factory=dict)
    implementation: Dict[str, Any] = field(default_factory=dict)
    business_impact: Dict[str, Any] = field(default_factory=dict)
    status: str = 'pending'  # pending, approved, rejected, implemented
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'target_skill': self.target_skill,
            'priority': self.priority.value,
            'type': self.type,
            'current_state': self.current_state,
            'proposed_change': self.proposed_change,
            'implementation': self.implementation,
            'business_impact': self.business_impact,
            'status': self.status,
            'created_at': self.created_at
        }

@dataclass
class SkillAudit:
    """Complete audit report for a skill."""
    skill_id: str
    audit_date: str
    skill_name: str
    health_score: int
    findings: List[Finding]
    recommendations: List[str]
    evolution_suggestion: Optional[str] = None
    
    def to_markdown(self) -> str:
        """Generate markdown audit report."""
        lines = [
            f"# Skill Audit: {self.skill_name}",
            f"",
            f"**Skill ID:** `{self.skill_id}`  ",
            f"**Audit Date:** {self.audit_date}  ",
            f"**Health Score:** {self.health_score}/100",
            f"",
            "## Executive Summary",
            f"",
            f"This skill has a health score of **{self.health_score}/100**, indicating " +
            f"{'excellent' if self.health_score >= 85 else 'good' if self.health_score >= 70 else 'fair' if self.health_score >= 60 else 'poor'} health.",
            f"",
            f"### Key Findings: {len(self.findings)}",
            f"",
        ]
        
        # Group findings by severity
        critical = [f for f in self.findings if f.severity == Priority.CRITICAL]
        high = [f for f in self.findings if f.severity == Priority.HIGH]
        medium = [f for f in self.findings if f.severity == Priority.MEDIUM]
        low = [f for f in self.findings if f.severity == Priority.LOW]
        
        if critical:
            lines.extend([f"- 🔴 **Critical:** {len(critical)} issue(s)", ""])
        if high:
            lines.extend([f"- 🟠 **High:** {len(high)} issue(s)", ""])
        if medium:
            lines.extend([f"- 🟡 **Medium:** {len(medium)} issue(s)", ""])
        if low:
            lines.extend([f"- 🟢 **Low:** {len(low)} issue(s)", ""])
        
        lines.extend([
            "## Detailed Findings",
            "",
        ])
        
        for i, finding in enumerate(self.findings, 1):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(finding.severity.value, '⚪')
            lines.extend([
                f"### {i}. {emoji} {finding.type.name}",
                f"",
                f"**Severity:** {finding.severity.value.upper()}",
                f"",
                f"**Description:** {finding.description}",
                f"",
            ])
            if finding.location:
                lines.extend([f"**Location:** `{finding.location}`", ""])
            if finding.suggestion:
                lines.extend([f"**Suggestion:** {finding.suggestion}", ""])
            lines.append(f"**Confidence:** {finding.confidence * 100:.0f}%")
            lines.append("")
        
        lines.extend([
            "## Recommendations",
            "",
        ])
        for rec in self.recommendations:
            lines.extend([f"- {rec}", ""])
        
        if self.evolution_suggestion:
            lines.extend([
                "## Evolution Suggestion",
                "",
                f"{self.evolution_suggestion}",
                "",
            ])
        
        lines.extend([
            "---",
            "*Generated by Skill Evolution Engine (SEE)*",
            f"*Audit ID: AUDIT-{self.skill_id}-{self.audit_date.replace(':', '-')}*"
        ])
        
        return "\n".join(lines)

# ============================================================================
# FILE UTILITIES
# ============================================================================

class FileUtils:
    """Utility functions for file operations with error handling."""
    
    @staticmethod
    def safe_read(path: Path) -> Optional[str]:
        """Safely read a file, return None if not found or corrupted."""
        try:
            if not path.exists():
                return None
            return path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to read {path}: {e}")
            return None
    
    @staticmethod
    def safe_write(path: Path, content: str) -> bool:
        """Safely write to a file with backup."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if path.exists():
                backup_path = path.with_suffix('.json.bak')
                shutil.copy2(path, backup_path)
            
            path.write_text(content, encoding='utf-8')
            return True
        except IOError as e:
            logger.error(f"Failed to write {path}: {e}")
            return False
    
    @staticmethod
    def safe_json_read(path: Path) -> Optional[Dict]:
        """Safely read JSON file."""
        content = FileUtils.safe_read(path)
        if content is None:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error in {path}: {e}")
            # Try backup
            backup_path = path.with_suffix('.json.bak')
            if backup_path.exists():
                try:
                    return json.loads(backup_path.read_text())
                except json.JSONDecodeError:
                    pass
            return None
    
    @staticmethod
    def safe_json_write(path: Path, data: Dict) -> bool:
        """Safely write JSON file with formatting."""
        try:
            content = json.dumps(data, indent=2, default=str)
            return FileUtils.safe_write(path, content)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON serialization error: {e}")
            return False

# ============================================================================
# SKILL PARSER
# ============================================================================

class SkillParser:
    """Parser for SKILL.md files."""
    
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.validation_patterns = {
            'name': re.compile(r'^name:\s*(.+)$', re.MULTILINE),
            'description': re.compile(r'^description:\s*(.+)$', re.MULTILINE),
            'commands': re.compile(r'^(?:#+)\s*Commands', re.MULTILINE),
            'storage': re.compile(r'^(?:#+)\s*Storage', re.MULTILINE),
        }
    
    def discover_skills(self) -> List[Path]:
        """Discover all skill directories with SKILL.md files."""
        skills = []
        try:
            for item in self.skills_dir.iterdir():
                if item.is_dir():
                    skill_file = item / 'SKILL.md'
                    if skill_file.exists():
                        skills.append(item)
        except PermissionError as e:
            logger.error(f"Permission denied accessing skills directory: {e}")
        return sorted(skills)
    
    def parse_skill_md(self, skill_path: Path) -> Dict[str, Any]:
        """Parse a SKILL.md file and extract structured data."""
        skill_file = skill_path / 'SKILL.md'
        content = FileUtils.safe_read(skill_file)
        
        if content is None:
            return {'error': 'Could not read SKILL.md', 'valid': False}
        
        result = {
            'skill_id': skill_path.name,
            'path': str(skill_file),
            'valid': True,
            'name': None,
            'description': None,
            'has_commands': False,
            'has_storage': False,
            'sections': [],
            'tool_references': [],
            'integration_points': [],
            'raw_content': content,
        }
        
        # Extract metadata
        name_match = self.validation_patterns['name'].search(content)
        if name_match:
            result['name'] = name_match.group(1).strip()
        
        desc_match = self.validation_patterns['description'].search(content)
        if desc_match:
            result['description'] = desc_match.group(1).strip()
        
        # Check for required sections
        result['has_commands'] = bool(self.validation_patterns['commands'].search(content))
        result['has_storage'] = bool(self.validation_patterns['storage'].search(content))
        
        # Extract sections
        section_pattern = re.compile(r'^(#+)\s+(.+)$', re.MULTILINE)
        for match in section_pattern.finditer(content):
            result['sections'].append(match.group(2).strip())
        
        # Detect tool references
        tool_patterns = [
            r'`(\w+)`\s*tool',
            r'(browser|exec|read|write|edit|web_fetch)',
            r'\b(Brave Search|Birdeye|Jupiter|Telegram|Discord)\b',
        ]
        for pattern in tool_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                tool = match.group(1).lower() if match.groups() else match.group(0).lower()
                if tool not in result['tool_references']:
                    result['tool_references'].append(tool)
        
        # Detect integration points (references to other skills)
        integration_pattern = re.compile(r'\b(\w+-\w+-\w+|\w+-\w+)\b.*skill', re.IGNORECASE)
        for match in integration_pattern.finditer(content):
            skill_ref = match.group(1)
            if skill_ref not in result['integration_points'] and skill_ref != result['skill_id']:
                result['integration_points'].append(skill_ref)
        
        # Validate structure
        if not result['name']:
            result['valid'] = False
            result['error'] = 'Missing name in frontmatter'
        
        return result

# ============================================================================
# SKILL ANALYZER
# ============================================================================

class SkillAnalyzer:
    """Analyzes skills for health, gaps, and improvements."""
    
    def __init__(self, parser: SkillParser):
        self.parser = parser
        self.deprecated_patterns = {
            'jupiter v4': 'Jupiter API v4 is deprecated, use v6',
            'solscan': 'Solscan API has rate limits, consider alternatives',
            'old syntax': 'Using deprecated syntax patterns',
        }
    
    def calculate_health_score(self, skill_data: Dict[str, Any]) -> Tuple[int, List[Finding]]:
        """Calculate health score and identify findings."""
        score = 100
        findings = []
        
        # Check name
        if not skill_data.get('name'):
            score -= 15
            findings.append(Finding(
                type=FindingType.MISSING,
                description="Skill missing name in frontmatter",
                severity=Priority.HIGH,
                location="SKILL.md header",
                suggestion="Add proper 'name:' field in frontmatter",
                confidence=1.0
            ))
        
        # Check description
        if not skill_data.get('description'):
            score -= 10
            findings.append(Finding(
                type=FindingType.DOCUMENTATION,
                description="Skill missing description",
                severity=Priority.MEDIUM,
                suggestion="Add 'description:' to frontmatter explaining what this skill does",
                confidence=1.0
            ))
        
        # Check commands section
        if not skill_data.get('has_commands'):
            score -= 10
            findings.append(Finding(
                type=FindingType.DOCUMENTATION,
                description="Missing Commands section",
                severity=Priority.MEDIUM,
                location="SKILL.md",
                suggestion="Add Commands section with usage examples",
                confidence=1.0
            ))
        
        # Check storage section
        if not skill_data.get('has_storage'):
            score -= 5
            findings.append(Finding(
                type=FindingType.DOCUMENTATION,
                description="Missing Storage section",
                severity=Priority.LOW,
                suggestion="Add Storage section documenting file paths",
                confidence=1.0
            ))
        
        # Check for deprecated patterns
        content = skill_data.get('raw_content', '')
        for pattern, message in self.deprecated_patterns.items():
            if pattern.lower() in content.lower():
                score -= 10
                findings.append(Finding(
                    type=FindingType.OUTDATED,
                    description=message,
                    severity=Priority.HIGH,
                    location="SKILL.md content",
                    suggestion=f"Update to newer {pattern.split()[-1]} version",
                    confidence=0.9
                ))
        
        # Check tool references
        tools = skill_data.get('tool_references', [])
        if len(tools) == 0:
            score -= 5
            findings.append(Finding(
                type=FindingType.MISSING,
                description="No tool references detected",
                severity=Priority.LOW,
                suggestion="Document which tools this skill uses",
                confidence=0.7
            ))
        
        # Check for error handling mentions
        if 'error' not in content.lower() and 'exception' not in content.lower():
            score -= 5
            findings.append(Finding(
                type=FindingType.MISSING,
                description="No error handling documentation found",
                severity=Priority.MEDIUM,
                suggestion="Add Error Handling section with common failure modes",
                confidence=0.8
            ))
        
        # Check integration points
        integrations = skill_data.get('integration_points', [])
        if len(integrations) > 5:
            score -= 5
            findings.append(Finding(
                type=FindingType.INEFFICIENT,
                description=f"High integration complexity ({len(integrations)} dependencies)",
                severity=Priority.LOW,
                suggestion="Consider simplifying integrations or documenting dependency graph",
                confidence=0.6
            ))
        
        return max(0, score), findings
    
    def detect_gaps(self, skill_data: Dict[str, Any]) -> List[str]:
        """Detect gaps and improvement opportunities."""
        gaps = []
        content = skill_data.get('raw_content', '')
        
        # Check for common gaps
        if 'testing' not in content.lower() and 'test' not in content.lower():
            gaps.append("Missing testing strategy documentation")
        
        if 'cli' not in content.lower() and 'command line' not in content.lower():
            gaps.append("No CLI documentation")
        
        if 'config' not in content.lower():
            gaps.append("No configuration documentation")
        
        if 'example' not in content.lower():
            gaps.append("No usage examples provided")
        
        if 'TODO' in content or 'FIXME' in content:
            gaps.append("Contains TODO/FIXME items")
        
        return gaps
    
    def generate_recommendations(self, findings: List[Finding], gaps: List[str]) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Prioritize by severity
        critical = [f for f in findings if f.severity == Priority.CRITICAL]
        high = [f for f in findings if f.severity == Priority.HIGH]
        
        for finding in critical:
            if finding.suggestion:
                recommendations.append(f"[CRITICAL] {finding.suggestion}")
        
        for finding in high:
            if finding.suggestion:
                recommendations.append(f"[HIGH] {finding.suggestion}")
        
        for gap in gaps:
            recommendations.append(f"[MEDIUM] {gap}")
        
        return recommendations

# ============================================================================
# SKILL AUDIT GENERATOR
# ============================================================================

class AuditGenerator:
    """Generates comprehensive skill audit reports."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_audit(self, skill_id: str, skill_data: Dict[str, Any], 
                       health_score: int, findings: List[Finding],
                       recommendations: List[str]) -> SkillAudit:
        """Generate a complete skill audit."""
        
        evolution_suggestion = self._generate_evolution_suggestion(
            skill_id, skill_data, health_score, findings
        )
        
        audit = SkillAudit(
            skill_id=skill_id,
            audit_date=datetime.now().isoformat(),
            skill_name=skill_data.get('name', skill_id),
            health_score=health_score,
            findings=findings,
            recommendations=recommendations,
            evolution_suggestion=evolution_suggestion
        )
        
        return audit
    
    def _generate_evolution_suggestion(self, skill_id: str, skill_data: Dict[str, Any],
                                        health_score: int, findings: List[Finding]) -> Optional[str]:
        """Generate evolution suggestion based on analysis."""
        
        if health_score >= 90:
            return (f"This skill is in excellent health. Consider evolving it to be a "
                   f"template for other similar skills. Document its success patterns.")
        
        if health_score >= 70:
            return (f"This skill is healthy with minor issues. Focus on addressing "
                   f"the {len([f for f in findings if f.severity in (Priority.HIGH, Priority.CRITICAL)])} "
                   f"high/critical findings to reach excellent health.")
        
        if health_score >= 60:
            return (f"This skill needs attention. Consider a focused refactor session "
                   f"to address documentation gaps and update any deprecated patterns.")
        
        return (f"This skill requires significant evolution. Consider a complete "
               f"rewrite using the ACA 7-step workflow. Address critical issues first.")
    
    def save_audit(self, audit: SkillAudit) -> Path:
        """Save audit to file and update history."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{audit.skill_id}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # Save markdown report
        FileUtils.safe_write(filepath, audit.to_markdown())
        
        # Update history
        history_path = SEEConfig.MEMORY_DIR / 'audit_history.json'
        history = FileUtils.safe_json_read(history_path) or {}
        
        if audit.skill_id not in history:
            history[audit.skill_id] = []
        
        history[audit.skill_id].append({
            'date': audit.audit_date,
            'score': audit.health_score,
            'findings': len(audit.findings),
            'file': str(filepath)
        })
        
        FileUtils.safe_json_write(history_path, history)
        
        return filepath

# ============================================================================
# SKILL REGISTRY
# ============================================================================

class SkillRegistry:
    """Manages skill registry and health tracking."""
    
    def __init__(self, health_file: Path, metrics_file: Path, backlog_file: Path):
        self.health_file = health_file
        self.metrics_file = metrics_file
        self.backlog_file = backlog_file
        self.health_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.backlog_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_health_data(self) -> Dict[str, SkillHealth]:
        """Load skill health data from file."""
        data = FileUtils.safe_json_read(self.health_file) or {}
        
        result = {}
        for skill_id, skill_dict in data.items():
            try:
                findings = [Finding(
                    type=FindingType[f['type']],
                    description=f['description'],
                    severity=Priority(f['severity']),
                    location=f.get('location'),
                    suggestion=f.get('suggestion'),
                    confidence=f.get('confidence', 0.5)
                ) for f in skill_dict.get('findings', [])]
                
                metrics_dict = skill_dict.get('metrics', {})
                metrics = SkillMetrics(**metrics_dict)
                
                result[skill_id] = SkillHealth(
                    skill_id=skill_id,
                    name=skill_dict.get('name', skill_id),
                    health_score=skill_dict.get('health_score', 0),
                    last_audit=skill_dict.get('last_audit', ''),
                    findings=findings,
                    metrics=metrics,
                    version=skill_dict.get('version', '1.0.0'),
                    status=skill_dict.get('status', 'active')
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse skill data for {skill_id}: {e}")
        
        return result
    
    def save_health_data(self, health_data: Dict[str, SkillHealth]) -> bool:
        """Save skill health data to file."""
        data = {skill_id: health.to_dict() for skill_id, health in health_data.items()}
        return FileUtils.safe_json_write(self.health_file, data)
    
    def update_skill_health(self, skill_id: str, health: SkillHealth) -> bool:
        """Update health data for a specific skill."""
        health_data = self.load_health_data()
        health_data[skill_id] = health
        return self.save_health_data(health_data)
    
    def get_skill_health(self, skill_id: str) -> Optional[SkillHealth]:
        """Get health data for a specific skill."""
        health_data = self.load_health_data()
        return health_data.get(skill_id)
    
    def get_outdated_skills(self, max_age_days: int = 30) -> List[str]:
        """Get list of skills with outdated audits."""
        health_data = self.load_health_data()
        outdated = []
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        for skill_id, health in health_data.items():
            try:
                last_audit = datetime.fromisoformat(health.last_audit)
                if last_audit < cutoff:
                    outdated.append(skill_id)
            except ValueError:
                outdated.append(skill_id)
        
        return outdated
    
    def get_underperforming_skills(self, threshold: int = 60) -> List[SkillHealth]:
        """Get skills below health threshold."""
        health_data = self.load_health_data()
        return [h for h in health_data.values() if h.health_score < threshold]

# ============================================================================
# IMPROVEMENT PROPOSAL MANAGER
# ============================================================================

class ProposalManager:
    """Manages improvement proposals."""
    
    def __init__(self, proposals_file: Path):
        self.proposals_file = proposals_file
        self.proposals_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_proposals(self) -> Dict[str, ImprovementProposal]:
        """Load all proposals."""
        data = FileUtils.safe_json_read(self.proposals_file) or {}
        
        result = {}
        for prop_id, prop_dict in data.items():
            try:
                result[prop_id] = ImprovementProposal(
                    id=prop_id,
                    target_skill=prop_dict['target_skill'],
                    priority=Priority(prop_dict['priority']),
                    type=prop_dict['type'],
                    current_state=prop_dict.get('current_state', {}),
                    proposed_change=prop_dict.get('proposed_change', {}),
                    implementation=prop_dict.get('implementation', {}),
                    business_impact=prop_dict.get('business_impact', {}),
                    status=prop_dict.get('status', 'pending'),
                    created_at=prop_dict.get('created_at', datetime.now().isoformat())
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse proposal {prop_id}: {e}")
        
        return result
    
    def save_proposals(self, proposals: Dict[str, ImprovementProposal]) -> bool:
        """Save all proposals."""
        data = {prop_id: prop.to_dict() for prop_id, prop in proposals.items()}
        return FileUtils.safe_json_write(self.proposals_file, data)
    
    def create_proposal(self, skill_id: str, finding: Finding, 
                        context: Dict[str, Any]) -> ImprovementProposal:
        """Create a new improvement proposal from a finding."""
        prop_id = f"IMP-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(skill_id.encode()).hexdigest()[:6]}"
        
        proposal = ImprovementProposal(
            id=prop_id,
            target_skill=skill_id,
            priority=finding.severity,
            type=finding.type.name.lower(),
            current_state={'issue': finding.description, 'location': finding.location},
            proposed_change={'suggestion': finding.suggestion},
            implementation={'complexity': 'medium', 'risk': 'low'},
            business_impact={'time_saved': 'unknown', 'confidence': finding.confidence}
        )
        
        proposals = self.load_proposals()
        proposals[prop_id] = proposal
        self.save_proposals(proposals)
        
        return proposal
    
    def get_pending_proposals(self) -> List[ImprovementProposal]:
        """Get all pending proposals."""
        proposals = self.load_proposals()
        return [p for p in proposals.values() if p.status == 'pending']
    
    def update_proposal_status(self, proposal_id: str, status: str) -> bool:
        """Update proposal status."""
        proposals = self.load_proposals()
        if proposal_id in proposals:
            proposals[proposal_id].status = status
            return self.save_proposals(proposals)
        return False

# ============================================================================
# EVENT INTEGRATION (Tier 2 ALOE)
# ============================================================================

class EventBus:
    """Event bus for ALOE integration."""
    
    def __init__(self, event_dir: Path):
        self.event_dir = event_dir
        self.event_dir.mkdir(parents=True, exist_ok=True)
    
    def emit_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Emit an event to the event bus."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'source': 'SEE',
            'payload': payload
        }
        
        event_file = self.event_dir / f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        return FileUtils.safe_json_write(event_file, event)
    
    def emit_skill_analyzed(self, skill_id: str, health_score: int, findings_count: int) -> bool:
        """Emit skill analyzed event."""
        return self.emit_event('skill_analyzed', {
            'skill_id': skill_id,
            'health_score': health_score,
            'findings_count': findings_count
        })
    
    def emit_proposal_created(self, proposal: ImprovementProposal) -> bool:
        """Emit proposal created event."""
        return self.emit_event('proposal_created', proposal.to_dict())
    
    def emit_audit_completed(self, skill_id: str, audit_file: str) -> bool:
        """Emit audit completed event."""
        return self.emit_event('audit_completed', {
            'skill_id': skill_id,
            'audit_file': audit_file
        })

# ============================================================================
# MAIN SKILL EVOLUTION ENGINE
# ============================================================================

class SkillEvolutionEngine:
    """
    Main class for the Skill Evolution Engine (SEE).
    
    Self-improving skill analyzer that:
    - Analyzes existing skills (read SKILL.md, check implementations)
    - Detects gaps and improvement opportunities
    - Suggests new skill designs
    - Tracks skill performance over time
    - Generates skill audit reports
    - Proposes evolution paths
    """
    
    def __init__(self):
        self.parser = SkillParser(SEEConfig.SKILLS_DIR)
        self.analyzer = SkillAnalyzer(self.parser)
        self.audit_generator = AuditGenerator(SEEConfig.MEMORY_DIR / 'audit_history')
        self.registry = SkillRegistry(
            SEEConfig.SKILL_HEALTH_FILE,
            SEEConfig.PERFORMANCE_METRICS_FILE,
            SEEConfig.IMPROVEMENT_BACKLOG_FILE
        )
        self.proposal_manager = ProposalManager(SEEConfig.PROPOSALS_FILE)
        self.event_bus = EventBus(SEEConfig.MEMORY_DIR / 'events')
        
        self._shutdown = False
    
    # ====================================================================
    # CORE ANALYSIS METHODS
    # ====================================================================
    
    async def analyze_all_skills(self) -> Dict[str, SkillHealth]:
        """Analyze all discovered skills."""
        logger.info("Starting skill analysis...")
        
        skill_paths = self.parser.discover_skills()
        results = {}
        
        for skill_path in skill_paths:
            if self._shutdown:
                break
            
            skill_id = skill_path.name
            try:
                skill_health = await self.analyze_skill(skill_id)
                if skill_health:
                    results[skill_id] = skill_health
                    self.event_bus.emit_skill_analyzed(
                        skill_id, 
                        skill_health.health_score,
                        len(skill_health.findings)
                    )
            except Exception as e:
                logger.error(f"Error analyzing skill {skill_id}: {e}", exc_info=True)
        
        logger.info(f"Analyzed {len(results)} skills")
        return results
    
    async def analyze_skill(self, skill_id: str) -> Optional[SkillHealth]:
        """Analyze a specific skill."""
        skill_path = SEEConfig.SKILLS_DIR / skill_id
        
        if not skill_path.exists():
            logger.warning(f"Skill not found: {skill_id}")
            return None
        
        # Parse SKILL.md
        skill_data = self.parser.parse_skill_md(skill_path)
        
        # Calculate health score
        health_score, findings = self.analyzer.calculate_health_score(skill_data)
        
        # Detect gaps
        gaps = self.analyzer.detect_gaps(skill_data)
        
        # Generate recommendations
        recommendations = self.analyzer.generate_recommendations(findings, gaps)
        
        # Create health record
        health = SkillHealth(
            skill_id=skill_id,
            name=skill_data.get('name', skill_id),
            health_score=health_score,
            last_audit=datetime.now().isoformat(),
            findings=findings,
            recommendations=recommendations
        )
        
        # Update registry
        self.registry.update_skill_health(skill_id, health)
        
        # Generate audit if significant issues
        if health_score < 85 or len(findings) > 2:
            audit = self.audit_generator.generate_audit(
                skill_id, skill_data, health_score, findings, recommendations
            )
            audit_file = self.audit_generator.save_audit(audit)
            self.event_bus.emit_audit_completed(skill_id, str(audit_file))
        
        logger.info(f"Analyzed {skill_id}: score={health_score}, findings={len(findings)}")
        return health
    
    # ====================================================================
    # GAP DETECTION & PROPOSALS
    # ====================================================================
    
    async def detect_system_gaps(self) -> List[Dict[str, Any]]:
        """Detect gaps across the entire skill system."""
        logger.info("Detecting system gaps...")
        
        health_data = self.registry.load_health_data()
        gaps = []
        
        # Check for health coverage
        skill_paths = self.parser.discover_skills()
        analyzed_skills = set(health_data.keys())
        all_skills = {p.name for p in skill_paths}
        
        missing_analysis = all_skills - analyzed_skills
        if missing_analysis:
            gaps.append({
                'type': 'missing_analysis',
                'description': f'{len(missing_analysis)} skills not yet analyzed',
                'skills': list(missing_analysis)
            })
        
        # Check for low health skills
        underperforming = self.registry.get_underperforming_skills(SEEConfig.MIN_HEALTH_SCORE)
        if underperforming:
            gaps.append({
                'type': 'underperforming_skills',
                'description': f'{len(underperforming)} skills below health threshold',
                'skills': [h.skill_id for h in underperforming]
            })
        
        # Check for outdated audits
        outdated = self.registry.get_outdated_skills(SEEConfig.MAX_AUDIT_AGE_DAYS)
        if outdated:
            gaps.append({
                'type': 'outdated_audits',
                'description': f'{len(outdated)} skills have outdated audits',
                'skills': outdated
            })
        
        # Check for integration gaps
        integration_graph = self._build_integration_graph()
        circular = self._detect_circular_dependencies(integration_graph)
        if circular:
            gaps.append({
                'type': 'circular_dependencies',
                'description': f'{len(circular)} circular dependencies detected',
                'cycles': circular
            })
        
        return gaps
    
    def _build_integration_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph from skill integrations."""
        graph = {}
        
        for skill_path in self.parser.discover_skills():
            skill_id = skill_path.name
            skill_data = self.parser.parse_skill_md(skill_path)
            graph[skill_id] = set(skill_data.get('integration_points', []))
        
        return graph
    
    def _detect_circular_dependencies(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    async def generate_improvement_proposals(self) -> List[ImprovementProposal]:
        """Generate improvement proposals for identified issues."""
        logger.info("Generating improvement proposals...")
        
        proposals = []
        health_data = self.registry.load_health_data()
        
        for skill_id, health in health_data.items():
            for finding in health.findings:
                if finding.severity in (Priority.CRITICAL, Priority.HIGH):
                    proposal = self.proposal_manager.create_proposal(
                        skill_id, finding, {'health_score': health.health_score}
                    )
                    proposals.append(proposal)
                    self.event_bus.emit_proposal_created(proposal)
        
        logger.info(f"Generated {len(proposals)} proposals")
        return proposals
    
    # ====================================================================
    # NEW SKILL DESIGN
    # ====================================================================
    
    def suggest_new_skill(self, opportunity: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest a new skill design based on opportunity."""
        logger.info(f"Suggesting new skill for: {opportunity}")
        
        # Generate skill specification
        skill_spec = {
            'name': self._generate_skill_name(opportunity),
            'description': context.get('description', f'Automation for {opportunity}'),
            'purpose': context.get('purpose', f'Automate {opportunity} workflow'),
            'capabilities': context.get('capabilities', ['Automated execution', 'Error handling']),
            'inputs': context.get('inputs', ['user_request']),
            'outputs': context.get('outputs', ['result', 'status']),
            'tools': self._suggest_tools(opportunity, context),
            'integrations': self._suggest_integrations(opportunity, context),
            'estimated_effort': context.get('effort', 'medium'),
            'confidence': 0.7
        }
        
        return skill_spec
    
    def _generate_skill_name(self, opportunity: str) -> str:
        """Generate a skill name from opportunity description."""
        words = opportunity.lower().replace('for ', '').replace('to ', '').split()[:3]
        return '-'.join(words)
    
    def _suggest_tools(self, opportunity: str, context: Dict[str, Any]) -> List[str]:
        """Suggest tools based on opportunity."""
        tools = []
        opportunity_lower = opportunity.lower()
        
        if any(word in opportunity_lower for word in ['web', 'url', 'site', 'scrape']):
            tools.extend(['browser', 'web_fetch'])
        if any(word in opportunity_lower for word in ['file', 'save', 'load', 'read']):
            tools.extend(['read', 'write', 'edit'])
        if any(word in opportunity_lower for word in ['api', 'fetch', 'data', 'price']):
            tools.extend(['web_fetch', 'exec'])
        if any(word in opportunity_lower for word in ['notify', 'alert', 'message', 'send']):
            tools.extend(['message'])
        
        return tools or ['read', 'write']
    
    def _suggest_integrations(self, opportunity: str, context: Dict[str, Any]) -> List[str]:
        """Suggest integrations based on opportunity."""
        integrations = []
        opportunity_lower = opportunity.lower()
        
        if 'learning' in opportunity_lower:
            integrations.append('aloe')
        if 'opportunit' in opportunity_lower:
            integrations.append('autonomous-opportunity-engine')
        if 'code' in opportunity_lower or 'develop' in opportunity_lower:
            integrations.append('autonomous-code-architect')
        
        return integrations
    
    # ====================================================================
    # PERFORMANCE TRACKING
    # ====================================================================
    
    async def track_performance(self, skill_id: Optional[str] = None) -> Dict[str, SkillMetrics]:
        """Track skill performance over time."""
        logger.info("Tracking performance...")
        
        if skill_id:
            metrics = self._collect_metrics(skill_id)
            health = self.registry.get_skill_health(skill_id)
            if health:
                health.metrics = metrics
                self.registry.update_skill_health(skill_id, health)
            return {skill_id: metrics}
        
        # Track all skills
        all_metrics = {}
        for skill_path in self.parser.discover_skills():
            skill_id = skill_path.name
            metrics = self._collect_metrics(skill_id)
            all_metrics[skill_id] = metrics
            
            health = self.registry.get_skill_health(skill_id)
            if health:
                health.metrics = metrics
                self.registry.update_skill_health(skill_id, health)
        
        return all_metrics
    
    def _collect_metrics(self, skill_id: str) -> SkillMetrics:
        """Collect metrics for a skill."""
        # This would integrate with actual execution tracking
        # For now, return placeholder metrics based on file analysis
        
        skill_path = SEEConfig.SKILLS_DIR / skill_id
        metrics = SkillMetrics()
        
        # Count script files
        scripts_dir = skill_path / 'scripts'
        if scripts_dir.exists():
            metrics.tool_calls['scripts'] = len(list(scripts_dir.glob('*.py')))
        
        # Check for recent audit
        audit_history = FileUtils.safe_json_read(SEEConfig.AUDIT_HISTORY_FILE) or {}
        if skill_id in audit_history:
            recent_audits = audit_history[skill_id]
            if recent_audits:
                latest = recent_audits[-1]
                metrics.success_rate = latest.get('score', 0) / 100.0
        
        return metrics
    
    # ====================================================================
    # AUDIT & REPORTING
    # ====================================================================
    
    def generate_dashboard(self) -> str:
        """Generate performance dashboard."""
        health_data = self.registry.load_health_data()
        
        if not health_data:
            return "No skill data available. Run analysis first."
        
        # Calculate statistics
        scores = [h.health_score for h in health_data.values()]
        avg_score = sum(scores) / len(scores)
        top_performers = sorted(health_data.values(), key=lambda x: x.health_score, reverse=True)[:5]
        underperforming = [h for h in health_data.values() if h.health_score < SEEConfig.MIN_HEALTH_SCORE]
        
        lines = [
            "# Skill Evolution Dashboard",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Skills:** {len(health_data)}",
            f"**Average Health:** {avg_score:.1f}/100",
            "",
            "## Top Performers",
            "",
        ]
        
        for skill in top_performers:
            bar = "█" * int(skill.health_score / 10)
            lines.append(f"- **{skill.name}** {bar} {skill.health_score}%")
        
        lines.extend([
            "",
            "## Needs Attention",
            "",
        ])
        
        if underperforming:
            for skill in underperforming:
                lines.append(f"- **{skill.name}** ({skill.health_score}%) - {len(skill.findings)} issue(s)")
        else:
            lines.append("All skills above health threshold! 🎉")
        
        lines.extend([
            "",
            "## Recommendations",
            "",
            f"1. Review {len(underperforming)} underperforming skills",
            f"2. Update outdated audits",
            f"3. Address critical findings",
            "",
            "---",
            "*Generated by Skill Evolution Engine (SEE)*"
        ])
        
        return "\n".join(lines)
    
    def save_dashboard(self) -> Path:
        """Save dashboard to file."""
        dashboard = self.generate_dashboard()
        path = SEEConfig.MEMORY_DIR / 'dashboard.md'
        FileUtils.safe_write(path, dashboard)
        return path
    
    # ====================================================================
    # CLI INTERFACE
    # ====================================================================
    
    async def run_cli_command(self, command: str, args: List[str]) -> str:
        """Execute a CLI command."""
        commands = {
            'analyze': self._cmd_analyze,
            'dashboard': self._cmd_dashboard,
            'audit': self._cmd_audit,
            'propose': self._cmd_propose,
            'gaps': self._cmd_gaps,
            'health': self._cmd_health,
            'list': self._cmd_list,
        }
        
        handler = commands.get(command, self._cmd_help)
        return await handler(args)
    
    async def _cmd_analyze(self, args: List[str]) -> str:
        """Analyze command handler."""
        if args and args[0] != 'all':
            skill_id = args[0]
            health = await self.analyze_skill(skill_id)
            if health:
                return f"Analyzed {skill_id}: Health={health.health_score}%, Findings={len(health.findings)}"
            return f"Failed to analyze {skill_id}"
        
        results = await self.analyze_all_skills()
        return f"Analyzed {len(results)} skills. Run 'dashboard' to see results."
    
    async def _cmd_dashboard(self, args: List[str]) -> str:
        """Dashboard command handler."""
        path = self.save_dashboard()
        return f"Dashboard saved to: {path}\n\n{self.generate_dashboard()}"
    
    async def _cmd_audit(self, args: List[str]) -> str:
        """Audit command handler."""
        if not args:
            return "Usage: audit <skill_id>"
        
        skill_id = args[0]
        health = await self.analyze_skill(skill_id)
        
        if health:
            audit = self.audit_generator.generate_audit(
                skill_id,
                self.parser.parse_skill_md(SEEConfig.SKILLS_DIR / skill_id),
                health.health_score,
                health.findings,
                health.recommendations
            )
            path = self.audit_generator.save_audit(audit)
            return f"Audit saved to: {path}"
        
        return f"Failed to audit {skill_id}"
    
    async def _cmd_propose(self, args: List[str]) -> str:
        """Propose command handler."""
        proposals = await self.generate_improvement_proposals()
        return f"Generated {len(proposals)} improvement proposals"
    
    async def _cmd_gaps(self, args: List[str]) -> str:
        """Gaps command handler."""
        gaps = await self.detect_system_gaps()
        lines = ["System Gaps Detected:", ""]
        for gap in gaps:
            lines.append(f"- **{gap['type']}**: {gap['description']}")
        return "\n".join(lines)
    
    async def _cmd_health(self, args: List[str]) -> str:
        """Health command handler."""
        health_data = self.registry.load_health_data()
        
        if args:
            skill_id = args[0]
            health = health_data.get(skill_id)
            if health:
                return f"{skill_id}: Health={health.health_score}%, Status={health.status}"
            return f"No health data for {skill_id}"
        
        # Summary
        total = len(health_data)
        if total == 0:
            return "No health data. Run 'analyze' first."
        
        avg = sum(h.health_score for h in health_data.values()) / total
        low = len([h for h in health_data.values() if h.health_score < 60])
        
        return f"Health Summary: {total} skills, avg={avg:.1f}%, {low} below threshold"
    
    async def _cmd_list(self, args: List[str]) -> str:
        """List command handler."""
        skills = self.parser.discover_skills()
        lines = [f"Discovered {len(skills)} skills:", ""]
        
        health_data = self.registry.load_health_data()
        for skill_path in skills:
            skill_id = skill_path.name
            health = health_data.get(skill_id)
            if health:
                lines.append(f"- {skill_id} ({health.health_score}%)")
            else:
                lines.append(f"- {skill_id} (not analyzed)")
        
        return "\n".join(lines)
    
    async def _cmd_help(self, args: List[str]) -> str:
        """Help command handler."""
        return """
Available commands:
  analyze [skill_id|all]  Analyze skill(s)
  dashboard              Show performance dashboard
  audit <skill_id>       Generate audit report
  propose                Generate improvement proposals
  gaps                   Show system gaps
  health [skill_id]      Show health status
  list                   List all skills
  help                   Show this help
""".strip()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Skill Evolution Engine (SEE) - Tier 4 Meta-System'
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='dashboard',
        help='Command to execute (analyze, dashboard, audit, propose, gaps, health, list, help)'
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='Additional arguments for the command'
    )
    parser.add_argument(
        '--automatic',
        action='store_true',
        help='Run in automatic mode (for cron)'
    )
    parser.add_argument(
        '--emit-events',
        action='store_true',
        default=True,
        help='Emit events to ALOE'
    )
    
    cli_args = parser.parse_args()
    
    # Initialize engine
    engine = SkillEvolutionEngine()
    
    # Run command
    result = asyncio.run(engine.run_cli_command(cli_args.command, cli_args.args))
    print(result)
    
    # Automatic mode: run full analysis
    if cli_args.automatic:
        print("\n[Automatic Mode] Running full analysis...")
        health_results = asyncio.run(engine.analyze_all_skills())
        gaps = asyncio.run(engine.detect_system_gaps())
        proposals = asyncio.run(engine.generate_improvement_proposals())
        dashboard_path = engine.save_dashboard()
        
        print(f"\nAnalysis complete:")
        print(f"  - Analyzed {len(health_results)} skills")
        print(f"  - Detected {len(gaps)} system gaps")
        print(f"  - Generated {len(proposals)} proposals")
        print(f"  - Dashboard: {dashboard_path}")

if __name__ == '__main__':
    main()
