# Solana Alpha Hunter - Updated Scan Template (with Wallet Clustering)

## Updated Daily Scan Format - Market Cap + Clustering Focus

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

**4. NEW: Wallet Clustering Section (🫧):**
```
🫧 WALLET CLUSTERING ANALYSIS:
  Graph Insiders Detected: [0]
  Insider Networks: [count]
  Top Whale: [X%]
  Whale Concentration (>2%): [count] wallets holding [X%]
  
  🚩 RED FLAGS:
  - Top whale >50% = SKIP
  - <200 holders = CAUTION
  - Insider networks >0 = AVOID
  
  Risk Score: [0-10]
  Verdict: [✅ CLEAN / 🟡 LOW RISK / 🟠 CAUTION / 🔴 AVOID]
```

**5. 2X Potential (Market Cap Based):**
```
💡 2X TARGET ANALYSIS:
  Current MCAP: $XX,XXX
  2X Target: $XXX,XXX MCAP
  5X Target: $XXX,XXX MCAP
  Likelihood: HIGH/MEDIUM/LOW
```

**6. Security Section:**
```
🔒 SECURITY CHECKS:
  Mint: Revoked ✅
  Freeze: Revoked ✅
  LP Lock: XX% ✅
  Top 10: XX.X% ✅
  Risk Score: XXX/100
```

**7. Comparison Table (If Rescan):**
```
📉 COMPARISON TO PREVIOUS SCAN:
  Metric        | Before     | Now        | Change
  --------------|------------|------------|------------
  Market Cap    | $XXX,XXX   | $XXX,XXX   | +/- XX%
  Liquidity     | $XX,XXX    | $XX,XXX    | +/- XX%
  5m Volume     | $XX,XXX    | $XX,XXX    | +/- XX%
  Holders       | XXX        | XXX        | +/- X
  Cluster Risk  | X/10       | X/10       | +/- X
```

**8. Final Verdict:**
```
🎯 VERDICT:
  X/7 Criteria Passed
  - MCAP <$250K: ✅
  - Liq >$15K: ✅
  - 5m Vol >$5K: ✅
  - Mint Revoked: ✅
  - LP Locked: ✅
  - Top 10 <30%: ✅
  - Cluster Risk <3/10: ✅
  
  Entry Zone: $XXX,XXX - $XXX,XXX MCAP
  2X Target: $XXX,XXX MCAP
  Stop: $XXX,XXX MCAP (-25%)
```

## Updated Criteria (7 Total)

| # | Criteria | Threshold | Check Via |
|---|----------|-----------|-----------|
| 1 | Market Cap | <$250,000 | Dex Screener |
| 2 | Liquidity | >$15,000 | Dex Screener |
| 3 | 5m Volume | >$5,000 | Dex Screener |
| 4 | Mint Revoked | Yes | RugCheck API |
| 5 | LP Locked | 100% | RugCheck API |
| 6 | Top 10 <30% | Yes | RugCheck API |
| 7 | **Cluster Risk** | **<3/10** | **RugCheck (holders + networks)** |

## Cluster Risk Scoring

| Risk Factor | Points | Detection Method |
|-------------|--------|----------------|
| Insider Networks | +2 each | RugCheck `insiderNetworks` |
| Graph Insiders | +1 | RugCheck `graphInsidersDetected` |
| Bundle Patterns | +1 | Heuristic: similar amounts |
| Whale >50% | +3 | Top holder analysis |
| Low Holders (<200) | +1 | RugCheck `totalHolders` |

**Verdict Scale:**
- **0 = ✅ CLEAN** - Safe to ape
- **1-3 = 🟡 LOW RISK** - Proceed with caution
- **4-6 = 🟠 CAUTION** - Higher risk, smaller position
- **7+ = 🔴 AVOID** - Bundled/insider play

## Implementation Notes

**APIs Used:**
- Dex Screener: Market data, volume, liquidity
- RugCheck: Security + wallet clustering (holders, networks, insiders)

**Manual Verification:**
- Bubble Maps: https://app.bubblemaps.io/token/solana/[CA] (for visual confirmation)

## Example Output

```
🎯 ALPHA ALERT: LUMO ($Lumo)
CA: 7Uhq9sPuWRGVFHB4tQztEcqh6tbLJu2GqXaeQJS8pump

📊 MARKET CAP METRICS:
  Current MCAP: $94,366 ← PRIMARY METRIC
  Liquidity: $17,882 (18.9% of MCAP)
  LP Locked: 100%

📈 VOLUME MOMENTUM:
  5m: $7,061 | 1h: $101,074 | 24h: $101,074
  Rising Wedge: ➡️ Stable

🫧 WALLET CLUSTERING:
  Graph Insiders: 0 ✅
  Insider Networks: 0 ✅
  Top Whale: 14.5% ✅
  Whales (>2%): 4 holding 21.0%
  Risk Score: 0/10 ✅ CLEAN

💡 2X TARGET:
  Current: $94,366 MCAP
  2X: $188,732 MCAP
  Likelihood: MEDIUM

🔒 SECURITY:
  Mint: Revoked ✅ | Freeze: Revoked ✅ | LP: 100% ✅

🎯 VERDICT: 7/7 Passed ✅
Entry: $94K MCAP | 2X: $189K | Stop: $71K
```

---
Updated: 2026-02-15
Includes: Wallet clustering analysis
