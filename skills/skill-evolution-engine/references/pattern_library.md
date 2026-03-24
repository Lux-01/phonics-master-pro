# SEE Pattern Library

## Common Improvement Patterns

### Pattern 1: Tool Parallelization

**When:** Skill makes multiple independent tool calls sequentially
**Detection:**
```python
tool_calls = [
    "fetch_jupiter(token)",
    "fetch_birdeye(token)",
    "fetch_dexscreener(token)"
]
if not_parallel(tool_calls):
    suggest("Use asyncio.gather for parallel execution")
```

**Implementation:**
```python
# Before
jupiter = fetch_jupiter(token)
birdeye = fetch_birdeye(token)
dex = fetch_dexscreener(token)

# After
jupiter, birdeye, dex = await asyncio.gather(
    fetch_jupiter(token),
    fetch_birdeye(token),
    fetch_dexscreener(token)
)
```

**Expected Improvement:** 2-3x faster execution

---

### Pattern 2: Caching Implementation

**When:** Same API calls repeated within short timeframe
**Detection:**
```python
if repeated_call_within(minutes=5) and data_not_volatile:
    suggest("Implement result caching")
```

**Implementation:**
```python
cache = TTLCache(maxsize=100, ttl=300)

@cache_result(ttl=300)
def fetch_token_data(token):
    return api.get(f"/token/{token}")
```

**Expected Improvement:** 50-80% fewer API calls

---

### Pattern 3: Error Handling Gaps

**When:** Tool calls without try/catch
**Detection:**
```python
if tool_call.has_no_error_handling():
    suggest("Add try/except with fallback logic")
```

**Implementation:**
```python
# Before
result = api.fetch_data()

# After
try:
    result = api.fetch_data()
except APIError as e:
    logger.error(f"API failed: {e}")
    result = try_fallback()
except TimeoutError:
    result = cached_value()
finally:
    track_metrics()
```

---

### Pattern 4: Schema Validation

**When:** Inputs not validated before processing
**Detection:**
```python
if skill_has_parameters() and no_validation():
    suggest("Add input validation")
```

**Implementation:**
```python
from pydantic import BaseModel, validator

class TokenInput(BaseModel):
    address: str
    
    @validator('address')
    def validate_address(cls, v):
        if not v.startswith('0x') and len(v) != 44:
            raise ValueError('Invalid Solana address')
        return v
```

---

### Pattern 5: Workflow Decomposition

**When:** Single skill doing too much
**Detection:**
```python
if skill_step_count() > 10 or skill_duration() > 60:
    suggest("Decompose into sub-skills or steps")
```

**Implementation:**
```python
# Before: One giant skill
def comprehensive_analysis():
    fetch_data()
    analyze_data()
    generate_report()
    send_notification()
    update_database()

# After: Composable steps
workflow = [
    fetch_data(),
    analyze_data(),
    generate_report(),
    send_notification(),
    update_database()
]
```

---

### Pattern 6: Redundancy Removal

**When:** Same logic repeated across skills
**Detection:**
```python
duplicated_functions = find_similar_code(across_skills, similarity_threshold=0.8)
if duplicated_functions:
    suggest("Extract to shared utility")
```

**Implementation:**
```python
# Extract to utils/token_formatting.py
utils/
├── token_formatting.py  # Shared
├── risk_calculator.py
└── price_fetcher.py
```

---

## New Skill Detection Patterns

### Pattern A: Frequent Similar Tasks

**Detection:**
```python
if task_frequency > 3 and task_duration > 10:
    suggest_new_skill(f"""
        Detected pattern: {task_name}
        Frequency: {count} times this week
        Time per execution: {duration} min
        
        Proposed skill: {skill_name}
        Expected savings: {count * duration} min/week
    """)
```

**Example:**
- "Formatting token data" requested 8 times
- Time saved: ~45 min/week
- New skill: token-formatter

---

### Pattern B: Unsupported Domain

**Detection:**
```python
if user_request_matches(skill_keywords) and not_covered_by_existing_skills():
    suggest_new_skill("Domain gap detected")
```

**Example:**
- User repeatedly asks about "NFT floor tracking"
- No existing skill covers this
- New skill: nft-floor-tracker

---

### Pattern C: Tool Gap

**Detection:**
```python
new_tool = detect_new_tool_availability()
if new_tool and no_skill_uses_it() and high_relevance():
    suggest_new_skill(f"""
        New {new_tool.name} available
        No existing integration
        High relevance to your workflow
        
        Proposed skill: {new_tool.name}-integration
    """)
```

---

## Income Opportunity Patterns

### Pattern I1: High-Engagement Content

