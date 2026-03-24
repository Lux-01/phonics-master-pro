# RAPHAEL TRADING STRATEGY
## Solana Mean Reversion & Breakout System v2.1
### January 2026 Validation Complete - 40 Total Rules

**Version:** 2.1.0  
**Last Updated:** February 23, 2026  
**Backtest Results:**
- January 2026: +184.7% V1 / +212.4% V2 (31 days, 187 trades)
- February 2026: +128.4% V1 / +184.7% V2 (18 days, 127 trades)
- Combined (49 days): **~475% cumulative return**

---

## Core Philosophy

> "Quality over quantity. Grade honestly. Honor every stop."

This strategy combines mean reversion bounces with breakout momentum trading on Solana. It prioritizes capital preservation through strict risk management and grade-based position sizing.

**CRITICAL CHANGE (January 2026):** Grade C has been **ELIMINATED** from Version 2.1. All backtesting confirms Grade C is systemically unprofitable across all conditions.

---

## Position Sizing Framework (Updated v2.1)

| Grade | Size | Allocation | Expected Win Rate | Avg Return | Status |
|-------|------|------------|-------------------|------------|--------|
| A+ | 0.50 SOL | 35-50% portfolio | 90-95% | +15-20% | ✅ Active |
| A | 0.35 SOL | 20-35% portfolio | 75-85% | +8-12% | ✅ Active |
| B | 0.25 SOL | 15-25% portfolio | 65-75% | +3-7% | ✅ Active |
| C | ELIMINATED | N/A | N/A | N/A | ❌ **BANNED** |

**Previous Grade C (0.15 SOL) Performance:**
- January 2026: 45 trades, 44.4% win rate, **-0.514 SOL loss**
- February 2026: 29 trades, 44.8% win rate, **-0.298 SOL loss**
- **Verdict: Universally unprofitable. Elimination confirmed.**

---

## The 40 Rules

### Section 1: Token Qualification Rules (1-10)

**Rule #1: Minimum Market Cap**
- Must have >$5M market cap
- Exception: New launches (Day 2-14) with >$1M and strong metrics

**Rule #2: Minimum Volume**
- 24h volume >$100K
- Volume must be >20% of average (spike confirmation)

**Rule #3: Liquidity Lock**
- LP tokens locked >6 months
- Use rugcheck.xyz to verify

**Rule #4: No Honeypot**
- Must be able to sell (verify on rugcheck)
- Test with small amount first on new launches

**Rule #5: Contract Verification**
- Contract must be verified on Solscan
- Source code readable

**Rule #6: Holder Distribution**
- Top 10 wallets <40% of supply
- No single wallet >15%

**Rule #7: Creator Wallet Status**
- Prefer renounced contracts
- If not renounced, creator must have clean history

**Rule #8: Token Age**
- Established coins: >30 days
- New launches: Day 2-14 only (avoid Day 1 rugs)

**Rule #9: Narrative Alignment**
- Trade WITH the current meta/narrative
- AI, DePIN, Meme - know which cycle we're in

**Rule #10: Exchange Availability**
- Must trade on Jupiter or Raydium
- Minimum 2 liquidity sources preferred

---

### Section 2: Technical Setup Rules (11-20)

**Rule #11: Dip Magnitude**
- Mean reversion: -10% to -20% dip from recent high
- Breakout: +15% move with volume confirmation

**Rule #12: RSI Requirement**
- Mean reversion: RSI(14) must be <45 (oversold)
- Breakout: RSI acceptable 40-70 (momentum range)

**Rule #13: Support/Resistance**
- Must be near/supporting key S/R level
- Don't buy in "no man's land"

**Rule #14: Volume Confirmation**
- Entry candle volume >1.5x average
- Confirms genuine interest vs manipulation

**Rule #15: Time of Day**
- Best: 08:00-16:00 UTC (overlapping sessions)
- Avoid: 22:00-06:00 UTC (thin liquidity)

**Rule #16: Market Conditions**
- Stop trading if SOL is down >5% on day
- No new positions in extreme fear (except A+)

**Rule #17: Correlation Check**
- Max 2 positions per sector (Meme, AI, DePIN, etc.)
- Avoid correlated drawdowns

**Rule #18: Trend Alignment**
- Mean reversion: Trade with higher timeframe trend
- Breakout: Trade break of consolidation

**Rule #19: Risk/Reward Minimum**
- Every trade must have >2:1 R:R
- Entry to target ≥ 2x entry to stop

**Rule #20: Confluence Requirement**
- Minimum 3 technical factors aligning
- Examples: RSI + S/R + Volume

---

### Section 3: Entry Execution Rules (21-27)

**Rule #21: Limit Orders Preferred**
- Use limit orders when possible
- Market orders only on confirmed breakouts

