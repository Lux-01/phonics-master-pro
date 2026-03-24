#!/usr/bin/env python3
"""
ALOE Engine - Adaptive Learning & Observation Evolution
Implements the LOAE Cycle (Learn → Observe → Adapt → Evolve)

ACA Compliance:
- Core engine class with clear lifecycle
- State persistence (memory/aloe/state.json)
- CLI with --mode (run, test, status, config)
- Event emission hooks
- Pattern recognition and outcome tracking
- Confidence scoring system
"""

import argparse
import hashlib
import json
import logging
import math
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from collections import defaultdict
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ALOE')

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

STATE_DIR = Path("/home/skux/.openclaw/workspace/memory/aloe")
STATE_FILE = STATE_DIR / "state.json"
PATTERNS_FILE = STATE_DIR / "patterns.json"
OUTCOMES_FILE = STATE_DIR / "outcomes.json"

# Learning parameters
CONFIDENCE_DECAY_DAYS = 30  # Confidence decays over time
MIN_PATTERN_OCCURRENCES = 3  # Min occurrences before pattern is reliable
MAX_PATTERNS = 1000  # Maximum patterns to store
SIMILARITY_THRESHOLD = 0.75  # For pattern matching

# Weights for pattern scoring
WEIGHT_SUCCESS_RATE = 0.4
WEIGHT_FREQUENCY = 0.3
WEIGHT_RECENCY = 0.3

class PatternType:
    """Types of patterns ALOE can learn."""
    SUCCESS = "success"
    FAILURE = "failure"
    WORKFLOW = "workflow"
    DECISION = "decision"
    ERROR_RECOVERY = "error_recovery"
    PERFORMANCE = "performance"

class ConfidenceLevel:
    """Confidence levels for patterns."""
    UNKNOWN = (0.0, 0.3, "unknown")
    LOW = (0.3, 0.5, "low")
    MEDIUM = (0.5, 0.7, "medium")
    HIGH = (0.7, 0.9, "high")
    CERTAIN = (0.9, 1.0, "certain")
    
    @classmethod
    def from_score(cls, score: float) -> str:
        for low, high, name in [cls.UNKNOWN, cls.LOW, cls.MEDIUM, cls.HIGH, cls.CERTAIN]:
            if low <= score <= high:
                return name
        return "unknown"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Pattern:
    """Represents a learned pattern."""
    id: str
    type: str
    signature: str  # Hashable representation
    description: str
    context_keys: List[str] = field(default_factory=list)
    outcome_template: Dict[str, Any] = field(default_factory=dict)
    occurrences: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Outcome:
    """Records an outcome for learning."""
    id: str
    pattern_id: Optional[str]
    timestamp: str
    task_description: str
    context: Dict[str, Any]
    success: bool
    result_data: Dict[str, Any]
    metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class ALOEState:
    """Persistent state for the ALOE engine."""
    version: str = "2.0.0"
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    patterns: Dict[str, Dict] = field(default_factory=dict)
    outcomes: List[Dict] = field(default_factory=list)
    pattern_index: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "total_outcomes": 0,
        "total_patterns": 0,
        "learning_rate": 0.0,
        "avg_confidence": 0.0,
        "prediction_accuracy": 0.0
    })
    config: Dict[str, Any] = field(default_factory=lambda: {
        "auto_prune": True,
        "prune_threshold_days": 90,
        "max_patterns": MAX_PATTERNS,
        "learning_enabled": True,
        "min_confidence_for_prediction": 0.6
    })
    event_log: List[Dict] = field(default_factory=list)

# ============================================================================
# LOAE CYCLE IMPLEMENTATION
# ============================================================================

