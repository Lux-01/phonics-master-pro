# 🔍 Research: Alternative Sell Solutions for Solana Tokens

## Executive Summary

After researching multiple alternatives to Jupiter for selling tokens, here are the findings:

| Solution | API Available | Best For | Status |
|----------|---------------|----------|--------|
| **OKX DEX API** | ✅ Yes | Multi-DEX aggregation | ⭐ Recommended |
| **GMGN API** | ⚠️ Limited | Data only (no swap) | ❌ Not suitable |
| **Telegram Bots** | ❌ No API | Manual trading only | ❌ Not suitable |
| **Pump.fun Direct** | ⚠️ Complex | Pump.fun tokens only | ⚠️ Technical |
| **Raydium Direct** | ✅ Yes | Raydium pools | ✅ Good fallback |

---

## 1. ✅ OKX DEX API (Best Alternative)

**Website:** https://www.okx.com/web3/build/docs/waas/dex-swap  
**API Endpoint:** `https://web3.okx.com/api/v5/dex/aggregator/swap`

### Features:
- ✅ Multi-DEX aggregation (similar to Jupiter)
- ✅ Supports Solana (chainId: 501)
- ✅ Swap API with transaction building
- ✅ Token list API
- ✅ Custom slippage settings
- ✅ Commission/referral fees support
- ✅ Gas level settings

### Swap API Parameters:

```
GET /api/v5/dex/aggregator/swap

Required params:
- chainId: "501" (Solana)
- fromTokenAddress: Input token
- toTokenAddress: Output token (SOL = "11111111111111111111111111111111")
- amount: Amount in minimal units
- slippage: "0.01" for 1%
- userWalletAddress: Your wallet

Optional:
- feePercent: Referral fee (0-3%)
- gasLevel: "slow", "average", "fast"
- dexIds: Specific DEX IDs
```

### Example Request:

```bash
curl "https://web3.okx.com/api/v5/dex/aggregator/swap?\
chainId=501&\
fromTokenAddress=2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ&\
toTokenAddress=11111111111111111111111111111111&\
amount=941520000000&\
slippage=0.1&\
userWalletAddress=8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
```

### Pros:
- ✅ Enterprise-grade infrastructure
- ✅ Aggregates multiple DEXs
- ✅ Better error handling than Jupiter
- ✅ Supports custom fees
- ✅ Free tier available

### Cons:
- ⚠️ Requires OKX account + API key
- ⚠️ Rate limits on free tier
- ⚠️ Different response format than Jupiter

---

## 2. ⚠️ GMGN.AI API (Limited)

**Website:** https://gmgn.ai  
**Docs:** https://docs.gmgn.ai

### Current Status:
- ❌ **NO public swap API**
- ✅ Data crawling API (IP whitelist only)
- ⚠️ Rate limited: 2 requests/second
- ⚠️ Requires application form

### What's Available:
- Token data (prices, holders, etc.)
- Wallet tracking
- Transaction history
- Smart money tracking

### What's NOT Available:
- ❌ Swap execution
- ❌ Transaction building
- ❌ Direct trading API

### Application Process:
1. Fill out form: https://forms.gle/7kp58kunJ6Ab3FNr6
2. Provide:
   - GMGN transaction address
   - Invitation code
   - IP address for whitelist
3. Wait for approval

### Verdict:
**Not suitable for automated selling** - only provides data, not swap functionality.

---

## 3. ❌ Telegram Trading Bots (No API)

### Popular Bots:
- **BONKbot** - https://bonkbot.io
- **Trojan** - https://trojan.trading
- **Maestro** - https://maestrobot.io
- **Banana Gun** - https://bananagun.io

### How They Work:
- All operate through Telegram UI
- Users send commands like `/buy` or `/sell`
- Bots execute trades via Jupiter/Raydium
- No public API for external integration

### Integration Options:

#### Option A: Telegram Bot API (Limited)
```python
# Can send messages to bot, but can't execute trades
import telegram

bot = telegram.Bot(token="YOUR_TOKEN")
bot.send_message(chat_id="@bonkbot", text="/sell TOKEN_AMOUNT")
```

**Problem:** Bots require interactive confirmation, not API-friendly.

#### Option B: Browser Automation
```python
# Use Playwright to automate Telegram Web
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://web.telegram.org")
    # Navigate to bot and execute trades
```

**Problem:** Brittle, requires active session, not reliable for automation.

### Verdict:
**Not suitable for programmatic trading** - designed for manual Telegram use.

---

## 4. ⚠️ Pump.fun Direct Bonding Curve

**For Pump.fun tokens only**

### How It Works:
- Pump.fun uses bonding curve pricing
- Direct contract interaction possible
- No Jupiter/Raydium needed for tokens still on curve

