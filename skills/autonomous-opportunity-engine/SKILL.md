---
name: autonomous-opportunity-engine
description: Continuously scan, evaluate, and act on opportunities across all domains. Crypto, trading, development, content creation - AOE finds opportunities 24/7, scores them, and either alerts you or acts autonomously based on confidence and risk. The proactive arm of the ALOE ecosystem.
---

# Autonomous Opportunity Engine (AOE)

**Always scanning. Always evaluating. Always seeking alpha.**

AOE continuously monitors multiple domains for opportunities, evaluates them using multi-factor scoring, and either alerts you or acts based on pre-configured rules.

## Philosophy

**From reactive to proactive.**

Instead of waiting for you to ask, AOE actively seeks:
- Trading opportunities
- Development opportunities
- Content opportunities
- Learning opportunities
- Connection opportunities

## Core Workflow

```
CONTINUOUS SCAN
     ↓
OPPORTUNITY DETECTED
     ↓
EVALUATE (Multi-Factor Score)
     ↓
DECIDE (Alert / Act / Ignore)
     ↓
EXECUTE or NOTIFY
     ↓
LEARN (via ALOE)
```

## Opportunity Domains

### WebSocket Real-Time Scanner (NEW)

**Real-time opportunity detection via WebSocket connections:**

- **Solana WebSocket**: Live transaction monitoring
- **Helius WebSocket**: Enhanced Solana data feeds
- **Birdeye WebSocket**: Real-time price updates
- **Custom endpoints**: Connect to any WebSocket API

**Example Detection:**
```
🌐 WebSocket Alert: Price Spike Detected
Token: SOL/USDC
Change: +25% (5 minutes)
Volume: 3x average
Score: 88/100 (A)
Urgency: HIGH
Source: Birdeye WebSocket
```

**Usage:**
```python
from aoe_runner import AOERunner

aoe = AOERunner()

# Start WebSocket scanner
aoe.start_websocket_scanner(sources=["solana", "birdeye"])

# Get real-time opportunities
ws_opps = aoe.get_websocket_opportunities(limit=10)

# Stop when done
aoe.stop_websocket_scanner()
```

### 1. Crypto/Trading Opportunities

**What AOE Scans:**
- New token launches
- Sudden volume spikes (+300%)
- Price breakouts on high volume
- Narrative alignment (AI coins pumping while you hold AI16Z)
- Large wallet activity (whale tracking)
- LP additions/removals
- Social sentiment shifts
- Arbitrage opportunities

**Example Detection:**
```
Opportunity: New token launch
CA: EPjFWdd5...
MC: $450K
Volume: $120K (5x avg)
Liquidity: $200K locked
Holders: Growing fast
Narrative: AI Agent
Score: 82/100 (A-)

Action: Alert user immediately
Confidence: 75%
```

### 2. Development Opportunities

**What AOE Scans:**
- New API features
- Library updates with breaking changes
- Deprecated dependencies
- Performance improvements
- Security patches
- New tools that fit your stack

**Example Detection:**
```
Opportunity: Jupiter API v7 released
Breaking: v4/v5 deprecated in 60 days
Benefit: 40% lower latency
Risk: Migration needed
Score: 88/100 (A)

Action: Auto-create migration task in LPM
Confidence: 90%
```

### 3. Content Opportunities

**What AOE Scans:**
- Trending topics in your niche
- Knowledge gaps you can fill
- Repurposing opportunities (blog → video → thread)
- Optimal posting times
- Audience questions needing answers

**Example Detection:**
```
Opportunity: Moltbook trend
Topic: "Agent communication patterns"
Views: Growing 300%/day
Your expertise: High (built MAC skill)
Content gap: No deep dive exists
Score: 85/100 (A)

Action: Generate content outline
Confidence: 80%
```

### 4. Learning Opportunities

**What AOE Scans:**
- Skills gaps in your workflow
- New tech relevant to your projects
- Patterns from successful projects
- Failed approaches to avoid

**Example Detection:**
```
Opportunity: Rust for Solana
Need: Trading bot needs performance
Current: Python (slower)
Benefit: 10x faster execution
Learning curve: Moderate
Score: 78/100 (B+)

Action: Suggest learning path
Confidence: 85%
```

### 5. Social/Network Opportunities

**What AOE Scans:**
- Active conversations you should join
- Questions you can answer
- Potential collaborations
- Relevant mentions
- Engagement opportunities

**Example Detection:**
```
Opportunity: Moltbook thread
Author: @crypto_guru
Topic: "What's the best DEX scanner?"
Your knowledge: Built v5.5
Engagement: High visibility
Score: 80/100 (A-)

Action: Suggest response
Confidence: 85%
```