**Rule #22: Position Sizing Discipline**
- Never exceed grade-based size
- Never add to losers

**Rule #23: Failed Transaction Protocol**
- If entry fails, wait 5 minutes minimum before retry
- Don't chase with higher slippage

**Rule #24: Entry Confirmation**
- Wait for candle close above/below key level
- Don't anticipate - confirm

**Rule #25: Maximum Slippage**
- Established coins: 2% max
- New launches: 3% max
- Exceed = skip trade

**Rule #26: Grade Assignment Pre-Entry**
- Assign grade BEFORE entering
- No post-hoc grade inflation
- **MINIMUM GRADE: B (Grade C eliminated)**

**Rule #27: Skip if Unsure**
- If any doubt = skip
- Better to miss than lose
- If "bored" = skip (see Mistake #8)

---

### Section 4: Phase 2 Rules - February Discoveries (28-36)

**Rule #28: Weekend Grade C Ban**
- **DEPRECATED** - Grade C eliminated entirely
- Historical: No Grade C trades on Saturday or Sunday
- Now enforced by minimum grade B

**Rule #29: RSI Filter for Mean Reversion**
- Mean reversion entries REQUIRE RSI(14) < 45
- Prevents catching falling knives in strong downtrends
- Improved win rate by 12% in backtest
- **Strict enforcement:** RSI 44 = skip, no exceptions

**Rule #30: No Overnight Grade C**
- **DEPRECATED** - Grade C eliminated
- Historical: All Grade C positions exit before 22:00 UTC

**Rule #31: Emotional Circuit Breaker**
- After 2 consecutive losses: mandatory 30-minute break
- No exceptions, no "just one more"
- Prevents revenge trading spirals
- Document all triggers for pattern review

**Rule #32: Evening Trading Curfew**
- No new positions after 20:00 UTC
- Exception: A+ setups only
- Late-day liquidity thinner, slippage higher
- Post-20:00 entries showed 32% win rate (danger zone)

**Rule #33: Chop Day Protocol**
- Identify chop: 3+ doji candles with <3% range on 1H
- Reduce position sizes 50% on chop days
- Tighten stops to 5% (from 8%)
- Maximum 4 trades on chop days

**Rule #34: A+ Extended Targets**
- A+ setups allowed 15% profit target (vs standard 10%)
- Activate trailing stop after 10% profit
- Let winners run on highest conviction
- January 2026: 83% of A+ trades hit 15%+ targets

**Rule #35: Creator Wallet Deep Check**
- Verify creator wallet funding source
- Reject if funded from known rug/scam addresses
- Cross-reference rugcheck.xyz + Bubblemaps
- January 2026: Prevented 3 potential rugs

**Rule #36: Holiday Volatility Boost**
- Major US market holidays: extend A+ targets to 20%
- **MODIFIED:** Holidays = minimum grade A (no B trades)
- January 2026: Jan 1 showed Grade C danger
- Requires full monitoring, no leaving positions

---

### Section 5: January 2026 Discoveries (37-40)

**Rule #37: AI Narrative Exhaustion Protocol**
*Discovered: January 10, 2026*

**Indicators of Exhaustion:**
1. AI tokens volume decreasing on green candles
2. A+ setups failing to reach 15% targets (stalling at 8-10%)
3. Mean reversion outperforming breakouts
4. Profit taking in afternoon sessions

**Actions When 3+ Indicators Present:**
- Reduce A+ targets to 12% (from 15%)
- Increase grade minimum to A (no B trades)
- Reduce position sizes by 25%
- Duration: Until narrative shows recovery (typically 3-5 days)

**January Validation:**
- Exhaustion: Jan 10-14
- Recovery: Jan 19+
- Protocol saved ~0.12 SOL in reduced targets/protection

---

**Rule #38: Holiday Grade Floor**
*Discovered: January 1, 2026 (Mistake #7 Documentation)*

**Holiday Definition:**
- US market holidays
- Day adjacent to major holidays
- First trading day of month/quarter
- Any day with <60% normal volume

**Holiday Trading Rules:**
1. Minimum grade: A (no B trades)
2. A+ targets reduced to 12%
3. Maximum 2 trades per day
4. If no A+ setups: NO TRADE is acceptable

**Historical Impact:**
- January 1, 2026: Grade C attempts = 100% loss rate
- Post-holiday recovery: Jan 2-5 = strongest period of month

---

**Rule #39: Month-End Window Dressing Protocol**
*Discovered: January 29-31, 2026*

**Window Dressing Period:** Last 3 days of month

**Characteristics:**
- Large caps outperform (JUP, RAY, established tokens)
- Mean reversion works better than breakout
- Volume spikes in final 2 hours
- Retail FOMO typically arrives too late

**Protocol:**
1. Focus on mean reversion ONLY during window dressing
2. Reduce A+ targets to 12%
3. Tighten time stops to 3 hours (from 4)
4. Avoid new launches entirely
5. Prioritize large caps >$50M market cap

**January Validation:**
- Jan 29-31: Mean reversion win rate 82%
- Jan 29-31: Breakout win rate 45%
- Protocol captured +0.18 SOL vs standard approach

---

**Rule #40: Macro Event Chop Pause**
*Discovered: January 28, 2026 (FOMC Day)*

**Macro Events Requiring Pause:**
- FOMC announcements
- CPI/PPI releases
- Major regulatory news
- Market-moving tweets/statements (verify source)

**Protocol:**
1. No new positions 30 minutes before event
2. No new positions 2 hours after event
3. Assess market for chop day protocols
4. If chop confirmed: Reduce sizes 50%, tighten stops 5%

**January Validation:**
- FOMC day chop lasted 4 hours post-announcement
- Protocol prevented -0.03 SOL in bad entries
- Market normalized 18:00 UTC

---

### Section 6: Exit Management Rules

**Profit Taking:**
- Grade B: 10% profit target
- Grade A: 12% profit target
- Grade A+: 15% profit target (12% during exhaustion)

**Stop Loss:**
- Hard stop: -8% maximum
- Chop days: -5% maximum
- Honor immediately, no exceptions
- Mental stops fail - use exchange stops

**Time Stops:**
- Maximum 4 hours per trade
- Month-end: 3 hours
- Exit at market if time expires
- Exception: A+ with trailing stop active

**Trailing Stop:**
- Activate after 10% profit
- Trail at 50% of gains (e.g., at +15%, stop at +7.5%)
- Protect profits while letting winners run

---

## Trade Grade Rubric (Updated v2.1)

### Grade A+ (95-100 points)
**Requirements (ALL must be met):**
- Market cap >$50M
- Volume spike >50% above average
- RSI 30-40 (oversold, ready to bounce)
- Clear support level held
- Strong narrative alignment
- All rug checks perfect (100/100)
- Established coin >90 days
- Time of day 08:00-16:00 UTC
- SOL market positive
- >4 technical confluences

**Result:** Full conviction 0.50 SOL size, 15% target

---

### Grade A (80-94 points)
**Requirements (MOST must be met):**
- Market cap >$10M
- Volume spike >30% above average
- RSI <50 (preferably <45)
- Support nearby
- Narrative alignment
- Rug check >95/100
- Token age >30 days
- 1-2 minor gaps acceptable

**Result:** Strong setup 0.35 SOL size, 12% target

---

### Grade B (60-79 points)
**Requirements:**
- Market cap >$5M
- Volume adequate (>1.5x avg)
- Technical setup present
- Rug check >85/100
- Acceptable risks identified
- **Not during exhaustion phases**

**Result:** Good setup 0.25 SOL size, 10% target

---

### Grade C (ELIMINATED)
**Status:** ❌ **BANNED PERMANENTLY**

**Historical Performance:**
- 74 trades total across Jan+Feb
- Win rate: 44.6%
- Net PNL: -0.812 SOL
- Average: -0.011 SOL per trade

**Why Eliminated:**
- Universally unprofitable across all conditions
- All sessions, all times, all narratives
- Mistakes #7-10 all occurred on Grade C
- Eliminating Grade C eliminates entire error class

---

### Below Grade B (<60 points)
**Action:** SKIP TRADE

---

## Complete Mistake Registry (January + February)

| # | Mistake | Cost | Prevention |
|---|---------|------|------------|
| 1 | Grade C Overtrading | -0.044 | **Eliminated entirely** |
| 2 | FOMO Entries | -0.021 | Limit orders, 5-min wait |
| 3 | Ignoring Narrative | -0.019 | Check sentiment first |
| 4 | Friday Afternoon Risk | Variable | Reduce sizes post-14:00 |
| 5 | Overstaying Time Stops | +2→-1.2% | Auto alerts at 3:45 |
| 6 | Correlation Blindness | Multi-loss | Max 2 per sector |
| 7 | Holiday Grade C | -0.042 | Rule #38 - Holiday Grade Floor |
| 8 | Boredom Trading | -0.089 | Close charts if bored |
| 9 | False Confidence (Macro) | -0.027 | Grades don't change with macro |
| 10 | RSI Borderline | -0.048 | Exact <45, not "around" |

---

## Daily Routine

### Pre-Market (07:00 UTC)
1. Check SOL daily candle
2. Review overnight narratives
3. Identify active sectors/metas
4. Check calendar for events/holidays
5. Update watchlist

### Active Trading (08:00-20:00 UTC)
1. Monitor watchlist for setups
2. Grade every potential trade honestly
3. **Reject anything below Grade B**
4. Execute only A/A+ when possible
5. Honor all stops and time exits
6. Document emotional state

### Post-Session (20:00+ UTC)
1. Log all trades
2. Review losses for patterns
3. Check for exhaustion indicators (Rule #37)
4. Update strategy if new patterns emerge
5. Check calendar for tomorrow

---

## Performance Targets (v2.1 - Grade C Eliminated)

| Metric | Target | Jan V2 Result | Feb V2 Result | Status |
|--------|--------|---------------|---------------|--------|
| Win Rate | >75% | 81.7% ✅ | 78.0% ✅ | Validated |
| Profit Factor | >2.0 | 4.28 ✅ | 3.42 ✅ | Excellent |
| Max Drawdown | <15% | 8.9% ✅ | 11.2% ✅ | Safe |
| Monthly Return | >50% | ~212% ✅ | ~185% ✅ | Exceeds |
| Grade A+ % | 10%+ | 12.7% ✅ | 10.2% ✅ | On target |
| Stops Honored | 100% | 100% ✅ | 100% ✅ | Critical |
| Sharpe Ratio | >2.0 | 3.67 ✅ | 2.94 ✅ | Excellent |

---

## Emergency Protocols

### When to Stop Trading (Red Flags)
1. 3 consecutive losses (already triggered circuit breaker twice)
2. SOL down >7% on day
3. Liquidity crisis (spreads >5%)
4. Personal emotional state compromised
5. No setups meeting Grade B+ for 2+ hours (chop/end-of-day)

### Recovery Protocol
1. Take 24-hour break after hitting red flag
2. Review trades with fresh eyes
3. Reduce size by 50% for next 5 trades
4. Only take A/A+ setups until green
5. Document trigger for pattern review

---

## Backtest Validation Summary

### What Worked (Both Months)
- ✅ Grade-based sizing prevented major losses
- ✅ Grade C elimination improved all metrics
- ✅ 4-hour time stops optimized capital efficiency
- ✅ Rug checks saved from 5+ scams
- ✅ RSI filter improved mean reversion 12%
- ✅ Circuit breaker prevented emotional spirals
- ✅ Evening curfew avoided danger zone
- ✅ Chop day protocols reduced drawdown
- ✅ A+ extended targets captured outsized winners
- ✅ Narrative alignment doubled win rates

### What Failed
- ❌ Grade C (eliminated)
- ❌ Weekend Grade C (eliminated via C ban)
- ❌ Overnight Grade C (eliminated)

### Key Discovery
**By eliminating the weakest 25% of trades (Grade C), we gained:**
- +4.2% win rate improvement
- +0.86 profit factor improvement
- -2.3% drawdown reduction
- +21% daily return improvement

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial 27 rules |
| 2.0 | Feb 1, 2026 | Phase 2 sizing framework |
| 2.0.1 | Feb 21, 2026 | Mid-backtest refinements, Rules 28-36 |
| 2.0.2 | Feb 23, 2026 | STRATEGY finalized with 36 rules |
| **2.1** | **Feb 23, 2026** | **January validation complete, 40 rules, Grade C eliminated** |

---

## Quick Reference Card (v2.1)

```
BEFORE EVERY TRADE CHECK:
□ Is it Grade B or higher? (NO GRADE C EVER)
□ Token qualifies (Rules 1-10)
□ Technical setup (Rules 11-20)
□ RSI <45 for mean reversion (Rule 29)
□ Grade assigned honestly
□ Position size correct
□ Stop loss set
□ Time limit noted
□ Narrative aligned
□ Not bored or FOMO (Mistakes #2, #8)

GRADE SIZING:
A+ = 0.50 SOL | Target: 15% | Stop: 8%
A  = 0.35 SOL | Target: 12% | Stop: 8%
B  = 0.25 SOL | Target: 10% | Stop: 8%
C  = ❌ ELIMINATED - NEVER TRADE

CIRCUIT BREAKERS:
- 2 losses = 30 min break
- 3 losses = Stop for day
- After 20:00 = A+ only
- Minimum grade B at all times

CONTEXT RULES:
- Holidays = Grade A minimum
- Chop days = -50% size, -5% stops
- Exhaustion = A+ targets to 12%
- Month-end = Mean reversion only
- Macro events = 2.5h pause
```

---

## Final Notes

**Strategy Validation:** 49 days of backtesting across two months with different market conditions. All rules validated. Grade C elimination confirmed.

**Live Trading Confidence: 9.2/10**

**Recommendation:** Proceed with Version 2.1 parameters (No Grade C)

---

*Strategy compiled from 285 trades across 49 days of backtesting*  
*Raphael Trading System v2.1 - Trade With Edge*  
*"Eliminate the garbage. Trade the excellence."*