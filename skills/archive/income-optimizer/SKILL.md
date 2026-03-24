---
name: income-optimizer
description: Complete income tracking and optimization system. Monitors all revenue streams, calculates MRR, tracks ROI per skill, generates monthly dashboards, and identifies opportunities to increase and diversify income.
---

# Income Optimizer

**Track, analyze, and grow your income.**

The Income Optimizer monitors every revenue stream, calculates true MRR (Monthly Recurring Revenue) including crypto investments and trading, and provides actionable insights to increase profitability per skill.

## Philosophy

**You can't optimize what you don't measure.**

Every source of income - from crypto trading to affiliate revenue - is tracked, categorized, and analyzed to reveal patterns and opportunities.

## Core Workflow

```
COLLECT (All income sources)
     ↓
CATEGORIZE (By type/skill)
     ↓
CALCULATE (MRR, ROI, trends)
     ↓
ANALYZE (Performance by source)
     ↓
IDENTIFY (Growth opportunities)
     ↓
REPORT (Monthly dashboard)
```

## Income Categories

### 1. Skill-Generated Income

Income directly attributable to specific skills:

| Skill | Income Source | Tracking Method |
|-------|---------------|-----------------|
| **ATS** | Trading profits | Wallet tracking |
| **AOE** | Opportunity alerts | Trade outcomes |
| **AWB** | Workflow sales | Product revenue |
| **Research-Synthesizer** | Research service | Service fees |
| **Trading Bots** | Automated trades | Bot logs |

### 2. Crypto Income Streams

- **Trading Profits:** Manual and bot-generated
- **Staking Rewards:** Passive income from holdings
- **Airdrops:** Free tokens received
- **Yield Farming:** DeFi returns
- **NFT Sales:** Digital asset trading
- **Gaming/Social:** Play-to-earn, Moltbook

### 3. Digital Product Revenue

- **Avatar Packs:** Etsy sales
- **Automation Scripts:** Direct sales
- **Templates:** Notion, other platforms
- **Digital Downloads:** Gumroad, etc.

### 4. Service Revenue

- **Consulting:** Hourly/project fees
- **Research Services:** Bespoke analysis
- **Code Reviews:** Development services
- **Strategy Sessions:** Trading guidance

### 5. Passive/Other

- **Affiliate Income:** Referral commissions
- **Ad Revenue:** If applicable
- **Royalties:** Licensing fees
- **Interest:** Savings, etc.

## MRR Calculation

### What Counts Toward MRR

```yaml
# Monthly Recurring Revenue Components

stable_recurring:
  description: "Guaranteed monthly income"
  examples:
    - subscriptions: "Monthly subscriptions"
    - retainers: "Monthly service agreements"
    - staking: "Consistent staking rewards"
  calculation: "sum(all stable sources)"
  confidence: 100%

variable_monthly:
  description: "Income that varies but is consistent"
  examples:
    - trading_average: "Avg monthly trading profit"
    - product_sales: "Avg monthly product revenue"
    - service_income: "Avg monthly service fees"
  calculation: "rolling_3_month_average"
  confidence: 80%

opportunistic:
  description: "One-time or irregular income"
  examples:
    - airdrops: "Unexpected token drops"
    - bonuses: "One-time payments"
    - windfalls: "Large irregular events"
  calculation: "exclude_from_mrr"
  confidence: N/A

mrr_formula: |
  MRR = Stable Recurring + Variable Monthly
  
  Total Monthly Income = MRR + Opportunistic
```

## ROI Per Skill

### Skill ROI Calculation

```python
skill_roi = {
    "development_time_hours": 0,  # Time to build skill
    "maintenance_time_hours_per_month": 0,  # Ongoing upkeep
    "time_cost_at_rate": 0,  # Value of time invested
    
    "direct_income_generated": 0,  # Revenue directly from skill
    "time_saved_hours": 0,  # Hours saved by using skill
    "time_savings_value": 0,  # Value of time saved
    "opportunities_generated": 0,  # Count
    
    "total_return": "direct_income + time_savings_value + opportunity_value",
    "total_investment": "development_time + maintenance_time",
    "roi_percentage": "((total_return - total_investment) / total_investment) * 100"
}
```

### Example Skill ROI

```yaml
# ATS (Autonomous Trading Strategist)
direct_income: "$X/month from trading"
time_saved: "10 hours/week research"
time_saved_value: "$2000/month at $50/hr"
opportunities_generated: "15 high-quality trades/month"
opportunity_value: "$Y/month"

development_time: "40 hours"
maintenance: "2 hours/month"
time_cost: "$2800 initial, $140/month"

roi: "((income + savings) - investment) / investment * 100"
status: "highly_profitable"
```

## Monthly Dashboard

### Dashboard Sections

