#!/usr/bin/env node
/**
 * Solana Trading Bot - Main Entry
 * Smart Swing Strategy v2.2 Execution Engine
 */

require('dotenv').config();
const fs = require('fs');
const bs58 = require('bs58');
const { Connection, Keypair, PublicKey } = require('@solana/web3.js');
const axios = require('axios');

// Constants
const SOL_MINT = 'So11111111111111111111111111111111111111112';
const RPC_URL = 'https://api.mainnet-beta.solana.com';
const JUPITER_QUOTE_URL = 'https://quote-api.jup.ag/v6/quote';
const JUPITER_SWAP_URL = 'https://quote-api.jup.ag/v6/swap';

class SecureWallet {
  constructor(keyPath) {
    if (!fs.existsSync(keyPath)) {
      throw new Error(`Wallet key not found at ${keyPath}`);
    }
    
    const privateKeyString = fs.readFileSync(keyPath, 'utf8').trim();
    const privateKey = bs58.decode(privateKeyString);
    this.keypair = Keypair.fromSecretKey(privateKey);
  }
  
  getPublicKey() {
    return this.keypair.publicKey;
  }
  
  getKeypair() {
    return this.keypair;
  }
}

class JupiterTrader {
  constructor(walletKeypair, connectionUrl = RPC_URL) {
    this.wallet = walletKeypair;
    this.connection = new Connection(connectionUrl, 'confirmed');
    this.quoteCache = new Map();
  }
  
  async getBalance() {
    const balance = await this.connection.getBalance(this.wallet.publicKey);
    return balance / 1e9;  // Convert lamports to SOL
  }
  
  async getTokenBalance(tokenMint) {
    try {
      const tokenAccounts = await this.connection.getTokenAccountsByOwner(
        this.wallet.publicKey,
        { mint: new PublicKey(tokenMint) }
      );
      
      if (tokenAccounts.value.length === 0) return 0;
      
      const accountInfo = await this.connection.getTokenAccountBalance(
        tokenAccounts.value[0].pubkey
      );
      return accountInfo.value.uiAmount || 0;
    } catch (e) {
      return 0;
    }
  }
  
  async getQuote(inputMint, outputMint, amount, slippageBps = 50) {
    try {
      const response = await axios.get(JUPITER_QUOTE_URL, {
        params: {
          inputMint,
          outputMint,
          amount: amount.toString(),
          slippageBps,
          onlyDirectRoutes: false,
          asLegacyTransaction: false
        },
        timeout: 10000
      });
      
      return response.data;
    } catch (error) {
      console.error('Quote error:', error.response?.data || error.message);
      throw error;
    }
  }
  
  async executeSwap(quoteResponse, wrapUnwrapSOL = true) {
    try {
      const response = await axios.post(JUPITER_SWAP_URL, {
        quoteResponse,
        userPublicKey: this.wallet.publicKey.toString(),
        wrapUnwrapSOL,
        prioritizationFeeLamports: 10000  // 0.001 SOL priority fee
      }, {
        timeout: 30000
      });
      
      return response.data;
    } catch (error) {
      console.error('Swap error:', error.response?.data || error.message);
      throw error;
    }
  }
  
  async sendTransaction(swapData) {
    const { swapTransaction } = swapData;
    
    // Deserialize
    const transaction = require('@solana/web3.js').VersionedTransaction.deserialize(
      Buffer.from(swapTransaction, 'base64')
    );
    
    // Sign
    transaction.sign([this.wallet]);
    
    // Serialize and send
    const signature = await this.connection.sendTransaction(transaction, {
      maxRetries: 3,
      skipPreflight: false,
      preflightCommitment: 'confirmed'
    });
    
    // Wait for confirmation
    await this.connection.confirmTransaction(signature, 'confirmed');
    
    return signature;
  }
  
  async buy(tokenMint, solAmount, slippage = 50) {
    console.log(`🟢 BUY: ${solAmount} SOL → Token`);
    
    // Get quote
    const lamports = Math.floor(solAmount * 1e9);
    const quote = await this.getQuote(SOL_MINT, tokenMint, lamports, slippage);
    
    console.log(`   Expected output: ${quote.outAmount} tokens`);
    console.log(`   Route: ${quote.routePlan?.length || 1} hops`);
    
    // Execute swap
    const swapData = await this.executeSwap(quote);
    const signature = await this.sendTransaction(swapData);
    
    console.log(`   ✅ Transaction: ${signature}`);
    return signature;
  }
  
