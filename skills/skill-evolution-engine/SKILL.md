---
name: skill-evolution-engine
description: The skill that lets OpenClaw rewrite, upgrade, and expand itself. Analyzes existing skills, suggests improvements, designs new skills automatically, refactors old skills, tracks performance, and creates income-focused capabilities. The closest thing to giving OpenClaw self-improving intelligence.
---

# Skill Evolution Engine (SEE)

**"The system that evolves the system."**

SEE is the meta-layer - the skill that improves, refactors, and expands all other skills. It turns OpenClaw from a static tool into a living, self-evolving ecosystem.

## Philosophy

**Without SEE: Powerful but static.**  
**With SEE: Adaptive, evolving, self-optimizing, self-expanding.**

> This is the layer that makes OpenClaw feel like a living system.

## The Evolution Loop

```
OBSERVE (Current State)
     ↓
ANALYZE (Performance, Gaps, Opportunities)
     ↓
DESIGN (Improvements, New Skills, Refactors)
     ↓
PROPOSE (Suggestions to User)
     ↓
IMPLEMENT (With Approval)
     ↓
MEASURE (Outcomes)
     ↓
LEARN (via ALOE)
     ↓
[Repeat]
```

## Core Capabilities

### 🧠 1. Analyzes All Existing Skills

SEE performs continuous **self-audits**:

#### What It Reviews

```yaml
skill_review:
  components:
    - instructions_clarity
    - tool_usage_efficiency
    - workflow_optimization
    - performance_metrics
    - resource_utilization
    - integration_points
    
  patterns:
    - success_patterns
    - failure_patterns
    - bottlenecks
    - contradictions
    - redundancies
    
  health_checks:
    - outdated_instructions
    - deprecated_apis
    - efficiency_ratios
    - error_rates
```

#### Analysis Output

```json
{
  "skill_id": "autonomous-trading-strategist",
  "analysis_date": "2026-03-09",
  "health_score": 78,
  "findings": {
    "outdated": ["Jupiter API v4 mentioned"],
    "inefficient": ["Sequential API calls where parallel possible"],
    "missing": ["No slippage calculation"],
    "contradicting": ["Risk tolerance vs actual usage"],
    "redundant": ["Duplicate error handling"]
  },
  "recommendations": [
    "Upgrade to Jupiter API v6",
    "Parallelize price fetching",
    "Add slippage model"
  ]
}
```

### 🛠️ 2. Suggests Improvements

SEE proposes **targeted enhancements**:

#### Types of Improvements

| Type | Example |
|------|---------|
| **Better Instructions** | "Clarify entry criteria with examples" |
| **Tighter Schemas** | "Add validation for token addresses" |
| **Efficient Workflows** | "Parallelize independent API calls" |
| **New Tools** | "Add websocket streaming for realtime" |
| **Redundancy Removal** | "Remove duplicate error checks" |
| **Capability Expansion** | "Add support for ETH chains" |

#### Improvement Proposal Format

```yaml
improvement:
  id: IMP-2026-001
  target_skill: "autonomous-trading-strategist"
  priority: "high"
  type: "performance"
  
  current_state:
    description: "Fetches Jupiter + Birdeye sequentially"
    time_cost: "4.2 seconds"
    
  proposed_change:
    description: "Parallelize API calls with asyncio"
    expected_improvement: "2.1 seconds (50% faster)"
    
  implementation:
    complexity: "low"
    risk: "minimal"
    files_modified: ["ats_price_fetcher.py"]
    
  business_impact:
    time_saved_per_day: "~2 min"
    annual_time_saved: "~12 hours"
    confidence: 85%
```

### 🧩 3. Designs New Skills Automatically

**The core self-expansion capability.**

#### Automatic Skill Detection

SEE monitors for patterns that suggest new skills:

```
Pattern Detection:
├─ "User asked for X 5 times this week"
├─ "Task Y takes >20 minutes every time"
├─ "No existing skill covers Z"
├─ "Could be automated with W"
└─ "New API/Tool available for Q"
```