## Scoring System

Each opportunity scored on 0-100:

### Factors (Configurable Weights)

| Factor | Weight | Description |
|--------|--------|-------------|
| **Potential** | 25% | Upside/reward potential |
| **Probability** | 25% | Likelihood of success |
| **Risk** | -20% | Penalty for risk |
| **Speed** | 15% | How soon must act |
| **Effort** | -10% | Penalty for work required |
| **Fit** | 15% | Alignment with goals |
| **Alpha** | 20% | Information asymmetry |

### Score Interpretation

| Score | Grade | Action |
|-------|-------|--------|
| 90-100 | A+ | High priority - alert immediately |
| 80-89 | A | Strong opportunity - evaluate for auto-action |
| 70-79 | B+ | Good opportunity - add to queue |
| 60-69 | B | Moderate - log for review |
| 50-59 | C+ | Weak - ignore unless specific interest |
| <50 | C/D | Ignore |

## Auto-Action Rules

Configure what AOE does automatically:

### High Confidence (Score ≥85)
```yaml
auto_action:
  crypto_signals:
    score_threshold: 85
    action: alert_immediately
    channel: telegram
    priority: high
    
  new_tokens:
    score_threshold: 82
    action: full_analysis
    - fetch_onchain
    - social_scan
    - risk_score
    - generate_thesis
    - deliver_report
```

### Medium Confidence (Score 70-84)
```yaml
queue_action:
  score_range: [70, 84]
  action: add_to_opportunity_queue
  review_time: daily_9am
  digest_size: top_10
```

### Low Confidence (Score <70)
```yaml
ignore_action:
  score_threshold: 70
  action: log_only
  accessible: via_web_dashboard
```

## Integration with Other Skills

### AOE + SIL (Sensory Input)
```
AOE: "Scan for opportunities"
  ↓
SIL: Fetches real-time data
  - Jupiter prices
  - Birdeye volumes
  - Social feeds
  - On-chain data
  ↓
AOE: Scores opportunities
```

### AOE + ATS (Trading Strategist)
```
AOE: Detects volume spike
  ↓
ATS: Deep analysis
  - Risk scoring
  - Thesis generation
  - Entry/exit logic
  ↓
AOE: Evaluates ATS output
  ↓
Alert/Act based on combined score
```

### AOE + MAC (Multi-Agent Coordination)
```
AOE: Complex opportunity detected
  ↓
MAC: Spawns specialists
  - Research agent
  - Risk agent
  - Analysis agent
  ↓
AOE: Synthesizes outputs
  ↓
Unified recommendation
```

### AOE + LPM (Project Manager)
```
AOE: Finds optimization opportunity
  ↓
LPM: Creates task
  - "Migrate to Jupiter v7"
  - Priority: High
  - Deadline: Auto-calculated
  ↓
LPM: Tracks to completion
```

### AOE + ALOE (Learning)
```
AOE: Acts on opportunity
  ↓
Outcome: Success/Failure
  ↓
ALOE: Learns pattern
  ↓
Future scoring improves
```

### AOE + KGE (Knowledge Graph)
```
AOE: Evaluating opportunity
  ↓
KGE: Queries connections
  - Similar past opportunities
  - Related projects
  - Success patterns
  ↓
AOE: Uses context to refine score
```

## Continuous Scanners

### Scanner 1: Market Pulse
```yaml
frequency: every_5_minutes
targets:
  - dexscreener_new
  - birdeye_volume_leaders
  - jupiter_price_changes
  - pumpfun_launches

detect:
  - volume_spike: "> 300%"
  - price_breakout: "> 20%"
  - new_listing: "< 2 hours old"
  - liquidity_change: "> 50%"
```

### Scanner 2: Social Signal
```yaml
frequency: every_15_minutes
targets:
  - moltbook_feed
  - twitter_crypto
  - discord_alpha_channels

detect:
  - narrative_emerging: "> 10 mentions/hour"
  - sentiment_shift: "> 0.2 delta"
  - influencer_calls: "> 3 per token"
```

### Scanner 3: Whale Watch
```yaml
frequency: every_2_minutes
targets:
  - tracked_wallets:
    - smart_money_whales
    - dev_wallets
    - insider_wallets

detect:
  - buy: "> 1 SOL"
  - multiple_buys: "3+ in 30 min"
  - new_token_position
```

### Scanner 4: Dev Opportunities
```yaml
frequency: daily
targets:
  - github_releases
  - npm_updates
  - docker_hub
  - api_changelogs

detect:
  - major_version: deprecated
  - security_patch: critical
  - performance_gain: "> 20%"
```

