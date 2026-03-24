# 🎯 Wallet Copy Trader

Copy buy trades from target wallets and sell when in profit.

## How It Works

1. **Monitors** specified wallet addresses via Helius API
2. **Detects** when target wallet buys tokens
3. **Copies** the buy with your configured position size
4. **Sells** automatically:
   - When +15% profit (configurable)
   - When -15% stop loss hit
   - After 4 hours (time stop)

## Quick Start

### 1. Configure Target Wallets

Edit `/agents/wallet_tracker/config.json`:

```json
"target_wallets": [
  "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
]
```

Add wallets you want to copy from.

### 2. Adjust Settings (Optional)

```json
"trading_settings": {
  "position_size_sol": 0.01,      // Size per trade
  "profit_target_pct": 15,        // Sell at +15%
  "stop_loss_pct": 15,           // Stop at -15%
  "max_hold_hours": 4,            // Max hold time
  "min_token_mc": 5000,           // Min market cap
  "max_token_mc": 500000          // Max market cap
}
```

### 3. Run

```bash
cd /home/skux/.openclaw/workspace/agents/wallet_tracker
./run_wallet_tracker.sh
```

Or directly:
```bash
python3 wallet_copy_strategy.py
```

### 4. Run Continuously

Add to crontab for automatic monitoring:
```bash
crontab -e

# Check every 5 minutes
*/5 * * * * cd /home/skux/.openclaw/workspace/agents/wallet_tracker && python3 wallet_copy_strategy.py >> wallet_tracker_cron.log 2>&1
```

## Strategy Logic

### Entry Criteria
- Target wallet buys a token
- Token MC is between $5k-$500k
- Not already holding this token

### Exit Criteria
- **Profit Target**: +15% (sell immediately)
- **Stop Loss**: -15% (cut losses)
- **Time Stop**: 4 hours max hold

### Token Filters
- Min Market Cap: $5,000 (avoid rugs)
- Max Market Cap: $500,000 (focus on low caps)
- Only copy tokens target wallet is actually buying

## Files

- `wallet_copy_strategy.py` - Main strategy
- `config.json` - Configuration
- `wallet_tracker_state.json` - Position tracking
- `wallet_tracker_trades.json` - Trade history
- `wallet_tracker.log` - Runtime logs

## Monitoring

Check positions:
```bash
python3 wallet_copy_strategy.py
cat wallet_tracker_state.json | jq '.positions'
```

View trade history:
```bash
cat wallet_tracker_trades.json | tail -20
```

## API Requirements

Uses free tiers:
- **Helius**: Transaction history (free tier: 100k requests/month)
- **Birdeye**: Price/MC data

If you hit rate limits, reduce check frequency in crontab.

## Important Notes

⚠️ **This is a paper/testing strategy only!**
- Set `position_size_sol` very small (0.01 SOL) until tested
- Target wallets can lose money too
- Copy trading doesn't guarantee profits
- Always DYOR (Do Your Own Research)

🔒 **Safety Features**:
- Max position size limit
- Market cap filters
- Hard stop losses
- Time stops

## Next Steps

1. Add live execution (Jupiter swaps)
2. Add Telegram notifications
3. Add multiple wallet tracking
4. Add wallet performance analytics

## Troubleshooting

**No trades found?**
- Check if target wallets are actually buying
- Verify wallet addresses are correct
- Check logs: `tail -f wallet_tracker.log`

**Rate limits?**
- Reduce check frequency
- Use fewer target wallets
- Consider Helius paid tier

**Wrong token bought?**
- Token analysis happens after buy detection
- Some token buys might be filtered by MC limits
