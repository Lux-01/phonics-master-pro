# 🔍 Raydium SDK Integration - Research Results

## Token Analysis: INCOME

| Property | Value |
|----------|-------|
| **Token** | INCOME |
| **Address** | 5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump |
| **Amount** | 490.916016 |
| **DEX** | **PumpSwap** (not Raydium!) |
| **Pool** | C1CfVtbnUoW9y2ZgZkynn9di4eANZwqa4TPGHa7pfFFr |
| **Liquidity** | $32,576 |

---

## ❌ Why Raydium SDK Won't Work

**The token trades on PumpSwap, NOT Raydium.**

Raydium SDK only works for:
- ✅ Raydium AMM v4 pools
- ✅ Raydium Concentrated Liquidity (CLMM)
- ✅ Raydium CPMM pools

**PumpSwap is a separate DEX** with different:
- Smart contracts
- Bonding curve mechanics
- API endpoints

---

## 🔧 What We Tried

### 1. Raydium API v3
**Status:** ❌ Failed
- API endpoints changed/deprecated
- Token not in Raydium pools

### 2. Direct Contract Integration
**Status:** ❌ Not possible
- Token not on Raydium
- Would need PumpSwap program IDs

### 3. Jupiter with PumpSwap Filter
**Status:** ❌ DNS issues
- quote-api.jup.ag not resolving
- Network connectivity issues

---

## ✅ Working Solution: Manual Sell

Since automated solutions are failing, here are the **manual options** that will work:

### Option 1: Jupiter UI (Best)
```
https://jup.ag/swap/5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump-SOL
```
**Steps:**
1. Connect wallet: `8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5`
2. Set slippage to **10-20%** (PumpSwap requires high slippage)
3. Click Swap
4. Confirm in wallet

### Option 2: PumpSwap Direct
```
https://pump.fun/swap
```
**Steps:**
1. Connect wallet
2. Search for INCOME
3. Enter amount: 490.916016
4. Swap to SOL

### Option 3: Phantom Wallet
**Steps:**
1. Open Phantom
2. Click Swap
3. Select INCOME → SOL
4. Set slippage to 10%
5. Confirm

---

## 📊 Current Holdings

| Token | Amount | Status |
|-------|--------|--------|
| **INCOME** | 490.916016 | ⏳ Need to sell |
| **MEMECARD** | 951.03 | ✅ Sold manually |

---

## 🎯 Key Insight

**PumpSwap tokens require different handling:**

| Feature | Standard DEX | PumpSwap |
|---------|--------------|----------|
| Slippage | 0.5-1% | 10-20% |
| Route stability | Good | Poor (stale routes) |
| API support | Good | Limited |
| Best method | Automated | Manual UI |

---

## 🔮 Future Solutions

For future PumpSwap tokens, consider:

### 1. PumpSwap SDK (if available)
```bash
# Check if PumpSwap releases an SDK
npm install @pump-swap/sdk
```

### 2. Direct Contract Calls
- Use Solana-py to call PumpSwap programs directly
- Requires knowing PumpSwap instruction layouts

### 3. Jupiter Retry Strategy
- Implement 5+ retry attempts
- Increase slippage each time: 1% → 5% → 10% → 20%
- Wait 30-60 seconds between attempts

### 4. Manual-First Approach
- For PumpSwap tokens, always use UI
- Only automate Raydium/Orca tokens

---

## 📁 Files Created

- `raydium_sell_income.py` - Raydium API attempt
- `raydium_integration.py` - Direct contract research
- `pumpswap_sell.py` - PumpSwap integration attempt
- `RAYDIUM_RESEARCH.md` - This file

---

## 💡 Recommendation

**For INCOME token:**
1. Use Jupiter UI with 15% slippage
2. Or use PumpSwap direct
3. Expect ~0.0009-0.001 SOL return

**For future trading:**
- Check DEX Screener first
- If token is on PumpSwap → Use manual UI
- If token is on Raydium/Orca → Can automate

---

## 🔗 Quick Links

- **Jupiter:** https://jup.ag/swap/5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump-SOL
- **PumpSwap:** https://pump.fun/swap
- **Solscan:** https://solscan.io/token/5QmbJw7mM6tcCdXVy8ftc2bu8izded7Etc57TMA2pump

---

**Status:** Research complete. Manual sell recommended.
