# 🐳 Whale Tracker Setup Guide

Complete guide to finding profitable whale wallets and setting up Telegram alerts.

---

## Part 1: Finding Profitable Whale Wallets

### Method 1: DeBank (Recommended)

**Step 1:** Go to https://debank.com/ranking

**Step 2:** Filter by:
- Chain: Solana
- Time: 7 days or 30 days
- Sort by: ROI

**Step 3:** Look for wallets with:
- ✅ ROI > 50% (7 days) or > 100% (30 days)
- ✅ Consistent profits (not just one lucky trade)
- ✅ Multiple tokens traded (shows experience)
- ✅ Early entry patterns (buys before pumps)

**Step 4:** Click on promising wallets to see:
- Trade history
- Token holding periods
- Win/loss ratio
- Average position size

**Step 5:** Copy the wallet address and add it:
```bash
python3 run_tracker_v2.py add-wallet <ADDRESS> "Whale_Name" 1.0
```

---

### Method 2: Solscan (For Early Adopters)

**Step 1:** Find a token that recently pumped 5x+

**Step 2:** Go to https://solscan.io/token/<TOKEN_ADDRESS>

**Step 3:** Click "Holders" tab

**Step 4:** Look for wallets that:
- Bought in first 100 holders
- Still hold significant amount
- Have multiple successful tokens

**Step 5:** Click wallet address → "Transactions" to verify pattern

---

### Method 3: Birdeye Wallet Analyzer

**Step 1:** Go to https://birdeye.so

**Step 2:** Search for any token

**Step 3:** Click "Holders" → Top holder

**Step 4:** View their portfolio and P&L

**Step 5:** If profitable, copy address

---

## Part 2: Wallet Types to Track

### 🥇 Tier 1: Smart Money (Highest Priority)
**Characteristics:**
- ROI: 100%+ over 30 days
- Win rate: >60%
- Average hold: 2-48 hours
- Position size: 0.5-2 SOL

**Why track them:**
- Research-backed entries
- Good risk management
- Consistent profits

**How many:** 2-3 wallets

---

### 🥈 Tier 2: Early Adopters
**Characteristics:**
- Always in first 50 buyers
- High volume (20+ trades/day)
- Small positions (0.1-0.5 SOL)
- Quick exits (1-6 hours)

**Why track them:**
- Find tokens before they trend
- 10x+ potential
- Early alpha

**How many:** 1-2 wallets

---

### 🥉 Tier 3: Diamond Hands
**Characteristics:**
- Hold through dips
- Sell at 2x-5x
- Lower trade frequency
- Higher conviction

**Why track them:**
- Filter out noise
- Higher quality signals
- Better for larger positions

**How many:** 1-2 wallets

---

## Part 3: Recommended Wallets to Research

### Known Profitable Patterns

Based on community data and successful traders:

1. **Dev Wallet Followers**
   - Track wallets that buy right after token deployers
   - Often insiders or connected accounts
   - Signal strength: HIGH

2. **Pump.fun Early Buyers**
   - Wallets that consistently buy within first 5 minutes
   - Look for wallets with 5+ successful early entries
   - Signal strength: MEDIUM-HIGH

3. **Raydium Migration Snipers**
   - Buy when tokens migrate from Pump.fun to Raydium
   - Usually 10-100x gains
   - Signal strength: VERY HIGH

4. **Influencer Wallets**
   - Track wallets of known crypto Twitter accounts
   - They often buy before shilling
   - Signal strength: MEDIUM

---

## Part 4: Telegram Bot Setup

### Quick Setup (Automated)

```bash
cd /home/skux/.openclaw/workspace/agents/wallet_whale
chmod +x setup_telegram.sh
./setup_telegram.sh
```

### Manual Setup

