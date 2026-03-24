---
name: pattern-extractor
description: Mine patterns from user behavior, task outcomes, and system interactions. Identifies successful workflows, common sequences, and optimization opportunities for continuous improvement.
---

# Pattern Extractor

**Find the patterns that lead to success.**

The Pattern Extractor analyzes historical data to identify recurring patterns in user behavior, successful workflows, and optimal approaches. These patterns feed into ALOE for continuous improvement.

## Core Philosophy

**Success leaves clues. Find them.**

Patterns are everywhere:
- User behavior patterns
- Successful workflow patterns
- Tool usage patterns
- Timing patterns
- Context patterns

## Architecture

```
┌─────────────────────────────────────────┐
│         PATTERN EXTRACTOR               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   DATA       │  │   PATTERN    │    │
│  │   INGESTER   │  │   MINER      │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   PATTERN       │             │
│         │   VALIDATOR     │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   PATTERN       │             │
│         │   STORE         │             │
│         └─────────────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

## Pattern Types

### 1. Temporal Patterns

**Time-Based:**
```python
temporal_patterns = {
    "morning_routine": {
        "time": "08:00-09:00",
        "actions": ["check_crypto", "review_calendar"],
        "frequency": "daily",
        "confidence": 0.92
    },
    "focus_time": {
        "time": "09:00-12:00",
        "activity": "deep_work",
        "frequency": "weekdays",
        "confidence": 0.85
    },
    "end_of_day": {
        "time": "17:00-18:00",
        "actions": ["daily_summary", "plan_tomorrow"],
        "frequency": "daily",
        "confidence": 0.88
    }
}
```

**Day-Based:**
```python
day_patterns = {
    "monday": {
        "theme": "planning",
        "common_tasks": ["week_planning", "review_goals"]
    },
    "friday": {
        "theme": "review",
        "common_tasks": ["week_summary", "income_review"]
    },
    "sunday": {
        "theme": "strategy",
        "common_tasks": ["strategy_review", "learning"]
    }
}
```

### 2. Sequential Patterns

**Action Sequences:**
```python
sequential_patterns = {
    "coding_workflow": {
        "sequence": ["code", "test", "commit", "push"],
        "frequency": 0.95,
        "avg_time": "45_minutes"
    },
    "research_workflow": {
        "sequence": ["search", "read", "synthesize", "document"],
        "frequency": 0.88
    },
    "trading_workflow": {
        "sequence": ["scan", "analyze", "decide", "execute", "log"],
        "frequency": 0.92
    }
}
```

**Tool Usage Sequences:**
```python
tool_sequences = {
    "file_editing": {
        "sequence": ["read", "edit", "read", "exec"],
        "frequency": 0.90
    },
    "web_research": {
        "sequence": ["web_fetch", "web_fetch", "web_fetch", "synthesize"],
        "frequency": 0.85
    }
}
```

### 3. Contextual Patterns

**Activity-Based:**
```python
context_patterns = {
    "after_coding": {
        "context": "just_finished_coding",
        "next_actions": ["commit", "test", "review"],
        "probability": 0.87
    },
    "before_meeting": {
        "context": "meeting_in_15_min",
        "next_actions": ["review_docs", "prep_notes"],
        "probability": 0.82
    },
    "market_volatile": {
        "context": "high_volatility_detected",
        "next_actions": ["check_positions", "review_stops"],
        "probability": 0.91
    }
}
```

**Environment-Based:**
```python
environment_patterns = {
    "desktop_session": {
        "device": "desktop",
        "activities": ["coding", "research", "multi_task"],
        "avg_duration": "3_hours"
    },
    "mobile_session": {
        "device": "mobile",
        "activities": ["quick_checks", "monitoring", "messaging"],
        "avg_duration": "15_minutes"
    }
}
```

### 4. Success Patterns

**What leads to success:**
```python
success_patterns = {
    "successful_coding": {
        "prerequisites": ["clear_requirements", "aca_plan"],
        "tools": ["autonomous-code-architect"],
        "approach": "plan_first_then_code",
        "success_rate": 0.94
    },
    "successful_research": {
        "prerequisites": ["multi_source"],
        "tools": ["research-synthesizer"],
        "approach": "synthesize_not_summarize",
        "success_rate": 0.89
    },
    "successful_trading": {
        "prerequisites": ["grade_a_signal", "risk_check"],
        "tools": ["autonomous-trading-strategist"],
        "approach": "follow_strategy_rules",
        "success_rate": 0.76
    }
}
```

### 5. Failure Patterns

**What leads to failure:**
```python
failure_patterns = {
    "coding_failures": {
        "red_flags": ["no_planning", "rushed", "no_testing"],
        "common_errors": ["syntax_errors", "logic_bugs"],
        "avoidance_strategy": "always_use_aca"
    },
    "research_failures": {
        "red_flags": ["single_source", "no_synthesis"],
        "common_issues": ["incomplete_info", "contradictions_missed"],
        "avoidance_strategy": "use_research_synthesizer"
    }
}
```

## Pattern Mining Algorithms

### Apriori Algorithm (Association Rules)

```python
def mine_association_rules(transactions, min_support=0.1, min_confidence=0.7):
    """
    Find patterns like:
    - If user does X, they likely do Y next
    - If context is A, user needs B
    """
    
    # Find frequent itemsets
    frequent_itemsets = apriori(transactions, min_support)
    
    # Generate rules
    rules = []
    for itemset in frequent_itemsets:
        for antecedent, consequent in generate_rules(itemset):
            confidence = calculate_confidence(antecedent, consequent)
            if confidence >= min_confidence:
                rules.append({
                    'if': antecedent,
                    'then': consequent,
                    'confidence': confidence,
                    'support': calculate_support(itemset)
                })
    
    return rules
