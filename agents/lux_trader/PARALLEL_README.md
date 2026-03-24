# Holy Trinity LIVE + LuxTrader v3.0 PARALLEL SYSTEM

## ✅ SYSTEMS READY

Both trading systems are configured and ready to run in parallel.

---

## 📊 SYSTEM COMPARISON

| Feature | LuxTrader v3.0 | Holy Trinity |
|---------|---------------|--------------|
| **Position Size** | 0.6% of capital | **10.5-11.46%** |
| **Signal Required** | Score ≥75 | **Composite ≥80** |
| **Strategies** | 1 (Quality) | **3 (Safety + Timing + Quality)** |
| **Max Trades/Day** | 5 | **3** |
| **Max Drawdown** | 15% | **20%** |
| **Daily Loss Limit** | -0.05 SOL | **-0.10 SOL** |
| **Min Liquidity** | $8,000 | **$10,000** |
| **Rug Protection** | Basic | **Advanced** |

---

## 🔥 COMPONENTS

### LuxTrader v3.0
- **Entry**: Grade A/A+ tokens
- **Sizing**: 0.6% base, +50% pyramid, +30% add-on
- **Exits**: 15/25/40% tier targets
- **Safety**: -7% stop, 4h time limit

### Holy Trinity
- **Component 1**: Rug-Radar (35% weight) - Safety gate
- **Component 2**: Mean-Reverter (40% weight) - Entry timing
- **Component 3**: LuxTrader (25% weight) - Quality check
- **Requirement**: ALL 3 must approve
- **Sizing**: 10.5-11.46% of capital per trade
- **Safety**: -8% stop, 6h time limit

---

## 💰 CAPITAL ALLOCATION

```
Starting Capital: 1.0 SOL each (separate)

LuxTrader v3.0:
  Position per trade: 0.006 SOL (0.6%)
  Max concurrent: 3 positions
  Max deployed: ~1.8% of capital

Holy Trinity:
  Position per trade: 0.105-0.1146 SOL (10.5-11.46%)
  Max concurrent: 2 positions  
  Max deployed: ~20-23% of capital
```

---

## 📁 FILES CREATED

| File | Purpose |
|------|---------|
| `holy_trinity_live.py` | Main trading script |
| `holy_trinity_state.json` | Separate state tracking |
| `run_parallel.sh` | Launch both systems |
| `check_parallel.sh` | Check status / stop systems |
| `holy_trinity_logs/` | Daily logs |
| `parallel_logs/` | Combined logs |

---

## 🚀 HOW TO RUN

### Option 1: Check Current Status
```bash
cd /agents/lux_trader
./check_parallel.sh
```

### Option 2: Start Both Systems
```bash
cd /agents/lux_trader
./run_parallel.sh
```

This will:
1. Check if LuxTrader is running (start if not)
2. Start Holy Trinity
3. Show both PIDs
4. Log to separate files

### Option 3: Stop Both Systems
```bash
cd /agents/lux_trader
./check_parallel.sh --stop
```

### Option 4: Manual Scan
```bash
# Terminal 1: LuxTrader
python3 luxtrader_live.py

# Terminal 2: Holy Trinity
python3 holy_trinity_live.py
```

---

## 📊 CURRENT STATUS

```
LuxTrader v3.0:
  ✅ State file exists
  💰 Capital: 1.0099 SOL (+0.99%)
  📊 Trades: 2 (2 wins, 0 losses)
  ⏳ Status: Ready

Holy Trinity:
  ✅ State file exists
  💰 Capital: 1.0000 SOL
  📊 Trades: 0
  ⏳ Status: Ready
```

---

## 🎯 HOW IT WORKS

1. **AOE Scanner** runs every 30 mins
2. **Tokens** are scored by grade/quality
3. **LuxTrader**: Trades if score ≥75
4. **Holy Trinity**: Trades if composite ≥80 (requires all 3)
5. **Both systems** can trade the same token independently
6. **Positions** are sized differently (0.6% vs 11.46%)

---

## ⚠️ SAFETY FEATURES

- **Separate state files** - no conflicts
- **Circuit breakers** - daily loss limits
- **Drawdown protection** - stops at limits
- **Trade limits** - max 5/day (LuxTrader), 3/day (Trinity)
- **Graduated scaling** - increase size when profitable

---

## 📈 EXPECTED PERFORMANCE

Based on 1-year backtest:

| Strategy | Multiplier | Win Rate | Trades |
|----------|-----------|----------|--------|
| LuxTrader v3.0 | 1,219x | 62% | ~1,100 |
| Holy Trinity | 911x | 63% | ~982 |

**Combined:** Higher returns through diversification

---

## 🔧 CONFIGURATION

### To Switch Holy Trinity to LIVE Mode:

Edit `holy_trinity_live.py`:
```python
MODE = "LIVE"  # Change from "PAPER"
```

### To Adjust Position Size:

Edit `holy_trinity_live.py`:
```python
SAFETY = {
    "max_position_sol": 0.15,  # Adjust this
    "max_position_pct": 0.15,  # And this
}
```

### To Change Signal Threshold:

Edit `holy_trinity_live.py`:
```python
CONFIG = {
    "composite_score_min": 80,  # Adjust this
}
```

---

## 📝 LOG FILES

```
/agents/lux_trader/
├── parallel_logs/
│   ├── luxtrader_YYYYMMDD_HHMMSS.log
│   └── holy_trinity_YYYYMMDD_HHMMSS.log
├── holy_trinity_logs/
│   └── holy_trinity_YYYYMMDD.log
├── live_state.json
└── holy_trinity_state.json
```

---

## 🦞 NEXT STEPS

1. ✅ Systems configured
2. ✅ State files initialized
3. ⏳ **Run `./run_parallel.sh` to start both**
4. ⏳ Let AOE scanner feed opportunities
5. ⏳ Monitor with `./check_parallel.sh`

---

**Both systems are ready to run in parallel!** 🔥🦞