  async sell(tokenMint, percentage = 100, slippage = 50) {
    console.log(`🔴 SELL: ${percentage}% of token → SOL`);
    
    // Get balance
    const balance = await this.getTokenBalance(tokenMint);
    if (balance <= 0) {
      throw new Error(`No balance for token ${tokenMint}`);
    }
    
    const amount = Math.floor(balance * (percentage / 100) * 1e6);  // Assuming 6 decimals
    
    // Get quote
    const quote = await this.getQuote(tokenMint, SOL_MINT, amount, slippage);
    
    console.log(`   Selling: ${amount / 1e6} tokens`);
    console.log(`   Expected SOL: ${quote.outAmount / 1e9} SOL`);
    
    // Execute swap
    const swapData = await this.executeSwap(quote);
    const signature = await this.sendTransaction(swapData);
    
    console.log(`   ✅ Transaction: ${signature}`);
    return signature;
  }
}

class SmartSwingBot {
  constructor(config) {
    this.wallet = new SecureWallet(config.wallet.keyPath);
    this.trader = new JupiterTrader(this.wallet.getKeypair());
    this.config = config;
    
    // Trading state
    this.state = {
      current: 'IDLE',  // IDLE, POSITION_OPEN, TRAILING, WAITING_REENTRY
      position: null,
      trades: []
    };
    
    // Load state if exists
    this.loadState();
  }
  
  loadState() {
    try {
      if (fs.existsSync('./state.json')) {
        this.state = JSON.parse(fs.readFileSync('./state.json'));
      }
    } catch (e) {
      console.log('No previous state found');
    }
  }
  
  saveState() {
    fs.writeFileSync('./state.json', JSON.stringify(this.state, null, 2));
  }
  
  async getWalletBalance() {
    const solBalance = await this.trader.getBalance();
    console.log(`💰 Wallet Balance: ${solBalance.toFixed(4)} SOL`);
    return solBalance;
  }
  
  async enterPosition(tokenMint, solAmount) {
    console.log(`\n📊 EXECUTING: Enter position for ${tokenMint}`);
    
    try {
      // Execute buy
      const tx = await this.trader.buy(tokenMint, solAmount);
      
      // Update state
      const price = await this.getTokenPrice(tokenMint);
      this.state.current = 'POSITION_OPEN';
      this.state.position = {
        token: tokenMint,
        entryPrice: price,
        entryAmount: solAmount,
        entryTx: tx,
        peakPrice: price,
        scaled: false,
        entryTime: Date.now()
      };
      
      this.logTrade('ENTRY', tokenMint, solAmount, tx);
      this.saveState();
      
      return { success: true, tx };
    } catch (error) {
      console.error('❌ Entry failed:', error.message);
      return { success: false, error: error.message };
    }
  }
  
  async scalePosition(percentage = 50) {
    if (!this.state.position) {
      throw new Error('No position to scale');
    }
    
    const token = this.state.position.token;
    console.log(`\n📊 EXECUTING: Scale ${percentage}% of position`);
    
    try {
      const tx = await this.trader.sell(token, percentage);
      
      this.state.position.scaled = true;
      this.logTrade('SCALE', token, percentage, tx);
      this.saveState();
      
      return { success: true, tx };
    } catch (error) {
      console.error('❌ Scale failed:', error.message);
      return { success: false, error: error.message };
    }
  }
  
  async exitPosition(reason = 'TRAIL_STOP') {
    if (!this.state.position) {
      throw new Error('No position to exit');
    }
    
    const token = this.state.position.token;
    console.log(`\n📊 EXECUTING: Full exit - ${reason}`);
    
    try {
      // Sell 100%
      const tx = await this.trader.sell(token, 100);
      
      // Calculate P&L
      const currentPrice = await this.getTokenPrice(token);
      const entryPrice = this.state.position.entryPrice;
      const pnl = ((currentPrice - entryPrice) / entryPrice) * 100;
      
      // Log trade
      this.state.trades.push({
        ...this.state.position,
        exitPrice: currentPrice,
        exitTx: tx,
        exitTime: Date.now(),
        pnl: pnl,
        reason
      });
      
      this.state.current = 'WAITING_REENTRY';
      this.state.position = null;
      this.logTrade('EXIT', token, 100, tx, { pnl, reason });
      this.saveState();
      
      return { success: true, pnl, tx };
    } catch (error) {
      console.error('❌ Exit failed:', error.message);
      return { success: false, error: error.message };
    }
  }
  
