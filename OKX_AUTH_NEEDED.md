# OKX API Authentication Requirements
# Created: 2026-03-15

## Current Status
✅ API Key received: 911fb148-e0fe-41b5-bab5-6f9a1a902137
❌ Missing: Secret Key and Passphrase

## Why It Failed

OKX requires **3 credentials** for API access:

1. **API Key** (you provided) ✅
   - Public identifier
   - Example: `911fb148-e0fe-41b5-bab5-6f9a1a902137`

2. **Secret Key** (needed) ❌
   - Used to sign requests
   - Looks like: `1A2B3C4D5E6F...` (longer string)
   - **Only shown once when created!**

3. **Passphrase** (needed) ❌
   - Extra security layer
   - You set this when creating the API key

## How to Get Missing Credentials

### If you just created the API key:
1. Go back to the API key creation page
2. Look for:
   - "Secret Key" (long string, copy immediately!)
   - "Passphrase" (you set this yourself)

### If you already closed the page:
**You need to create a new API key** - the Secret Key is only shown once!

Steps:
1. Go to: https://www.okx.com/account/my-api
2. Click "Create API Key"
3. Select "Trade" permissions
4. **SAVE ALL 3 VALUES:**
   - API Key
   - Secret Key  ← This is new!
   - Passphrase  ← You create this!

## What I Need From You

Please provide:
1. ✅ API Key: `911fb148-e0fe-41b5-bab5-6f9a1a902137` (already have)
2. ❌ Secret Key: `______________________________` (need this)
3. ❌ Passphrase: `______________________________` (need this)

## Security Note

I'll store these securely in a local config file (`.okx_config`) that only you can access. The credentials will be used only for:
- Testing the API
- Building swap transactions
- Executing sell orders

## Alternative: Web3 API Key

OKX has TWO types of API keys:
1. **Trading API** (requires Secret Key + Passphrase)
2. **Web3 API** (may be simpler)

Try getting a Web3 API key instead:
1. Go to: https://www.okx.com/web3
2. Click "Developer" → "API Keys"
3. Create Web3 API key

This might have different authentication requirements.

---

**Next step:** Please provide the Secret Key and Passphrase, or create a new API key and save all 3 values.
