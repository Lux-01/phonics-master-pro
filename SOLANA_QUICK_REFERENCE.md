# Solana Meme Coin Trading - Quick Reference

## 🚀 Quick Start (5 Minutes)

### 1. Get API Keys
```
Helius:      https://helius.xyz (Free tier)
Birdeye:     https://birdeye.so (Free tier)
Jupiter:     https://jup.ag (Free, no key needed)
```

### 2. Essential Code Template
```python
import requests
from solana.rpc.api import Client

# Setup
HELIUS_KEY = 'your_key'
BIRDEYE_KEY = 'your_key'

solana = Client(f'https://mainnet.helius-rpc.com/?api-key={HELIUS_KEY}')

# Quick scan
def quick_scan():
    url = 'https://public-api.birdeye.so/public/tokenlist'
    headers = {'X-API-KEY': BIRDEYE_KEY}
    
    r = requests.get(url, headers=headers, params={
        'sort_by': 'v24hUSD',
        'sort_type': 'desc',
        'limit': 20
    })
    
    tokens = r.json()['data']['tokens']
    
    # Filter
    good_tokens = [
        t for t in tokens 
        if t['liquidity'] > 10000  # $10K liquidity
        and t['v24hUSD'] > 5000    # $5K volume
    ]
    
    return good_tokens

# Quick buy
def quick_buy(token_address, sol_amount=0.1):
    url = 'https://quote-api.jup.ag/v6/quote'
    
    quote = requests.get(url, params={
        'inputMint': 'So11111111111111111111111111111111111111112',  # SOL
        'outputMint': token_address,
        'amount': int(sol_amount * 1e9),  # Convert to lamports
        'slippageBps': 100  # 1%
    }).json()
    
    # Execute swap (simplified - see full docs)
    return quote
```

---

## 📊 Best Strategies (Copy-Paste Ready)

### Strategy 1: Volume Spike Hunter
```python
def volume_spike_scanner():
    """Find tokens with 3x+ volume spike"""
    tokens = birdeye.get_trending(timeframe='5m')
    
    for token in tokens:
        if token['volumeChangePercent'] > 300:
            if token['priceChangePercent'] > 10:
                # Buy signal
                enter_position(token['address'], 0.2)
                set_stop_loss(-10)
                set_take_profit(+50)
```

### Strategy 2: New Token Sniper
```python
def new_token_sniper():
    """Buy new tokens within 30 seconds of launch"""
    # Via Helius webhook
    @webhook.route('/new-pool')
    def handle_new_pool():
        token = request.json['tokenAddress']
        
        # Quick validation
        if get_liquidity(token) > 5000:
            buy(token, amount=0.1)
            set_sell_targets([+50, +100, +200])
```

### Strategy 3: Mean Reversion
```python
def mean_reversion_bot():
    """Buy dips, sell pumps"""
    for token in watchlist:
        price = get_price(token)
        high_1h = get_high(token, '1h')
        
        # Buy if down 20% from 1h high
        if price < high_1h * 0.80:
            buy(token, 0.2)
            sell_target = price * 1.15  # +15%
            stop_loss = price * 0.93    # -7%
```

---

## 🔌 API Endpoints

### Jupiter (Swaps)
```
Quote:   GET https://quote-api.jup.ag/v6/quote
Swap:    POST https://quote-api.jup.ag/v6/swap
```

### Birdeye (Prices)
```
Price:   GET https://public-api.birdeye.so/public/price
History: GET https://public-api.birdeye.so/public/history_price
Tokens:  GET https://public-api.birdeye.so/public/tokenlist
```

### Helius (RPC)
```
RPC:     https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
Webhook: POST https://api.helius.xyz/v0/webhooks?api-key=YOUR_KEY
```

### DexScreener
```
Pairs:   GET https://api.dexscreener.com/latest/dex/pairs/solana
Search:  GET https://api.dexscreener.com/latest/dex/search?q=TOKEN
```

---

## 💰 Risk Management Rules

### Position Sizing
```
Bankroll: 10 SOL
Max per trade: 0.5 SOL (5%)
Max daily loss: 1 SOL (10%)
```

### Stop Losses
```
Hard stop: -7%
Trailing stop: -10% from peak
Time stop: 4 hours max
```

### Take Profits
```
Scale 1: +30% (sell 25%)
Scale 2: +60% (sell 25%)
Scale 3: +100% (sell 25%)
Let rest run with trailing stop
```

---

## 📈 Key Metrics to Track

| Metric | Target | Why |
|--------|--------|-----|
| Win Rate | >55% | Probability of profit |
| Profit Factor | >1.5 | Wins vs losses ratio |
| Avg Win/Loss | >2:1 | Reward vs risk |
| Max Drawdown | <20% | Capital preservation |
| Sharpe Ratio | >1.0 | Risk-adjusted returns |

---

## 🛠️ Tech Stack

### Python
```bash
pip install solana solders anchorpy requests pandas numpy
```

### Node.js
```bash
npm install @solana/web3.js @solana/spl-token @jup-ag/core axios
```

---

## ⚡ Performance Tips

1. **Use Helius** - Faster RPC than public nodes
2. **Priority Fees** - 0.00001 SOL for faster execution
3. **Batch Requests** - Reduce API calls
4. **Cache Prices** - Don't fetch every second
5. **WebSockets** - Real-time updates vs polling

---

## 🚨 Common Mistakes

❌ **Don't:**
- Risk more than 5% per trade
- Chase pumps (buying +50% already)
- Ignore liquidity (can get stuck)
- Hold bags (cut losses quickly)
- Over-trade (fees eat profits)

✅ **Do:**
- Paper trade first
- Set stop losses immediately
- Take profits in stages
- Track all trades
- Review and optimize weekly

---

## 📞 Support Resources

- **Jupiter Discord:** https://discord.gg/jup
- **Helius Discord:** https://discord.gg/helius
- **Solana StackExchange:** https://solana.stackexchange.com
- **Birdeye Docs:** https://docs.birdeye.so

---

**Start here:** Get Helius + Birdeye API keys, run the quick_scan() function, paper trade for 1 week.
