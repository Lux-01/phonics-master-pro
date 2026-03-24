---
name: ai-learning-system
tier: 1
type: core-integration
status: active
---

# AI Learning System

**Integrated learning module connecting memory, decisions, and outcomes.**

This skill creates a unified learning pipeline that connects:
- **Memory Manager**: Auto-tagging and organization
- **Decision Log**: Decision tracking with rationale
- **Outcome Tracker**: Success/failure measurement
- **ALOE**: Pattern learning and adaptation

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI LEARNING SYSTEM                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   MEMORY     │  │   DECISION   │  │   OUTCOME    │  │
│  │   MANAGER    │◄─┤     LOG      │◄─┤   TRACKER    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
│         └─────────────────┼─────────────────┘          │
│                           │                             │
│                  ┌────────▼────────┐                     │
│                  │  PATTERN        │                     │
│                  │  EXTRACTOR    │                     │
│                  └────────┬────────┘                     │
│                           │                             │
│                  ┌────────▼────────┐                     │
│                  │     ALOE       │                     │
│                  │   INTEGRATION  │                     │
│                  └─────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## Capabilities

### 1. Decision-Outcome Integration

Log decisions with expected outcomes and track actual results:

```python
from ai_learning_system import AILearningSystem

ai = AILearningSystem()

# Log decision with expected outcome
decision_id = ai.log_decision_with_outcome(
    decision="Enter SOL long position",
    rationale="Bullish divergence on 4h timeframe",
    expected_outcome="5-10% profit",
    context="SOL/USDC, $150 entry",
    tags=["trading", "solana"]
)

# Later, record actual outcome
ai.record_decision_outcome(
    decision_id=decision_id,
    actual_outcome="success",
    impact_score=4,  # -5 to +5
    notes="Hit 8% profit target, exited successfully"
)
```

### 2. Contextual Decision Support

Get suggestions based on similar past decisions:

```python
# Get relevant past decisions
similar = ai.get_contextual_decisions("trading strategy", limit=10)

# Get AI-powered suggestions
suggestions = ai.suggest_based_on_history("Should I enter this trade?")
```

### 3. Pattern Extraction

Automatically extract patterns from decision-outcome pairs:

```python
# Extract all patterns
patterns = ai.extract_all_patterns()

# Patterns include:
# - Success patterns (what works)
# - Failure patterns (what to avoid)
# - Decision categories
# - Optimal timing
```

### 4. ALOE Integration

Feed learning data to ALOE for continuous improvement:

```python
# Sync with ALOE
ai.sync_with_aloe()

# All patterns, insights, and outcomes are fed to ALOE
# for pattern recognition and learning
```

### 5. Insight Generation

Generate actionable insights from tracked data:

```python
# Generate insights
insights = ai.generate_insights()

# Get recommendations
recommendations = ai.generate_recommendations()
```

## Commands

### Command Line

```bash
# Generate comprehensive report
python3 ai_learning_system.py --mode report

# Sync with ALOE
python3 ai_learning_system.py --mode sync

# Generate insights
python3 ai_learning_system.py --mode insights

# Extract patterns
python3 ai_learning_system.py --mode patterns

# Run tests
python3 ai_learning_system.py --mode test
```

### Natural Language

| Command | Action |
|---------|--------|
| "Log this decision" | Start tracking a decision |
| "Record outcome" | Record decision outcome |
| "Show learning report" | Display AI learning report |
| "Sync with ALOE" | Feed patterns to ALOE |
| "Generate insights" | Create insights from data |
| "What would you suggest?" | Get contextual suggestions |

## Storage Structure

```
memory/ai_learning/
├── learned_patterns.json      # Extracted patterns
├── insights.json              # Generated insights
├── aloe_feed_log.json         # ALOE integration log
├── aloe_sync.json            # ALOE sync data
├── outcome_expectations.json  # Pending outcomes
└── outcomes/
    ├── 2026-03.json          # Monthly outcome records
    └── 2026-04.json
```

## Integration Points

### With Memory Manager
- Auto-index decisions in memory
- Tag decisions with relevant categories
- Surface related memories during decision-making

### With Decision Log
- Log decisions with AI learning metadata
- Track expected vs actual outcomes
- Calculate decision success rates

### With Outcome Tracker
- Record task outcomes
- Measure impact scores
- Extract success/failure patterns

### With ALOE
- Feed patterns for learning
- Sync insights and recommendations
- Enable continuous improvement

## Metrics Tracked

- **Decision Success Rate**: % of decisions with positive outcomes
- **Pattern Recognition**: Number of patterns learned
- **Memory Integration**: Files indexed and tagged
- **ALOE Sync**: Data fed to learning system
- **Insight Generation**: Actionable insights created

## Example Workflow

```python
# Initialize
ai = AILearningSystem()

# 1. Log a decision
decision_id = ai.log_decision_with_outcome(
    decision="Implement new trading strategy",
    rationale="Backtested with 85% win rate",
    expected_outcome="Increased profitability",
    tags=["trading", "strategy"]
)

# 2. Execute the decision
# ... do the work ...

# 3. Record outcome
ai.record_decision_outcome(
    decision_id=decision_id,
    actual_outcome="success",
    impact_score=5,
    notes="Strategy exceeded expectations"
)

# 4. Generate insights
insights = ai.generate_insights()

# 5. Sync with ALOE
ai.sync_with_aloe()

# 6. Get report
print(ai.generate_report())
```

## Benefits

1. **Continuous Learning**: Every decision and outcome feeds learning
2. **Pattern Recognition**: Automatically identify what works
3. **Contextual Support**: Get suggestions based on history
4. **Measurable Impact**: Track success rates over time
5. **ALOE Integration**: Feed data to adaptive learning system

## Configuration

```yaml
# ai_learning_config.yaml

learning:
  auto_track_decisions: true
  auto_extract_patterns: true
  sync_with_aloe: true
  sync_interval: 3600  # 1 hour

patterns:
  min_confidence: 0.7
  max_patterns: 1000
  retention_days: 365

insights:
  generate_daily: true
  max_insights: 100
  min_data_points: 10

aloe:
  batch_size: 50
  flush_interval: 300  # 5 minutes
```

---

**The AI Learning System: Learn from every decision.** 🧠📊