**Detection:**
```python
content_perf = analyze_content_performance()
if content_perf.engagement_rate > 0.15 and not_monetized():
    suggest_income_opportunity({
        "type": "subscription",
        "name": f"{content_type}_premium",
        "rationale": "High engagement, not monetized",
        "projected_revenue": content_perf.followers * 0.02 * 29
    })
```

---

### Pattern I2: Automation → Product

**Detection:**
```python
automation = find_well_performing_automation()
if automation.usage > 10 and generalizable():
    suggest_income_opportunity({
        "type": "digital_product",
        "name": automation.name + "_toolkit",
        "rationale": "Working automation others would buy",
        "market": "people with similar needs"
    })
```

---

### Pattern I3: Service Scaling

**Detection:**
```python
service = analyze_service_performance()
if service.demand > capacity and bottlenecks:
    suggest_income_opportunity({
        "type": "service_optimization",
        "strategy": "automation_or_raising_prices",
        "impact": "can serve 3x more clients"
    })
```

---

## Refactor Patterns

### Pattern R1: Clarify Intent

**Before:**
```
Do the thing with the stuff.
```

**After:**
```
Fetch token metadata from Jupiter API.
Inputs: token_address (str)
Outputs: {symbol, decimals, name, supply}
Errors: Raises if token not found
```

---

### Pattern R2: Add Examples

**Before:**
```
Use this skill by calling it.
```

**After:**
```
Example:
""")
user: "Analyze SOL"
→ Tool: ats.analyze("SOL")
→ Returns: {score: 85, thesis: "...", entry: "145"}
""
```

---

### Pattern R3: Standardize Terminology

**Before:**
- "token" in one place
- "coin" in another
- "asset" in a third

**After:**
- Standard: "token" everywhere
- Document: "Token means any ERC-20 or SPL token"

---

## Business Model Patterns

### Pattern B1: Product Ladder

**Detect:** User buys entry-level product
**Suggest:** Create premium tier

```
Current: Avatar pack ($3)
Proposed: Pro bundle ($20), Agency pack ($100)
```

---

### Pattern B2: Subscription Pivot

**Detect:** One-time purchases, high repeat customers
**Suggest:** Subscription model

```
Current: Report for $49 (one-time)
Proposed: Report weekly for $29/month
Value: Higher LTV, predictable revenue
```

---

### Pattern B3: Complementary Services

**Detect:** Skill creates asset X
**Suggest:** Add service Y that uses X

```
Current: Creates trading strategy
Proposed: "I can execute this for you" service
```

---

## Performance Optimization Patterns

### Pattern P1: Batch Operations

**When:** Processing items one by one
**Optimize:** Batch process

```python
# Before
for item in items:
    process(item)

# After
chunks = [items[i:i+10] for i in range(0, len(items), 10)]
for chunk in chunks:
    process_batch(chunk)
```

---

### Pattern P2: Async Where Possible

**When:** I/O bound operations
**Optimize:** Make async

```python
# Before (blocking)
data = fetch_api()  # waits 2 seconds

# After (non-blocking)
task = asyncio.create_task(fetch_api())
# ... do other work ...
data = await task
```

---

### Pattern P3: Lazy Loading

**When:** Loading everything upfront
**Optimize:** Load on demand

```python
class SkillData:
    @property
    def heavy_calculation(self):
        if not hasattr(self, '_cached'):
            self._cached = expensive_operation()
        return self._cached
```

---

## ALOE Integration Patterns

### Pattern L1: Success Attribution

```python
def track_success(skill, outcome):
    """What made this skill succeed?"""
    success_factors = {
        "clear_inputs": has_clear_inputs(skill),
        "error_handling": has_error_handling(skill),
        "examples": has_examples(skill),
        "documentation": has_full_docs(skill)
    }
    ALOE.record_pattern("skill_success_factors", success_factors)
```

### Pattern L2: Failure Analysis

```python
def analyze_failure(skill, error):
    """Why did this skill fail?"""
    failure_patterns = {
        "ambiguous_outputs": check_ambiguity(skill),
        "missing_validation": check_validation_gaps(skill),
        "tool_errors": analyze_tool_errors(error)
    }
    ALOE.record_pattern("skill_failure_reasons", failure_patterns)
```

---

## Evolution Cycle Patterns

### Monthly Review Cycle

```
Week 1: Full skill audit
├─ Health scores for all skills
├─ Performance metrics
└─ Gap identification

Week 2: Generate proposals
├─ Improvement suggestions
├─ New skill designs
└─ Income opportunities

Week 3: User review
├─ Present proposals
├─ Get feedback
└─ Prioritize approved

Week 4: Implement
├─ Execute approved changes
├─ Measure outcomes
└─ Update tracking
```

---

These patterns are the building blocks SEE uses to evolve the entire system.
