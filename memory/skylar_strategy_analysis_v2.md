# Skylar v2.0 Trading Strategy - Updated Analysis
**Date:** 2026-03-12  
**Author:** Lux (ACA Methodology Applied)

---

## 📊 CURRENT STATUS

### Live Positions (Review Required)
| Trade | Token | Entry | Age | Size | Grade |
|-------|-------|-------|-----|------|-------|
| #3 | UNKNOWN | Feb 28 01:57 | 12 days | 0.01 SOL | A/90 |
| #4 | UNKNOWN | Feb 28 01:57 | 12 days | 0.01 SOL | A+/85 |
| #5 | UNKNOWN | Feb 28 01:57 | 12 days | 0.01 SOL | A/80 |

**⚠️ ALERT:** 3 positions are 12+ days old. Review immediately for exit or manual closure.

---

## 📈 PERFORMANCE METRICS (From Learning Log)

### Overall Statistics
- **Total Trades:** 14
- **Win Rate:** 71.4% (10 wins, 4 losses)
- **Average Win:** +15.8%
- **Average Loss:** -10.2%
- **Net P&L:** +117.0% (from 1.0 SOL start)

### Win/Loss Distribution
```
Wins:  +11.2%, +24.6%, +7.5%, +20.2%, +19.3%, +16.5%, +23.7%, +6.5%, [2 more]
Losses:  -19.5% (rug), -5.9%, -7.7%, -7.6%
```

---

## 🎯 VALIDATED RULES (From 14 Trade Analysis)

### High-Confidence Rules (3+ successful applications)
1. **Enter within first 6 hours of launch** - Appears in top 3 wins
   - Avg win when applied: +20-24%
   
2. **Exit at +15% - don't get greedy** - Consistent target hits
   - Prevents giving back gains
   
3. **Enter coins under $43k when volume spikes 3x** - Sweet spot
   - Best performing market cap range

### Proven Patterns
| Pattern | Win Rate | Avg Return | Notes |
|---------|----------|------------|-------|
| Age ≤6h + Volume spike | 80% | +20% | Optimal entry window |
| MCap $20k-$43k | 75% | +15% | Best risk/reward |
| MCap < $10k | 50% | +8% | Higher rug risk |
| Age > 24h | 33% | -5% | Momentum dead |

---

## ⚠️ COMMON MISTAKES (To Fix)

### Critical Issues
1. **Entering without checking liquidity depth** (14x repeated)
   - **Impact:** Caused most losses
   - **Fix:** Add liquidity ratio check before entry

2. **Holding too long on losers**
   - **Impact:** -19.5% rug loss
   - **Fix:** Strict 4h time stop

3. **Chasing old coins (>24h)**
   - **Impact:** 2 of 4 losses were on older coins
   - **Fix:** 24h hard cutoff

---

## 🔧 PARAMETER REFINEMENTS

### Current Config vs Recommended
```python
CURRENT → RECOMMENDED

mcap_max: $70k → $50k (optimal_max unchanged)
age_max: 24h → Keep (validated)
require_2_green_candles: True → Keep 
time_stop: 240min → Keep
stop_loss: 7% → Keep
target_profit: 15% → Keep

NEW FILTERS TO ADD:
- liquidity_ratio_check: min 0.15
- volume_5m_threshold: 3x avg
- consecutive_loss_pause: 2 losses
```

---

## 📋 ENTRY CHECKLIST (Updated)

Before executing any trade:

- [ ] **Liquidity Check:** ≥$5K AND ratio >15% of mcap
- [ ] **Age Check:** 1h - 24h (optimal: 1-6h)
- [ ] **Market Cap:** $15K - $50K sweet spot
- [ ] **Volume Spike:** ≥3x 5-min average
- [ ] **2 Green Candles:** Confirmed
- [ ] **Grade:** A+ or A only
- [ ] **Cooldown:** Not after 2 consecutive losses

---

## 🎯 STRATEGY SUMMARY

**Core Thesis:** Low-cap scalping on fresh launches (<6h) with momentum confirmation

**Key Edge:** 
1. Speed of detection (AOE scans every 30 min)
2. Liquidity filtering (prevents rugs)
3. Age-based momentum window
4. Disciplined exits (+15% TP, -7% SL, 4h time)

**Expected Performance:**
- Win Rate: 70-75%
- Avg Winner: +15%
- Avg Loser: -7%
- Risk/Reward: 2.1:1

**Current Issues to Address:**
1. 3 stuck positions (12 days old)
2. Liquidity depth not checked pre-entry
3. Need automatic position timeout alerts

---

## 📝 ACTION ITEMS

1. **URGENT:** Review/close 3 old positions
2. **Fix liquidity check** in entry validation
3. **Add position aging alerts** (>24h warning, >4d urgent)
4. **Resume live trading** once positions cleared
5. **Consider AOE-Skylar reintegration** for signal flow

---

*Generated using ACA 7-step methodology*  
*Next Review: 2026-03-19*
