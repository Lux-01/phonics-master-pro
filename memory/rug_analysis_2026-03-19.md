# Rug Pull Analysis: ALIENS & XTuber

**Date:** 2026-03-19  
**Tokens:** ALIENS (aliens.gov), XTuber (Panora)  
**Outcome:** Both rugged within 40 minutes of scanner detection

---

## What the Scanner Saw

| Metric | ALIENS | XTuber |
|--------|--------|--------|
| Age | 0.2h (11 min) | 1.0h |
| MCAP | $71.9K | $155K |
| Liquidity | $21.6K | $34.7K |
| Top 10% | 27.4% ✅ | 72.9% 🚨 |
| Grade | A ✅ | A ✅ |
| Score | 15 | 15.5 |

---

## Why They Passed

### ALIENS (11 minutes old)
- **Scoring:** Got 0.5 points for age (>= 30 min threshold)
- **Red flag:** "🚨 TOO NEW" warning logged but didn't prevent Grade A
- **Problem:** 11 minutes is not enough time to prove legitimacy

### XTuber (1 hour old)
- **Scoring:** Got 0.5 points for age (>= 30 min, < 6h)
- **Red flag:** "⚠️ TOO NEW" + whale concentration ignored
- **Problem:** 72.9% Top 10 = whales can dump instantly

---

## Root Causes

1. **Age scoring too generous**
   - Current: 0.5 points for 30m+, 1 point for 6h+
   - Problem: 11-minute-old tokens shouldn't qualify for Grade A

2. **No whale concentration penalty**
   - Current: Only bonus for < 30% Top 10
   - Problem: No penalty for > 50% concentration

3. **Red flags don't affect grade**
   - Current: Warnings logged but score still >= 14
   - Problem: "TOO NEW" should cap grade at B or C

4. **Volume/MCAP ratio gameable**
   - Both had high volume ratios (2.5x and 1.1x)
   - Early volume can be wash trading or dev buying

---

## Lessons Learned

### For Scanner v5.5+

**Age Requirements:**
- ❌ Current: Grade A possible at 30 minutes
- ✅ Fix: Minimum 2 hours for Grade A, 6 hours for A+
- ✅ Fix: < 1 hour = automatic C grade max

**Whale Concentration:**
- ❌ Current: No penalty for high Top 10%
- ✅ Fix: Top 10% > 50% = automatic reject
- ✅ Fix: Top 10% > 35% = grade cap at B

**Red Flag Impact:**
- ❌ Current: Warnings don't reduce score
- ✅ Fix: Each red flag = -2 points
- ✅ Fix: "TOO NEW" red flag = max score 10 (Grade B)

**Survivor Checkpoint:**
- ✅ Keep: 6h, 12h, 24h checkpoint tracking
- ✅ Add: Tokens must survive 1h before Grade A eligible
- ✅ Add: Track "graduated" tokens separately from "new"

---

## Recommended Code Changes

```python
# In scoring section:

# Age scoring - STRICTER
if age_hours >= 6:
    score += 1
elif age_hours >= 2:
    score += 0.5  # Reduced from 1
else:
    red_flags.append(f"🚨 TOO NEW ({age_hours:.1f}h < 2h)")
    score -= 3  # NEW: Penalty for very new tokens

# Whale concentration - NEW CHECK
if top10_pct > 50:
    red_flags.append(f"🚨 WHALE CONCENTRATION ({top10_pct:.1f}% > 50%)")
    score -= 5  # Severe penalty
    max_grade = "C"  # Cap grade
elif top10_pct > 35:
    red_flags.append(f"⚠️ HIGH CONCENTRATION ({top10_pct:.1f}% > 35%)")
    score -= 2

# Grade calculation with red flag impact
if len(red_flags) > 0:
    score -= len(red_flags) * 2  # Each red flag costs 2 points

# Final grade with caps
if score >= 17 and len(red_flags) == 0:
    grade = "A+ 🔥"
elif score >= 14 and len(red_flags) <= 1:
    grade = "A ✅"
elif score >= 10:
    grade = "B 🟡"
else:
    grade = "C ⚠️" if score >= 7 else "D ❌"
```

---

## Trading Implications

**Never enter:**
- Tokens < 1 hour old
- Top 10% > 50%
- Multiple red flags

**Wait for:**
- 2+ hour survivor checkpoint
- Stable holder distribution
- Volume confirmation (not just initial spike)

**Risk Management:**
- Even Grade A tokens can rug
- Position sizing: 0.5% max on new tokens
- Time stops: 30 minutes max on < 2h tokens

---

## Files Updated
- `memory/2026-03-19.md` - Daily log
- `memory/rug_analysis_2026-03-19.md` - This file
- `solana_alpha_hunter_v54.py` - Scanner improvements (pending)

---

*Documented by Lux after ALIENS/XTuber rug pulls*
