---
name: knowledge-graph-engine
description: Build a map of everything known. Organize concepts, entities, relationships, timelines, narratives, and dependencies. Enables deep reasoning, cross-domain insights, pattern detection, and memory-based inference.
---

# Knowledge Graph Engine (KGE)

Build a structured map of knowledge. Not just text - a web of connected understanding.

## Philosophy

**OpenClaw builds a map of everything it knows.**

Raw text is flat. Knowledge graphs are connected. Reason across domains. See patterns.

## Knowledge Organization

### Entities (Nodes)

Everything is an entity:
```
Projects
├── Crypto Scanner v5.5
├── Avatar 3D Integration
└── Skylar Trading Bot

People
├── Tem (user)
└── Lux (assistant)

Technologies
├── Solana
├── Jupiter Aggregator
├── Python
└── Three.js

Concepts
├── Mean Reversion
├── NFT
├── Microcap
└── Narrative

Tokens
├── SOL
├── BONK
├── JUP
└── USDC
```

### Relationships (Edges)

Entities connect through relationships:
```
Crypto Scanner v5.5 ──uses──> Solana
                   ──implements──> Mean Reversion
                   ──created_by──> Tem & Lux
                   ──version──> v5.5
                   
Solana ──has──> Jupiter Aggregator
       ──is_a──> Blockchain
       ──has_token──> SOL

Tem ──owns──> Crypto Scanner v5.5
    ──located_in──> Sydney
    ──interests──> [Trading, AI, Crypto]
```

### Properties (Attributes)

Entities have properties:
```
Crypto Scanner v5.5:
  - created_date: 2026-02-18
  - status: active
  - language: python
  - score_max: 30
  - components: [charts, fundamentals]
  
SOL:
  - current_price: $145.23
  - market_cap: $67B
  - 24h_volume: $2.3B
  - category: layer1
```

## Graph Structure

```
memory/kge/
├── entities.json        # All nodes
├── relationships.json   # All edges
├── properties.json      # All attributes
├── queries/            # Saved queries
└── visualizations/     # Graph renders
```

### Entity Schema
```json
{
  "id": "ENT-001",
  "type": "project",
  "name": "Crypto Scanner v5.5",
  "aliases": ["scanner", "v5.5"],
  "properties": {
    "created": "2026-02-18",
    "status": "active",
    "language": "python"
  },
  "tags": ["trading", "solana", "automation"],
  "sources": [
    {"file": "MEMORY.md", "line": 45},
    {"file": "v55_chart_analyzer.py", "line": 1}
  ]
}
```

### Relationship Schema
```json
{
  "id": "REL-001",
  "type": "uses",
  "from": "ENT-001",
  "to": "ENT-002",
  "properties": {
    "strength": "strong",
    "since": "2026-02-18"
  }
}
```

## Query Language

### Natural Language Queries

```
"What projects use Solana?"
→ MATCH (p:project)-[:uses]->(t:technology {name: "Solana"})
→ RETURN p.name, p.status

"Show me all trading-related tokens"
→ MATCH (t:token)
→ WHERE t.category contains "trading"
→ RETURN t.name, t.price

"What's connected to the avatar project?"
→ MATCH (p {name: "Avatar 3D"})-[]-(x)
→ RETURN x.type, x.name

"Find all skills created this week"
→ MATCH (s:skill)
→ WHERE s.created > "2026-03-01"
→ RETURN s.name, s.purpose
```

### Query Examples

**Cross-Domain Insight:**
```
"Which trading strategies use both RSI and narrative detection?"

MATCH (s)-[:implements]->(c:concept {name: "RSI"}),
      (s)-[:implements]->(c2:concept {name: "Narrative Detection"})
RETURN s.name
```

**Temporal Reasoning:**
```
"What projects evolved from earlier versions?"

MATCH (v2)-[:version_after]->(v1)
WHERE v2.created > v1.created
RETURN v1.name, v2.name, v2.created
```

**Dependency Analysis:**
```
"If I change Jupiter API, what breaks?"

MATCH (j:technology {name: "Jupiter"})
      <-[:depends_on]-(x)
RETURN x.name, x.type
```

## Inference Engine

### Pattern Detection

KGE finds patterns:
```
Pattern: Projects with high ALOE usage tend to:
- Iterate faster
- Have more test coverage
- Produce better outcomes

Pattern: Trading strategies that combine:
- Technical indicators
- Sentiment analysis
- Risk scoring
→ Higher success rates
```

### Predictive Reasoning

```
"Skylar v2.0 uses mean reversion + trend filter"
→ Similar projects: Crypto Scanner, Alpha Hunter
→ Pattern: These succeed with similar architecture
→ Inference: Skylar likely to succeed
```

### Anomaly Detection

