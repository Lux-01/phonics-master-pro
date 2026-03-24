const axios = require('axios');
const fs = require('fs');
const { Connection, Keypair, Transaction, VersionedTransaction, PublicKey, sendAndConfirmTransaction } = require('@solana/web3.js');

// Load Helius RPC URL
const heliusKey = fs.readFileSync('./.secrets/helius.key', 'utf8').trim();
const HELIUS_RPC = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;

// Load config
const CONFIG = {
  jupiterApiUrl: 'https://api.jup.ag/swap/v1',
  rpcEndpoint: HELIUS_RPC,  // Helius RPC - fast & reliable
  walletKeyPath: './.secrets/wallet.key',
  slippageBps: 50, // 0.5%
  priorityFee: 50000 // 0.00005 SOL priority fee
};

// Token mints
const TOKENS = {
  SOL: {
    mint: 'So11111111111111111111111111111111111111112',
    decimals: 9,
    symbol: 'SOL'
  },
  USDC: {
    mint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    decimals: 6,
    symbol: 'USDC'
  },
  USDT: {
    mint: 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    decimals: 6,
    symbol: 'USDT'
  },
  BONK: {
    mint: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    decimals: 5,
    symbol: 'BONK'
  },
  WIF: {
    mint: 'EKpQGSJtjGFqKckxLSpxUtMJufH1R9kB2YrJ1ZC86yX',
    decimals: 6,
    symbol: 'WIF'
  }
};

class JupiterTrader {
  constructor() {
    this.apiKey = null;
    this.keypair = null;
    this.connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
    this.walletAddress = null;
    this.tradeLog = [];
  }

  async init() {
    try {
      // Load API key
      this.apiKey = fs.readFileSync('./.secrets/jupiter.key', 'utf8').trim();
      console.log('✅ Jupiter API key loaded');

      // Load wallet
      const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
      const secretKeyBytes = Buffer.from(secretKey, 'base64');
      
      // Try base64 first, then try bs58
      try {
        this.keypair = Keypair.fromSecretKey(secretKeyBytes);
      } catch (e) {
        // If base64 fails, the key might be bs58 encoded
        const bs58 = require('bs58');
        const decoded = bs58.decode(secretKey);
        this.keypair = Keypair.fromSecretKey(decoded);
      }
      
      this.walletAddress = this.keypair.publicKey.toString();
      console.log(`✅ Wallet loaded: ${this.walletAddress.substring(0, 8)}...${this.walletAddress.slice(-4)}`);

      // Check SOL balance (optional - may fail on some RPCs)
      try {
        const balance = await this.connection.getBalance(this.keypair.publicKey);
        const solBalance = balance / 1e9;
        console.log(`💰 Balance: ${solBalance.toFixed(4)} SOL`);

        if (solBalance < 0.01) {
          console.log('⚠️  Warning: Low SOL balance for transactions');
        }
      } catch (e) {
        console.log('ℹ️  RPC limited - balance check skipped (swap will still work)');
      }

      return true;
    } catch (e) {
      console.error('❌ Init failed:', e.message);
      return false;
    }
  }

  // Convert human amount to base units
  toBaseUnits(amount, decimals) {
    return Math.floor(amount * Math.pow(10, decimals)).toString();
  }

  // Get swap quote
  async getQuote(inputMint, outputMint, amount, exactIn = true) {
    try {
      const url = exactIn 
        ? `${CONFIG.jupiterApiUrl}/quote`
        : `${CONFIG.jupiterApiUrl}/quote`;
      
      const params = new URLSearchParams({
        inputMint,
        outputMint,
        amount: amount.toString(),
        slippageBps: CONFIG.slippageBps.toString(),
        onlyDirectRoutes: 'false'
      });

      const res = await axios.get(`${url}?${params.toString()}`, {
        headers: {
          'x-api-key': this.apiKey,
          'Accept': 'application/json'
        },
        timeout: 15000
      });

      return res.data;
    } catch (e) {
      const errMsg = e.response?.data?.message || e.message;
      console.error('Quote error:', errMsg);
      return null;
    }
  }