```

### Sequence Mining (PrefixSpan)

```python
def mine_sequences(sequences, min_support=0.1):
    """
    Find common action sequences
    """
    
    patterns = prefixspan(sequences, min_support)
    
    return [
        {
            'sequence': pattern.sequence,
            'support': pattern.support,
            'frequency': pattern.frequency
        }
        for pattern in patterns
    ]
```

### Temporal Pattern Mining

```python
def mine_temporal_patterns(events, time_granularity='hour'):
    """
    Find time-based patterns
    """
    
    # Group events by time
    time_groups = group_by_time(events, time_granularity)
    
    # Find recurring patterns
    patterns = []
    for time_slot, slot_events in time_groups.items():
        common_actions = find_common_actions(slot_events)
        if len(common_actions) > 0:
            patterns.append({
                'time': time_slot,
                'actions': common_actions,
                'frequency': len(slot_events) / total_days
            })
    
    return patterns
```

## Pattern Validation

### Confidence Scoring

```python
class PatternValidator:
    def validate_pattern(self, pattern) -> ValidationResult:
        """Validate a discovered pattern"""
        
        score = 0
        checks = []
        
        # Check frequency
        if pattern.frequency >= 0.7:
            score += 30
            checks.append("High frequency ✓")
        elif pattern.frequency >= 0.5:
            score += 20
            checks.append("Medium frequency")
        else:
            checks.append("Low frequency ✗")
        
        # Check consistency
        if pattern.consistency >= 0.8:
            score += 30
            checks.append("High consistency ✓")
        
        # Check recency
        if pattern.last_seen < 7_days:
            score += 20
            checks.append("Recent activity ✓")
        
        # Check specificity
        if pattern.is_specific():
            score += 20
            checks.append("Specific pattern ✓")
        
        return ValidationResult(
            score=score,
            is_valid=score >= 60,
            checks=checks
        )
```

### Statistical Significance

```python
def calculate_significance(pattern, baseline):
    """Calculate statistical significance of pattern"""
    
    # Chi-square test
    chi2, p_value = chisquare(pattern.observed, baseline.expected)
    
    # Effect size
    effect_size = calculate_effect_size(pattern, baseline)
    
    return {
        'p_value': p_value,
        'significant': p_value < 0.05,
        'effect_size': effect_size
    }
