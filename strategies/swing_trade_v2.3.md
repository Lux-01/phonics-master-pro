# Smart Swing Trading Strategy v2.3

**Version:** 2.3 (Final)  
**Date:** 2026-02-22  
**Status:** Production Ready

---

## Overview

An automated Solana meme coin trading strategy combining breakout signals with risk management, designed for the 12am-4am Sydney window when US markets overlap with high volatility.

---

## Trading Window

| Parameter | Value |
|-----------|-------|
| **Time** | 12:00 AM - 4:00 AM Sydney Time (AEDT) |
| **Frequency** | Daily |
| **Why** | US market overlap creates high volatility |
| **Scan Interval** | Every 30 seconds |

---

## Entry Criteria

### Signal Requirements

| Rule | Threshold |
|------|-----------|
| **Price Breakout** | >+5% in past 6 hours |
| **Market Cap** | $10M - $100M (sweet spot: $20M-$50M) |
| **Liquidity** | >$100,000 |
| **Minimum Score** | 6/8 |

### Scoring System

| Factor | Points |
|--------|--------|
| Market cap $20M-$50M | +3 |
| Market cap $10M-$100M | +2 |
| Price change +10%+ | +3 |
| Price change +5%+ | +2 |
| Volume acceleration | +2 |
| **Maximum** | **8/8** |

### Position Sizing

- **Entry Size:** 0.5 SOL maximum per trade
- **Cash Reserve:** Minimum 0.25 SOL must remain in wallet

---

## Exit Rules

### 1. Scale Target (+20%)

**Trigger:** Price reaches +20% from entry  
**Action:** Sell 50% of position immediately  
**Purpose:** Lock in profits, reduce risk  
**Remaining:** 50% rides with trailing stop

```
Entry: $10.00
Scale: $12.00 (+20%)
Action: Sell 500 tokens → Return ~0.3 SOL
Remaining: 500 tokens for trailing stop
```

### 2. Trailing Stop

**Trigger:** Price drops 10% from highest peak (after scale)  
**Action:** Sell 100% of remaining position  
**Purpose:** Protect remaining gains, let winners run

```
Peak: $13.00
Trail: $11.70 (-10% from peak)
Action: Sell remaining 500 tokens
```

### 3. Hard Stop (-7%)

**Trigger:** Price drops 7% from entry price  
**Action:** Sell 100% immediately  
**Purpose:** Capital preservation on bad trades

```
Entry: $10.00
Stop: $9.30 (-7%)
Action: Sell all 1000 tokens
```

### 4. Break-Even Stop 🛡️ *(v2.2 Addition)*

**Trigger:** Price hits +10% (before scale)  
**Action:** Move hard stop to entry price + 0.5% buffer  
**Purpose:** Never lose money after +10% gain

```
Entry: $10.00
+10%: $11.00 → BE triggered
New stop: $10.05 (+0.5% buffer)

If price drops to $10.00:
Old: Continue to -7% hard stop → Lose money ❌
New: Exit at break-even → No loss ✓
```

### 5. Time Stop

**Trigger:** 4:00 AM Sydney (session end)  
**Action:** Close all open positions  
**Purpose:** No overnight/weekend risk

---

## Risk Management

### Token Blacklist 🚫 *(v2.3 Addition)*

**Trigger:** After ANY exit (hard stop, trail stop, sell all)  
**Duration:** 30 minutes  
**Purpose:** Prevent immediate rebuy of same token after exit

```
Exit PUMP1 at -7% (hard stop)
→ PUMP1 added to blacklist for 30 minutes
→ Bot cannot rebuy PUMP1 during cooldown
→ Prevents "catching a falling knife"
```

### Circuit Breaker 🛑 *(v2.3 Addition)*

**Trigger:** 3 consecutive losses  
**Action:** Stop trading for 60 minutes  
**Purpose:** Protect capital during bad market conditions

```
Trade 1: POPCAT -5% ❌
Trade 2: WIF -6% ❌
Trade 3: MEW -4% ❌
→ CIRCUIT BREAKER TRIGGERED!
→ Trading paused for 60 minutes
→ Market may be choppy - protecting capital
→ Resets after cooldown OR on winning trade
```