### Scanner 5: Content Gaps
```yaml
frequency: every_6_hours
targets:
  - trending_topics
  - unanswered_questions
  - your_content_performance

detect:
  - trending_without_coverage: you
  - high_engagement_questions
  - repurposing_opportunities
```

## Opportunity Queue

### Priority Queue Structure

```
Queue: TOP_OPPORTUNITIES
┌─────────────────────────────────────┐
│ #1 [URGENT] New AI token breakout   │
│    Score: 88 | Action: Analyze now  │
│    Time left: 15 minutes            │
├─────────────────────────────────────┤
│ #2 [HIGH] Jupiter v7 migration        │
│    Score: 85 | Action: Plan task    │
│    Deadline: 30 days                │
├─────────────────────────────────────┤
│ #3 [MED] Moltbook content gap         │
│    Score: 78 | Action: Draft post   │
│    Optimal time: Tomorrow 9am       │
└─────────────────────────────────────┘
```

### Queue Management

```python
class OpportunityQueue:
    def add(self, opportunity):
        scored = self.score(opportunity)
        if scored.priority == "urgent":
            self.alert_immediately(scored)
        elif scored.priority == "high":
            self.queue.insert_priority(scored)
        else:
            self.queue.add(scored)
    
    def process(self):
        top = self.queue.pop_highest()
        if top.score >= AUTO_ACTION_THRESHOLD:
            return self.auto_act(top)
        else:
            return self.request_approval(top)
```

## Alert System

### Alert Channels

| Channel | Use For | Priority |
|---------|---------|----------|
| Telegram (immediate) | Score ≥85 | Urgent |
| Telegram (digest) | Score 70-84 | Daily summary |
| Dashboard | All opportunities | Archive |
| LPM task | Action items | Tracked |

### Alert Format

```markdown
🎯 OPPORTUNITY ALERT
Score: 88/100 (A) | Urgent

TYPE: Crypto Trading
NAME: New AI Token Launch
SYMBOL: $AICO
CA: EPjFWdd5...

DETECTION:
• Launched: 45 min ago
• MC: $420K
• Volume: $150K (6x avg)
• Liquidity: $200K locked
• Holders: 450 (growing fast)

NARRATIVE: AI Agent tokens pumping
FIT: You hold AI16Z (+23% today)

SCORE BREAKDOWN:
✓ Potential +25
✓ Probability +22
✓ Speed +13
✓ Fit +14
✓ Alpha +18
• Risk -14

RECOMMENDED ACTION:
Analyze immediately for entry
Risk: Moderate
Time window: ~15 minutes

[Analyze Now] [Queue] [Dismiss]
```

## Auto-Action Examples

### Example 1: Trading Signal
```
Opportunity: $BONK volume spike
Score: 87 (A)
Confidence: 80%

Auto-Action Triggered:
1. SIL fetches full data
2. ATS runs risk analysis
3. Score: 82 (passes threshold)
4. Thesis generated
5. Alert sent to user
6. LPM creates watch task

User receives:
Complete analysis + recommendation
```

### Example 2: Development Upgrade
```
Opportunity: Critical security patch
Score: 95 (A+)
Confidence: 99%

Auto-Action Triggered:
1. AOE identifies patch
2. Checks if affects your code
3. Verifies vulnerability exists
4. LPM creates urgent task
5. AWB generates migration script
6. Alert sent with fix ready

User receives:
Task created + migration script
```

### Example 3: Content Opportunity
```
Opportunity: Trending topic match
Score: 83 (A)
Confidence: 85%

Auto-Action Triggered:
1. Detects trend
2. Checks your expertise (high)
3. Verifies no existing content
4. AWB generates outline
5. LPM suggests optimal time
6. Alert sent with draft ready

User receives:
Content outline + posting time
```

## Learning Loop

```
AOE detects opportunity → Acts → Outcome → ALOE learns → Future scores improve

Example:
1. AOE finds token at launch
2. Action: Recommend buy
3. Outcome: +150% in 1 hour
4. ALOE learns: Early launch + high volume = success
5. Future similar opportunities get higher score
```

## Configuration

### User Preferences

```yaml
# User config: /memory/aoe/config.yaml

risk_tolerance: aggressive  # conservative/moderate/aggressive

auto_actions:
  crypto_trades: false      # Never auto-trade
  token_alerts: true        # Alert on high scores
  dev_patches: true         # Auto-create tasks
  content: ask_first        # Always ask

scores:
  minimum_alert: 75
  minimum_queue: 60
  auto_action: 85

watchlists:
  tokens: ["BONK", "JUP", "SOL"]
  narratives: ["AI Agents", "DePIN"]
  wallets: ["JBhVoSaX..."]

time:
  digest_time: "09:00"
  active_hours: ["00:00-08:00"]  # Sydney = US market hours
```

