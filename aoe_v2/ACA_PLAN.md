# AOE v2.0 - ACA Engineering Plan

## Project Overview
**AOE (Autonomous Opportunity Engine)** - Multi-source token opportunity detection system
**Status:** v1.0 underperforming (2 tokens/scan vs target 50+)
**Goal:** v2.0 production-ready with 50+ tokens/scan, 3-5 high-quality opportunities daily

---

## Step 1: Requirements

### 1.1 Inputs
| Source | Endpoint | Rate Limit | Auth |
|--------|----------|------------|------|
| DexScreener | /token-profiles/latest/v1 | No limit | None |
| DexScreener | /latest/dex/pairs/solana | No limit | None |
| DexScreener | /latest/dex/search?q= | No limit | None |
| Birdeye | /defi/tokenlist | 100 req/min | API Key |
| Birdeye | /defi/history_price | 100 req/min | API Key |
| PumpFun | Internal API | Unknown | None |
| Helius | getSignaturesForAddress | Free tier  | API Key |

### 1.2 Outputs
- **Raw Tokens:** 50+ per scan cycle
- **Scored Opportunities:** 3-5 daily with scores 75-95
- **Alerts:** Telegram messages for score >=82
- **Queue:** Stored opportunities 70-82 for review

### 1.3 Success Criteria
```
PASS Criteria:
✓ Scan finds 50+ tokens per run
✓ Score >=75 tokens output per run
✓ Score >=82 tokens trigger Telegram alert within 1 second
✓ Pipeline completes in <30 seconds end-to-end
✓ No unhandled exceptions during 24h test

FAIL Criteria:
✗ <50 tokens scanned (API failure or filter too tight)
✗ Score distribution all <70 (scoring algorithm issue)
✗ Alert delivery fails (Telegram/network issue)
✗ Pipeline crashes on empty API response
```

### 1.4 Strategy Context (User Requirements)
- **Mean Reversion Focus:** Buy dips -10% to -18%
- **Market Cap:** $100K - $20M (adjusted from v1: $500K min)
- **Volume:** Any with 3x+ spike vs 24h average
- **Active Hours:** US market hours (12am-8am Sydney)
- **Narrative Preference:** AI/Meme tokens

---

## Step 2: Architecture

### 2.1 Module Structure
```
aoe_v2/
├── __init__.py
├── scanner_base.py          # Abstract base class
├── scanner_dexscreener.py   # DexScreener implementation
├── scanner_birdeye.py       # Birdeye implementation
├── scanner_pumpfun.py       # PumpFun implementation
├── token_pipeline.py        # Orchestrator/merger
├── scorer.py                # Scoring algorithm v2
├── strategy_filter.py       # User strategy application
├── alerts.py                # Telegram integration
├── main.py                  # Entry point
├── data/
│   ├── token_cache.json
│   └── historical_volume.json
└── tests/
    ├── test_scanners.py
    ├── test_scorer.py
    └── test_integration.py
```

### 2.2 Component Diagram
```
┌─────────────────┐
│   Entry Point   │ main.py
│   (cron job)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│  Fetch  │ │  Fetch   │ Parallel execution
│DexScreen│ │ Birdeye  │
└────┬────┘ └────┬─────┘
     │           │
     └─────┬─────┘
           ▼
┌──────────────────┐
│   Token Pipeline │ Merge, dedupe, enrich
│   (orchestrator) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Scorer v2      │ Multi-factor scoring
│   (score 0-100)  │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│ >=82    │ │ 70-82    │
│ ALERT   │ │ Queue    │
└────┬────┘ └──────────┘
     │
     ▼
┌──────────────────┐
│   Telegram       │ Immediate delivery
│   Notification   │
└──────────────────┘
```

