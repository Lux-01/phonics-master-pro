# Helius RPC Setup Guide

## Free Tier Benefits
- **Free Plan**: No credit card required
- **Requests**: 500k calls/day
- **Rate Limit**: 25 requests/second (sufficient for trading)
- **Endpoints**: Global edge deployment

---

## Setup Steps

### 1. Sign Up
```
1. Go to: https://www.helius.dev/
2. Click "Get Started"
3. Sign up with email/password (or wallet)
4. No credit card required for free tier
```

### 2. Create API Key
```
1. After login, click "Create New Key"
2. Give it a name like "TradingBot"
3. Select network: "Mainnet"
4. Copy your RPC URL (looks like: https://mainnet.helius-rpc.com/?api-key=YOUR_KEY)
```

### 3. Save to Project
```bash
# In your solana-trader directory
echo "HELIUS_RPC_URL=YOUR_HELIUS_URL_HERE" >> .env
echo "HELIUS_API_KEY=YOUR_API_KEY_HERE" >> .env
```

---

## Alternative: QuickNode (Also Free)

### Free Tier:
- 25M credits/month (~250k requests)
- 1 endpoint
- Basic support

### Sign Up:
```
https://www.quicknode.com/
```

---

## Using With Your Trader

Once you have the RPC URL, update:

```javascript
// In jupiter_trader.js
const CONFIG = {
  jupiterApiUrl: 'https://api.jup.ag/swap/v1',
  rpcEndpoint: 'https://mainnet.helius-rpc.com/?api-key=YOUR_KEY',  // Replace this
  ...
};
```

Your swaps will then execute reliably without rate limits!

---

## Current Status Without Helius

Your trader is **working** but may hit rate limits:
- ✅ Quote API: Works fine
- ✅ Swap building: Works fine
- ⚠️ Transaction execution: May fail due to public RPC limits
- ⚠️ Balance checking: May fail due to public RPC limits

With Helius, all will be 100% reliable.

---

## Recommendation

**For Tonight's Trading:**
Your setup is functional. You can execute trades - just be aware public RPC might rate-limit during busy periods.

**For Reliable Trading:**
Spend 2 minutes signing up for Helius free tier. It gives you 500k calls/day which is more than enough for active trading.

**Want me to help execute a trade now while you set up Helius?** The public RPC might work for a few test trades.