## Dashboard

### Real-Time View

```
┌──────────────────────────────────────────┐
│ AOE Dashboard - Live Opportunities       │
├──────────────────────────────────────────┤
│                                           │
│ ACTIVE OPPORTUNITIES (3)                 │
│ 🎯 $AICO    Launch    88  URGENT  12m    │
│ 🎯 Jupiter  Upgrade   85  HIGH    30d    │
│ 🎯 Content  Gap       78  MED     1d     │
│                                           │
│ SCANNERS STATUS                          │
│ ✓ Market Pulse      [Running 5min]       │
│ ✓ Social Signal     [Running 15min]      │
│ ✓ Whale Watch       [Running 2min]       │
│ ✓ Dev Updates       [Next: 4h]           │
│                                           │
│ TODAY'S STATS                            │
│ Opportunities found: 23                  │
│ Alerts sent: 3                           │
│ Auto-actions: 1                          │
│ Queue additions: 8                       │
│                                           │
│ ALOE LEARNING                            │
│ Patterns learned: 15                     │
│ Success rate: 78%                        │
└──────────────────────────────────────────┘
```

## Safety Controls

### Protected Actions
AOE will NOT auto-act on:
- Financial transactions (even with high confidence)
- Code changes to production
- External communications
- Deleting files
- System configuration changes

### Human-in-the-Loop Required
For these, only alert:
- Trading decisions
- Production deployments
- External messages
- Risky operations

### Approval Levels

```yaml
approval_required:
  score_90_plus: true             # Always confirm action
  score_80_89: user_depends       # Based on user preference
  score_70_79: false              # Queue only
  
financial_impact: always_ask
api_cost: auto_if_under_$0.10
```

## Commands

| Command | Action |
|---------|--------|
| "Scan for opportunities" | Manual scan |
| "Show my opportunities" | View queue |
| "AOE status" | Dashboard |
| "Configure AOE" | Update preferences |
| "Priority mode" | Set alert threshold |
| "Quiet mode" | Pause non-urgent alerts |
| "AOE learn from this" | Manual pattern add |

## Storage

```
memory/aoe/
├── opportunities/
│   ├── active_queue.json
│   ├── history/
│   └── dismissed.json
├── scanners/
│   ├── market_scanner.py
│   ├── social_scanner.py
│   ├── whale_scanner.py
│   └── dev_scanner.py
├── evaluators/
│   ├── scoring_engine.py
│   └── risk_assessor.py
├── config.yaml
├── stats.json
└── patterns/
    └── learned_patterns.json
```

## Example Usage

### Scenario 1: Passive Income
```
AOE running 24/7

3:47 AM: New token launches
AOE: Detects → Scores 88 → Analyzes → Alerts user

User wakes up to:
"🎯 URGENT: High-score opportunity detected 4 hours ago
Full analysis ready. Token now +45% from detection."

User: "Evaluate now" or "Dismiss"
```

### Scenario 2: Development
```
AOE running 24/7

Tuesday 11 PM: New Jupiter API released
AOE: Detects → Checks if affects user → Scores 92
→ Creates LPM task → Generates migration script
→ Adds to digest

Next morning:
User sees task: "Migrate to Jupiter v7 (URGENT)"
With: Migration script ready, 30 days to deadline
```

### Scenario 3: Content
```
AOE running 24/7

Thursday afternoon: Topic starts trending
AOE: Detects → Checks your expertise → Scores 81
→ Generates outline → Suggests optimal time
→ Adds to digest

Next day at 9 AM:
Digest shows: "Content opportunity ready - draft available"
```

## Integration Summary

```
                    ┌──────────────┐
                    │    USER      │
                    └──────┬───────┘
                           │
         ┌─────────────────┴──────────────────┐
         ↓                                      ↓
    ┌─────────┐                          ┌──────────┐
    │  Alert  │                          │  Action  │
    └────┬────┘                          └────┬─────┘
         ↓                                      ↓
┌──────────────────────────────────────────────────────┐
│                    AOE - Opportunity Engine           │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐         │
│  │ Scanners │   │ Evaluator│   │ Decider  │         │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘         │
│       ↓              ↓              ↓              │
│  SIL → ATS → MAC → LPM → AWB → KGE → ALOE         │
│       ↑              ↑              ↑              │
│       └──────────────┴──────────────┘              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**AOE: The always-on opportunity seeker.**
