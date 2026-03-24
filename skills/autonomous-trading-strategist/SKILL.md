---
name: autonomous-trading-strategist
description: 24/7 crypto research and analysis engine. Market structure, liquidity analysis, volume patterns, narrative mapping, risk scoring, entry/exit logic, thesis generation. Not financial advice - purely analytical.
---

# Autonomous Trading Strategist (ATS)

A full trading analyst that operates 24/7 - scanning, analyzing, and generating actionable intelligence.

## Philosophy

**Turn OpenClaw into a crypto research engine.**

Analyze markets continuously. Generate theses. Track narratives. Score risks. 

## Core Capabilities

### 1. Market Structure Analysis

Understand the market landscape:
```
├─ Token distribution
├─ Holder concentration
├─ Liquidity depth
├─ Trading venues
└─ Market cap tiers
```

### 2. Liquidity Analysis

Assess market health:
- LP pool depth
- Slippage at different sizes
- DEX vs CEX liquidity
- Wash trading detection
- Liquidity concentration

### 3. Volume Pattern Detection

Find unusual activity:
- Volume spikes
- Breakout volume
- Distribution volume
- Accumulation patterns
- Volume divergences

### 4. Narrative Mapping

Track storylines:
- AI coins trending
- Meme narratives
- DeFi innovations
- Gaming/metaverse
- Real world assets (RWA)

### 5. Risk Scoring

Calculate comprehensive risk:
```
Total Risk Score = 
  Contract Risk (30%) +
  Liquidity Risk (25%) +
  Holder Risk (20%) +
  Volume Risk (15%) +
  Narrative Risk (10%)
```

### 6. Entry/Exit Logic

Generate signals:
- Entry conditions
- Exit targets
- Stop losses
- Position sizing
- Time stops

### 7. Thesis Generation

Write complete investment theses:
```markdown
# [Token] Investment Thesis

## Executive Summary
[One paragraph thesis]

## Market Context
[Current market conditions]

## Token Analysis
[Deep dive into metrics]

## Risk Assessment
[Comprehensive risk score]

## Entry Strategy
[How to enter]

## Exit Strategy
[When and how to exit]

## Conclusion
[Final recommendation]
```

### 8. MEV Protection (NEW)

Protect trades from MEV attacks:
- **Sandwich Attack Detection**: Analyze risk before executing
- **Front-running Protection**: Private transaction relays
- **Dynamic Slippage**: Adjust based on risk level
- **Route Splitting**: Break large orders into smaller chunks
- **Mempool Monitoring**: Detect suspicious activity

**Usage:**
```bash
# Analyze MEV risk for a token
python3 ats_runner.py --mode mev-analyze --token BONK --amount 5000

# Generate signal with MEV protection (default)
python3 ats_runner.py --mode signal --token SOL

# Generate signal without MEV protection
python3 ats_runner.py --mode signal --token SOL --no-mev

# View MEV protection report
python3 ats_runner.py --mode mev-report
```

**Example Output:**
```
MEV Risk Analysis for BONK
Risk Level: medium
Risk Score: 45/100
Safe to proceed: True

Risk Factors:
  • Large transaction size attracts MEV bots
  
Recommendations:
  • Set tight slippage tolerance
  • Use priority fees to skip ahead
  • Monitor mempool before executing
```

## Scanner Types

### 1. Token Scanners

**Microcap Scanner**
- Market cap < $1M
- Volume > $10K/day
- LP locked or burned
- Holder count growing
- No major red flags

**Momo Scanner** (Momentum)
- Price up > 10% in 24h
- Volume up > 200%
- Social mentions up
- Fresh narrative
- Early stage

**Value Scanner**
- MC/FDV ratio healthy
- Revenue generating
- Undervalued metrics
- Strong fundamentals
- Sustainable model

### 2. Narrative Detection

Track emerging stories:
```python
NARRATIVES = {
    "AI Agents": ["AI16Z", "ZEREBRO", "GRIFFAIN"],
    "Meme Coins": ["BONK", "WIF", "POPCAT"],
    "DeFi": ["JUP", "RAY", "ORCA"],
    "Gaming": ["PRIME", "BEAM", "ATLAS"]
}

# Detect which narrative is trending
trending = analyze_narrative_momentum(NARRATIVES)
```

### 3. Alert System

