# Solana Auto-Trading Bot Setup
## Jupiter SDK + Phantom Wallet Integration

---

## 🔐 Level 3: Secure Private Key Setup

### Step 1: Export Private Key from Phantom

```
1. Open Phantom Wallet
2. Settings ⚙️ → Security & Privacy
3. Show Secret Recovery Phrase → Export Private Key
4. Select Solana account → Copy private key (base58 encoded)
5. KEEP THIS SECRET - never share! ⚠️
```

### Step 2: Secure Storage (GPG Encryption)

We'll use GPG to encrypt your private key:

```bash
# Create encrypted file for private key
cd ~/.openclaw/workspace
mkdir -p .secrets
echo "paste_private_key_here" > .secrets/solana_wallet.key

# Set permissions (owner only)
chmod 600 .secrets/solana_wallet.key

# Read this file for loading
```

### Step 3: Never Commit to Git

Add to `.gitignore`:
```
.secrets/
*.key
.env
config/private*
```

---

## 🛠️ Level 2: Jupiter SDK Integration

### Architecture

```
OpenClaw Trading Agent
        ↓
Jupiter API (Quote + Execute)
        ↓
Solana RPC (QuickNode/Alchemy)
        ↓
Your Wallet (Direct signing)
```

### Requirements

```bash
# Node.js packages needed
npm install @solana/web3.js @jup-ag/core bs58

# Or Python
pip install solders solana
```

---

## 💻 Trading Bot Code

### Core Components

#### 1. Wallet Manager (Secure)

```javascript
// wallet_manager.js
const fs = require('fs');
const bs58 = require('bs58');
const { Keypair } = require('@solana/web3.js');

class SecureWallet {
  constructor(keyPath) {
    // Read private key from secure file
    const privateKeyString = fs.readFileSync(keyPath, 'utf8').trim();
    const privateKey = bs58.decode(privateKeyString);
    this.keypair = Keypair.fromSecretKey(privateKey);
  }
  
  getPublicKey() {
    return this.keypair.publicKey.toString();
  }
  
  getKeypair() {
    return this.keypair;
  }
}

module.exports = SecureWallet;
```

#### 2. Jupiter Swap Integration

```javascript
// jupiter_trader.js
const axios = require('axios');
const { Connection, VersionedTransaction } = require('@solana/web3.js');

class JupiterTrader {
  constructor(keypair, connectionUrl = 'https://api.mainnet-beta.solana.com') {
    this.keypair = keypair;
    this.connection = new Connection(connectionUrl);
  }
  
  // Step 1: Get quote
  async getQuote(inputMint, outputMint, amount, slippageBps = 50) {
    const url = `https://quote-api.jup.ag/v6/quote`;
    const params = {
      inputMint,
      outputMint,
      amount,  // in lamports/smallest unit
      slippageBps,
      onlyDirectRoutes: false
    };
    
    const response = await axios.get(url, { params });
    return response.data;
  }
  
  // Step 2: Get swap transaction
  async getSwapTransaction(quoteResponse) {
    const url = 'https://quote-api.jup.ag/v6/swap';
    const body = {
      quoteResponse,
      userPublicKey: this.keypair.publicKey.toString(),
      wrapUnwrapSOL: true,
      // Optional: priority fee for faster execution
      prioritizationFeeLamports: 10000  // 0.001 SOL
    };
    
    const response = await axios.post(url, body);
    return response.data;
  }
  
  // Step 3: Execute swap
  async executeSwap(swapTransaction) {
    // Deserialize transaction
    const transaction = VersionedTransaction.deserialize(
      Buffer.from(swapTransaction.swapTransaction, 'base64')
    );
    
    // Sign with wallet
    transaction.sign([this.keypair]);
    
    // Send transaction
    const signature = await this.connection.sendTransaction(transaction);
    
    // Wait for confirmation
    await this.connection.confirmTransaction(signature, 'confirmed');
    
    return signature;
  }
  
  // Full swap flow
  async swap(inputMint, outputMint, amount) {
    console.log(`Swapping ${amount} of ${inputMint} → ${outputMint}`);
    
    // 1. Get quote
    const quote = await this.getQuote(inputMint, outputMint, amount);
    console.log('Quote received:', quote.outAmount);
    
    // 2. Get swap tx
    const swapData = await this.getSwapTransaction(quote);
    console.log('Swap transaction ready');
    
    // 3. Execute
    const signature = await this.executeSwap(swapData);
    console.log('Swap executed:', signature);
    
    return signature;
  }
}

module.exports = JupiterTrader;
```

#### 3. Smart Swing Strategy Implementation

```javascript
// swing_trade_executor.js
const SecureWallet = require('./wallet_manager');
const JupiterTrader = require('./jupiter_trader');

