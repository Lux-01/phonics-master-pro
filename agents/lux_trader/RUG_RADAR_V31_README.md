# 🛡️ Rug-Radar v3.1 - Shell Wallet Detection

## Overview

Rug-Radar v3.1 introduces **DEV SHELL WALLET DETECTION** to identify and block fake/sybil wallet clusters designed to manipulate token metrics.

## Files Created

| File | Description |
|------|-------------|
| `wallet_analyzer.py` | Core detection module with 4 shell detection methods |
| `rug_radar_v31.py` | Main trading bot with integrated shell detection |
| `rug_radar_v31_shell_demo.py` | Interactive demo of detection capabilities |

## Shell Wallet Detection Methods

### 1. 🔴 Cluster Age Detection (penalty: -4)
**How it works:**
- Analyzes wallet creation timestamps (using first transaction as proxy)
- Organic users have highly varied wallet ages (days/months/years apart)
- Bot clusters are created in batches within hours

**Flag Condition:** Wallet age variance < 1 hour

**Developer Scam Pattern:**
```
❌ DEV BEHAVIOR: Create 100 wallets in a script, all born within 30 minutes
✅ REAL BEHAVIOR: Users have wallets created months/years apart
```

### 2. 🟠 Micro-Buy Filtering (penalty: -3)
**How it works:**
- Tracks average buy size across wallets
- Real retail typically invests $10-$100+
- Shell wallets make tiny purchases to fake activity

**Flag Condition:** Average buy < $5 USD

**Developer Scam Pattern:**
```
❌ DEV BEHAVIOR: 50 wallets each buy $1-3 (cheap fake volume)
✅ REAL BEHAVIOR: Varied $15-200 purchases with real conviction
```

### 3. 🔵 Funding Source Analysis (penalty: -5)
**How it works:**
- Traces first funding transaction for each wallet
- Organic wallets come from exchanges, bridges, varied sources
- Shell wallets funded by single dev wallet

**Flag Condition:** >60% of wallets share common funding source

**Developer Scam Pattern:**
```
❌ DEV BEHAVIOR: Send $5 from DEV_WALLET_1 to 60 new wallets
✅ REAL BEHAVIOR: Users fund from Coinbase, Phantom swaps, etc.
```

### 4. 🟣 Timing Pattern Detection (penalty: -3)
**How it works:**
- Calculates coefficient of variation (CV) for buy intervals
- CV = std_dev / mean (measures irregularity)
- Humans act randomly; bots act regularly

**Flag Condition:** CV < 0.5 (too regular - bot-like)

**Developer Scam Pattern:**
```
❌ DEV BEHAVIOR: Bot executes buys every 60 seconds exactly
✅ REAL BEHAVIOR: Humans buy at random, FOMO-driven times
```

## Red Flags Integration

### Safety Score Calculation
```
Base Safety Score (v3.0 logic)
+ market_cap_range:    +3 pts
+ token_age_sweet:      +2 pts
+ not_known_rug:        +3 pts
+ A+ grade:             +3 pts
+ volume_confirmed:     +2 pts
                        = 13 max

Shell Wallet Deductions (v3.1)
- cluster_age_flag:       -4 pts (variance < 1hr)
- micro_buy_flag:         -3 pts (avg < $5)
- funding_cluster_flag:   -5 pts (>60% same source)
- timing_pattern_flag:    -3 pts (regular intervals)
                        = -15 max penalty

Final Score = Base - Deductions
Minimum = 0
```

### Trade Blocking Logic
```
If Final Score < 4:
    → BLOCK TRADE (too risky)
    
If 3+ shell flags AND Final Score < 6:
    → BLOCK TRADE (high confidence shell cluster)
    
If 1-2 shell flags:
    → ALLOW but reduce position size by 20%
    
If no shell flags:
    → NORMAL execution
```

## API Integration Ready

The module is built to integrate with:

**Helius API** (`fetch_wallet_creation_dates()`)
- Get first transaction timestamp (wallet age proxy)
- Trace funding transaction history
- Identify common funding sources

**Birdeye API** (`holder_stats` endpoint)
- Retrieve holder wallet list
- Get recent trading activity
- Buy/sell transaction data

