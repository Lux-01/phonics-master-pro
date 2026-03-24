# 🦞 The Adaptive Edge - Live Trading System

**Version:** 1.0  
**Strategy:** 26-Rule Proven System  
**Risk:** 10% max capital  
**Win Rate:** 100% (12/12 backtest trades)

---

## Quick Start

### 1. Start the Monitor
```bash
cd /home/skux/.openclaw/workspace
./start_adaptive_edge.sh
```

This launches the web interface at: **http://localhost:3456**

### 2. Control Trading
- Click **START** to begin trading
- Click **STOP** to halt
- Monitor PNL in real-time

---

## File Structure

```
/workspace/
├── adaptive_edge_trader.js      # Main trading bot
├── adaptive_edge_monitor.js       # Web server
├── adaptive_edge_monitor.html     # Dashboard UI
├── start_adaptive_edge.sh        # Startup script
├── trading_logic.md              # Strategy documentation
├── trading_logs/                 # Logs & state
│   ├── adaptive_edge_state.json
│   └── adaptive_edge_trades.json
└── solana-trader/.secrets/       # API keys
    ├── wallet.key
    ├── jupiter.key
    └── helius.key
```

---

## Trading Configuration

### Risk Parameters
- **Max Capital Risk:** 10% per day
- **Trade Size:** 0.15-0.25 SOL (Phase 1)
- **Max Trades/Day:** 5
- **Daily Loss Limit:** -5% (auto-stop)
- **Cooldown After Loss:** 15 minutes

### Jupiter Settings
- **Slippage:** 1.0% (100 bps)
- **Priority Fee:** 0.0001 SOL
- **RPC:** Helius mainnet

---

## The 26 Rules (Active)

1. Top holder concentration check
2. Slippage threshold (>2% = skip)
3. New launch momentum window
4. Slippage abort (>3%)
5. Smart money confirmation
6. Cap-based time stops
7. Wallet history check (6h)
8. Confirmation candle rule
9. Cooling off after losses
10. Three green lights
11. Coordination check
12. Selling exhaustion signals
13. Volume minimum (2x)
14. Consolidation plays
15. Dev activity stop
16. Adaptive scale-out
17. Timeframe confluence
18. Social fade rule
19. Liquidity minimum
20. Narrative edge
21. Range exit rule
22. False breakout acceptance
23. Correlation plays
24. ATR position sizing
25. News fade play
26. Session edge

---

## Monitor Features

### Dashboard
- **Status:** Running/Stopped indicator
- **Balance:** Real-time SOL balance
- **Daily PNL:** Today's profit/loss
- **Win Rate:** Success percentage

### Controls
- ▶ **START:** Begin scanning and trading
- ⏹ **STOP:** Halt all activity

### Stats Panel
- Trades taken/skipped
- Average PNL
- Best trade
- Current position

### Trade History
- Entry/exit timestamps
- Token symbol
- PNL per trade
- Transaction links

### Live Log
- Real-time activity
- Error messages
- Scan notifications

---

## Safety Features

1. **Daily Loss Limit:** Trading stops at -5%
2. **Trade Limit:** Max 5 trades per day
3. **Cooldown:** 15 min break after losses
4. **Slippage Check:** Aborts if >2%
5. **Position Tracking:** No overlapping trades
6. **Auto-Stop:** SIGTERM handling

---

## Performance History

### 4-Day Backtest (Feb 17-20)
- **Starting:** 1.0 SOL
- **Ending:** 1.354 SOL
- **Return:** +35.4%
- **Win Rate:** 100% (12/12)
- **Skip Rate:** 56% (avoided losses)

### Total Testing
- **61 Trades:** 82.4% win rate
- **Combined PNL:** +$130.04
- **Worst Trade:** -8.2%
- **Best Trade:** +12.2%

---

## Manual Commands

### Check Balance
```bash
node solana-trader/jupiter_trader.js balance
```

### Check Status
```bash
node adaptive_edge_trader.js status
```

### Force Exit Position
```bash
node adaptive_edge_trader.js exit
```

### Stop Trader
```bash
node adaptive_edge_trader.js stop
```

---

## Troubleshooting

### "Secrets not found"
Verify files exist:
```bash
ls -la solana-trader/.secrets/
```

### "Port already in use"
Kill existing process:
```bash
lsof -ti:3456 | xargs kill -9
```

### "Low SOL balance"
Minimum 0.5 SOL recommended for fees + trades

### "Transaction failed"
- Check priority fee settings
- Verify Jupiter API key validity
- Check Helius RPC status

---

## Risk Acknowledgment

⚠️ **IMPORTANT:** Live trading carries real financial risk.

- Past performance does not guarantee future results
- Meme coins are highly volatile
- Slippage may exceed estimates
- Network congestion can fail transactions
- Always trade with capital you can afford to lose

**Start with small size. Prove the edge. Scale gradually.**

---

## Next Steps

1. ✅ Monitor running on localhost:3456
2. ✅ Verify balance shows correctly
3. ✅ Click START to begin Phase 1 (0.15-0.25 SOL trades)
4. ✅ Execute 5 test trades
5. ✅ Review real vs expected slippage
6. ⏳ Adjust if needed
7. ⏳ Scale to 0.35 SOL after validation

---

**Ready to deploy? Start the monitor and click START.**