### 2.3 Token Data Schema
```python
@dataclass
class Token:
    # Identity
    address: str          # Contract address
    symbol: str           # Token symbol
    name: str             # Full name
    chain_id: str         # blockchain
    
    # Market Data
    price: float          # Current price USD
    market_cap: float     # Market cap USD
    liquidity: float      # Liquidity USD
    volume_24h: float     # 24h volume USD
    volume_1h: float      # 1h volume for spike detection
    volume_5m: float     # 5m volume for momentum
    price_change_1h: float
    price_change_24h: float
    price_change_5m: float
    
    # Metadata
    txns_24h: int         # Transaction count
    holders: int          # Unique holders
    creation_time: Optional[datetime]  # Token age
    
    # Scoring
    opportunity_score: Optional[float] = None
    score_breakdown: Optional[Dict] = None
    
    # Source tracking
    source: str           # Where discovered
    discovered_at: datetime  # When first seen
```

---

## Step 3: Data Flow

### 3.1 Pipeline Stages

**Stage 1: Discovery (5 seconds)**
```
Scanner Base → Parallel API Calls
├── DexScreener: token-profiles (max 100 tokens)
├── DexScreener: trending pairs (max 100 pairs)
├── Birdeye: tokenlist sorted by volume (max 100 tokens)
└── PumpFun: recent listings (max 50 tokens)

Output: Raw token list (~250 tokens, high duplication)
```

**Stage 2: Deduplication (1 second)**
```
Token Pipeline → Address-based deduplication
- Create dict keyed by address
- Merge duplicate entries (prefer richer data)
- Track all sources that found token

Output: Unique token list (~150 tokens)
```

**Stage 3: Filtering (1 second)**
```
Strategy Filter → Apply user constraints
- MC: $100K - $20M (relaxed from v1: $500K - $50M)
- No minimum liquidity (was $20K)
- Volume: Any (was $50K min)
- Exclude: stablecoins, obvious rugs

Output: Filtered token list (~80-120 tokens)
```

**Stage 4: Enrichment (10 seconds)**
```
Token Pipeline → Enrich with calculated metrics
- Volume spike ratio (1h/24h avg)
- Price momentum (5m, 1h, 24h)
- Liquidity/MC ratio
- Transaction density (txns/volume)
- Age calculation (if available)

Output: Enriched token data
```

**Stage 5: Scoring (5 seconds)**
```
Scorer v2 → Multi-factor scoring
┌──────────────────────────────────────────────────┐
│  Component          Weight   Target Value       │
├──────────────────────────────────────────────────┤
│  Mean Reversion Fit  25%     Dip -10% to -18%   │
│  Microcap Potential  20%     MC $100K-$5M       │
│  Volume Spike        20%     3x+ avg             │
│  Narrative Match     15%     AI/Meme keywords    │
│  Momentum            10%     Positive 5m/1h     │
│  Liquidity Health     5%     Liq/MC >0.1        │
│  Risk Penalty       -15%     Volatility, age      │
└──────────────────────────────────────────────────┘

Output: Scored opportunities (expect 20-40 tokens 70+)
```

**Stage 6: Alert Decision (2 seconds)**
```
┌─────────────┐     ┌─────────────┐     ┌───────────┐
│   Score     │────▶│   >=82?     │────▶│ TELEGRAM  │
│   0-100     │     └──────┬──────┘     │ ALERT     │
└─────────────┘            │            └───────────┘
                           │No
                           ▼
                    ┌─────────────┐
                    │   >=75?     │
                    └──────┬──────┘
                           │Yes
                           ▼
                    ┌─────────────┐
                    │ ADD TO QUEUE│
                    └─────────────┘
```

**Stage 7: persistence (2 seconds)**
```
- Alert log: timestamp, token, score, breakdown
- Queue update: scored opportunities 75-82
- State update: scan stats for monitoring
```

---

## Step 4: Edge Cases

### 4.1 API Failures
| Scenario | Behavior | Fallback |
|----------|----------|----------|
| DexScreener timeout | Log warning, continue with other sources | Use cached data if <1hr old |
| Birdeye rate limit (429) | Exponential backoff, retry 3x | Skip, mark source unavailable |
| Helius API down | Skip wallet analysis | Continue without holder data |
| All APIs down | Exit with error, alert user | Don't send false "no opportunities" |
| Empty response | Log, return empty list | Don't crash pipeline |

