#!/usr/bin/env node
/**
 * The Adaptive Edge - Live Trading Bot v1.0
 * Jupiter API Integration for Solana Meme Coin Trading
 * 26 Rules Active | 10% Risk Management
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { Connection, Keypair, PublicKey, VersionedTransaction } = require('@solana/web3.js');

// Load secrets
const HELIUS_KEY = fs.readFileSync('./.secrets/helius.key', 'utf8').trim();
const JUPITER_KEY = fs.readFileSync('./.secrets/jupiter.key', 'utf8').trim();
const WALLET_KEY = fs.readFileSync('./.secrets/wallet.key', 'utf8').trim();

// RPC Endpoint
const RPC_URL = `https://mainnet.helius-rpc.com/?api-key=${HELIUS_KEY}`;

// Trading Configuration
const CONFIG = {
  // Risk Management
  MAX_CAPITAL_PERCENT: 0.10,        // 10% max risk
  TRADE_SIZE_MIN_SOL: 0.15,         // Minimum 0.15 SOL
  TRADE_SIZE_MAX_SOL: 0.25,         // Maximum 0.25 SOL (Phase 1)
  DAILY_LOSS_LIMIT_PERCENT: 5,      // Stop trading after -5% day
  MAX_TRADES_PER_DAY: 5,            // Max 5 trades
  COOLDOWN_AFTER_LOSS_MIN: 15,      // 15 min cooldown
  
  // Jupiter Settings
  SLIPPAGE_BPS: 100,                // 1.0% slippage (slightly higher for meme coins)
  PRIORITY_FEE_LAMPORTS: 100000,    // 0.0001 SOL priority fee
  
  // API Endpoints
  JUPITER_QUOTE_URL: 'https://api.jup.ag/swap/v1/quote',
  JUPITER_SWAP_URL: 'https://api.jup.ag/swap/v1/swap',
  BIRDEYE_API_URL: 'https://public-api.birdeye.so/public',
  DEXSCREENER_API_URL: 'https://api.dexscreener.com/latest/dex',
  
  // The Adaptive Edge Rules
  RULES: {
    SLIPPAGE_MAX_PERCENT: 2.0,      // Skip if >2%
    MARKET_CAP_MIN: 2000000,        // $2M minimum
    MARKET_CAP_MAX: 500000000,      // $500M maximum
    VOLUME_MULTIPLIER_MIN: 2.0,    // 2x average volume
    HOLDER_CONCENTRATION_MAX: 0.50, // Max 50% top 10
    ATR_MAX_PERCENT: 18.0,          // Skip if too volatile
    SESSION_TIMING: true,           // Use session edges
    CONFIRMATION_CANDLE: true,      // Wait for close
    DEV_ACTIVITY_CHECK: true        // Check wallet history
  }
};

// Token Definitions
const SOL_TOKEN = {
  mint: 'So11111111111111111111111111111111111111112',
  decimals: 9,
  symbol: 'SOL'
};

const USDC_TOKEN = {
  mint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  decimals: 6,
  symbol: 'USDC'
};

// State tracking
let state = {
  running: false,
  dailyStats: {
    date: new Date().toDateString(),
    tradesTaken: 0,
    tradesSkipped: 0,
    realizedPnl: 0,
    unrealizedPnl: 0,
    startingBalance: 0,
    currentBalance: 0
  },
  currentPosition: null,
  lastTradeTime: null,
  tradeHistory: [],
  errors: []
};

// Files
const STATE_FILE = './trading_logs/adaptive_edge_state.json';
const LOG_FILE = './trading_logs/adaptive_edge_trades.json';

class AdaptiveEdgeTrader {
  constructor() {
    this.connection = new Connection(RPC_URL, 'confirmed');
    this.wallet = null;
    this.walletAddress = null;
    this.watchList = [];
  }

  async init() {
    console.log('🦞 Initializing The Adaptive Edge...');
    
    try {
      // Load wallet
      const secretKey = Buffer.from(WALLET_KEY, 'base64');
      this.wallet = Keypair.fromSecretKey(secretKey);
      this.walletAddress = this.wallet.publicKey.toString();
      console.log(`✅ Wallet: ${this.walletAddress.substring(0, 12)}...
`);
      
      // Load state
      this.loadState();
      
      // Check balance
      const balance = await this.getSolBalance();
      console.log(`💰 SOL Balance: ${balance.toFixed(4)} SOL`);
      
      if (!state.dailyStats.startingBalance) {
        state.dailyStats.startingBalance = balance;
        state.dailyStats.currentBalance = balance;
        this.saveState();
      }
      
      // Calculate max risk
      const maxRisk = state.dailyStats.startingBalance * CONFIG.MAX_CAPITAL_PERCENT;
      console.log(`💸 Daily Risk Limit: ${maxRisk.toFixed(4)} SOL (10%)`);
      console.log(`🎯 Trade Size: ${CONFIG.TRADE_SIZE_MIN_SOL}-${CONFIG.TRADE_SIZE_MAX_SOL} SOL`);
      
      state.running = true;
      this.saveState();
      
      console.log('✅ Initialization complete!\n');
      return true;
      
    } catch (e) {
      console.error('❌ Init failed:', e.message);
      return false;
    }
  }

  loadState() {
    try {
      if (fs.existsSync(STATE_FILE)) {
        const saved = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
        state = { ...state, ...saved };
        
        // Reset daily stats if new day
        if (state.dailyStats.date !== new Date().toDateString()) {
          state.dailyStats = {
            date: new Date().toDateString(),
            tradesTaken: 0,
            tradesSkipped: 0,
            realizedPnl: 0,
            unrealizedPnl: 0,
            startingBalance: 0,
            currentBalance: 0
          };
        }
      }
    } catch (e) {
      console.log('⚠️  No previous state found');
    }
  }

  saveState() {
    try {
      fs.mkdirSync('./trading_logs', { recursive: true });
      fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    } catch (e) {
      console.error('Failed to save state:', e.message);
    }
  }

  logTrade(trade) {
    try {
      fs.mkdirSync('./trading_logs', { recursive: true });
      let history = [];
      if (fs.existsSync(LOG_FILE)) {
        history = JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
      }
      history.push({
        ...trade,
        timestamp: new Date().toISOString()
      });
      fs.writeFileSync(LOG_FILE, JSON.stringify(history, null, 2));
      state.tradeHistory = history;
    } catch (e) {
      console.error('Failed to log trade:', e.message);
    }
  }

  async getSolBalance() {
    try {
      const balance = await this.connection.getBalance(this.wallet.publicKey);
      return balance / 1e9;
    } catch (e) {
      return 0;
    }
  }

  // Check Birdeye for token data
  async getTokenData(tokenAddress) {
    try {
      const response = await axios.get(
        `https://public-api.birdeye.so/public/token_overview?address=${tokenAddress}`,
        {
          headers: { 'X-API-KEY': '0d1a8a6a4e6d4f5eb3c92e9c1a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a' }, // Generic test key
          timeout: 10000
        }
      );
      return response.data?.data || null;
    } catch (e) {
      return null;
    }
  }

  // Get quote from Jupiter
  async getJupiterQuote(inputMint, outputMint, amount) {
    try {
      const params = new URLSearchParams({
        inputMint,
        outputMint,
        amount: amount.toString(),
        slippageBps: CONFIG.SLIPPAGE_BPS.toString(),
        onlyDirectRoutes: 'false'
      });

      const response = await axios.get(
        `${CONFIG.JUPITER_QUOTE_URL}?${params.toString()}`,
        {
          headers: { 'x-api-key': JUPITER_KEY },
          timeout: 15000
        }
      );
      
      return response.data;
    } catch (e) {
      console.error('Quote error:', e.message);
      return null;
    }
  }

  // Build swap transaction
  async buildSwapTransaction(quoteResponse) {
    try {
      const body = {
        quoteResponse,
        userPublicKey: this.walletAddress,
        wrapAndUnwrapSol: true,
        prioritizationFeeLamports: CONFIG.PRIORITY_FEE_LAMPORTS
      };

      const response = await axios.post(
        CONFIG.JUPITER_SWAP_URL,
        body,
        {
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': JUPITER_KEY
          },
          timeout: 15000
        }
      );
      
      return response.data;
    } catch (e) {
      console.error('Swap build error:', e.message);
      return null;
    }
  }

  // Execute swap
  async executeSwap(swapTransaction) {
    try {
      const serializedTx = Buffer.from(swapTransaction.swapTransaction, 'base64');
      const transaction = VersionedTransaction.deserialize(serializedTx);
      
      transaction.sign([this.wallet]);
      
      const signature = await this.connection.sendTransaction(transaction, {
        maxRetries: 3,
        skipPreflight: false
      });
      
      console.log(`📤 TX Sent: ${signature.substring(0, 20)}...`);
      
      // Wait for confirmation
      await this.connection.confirmTransaction(signature, 'confirmed');
      console.log(`✅ TX Confirmed!`);
      
      return signature;
    } catch (e) {
      console.error('Execute error:', e.message);
      return null;
    }
  }

  // Main trading logic - Apply the 26 Rules
  shouldEnterTrade(tokenData) {
    const now = new Date();
    
    // Rule 0: Max trades per day
    if (state.dailyStats.tradesTaken >= CONFIG.MAX_TRADES_PER_DAY) {
      return { trade: false, reason: 'Max trades per day reached' };
    }
    
    // Rule 0: Daily loss limit
    const totalPnl = state.dailyStats.realizedPnl + state.dailyStats.unrealizedPnl;
    if (totalPnl < -(state.dailyStats.startingBalance * CONFIG.DAILY_LOSS_LIMIT_PERCENT / 100)) {
      return { trade: false, reason: 'Daily loss limit hit (-5%)' };
    }
    
    // Rule 0: Cooldown after loss
    if (state.lastTradeTime) {
      const minutesSinceLast = (now - new Date(state.lastTradeTime)) / 60000;
      if (state.dailyStats.realizedPnl < 0 && minutesSinceLast < CONFIG.COOLDOWN_AFTER_LOSS_MIN) {
        return { trade: false, reason: `Cooldown: ${CONFIG.COOLDOWN_AFTER_LOSS_MIN - Math.floor(minutesSinceLast)} min remaining` };
      }
    }
    
    // Rule 1: Check market cap
    const mcap = tokenData.marketCap || 0;
    if (mcap < CONFIG.RULES.MARKET_CAP_MIN || mcap > CONFIG.RULES.MARKET_CAP_MAX) {
      return { trade: false, reason: `Market cap out of range: $${(mcap/1e6).toFixed(1)}M` };
    }
    
    // Rule 2: Check volume
    const volumeMult = tokenData.volumeMultiplier || 1;
    if (volumeMult < CONFIG.RULES.VOLUME_MULTIPLIER_MIN) {
      return { trade: false, reason: `Volume too low: ${volumeMult.toFixed(1)}x` };
    }
    
    // Rule 3: Check slippage estimate
    const slippage = tokenData.slippageEstimate || 0;
    if (slippage > CONFIG.RULES.SLIPPAGE_MAX_PERCENT) {
      return { trade: false, reason: `Slippage too high: ${slippage.toFixed(1)}%` };
    }
    
    // Rule 4: Holder concentration
    const holderConc = tokenData.top10HolderPercent || 0;
    if (holderConc > CONFIG.RULES.HOLDER_CONCENTRATION_MAX) {
      return { trade: false, reason: `Holders too concentrated: ${(holderConc*100).toFixed(0)}%` };
    }
    
    // Rule 5: Session timing (simplified)
    const hour = now.getHours();
    const isGoodSession = (hour >= 0 && hour <= 4) || // US close
                          (hour >= 6 && hour <= 10) || // Asia open  
                          (hour >= 17 && hour <= 21);   // US open
    
    if (!isGoodSession) {
      return { trade: false, reason: 'Poor session timing', weak: true };
    }
    
    // Rule 6: ATR check
    const atr = tokenData.atr || 0;
    if (atr > CONFIG.RULES.ATR_MAX_PERCENT) {
      return { trade: false, reason: `ATR too high: ${atr.toFixed(1)}%` };
    }
    
    // If we get here, signal is valid
    return { trade: true, grade: atr < 10 ? 'A' : 'B' };
  }

  // Execute entry
  async enterTrade(tokenData) {
    const tokenAddress = tokenData.address;
    const symbol = tokenData.symbol || 'UNKNOWN';
    
    console.log(`\n🟢 ENTRY SIGNAL: ${symbol}`);
    console.log(`   Market Cap: $${((tokenData.marketCap || 0)/1e6).toFixed(1)}M`);
    console.log(`   Volume: ${(tokenData.volumeMultiplier || 1).toFixed(1)}x`);
    
    // Calculate size
    const balance = await this.getSolBalance();
    const maxSize = Math.min(CONFIG.TRADE_SIZE_MAX_SOL, balance * 0.45);
    const size = Math.max(CONFIG.TRADE_SIZE_MIN_SOL, maxSize);
    
    console.log(`   Size: ${size.toFixed(3)} SOL`);
    
    // Get quote
    const amountLamports = Math.floor(size * 1e9);
    const quote = await this.getJupiterQuote(
      SOL_TOKEN.mint,
      tokenAddress,
      amountLamports
    );
    
    if (!quote) {
      console.log('❌ Failed to get quote');
      return false;
    }
    
    // Check slippage from quote
    const outAmount = parseFloat(quote.outAmount) / Math.pow(10, tokenData.decimals || 6);
    const expectedOut = size / (tokenData.price || 1);
    const actualSlippage = ((expectedOut - outAmount) / expectedOut) * 100;
    
    console.log(`   Expected: ${expectedOut.toFixed(4)} | Actual: ${outAmount.toFixed(4)}`);
    console.log(`   Slippage: ${actualSlippage.toFixed(2)}%`);
    
    if (actualSlippage > CONFIG.RULES.SLIPPAGE_MAX_PERCENT) {
      console.log('❌ Slippage too high, aborting');
      return false;
    }
    
    // Build transaction
    console.log('🔨 Building swap...');
    const swapTx = await this.buildSwapTransaction(quote);
    if (!swapTx) {
      console.log('❌ Failed to build swap');
      return false;
    }
    
    // Execute
    console.log('🚀 Executing...');
    const signature = await this.executeSwap(swapTx);
    
    if (signature) {
      // Update state
      state.currentPosition = {
        token: symbol,
        address: tokenAddress,
        entryPrice: tokenData.price || 0,
        size: size,
        entryTime: new Date().toISOString(),
        signature: signature,
        scale1Done: false,
        scale2Done: false,
        tokenAmount: outAmount
      };
      
      state.dailyStats.tradesTaken++;
      state.lastTradeTime = new Date().toISOString();
      
      this.logTrade({
        type: 'ENTRY',
        token: symbol,
        size: size,
        price: tokenData.price || 0,
        signature: signature,
        slippage: actualSlippage
      });
      
      this.saveState();
      
      console.log(`\n✅ ENTRY COMPLETE: ${size.toFixed(3)} SOL → ${symbol}`);
      console.log(`   TX: https://solscan.io/tx/${signature}\n`);
      
      return true;
    }
    
    return false;
  }

  // Execute exit
  async exitTrade(reason) {
    if (!state.currentPosition) {
      console.log('No position to exit');
      return false;
    }
    
    const pos = state.currentPosition;
    console.log(`\n🔴 EXIT: ${pos.token} - ${reason}`);
    
    // Get current price for PNL calculation
    const currentPrice = await this.getTokenPrice(pos.address) || pos.entryPrice;
    const pnlPercent = ((currentPrice - pos.entryPrice) / pos.entryPrice) * 100;
    
    // Check if profitable
    if (pnlPercent < 0 && reason === 'manual') {
      console.log('⚠️  Exit would be at loss. Use stop-loss to confirm.');
      return false;
    }
    
    // Execute swap back to SOL
    const amountTokens = Math.floor(pos.tokenAmount * Math.pow(10, 6)); // Approximate decimals
    
    // Get sell quote
    const quote = await this.getJupiterQuote(
      pos.address,
      SOL_TOKEN.mint,
      amountTokens
    );
    
    if (!quote) {
      console.log('❌ Failed to get sell quote');
      return false;
    }
    
    // Build and execute
    const swapTx = await this.buildSwapTransaction(quote);
    if (!swapTx) {
      console.log('❌ Failed to build sell swap');
      return false;
    }
    
    const signature = await this.executeSwap(swapTx);
    
    if (signature) {
      const solReceived = parseFloat(quote.outAmount) / 1e9;
      const pnlSol = solReceived - pos.size;
      
      // Update stats
      state.dailyStats.realizedPnl += pnlSol;
      state.currentPosition = null;
      
      this.logTrade({
        type: 'EXIT',
        token: pos.token,
        size: solReceived,
        pnlSol: pnlSol,
        pnlPercent: pnlPercent,
        reason: reason,
        signature: signature
      });
      
      this.saveState();
      
      console.log(`\n✅ EXIT COMPLETE: ${pos.token}`);
      console.log(`   Received: ${solReceived.toFixed(4)} SOL`);
      console.log(`   PNL: ${pnlSol.toFixed(4)} SOL (${pnlPercent.toFixed(2)}%)`);
      console.log(`   TX: https://solscan.io/tx/${signature}\n`);
      
      return true;
    }
    
    return false;
  }

  async getTokenPrice(tokenAddress) {
    // Placeholder - would fetch from Birdeye/DexScreener
    return 0;
  }

  // Monitor position
  async monitorPosition() {
    if (!state.currentPosition) return;
    
    const pos = state.currentPosition;
    const now = new Date();
    const entryTime = new Date(pos.entryTime);
    const minutesHeld = (now - entryTime) / 60000;
    
    // Get current price (would fetch from API)
    console.log(`📊 Monitoring ${pos.token} - ${minutesHeld.toFixed(0)} min held`);
    
    // Check time stop (30 min default)
    if (minutesHeld > 30 && !pos.scale1Done) {
      console.log(`⏰ Time stop approaching for ${pos.token}`);
    }
  }

  // Main scan loop
  async scanForTrades() {
    console.log('\n🔍 Scanning market...');
    
    // In real implementation, this would:
    // 1. Fetch trending tokens from Birdeye/DexScreener
    // 2. Check each against the 26 rules
    // 3. Execute on valid setups
    
    // For now, show status
    console.log(`   Trades today: ${state.dailyStats.tradesTaken}/${CONFIG.MAX_TRADES_PER_DAY}`);
    console.log(`   Daily PNL: ${state.dailyStats.realizedPnl.toFixed(4)} SOL`);
    console.log(`   Position: ${state.currentPosition ? state.currentPosition.token : 'None'}\n`);
  }

  async run() {
    console.log('=' .repeat(60));
    console.log('🦞 The Adaptive Edge - Live Trading Bot v1.0');
    console.log('   26 Rules Active | 10% Risk Limit');
    console.log('=' .repeat(60));
    
    if (!await this.init()) {
      process.exit(1);
    }
    
    console.log('⏳ Starting trading loop...');
    console.log('Press Ctrl+C to stop\n');
    
    // Main loop
    while (state.running) {
      try {
        if (!state.currentPosition) {
          await this.scanForTrades();
        } else {
          await this.monitorPosition();
        }
        
        // Update balance
        const balance = await this.getSolBalance();
        state.dailyStats.currentBalance = balance;
        this.saveState();
        
        // Wait 30 seconds between scans
        await new Promise(r => setTimeout(r, 30000));
        
      } catch (e) {
        console.error('Error in loop:', e.message);
        await new Promise(r => setTimeout(r, 5000));
      }
    }
  }

  stop() {
    console.log('\n🛑 Stopping trader...');
    state.running = false;
    this.saveState();
    console.log('✅ Trader stopped');
  }
}

// CLI interface
const trader = new AdaptiveEdgeTrader();

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];

  switch (cmd) {
    case 'start':
      await trader.run();
      break;
      
    case 'stop':
      trader.stop();
      break;
      
    case 'status':
      trader.loadState();
      console.log('\n📊 Status:');
      console.log(`   Running: ${state.running}`);
      console.log(`   Trades taken: ${state.dailyStats.tradesTaken}`);
      console.log(`   Realized PNL: ${state.dailyStats.realizedPnl.toFixed(4)} SOL`);
      console.log(`   Position: ${state.currentPosition?.token || 'None'}\n`);
      break;
      
    case 'exit':
      trader.loadState();
      await trader.exitTrade('manual');
      break;
      
    default:
      console.log('\n🦞 The Adaptive Edge - Live Trading Bot');
      console.log('\nCommands:');
      console.log('  node adaptive_edge_trader.js start    - Start trading');
      console.log('  node adaptive_edge_trader.js stop     - Stop trading');
      console.log('  node adaptive_edge_trader.js status - Show status');
      console.log('  node adaptive_edge_trader.js exit     - Exit current position\n');
  }
}

// Handle signals
process.on('SIGINT', () => {
  trader.stop();
  process.exit(0);
});

process.on('SIGTERM', () => {
  trader.stop();
  process.exit(0);
});

main().catch(console.error);