**DexScreener**
- Holder count verification
- Trading volume cross-check
- Recent swaps data

## Testing Results

### Unit Tests (wallet_analyzer.py)
```
✅ Test 1: Organic wallets (20 wallets) - NOT flagged
✅ Test 2: Shell wallets (50 wallets) - Correctly detected
✅ Test 3: Safety integration - High-risk token blocked
✅ Test 4: Mixed wallets - Edge case handled
```

### Demo Results (v3.1 scenarios)
```
┌──────────────┬──────┬──────┬─────────┬────────┬────────────┐
│ Token        │ Base │ Pen. │ Final   │ Status │ Flags      │
├──────────────┼──────┼──────┼─────────┼────────┼────────────┤
│ BONK_REAL    │ 13   │ 0    │ 13      │ ✅ SAFE │ None       │
│ SUSHI_BOT    │ 10   │ -5   │ 5       │ ⚠️ WARN │ funding    │
│ FAKE_CLUSTER │ 9    │ -12  │ 0       │ 🚫 BLOCK│ age,micro,│
│              │      │      │         │        │ funding    │
│ MIXED_OK     │ 13   │ 0    │ 13      │ ✅ SAFE │ None       │
│ BULL_RUNNER  │ 13   │ 0    │ 13      │ ✅ SAFE │ None       │
└──────────────┴──────┴──────┴─────────┴────────┴────────────┘

Total: 5 trades
🚫 Blocked: 1 (full shell cluster)
⚠️  Flagged: 1 (reduced position)
✅ Clean: 3
```

## Production Deployment

### Step 1: Add API Keys
```python
analyzer = WalletAnalyzer(
    helius_api_key="YOUR_HELIUS_KEY",
    birdeye_api_key="YOUR_BIRDEYE_KEY"
)
```

### Step 2: Replace Simulated Data
In `rug_radar_v31.py`, replace:
```python
# FROM (simulation)
holders = simulate_holder_analytics(token, analyzer)

# TO (real API calls)
holders = fetch_helius_holder_data(token['address'])
```

### Step 3: Run Production
```bash
python3 rug_radar_v31.py
```

## Comparison to Previous Versions

| Metric | v2.1 | v3.0 | v3.1 |
|--------|------|------|------|
| Returns | 30.9x | 35.2x | 40.8x* |
| Shell Detection | ❌ | ❌ | ✅ |
| Micro-Buy Filtering | ❌ | ❌ | ✅ |
| Funding Analysis | ❌ | ❌ | ✅ |
| Timing Pattern | ❌ | ❌ | ✅ |
| Risk Protection | Basic | Medium | High |

*Note: v3.1 simulation shows higher returns due to shell filtering. With real data and blocked trades, returns may be lower but with significantly reduced rug risk.

## Warning Signs - What v3.1 Catches

### 🚨 DEFINITELY DEV
- Wallet ages within 1 hour of each other
- All funded from same dev wallet
- All buys are $1-3 exactly
- Transactions exactly 60 seconds apart

### ⚠️  PROBABLY DEV (mixed)
- 60% wallets from same funding source
- Some micro-buys mixed with real ones
- Moderate age variance but clustering

### ✅ LIKELY REAL
- Varied wallet ages (days to years)
- Diverse funding sources
- Varied buy sizes ($15-$200+)
- Random transaction timing

## Future Enhancements

- **Jupiter API Integration**: Auto-skip trades with shell scores
- **Twitter Bot**: Post shell alerts to warn community
- **Historical Pattern DB**: Learn from past shell clusters
- **Cross-Token Analysis**: Track dev wallet across launches

## Files Location
```
/home/skux/.openclaw/workspace/agents/lux_trader/
├── wallet_analyzer.py              # Detection module
├── rug_radar_v31.py                # Main bot
├── rug_radar_v31_shell_demo.py     # Demo script
├── rug_radar_v31_results.json      # Simulation results
├── shell_detection_demo.json       # Demo results
└── RUG_RADAR_V31_README.md         # This file
```

---

*Built with 🛡️ protection for the Solana ecosystem*
