# AOE Scoring Engine

## Scoring Algorithm

The core of AOE is the opportunity scoring engine.

### Formula

```python
score = (
    potential * W_p +
    probability * W_b +
    speed * W_s +
    fit * W_f +
    alpha * W_a -
    risk * W_r -
    effort * W_e
)

# Where W_* are weights from config
# Score is normalized to 0-100
```

### Factor Calculations

#### 1. Potential (0-100)
How big is the upside?

**Trading:**
```python
def calculate_potential_trading(token_data):
    # Based on:
    # - Historical breakouts of similar tokens
    # - Narrative strength
    # - Market cap size (smaller = more room)
    # - Liquidity depth (can you exit?)
    
    mc_multiplier = {
        "<1M": 2.0,
        "1M-10M": 1.5,
        "10M-100M": 1.0,
        ">100M": 0.7
    }
    
    narrative_score = get_narrative_strength(token_data)
    similar_performance = lookup_similar_tokens_average_return(token_data)
    liquidity_factor = min(1.0, liquidity_usd / 1000000)
    
    potential = similar_performance * mc_multiplier * liquidity_factor * (narrative_score / 100)
    return min(100, potential)
```

**Development:**
```python
def calculate_potential_dev(update_data):
    # Based on:
    # - Security risk of not updating
    # - Performance gain
    # - New features enabled
    
    security_score = 0
    if update_data.type == "security_patch":
        security_score = 100
    elif update_data.cve_score:
        security_score = min(100, update_data.cve_score * 10)
    
    perf_score = update_data.performance_gain * 100
    
    potential = max(security_score, perf_score)
    return min(100, potential)
```

#### 2. Probability (0-100)
How likely is success?

```python
def calculate_probability(opportunity, historical_data):
    # Base probability on:
    # - Pattern match with past successes
    # - Market conditions
    # - Quality of signals
    
    base_prob = 50  # Neutral
    
    # Historical pattern matching
    similar_outcomes = find_similar_opportunities(opportunity)
    success_rate = calculate_success_rate(similar_outcomes)
    base_prob += (success_rate - 50) * 0.5
    
    # Signal quality
    if opportunity.signals:
        signal_strength = sum(s.confidence for s in opportunity.signals) / len(opportunity.signals)
        base_prob += signal_strength * 0.3
    
    # Market conditions
    market_score = get_current_market_conditions()
    base_prob += market_score * 0.2
    
    return max(0, min(100, base_prob))
```

#### 3. Risk (0-100, penalty)
What could go wrong?

**Trading Risk:**
```python
def calculate_risk_trading(token_data):
    risk_factors = {
        "contract_risk": assess_contract(token_data.address),
        "liquidity_risk": 100 if liquidity < 50K else 50 if liquidity < 200K else 20,
        "holder_risk": 100 if top_10 > 50 else 50 if top_10 > 35 else 20,
        "narrative_risk": 100 if no_narrative else 50 if fading else 20,
        "rug_risk": detect_rug_signals(token_data)
    }
    
    # Weighted average
    weights = {
        "contract_risk": 0.25,
        "liquidity_risk": 0.20,
        "holder_risk": 0.20,
        "rug_risk": 0.25,
        "narrative_risk": 0.10
    }
    
    risk = sum(risk_factors[k] * weights[k] for k in risk_factors)
    return risk
```

**Development Risk:**
```python
def calculate_risk_dev(update_data):
    # Risk factors:
    # - Breaking changes
    # - Migration complexity
    # - Dependency conflicts
    
    breaking_score = 80 if update_data.breaking else 20
    migration_score = len(update_data.migration_steps) * 10
    test_coverage_score = 100 - (update_data.test_coverage or 0)
    
    risk = (breaking_score + migration_score + test_coverage_score) / 3
    return risk
```

#### 4. Speed (0-100)
How urgent?

```python
def calculate_speed(opportunity):
    # Time-sensitivity
    if opportunity.time_window_minutes < 15:
        return 100  # Extremely urgent
    elif opportunity.time_window_minutes < 60:
        return 80
    elif opportunity.time_window_minutes < 240:
        return 60
    elif opportunity.time_window_hours < 24:
        return 40
    elif opportunity.time_window_days < 7:
        return 20
    else:
        return 10
```

#### 5. Effort (0-100, penalty)
How much work?

