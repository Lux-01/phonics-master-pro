# 🚨 RAPHAEL LIVE TEST PROTOCOL v3.0
**Status:** READY FOR DEPLOYMENT  
**Date:** 2026-02-23  
**Version:** 3.0 (Post-Backtest Validation)

---

## ✅ Prerequisites COMPLETED

| Requirement | Status |
|-------------|--------|
| February Backtest (21 days) | ✅ +184.7%, 78% win rate |
| January Backtest (31 days) | ✅ +212%, 81.7% win rate |
| 40 Rules System | ✅ Documented |
| Grade C Elimination | ✅ Validated (-27% better performance) |
| Emergency Stop | ✅ Built into monitor |
| Watchdog Respawn | ✅ Cron job active (every 5 min) |
| Rug Check Integration | ✅ 100/100 score for BONK/JUP |

---

## 🎯 LIVE TEST PHASE 1: 0.01 SOL Validation

### Objective
Validate live execution with real money before scaling to full Phase 2 sizing.

### Parameters
| Setting | Value |
|---------|-------|
| **Max Trade Size** | 0.01 SOL (~$1.50-2.00) |
| **Number of Trades** | Minimum 5, Maximum 10 |
| **Grade Filter** | A+ and A only (no B for live test) |
| **Max Daily Loss** | 0.02 SOL (2% of test capital) |
| **Session** | Wait for US market hours only |
| **Duration** | 2-3 days or 5+ trades |

### Execution Checklist

#### Before Each Trade
```bash
# 1. Check emergency stop status
curl -s http://localhost:3456/api/status | jq '.emergencyStop'

# 2. Rug check the token
bash check_before_trade.sh TOKEN MINT

# 3. Verify wallet has funds
solana balance --url https://api.mainnet-beta.solana.com

# 4. Confirm trade size <= 0.01 SOL
```

#### Trade Execution Flow
```
1. ✅ Emergency stop NOT triggered
2. ✅ Rug check PASSED (Score >= 70)
3. ✅ Setup is Grade A+ or A
4. ✅ Slippage quote < 1.5%
5. ✅ Time stop acceptable (30-45 min)
6. ✅ Execute via Jupiter
7. ✅ Log transaction signature
8. ✅ Update monitor
9. ✅ Verify entry in wallet
```

### Live Test Success Criteria

| Metric | Pass Criteria |
|--------|---------------|
| **Win Rate** | ≥60% (3/5 trades) |
| **Total PNL** | ≥-10% (acceptable drawdown) |
| **Slippage** | ≤2% average (vs 1-2% expected) |
| **Failed Transactions** | ≤20% of attempts |
| **Emergency Stop Test** | ✅ Verified working |
| **Log Accuracy** | 100% of trades logged |

---

## 🚨 EMERGENCY STOP PROCEDURE

### How to Trigger
```bash
# Method 1: Dashboard Button
1. Open http://localhost:3456
2. Click RED "⚠️ EMERGENCY STOP ⚠️" button
3. Confirm in popup

# Method 2: API Call
curl -X POST http://localhost:3456/api/emergency-stop

# Method 3: Manual File Create
touch /tmp/raphael_emergency_stop
```

### What Happens
1. ✅ Raphael STOPS entering new positions immediately
2. ✅ Existing positions held (manual exit required)
3. ✅ Dashboard shows "TRADING HALTED"
4. ✅ Emergency status logged
5. ✅ You receive notification

### How to Resume
```bash
# 1. Review why stop was triggered
# 2. Fix the issue
# 3. Manually remove stop file
rm /tmp/raphael_emergency_stop

# 4. Restart Raphael session if needed
# 5. Click "Resume Trading" in dashboard
```

---

## 📋 Test Trade Template

### Trade #1: [TOKEN NAME]

**Setup**
- Date: YYYY-MM-DD HH:MM
- Token: [SYMBOL]
- Mint: [ADDRESS]
- Grade: [A+/A/B/C]
- Setup Type: [Exhaustion/Breakout/Mean Reversion]

**Pre-Trade Checks**
- [ ] Emergency stop: NOT triggered
- [ ] Rug check: Score ___/100
- [ ] Mint authority: ___
- [ ] Top holders: ___%
- [ ] Price action: [Describe]
- [ ] Volume: ___x average
- [ ] RSI: ___ (if applicable)

**Execution**
- Entry Price: $_____
- Size: ____ SOL
- Target: +8% or 15% (A+)
- Stop: -7%
- Time stop: ___ min
- Slippage quoted: ___%
- Actual slippage: ___%
- Tx Signature: ________

**Result**
- Exit Price: $_____
- Exit Type: [Target/Stop/Time/Manual]
- PNL %: ___%
- PNL SOL: +/- _____
- Duration: ___ min
- Grade Accuracy: [Was assigned grade correct?]
- Lessons: ___________

---

## 🔄 Scaling Plan

### Phase 1: Live Test (Current - Starting)
- **When:** Now
- **Size:** 0.01 SOL max
- **Trades:** 5-10
- **Target:** Validate execution, slippage, wallet
- **Duration:** 2-3 days
- **Success Criteria:** 60% win rate, ≤-10% drawdown

