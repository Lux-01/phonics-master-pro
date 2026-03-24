# LuxTrader v1.0 - Self-Learning Paper Trading System
## ACA Plan (Autonomous Code Architect)

---

## 1. REQUIREMENTS GATHERING

**Goal:** Build a trading system that:
- Starts with minimal/naive strategy
- Paper trades (no real money)
- Records outcome of every trade
- Automatically extracts patterns from wins/losses
- Evolves strategy parameters based on learnings
- A/B tests new rules against historical performance

**Success Metrics:**
- Win rate improves over time
- Clear learning rules emerge
- Strategy file auto-updates
- Paper P&L tracked

**Inputs:**
- AOE high-score tokens (≥75)
- Real-time price data (Birdeye/DexScreener)
- Historical trade outcomes

**Outputs:**
- Trade decisions (buy/sell/hold)
- Learning log with patterns
- Updated strategy config
- Performance dashboard

---

## 2. ARCHITECTURE DESIGN

```
┌─────────────────────────────────────────┐
│  LuxTrader Main Loop                    │
│  (Runs every 30 mins via cron)          │
└──────────────────┬──────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐    ┌───▼────┐   ┌────▼────┐
│ Signal │    │ Price  │   │ Learn   │
│ Check  │    │ Monitor│   │ Engine  │
└───┬────┘    └───┬────┘   └────┬────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
          ┌───────▼────────┐
          │ Trade Executor │
          │ (Paper Mode)   │
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Outcome Logger │
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Pattern Extract│
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Update Strategy│
          └────────────────┘
```

---

## 3. DATA FLOW PLANNING

### Trade Flow
1. **Discovery:** Get tokens from AOE (score ≥75)
2. **Evaluation:** Apply current strategy rules
3. **Entry:** Paper buy @ current price
4. **Monitor:** Track price every 5 mins
5. **Exit:** Hit TP/SL/Time limit → Paper sell
6. **Log:** Record full trade outcome
7. **Learn:** Extract patterns from result
8. **Evolve:** Update strategy config

### Data Storage
```
/agents/lux_trader/
├── strategy.json          # Current rules (auto-updated)
├── trades.json            # All trade history
├── learning_log.json      # Patterns extracted
├── paper_portfolio.json   # Current positions
└── performance.json       # Win rate, P&L, stats
```

---

## 4. EDGE CASE IDENTIFICATION

| Edge Case | Handling |
|-----------|----------|
| No tokens ≥75 | Skip cycle, log "no signals" |
| Price API fails | Use cached, flag for retry |
| Position already exists | Skip duplicate token |
| Token rugs (price → 0) | Mark as "rug" loss, special rule |
| Max positions reached | Queue or skip |
| TP and SL hit simultaneously | Check which came first |
| Time stop while pumping | Extend if strong momentum? |
| Learning log too big | Archive old entries monthly |
| Invalid strategy update | Rollback to last valid |

---

## 5. TOOL CONSTRAINTS ANALYSIS

**Available APIs:**
- Birdeye: Price, OHLCV, token metadata
- DexScreener: Pair data, volume
- Jupiter: Quote/swap (for paper calc)
- Helius: Transaction data

**Rate Limits:**
- Birdeye: ~100 req/min (be careful)
- Need caching between checks

**Time Constraints:**
- 30 min cron cycle
- Price checks every 5 mins when in position
- Must complete within timeout

---

## 6. ERROR HANDLING STRATEGY

| Error Type | Response |
|------------|----------|
| API timeout | Retry 3x with backoff, use last known price |
| JSON parse error | Log corrupt file, use backup |
| Insufficient data | Skip token, don't trade |
| Division by zero (volatility) | Default to conservative value |
| Invalid strategy config | Load defaults, alert user |
| Disk full | Critical alert, stop trading |

---

## 7. TESTING PLAN

### Unit Tests
1. Signal scoring with known tokens
2. Entry/exit logic with mock prices
3. Pattern extraction from mock trades
4. Strategy evolution with synthetic data

### Integration Tests
1. Full paper trade cycle (buy → monitor → sell)
2. Learning from 10 mock trades
3. Strategy update propagation

### Validation
1. Verify no real SOL spent
2. Check all trades logged
3. Confirm strategy file updates
4. Validate win rate calculation

---

## INITIAL STRATEGY (v0.1 - Naive)

Start simple, let learning improve it:

```json
{
  "version": "0.1",
  "max_positions": 3,
  "position_size_sol": 0.01,
  "target_profit": 0.15,
  "stop_loss": 0.07,
  "time_stop_minutes": 240,
  "filters": {
    "min_liquidity": 5000,
    "max_age_hours": 24,
    "min_score": 75
  }
}
```

Then learn:
- Which age ranges win most
- Which market caps perform
- Which volume patterns predict pumps
- Optimal TP/SL levels

---

## NEXT STEPS

1. ✅ Create directory structure
2. ✅ Build core trader class
3. ✅ Implement paper trading logic
4. ✅ Build learning engine
5. ✅ Create strategy evolution
6. ✅ Add cron job
7. ✅ Monitor first 10 trades

**Estimated:** 2-3 hours to MVP