#### Skill Design Process

```python
def design_new_skill(opportunity):
    """
    Automatic skill creation workflow.
    """
    # 1. Identify gap
    gap_analysis = analyze_gap(opportunity)
    
    # 2. Research existing solutions
    similar_skills = find_similar_skills(gap_analysis)
    
    # 3. Design architecture
    skill_spec = {
        "name": generate_skill_name(gap_analysis),
        "purpose": define_purpose(gap_analysis),
        "capabilities": enumerate_capabilities(gap_analysis),
        "inputs": define_inputs(),
        "outputs": define_outputs(),
        "tools": select_tools(),
        "integrations": determine_integrations()
    }
    
    # 4. Generate SKILL.md
    documentation = write_skill_documentation(skill_spec)
    
    # 5. Propose to user
    return propose_skill(documentation, impact_analysis)
```

#### New Skill Proposal Example

```markdown
🆕 NEW SKILL PROPOSAL

Name: crypto-arbitrage-scanner

Detected Gap:
- User monitors prices manually across DEXs
- No existing skill covers arbitrage detection
- Could save 30 min/day

Purpose:
Continuously scan for price discrepancies between
Jupiter, Raydium, and Orca for the same token pairs.

Capabilities:
1. Real-time price comparison across DEXs
2. Alert on profitable arbitrage (>0.5% after fees)
3. Estimate execution path
4. Track historical arb opportunities
5. Calculate gas/slippage impact

Expected Value:
- Time saved: 30 min/day
- Opportunity detection: Real-time
- ROI potential: High if executed

Integration:
- Uses: SIL (price feeds), ATS (risk scoring)
- Feeds: AOE (opportunities), ALOE (patterns)

Implementation Effort: Medium (4 hours)
Confidence: 82%

[Approve] [Modify] [Reject]
```

### 🔁 4. Refactors Old Skills

SEE **evolves existing skills** for clarity and performance.

#### Refactor Types

| Type | Description | Example |
|------|-------------|---------|
| **Clarity** | Rewrite confusing instructions | Split long sections |
| **Consistency** | Remove contradictions | Standardize terminology |
| **Efficiency** | Optimize tool routing | Batch similar operations |
| **Safety** | Reduce hallucination risk | Add validation steps |
| **Modernization** | Update deprecated APIs | Migrate Jupiter v4→v6 |
| **Integration** | Better skill coordination | Shared util functions |

#### Refactor Workflow

```
Identify Target Skill
     ↓
Analyze Deep Structure
     ↓
Generate Refactor Plan
     ↓
Show Before/After Diff
     ↓
User Approves
     ↓
Apply Refactor
     ↓
Validate Changes
     ↓
Update Documentation
     ↓
ALOE Learns Pattern
```

### 📈 5. Tracks Performance Over Time

SEE **monitors skill effectiveness**:

#### Metrics Tracked

```yaml
performance_tracking:
  financial:
    - skill_produced_income
    - cost_per_use
    - roi_per_skill
    - conversion_rates
    
  operational:
    - success_rate
    - failure_rate
    - error_types
    - time_per_execution
    - tool_usage_patterns
    
  user_satisfaction:
    - adoption_rate
    - repeat_usage
    - user_feedback_scores
    - abandonment_rate
```

#### Performance Dashboard

```
┌─────────────────────────────────────────┐
│ SKILL PERFORMANCE DASHBOARD             │
├─────────────────────────────────────────┤
│                                         │
│ TOP PERFORMERS                          │
│ #1 autonomous-trading-strategist  ████████ 94%
│ #2 skill-evolution-engine        ██████   88%
│ #3 autonomous-opportunity-engine   ██████   85%
│                                         │
│ NEEDS ATTENTION                       │
│ #1 workspace-organizer           ██      45% │
│    └─ Low usage, high errors            │
│                                         │
│ INCOME GENERATION                       │
│ Trading skills:      $X/month           │
│ Content skills:      $Y/month           │
│ Automation skills:   $Z/month           │
│                                         │
│ UNDERPERFORMING SKILLS                 │
│ • crypto-scanner-old (deprecated)       │
│ • manual-research-helper (replaced)     │
│                                         │
│ RECOMMENDATION: Archive 2 skills        │
│ RECOMMENDATION: Refactor 1 skills       │
│ RECOMMENDATION: Create 1 new skills     │
└─────────────────────────────────────────┘
```