### Phase 2: Micro Scale
- **When:** After Phase 1 success
- **Size:** 0.05 SOL max
- **Trades:** 10-20
- **Target:** Stress test with real conditions
- **Duration:** 1 week

### Phase 3: Graduated Scale
- **When:** After Phase 2 success
- **Size:** 0.10-0.15 SOL
- **Target:** Transition to Phase 2 sizing slowly
- **Duration:** 1-2 weeks

### Phase 4: Full Phase 2
- **When:** After 20+ successful live trades
- **Size:** Phase 2 sizing (0.35-0.50 SOL for A+)
- **Target:** Full deployment
- **Duration:** Ongoing

---

## 📊 Live Test Monitoring

### Dashboard Features
- 🟢/🔴 Status light for Raphael
- 🚨 Emergency stop button
- 📊 Real-time PNL tracking
- 📝 Position logging with tx signatures
- 📈 Win rate and stats
- ⏱️ Trade duration tracking

### Daily Check-Ins
**Morning:**
1. Check emergency stop status
2. Review overnight positions (if any)
3. Confirm wallet balance
4. Set daily loss limit (0.02 SOL)

**After Each Trade:**
1. Log in template (above)
2. Verify tx on Solscan
3. Update monitor
4. Check slippage vs expected

**Evening:**
1. Review day's trades
2. Compare to backtest expectations
3. Document lessons learned
4. Plan next day's approach

---

## ⚠️ Stop Conditions

### Immediate Halt Required
- [ ] Emergency stop triggered
- [ ] Two consecutive losses (circuit breaker)
- [ ] Slippage >3% on entry
- [ ] Failed transaction >50% of attempts
- [ ] Wallet balance discrepancy
- [ ] Unexpected error in logs
- [ ] Human override (your intuition)

### Pause for Investigation
- [ ] Grade A trade loses unexpectedly
- [ ] Slippage consistently >2%
- [ ] Jupiter API errors
- [ ] Network congestion for >30 min
- [ ] Monitor goes offline >5 min

---

## 🎯 Success Metrics

### Minimum Viable Live Test
| Metric | Target |
|--------|--------|
| Trades | 5+ |
| Win Rate | ≥60% |
| Total PNL | ≥-10% (acceptable) |
| Slippage Avg | ≤2% |
| Failed Tx | ≤20% |
| Emergency Stop | ✅ Tested |

### Excellent Live Test
| Metric | Target |
|--------|--------|
| Trades | 10+ |
| Win Rate | ≥70% |
| Total PNL | >0% (profitable) |
| Slippage Avg | ≤1.5% |
| Failed Tx | ≤10% |
| All Grades Accurate | ✅ |

---

## 📝 Documentation Required

Each live test trade needs:
1. ✅ Pre-trade setup photo/screenshot
2. ✅ Tx signature
3. ✅ Pre-trade checklist completed
4. ✅ Post-trade summary
5. ✅ Slippage analysis
6. ✅ Grade accuracy assessment
7. ✅ Any deviations logged

Store in: `/solana-trader/live_test_logs/`

---

## 🚀 START SEQUENCE

```bash
# 1. Start monitor (fresh, zeroed)
bash /home/skux/.openclaw/workspace/start_monitor_v3.sh

# 2. Verify emergency stop not triggered
curl -s http://localhost:3456/api/status | jq '.emergencyStop'
# Expected: false

# 3. Verify watchdog running
cron status | grep raphael-watchdog
# Expected: active

# 4. Confirm wallet has 0.05+ SOL
solana balance

# 5. Open dashboard
open http://localhost:3456

# 6. Click "Start Live Test" button

# 7. Wait for Grade A+ or A setup

# 8. Execute first 0.01 SOL trade

# 9. Document everything
```

---

## 📞 Support

**Emergency Contacts:**
- Emergency Stop: http://localhost:3456 → Red Button
- Kill Monitor: `pgrep -f monitor_v3.py | xargs kill -9`
- Check Logs: `tail -f /tmp/raphael_monitor.log`

**Status Check:**
```bash
# Is Raphael running?
sessions_list | grep raphael

# Is emergency stop active?
test -f /tmp/raphael_emergency_stop && echo "STOPPED" || echo "ACTIVE"

# Is monitor running?
curl -s http://localhost:3456/api/status | jq '{emergencyStop, balance, trades: .totalTrades}'
```

---

## ✅ FINAL CHECKLIST

Before Starting Live Test:

- [ ] Emergency stop button tested (click it, verify works, then remove)
- [ ] Monitor dashboard open at http://localhost:3456
- [ ] Watchdog cron job confirmed active
- [ ] Wallet funded with 0.05+ SOL
- [ ] Rug checker tested on BONK/JUP
- [ ] Trade template ready
- [ ] Daily loss limit set (0.02 SOL)
- [ ] 40 rules reviewed
- [ ] Grade C confirmed eliminated
- [ ] You are ready mentally

---

**Ready to Start:** Run the start sequence above  
**Emergency:** Red button in dashboard or `touch /tmp/raphael_emergency_stop`  
**Confidence Level:** 9.2/10 → 10/10 after 5 successful live trades

**LET'S GO LIVE** 🚀
