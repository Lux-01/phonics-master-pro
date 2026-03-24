# ALOE Learning Patterns Guide

## How ALOE Learns

### Observation Phase
Every interaction is observed:
- What action was taken
- What the outcome was
- How long it took
- Any errors encountered

### Pattern Recognition Phase
After observations accumulate:
- Identify repeated patterns
- Correlate actions with outcomes
- Calculate confidence scores
- Extract generalizable rules

### Adaptation Phase
Apply patterns to future tasks:
- Prioritize successful approaches
- Warn about known failures
- Optimize based on efficiency gains
- Respect user preferences

## Learning Types

### 1. Supervised Learning (User Feedback)

```
User: "Do X"
→ Agent does X
→ User: "Good!" or "No, wrong"
→ ALOE learns preference/outcome
```

### 2. Unsupervised Learning (Pattern Discovery)

```
Agent does X 10 times
→ ALOE notices: "Always succeeds with Y condition"
→ Extracts pattern automatically
```

### 3. Reinforcement Learning (Outcome Based)

```
Action → Outcome → Reward
- Success: +1 confidence
- Failure: -1 confidence
- Neutral: 0
```

## Pattern Evolution

### Stage 1: Observation (n < 3)
- Initial observation
- Low confidence
- Tentative pattern

### Stage 2: Emerging (3 <= n < 10)
- Pattern forming
- Medium confidence
- Starting to apply

### Stage 3: Established (n >= 10)
- Proven pattern
- High confidence
- Auto-applied

### Stage 4: Validated (n >= 50)
- Battle-tested
- Very high confidence
- Default behavior

## Confidence Scoring

```python
def calculate_confidence(successes, total):
    """Bayesian confidence calculation."""
    if total == 0:
        return 0.5
    
    # Laplace smoothing
    alpha = 1
    beta = 1
    
    confidence = (successes + alpha) / (total + alpha + beta)
    return confidence
```

## Pattern Prioritization

When multiple patterns apply, rank by:
1. Confidence score (highest first)
2. Recency (newer first)
3. Specificity (most specific first)
4. User preference

## Forgetting Patterns

ALOE forgets patterns when:
- Not used for 90 days
- Confidence drops below 50%
- User explicitly says "forget this"
- Contradicted by new evidence

## Learning from Failures

**Important:** Failures teach as much as successes.

```
action: "Write to production file"
outcome: "failure - permission denied"
learned: 
  - production files need sudo
  - should backup first
  - check permissions before write
```

## Continuous Learning

ALOE improves through:
1. **Volume:** More interactions = more data
2. **Diversity:** Different tasks = robust patterns
3. **Feedback:** User corrections = better alignment
4. **Time:** Long observation = reliable patterns
