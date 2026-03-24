const axios = require('axios');
const fs = require('fs');
const { Connection, Keypair, VersionedTransaction, PublicKey } = require('@solana/web3.js');

// Config
const heliusKey = fs.readFileSync('./.secrets/helius.key', 'utf8').trim();
const CONFIG = {
  jupiterApiUrl: 'https://api.jup.ag/swap/v1',
  rpcEndpoint: `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`,
  walletKeyPath: './.secrets/wallet.key',
  jupiterApiKeyPath: './.secrets/jupiter.key'
};

// Known tokens with high liquidity
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
  }
};

class JupiterSwapTester {
  constructor() {
    this.connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
    this.keypair = null;
    this.apiKey = null;
    this.walletAddress = null;
  }

  init() {
    // Load keys
    this.apiKey = fs.readFileSync(CONFIG.jupiterApiKeyPath, 'utf8').trim();
    const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
    
    // Decode key (try base64 first, then bs58)
    try {
      const secretKeyBytes = Buffer.from(secretKey, 'base64');
      this.keypair = Keypair.fromSecretKey(secretKeyBytes);
    } catch (e) {
      const bs58 = require('bs58');
      this.keypair = Keypair.fromSecretKey(bs58.decode(secretKey));
    }
    
    this.walletAddress = this.keypair.publicKey.toString();
    console.log(`✅ Wallet: ${this.walletAddress.substring(0,8)}...${this.walletAddress.slice(-4)}\n`);
  }

  // Get quote
  async getQuote(inputMint, outputMint, amountLamports) {
    const url = `${CONFIG.jupiterApiUrl}/quote`;
    const params = new URLSearchParams({
      inputMint,
      outputMint,
      amount: amountLamports.toString(),
      slippageBps: '50'
    });

    const res = await axios.get(`${url}?${params.toString()}`, {
      headers: { 'x-api-key': this.apiKey },
      timeout: 15000
    });

    return res.data;
  }

  // Build swap transaction
  async buildSwap(quoteResponse) {
    const url = `${CONFIG.jupiterApiUrl}/swap`;
    
    const body = {
      quoteResponse,
      userPublicKey: this.walletAddress,
      wrapAndUnwrapSol: true,
      prioritizationFeeLamports: 50000 // 0.00005 SOL
    };

    const res = await axios.post(url, body, {
      headers: { 
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey 
      },
      timeout: 15000
    });

    return res.data;
  }

  // Execute swap
  async executeSwap(swapResponse) {
    // Deserialize transaction
    const serializedTx = Buffer.from(swapResponse.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);

    // Sign
    transaction.sign([this.keypair]);

    console.log('📤 Sending transaction...');
    
    // Send
    const signature = await this.connection.sendTransaction(transaction, {
      maxRetries: 3,
      skipPreflight: false
    });

    console.log(`⏳ Waiting for confirmation...`);
    console.log(`   TX: ${signature}`);
    console.log(`   Explorer: https://solscan.io/tx/${signature}`);

    // Confirm
    await this.connection.confirmTransaction(signature, 'confirmed');
    
    return signature;
  }

  // Test quote
  async testQuote() {
    console.log('🧪 Test 1: Get Quote');
    const amount = 100000; // 0.0001 SOL
    const quote = await this.getQuote(
      TOKENS.SOL.mint,
      TOKENS.USDC.mint,
      amount
    );
    const usdcAmount = parseFloat(quote.outAmount) / 1e6;
    console.log(`   ✅ Quote: 0.0001 SOL → ${usdcAmount.toFixed(6)} USDC`);
    return quote;
  }

  // Test build swap
  async testBuildSwap(quote) {
    console.log('\n🧪 Test 2: Build Swap Transaction');
    const swap = await this.buildSwap(quote);
    console.log(`   ✅ Transaction built (${swap.swapTransaction.length} bytes)`);
    return swap;
  }

  // Test execute (COMMENTED OUT - requires small amount of SOL)
  async testExecuteSwap(swap) {
    console.log('\n🧪 Test 3: Execute Swap (SKIPPED - Uncomment to execute live trade)');
    console.log('   Transaction is ready to submit');
    console.log('   Uncomment line below to execute actual swap\n');
    
    // COMMENTED OUT FOR SAFETY
    // const signature = await this.executeSwap(swap);
    // console.log(`   ✅ Transaction confirmed: ${signature}`);
    
    console.log('   [Would execute: 0.0001 SOL → USDC]');
    return null;
  }

  // Full test
  async runTests() {
    console.log('=== Jupiter Swap Tests ===\n');
    
    try {
      this.init();
      
      // Test 1: Quote
      const quote = await this.testQuote();
      
      // Test 2: Build
      const swap = await this.testBuildSwap(quote);
      
      // Test 3: Execute (commented out)
      await this.testExecuteSwap(swap);
      
      console.log('\n✅ All tests passed!');
      console.log('\nTo execute a real trade:');
      console.log('  Uncomment the execute line in testExecuteSwap()');
      console.log('  Run: node jupiter_swap_test.js');
      
    } catch (e) {
      console.error('\n❌ Test failed:', e.message);
      if (e.response) {
        console.error('   API Error:', e.response.data);
      }
    }
  }
}

// CLI
const tester = new JupiterSwapTester();
tester.runTests();
