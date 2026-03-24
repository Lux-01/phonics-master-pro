# Solana Alpha Hunter - Scan Template

This file contains the updated scan template for daily alpha hunting.

## Updated Output Format (Market Cap Focus)

### For Each Candidate, Report:

**1. Header Section:**
```
🎯 ALPHA ALERT: TokenName ($SYMBOL)
CA: [full_contract_address]
```

**2. Market Cap Section (PRIMARY FOCUS):**
```
📊 MARKET CAP METRICS:
  Current MCAP: $XXX,XXX  ← LEAD WITH THIS
  Liquidity: $XX,XXX (XX% of MCAP)
  LP Locked: XX%
  FDV: $XXX,XXX (if different from MCAP)
```

**3. Volume Section:**
```
📈 VOLUME MOMENTUM:
  5m: $XX,XXX  |  1h: $XXX,XXX  |  24h: $XXX,XXX
  Rising Wedge: YES/NO
  Vol/MCAP Ratio: X.Xx
```

**4. 2X Potential (Market Cap Based):**
```
💡 2X TARGET ANALYSIS:
  Current MCAP: $XX,XXX
  2X Target: $XXX,XXX MCAP
  5X Target: $XXX,XXX MCAP
  Likelihood: HIGH/MEDIUM/LOW
```

**5. Security Section:**
```
🔒 SECURITY CHECKS:
  Mint: Revoked ✅
  Freeze: Revoked ✅
  LP Lock: XX% ✅
  Top 10: XX.X% ✅
  Risk Score: XXX/100
```

**6. Comparison Table (If Rescan):**
```
📉 COMPARISON TO PREVIOUS SCAN:
  Metric        | Before     | Now        | Change
  --------------|------------|------------|------------
  Market Cap    | $XXX,XXX   | $XXX,XXX   | +/- XX%
  Liquidity     | $XX,XXX    | $XX,XXX    | +/- XX%
  5m Volume     | $XX,XXX    | $XX,XXX    | +/- XX%
  Holders       | XXX        | XXX        | +/- X
```

**7. Final Verdict:**
```
🎯 VERDICT:
  X/6 Criteria Passed
  Entry Zone: $XXX,XXX - $XXX,XXX MCAP
  Target: $XXX,XXX MCAP (2X)
  Stop: $XXX,XXX MCAP (-25%)
```

## Why Market Cap Instead of Price?

- **Price is misleading** - varies wildly with decimals (0.000001 vs 0.5)
- **Market cap is universal** - easy to compare across tokens
- **2X math is simple** - $50K → $100K is clear
- **Risk assessment** - $250K MCAP cap is concrete
- **Liquidity context** - Liq/MCAP ratio matters more than price

## Cron Job Settings

- **Job ID:** 7cba3029-67ba-4992-a863-f84be9332ff0
- **Schedule:** Daily at 2:00 PM AEST
- **Output:** Market-cap focused reports
- **Next Run:** Tomorrow 2:00 PM

---
Updated: 2026-02-15
Requested by: User