  // Build swap transaction
  async buildSwapTransaction(quoteResponse) {
    try {
      const url = `${CONFIG.jupiterApiUrl}/swap`;
      
      const body = {
        quoteResponse,
        userPublicKey: this.walletAddress,
        wrapAndUnwrapSol: true,
        prioritizationFeeLamports: CONFIG.priorityFee
      };

      const res = await axios.post(url, body, {
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        },
        timeout: 15000
      });

      return res.data;
    } catch (e) {
      const errMsg = e.response?.data?.message || e.message;
      console.error('Build swap error:', errMsg);
      return null;
    }
  }

  // Execute swap
  async executeSwap(swapTransaction) {
    try {
      // Deserialize transaction
      const serializedTx = Buffer.from(swapTransaction.swapTransaction, 'base64');
      const transaction = VersionedTransaction.deserialize(serializedTx);

      // Sign transaction
      transaction.sign([this.keypair]);

      // Send transaction
      const signature = await this.connection.sendTransaction(transaction, {
        maxRetries: 3,
        skipPreflight: false
      });

      console.log(`📤 Transaction sent: ${signature}`);
      
      // Wait for confirmation
      console.log('⏳ Waiting for confirmation...');
      await this.connection.confirmTransaction(signature, 'confirmed');
      console.log(`✅ Transaction confirmed!`);

      return signature;
    } catch (e) {
      console.error('Execute swap error:', e.message);
      return null;
    }
  }

  // Full swap flow
  async swap(inputToken, outputToken, amount) {
    console.log(`\n🔄 Swap: ${amount} ${inputToken.symbol} → ${outputToken.symbol}`);
    
    const amountInBase = this.toBaseUnits(amount, inputToken.decimals);
    console.log(`   Amount (base): ${amountInBase}`);

    // Get quote
    console.log('📊 Getting quote...');
    const quote = await this.getQuote(inputToken.mint, outputToken.mint, amountInBase);
    
    if (!quote) {
      console.log('❌ Failed to get quote');
      return null;
    }

    // Calculate output amount
    const outAmount = parseFloat(quote.outAmount) / Math.pow(10, outputToken.decimals);
    const inAmount = parseFloat(quote.inAmount) / Math.pow(10, inputToken.decimals);
    
    console.log(`   Input: ${inAmount} ${inputToken.symbol}`);
    console.log(`   Output: ${outAmount.toFixed(6)} ${outputToken.symbol}`);
    console.log(`   Routes: ${quote.routePlan?.length || 1}`);

    // Build transaction
    console.log('🔨 Building transaction...');
    const swapTx = await this.buildSwapTransaction(quote);
    
    if (!swapTx) {
      console.log('❌ Failed to build transaction');
      return null;
    }

    // Execute
    console.log('🚀 Executing...');
    const signature = await this.executeSwap(swapTx);
    
    if (signature) {
      console.log(`\n✅ Swap complete!`);
      console.log(`   TX: https://solscan.io/tx/${signature}`);
      
      // Log trade
      this.tradeLog.push({
        timestamp: new Date().toISOString(),
        input: { token: inputToken.symbol, amount: inAmount },
        output: { token: outputToken.symbol, amount: outAmount },
        signature,
        explorer: `https://solscan.io/tx/${signature}`
      });
      
      this.saveTradeLog();
      
      return signature;
    }

    return null;
  }

  // Buy token with SOL
  async buy(tokenSymbol, solAmount) {
    const token = TOKENS[tokenSymbol.toUpperCase()];
    if (!token) {
      console.log(`❌ Unknown token: ${tokenSymbol}`);
      return null;
    }
    
    return await this.swap(TOKENS.SOL, token, solAmount);
  }

  // Sell token for SOL
  async sell(tokenSymbol, tokenAmount) {
    const token = TOKENS[tokenSymbol.toUpperCase()];
    if (!token) {
      console.log(`❌ Unknown token: ${tokenSymbol}`);
      return null;
    }
    
    return await this.swap(token, TOKENS.SOL, tokenAmount);
  }

  // Sell all of a token
  async sellAll(tokenSymbol) {
    const token = TOKENS[tokenSymbol.toUpperCase()];
    if (!token) {
      console.log(`❌ Unknown token: ${tokenSymbol}`);
      return null;
    }

    try {
      // Get token account balance
      const tokenAccounts = await this.connection.getParsedTokenAccountsByOwner(
        this.keypair.publicKey,
        { mint: new PublicKey(token.mint) }
      );

      if (tokenAccounts.value.length === 0) {
        console.log(`❌ No ${tokenSymbol} balance found`);
        return null;
      }

      const balance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
      console.log(`${tokenSymbol} balance: ${balance}`);

      if (balance <= 0) {
        console.log(`❌ Zero ${tokenSymbol} balance`);
        return null;
      }

      return await this.sell(tokenSymbol, balance);
    } catch (e) {
      console.error('Sell all error:', e.message);
      return null;
    }
  }

  // Get token balance
  async getBalance(tokenSymbol) {
    if (tokenSymbol.toUpperCase() === 'SOL') {
      const balance = await this.connection.getBalance(this.keypair.publicKey);
      return balance / 1e9;
    }

    const token = TOKENS[tokenSymbol.toUpperCase()];
    if (!token) return null;

    try {
      const tokenAccounts = await this.connection.getParsedTokenAccountsByOwner(
        this.keypair.publicKey,
        { mint: new PublicKey(token.mint) }
      );

      if (tokenAccounts.value.length === 0) return 0;
      
      return tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
    } catch (e) {
      return 0;
    }
  }

  // Save trade log
  saveTradeLog() {
    try {
      fs.writeFileSync('./trade_log.json', JSON.stringify(this.tradeLog, null, 2));
    } catch (e) {
      // Ignore save errors
    }
  }

  // Show portfolio
  async showPortfolio() {
    console.log('\n📊 Portfolio:');
    
    const solBalance = await this.getBalance('SOL');
    console.log(`  SOL: ${solBalance.toFixed(4)}`);

    for (const [symbol, token] of Object.entries(TOKENS)) {
      if (symbol === 'SOL') continue;
      const balance = await this.getBalance(symbol);
      if (balance > 0) {
        console.log(`  ${symbol}: ${balance.toFixed(4)}`);
      }
    }
  }
}