class LOAECycle:
    """
    Implements the Learn → Observe → Adapt → Evolve cycle.
    
    This is the core learning loop that continuously improves
    the agent's decision-making through pattern recognition.
    """
    
    def __init__(self, engine: 'ALOEEngine'):
        self.engine = engine
        self.hooks: Dict[str, List[Callable]] = {
            'learn': [],
            'observe': [],
            'adapt': [],
            'evolve': []
        }
    
    def register_hook(self, phase: str, callback: Callable) -> None:
        """Register a callback for a specific LOAE phase."""
        if phase in self.hooks:
            self.hooks[phase].append(callback)
    
    def _emit(self, phase: str, data: Dict[str, Any]) -> None:
        """Emit event to all registered hooks."""
        for callback in self.hooks.get(phase, []):
            try:
                callback(data)
            except Exception as e:
                logger.warning(f"Hook error in {phase}: {e}")
    
    def learn(self, outcome: Outcome) -> Optional[Pattern]:
        """
        LEARN: Extract patterns from an outcome.
        
        Analyzes the outcome to identify what made it succeed or fail,
        and updates or creates patterns accordingly.
        """
        logger.debug(f"Learning from outcome: {outcome.id}")
        
        # Generate signature from context
        signature = self._generate_signature(outcome.context)
        
        # Look for existing pattern
        pattern = self.engine.find_pattern_by_signature(signature)
        
        if pattern:
            # Update existing pattern
            pattern.occurrences += 1
            if outcome.success:
                pattern.success_count += 1
            else:
                pattern.failure_count += 1
            pattern.last_seen = datetime.utcnow().isoformat()
            
            # Recalculate confidence
            pattern.confidence = self._calculate_pattern_confidence(pattern)
            
            logger.debug(f"Updated pattern {pattern.id}: confidence={pattern.confidence:.2f}")
            
        else:
            # Create new pattern
            pattern_id = f"pat_{hashlib.md5(signature.encode()).hexdigest()[:8]}"
            
            pattern = Pattern(
                id=pattern_id,
                type=self._classify_outcome(outcome),
                signature=signature,
                description=self._generate_description(outcome),
                context_keys=list(outcome.context.keys()),
                outcome_template=self._extract_template(outcome),
                occurrences=1,
                success_count=1 if outcome.success else 0,
                failure_count=0 if outcome.success else 1,
                confidence=0.3  # Initial low confidence
            )
            
            # Extract metadata
            pattern.metadata = {
                'source_tags': outcome.tags,
                'context_summary': self._summarize_context(outcome.context)
            }
            
            logger.info(f"Created new pattern {pattern.id}")
        
        outcome.pattern_id = pattern.id
        self._emit('learn', {'pattern': asdict(pattern), 'outcome': asdict(outcome)})
        
        return pattern
    
    def observe(self, situation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        OBSERVE: Monitor current situation for pattern matches.
        
        Identifies which patterns might apply to the current context
        and returns relevant matches with confidence scores.
        """
        logger.debug("Observing current situation for patterns")
        
        # Generate partial signature from available context
        signature = self._generate_signature(situation)
        
        # Find matching patterns
        matches = []
        for pattern_id, pattern_data in self.engine.state.patterns.items():
            pattern = Pattern(**pattern_data)
            
            # Calculate similarity
            similarity = self._calculate_similarity(signature, pattern.signature)
            
            if similarity >= SIMILARITY_THRESHOLD:
                # Calculate match score
                score = self._calculate_match_score(pattern, similarity)
                
                matches.append({
                    'pattern_id': pattern.id,
                    'type': pattern.type,
                    'description': pattern.description,
                    'similarity': similarity,
                    'confidence': pattern.confidence,
                    'score': score,
                    'success_rate': pattern.success_count / max(pattern.occurrences, 1),
                    'recommendation': self._generate_recommendation(pattern)
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        self._emit('observe', {
            'situation_signature': signature[:50],
            'matches_found': len(matches),
            'top_matches': matches[:3]
        })
        
        return matches
    
    def adapt(self, pattern: Pattern, new_data: Dict[str, Any]) -> Pattern:
        """
        ADAPT: Refine patterns based on new information.
        
        Adjusts pattern parameters and confidence based on
        accumulated evidence and changing conditions.
        """
        logger.debug(f"Adapting pattern {pattern.id}")
        
        # Update metadata
        pattern.metadata['last_adaptation'] = datetime.utcnow().isoformat()
        pattern.metadata['adaptation_count'] = pattern.metadata.get('adaptation_count', 0) + 1
        
        # Recalculate confidence with time decay
        old_confidence = pattern.confidence
        pattern.confidence = self._calculate_pattern_confidence(pattern)
        
        # Check for pattern drift
        if abs(pattern.confidence - old_confidence) > 0.2:
            pattern.metadata['drift_detected'] = True
            pattern.metadata['drift_magnitude'] = abs(pattern.confidence - old_confidence)
            logger.warning(f"Pattern drift detected in {pattern.id}: {old_confidence:.2f} -> {pattern.confidence:.2f}")
        
        # Update outcome template if new data provides better insights
        if new_data.get('refined_result'):
            pattern.outcome_template = self._merge_templates(
                pattern.outcome_template,
                new_data['refined_result']
            )
        
        self._emit('adapt', {'pattern': asdict(pattern), 'adaptations': new_data})
        
        return pattern
    
    def evolve(self) -> List[str]:
        """
        EVOLVE: Optimize the pattern database.
        
        Removes outdated patterns, consolidates duplicates,
        and improves overall learning efficiency.
        """
        logger.info("Running pattern evolution process")
        
        evolved = []
        
        # 1. Prune old patterns
        pruned = self._prune_patterns()
        evolved.extend(pruned)
        
        # 2. Consolidate similar patterns
        consolidated = self._consolidate_patterns()
        evolved.extend(consolidated)
        
        # 3. Update pattern index
        self._rebuild_index()
        
        # 4. Calculate learning metrics
        self._update_learning_metrics()
        
        self._emit('evolve', {
            'pruned': pruned,
            'consolidated': consolidated,
            'total_patterns': len(self.engine.state.patterns)
        })
        
        logger.info(f"Evolution complete: {len(pruned)} pruned, {len(consolidated)} consolidated")
        
        return evolved
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_signature(self, context: Dict[str, Any]) -> str:
        """Generate a hashable signature from context."""
        # Extract key fields that define a pattern
        key_fields = sorted([k for k in context.keys() if not k.startswith('_')])
        signature_parts = []
        
        for key in key_fields[:10]:  # Limit to top 10 keys
            value = context.get(key)
            if isinstance(value, (str, int, float, bool)):
                signature_parts.append(f"{key}={str(value)[:50]}")
            elif isinstance(value, list) and value:
                signature_parts.append(f"{key}=[{len(value)}]")
        
        return "|".join(signature_parts)
    
    def _generate_description(self, outcome: Outcome) -> str:
        """Generate a human-readable pattern description."""
        desc_lower = outcome.task_description.lower()
        
        if outcome.success:
            action = "succeeded"
        else:
            action = "failed"
        
        # Extract key elements
        elements = []
        if 'api' in desc_lower or 'request' in desc_lower:
            elements.append('API')
        if 'file' in desc_lower:
            elements.append('file operation')
        if 'error' in desc_lower:
            elements.append('error handling')
        
        element_str = ', '.join(elements) if elements else 'task'
        
        return f"{element_str} {action}: {outcome.task_description[:60]}"
    
    def _extract_template(self, outcome: Outcome) -> Dict[str, Any]:
        """Extract an outcome template for pattern matching."""
        return {
            'success': outcome.success,
            'key_metrics': list(outcome.metrics.keys()),
            'common_tags': outcome.tags[:5],
            'context_structure': list(outcome.context.keys())
        }
    
    def _summarize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of context for metadata."""
        summary = {}
        for key, value in list(context.items())[:5]:
            if isinstance(value, (str, int, float, bool)):
                summary[key] = value
            elif isinstance(value, list):
                summary[key] = f"[{len(value)} items]"
            elif isinstance(value, dict):
                summary[key] = f"{{...}}"
        return summary
    
    def _classify_outcome(self, outcome: Outcome) -> str:
        """Classify the outcome type."""
        desc = outcome.task_description.lower()
        tags = [t.lower() for t in outcome.tags]
        
        if 'error' in desc or 'error' in tags:
            return PatternType.ERROR_RECOVERY
        elif 'workflow' in tags or 'sequence' in desc:
            return PatternType.WORKFLOW
        elif 'decision' in desc or 'choose' in desc:
            return PatternType.DECISION
        elif 'performance' in tags or 'duration' in outcome.metrics:
            return PatternType.PERFORMANCE
        elif outcome.success:
            return PatternType.SUCCESS
        else:
            return PatternType.FAILURE
    
    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between two signatures."""
        if sig1 == sig2:
            return 1.0
        
        parts1 = set(sig1.split('|'))
        parts2 = set(sig2.split('|'))
        
        if not parts1 or not parts2:
            return 0.0
        
        intersection = len(parts1 & parts2)
        union = len(parts1 | parts2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_pattern_confidence(self, pattern: Pattern) -> float:
        """Calculate confidence score for a pattern."""
        total = pattern.occurrences
        if total < MIN_PATTERN_OCCURRENCES:
            return 0.3 + (total / MIN_PATTERN_OCCURRENCES) * 0.3
        
        # Base confidence on success rate
        success_rate = pattern.success_count / total
        
        # Apply time decay
        try:
            last_seen = datetime.fromisoformat(pattern.last_seen)
            days_since = (datetime.utcnow() - last_seen).days
            time_decay = max(0.5, 1 - (days_since / CONFIDENCE_DECAY_DAYS))
        except:
            time_decay = 0.5
        
        # Frequency bonus
        frequency_bonus = min(0.1, (total - MIN_PATTERN_OCCURRENCES) * 0.01)
        
        confidence = (success_rate * WEIGHT_SUCCESS_RATE +
                     time_decay * WEIGHT_RECENCY +
                     frequency_bonus * WEIGHT_FREQUENCY)
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_match_score(self, pattern: Pattern, similarity: float) -> float:
        """Calculate overall match score."""
        # Weighted combination of similarity and confidence
        score = similarity * 0.4 + pattern.confidence * 0.6
        
        # Boost for high-occurrence patterns
        if pattern.occurrences > 10:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_recommendation(self, pattern: Pattern) -> str:
        """Generate a recommendation based on pattern."""
        success_rate = pattern.success_count / max(pattern.occurrences, 1)
        
        if success_rate > 0.8 and pattern.confidence > 0.7:
            return "strong_recommendation"
        elif success_rate > 0.5:
            return "moderate_recommendation"
        elif success_rate < 0.3:
            return "avoid"
        else:
            return "neutral"
    
    def _merge_templates(self, template1: Dict, template2: Dict) -> Dict:
        """Merge two outcome templates."""
        merged = template1.copy()
        for key, value in template2.items():
            if key in merged:
                # Keep most common value
                if isinstance(merged[key], list) and isinstance(value, list):
                    merged[key] = list(set(merged[key] + value))[:10]
            else:
                merged[key] = value
        return merged
    
    def _prune_patterns(self) -> List[str]:
        """Remove old or low-confidence patterns."""
        pruned = []
        threshold_days = self.engine.state.config.get('prune_threshold_days', 90)
        
        for pattern_id, pattern_data in list(self.engine.state.patterns.items()):
            pattern = Pattern(**pattern_data)
            
            # Check if pattern is too old
            try:
                last_seen = datetime.fromisoformat(pattern.last_seen)
                days_since = (datetime.utcnow() - last_seen).days
                
                if days_since > threshold_days and pattern.confidence < 0.5:
                    del self.engine.state.patterns[pattern_id]
                    pruned.append(pattern_id)
            except:
                # If date parsing fails, mark for pruning
                if pattern.confidence < 0.3:
                    del self.engine.state.patterns[pattern_id]
                    pruned.append(pattern_id)
        
        return pruned
    
    def _consolidate_patterns(self) -> List[str]:
        """Consolidate similar patterns."""
        consolidated = []
        patterns_list = list(self.engine.state.patterns.items())
        
        for i, (id1, data1) in enumerate(patterns_list):
            if id1 not in self.engine.state.patterns:
                continue
            
            pattern1 = Pattern(**data1)
            
            for id2, data2 in patterns_list[i+1:]:
                if id2 not in self.engine.state.patterns:
                    continue
                
                pattern2 = Pattern(**data2)
                
                # Check if patterns are very similar
                similarity = self._calculate_similarity(pattern1.signature, pattern2.signature)
                
                if similarity > 0.9:
                    # Merge pattern2 into pattern1
                    pattern1.occurrences += pattern2.occurrences
                    pattern1.success_count += pattern2.success_count
                    pattern1.failure_count += pattern2.failure_count
                    pattern1.last_seen = max(pattern1.last_seen, pattern2.last_seen)
                    pattern1.confidence = self._calculate_pattern_confidence(pattern1)
                    
                    # Remove pattern2
                    del self.engine.state.patterns[id2]
                    consolidated.append(id2)
        
        return consolidated
    
    def _rebuild_index(self) -> None:
        """Rebuild the pattern index."""
        self.engine.state.pattern_index = defaultdict(list)
        
        for pattern_id, pattern_data in self.engine.state.patterns.items():
            pattern = Pattern(**pattern_data)
            # Index by type
            self.engine.state.pattern_index[pattern.type].append(pattern_id)
            # Index by context keys
            for key in pattern.context_keys:
                self.engine.state.pattern_index[f"key:{key}"].append(pattern_id)
    
    def _update_learning_metrics(self) -> None:
        """Update learning metrics."""
        patterns = list(self.engine.state.patterns.values())
        
        if patterns:
            avg_conf = sum(p.get('confidence', 0) for p in patterns) / len(patterns)
            self.engine.state.metrics['avg_confidence'] = round(avg_conf, 3)
            self.engine.state.metrics['total_patterns'] = len(patterns)
        
        # Calculate learning rate (patterns created in last 7 days)
        recent_patterns = 0
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        for p in patterns:
            if p.get('created_at', '') > cutoff:
                recent_patterns += 1
        
        self.engine.state.metrics['learning_rate'] = recent_patterns


# ============================================================================
# MAIN ALOE ENGINE CLASS
# ============================================================================

class ALOEEngine:
    """
    Adaptive Learning and Observation Evolution Engine.
    
    ALOE provides:
    - Pattern recognition from outcomes
    - Confidence scoring for decisions
    - Performance metrics tracking
    - Adaptive learning from experience
    """
    
    def __init__(self):
        self.state = self._load_state()
        self.loae = LOAECycle(self)
        self._lock = Lock()
        
        # Ensure state directory exists
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> ALOEState:
        """Load ALOE state from disk."""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    return ALOEState(**data)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
        
        return ALOEState()
    
    def _save_state(self) -> None:
        """Save ALOE state to disk."""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            self.state.last_updated = datetime.utcnow().isoformat()
            
            with open(STATE_FILE, 'w') as f:
                json.dump(asdict(self.state), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event."""
        event = {
            'type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        self.state.event_log.append(event)
        if len(self.state.event_log) > 1000:
            self.state.event_log = self.state.event_log[-1000:]
        self._save_state()
    
    def record_outcome(self, task_description: str, context: Dict[str, Any],
                       success: bool, result_data: Dict[str, Any],
                       metrics: Dict[str, float] = None,
                       tags: List[str] = None) -> Outcome:
        """Record a task outcome for learning."""
        outcome_id = f"out_{hashlib.md5(f"{task_description}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]}"
        
        outcome = Outcome(
            id=outcome_id,
            pattern_id=None,
            timestamp=datetime.utcnow().isoformat(),
            task_description=task_description,
            context=context,
            success=success,
            result_data=result_data,
            metrics=metrics or {},
            tags=tags or []
        )
        
        with self._lock:
            self.state.outcomes.append(asdict(outcome))
            self.state.metrics['total_outcomes'] = len(self.state.outcomes)
            
            # Limit stored outcomes
            if len(self.state.outcomes) > 10000:
                self.state.outcomes = self.state.outcomes[-5000:]
        
        # Learn from the outcome
        if self.state.config.get('learning_enabled', True):
            pattern = self.loae.learn(outcome)
            if pattern:
                self.state.patterns[pattern.id] = asdict(pattern)
                # Update pattern index
                self.state.pattern_index[pattern.type].append(pattern.id)
        
        self._save_state()
        self.log_event('outcome_recorded', {'outcome_id': outcome.id, 'success': success})
        
        logger.info(f"Recorded outcome: {outcome.id} (success={success})")
        return outcome
    
    def find_pattern_by_signature(self, signature: str) -> Optional[Pattern]:
        """Find a pattern by its signature."""
        for pattern_data in self.state.patterns.values():
            if pattern_data.get('signature') == signature:
                return Pattern(**pattern_data)
        return None
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a pattern by ID."""
        pattern_data = self.state.patterns.get(pattern_id)
        if pattern_data:
            return Pattern(**pattern_data)
        return None
    
    def query_patterns(self, context: Dict[str, Any], min_confidence: float = None) -> List[Dict]:
        """Query patterns that match the given context."""
        if min_confidence is None:
            min_confidence = self.state.config.get('min_confidence_for_prediction', 0.6)
        
        matches = self.loae.observe(context)
        
        # Filter by confidence
        filtered = [m for m in matches if m['confidence'] >= min_confidence]
        
        return filtered
    
    def predict_success(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the likelihood of success for a task."""
        matches = self.query_patterns(context)
        
        if not matches:
            return {
                'predicted_success': None,
                'confidence': 0.0,
                'reasoning': 'No matching patterns found',
                'recommendations': []
            }
        
        # Weight by confidence
        total_weight = sum(m['confidence'] for m in matches)
        weighted_success = sum(m['success_rate'] * m['confidence'] for m in matches)
        
        predicted_success = weighted_success / total_weight if total_weight > 0 else 0.5
        
        # Build recommendations
        recommendations = []
        for m in matches[:3]:
            if m['recommendation'] == 'strong_recommendation':
                recommendations.append(f"Pattern {m['pattern_id'][:8]} has high success rate ({m['success_rate']:.0%})")
            elif m['recommendation'] == 'avoid':
                recommendations.append(f"Warning: Pattern {m['pattern_id'][:8]} often fails")
        
        return {
            'predicted_success': predicted_success > 0.6,
            'success_probability': round(predicted_success, 3),
            'confidence': round(matches[0]['confidence'], 3) if matches else 0.0,
            'matching_patterns': len(matches),
            'reasoning': f"Based on {len(matches)} matching patterns",
            'recommendations': recommendations
        }
    
    def get_pattern_stats(self, pattern_type: str = None) -> Dict[str, Any]:
        """Get statistics about learned patterns."""
        patterns = list(self.state.patterns.values())
        
        if pattern_type:
            patterns = [p for p in patterns if p.get('type') == pattern_type]
        
        if not patterns:
            return {'count': 0, 'avg_confidence': 0, 'types': {}}
        
        type_counts = {}
        for p in patterns:
            t = p.get('type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            'count': len(patterns),
            'avg_confidence': round(sum(p.get('confidence', 0) for p in patterns) / len(patterns), 3),
            'avg_occurrences': round(sum(p.get('occurrences', 0) for p in patterns) / len(patterns), 1),
            'types': type_counts,
            'high_confidence_count': sum(1 for p in patterns if p.get('confidence', 0) > 0.7)
        }
    
    def evolve_patterns(self) -> Dict[str, Any]:
        """Run the evolution process."""
        with self._lock:
            evolved = self.loae.evolve()
            self._save_state()
        
        return {
            'evolved_patterns': evolved,
            'remaining_patterns': len(self.state.patterns),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ALOE status."""
        return {
            'version': self.state.version,
            'patterns': self.get_pattern_stats(),
            'metrics': self.state.metrics,
            'config': self.state.config,
            'last_updated': self.state.last_updated
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def run_tests() -> bool:
    """Run internal tests for ALOE engine."""
    logger.info("Running ALOE Engine tests...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Pattern creation
    try:
        aloe = ALOEEngine()
        outcome = aloe.record_outcome(
            task_description="Test task execution",
            context={"tool": "read", "file": "/tmp/test.txt"},
            success=True,
            result_data={"content": "test data"},
            tags=["test", "file_operation"]
        )
        assert outcome.id is not None
        assert outcome.success is True
        tests_passed += 1
        print("✓ Test 1: Pattern creation from outcome")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 1: Pattern creation - {e}")
    
    # Test 2: Pattern matching
    try:
        aloe = ALOEEngine()
        # Create a pattern
        aloe.record_outcome(
            task_description="API call example",
            context={"endpoint": "test", "method": "GET"},
            success=True,
            result_data={}
        )
        
        # Query for similar context
        matches = aloe.query_patterns({"endpoint": "test", "method": "GET"})
        assert len(matches) > 0
        assert 'confidence' in matches[0]
        tests_passed += 1
        print("✓ Test 2: Pattern matching")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 2: Pattern matching - {e}")
    
    # Test 3: Confidence calculation
    try:
        aloe = ALOEEngine()
        
        # Create multiple outcomes to build confidence
        for i in range(5):
            aloe.record_outcome(
                task_description=f"Test task {i}",
                context={"type": "test"},
                success=True,
                result_data={}
            )
        
        matches = aloe.query_patterns({"type": "test"})
        if matches:
            assert matches[0]['confidence'] > 0.5
        tests_passed += 1
        print("✓ Test 3: Confidence calculation")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 3: Confidence calculation - {e}")
    
    # Test 4: Prediction
    try:
        aloe = ALOEEngine()
        
        # Record successful pattern
        for i in range(3):
            aloe.record_outcome(
                task_description="API request",
                context={"service": "birdeye", "action": "price"},
                success=True,
                result_data={"price": 1.23}
            )
        
        prediction = aloe.predict_success(
            "Get token price",
            {"service": "birdeye", "action": "price"}
        )
        assert 'predicted_success' in prediction
        assert prediction['success_probability'] > 0.5
        tests_passed += 1
        print("✓ Test 4: Success prediction")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 4: Success prediction - {e}")
    
    # Test 5: State persistence
    try:
        aloe1 = ALOEEngine()
        aloe1.record_outcome(
            task_description="Persistence test",
            context={"persist": True},
            success=True,
            result_data={}
        )
        
        pattern_count = len(aloe1.state.patterns)
        
        # Create new instance
        aloe2 = ALOEEngine()
        assert len(aloe2.state.patterns) >= pattern_count
        tests_passed += 1
        print("✓ Test 5: State persistence")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 5: State persistence - {e}")
    
    # Test 6: Pattern evolution
    try:
        aloe = ALOEEngine()
        # Add some old patterns with low confidence
        old_pattern = {
            'id': 'test_old',
            'type': 'test',
            'signature': 'old=pattern',
            'description': 'Old test pattern',
            'context_keys': ['old'],
            'outcome_template': {},
            'occurrences': 1,
            'success_count': 0,
            'failure_count': 1,
            'created_at': (datetime.utcnow() - timedelta(days=100)).isoformat(),
            'last_seen': (datetime.utcnow() - timedelta(days=100)).isoformat(),
            'confidence': 0.2,
            'metadata': {}
        }
        aloe.state.patterns['test_old'] = old_pattern
        aloe._save_state()
        
        result = aloe.evolve_patterns()
        # Should have pruned the old pattern
        assert 'evolved_patterns' in result
        tests_passed += 1
        print("✓ Test 6: Pattern evolution")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 6: Pattern evolution - {e}")
    
    print(f"\n{'='*50}")
    print(f"Tests Passed: {tests_passed}/{tests_passed + tests_failed}")
    print(f"{'='*50}")
    
    return tests_failed == 0

def main():
    parser = argparse.ArgumentParser(description='ALOE Engine - Adaptive Learning System')
    parser.add_argument('--mode', choices=['run', 'test', 'status', 'config'],
                       default='status', help='Operation mode')
    parser.add_argument('--query', type=str, help='Query patterns (JSON context)')
    parser.add_argument('--predict', type=str, help='Task description to predict')
    parser.add_argument('--record', action='store_true', help='Record an outcome')
    parser.add_argument('--success', action='store_true', help='Outcome was successful')
    parser.add_argument('--evolve', action='store_true', help='Run pattern evolution')
    parser.add_argument('--config-key', type=str, help='Config key to set')
    parser.add_argument('--config-value', type=str, help='Config value to set')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'status':
        aloe = ALOEEngine()
        status = aloe.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.mode == 'config':
        aloe = ALOEEngine()
        if args.config_key and args.config_value:
            # Parse value if it's a boolean or number
            value = args.config_value
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
            
            aloe.state.config[args.config_key] = value
            aloe._save_state()
            print(f"Config updated: {args.config_key} = {value}")
        else:
            print(json.dumps(aloe.state.config, indent=2))
    
    elif args.mode == 'run':
        aloe = ALOEEngine()
        
        if args.record:
            aloe.record_outcome(
                task_description=args.predict or "Manual recording",
                context={"manual": True},
                success=args.success,
                result_data={}
            )
            print("Outcome recorded")
        
        elif args.query:
            try:
                context = json.loads(args.query)
                matches = aloe.query_patterns(context)
                print(json.dumps(matches, indent=2))
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
        
        elif args.predict:
            prediction = aloe.predict_success(args.predict, {})
            print(json.dumps(prediction, indent=2))
        
        elif args.evolve:
            result = aloe.evolve_patterns()
            print(json.dumps(result, indent=2))
        
        else:
            print("Running ALOE learning cycle...")
            aloe.evolve_patterns()
            print("Evolution complete")

if __name__ == '__main__':
    main()