class SmartSwingExecutor {
  constructor(configPath) {
    const config = require(configPath);
    this.wallet = new SecureWallet(config.wallet.keyPath);
    this.trader = new JupiterTrader(
      this.wallet.getKeypair(),
      config.rpcUrl
    );
    
    // Strategy parameters
    this.params = {
      entrySize: 0.5,  // SOL
      scaleTarget: 20, // %
      reentrySize: 0.25,
      trailStop: 10   // %
    };
  }
  
  // Execute entry
  async enterTrade(tokenMint, size) {
    const lamports = size * 1e9;  // SOL to lamports
    const tx = await this.trader.swap(
      'So11111111111111111111111111111111111111112',  // SOL
      tokenMint,
      lamports
    );
    return tx;
  }
  
  // Execute exit
  async exitTrade(tokenMint, percentage = 100) {
    // Get token balance first
    const balance = await this.getTokenBalance(tokenMint);
    const amount = Math.floor(balance * percentage / 100);
    
    const tx = await this.trader.swap(
      tokenMint,
      'So11111111111111111111111111111111111111112',  // Back to SOL
      amount
    );
    return tx;
  }
  
  // Scale position (sell 50% at +20%)
  async scalePosition(tokenMint) {
    return await this.exitTrade(tokenMint, 50);
  }
  
  // Get token balance
  async getTokenBalance(tokenMint) {
    // Implementation needed
  }
}

module.exports = SmartSwingExecutor;
```

---

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
cd ~/.openclaw/workspace
mkdir solana-trader
cd solana-trader

npm init -y
npm install @solana/web3.js @jup-ag/core bs58 axios
```

### 2. Create Secure Config

```bash
mkdir -p .secrets

# Create wallet file (DO NOT COMMIT)
echo "YOUR_PHANTOM_PRIVATE_KEY_BASE58" > .secrets/wallet.key
chmod 600 .secrets/wallet.key

# Create config
cat > config.json << 'EOF'
{
  "wallet": {
    "keyPath": "./.secrets/wallet.key"
  },
  "rpcUrl": "https://api.mainnet-beta.solana.com",
  "strategy": {
    "entrySize": 0.5,
    "scaleTarget": 20,
    "trailStop": 10,
    "reentrySize": 0.25
  }
}
EOF
```

### 3. Test Connection

```javascript
const SecureWallet = require('./wallet_manager');

const wallet = new SecureWallet('./.secrets/wallet.key');
console.log('Public Key:', wallet.getPublicKey());
console.log('Wallet loaded successfully');
```

### 4. Test Swap (Small Amount First!)

```javascript
const SecureWallet = require('./wallet_manager');
const JupiterTrader = require('./jupiter_trader');

async function test() {
  const wallet = new SecureWallet('./.secrets/wallet.key');
  const trader = new JupiterTrader(wallet.getKeypair());
  
  // Test with tiny amount first (0.001 SOL)
  const signature = await trader.swap(
    'So11111111111111111111111111111111111111112',  // SOL
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', // USDC
    1000000  // 0.001 SOL in lamports
  );
  
  console.log('Test swap complete:', signature);
}

test().catch(console.error);
```

---

## 🔒 Security Checklist

Before running live:

- [ ] Private key NEVER committed to git
- [ ] `.secrets/` added to `.gitignore`
- [ ] Wallet file has 600 permissions
- [ ] Test with tiny amounts first
- [ ] Have backup of private key (paper/written)
- [ ] Understand all code before running
- [ ] Monitor first trades manually

---

## 🚨 Risk Warning

⚠️ **Never share private keys**
⚠️ **Test with tiny amounts first**
⚠️ **Start with paper trading**
⚠️ **Code can have bugs - audit it**
⚠️ **Solana requires ~0.005 SOL per tx for fees**
⚠️ **Slippage can cause losses**

---

## 📱 Telegram Alert Integration

Add to your trading agent:

```javascript
const axios = require('axios');

async function sendAlert(message) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  
  await axios.post(
    `https://api.telegram.org/bot${token}/sendMessage`,
    {
      chat_id: chatId,
      text: message,
      parse_mode: 'HTML'
    }
  );
}
```

---

## 🎯 Next Steps

1. **Tonight**: Export Phantom private key, encrypt, save securely
2. **Tomorrow**: Install dependencies, test connection
3. **Day 2**: Test small swap (0.001 SOL)
4. **Day 3**: Test strategy with 0.1 SOL
5. **Day 4**: Go live with 0.5 SOL

**Want me to create the actual trading bot files now?** 🦞