// CLI interface
async function main() {
  const trader = new JupiterTrader();
  
  if (!await trader.init()) {
    console.log('Failed to initialize trader');
    process.exit(1);
  }

  const args = process.argv.slice(2);
  const cmd = args[0];
  const params = args.slice(1);

  switch (cmd) {
    case 'balance':
      const symbol = params[0] || 'SOL';
      const bal = await trader.getBalance(symbol);
      console.log(`${symbol} balance: ${bal !== null ? bal.toFixed(6) : 'N/A'}`);
      break;

    case 'buy':
      if (params.length < 2) {
        console.log('Usage: node jupiter_trader.js buy <TOKEN> <SOL_AMOUNT>');
        return;
      }
      await trader.buy(params[0], parseFloat(params[1]));
      break;

    case 'sell':
      if (params.length < 2) {
        console.log('Usage: node jupiter_trader.js sell <TOKEN> <AMOUNT>');
        return;
      }
      await trader.sell(params[0], parseFloat(params[1]));
      break;

    case 'sellall':
      if (params.length < 1) {
        console.log('Usage: node jupiter_trader.js sellall <TOKEN>');
        return;
      }
      await trader.sellAll(params[0].toUpperCase());
      break;

    case 'portfolio':
      await trader.showPortfolio();
      break;

    case 'quote':
      if (params.length < 3) {
        console.log('Usage: node jupiter_trader.js quote <INPUT> <OUTPUT> <AMOUNT>');
        return;
      }
      const input = TOKENS[params[0].toUpperCase()];
      const output = TOKENS[params[1].toUpperCase()];
      const amt = parseFloat(params[2]);
      
      if (!input || !output) {
        console.log('Unknown token. Available:', Object.keys(TOKENS).join(', '));
        return;
      }
      
      const amountInBase = trader.toBaseUnits(amt, input.decimals);
      const quote = await trader.getQuote(input.mint, output.mint, amountInBase);
      
      if (quote) {
        const outAmt = parseFloat(quote.outAmount) / Math.pow(10, output.decimals);
        console.log(`Quote: ${amt} ${input.symbol} → ${outAmt.toFixed(6)} ${output.symbol}`);
      }
      break;

    default:
      console.log('Jupiter Trader Commands:');
      console.log('  node jupiter_trader.js balance [TOKEN]');
      console.log('  node jupiter_trader.js buy <TOKEN> <SOL_AMOUNT>');
      console.log('  node jupiter_trader.js sell <TOKEN> <AMOUNT>');
      console.log('  node jupiter_trader.js sellall <TOKEN>');
      console.log('  node jupiter_trader.js portfolio');
      console.log('  node jupiter_trader.js quote <INPUT> <OUTPUT> <AMOUNT>');
      console.log('\nAvailable tokens:', Object.keys(TOKENS).join(', '));
  }
}

main().catch(console.error);