```
"Token X has unusual pattern"
→ No similar projects in graph
→ No precedented outcome
→ Flag as novel/experimental
```

## Visualization

### Graph Views

Text representation:
```
Crypto Scanner v5.5
├─ uses ─> Solana
├─ implements ─> Mean Reversion
├─ implements ─> Pattern Recognition
├─ created_by ─> Tem
└─ version 5.5
   └─ version_after ─> v5.4

Solana
├─ has ─> Jupiter Aggregator
├─ has ─> Birdeye API
├─ has_token ─> SOL
└─ is_a ─> Blockchain

Jupiter Aggregator
├─ provides ─> Swaps
├─ provides ─> Prices
└─ used_by ─> [Crypto Scanner, Skylar Bot]
```

### Query Results

```
Query: "Projects using both Jupiter and Birdeye"

Results:
1. Crypto Scanner v5.5
   ├─ uses: Jupiter (prices)
   ├─ uses: Birdeye (OHLCV)
   └─ confidence: High experience

2. Skylar Trading Bot
   ├─ uses: Jupiter (execution)
   ├─ uses: Birdeye (data)
   └─ confidence: High experience
```

## Integration

### With MEMORY.md
```markdown
## Crypto Scanner (auto-linked by KGE)
- Entity ID: ENT-001
- Type: project
- Tags: [solana, trading, v5.5]
- Related: [Skylar Bot, Alpha Hunter]
```

### With Daily Logs
```
2026-03-08
- Worked on [Avatar 3D Project]
  └─ KGE auto-links to: WebGL, Three.js, Mixamo
  └─ Suggests: Similar projects, related skills
```

### With Skills
```
When using "autonomous-agent" skill:
- KGE suggests: Previous similar tasks
- KGE provides: Related entities
- KGE infers: Best approach
```

## Knowledge Types

### Explicit Knowledge
Directly stated facts:
```
"Crypto Scanner v5.5 was created on 2026-02-18"
→ Entity: Crypto Scanner v5.5
→ Property: created = 2026-02-18
```

### Implicit Knowledge
Inferred from relationships:
```
"Crypto Scanner uses Jupiter API"
"Jupiter API uses Solana"
→ Inference: Crypto Scanner depends on Solana
```

### Tacit Knowledge
User preferences learned:
```
"User prefers concise output"
→ Entity: Tem
→ Property: output_preference = "concise"
```

## Queries for Reasoning

### Reasoning Queries

**"What's missing in this plan?"**
```
Analyze plan graph
→ Check for:
  - Missing skill requirements
  - Unsatisfied dependencies
  - Risk factors
  - Similar failed projects
→ Return: Recommendations
```

**"Why did this succeed?"**
```
Analyze success project
→ Find:
  - Success factors
  - Patterns from similar successes
  - Critical components
  - What made the difference
→ Return: Success analysis
```

**"What should I worry about?"**
```
Analyze current project
→ Find:
  - Historical failures in this domain
  - Risky dependencies
  - Untested approaches
  - Novel components without precedent
→ Return: Risk assessment
```

## Storage

```
memory/kge/
├── entities/
│   ├── projects.json
│   ├── people.json
│   ├── technologies.json
│   ├── concepts.json
│   └── tokens.json
├── relationships/
│   ├── uses.json
│   ├── implements.json
│   ├── created_by.json
│   └── version_after.json
├── properties/
│   └── all_properties.json
├── indices/
│   ├── by_type.json
│   ├── by_tag.json
│   └── by_date.json
├── queries/
│   └── saved_queries.json
└── inferences/
    └── generated_insights.json
```

## Commands

| Command | Action |
|---------|--------|
| "Map what we know" | Build/refresh graph |
| "What's related to X?" | Find connections |
| "Similar projects?" | Pattern matching |
| "Why did this work?" | Success analysis |
| "What could go wrong?" | Risk inference |
| "Show the graph" | Visualize |
| "Connect X and Y" | Add relationship |
| "Query: [cypher]" | Direct query |

## ALOE Integration

KGE feeds ALOE patterns:
```
Pattern: "Projects with mix of [RSI + Sentiment] succeed"
Source: KGE query across all projects
ALOE learns: Prioritize mixed strategies
```

Every query teaches:
- What patterns work
- What connections matter
- What paths lead to success

## Continuous Growth

KGE grows as OpenClaw works:
```
New skill created → Add entity
Project completed → Update status
New relationship learned → Add edge
Pattern detected → ALOE learns
```

## Benefits

| Benefit | How KGE Helps |
|---------|---------------|
| Memory | Structured instead of flat text |
| Reasoning | Inference across domains |
| Efficiency | Reuse proven patterns |
| Insight | See hidden connections |
| Prediction | Learn from precedents |
| Risk | Early warning from history |
