# 🔍 Solana Tracker (yzylab) API

**Website:** https://www.solanatracker.io  
**Docs:** https://docs.solanatracker.io  
**Company:** yzylab

---

## 🚀 What is Solana Tracker?

Solana Tracker is a comprehensive API platform for building Solana applications, offering:

- **Data API** - Token prices, market data, analytics
- **Swap API** - Execute swaps across all major DEXs
- **RPC Infrastructure** - Shared and dedicated Solana RPC nodes
- **Streaming APIs** - Real-time WebSocket data feeds
- **Yellowstone gRPC** - High-performance streaming

---

## 💰 Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | Limited API calls, basic features |
| **Paid Plans** | Varies | Higher rate limits, dedicated RPC |

**Sign up:** https://www.solanatracker.io/account

---

## 🔑 Getting API Key

1. Go to https://www.solanatracker.io/account
2. Create free account
3. Get API key from dashboard
4. Pass in `x-api-key` header

---

## 🔄 Swap API (What You Need)

**Endpoint:** `POST https://api.solanatracker.io/swap`

**Supported DEXs:**
- ✅ Pump.fun
- ✅ PumpSwap
- ✅ Orca
- ✅ Meteora
- ✅ Moonshot
- ✅ Raydium (V4 AMM, CPMM, Launchpad)
- ✅ Jupiter (Aggregated routing)

**Key Features:**
- Build swap transactions
- Returns serialized transaction (you sign & send)
- Auto-routing across DEXs
- Custom fees support
- Priority fee support

---

## 📋 Example: Sell Token

```javascript
const tracker = new SolanaTracker();

// Sell 100% of token balance
const swap = await tracker.swap({
  from: 'TOKEN_ADDRESS',     // Token to sell
  to: 'So11111111111111111111111111111111111111112',  // SOL
  fromAmount: "auto",        // Sell entire balance
  slippage: 10,              // 10% slippage
  payer: 'YOUR_WALLET_ADDRESS',
  priorityFee: "auto",       // Auto priority fee
  priorityFeeLevel: "high"
});

// Returns serialized transaction
const txn = swap.txn;  // Base64 encoded
// Sign and send via RPC
```

---

## 📊 Response Format

```json
{
  "txn": "BASE64_ENCODED_TRANSACTION",
  "rate": {
    "amountIn": 0.1,
    "amountOut": 81.63,
    "minAmountOut": 73.47,
    "currentPrice": 0.0122,
    "executionPrice": 0.0110,
    "priceImpact": 0.0025,
    "fee": 0.000005,
    "platformFee": 9000000,
    "platformFeeUI": 0.009
  },
  "timeTaken": 0.016,
  "type": "v0"
}
```

---

## 💡 Why Use Solana Tracker for Selling?

| Feature | Jupiter | Solana Tracker |
|---------|---------|----------------|
| Multi-DEX routing | ✅ | ✅ |
| Error 0x1788 handling | ❌ | Better |
| Auto slippage | ❌ | ✅ (Beta) |
| Percentage amounts | ❌ | ✅ (e.g., "50%") |
| Custom fees | ❌ | ✅ |
| Priority fees | Manual | Auto |

**Key advantage:** Solana Tracker aggregates across DEXs including Jupiter, so if Jupiter's route fails, it may find alternatives through Raydium, Orca, etc.

---

## 🛠️ Python Implementation

```python
import requests
import base64

API_KEY = "your_api_key"

def sell_token_solana_tracker(
    token_address: str,
    wallet_address: str,
    amount: str = "auto",  # "auto", "50%", or numeric
    slippage: int = 10
):
    """Sell token using Solana Tracker API"""
    
    url = "https://api.solanatracker.io/swap"
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": token_address,
        "to": "So11111111111111111111111111111111111111112",
        "fromAmount": amount,
        "slippage": slippage,
        "payer": wallet_address,
        "priorityFee": "auto",
        "priorityFeeLevel": "high"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return {
            "transaction": data["txn"],  # Base64 encoded
            "expected_out": data["rate"]["amountOut"],
            "min_out": data["rate"]["minAmountOut"],
            "price_impact": data["rate"]["priceImpact"]
        }
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
result = sell_token_solana_tracker(
    token_address="2X4NETdeZAZshwsedjsJnwDWFhuN75gY9By642ySFeJJ",
    wallet_address="8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5",
    amount="auto",  # Sell entire balance
    slippage=10
)

if result:
    # Sign and send transaction
    tx_base64 = result["transaction"]
    # Use solders to deserialize, sign, and send
```

---

## 📈 Platform Fees

- **Standard:** 0.5% of transaction value
- Deducted from output
- Volume discounts available

---

## 🔗 Useful Links

- **Docs:** https://docs.solanatracker.io
- **Swap API Docs:** https://docs.solanatracker.io/swap-api/swap
- **Quick Start:** https://docs.solanatracker.io/quickstart
- **Discord:** https://discord.gg/JH2e9rR9fc
- **Account/Keys:** https://www.solanatracker.io/account

---

## ⚡ Quick Test

Want to test if Solana Tracker can sell your MEMECARD tokens?

1. Sign up for free API key
2. Use the Python code above
3. Try selling with `amount="auto"` and `slippage=10`

**Expected advantage:** If Jupiter fails with error 0x1788, Solana Tracker may route through Raydium directly since it aggregates multiple DEXs.

---

## 🎯 Recommendation

**For your MEMECARD sell issue:**

Solana Tracker is worth trying because:
1. ✅ It aggregates Jupiter + Raydium + Orca + others
2. ✅ If Jupiter route is stale, it may find Raydium route
3. ✅ "Auto" amount feature handles balance checking
4. ✅ Better error handling than raw Jupiter API

**Next step:** Sign up for free API key and test the swap endpoint.