**Step 1: Create Bot**
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Name it (e.g., "WhaleTracker Alerts")
5. Username (e.g., yourname_whalert_bot)
6. **Copy the API token** (looks like: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`)

**Step 2: Get Chat ID**
1. Send a message to your new bot
2. Visit: `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
3. Find: `"chat":{"id":123456789}`
4. **Copy the ID number**

**Step 3: Set Environment Variables**

```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id"
```

Add to `~/.bashrc` for persistence:
```bash
echo 'export TELEGRAM_BOT_TOKEN="your_token_here"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="your_chat_id"' >> ~/.bashrc
```

**Step 4: Test**
```bash
python3 run_tracker_v2.py test-telegram
```

---

## Part 5: Configuration

### Edit Config
```bash
nano whale_config.json
```

### Key Settings

```json
{
  "trigger_rules": {
    "min_buys_to_trigger": 4,      // Lower = more signals, more false positives
    "time_window_seconds": 30,    // Window for counting buys
    "multi_whale_threshold": 2,     // Wallets needed for multi-whale alert
    "cooldown_minutes_between_trades": 3
  },
  "skylar_strategy": {
    "entry_size_sol": 0.3,         // Your position size
    "target_profit_pct": 15,
    "stop_loss_pct": 7,
    "time_stop_hours": 4
  }
}
```

### Wallet Weights

Give higher weights to better wallets:
```json
{
  "address": "...",
  "name": "Smart Money A",
  "weight": 1.5,    // Higher = more confidence
  "enabled": true
}
```

---

## Part 6: Running the Tracker

### Start
```bash
python3 run_tracker_v2.py start
```

### Check Status
```bash
python3 run_tracker_v2.py status
```

### View Logs
```bash
tail -f tracker.log
```

### Stop
```bash
python3 run_tracker_v2.py stop
```

---

## Part 7: Interpreting Alerts

### 🐳 Single Whale Alert
**Meaning:** One wallet bought 4+ times in 30 seconds
**Action:** Review token, consider entry
**Risk:** Medium

### 🔥 Multi-Whale Alert
**Meaning:** 2+ different whales buying same token
**Action:** High confidence signal, likely good entry
**Risk:** Lower

### ✅ Trade Executed
**Meaning:** Skylar copied the whale
**Action:** Monitor position, wait for exit
**Follow-up:** You'll get updates on P&L

### ❌ Trade Failed
**Meaning:** Couldn't execute (liquidity, slippage, etc.)
**Action:** Check manually if you want to enter

---

## Part 8: Risk Management

### Position Sizing
- **New whale:** 0.1 SOL test position
- **Proven whale:** 0.3 SOL standard
- **Multi-whale signal:** 0.5 SOL (higher confidence)

### Stop Losses
- Hard stop: -7%
- Trailing stop: -10% from peak
- Time stop: 4 hours

### Daily Limits
- Max 5 trades per day
- Max 2% daily loss
- Stop after 3 consecutive losses

---

## Part 9: Troubleshooting

### No Alerts Coming
1. Check tracker is running: `python3 run_tracker_v2.py status`
2. Check logs: `tail -f tracker.log`
3. Verify Telegram token: `echo $TELEGRAM_BOT_TOKEN`
4. Test Telegram: `python3 run_tracker_v2.py test-telegram`

### Too Many False Signals
1. Increase `min_buys_to_trigger` to 5 or 6
2. Increase `time_window_seconds` to 60
3. Add wallet weights (higher = more selective)
4. Disable low-quality wallets

### Missing Good Trades
1. Decrease `min_buys_to_trigger` to 3
2. Decrease `cooldown_minutes_between_trades` to 2
3. Add more whale wallets
4. Check API rate limits

---

## Part 10: Advanced Tips

### Finding Hidden Whales
1. Look for wallets that buy before trending on DexScreener
2. Track wallets that sell right before dumps (reverse signal)
3. Find wallets that consistently buy dev's tokens
4. Look for sniper bots (first 10 buyers)

### Multi-Chain Expansion
Once Solana is working:
1. Add Ethereum whale tracking
2. Add Base chain tracking
3. Cross-reference signals across chains

### Machine Learning
Track which whales are most profitable to copy:
```bash
python3 analyze_whale_performance.py
```

Then weight them higher in config.

---

## Quick Reference Card

```bash
# Start tracking
python3 run_tracker_v2.py start

# Add wallet
python3 run_tracker_v2.py add-wallet <ADDRESS> <NAME> [WEIGHT]

# Remove wallet
python3 run_tracker_v2.py remove-wallet <NAME>

# Check status
python3 run_tracker_v2.py status

# View trades
python3 run_tracker_v2.py trades

# Test Telegram
python3 run_tracker_v2.py test-telegram

# Find new whales
python3 find_whales_helius.py

# View logs
tail -f tracker.log
```

---

## Support

If you have issues:
1. Check logs: `tracker.log`
2. Verify config: `whale_config.json`
3. Test APIs: `python3 -c "import requests; print('OK')"`
4. Check Telegram: @BotFather for bot issues

---

**Happy whale hunting! 🐳**
