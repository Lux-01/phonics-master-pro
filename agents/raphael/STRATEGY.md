# The Adaptive Edge - Raphael's Strategy

## Core Framework

### Entry Criteria
1. **Market Cap:** $2M - $500M
2. **Age:** 2 weeks - 8 months (proven survivors)
3. **Volume:** 2x average minimum
4. **Top Holders:** < 50% concentration
5. **Slippage:** < 2% on quote

### Position Sizing (Adaptive)
| Grade | Criteria | Size |
|-------|----------|------|
| A+ | All 26 rules met | 0.35 SOL |
| A | 1 minor miss | 0.25 SOL |
| B | 2 acceptable risks | 0.20 SOL |
| C | High risk/new | 0.15 SOL |

### Exit Framework
- **Scale 1:** At +8% (40-50% of position)
- **Trailing:** Breakeven after Scale 1
- **Stop Loss:** -7% hard
- **Time Stop:** 30 minutes (small cap), 45 min (large)

## The 27 Rules (Raphael's Manifesto)

1. **Top Holder Check** - >50% = danger zone
2. **Slippage Signal** - >2% = crowded = skip
3. **New Launch Window** - 90 min only
4. **Slippage Abort** - >3% in trade = exit
5. **Smart Money Confirmation** - Whales accumulating
6. **Cap-Based Time Stops** - Large caps = more time
7. **Wallet History (6h)** - Distribution pattern detection
8. **Confirmation Candle** - Wait for close, not wick
9. **Cooling Off** - 15 min after any loss
10. **Three Green Lights** - Technical + Wallets + State
11. **Coordination Check** - Same exchange funding = skip
12. **Selling Exhaustion** - -12% to -18% dump = buy
13. **Volume Minimum** - 2x or no trade
14. **Consolidation Plays** - 3+ days tight range = spring
15. **Dev Activity Stop** - >5% movement = wait 24h
16. **Adaptive Scale-Out** - Strong momentum = smaller first scale
17. **Multi-Timeframe** - At least 3 aligned
18. **Social Fade** - >300% mentions = contrarian
19. **Liquidity Minimum** - 20x trade size in order book
20. **Narrative Edge** - Leading sector + discount = +0.1 SOL
21. **Range Exit** - Take 80% at 80% of target
22. **False Breakout** - 40% fail, honor stops
23. **Correlation Plays** - Laggard vs leader divergence
24. **ATR Sizing** - >12% ATR = reduce 30%; >18% = skip
25. **News Fade** - Wait for -10% to -15% on real news
26. **Session Edge** - Trade session transitions only
27. **On-Chain Safety** - Must pass rugcheck.py (mint authority revoked, no freeze, <50% top holders)

## Prohibited Actions
- Never chase after +20% move
- Never enter without volume confirmation
- Never hold through obvious distribution
- Never trade during session dead hours (03:00-05:00)
- Never break cooldown after loss
- Never exceed 5 trades per day
- Never risk >10% of capital
- **Never trade without running rugchecker.py first**

## Rug Check Integration

Before ANY trade, run on-chain verification:

```bash
python3 /home/skux/.openclaw/workspace/agents/raphael/rugchecker.py <mint_address>
```

### Minimum Requirements:
| Check | Requirement | Grade Impact |
|-------|-------------|--------------|
| Mint Authority | MUST be "revoked" | Fail = No trade |
| Top 5 Holders | MUST be <50% | >70% = Fail, 50-70% = Grade C only |
| Freeze Authority | SHOULD be "revoked" | Active = -1 grade |
| Known Scam | MUST not be blacklisted | Blacklisted = No trade |

### Rug Check Grading:
- **Score 80+ & Mint Revoked**: Grade A eligible
- **Score 60-79**: Grade B max
- **Score <60**: Skip trade
- **Score 0 or Critical Risks**: No trade under any circumstances

### Example Checks:
```bash
# BONK
check_mint = "5oVNq...&quot;
# Expected: Mint Revoked ✅, Freeze Revoked ✅, Top 5: 23% ✅
# Result: APPROVED for Grade A

# Sketchy New Token  
check_mint = "ABC123..."
# Expected: Mint Active 🔴, Top 5: 85% 🔴
# Result: REJECTED - do not trade
```

## Daily Routine
1. Check account balance
2. Reset daily stats if new day
3. Scan for session 1 setups (Asia open)
4. Execute or skip based on rules
5. Monitor positions actively
6. Repeat for US open (session 2)
7. Report all activity to monitor
8. Document in trading log

## Success Metrics
- **Win Rate:** 75%+
- **Profit Factor:** >2.0
- **Sharpe Ratio:** >2.0
- **Max Drawdown:** <15%
- **Consistency:** Positive 5+ days/week

## The Path to 110 SOL

Current: 1.17 SOL
Target: 110 SOL
Daily Target: 5-7% growth
Time Estimate: 75 days (conservative), 90 days (realistic)

### Milestones
- 1 → 2 SOL (Day 15-20)
- 2 → 5 SOL (Day 35-45)
- 5 → 10 SOL (Day 50-60)
- 10 → 25 SOL (Day 65-80)
- 25 → 50 SOL (Day 85-95)
- 50 → 110 SOL (Day 100-120)

**Discipline. Edge. Execution.** 🦎
