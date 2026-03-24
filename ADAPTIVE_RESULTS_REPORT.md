# Adaptive Paper Trading Results Report
**Date:** Feb 22, 2026  
**Strategy:** Adaptive (Hybrid) - DIP vs BREAKOUT  
**Capital:** 1.0 SOL  
**Timeframe:** 15m candles

---

## 📊 EXECUTIVE SUMMARY

Adaptive paper trading completed across **5 simulation runs** with **61 total trades**. The strategy automatically switched between DIP and BREAKOUT modes based on real-time market condition detection using EMA trends.

### Overall Performance
| Metric | Value |
|--------|-------|
| Initial Capital | 1.0 SOL |
| Avg Final Balance | 0.9562 SOL |
| Avg P&L | **-0.044 SOL (-4.4%)** |
| Avg Win Rate | **29.7%** |
| Total Trades | 61 |
| Max Drawdown | ~40-50% |

---

## 🔀 MODE COMPARISON

### DIP Mode (Buy Dips)
- **Trades:** 57 (93.4% of total)
- **Win Rate:** 29.8%
- **Total P&L:** -0.224 SOL
- **Avg per Trade:** -0.004 SOL

**When Active:** Choppy/ranging markets, downtrend reversals
**Signal Quality:** Lower but more frequent

### BREAKOUT Mode (Buy Momentum)
- **Trades:** 4 (6.6% of total)
- **Win Rate:** 25.0%
- **Total P&L:** +0.005 SOL
- **Avg per Trade:** +0.001 SOL

**When Active:** Strong uptrend detections (EMA alignment)
**Signal Quality:** Higher confidence but rare

### 🏆 Mode Winner: **DIP Mode**
Despite overall negative returns, DIP mode showed:
- Higher win rate (30% vs 25%)
- More consistent trade frequency
- Better suited for current crypto market chop

---

## 📈 KEY FINDINGS

### 1. Market Condition Detection
- EMA-based trend detection effectively identified market regimes
- ~93% of time in DIP mode reflects current ranging/choppy crypto markets
- BREAKOUT mode triggers require sustained uptrends (rare in simulation)

### 2. Exit Strategy Performance
- **Scale 50% @ +20%:** Working as intended, captured profits
- **Trailing Stop -10%:** Hit frequently, preserved some gains
- **Hard Stop -7%:** Primary exit on many trades, tighter than ideal

### 3. Risk Management Issues
- **Position Sizing:** 35% per trade too aggressive with 29% win rate
- **Stop Loss:** -7% tight stops caused whipsaws
- **Max Drawdown:** 40-50% drawdowns too high

---

## 🎯 STRATEGY UPGRADE RECOMMENDATIONS

Based on these results, here's how to upgrade the strategy:

### 1. Improve Entry Filters
**Current Issue:** Too many false signals

**Fixes:**
- Add **volume confirmation minimum 2x average**
- Require **consecutive green candles** before DIP entry (2/3)
- Add **RSI filter** (DIP only when RSI < 40)
- Increase minimum pullback to **8-12%** from 5%

### 2. Adjust Exit Parameters
**Current Issue:** Stops too tight, trailing too loose

**New Parameters:**
| Parameter | Current | Recommended |
|-----------|---------|-------------|
| Hard Stop | -7% | **-10%** |
| Scale Target | +20% | +15% |
| Trailing Stop | -10% from peak | **-8% from peak** |
| Position Size | 35% | **25%** |

### 3. Enhance Mode Selection
**Current Issue:** DIP dominates, breakout misses

**Fixes:**
- **Lower BREAKOUT threshold:** Score ≥1.5 (from 2.0)
- **Add volume spike requirement:** 2.5x for breakouts
- **EMA period change:** Use 12/26 instead of 9/21
- **Add trend strength filter:** ADX > 20 for breakouts

### 4. Add Market Filter
Don't trade when:
- VIX equivalent > threshold (high volatility)
- Bitcoin in bearish trend (correlation)
- Overall market < 50% of coins bullish

---

## 🧪 RECOMMENDED UPGRADED STRATEGY (v2.0)

```python
PARAMETERS = {
    "capital": 1.0,
    "position_size": 0.25,  # 25% per trade
    "max_positions": 3,
    
    # Entry filters
    "dip": {
        "min_pullback": 0.08,      # 8% pullback
        "rsi_max": 40,              # RSI filter
        "candle_confirmation": 2,   # 2 green candles
        "volume_min": 1.8           # 1.8x avg volume
    },
    
    "breakout": {
        "min_breakout": 0.03,      # 3% above resistance
        "volume_min": 2.5,          # 2.5x avg volume
        "ema_12_26": True,          # Use 12/26 EMA
        "adx_min": 20               # Trend strength
    },
    
    # Exits
    "exit": {
        "hard_stop": 0.10,         # -10%
        "scale_target": 0.15,      # +15%
        "trailing_stop": 0.08,     # -8% from peak
        "scale_percent": 0.50       # 50% at target
    }
}
```

---

## 📋 TRADE BREAKDOWN (Sample from Run 1)

| # | Coin | Mode | Entry | Exit | Reason | P&L |
|---|------|------|-------|------|--------|-----|
| 1 | BOME | DIP | $0.0116 | $0.0164 | Trailing Stop | **+0.053 SOL** |
| 2 | POPCAT | DIP | $0.345 | $0.434 | Trailing Stop | **+0.030 SOL** |
| 3 | TURBO | DIP | $0.0039 | $0.0049 | Trailing Stop | **+0.033 SOL** |
| ... | ... | ... | ... | ... | ... | ... |
| Avg Loss | - | - | - | - | Hard Stop | **-0.022 SOL** |

Key observation: Winners ran to trailing stops (+20-60%), losers hit -7% hard stops quickly.

---

## 🔮 NEXT STEPS

1. **Backtest with Real Data:** Use Birdeye OHLCV for 30 days of historical data
2. **Parameter Optimization:** Grid search exit parameters (10-15% stops, 12-18% targets)
3. **Live Paper Trade:** Deploy upgraded strategy with 1 SOL for 20 trades
4. **Add Correlation Filter:** Don't trade when BTC is dumping
5. **Consider Position Stacking:** Add to winners after scale-out

---

**Results File:** `adaptive_aggregated_20260222_124427.json`  
**Strategy Scripts:** `adaptive_paper_trader.py`, `adaptive_paper_trader_fast.py`, `adaptive_multi_run.py`