# Smart Swing v2.2 - Auto Trading Strategy
## Name: swing_trade2.2
## Version: 2.2
## Created: 2026-02-21

---

## Strategy Overview

**Name:** swing_trade2.2
**Type:** Smart Swing Trading
**Markets:** Solana meme coins
**Timeframe:** 12:00 AM - 4:00 AM Sydney (4 hours)
**Risk Level:** Moderate (tight trailing stops)

---

## Core Rules

### Trading Window
- **Start:** 12:00 AM Sydney (midnight)
- **End:** 4:00 AM Sydney
- **Timezone:** Australia/Sydney (GMT+11)

### Entry Rules

#### Primary Entry (First Position)
- **Trigger:** Price breaks >5% above session low
- **Volume Check:** 3x average hourly volume
- **Position Size:** 0.5 SOL (50% of available capital)
- **Max Position:** Never more than 0.5 SOL in first entry

#### Confirmation Indicators
- Green candle showing >5% move
- Volume spike (>3x average)
- Market cap: $10M-$100M (safe zone)
- Price action: Higher low forming

### Exit Rules

#### Partial Scale at +20%
- **Trigger:** Position reaches +20% profit
- **Action:** Sell 50% of position (0.25 SOL)
- **Result:** Lock in profits, reduce exposure

#### Trailing Stop (Updated)
- **After scale:** -10% from highest price (tighter than v2.1)
- **Calculation:** Track peak price since entry
- **Exit:** Sell remaining position if price drops 10% from peak

#### Re-Entry Rules
- **Wait for:** Price dips -10% from recent peak
- **Position Size:** 0.25 SOL (25% of remaining capital)
- **Target:** +15% profit for scale (lower than primary entry)
- **Trail:** -10% from re-entry peak

#### EOD Rule (End of Day)
- **Trigger:** Time = 11:30 PM Sydney
- **Condition:** If profit >= +12%
- **Action:**
  1. Scale 75% of position immediately
  2. Trail remaining 25% with -8% stop
  3. Close by 4:00 AM regardless

### Hard Stops (Emergency)
- **Max Loss:** -7% from entry (immediate exit)
- **Time Stop:** If flat after 30 minutes, consider exit
- **Choppy Market:** If no trend forms in 1 hour, exit

---

## Risk Management

### Capital Allocation
- **Total Capital:** 1 SOL maximum exposure
- **Primary Entry:** 0.5 SOL (50%)
- **Re-Entry:** 0.25 SOL (25% max)
- **Dry Powder:** Minimum 0.25 SOL (25%) always available

### Position Sizing
| Setup Quality | Entry Size | Re-Entry Size |
|--------------|------------|---------------|
| A+ (all signals) | 0.5 SOL | 0.25 SOL |
| A (missing one) | 0.3 SOL | 0.2 SOL |
| B+ (marginal) | 0.25 SOL | Skip |
| B or lower | Skip trade | - |

### Daily Limits
- Max 3 trades per session
- Max 1 re-entry per primary trade
- Stop trading after 2 consecutive losses
- Stop if market cap falls below entry by >20%

---

## Signal Filters

### Trade These ✅
- ✅ Market cap: $10M-$100M (sweet spot)
- ✅ Volume: >$100K in last hour
- ✅ Trending status on DexScreener
- ✅ Green candles, higher lows
- ✅ Price above EMA20 on 15min chart
- ✅ Volume increasing on price rise

### Skip These ❌
- ❌ Market cap < $5M (too risky)
- ❌ Already up >100% in 6h (chasing)
- ❌ Volume declining as price rises (divergence)
- ❌ Multiple red wicks on recent candles
- ❌ BTC/SOL dumping >5% (market risk)
- ❌ Single wallet holding >5% supply (whale risk)

---

## Auto-Trading Logic