  async getTokenPrice(tokenMint) {
    try {
      // Get price in SOL
      const quote = await this.trader.getQuote(
        tokenMint,
        SOL_MINT,
        1000000  // 1 token worth
      );
      return parseFloat(quote.outAmount) / 1e9;
    } catch (e) {
      return 0;
    }
  }
  
  logTrade(type, token, amount, tx, extra = {}) {
    const log = {
      timestamp: new Date().toISOString(),
      type,
      token,
      amount,
      tx,
      ...extra
    };
    
    console.log(`📝 Trade logged: ${type} ${amount} of ${token}`);
    
    // Write to file
    const date = new Date().toISOString().split('T')[0];
    const logFile = `trading_logs/swing_trade2.2_${date}.json`;
    
    let logs = [];
    if (fs.existsSync(logFile)) {
      logs = JSON.parse(fs.readFileSync(logFile));
    }
    logs.push(log);
    fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
  }
  
  async runMonitoring() {
    console.log('\n🔍 Starting monitoring loop...');
    
    while (true) {
      try {
        // Check if in position
        if (this.state.position) {
          const token = this.state.position.token;
          const currentPrice = await this.getTokenPrice(token);
          const entryPrice = this.state.position.entryPrice;
          const peakPrice = Math.max(this.state.position.peakPrice, currentPrice);
          
          this.state.position.peakPrice = peakPrice;
          
          const pnl = ((currentPrice - entryPrice) / entryPrice) * 100;
          const fromPeak = ((currentPrice - peakPrice) / peakPrice) * 100;
          
          console.log(`\n⏰ ${new Date().toLocaleTimeString()}`);
          console.log(`   Token: ${token.slice(0, 8)}...`);
          console.log(`   Entry: $${entryPrice.toFixed(6)}`);
          console.log(`   Current: $${currentPrice.toFixed(6)}`);
          console.log(`   P&L: ${pnl.toFixed(2)}%`);
          console.log(`   From Peak: ${fromPeak.toFixed(2)}%`);
          
          // Check scale target (+20%)
          if (!this.state.position.scaled && pnl >= 20) {
            console.log('✅ HIT +20% SCALE TARGET');
            await this.scalePosition(50);
          }
          
          // Check trailing stop (-10% from peak)
          if (this.state.position.scaled && fromPeak <= -10) {
            console.log('🔴 TRAILING STOP HIT');
            await this.exitPosition('TRAIL_STOP');
          }
        }
        
        this.saveState();
        await new Promise(resolve => setTimeout(resolve, 60000));  // 1 minute
        
      } catch (error) {
        console.error('Monitor error:', error);
        await new Promise(resolve => setTimeout(resolve, 60000));
      }
    }
  }
}

// CLI Interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const params = args.slice(1);
  
  // Load config
  const config = JSON.parse(fs.readFileSync('./config.json'));
  
  // Initialize bot
  const bot = new SmartSwingBot(config);
  
  console.log('═══════════════════════════════════════════');
  console.log('  Smart Swing v2.2 - Solana Trading Bot');
  console.log('═══════════════════════════════════════════\n');
  
  // Check wallet
  await bot.getWalletBalance();
  
  switch (command) {
    case 'balance':
      await bot.getWalletBalance();
      break;
      
    case 'buy':
      if (params.length < 2) {
        console.log('Usage: node trader.js buy <token_mint> <sol_amount>');
        process.exit(1);
      }
      await bot.enterPosition(params[0], parseFloat(params[1]));
      break;
      
    case 'sell':
      if (params.length < 1) {
        console.log('Usage: node trader.js sell <token_mint> [percentage]');
        process.exit(1);
      }
      await bot.trader.sell(params[0], parseInt(params[1]) || 100);
      break;
      
    case 'monitor':
      await bot.runMonitoring();
      break;
      
    case 'state':
      console.log('\nCurrent State:');
      console.log(JSON.stringify(bot.state, null, 2));
      break;
      
    default:
      console.log('Commands:');
      console.log('  balance              - Check wallet balance');
      console.log('  buy <mint> <amount>  - Buy token with SOL');
      console.log('  sell <mint> [%]      - Sell token (default 100%)');
      console.log('  monitor              - Start monitoring (scales/trails)');
      console.log('  state                - Show current trading state');
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { SmartSwingBot, JupiterTrader, SecureWallet };