```python
def calculate_effort(opportunity):
    # Estimated hours to execution
    if opportunity.effort_hours < 0.5:
        return 10
    elif opportunity.effort_hours < 2:
        return 25
    elif opportunity.effort_hours < 4:
        return 40
    elif opportunity.effort_hours < 8:
        return 60
    elif opportunity.effort_hours < 24:
        return 80
    else:
        return 100
```

#### 6. Fit (0-100)
How aligned with your goals?

```python
def calculate_fit(opportunity, user_profile):
    fit_score = 50  # Neutral
    
    # Interest alignment
    if opportunity.domain in user_profile.interests:
        fit_score += 30
    
    # Expertise match
    if opportunity.required_skills in user_profile.skills:
        fit_score += 20
    
    # Portfolio/context fit
    if opportunity.token in user_profile.holdings:
        fit_score += 10
    
    # Narrative fit
    if opportunity.narrative in user_profile.preferred_narratives:
        fit_score += 15
    
    return min(100, fit_score)
```

#### 7. Alpha (0-100)
Do you have an edge?

```python
def calculate_alpha(opportunity, data_sources):
    alpha_score = 50  # Neutral
    
    # Information asymmetry
    early_detection = opportunity.detection_time_minutes
    if early_detection < 5:
        alpha_score += 40
    elif early_detection < 30:
        alpha_score += 30
    elif early_detection < 120:
        alpha_score += 15
    
    # Unique data sources
    unique_signals = len([s for s in opportunity.signals if s.source_type == "custom"])
    alpha_score += unique_signals * 5
    
    # Your specific advantage
    if opportunity.domain in your_expertise_domains:
        alpha_score += 15
    
    return min(100, alpha_score)
```

## Dynamic Scoring

Scores adjust based on context:

### Time Decay
```python
def apply_time_decay(score, detection_time):
    """Opportunity loses score as time passes."""
    hours_since_detection = (now - detection_time).hours
    decay_factor = max(0.5, 1 - (hours_since_detection * 0.05))
    return score * decay_factor
```

### Market Adjustment
```python
def apply_market_adjustment(score, current_market):
    """Adjust based on overall market conditions."""
    if current_market.sentiment == "bearish":
        score *= 0.9  # Reduce scores in bear
    elif current_market.sentiment == "bullish":
        score *= 1.1  # Boost scores in bull
    return min(100, score)
```

### ALOE Learning Boost
```python
def apply_learning_boost(score, opportunity):
    """Boost scores based on ALOE patterns."""
    patterns = aloe.find_matching_patterns(opportunity)
    if patterns:
        avg_success_rate = mean(p.success_rate for p in patterns)
        boost = (avg_success_rate - 70) * 0.3  # Normalize around 70%
        score += boost
    return max(0, min(100, score))
```

## Score Interpretation

### What Scores Mean

| Score | Confidence | Action |
|-------|------------|--------|
| 90-100 | Very High | Almost certain good opportunity |
| 80-89 | High | Strong opportunity, likely worth action |
| 70-79 | Good | Solid opportunity, evaluate carefully |
| 60-69 | Moderate | Possible opportunity, high scrutiny |
| 50-59 | Low | Weak signal, probably skip |
| <50 | Very Low | Not actionable |

### Score Components (Debug View)

```
Opportunity: $BONK breakout

Score Breakdown:
├─ Potential:    85  × 0.25 = 21.25
├─ Probability:  78  × 0.25 = 19.50
├─ Speed:        70  × 0.15 = 10.50
├─ Fit:          90  × 0.15 = 13.50
├─ Alpha:        65  × 0.20 = 13.00
├─ Risk:        -40  × 0.20 = -8.00
└─ Effort:      -30  × 0.10 = -3.00

Raw Score: 66.75
Bonuses:
├─ ALOE pattern match: +8
└─ Watchlist token: +5

Final Score: 79/100 (B+)

Recommendation: Good opportunity, moderate confidence.
Action: Add to queue for review.
```

## Calibration

### Feedback Loop
```
User acts on opportunity → Outcome
     ↓
AOE learns: Was score accurate?
     ↓
Adjust weights → Better future scores
```

### ALOE Integration
```python
# After opportunity resolves
aloe.record_outcome(
    opportunity=opp_id,
    predicted_score=79,
    actual_outcome="success",
    actual_return=1.45,  # 45% gain
    time_to_outcome_hours=4
)

# ALOE adjusts future scoring for similar opportunities
```