### Contract Address:
```
Pump.fun Program: 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P
```

### Direct Interaction:
```typescript
// Using Anchor/Solana Web3
import { Program, AnchorProvider } from '@coral-xyz/anchor';

// Buy from bonding curve
await program.methods.buy(new BN(amount), new BN(maxSolCost))
  .accounts({
    global,
    feeRecipient,
    mint,
    bondingCurve,
    bondingCurveTokenAccount,
    bondingCurveSolAccount,
    userTokenAccount,
    userSolAccount,
    tokenProgram,
    systemProgram,
    rent,
    clock,
  })
  .rpc();

// Sell to bonding curve
await program.methods.sell(new BN(amount), new BN(minSolOutput))
  .accounts({
    global,
    feeRecipient,
    mint,
    bondingCurve,
    bondingCurveTokenAccount,
    bondingCurveSolAccount,
    userTokenAccount,
    userSolAccount,
    tokenProgram,
    systemProgram,
    clock,
  })
  .rpc();
```

### Pros:
- ✅ No DEX routing issues
- ✅ Direct contract calls
- ✅ Lower fees

### Cons:
- ⚠️ Only for Pump.fun tokens
- ⚠️ Complex integration
- ⚠️ Requires Anchor framework
- ⚠️ Must check if token graduated

### Verdict:
**Only useful for Pump.fun tokens** - not a general solution.

---

## 5. ✅ Raydium Direct API

**Website:** https://raydium.io  
**API:** https://api-v3.raydium.io

### Available Endpoints:

#### Get Pools:
```
GET https://api-v3.raydium.io/pools
```

#### Get Swap Quote:
```
GET https://api-v3.raydium.io/swap/compute
  ?inputMint={token}
  &outputMint=So11111111111111111111111111111111111111112
  &amount={amount}
  &slippage=0.1
```

#### Build Transaction:
```
GET https://api-v3.raydium.io/swap/transaction
```

### Example:
```python
import requests

# Get quote
quote = requests.get(
    "https://api-v3.raydium.io/swap/compute",
    params={
        "inputMint": "2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ",
        "outputMint": "So11111111111111111111111111111111111111112",
        "amount": "941520000000",
        "slippage": "0.1",
        "txVersion": "V0"
    }
).json()

# Build transaction
tx = requests.get(
    "https://api-v3.raydium.io/swap/transaction",
    params={
        "wallet": "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5",
        # ... other params from quote
    }
).json()
```

### Pros:
- ✅ Direct pool access
- ✅ No Jupiter routing issues
- ✅ Good for Raydium-only tokens

### Cons:
- ⚠️ Only Raydium pools
- ⚠️ More complex than Jupiter
- ⚠️ Must handle transaction building

---

## 🎯 Recommendation

### Best Solution: OKX DEX API

**Why:**
1. ✅ Full swap API (like Jupiter)
2. ✅ Multi-DEX aggregation
3. ✅ Better reliability
4. ✅ Enterprise support
5. ✅ Free tier available

**Implementation:**
```python
import requests

class OKXDEXTrader:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://web3.okx.com/api/v5/dex/aggregator"
    
    def get_swap_quote(self, from_token, to_token, amount):
        """Get swap quote from OKX DEX"""
        url = f"{self.base_url}/swap"
        params = {
            "chainId": "501",  # Solana
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": str(amount),
            "slippage": "0.1",
            "userWalletAddress": self.wallet
        }
        
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": self._generate_signature(params),
            "OK-ACCESS-TIMESTAMP": str(int(time.time()))
        }
        
        response = requests.get(url, params=params, headers=headers)
        return response.json()
```

### Fallback Strategy:

1. **Primary:** Jupiter API (current)
2. **Fallback 1:** OKX DEX API
3. **Fallback 2:** Raydium Direct API
4. **Fallback 3:** Manual UI (Phantom/Raydium)

---

## 📋 Next Steps

1. **Sign up for OKX:** https://www.okx.com/account
2. **Get API credentials:** From developer dashboard
3. **Test swap endpoint:** With small amount
4. **Integrate into LuxTrader:** As fallback option

---

## 🔗 Useful Links

- **OKX DEX Docs:** https://www.okx.com/web3/build/docs/waas/dex-swap
- **Raydium API:** https://api-v3.raydium.io
- **GMGN Docs:** https://docs.gmgn.ai
- **BONKbot:** https://bonkbot.io
- **Trojan:** https://trojan.trading

---

## 💡 Key Insight

**The best alternative to Jupiter is OKX DEX API** because:
- It aggregates multiple DEXs (like Jupiter)
- Has enterprise-grade reliability
- Provides swap + quote APIs
- Supports custom fees
- Has free tier

**For immediate use:** Try OKX DEX API as your primary fallback when Jupiter fails with error 0x1788.