Notify on:
- Volume spike > 5x average
- New holder milestone
- Narrative breakout
- Risk score change
- Entry/exit signal trigger

## Analysis Framework

### Step 1: On-Chain Scan
```python
token_data = {
    "mint": address,
    "holders": {
        "count": 1250,
        "top10_pct": 35.4,
        "distribution": "healthy"
    },
    "liquidity": {
        "usd": "$450K",
        "locked": True,
        "dex": "Raydium"
    },
    "transfers": {
        "24h": 3400,
        "buy_sell_ratio": 1.3
    }
}
```

### Step 2: Market Data
```python
market_data = {
    "price": 0.045,
    "mcap": "$450K",
    "volume_24h": "$120K",
    "price_change_24h": "+23%",
    "volume_vs_avg": 3.2
}
```

### Step 3: Social Signals
```python
social_data = {
    "twitter_mentions": 234,
    "sentiment_score": 0.72,
    "trending": True,
    "influencer_calls": 3
}
```

### Step 4: Risk Assessment
```python
risk_scores = {
    "contract_score": 85,       # 0-100, higher = safer
    "liquidity_score": 70,
    "holder_score": 60,
    "narrative_score": 80,
    "overall": 73              # Weighted average
}
```

### Step 5: Thesis Generation
Combine all data into coherent thesis.

## Scoring System

### A+ (90-100)
- Exceptional fundamentals
- Strong narrative
- Deep liquidity
- Low risk

### A (80-89)
- Good fundamentals
- Growing narrative
- Adequate liquidity
- Manageable risk

### B (65-79)
- Decent fundamentals
- Emerging narrative
- Limited liquidity
- Moderate risk

### C (50-64)
- Weak fundamentals
- Fading narrative
- Thin liquidity
- High risk

### D (<50)
- Avoid
- Major red flags
- Likely rug/scam

## Integration with Other Skills

### With MAC
Spawn specialists:
- On-chain analyst agent
- Social sentiment agent
- Market data agent
- Risk analyst agent

### With SIL
Pull data from:
- Jupiter API (prices)
- Birdeye (OHLCV)
- Helius (on-chain)
- Social feeds (sentiment)

### With ALOE
Learn from outcomes:
- Which theses succeeded
- Which patterns predict pumps
- Which risk signals matter
- Optimal timing

## Continuous Operation

### Scanning Loop
```
Every 5 minutes:
1. Scan all microcaps
2. Check new listings
3. Update scores
4. Generate alerts
5. Update theses
```

### Analysis Loop
```
Every hour:
1. Update market structure
2. Re-score all tracked tokens
3. Recalculate risk
4. Update narratives
5. Refresh theses
```

### Reporting Loop
```
Every 4 hours:
1. Top opportunities
2. Trending narratives
3. Risk alerts
4. Thesis updates
5. Market summary
```

## Commands

| Command | Action |
|---------|--------|
| "Scan for tokens" | Microcap scan |
| "Analyze [token]" | Full thesis |
| "What narrative is trending?" | Narrative map |
| "Risk score for [token]" | Risk analysis |
| "Watch [token]" | Add to watchlist |
| "My opportunities" | Current picks |
| "Market overview" | Broad analysis |

## Storage

```
agents/ats/
├── scanners/
│   ├── microcap_scanner.py
│   ├── narrative_scanner.py
│   └── alert_scanner.py
├── analysis/
│   ├── risk_scorer.py
│   ├── thesis_generator.py
│   └── signal_generator.py
├── data/
│   ├── tracked_tokens.json
│   ├── theses/
│   └── alerts/
└── reports/
    ├── daily_summary.md
    └── opportunity_list.md
```

## Safety & Ethics

### Not Financial Advice
All outputs clearly marked:
```
⚠️ ANALYSIS ONLY - NOT FINANCIAL ADVICE ⚠️
This is automated analysis for research purposes.
Always DYOR (Do Your Own Research).
```

### Risk Transparency
Every thesis includes:
- Full risk breakdown
- What could go wrong
- Worst-case scenarios
- Confidence levels

### No Front-Running
ATS will not:
- Execute trades itself
- Share signals before analysis
- Manipulate markets
- Pump tokens

**DISCLAIMER:** This is analytical tooling only. Past performance doesn't predict future results. Crypto is high-risk. Never invest more than you can afford to lose.
