# Multi-Scanner Trading Signal System for Tem

## How It Works

**Multi-Scanner Consensus Approach:**
1. **I run 4 scanners simultaneously:**
   - v5.4 (Primary - Survivor Edition)
   - v5.5 (Chart Analysis - Experimental)
   - v5.3 (Post-Rug Protection)
   - v5.1 (Legacy Reliable)

2. **I aggregate results** - Find tokens that multiple scanners agree on

3. **I filter for consensus** - Only Grade A tokens that 2+ scanners confirm

4. **I send you signals** - Clean, high-confidence opportunities

5. **You trade** - You execute on your end

---

## Why Multi-Scanner?

**Problem with single scanner:**
- ALIENS/XTuber got Grade A from v5.4 but still rugged
- One scanner can be fooled by fake metrics

**Solution - Consensus:**
- Need 2+ scanners to agree on Grade A
- Reduces false positives
- Higher confidence trades
- Better risk management

---

## Signal Format

```
🎯 MULTI-SCANNER CONSENSUS SIGNALS
============================================================
Scanners Run: v5.4, v5.5, v5.3, v5.1
Signals Found: 3
Minimum Consensus: 2+ scanners Grade A
============================================================

🔥 CONSENSUS SIGNAL #1: TokenName (SYMBOL)
Consensus Level: STRONG
Scanners Agree: 3/4 Grade A
Average Score: 16.5

📊 TOKEN METRICS:
Age: 6.2h | Top 10%: 28%
MCAP: $85,000 | Liq: $25,000
Volume 24h: $120,000

📈 SCANNER BREAKDOWN:
  v5.4: Score 16.5 (Grade A)
  v5.5: Score 15.2 (Grade A)
  v5.3: Score 16.0 (Grade A)
  v5.1: Score 14.0 (Grade B)

🎯 TRADE PARAMETERS:
CA: `CNEq4NnvjVWaqJWPtD3PNGrY8T71K9jDe74iES3Epump`

Entry: 0.02 SOL (High Confidence)
Target: +15% | Stop: -7%
Time Stop: 4 hours
------------------------------------------------------------
```

---

## Consensus Levels

| Level | Criteria | Scanners | Action |
|-------|----------|----------|--------|
| 🔥 **STRONG** | Score ≥16, Age ≥6h, Top10% <35% | 3-4 agree | **High priority** - 0.02 SOL |
| ✅ **MODERATE** | Score ≥15, Age ≥3h, Top10% <50% | 2 agree | **Standard** - 0.02 SOL |
| ⚠️ **WEAK** | Score ≥14, Age ≥2h, Top10% <50% | 2 agree | **Optional** - 0.01 SOL |

**No signal** = No scanners agree = NO TRADE

---

## Your Execution Rules

**When you get a signal:**
1. Check the token on DexScreener (verify CA)
2. Look at scanner breakdown (which versions agree)
3. Enter with specified size
4. Set stop loss IMMEDIATELY
5. Set take profit target

**Position Sizing:**
- STRONG consensus (3-4 scanners): 0.02 SOL
- MODERATE consensus (2 scanners): 0.02 SOL
- WEAK consensus: 0.01 SOL or skip

**Daily Limits:**
- Max 3-5 trades per day
- Stop after 3 losses
- Max daily loss: 0.05 SOL

---

## Signal Schedule

| Time (Sydney) | Activity |
|-----------------|----------|
| **6:00 AM** | Morning scan (London open) |
| **12:00 PM** | Midday check |
| **6:00 PM** | Evening scan (US pre-market) |

**Note:** Only sends signals if 2+ scanners agree. No signal = no trade.

---

## Risk Filters (Post-Rug Lessons)

**ALL signals must pass:**
- ✅ Age > 2 hours (no fresh launches)
- ✅ Top 10% < 50% (whale protection)
- ✅ 2+ scanners Grade A (consensus)
- ✅ MCAP $20K-$500K (sweet spot)
- ✅ Liquidity > $10K

**If a token fails any filter = NO SIGNAL**

---

## Scanner Details

| Scanner | Focus | Weight |
|---------|-------|--------|
| **v5.4** | Survivor tracking, lifecycle | Primary |
| **v5.5** | Chart analysis, technicals | Experimental |
| **v5.3** | Post-rug protection | Reliable |
| **v5.1** | Legacy scoring | Stable |

**Consensus requires:**
- v5.4 + any other = MODERATE
- v5.4 + v5.3 + any = STRONG
- All 4 = MAXIMUM CONFIDENCE

---

## Example Scenarios

**Scenario 1: STRONG Signal**
- v5.4: Grade A (Score 16)
- v5.5: Grade A (Score 15)
- v5.3: Grade A (Score 16)
- v5.1: Grade B (Score 14)
- **Result:** 3/4 agree = STRONG signal, 0.02 SOL

**Scenario 2: MODERATE Signal**
- v5.4: Grade A (Score 15)
- v5.5: Grade B (Score 13)
- v5.3: Grade A (Score 15)
- v5.1: Grade C (Score 11)
- **Result:** 2/4 agree = MODERATE signal, 0.02 SOL

**Scenario 3: NO Signal**
- v5.4: Grade A (Score 15)
- v5.5: Grade B (Score 13)
- v5.3: Grade C (Score 12)
- v5.1: Grade B (Score 13)
- **Result:** Only 1 scanner Grade A = NO SIGNAL

---

## Communication

**I'll send:**
- Entry signals (with consensus breakdown)
- Daily P&L summary
- Scanner performance updates

**You handle:**
- All execution
- Stop loss placement
- Position management
- Emotional control

---

## Why This Is Better

**Before (Single Scanner):**
- ALIENS: v5.4 Grade A → Rugged
- XTuber: v5.4 Grade A → Rugged
- False positive rate: High

**After (Multi-Scanner):**
- Need 2+ scanners to agree
- Filters out fake signals
- Higher quality opportunities
- Better risk-adjusted returns

---

## Files

- `run_all_scanners.sh` - Multi-scanner orchestrator
- `SIGNAL_SYSTEM.md` - This documentation
- `generate_signals.sh` - Legacy single-scanner (backup)

---

**Ready to start? First multi-scanner signal tomorrow at 6 AM Sydney time!** 🚀