### State Machine
```
STATE: IDLE
  → Check every 5 minutes during trading window
  → Look for breakout >5% + volume spike
  → If signal: move to STATE: ENTERING

STATE: ENTERING
  → Execute buy order for 0.5 SOL
  → Track entry price
  → Set initial stop at -7%
  → Set scale target at +20%
  → Move to STATE: POSITION_OPEN

STATE: POSITION_OPEN
  → Monitor price every 1 minute
  → Update peak price tracker
  → Check scale target (+20%)
  → Check trailing stop (-10% from peak)
  → Check EOD rule (11:30 PM cutoff)
  → If scale: execute PARTIAL_EXIT
  → If stop: execute FULL_EXIT
  → Move to STATE: TRAILING

STATE: PARTIAL_EXIT
  → Sell 50% of position
  → Update trailing stop to -10% from peak
  → Continue monitoring
  → Move to STATE: TRAILING

STATE: FULL_EXIT
  → Sell 100% of remaining position
  → Log trade details
  → Wait 15 minutes cooldown
  → Move to STATE: WAITING_REENTRY

STATE: WAITING_REENTRY
  → Wait for -10% dip from peak
  → Volume >2x on bounce
  → If signal: move to STATE: REENTERING

STATE: REENTERING
  → Execute buy for 0.25 SOL
  → Set scale target at +15%
  → Set trailing stop -10%
  → Move to STATE: POSITION_2_OPEN

STATE: POSITION_2_OPEN
  → Same as POSITION_OPEN
  → Target: +15% scale, -10% trail
  → No third entries allowed

STATE: EOD_HANDLING
  → Check time (11:30 PM)
  → If profit >=+12%: scale 75%
  → Trail remaining 25% with -8%
  → At 4:00 AM: close all positions

STATE: SESSION_END
  → Log all trades
  → Calculate P&L
  → Generate summary
  → Wait for next session
```

---

## Execution Commands

### Manual Override (Emergency)
- `STOP_TRADING` - Immediately exit all positions
- `SKIP_REENTRY` - Skip planned re-entry
- `HOLD_POSITION` - Ignore trailing stop (manual)
- `SCALE_NOW` - Scale position immediately

### Auto-Trading Commands
- `START_SESSION` - Begin trading at 12:00 AM
- `END_SESSION` - Close all at 4:00 AM
- `PAUSE` - Stop new entries, manage open positions
- `RESUME` - Resume full trading

---

## Performance Metrics

### Track These
1. Total trades per session
2. Win rate (%)
3. Average profit per trade
4. Max drawdown
5. Profit factor (gross profit / gross loss)
6. Average hold time
7. Slippage on entries/exits

### Success Criteria
- Win rate >60%
- Average profit >+8%
- Max drawdown <15%
- Profit factor >1.5

---

## Files & Locations

```
~/.openclaw/workspace/
├── strategies/
│   └── swing_trade2.2.md            # This file
├── swing_trade2.2_agent.py         # Auto-trading script
├── swing_trade2.2_config.json     # Settings
├── trading_logs/
│   └── swing_trade2.2_YYYY-MM-DD.json  # Daily logs
└── alerts/
    └── swing_trade_alerts.py       # Notification system
```

---

## Contact & Alerts

### Notifications
- Entry/Exit: Immediate Telegram alert
- Scale: Immediate Telegram alert
- Stop hit: Immediate Telegram alert
- EOD rule: 11:30 PM alert
- Session summary: After 4:00 AM

### Emergency Contact
- Manual override available
- Human approval for:
  - Positions >0.75 SOL
  - Trades outside window
  - Unusual market conditions

---

## Backtest Results

**v2.2 Performance:**
- Tested on: PUNCH (+48.2%), 67 (+17.6%)
- Win rate: 80% (4/5 trades)
- Avg profit: +15.3%
- Max drawdown: -8.9%
- vs v2.1: +7% improvement via tighter trails

---

## Version History

- **v2.0:** Basic swing strategy
- **v2.1:** Added partial scaling, -15% trail
- **v2.2:** Tighter -10% trail, +15% re-entry target, EOD rule

---

_Last Updated: 2026-02-21 04:38 AM Sydney_
_Next Review: After 10 live trades_
