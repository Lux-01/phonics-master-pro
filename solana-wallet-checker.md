# Solana Wallet Health Checker Integration

## Purpose
Check wallet age and SOL balance for the Rug Pull Scanner v5.1 Wallet Health Filter.

## API Options

### 1. Helius API (Recommended)
- Endpoint: `https://mainnet.helius-rpc.com/?api-key=<KEY>`
- Methods needed:
  - `getAccountInfo` - For SOL balance
  - `getSignaturesForAddress` - For transaction history (wallet age)
  - Enhanced API for token balances

### 2. SolanaFM (Currently down)
- Endpoint: `https://api.solana.fm/v1/accounts/{address}`
- Provides: Balance, transaction count, first transaction date

### 3. Solscan (Public API - Limited)
- Endpoint: `https://public-api.solscan.io/account/{address}`
- Rate limited but free

## v5.1 Wallet Health Filter Algorithm

```javascript
async function checkWalletHealth(tokenCA) {
  // 1. Get holder list from RugCheck API
  const holders = await getTopHolders(tokenCA, 50); // Top 20 + random 30
  
  let unhealthyCount = 0;
  
  for (const wallet of holders) {
    const [balance, firstTx] = await Promise.all([
      getSOLBalance(wallet.address),
      getFirstTransaction(wallet.address)
    ]);
    
    const walletAge = Date.now() - firstTx.timestamp;
    const isNew = walletAge < (7 * 24 * 60 * 60 * 1000); // 7 days
    const isLowBalance = balance < 0.1; // Less than 0.1 SOL
    
    if (isNew || isLowBalance) {
      unhealthyCount++;
    }
  }
  
  // If 40/50 (80%) are unhealthy → F grade
  if (unhealthyCount >= 40) {
    return { grade: 'F', reason: 'Shell wallet attack', unhealthyCount };
  }
  
  return { grade: 'PASS', unhealthyCount };
}
```

## Implementation Steps

1. **Get Helius API Key**
   - Sign up at helius.xyz
   - Free tier: 100K requests/day
   - Paid tier: Unlimited

2. **Store API Key**
   - Add to TOOLS.md or OpenClaw config

3. **Create Wrapper Functions**
   - `getWalletAge(address)` → Returns days since first transaction
   - `getWalletBalance(address)` → Returns SOL balance
   - `batchCheckWallets(addresses[])` → Returns health scores

## Rate Limiting

- Helius: 100K requests/day on free tier
- Batch check 50 wallets = 50 API calls per token scan
- 2000 scans/day possible on free tier

## Example Response

```json
{
  "wallet": "3GyKoyLSZ4mAqUWKyFhCiRvt3MWa16YSnr6HJbJrX7eX",
  "solBalance": 12.45,
  "firstTransaction": "2023-08-15T10:23:45Z",
  "walletAgeDays": 184,
  "isHealthy": true
}
```

## Status

⏳ **PENDING API KEY**
- SolanaFM: Down (502 Bad Gateway)
- Helius: Requires API key
- Solscan: Limited rate

**Next Action:** Get Helius API key and test wallet queries.