```

## Implementation

### Core Extractor

```python
class PatternExtractor:
    def __init__(self):
        self.data_ingester = DataIngester()
        self.miners = {
            'temporal': TemporalMiner(),
            'sequential': SequenceMiner(),
            'contextual': ContextMiner(),
            'success': SuccessMiner(),
            'failure': FailureMiner()
        }
        self.validator = PatternValidator()
        self.storage = PatternStorage()
    
    def extract_all_patterns(self, timeframe='30d'):
        """Extract all pattern types"""
        
        # Ingest data
        data = self.data_ingester.ingest(timeframe)
        
        patterns = {}
        
        # Mine each pattern type
        for pattern_type, miner in self.miners.items():
            raw_patterns = miner.mine(data)
            
            # Validate patterns
            valid_patterns = [
                p for p in raw_patterns
                if self.validator.validate(p).is_valid
            ]
            
            patterns[pattern_type] = valid_patterns
        
        # Store patterns
        self.storage.store(patterns)
        
        return patterns
    
    def get_patterns_for_context(self, context):
        """Get patterns relevant to current context"""
        
        all_patterns = self.storage.load()
        
        # Filter by context
        relevant = []
        for pattern in all_patterns:
            if pattern.matches_context(context):
                relevant.append(pattern)
        
        # Sort by confidence
        relevant.sort(key=lambda p: p.confidence, reverse=True)
        
        return relevant[:10]  # Top 10
```

## Usage Examples

### Example 1: Extract User Patterns
```python
extractor = PatternExtractor()

# Extract patterns from last 30 days
patterns = extractor.extract_all_patterns(timeframe='30d')

print("Discovered Patterns:")
print(f"Temporal: {len(patterns['temporal'])}")
print(f"Sequential: {len(patterns['sequential'])}")
print(f"Success: {len(patterns['success'])}")

# Top temporal pattern
if patterns['temporal']:
    top = patterns['temporal'][0]
    print(f"\nTop Pattern: {top.description}")
    print(f"Confidence: {top.confidence:.1%}")
```

### Example 2: Get Contextual Patterns
```python
# Current context
context = {
    'time': '08:30',
    'day': 'monday',
    'activity': 'starting_work',
    'device': 'desktop'
}

# Get relevant patterns
patterns = extractor.get_patterns_for_context(context)

for pattern in patterns:
    print(f"💡 {pattern.description} ({pattern.confidence:.0%} confidence)")
```

### Example 3: Success Pattern Analysis
```python
# Analyze what leads to success
success_patterns = extractor.get_success_patterns()

print("Keys to Success:")
for pattern in success_patterns:
    print(f"\n{pattern.name}:")
    print(f"  Success rate: {pattern.success_rate:.1%}")
    print(f"  Key factors: {', '.join(pattern.key_factors)}")
    print(f"  Recommended approach: {pattern.approach}")
```

## Configuration

```yaml
# pattern_extractor.yaml

mining:
  min_support: 0.1
  min_confidence: 0.7
  max_pattern_length: 5
  
timeframes:
  short: 7d
  medium: 30d
  long: 90d

validation:
  min_frequency: 0.5
  min_consistency: 0.7
  require_recency: true

pattern_types:
  temporal: true
  sequential: true
  contextual: true
  success: true
  failure: true

aloe_integration:
  feed_patterns: true
  pattern_weight: 0.8
```

## Storage

```
memory/pattern_extractor/
├── patterns/
│   ├── temporal_patterns.json
│   ├── sequential_patterns.json
│   ├── contextual_patterns.json
│   ├── success_patterns.json
│   └── failure_patterns.json
├── raw_data/
│   └── events.jsonl
├── models/
│   └── pattern_models.pkl
└── config.yaml
```

## Commands

| Command | Action |
|---------|--------|
| "Extract patterns" | Mine all pattern types |
| "Show my patterns" | Display discovered patterns |
| "What patterns lead to success?" | Success pattern analysis |
| "Pattern for this context" | Get contextual patterns |
| "Validate patterns" | Check pattern quality |
| "Export patterns" | Export for analysis |

## Integration

### With ALOE
```python
# Feed patterns to ALOE
for pattern in patterns:
    aloe.learn_pattern(
        pattern_type=pattern.type,
        pattern=pattern.data,
        confidence=pattern.confidence
    )
```

### With Predictive Engine
```python
# Use patterns for predictions
patterns = pattern_extractor.get_patterns_for_context(context)
predictions = predictive_engine.predict_from_patterns(patterns)
```

### With Suggestion Engine
```python
# Use patterns for suggestions
patterns = pattern_extractor.get_patterns_for_context(context)
suggestions = suggestion_engine.suggest_from_patterns(patterns)
```

---

**The Pattern Extractor: Find what works, repeat what works.** 🔍