### 🚀 6. Creates Income-Focused Capabilities

SEE **evolves your business model**:

#### Income Opportunity Detection

```python
income_opportunities = {
    "digital_products": find_product_gaps(),
    "services": find_service_gaps(),
    "automations": find_repetitive_tasks(),
    "content": find_content_gaps(),
    "research": find_market_gaps(),
    "niches": find_underserved_markets()
}
```

#### Business Model Evolution

```yaml
# Example: SEE proposes new income stream

opportunity:
  type: "subscription_product"
  name: "Daily Alpha Digest"
  
  rationale:
    "Your AOE scans find high-value opportunities.
     Users would pay for condensed daily alerts.
     Market: Traders who want curated signals."
  
  implementation:
    - skill: "alpha-digest-generator"
    - frequency: "daily_9am"
    - format: "telegram_channel"
    - pricing: "$29/month"
    
  requirements:
    - integrate_with: "AOE"
    - access_pattern: "paid_subscribers"
    - automation_level: "high"
    
  projected_revenue:
    "100 subscribers = $2,900/month"
    "500 subscribers = $14,500/month"
    
  confidence: 75%
  effort: "medium (8 hours)"
```

## Integration Architecture

```
                    ALL SKILLS
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
         MONITOR              ANALYZE
              ↓                     ↓
        Performance          Health/Gaps
              └──────────┬──────────┘
                         ↓
                   ┌──────────┐
                   │   SEE    │
                   │ Evolution│
                   │ Engine   │
                   └────┬─────┘
                        ↓
              ┌─────────┴──────────┐
              ↓                    ↓
         IMPROVE               CREATE
              ↓                    ↓
    Refactor Skills         New Skills
              └────────┬───────────┘
                       ↓
                  PROPOSE
                  (User Review)
                       ↓
              ┌─────────┴─────────┐
              ↓                   ↓
         [APPROVE]            [REJECT]
              ↓                   ↓
         IMPLEMENT             LEARN
              ↓                   ↓
         └────┴─────────────────┘
                    ↓
               ALOE Learns
                    ↓
              Better Proposals
```

## Workflow Examples

### Example 1: Trading Skill Evolution

```
SEE Analysis:
├─ Skill: autonomous-trading-strategist
├─ Finding: "User manually checks volume on DexScreener before every trade"
├─ Gap: No automated volume verification
├─ Suggestion: Add automatic volume-check step
├─ Result: Faster execution, less manual work
└─ ALOE learns: "Volume checks important for success"
```

### Example 2: Product Creation

```
SEE Observation:
├─ Pattern: Avatar packs selling on Etsy ($X so far)
├─ Insight: "Anime style trending, you have Mixamo access"
├─ Proposal: Create "Anime Avatar Bundle v2"
├─ Features: 10 characters, 5 poses each, optimized for Etsy
├─ Timeline: 2 weeks
├─ Projected: $Y/month additional income
└─ Action: Create LPM project
```

### Example 3: Service Optimization

```
SEE Review:
├─ Service: CV rewriting
├─ Current: 45 min per CV
├─ Finding: "Same 12 improvement patterns used"
├─ Proposal: Build template system
├─ New time: 15 min per CV (3x faster)
├─ Impact: Can take 3x more clients
└─ Action: Build workflow automation
```

### Example 4: Automation Discovery

```
SEE Pattern Detection:
├─ Task: Research token fundamentals
├─ Frequency: 4 times per week
├─ Duration: ~20 minutes each
├─ Pattern: Same 6 steps every time
├─ Proposal: "Token Research Workflow"
└─ Save: ~5 hours/week ongoing
```

