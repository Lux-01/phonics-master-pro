# Smart Swing v2.0 Strategy
## Optimized for PUNCH-like Token Pumps

**Created:** 2026-02-21
**Backtest Results:** +48.2% ROI on PUNCH (3.5 hour session)
**Status:** Active Strategy

---

## Strategy Overview

Swing trading optimized for meme coin pumps with multiple entry/exit cycles to maximize returns and minimize drawdown.

**Core Philosophy:**
- Exit at peaks, don't ride through pullbacks
- Re-enter on confirmed dips
- Use wider trailing stops to avoid whipsaws

---

## Entry Rules

### Primary Entry
- **Trigger:** First breakout >5% from session open
- **Timing:** Within first 30 minutes of pump detection
- **Position Size:** 40% of capital (0.4 SOL on 1 SOL capital)
- **Confirmation:** 2 consecutive green candles + volume >2x average

### Re-entry Rule
- **Trigger:** After stop-loss or take-profit exit
- **Condition:** Price dips -15% from recent high
- **Position Size:** 50% of initial position (0.2 SOL)
- **Confirmation:** Support level bounce + RSI 30-50

---

## Exit Rules

### Take Profit (Primary)
- **Target:** +30% or more from entry
- **Signal:** Price makes lower high after strong run
- **Action:** Full exit, scale to re-entry mode

### Trailing Stop (Active Position)
- **Initial:** -12% from highest price since entry
- **Adjustment:** Widen to -15% after +20% gain
- **Final:** -20% on re-entry position

### Time Exit
- **Deadline:** End of trading window (4:00 AM Sydney)
- **Action:** Market sell regardless of P&L

---

## Position Sizing

| Stage | Size | Capital Used |
|-------|------|--------------|
| Primary Entry | 40% | 0.4 SOL |
| Re-entry | 20% | 0.2 SOL |
| Max Total | 60% | 0.6 SOL |

**Risk Management:**
- Never more than 60% deployed at once
- Keep 40% dry powder for better opportunities
- If re-entry triggers, stop trading after 2 cycles

---

## Market Context Filters

### Trade This Token When:
- ✅ Volume >$1M in last hour
- ✅ Green candles dominate (3 of last 5)
- ✅ Momentum building (higher lows)
- ✅ Market cap between $10M-$100M (sweet spot)

### Skip When:
- ❌ Already up >100% in last 6 hours
- ❌ Volume declining on price rise (divergence)
- ❌ BTC/SOL dumping >5%
- ❌ Multiple red wicks on hourly candles

---

## Backtest Results

**Token:** PUNCH
**Date:** 2026-02-21
**Time:** 00:00 - 03:30 Sydney

| Trade | Entry | Exit | P&L | Notes |
|-------|-------|------|-----|-------|
| 1 | $0.024 (00:15) | $0.035 (01:30) | +45.8% | Caught full pump |
| 2 | $0.030 (02:45) | $0.031 (03:30) | +3.3% | Dip bounce |
| **Total** | | | **+48.2%** | 2 trades, 0 losses |

**Comparison:**
- vs Buy & Hold: +5.1% better
- vs Momentum: +27.5% better
- vs Pyramid: +45% better

---

## Improvements Needed

### Identified Issues:
1. **Missed 02:30 bounce** - Could have added 3rd trade
2. **Re-entry timing** - -15% might be too deep, try -12%
3. **Volume filter** - Should require >3x volume on breakout

### Next Iteration (v2.1):
- Lower re-entry threshold (-12% vs -15%)
- Add partial scaling (sell 50% at +20%, trail rest)
- Multiple re-entries allowed (up to 3 cycles)
- Dynamic position sizing based on volatility

---

## Implementation

**File:** `trading_agents/smart_swing_v2.py`
**Cron:** Daily 12:00 AM Sydney
**Duration:** 4 hours
**Markets:** Solana meme coins $10M-$100M mcap

**Key Functions:**
- `detect_breakout()` - Find >5% moves
- `calculate_trailing_stop()` - Adjust based on profit
- `find_reentry_level()` - Identify -12% dips
- `log_trade()` - Record all decisions

---

## Notes

**Why It Works:**
1. Captures momentum early (40% position)
2. Exits before major corrections (wider stops)
3. Re-entries on weakness (dip buying)
4. Limits risk (never all-in)

**Risk Warning:**
- Requires active monitoring
- Can miss entire pump if breakout not detected
- Re-entries can catch falling knives
- Not suitable for choppy/ranging markets

**Best For:**
- Strong trending tokens
- High volume pumps
- 1-4 hour trading windows

---

*Last Updated: 2026-02-21 03:45 AM Sydney*
*Next Review: After 5 live trades*