### 4.2 Data Quality Issues
| Scenario | Detection | Handling |
|----------|-----------|----------|
| Zero market cap | MC == 0 after parsing | Filter out, log warning |
| Infinite volume | volume > 1T USD | Cap at reasonable max, flag |
| Negative price change | Already handled | Keep for reversion scoring |
| Missing symbol | symbol == "" or None | Skip, can't alert effectively |
| Stale data | unchanged since last scan | Remove from active tracking |

### 4.3 Scoring Edge Cases
| Scenario | Detection | Solution |
|----------|-----------|----------|
| Score >100 | arithmetic overflow | Clamp to 100 |
| Score <0 | risk penalty too high | Clamp to 0 |
| All scores identical | Same token data | Add tiny random jitter to break ties |
| No tokens pass filter | Empty after filtering | Log, return helpful message |
| Perfect DIP detected | -15% exactly | Give max mean reversion score |

### 4.4 Alert Edge Cases
| Scenario | Handling |
|----------|----------|
| Telegram down | Queue alerts, retry in 60s |
| Rate limited | Backoff, batch if multiple queued |
| Same token alerting repeatedly | 1hr cooldown per token |
| Queue full ( >100 ) | Remove oldest, add newest |
| Midnight UTC rollover | Handle timezone properly |

---

## Step 5: Tool Constraints

### 5.1 API Documentation Review

**DexScreener API:**
- Endpoints: `/token-profiles/latest/v1`, `/latest/dex/pairs/{chain}`, `/latest/dex/search`
- Rate limits: None documented (be polite: 1 req/sec)
- Response size: ~150KB typical
- Timeouts: Set to 15s

**Birdeye API:**
- Endpoint: `/defi/tokenlist` (public-api.birdeye.so)
- Auth: x-api-key header required
- Rate limit: 100req/min free tier
- Response: JSON with nested `data.tokens` array
- Timeouts: Set to 15s

**Telegram API:**
- Via OpenClaw `message` tool
- Rate limit: 20msg/min per chat
- Constraint: Must specify target channel
- Format: Markdown supported

### 5.2 Tool Requirements
```python
# Required imports (standard library only + requests)
import requests          # API calls
import json              # Data serialization
import time              # Rate limiting, timestamps
from datetime import datetime, timedelta  # Age calculations
from dataclasses import dataclass, asdict  # Token schema
from typing import List, Dict, Optional, Any  # Type hints
from pathlib import Path  # File operations
from abc import ABC, abstractmethod  # Scanner base class
from concurrent.futures import ThreadPoolExecutor, as_completed  # Parallel fetch
import logging           # Structured logging
```

### 5.3 Resource Constraints
- Max scan duration: 30 seconds
- Memory per scan: <100MB
- Disk writes: Only for state/cache files
- Network: ~10 API calls per scan
- Log retention: 7 days rotation

---

## Step 6: Error Handling

### 6.1 Retry Strategy
```python
@retry(stop=stop_after_attempt(3), 
       wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)))
def fetch_with_retry(url, headers=None, timeout=15):
    """Fetch with exponential backoff"""
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response
```

### 6.2 Error Logging
```python
# Structured logging format
{
    "timestamp": "2026-03-09T03:08:00Z",
    "level": "ERROR",
    "component": "scanner_birdeye",
    "message": "API timeout after 3 retries",
    "context": {
        "endpoint": "/defi/tokenlist",
        "attempt": 3,
        "error": "ConnectTimeout"
    }
}
```

### 6.3 Fallback Cascade
```
Primary: DexScreener token-profiles
    ↓ (if fails)
Fallback 1: DexScreener trending pairs
    ↓ (if fails)
Fallback 2: DexScreener search + Birdeye
    ↓ (if all fail)
Final: Exit with error, log to persistent store
```

---

## Step 7: Testing Plan

### 7.1 Unit Tests
```python
# test_scorer.py
def test_score_calculation():
    """Verify scoring math with known inputs"""
    token = Token(
        price_change_1h=-15.0,  # Perfect dip
        market_cap=1_000_000,    # Good microcap
        volume_5m=50000,         # High 5m spike
        liquidity=500_000
    )
    score, breakdown = scorer.score(token)
    assert 75 <= score <= 95
    assert breakdown['reversion_fit'] == 95  # Max for -15%

# test_scanners.py
def test_dexscreener_fetch():
    """Mock DexScreener response"""
    with requests_mock.Mocker() as m:
        m.get("https://api.dexscreener.com/token-profiles/latest/v1",
              json=MOCK_PROFILES)
        tokens = scanner.fetch()
        assert len(tokens) > 0
        assert all(hasattr(t, 'address') for t in tokens)
```