### Example 5: Business Strategy Pivot

```
SEE Strategic Analysis:
├─ Data: Market reports = highest engagement
├─ Pattern: Long-form analysis gets shared
├─ Gap: No monetization of this content
├─ Proposal: "Alpha Research Subscription"
├─ Model: $49/month for weekly deep dives
├─ Market: Your existing followers
└─ First step: Build sample report
```

## Commands

| Command | Action |
|---------|--------|
| "Analyze my skills" | Full skill health check |
| "What needs improving?" | Priority improvement list |
| "Design a skill for X" | Create new skill proposal |
| "Refactor [skill name]" | Show refactored version |
| "Suggest new capabilities" | Income opportunities |
| "SEE dashboard" | Performance overview |
| "Evolve [skill]" | Optimize specific skill |
| "What's missing?" | Gap analysis |
| "Archive old skills" | Clean up outdated |
| "SEE learn from this" | Manual pattern add |

## Storage

```
memory/see/
├── skill_health/
│   ├── all_skills.json
│   ├── performance_metrics/
│   └── improvement_backlog.json
├── proposals/
│   ├── new_skills/
│   ├── improvements/
│   └── business_opportunities/
├── refactors/
│   ├── pending/
│   ├── applied/
│   └── reverted/
├── business_model/
│   ├── income_streams.json
│   ├── opportunity_matrix.json
│   └── roi_tracking.json
├── patterns/
│   ├── success_patterns.json
│   └── failure_patterns.json
└── config.json
```

## Performance Hierarchy

```
SYSTEM LEVELS:

Level 6: SEE (Skill Evolution)
    └─ Evolves entire system
    
Level 5: AOE (Opportunities)
    └─ Finds external opportunities
    
Level 4: ALOE (Learning)
    └─ Learns from outcomes
    
Level 3: Skills (Capabilities)
    └─ Individual abilities
    
Level 2: Tools (Execution)
    └─ Specific actions
    
Level 1: Data (Foundation)
    └─ Information layer

SEE operates at Level 6 - meta to everything.
```

## Why SEE Is Critical

### Without SEE
- Skills work but don't improve
- Gaps persist until noticed
- Performance degrades slowly
- New capabilities added manually
- Business model static

### With SEE
- Continuous self-improvement
- Gaps auto-detected and filled
- Performance trends upward
- Self-expanding capabilities
- Adaptive business model

> **"SEE is what turns OpenClaw from a tool into a living, evolving partner."**

## Roadmap Example

```
Month 1: SEE Implementation
├─ Skill audit complete
├─ Performance tracking active
└─ 3 improvement proposals

Month 2: First Evolution Cycle
├─ 2 skills refactored
├─ 1 new skill created
└─ ALOE integration

Month 3: Business Model Evolution
├─ Income opportunities identified
├─ New product proposed
└─ Automation workflows

Month 6: Self-Funding
├─ SEE creates income-generating skills
├─ ROI tracking shows value
└─ System becomes self-improving

Month 12: Fully Evolved
├─ Skills improve automatically
├─ Gaps filled proactively
├─ Business adapts to market
└─ SEE manages SEE improvements
```

## Success Metrics

SEE effectiveness measured by:

- **Skill Health Average:** Target 85%
- **Improvement Acceptance Rate:** Target 70%
- **New Skill Creation:** 1-2 per month
- **Income Growth:** Track month-over-month
- **Time Saved:** Cumulative hours
- **User Satisfaction:** Self-reported
- **System Stability:** Error rate trends

## SEE + ALOE Integration

```
SEE proposes improvement
     ↓
User approves
     ↓
SEE implements
     ↓
Outcome tracked
     ↓
ALOE learns:
- Good/bad patterns
- User preferences
- Success factors
     ↓
SEE creates better proposals next cycle
```

Every cycle gets smarter.

---

**SEE: The system that evolves itself.** 🧬