```markdown
# Income Dashboard: March 2026

## Executive Summary
| Metric | Value | Change |
|--------|-------|--------|
| **MRR** | $X | +12% |
| **Total Month** | $Y | +8% |
| **Run Rate** | $Z | +15% |
| **Target** | $W | 94% of goal |

## By Category

### Crypto Trading (ATS + AOE)
| Source | Amount | MRR Contribution |
|--------|--------|------------------|
| Manual Trading | $X | 15% of MRR |
| Bot Trading | $Y | 20% of MRR |
| Whale Tracker | $Z | 5% of MRR |
| **Total Trading** | **$T** | **40% of MRR** |

Trend: ↑ 23% vs last month
Drivers: Strategy v2.0 improvements, whale tracker activation

### Digital Products
| Source | Amount | MRR Contribution |
|--------|--------|------------------|
| Avatar Packs | $X | 10% of MRR |
| Scripts | $Y | 5% of MRR |
| **Total Products** | **$T** | **15% of MRR** |

Trend: ↑ 5% vs last month
Drivers: New Etsy listing, SEO improvements

### Services
| Source | Amount | MRR Contribution |
|--------|--------|------------------|
| Research Service | $X | 20% of MRR |
| Consulting | $Y | 10% of MRR |
| **Total Services** | **$T** | **30% of MRR** |

Trend: ↑ 15% vs last month
Drivers: New client on retainer

### Staking/Passive
| Source | Amount | MRR Contribution |
|--------|--------|------------------|
| SOL Staking | $X | 12% of MRR |
| DeFi Yield | $Y | 3% of MRR |
| **Total Passive** | **$T** | **15% of MRR** |

Trend: → flat vs last month
Note: Rebalancing to higher-yield pools

## Skill ROI Performance

| Skill | Monthly Income | Time Cost | ROI | Status |
|-------|---------------|-----------|-----|--------|
| **ATS** | $X | 10 hrs | 450% | 🟢 Excellent |
| **AOE** | $Y | 3 hrs | 320% | 🟢 Excellent |
| **AWB** | $Z | 5 hrs | 180% | 🟢 Good |
| **Research** | $W | 8 hrs | 140% | 🟡 Acceptable |

## Top Recommendations

### Immediate Actions
1. **Increase AOE scan frequency** → +15% more trading opportunities
2. **Post weekly research to Moltbook** → Build credibility for services
3. **Create trading signal subscription** → Recurring revenue

### Strategic Initiatives
1. **Build signal bot product** → $500/month potential
2. **Expand research service** → Add 2 more retainer clients
3. **Launch affiliate links** → 10% of product referral income

### Risk Areas
⚠️ Trading revenue 40% of MRR - high volatility risk
→ Recommendation: Increase stable/passive to 50%

## Goals Tracking

| Goal | Target | Current | % Complete |
|------|--------|---------|------------|
| MRR $X | $X | $Y | 85% |
| Diversification | ≤30% from one source | 40% | Need work |
| Bot Performance | +25% monthly | +23% | On track |
| New Product | 1 launch | 0 | Behind |
```

## Revenue Tracking

### Income Entry Format

```json
{
  "income_record": {
    "id": "uuid",
    "date": "2026-03-09",
    "timestamp": "2026-03-09T14:30:00Z",
    
    "source": {
      "category": "trading|product|service|passive|other",
      "skill": "ats|aoe|awb|...",
      "sub_source": "manual|bot|whale_tracker"
    },
    
    "amount": {
      "value": 100.00,
      "currency": "USD|SOL|...",
      "usd_equivalent": 100.00
    },
    
    "metadata": {
      "description": "BONK trade profit",
      "transaction_id": "...",
      "wallet": "...",
      "skill_session_id": "...",
      "tags": ["crypto", "meme", "short_term"]
    },
    
    "reconciliation": {
      "recorded_by": "ats|manual|api",
      "verified": true,
      "verified_at": "..."
    }
  }
}
```

## Growth Opportunity Detection

### What Income Optimizer Scans For

1. **Skill Value Gaps**
   "Skill X generates $Y but could generate $Z with optimization"

2. **Revenue Diversification**
   "Too much concentration in crypto trading - add stable income"

3. **Pricing Optimization**
   "Services underpriced vs market - potential +30%"

4. **Product Gaps**
   "Users asking for X repeatedly - product opportunity"

5. **Affiliate Opportunities**
   "Tools you recommend could generate affiliate income"

### Opportunity Scoring

```yaml
opportunity:
  description: "Increase AOE scan frequency"
  
  potential_monthly_income: "$X"
  implementation_effort: "2 hours"
  confidence: 85%
  time_to_realization: "1 week"
  risk_level: "low"
  
  roi_calculation:
    investment: 2 hours
    return: "$X/month"
    annual_roi: "1200%"
  
  priority_score: "high"
```

## Integration with Other Skills

```
Income Optimizer +
  
  ATS: Track trading income per strategy
  AOE: Track opportunity value generation
  SEE: Skills generating most revenue
  LPM: Track project value
  ALOE: Learn what generates best ROI
  
  All skills contribute to the income picture
```

## Commands

| Command | Action |
|---------|--------|
| "Income dashboard" | Show current month |
| "Add income" | Record new income entry |
| "Show MRR" | Monthly recurring revenue |
| "Skill ROI" | ROI per skill breakdown |
| "Income opportunities" | Growth recommendations |
| "Month close" | Generate monthly report |
| "Compare to last month" | MoM analysis |
| "Income goals" | Progress to targets |
| "Diversification" | Revenue concentration analysis |

## Storage

```
memory/income/
├── streams/
│   ├── income_streams.json     # All income sources
│   ├── stream_history.json     # Historical data
│   └── stream_categories.json  # Categories config
├── transactions/
│   ├── YYYY-MM.json            # Monthly transaction files
│   └── pending.json            # Unverified entries
├── reports/
│   ├── monthly/                # Monthly dashboards
│   ├── quarterly/              # Quarterly summaries
│   └── annual/                 # Year-end reports
├── goals/
│   ├── income_goals.json       # Targets
│   └── progress.json           # Progress tracking
├── skills/
│   ├── skill_income.json       # ROI per skill
│   └── skill_time_cost.json    # Time investment
└── config.json
```

## Cron Jobs

```yaml
daily:
  - sync_wallet_transactions
  - categorize_new_income
  - update_mrr_calculation

weekly:
  - skill_roi_update
  - opportunity_detection

monthly:
  - generate_dashboard
  - goal_progress_update
  - trend_analysis
```

---

**Know your numbers. Grow your income.** 💰