### 7.2 Integration Tests
```python
# test_integration.py
def test_full_pipeline():
    """End-to-end scan with mocked APIs"""
    with mock_all_apis():
        results = pipeline.run_scan()
        
    # Verify outputs
    assert len(results['tokens_scanned']) >= 50
    assert len(results['opportunities']) >= 3
    assert all(o['score'] >= 75 for o in results['opportunities'])
```

### 7.3 Validation Report Script
```python
# validate_aoe.py
"""Self-debug validation script"""
def validate():
    print("🔍 AOE v2.0 Validation Report")
    print("=" * 60)
    
    # 1. Token count
    print("\n1. Token Coverage:")
    print(f"   Expected: 50+ | Actual: {len(tokens)}")
    assert len(tokens) >= 50
    
    # 2. Score distribution
    print("\n2. Score Distribution:")
    scores = [t.opportunity_score for t in tokens if t.opportunity_score]
    high = len([s for s in scores if s >= 82])
    print(f"   Score >=82: {high} tokens (target: 3-5 daily)")
    
    # 3. Alert test
    print("\n3. Alert System:")
    test_alert = alerts.send_test()
    print(f"   Test alert: {'✅ DELIVERED' if test_alert else '❌ FAILED'}")
    
    # 4. Performance
    print(f"\n4. Performance: {elapsed:.1f}s (target: <30s)")
    
    print("\n" + "=" * 60)
    print("✅ AOE v2.0 VALIDATION PASSED")
```

### 7.4 Success Metrics
```
After 24h live test:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric                    Target    Actual
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tokens scanned/run        50+       __
Opportunities (score 75+) 3-5/day   __
Alerts sent (score 82+)   3-5/day   __
False positive rate       <10%      __
Scan duration avg         <30s       __
API uptime                >95%      __
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Appendices

### A. File Checklist
- [x] ACA_PLAN.md (this document)
- [ ] scanner_dexscreener.py
- [ ] scanner_birdeye.py
- [ ] scanner_pumpfun.py
- [ ] token_pipeline.py
- [ ] scorer.py
- [ ] strategy_filter.py
- [ ] alerts.py
- [ ] main.py
- [ ] tests/test_scanners.py
- [ ] tests/test_scorer.py
- [ ] tests/test_integration.py
- [ ] validate_aoe.py
- [ ] integration.sh
- [ ] README.md

### B. Cron Configuration
```bash
# /etc/cron.d/aoe_v2 - Run every 15 minutes during US hours
# Sydney: US market hours 12am-8am (12:00-08:00)
# Cron: Every 15 min between minute 0-45 of hours 0-8
*/15 0-8 * * 1-5 skux /home/skux/.openclaw/workspace/aoe_v2/run_scan.sh >> /var/log/aoe.log 2>&1
```

### C. Configuration File
```json
{
  "strategy": {
    "name": "mean_reversion_microcap",
    "mc_min": 100000,
    "mc_max": 20000000,
    "dip_range": {"min": -18, "max": -10},
    "volume_spike": 3.0,
    "narratives": ["ai", "meme", "agent"]
  },
  "scoring": {
    "alert_threshold": 82,
    "queue_threshold": 75,
    "components": {
      "reversion_fit": 0.25,
      "microcap_potential": 0.20,
      "volume_spike": 0.20,
      "narrative_match": 0.15,
      "momentum": 0.10,
      "liquidity_health": 0.05,
      "risk_penalty": -0.15
    }
  },
  "alerts": {
    "telegram_channel": "trading_alerts",
    "cooldown_hours": 1,
    "max_queue_size": 100
  }
}
```

---

**Document Version:** 1.0
**Created:** 2026-03-09
**Author:** Subagent:765b4ec2-b971-4f04-8e34-fbdbf25da94a
**Status:** Draft → Final