**Reset Conditions:**
- 60-minute cooldown expires
- Next trade is a win

### Position Persistence *(v2.2 Addition)*

- Position saved to file after every action
- Loaded on bot restart
- Peak price tracked and saved
- Prevents data loss on crashes

---

## Re-Entry Rules

**Question:** Does the bot re-enter after scaling?  
**Answer:** NO

```
Entry → Scale (+20%) → Trail Stop OR Hold
                            ↓
                       After exit:
                   No automatic re-entry
                   (Blacklist prevents it)
```

**Why no re-entry?**
- Prevents over-trading
- Strategy is "one and done" per signal
- Capital moves to next opportunity

---

## Example Scenarios

### Scenario 1: Normal Win

```
Entry: $10.00
  ↓
+10% → $11.00 (BE triggered, stop at $10.05)
  ↓
+20% → $12.00 (SCALE: Sell 50%, bank profit)
  ↓
+30% → $13.00 (peak)
  ↓
-10% → $11.70 (Trailing stop: Sell remaining 50%)

Result: +15% overall (locked +20% on half, +17% on half)
```

### Scenario 2: Break-Even Protection

```
Entry: $10.00
  ↓
+12% → $11.20 (BE triggered at +10%)
  ↓
Falls to $9.50 (would hit -7% hard stop)

Old (no BE): Sell at -7% = Lose money ❌
New (with BE): Sold at $10.05 = Break-even ✓
```

### Scenario 3: Circuit Breaker

```
Trade 1: BONK -5% ❌ (Loss #1)
Trade 2: WIF -6% ❌ (Loss #2)
Trade 3: MEW -4% ❌ (Loss #3)
  ↓
🛑 CIRCUIT BREAKER TRIGGERED
  ↓
No trades for 60 minutes
  ↓
Cooldown expires → Resume trading
```

### Scenario 4: Blacklist Protection

```
Buy PUMP1 at $10
  ↓
Drops to $9.30 (-7%)
  ↓
Hard stop triggered → Sell all
  ↓
PUMP1 blacklisted for 30 minutes
  ↓
Next scan (30 sec later):
  PUMP1 signal still looks good...
  Score: 7/8...
  But: SKIPPING - blacklisted
  ↓
Bot moves to next signal
```

---

## Performance Tracking

### Session Stats

The bot tracks:
- Total wins/losses
- Consecutive losses (for circuit breaker)
- P&L per trade
- Cooldown status

### Monitoring

**GUI Monitor Available:**
- Real-time P&L display
- Position status
- Trigger prices
- Bot status (active/stopped)
- Control buttons (Start/Stop/Scale/Sell All)

---

## Files

| File | Purpose |
|------|---------|
| `swing_bot_v2.3.js` | Main bot (production) |
| `current_position.json` | Position persistence |
| `blacklist.json` | Token blacklist |
| `session_stats.json` | Win/loss tracking |
| `swing_session_YYYY-MM-DD.json` | Daily trade log |

---

## Quick Reference

| Trigger | Price Level | Action | Purpose |
|---------|-------------|--------|---------|
| 🟢 Scale | +20% | Sell 50% | Lock profits |
| 🛡️ Break-Even | +10% | Move stop | Never lose |
| 🔴 Trail | -10% from peak | Sell 100% | Protect gains |
| 🛑 Hard | -7% (or BE) | Sell 100% | Stop loss |
| ⏰ Time | 4:00 AM | Close all | Session end |
| 🚫 Blacklist | After exit | 30 min ban | No rebuy |
| 🛑 Circuit | 3 losses | 60 min pause | Protect capital |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | Feb 17 | Initial strategy |
| v2.0 | Feb 20 | Jupiter API integration |
| v2.1 | Feb 21 | Added persistence |
| v2.2 | Feb 22 | Break-even stop added |
| **v2.3** | Feb 22 | Blacklist + Circuit breaker |

---

**Ready for production trading** 🦞
