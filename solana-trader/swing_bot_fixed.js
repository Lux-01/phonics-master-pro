const axios = require('axios');
const fs = require('fs');
const { Connection, Keypair, VersionedTransaction, PublicKey } = require('@solana/web3.js');

// Load Helius RPC
const heliusKey = fs.readFileSync('./.secrets/helius.key', 'utf8').trim();
const HELIUS_RPC = `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`;

// Config
const CONFIG = {
  jupiterApiUrl: 'https://api.jup.ag/swap/v1',
  rpcEndpoint: HELIUS_RPC,
  walletKeyPath: './.secrets/wallet.key',
  jupiterApiKeyPath: './.secrets/jupiter.key',
  positionFile: './trading_logs/current_position.json',
  blacklistFile: './trading_logs/blacklist.json',  // 🔥 Blacklist file
  
  tradingWindowStart: 0,    // 00:00 (midnight)
  tradingWindowEnd: 4,      // 04:00 (4 AM)
  timezone: 'Australia/Sydney',
  
  breakoutThreshold: 5.0,
  volumeMultiplier: 3.0,
  minMarketCap: 10000000,
  maxMarketCap: 100000000,
  
  maxPositionSol: 0.5,
  reentrySizeSol: 0.25,
  minCashReserve: 0.25,
  
  scaleTarget: 20.0,
  scalePercent: 50,          // Sell 50% on scale
  trailingStop: 10.0,
  hardStop: 7.0,
  
  cooldownMinutes: 30,        // 🔥 30 min cooldown after exit
  
  checkIntervalSeconds: 30
};

const WATCHLIST = [
  { symbol: 'BONK', mint: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', decimals: 5 },
  { symbol: 'WIF', mint: 'EKpQGSJtjGFqKckxLSpxUtMJufH1R9kB2YrJ1ZC86yX', decimals: 6 },
  { symbol: 'MEW', mint: 'MEW1gQWJ3nUXGzz7kZJkeMo7FLMGLmM6jAp1M5MiZjy', decimals: 6 },
  { symbol: 'POPCAT', mint: '7GCihgBD8b79BRfY51y1xE6P7xZ1uNHHePgnTx4QWFLF', decimals: 6 },
  { symbol: 'PENGU', mint: '2zMMhcVQEXDPDLM5zwdkAmS1F3rpSJ5zxWuzRZyjqFN', decimals: 6 },
  { symbol: 'PUMP1', mint: 'NV2RYH954cTJ3ckFUpvfqaQXU4ARqqDH3562nFSpump', decimals: 6 },
  { symbol: 'PUMP2', mint: 'AVF9F4C4j8b1Kh4BmNHqybDaHgnZpJ7W7yLvL7hUpump', decimals: 6 }
];

const TOKENS = {
  SOL: { mint: 'So11111111111111111111111111111111111111112', decimals: 9, symbol: 'SOL' },
  USDC: { mint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', decimals: 6, symbol: 'USDC' }
};

class SwingTraderBot {
  constructor() {
    this.connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
    this.keypair = null;
    this.apiKey = null;
    this.walletAddress = null;
    this.position = null;
    this.blacklist = {};  // 🔥 Blacklist: { token: exitTime }
    this.sessionData = {
      startTime: null,
      trades: [],
      sessionLow: {},
      sessionHigh: {},
      entryPrices: {}
    };
    this.running = false;
  }

  async init() {
    this.apiKey = fs.readFileSync(CONFIG.jupiterApiKeyPath, 'utf8').trim();
    const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
    
    try {
      this.keypair = Keypair.fromSecretKey(Buffer.from(secretKey, 'base64'));
    } catch (e) {
      const bs58 = require('bs58');
      this.keypair = Keypair.fromSecretKey(bs58.decode(secretKey));
    }
    
    this.walletAddress = this.keypair.publicKey.toString();
    console.log(`✅ Bot initialized: ${this.walletAddress.substring(0,8)}...${this.walletAddress.slice(-4)}\n`);
    
    // 🔥 FIX: Load saved position from file
    this.loadPosition();
    
    // 🔥 NEW: Load blacklist
    this.loadBlacklist();
    
    if (this.position) {
      console.log(`📂 Loaded existing position: ${this.position.token}`);
      console.log(`   Entry: $${this.position.entryPrice.toFixed(8)}`);
      console.log(`   Tokens: ${this.position.tokensRemaining?.toFixed(2) || this.position.tokensReceived.toFixed(2)}\n`);
    }
    
    return true;
  }

  // 🔥 FIX: Save position to file
  savePosition() {
    if (this.position) {
      fs.writeFileSync(CONFIG.positionFile, JSON.stringify(this.position, null, 2));
    } else {
      try { fs.unlinkSync(CONFIG.positionFile); } catch(e) {}
    }
  }

  // 🔥 FIX: Load position from file
  loadPosition() {
    try {
      if (fs.existsSync(CONFIG.positionFile)) {
        const data = fs.readFileSync(CONFIG.positionFile, 'utf8');
        this.position = JSON.parse(data);
        console.log(`📂 Loaded position from file: ${this.position.token}`);
      }
    } catch (e) {
      console.log('📂 No saved position found');
      this.position = null;
    }
  }

  // 🔥 NEW: Save blacklist to file
  saveBlacklist() {
    fs.writeFileSync(CONFIG.blacklistFile, JSON.stringify(this.blacklist, null, 2));
  }

  // 🔥 NEW: Load blacklist from file
  loadBlacklist() {
    try {
      if (fs.existsSync(CONFIG.blacklistFile)) {
        const data = fs.readFileSync(CONFIG.blacklistFile, 'utf8');
        this.blacklist = JSON.parse(data);
        console.log(`📂 Loaded blacklist: ${Object.keys(this.blacklist).length} tokens`);
      }
    } catch (e) {
      console.log('📂 No blacklist found');
      this.blacklist = {};
    }
  }

  // 🔥 NEW: Check if token is blacklisted (in cooldown)
  isBlacklisted(tokenSymbol) {
    const exitTime = this.blacklist[tokenSymbol];
    if (!exitTime) return false;
    
    const now = Date.now();
    const cooldownMs = CONFIG.cooldownMinutes * 60 * 1000;
    const timeSinceExit = now - exitTime;
    const remainingMs = cooldownMs - timeSinceExit;
    
    if (timeSinceExit < cooldownMs) {
      const remainingMin = Math.ceil(remainingMs / 60000);
      console.log(`   ⏳ ${tokenSymbol} blacklisted - ${remainingMin} min remaining`);
      return true;
    }
    
    // Expired - remove from blacklist
    delete this.blacklist[tokenSymbol];
    this.saveBlacklist();
    return false;
  }

  // 🔥 NEW: Add token to blacklist
  addToBlacklist(tokenSymbol) {
    this.blacklist[tokenSymbol] = Date.now();
    this.saveBlacklist();
    console.log(`   🚫 Added ${tokenSymbol} to blacklist (${CONFIG.cooldownMinutes} min cooldown)`);
  }

  getSydneyTime() {
    return new Date().toLocaleString('en-AU', { timeZone: 'Australia/Sydney', hour12: false });
  }

  getSydneyHour() {
    const sydneyTime = new Date().toLocaleString('en-AU', { 
      timeZone: 'Australia/Sydney', 
      hour12: false,
      hour: '2-digit'
    });
    return parseInt(sydneyTime);
  }

  isTradingWindow() {
    const hour = this.getSydneyHour();
    return hour >= CONFIG.tradingWindowStart && hour < CONFIG.tradingWindowEnd;
  }

  async getSolBalance() {
    const balance = await this.connection.getBalance(this.keypair.publicKey);
    return balance / 1e9;
  }

  // Get token balance from wallet
  async getTokenBalance(mint) {
    try {
      const tokenAccounts = await this.connection.getParsedTokenAccountsByOwner(
        this.keypair.publicKey,
        { mint: new PublicKey(mint) }
      );
      
      if (tokenAccounts.value.length === 0) return 0;
      
      const balance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.amount;
      const decimals = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.decimals;
      return parseFloat(balance) / Math.pow(10, decimals);
    } catch (e) {
      return 0;
    }
  }

  async getTokenData(token) {
    try {
      const res = await axios.get(
        `https://api.dexscreener.com/latest/dex/tokens/${token.mint}`,
        { timeout: 10000 }
      );
      
      if (!res.data?.pairs?.[0]) return null;
      
      const pair = res.data.pairs[0];
      return {
        symbol: token.symbol,
        mint: token.mint,
        priceUsd: parseFloat(pair.priceUsd),
        marketCap: parseFloat(pair.marketCap || 0),
        volume24h: parseFloat(pair.volume24h || 0),
        volume6h: parseFloat(pair.volume?.h6 || 0),
        priceChange6h: parseFloat(pair.priceChange?.h6 || 0),
        liquidity: parseFloat(pair.liquidity?.usd || 0)
      };
    } catch (e) {
      return null;
    }
  }

  checkEntrySignal(data) {
    const checks = {
      marketCap: data.marketCap >= CONFIG.minMarketCap && data.marketCap <= CONFIG.maxMarketCap,
      priceChange: data.priceChange6h >= CONFIG.breakoutThreshold,
      hasLiquidity: data.liquidity > 100000
    };
    
    const passed = Object.values(checks).every(v => v);
    
    if (passed) {
      return {
        passed: true,
        score: this.calculateScore(data),
        details: checks
      };
    }
    
    return { passed: false, details: checks };
  }

  calculateScore(data) {
    let score = 0;
    if (data.marketCap >= 20000000 && data.marketCap <= 50000000) score += 3;
    else if (data.marketCap >= 10000000 && data.marketCap <= 100000000) score += 2;
    if (data.priceChange6h >= 10) score += 3;
    else if (data.priceChange6h >= 5) score += 2;
    if (data.volume6h > data.volume24h / 4 * 1.5) score += 2;
    return score;
  }

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

  async buildSwap(quoteResponse) {
    const url = `${CONFIG.jupiterApiUrl}/swap`;
    const body = {
      quoteResponse,
      userPublicKey: this.walletAddress,
      wrapAndUnwrapSol: true,
      prioritizationFeeLamports: 50000
    };

    const res = await axios.post(url, body, {
      headers: { 'Content-Type': 'application/json', 'x-api-key': this.apiKey },
      timeout: 15000
    });

    return res.data;
  }

  async executeSwap(swapResponse, label) {
    const serializedTx = Buffer.from(swapResponse.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([this.keypair]);

    console.log(`📤 Executing ${label}...`);
    const signature = await this.connection.sendTransaction(transaction, {
      maxRetries: 3,
      skipPreflight: false
    });

    console.log(`⏳ Confirming...`);
    await this.connection.confirmTransaction(signature, 'confirmed');
    
    console.log(`✅ ${label} complete!`);
    console.log(`   TX: https://solscan.io/tx/${signature}`);
    
    return signature;
  }

  async buyToken(token, solAmount) {
    try {
      console.log(`\n🟢 BUY SIGNAL: ${token.symbol}`);
      console.log(`   Amount: ${solAmount} SOL`);
      
      const amountLamports = Math.floor(solAmount * 1e9);
      const quote = await this.getQuote(TOKENS.SOL.mint, token.mint, amountLamports);
      
      const outAmount = parseFloat(quote.outAmount) / Math.pow(10, token.decimals);
      console.log(`   Expected: ~${outAmount.toFixed(2)} ${token.symbol}`);
      
      const swap = await this.buildSwap(quote);
      const signature = await this.executeSwap(swap, `Buy ${token.symbol}`);
      
      // 🔥 FIX: Save position with tokensRemaining and break-even tracking
      this.position = {
        token: token.symbol,
        mint: token.mint,
        decimals: token.decimals,
        entryPrice: parseFloat(quote.outAmount) / parseFloat(quote.inAmount) * Math.pow(10, 9 - token.decimals),
        solInvested: solAmount,
        tokensReceived: outAmount,
        tokensRemaining: outAmount,
        entryTime: Date.now(),
        peakPrice: parseFloat(quote.outAmount) / parseFloat(quote.inAmount) * Math.pow(10, 9 - token.decimals),
        scaled: false,
        beTriggered: false,  // 🔥 Break-even trigger flag
        beStopPrice: 0,      // 🔥 Break-even stop price
        signature
      };
      
      this.savePosition(); // 🔥 Persist position
      this.logTrade('ENTRY', this.position);
      
      return signature;
    } catch (e) {
      console.error(`   ❌ Buy failed: ${e.message}`);
      return null;
    }
  }

  // 🔥 FIX: Actually execute scale (sell 50%)
  async scalePosition() {
    if (!this.position || this.position.scaled) return;
    
    try {
      console.log(`\n🎯 EXECUTING SCALE OUT: ${this.position.token}`);
      
      const sellAmount = Math.floor(this.position.tokensRemaining * (CONFIG.scalePercent / 100) * Math.pow(10, this.position.decimals));
      
      console.log(`   Selling ${CONFIG.scalePercent}% (${sellAmount / Math.pow(10, this.position.decimals)} tokens)`);
      
      const quote = await this.getQuote(this.position.mint, TOKENS.SOL.mint, sellAmount);
      const solBack = parseFloat(quote.outAmount) / 1e9;
      
      console.log(`   Expected: ~${solBack.toFixed(4)} SOL back`);
      
      const swap = await this.buildSwap(quote);
      const signature = await this.executeSwap(swap, `Scale ${this.position.token}`);
      
      // Update position
      this.position.tokensRemaining -= (sellAmount / Math.pow(10, this.position.decimals));
      this.position.scaled = true;
      this.position.scaleSignature = signature;
      this.position.scaleTime = Date.now();
      
      this.savePosition(); // 🔥 Persist updated position
      this.logTrade('SCALE', this.position);
      
      console.log(`\n💰 POSITION UPDATE:`);
      console.log(`   Tokens remaining: ${this.position.tokensRemaining.toFixed(2)}`);
      console.log(`   Will trail stop on remaining position\n`);
      
      return signature;
    } catch (e) {
      console.error(`   ❌ Scale failed: ${e.message}`);
      return null;
    }
  }

  async monitorPosition() {
    if (!this.position) return;
    
    const data = await this.getTokenData({
      symbol: this.position.token,
      mint: this.position.mint
    });
    
    if (!data) return;
    
    const currentPrice = data.priceUsd;
    const entryPrice = this.position.entryPrice;
    const pnl = ((currentPrice - entryPrice) / entryPrice) * 100;
    
    if (currentPrice > this.position.peakPrice) {
      this.position.peakPrice = currentPrice;
      this.savePosition(); // 🔥 Update peak
    }
    
    const fromPeak = ((currentPrice - this.position.peakPrice) / this.position.peakPrice) * 100;
    
    console.log(`\n📊 Position Monitor: ${this.position.token}`);
    console.log(`   Current: $${currentPrice.toFixed(8)}`);
    console.log(`   Entry: $${entryPrice.toFixed(8)}`);
    console.log(`   Peak: $${this.position.peakPrice.toFixed(8)}`);
    console.log(`   P&L: ${pnl.toFixed(2)}%`);
    console.log(`   From Peak: ${fromPeak.toFixed(2)}%`);
    console.log(`   Scaled: ${this.position.scaled ? '✅ YES' : '⏳ NO'}`);
    console.log(`   BE Stop: ${this.position.beTriggered ? '✅ ACTIVE' : '⏳ WAITING'}`);
    console.log(`   BE Price: $${this.position.beStopPrice.toFixed(8) || entryPrice}`);
    console.log(`   Remaining: ${this.position.tokensRemaining?.toFixed(2) || 'N/A'} tokens`);
    
    // 🔥 NEW: Break-even trigger at +10%
    if (!this.position.beTriggered && !this.position.scaled && pnl >= 10) {
      console.log(`\n🛡️ BREAK-EVEN TRIGGERED at +${pnl.toFixed(1)}%!`);
      
      // Set break-even stop at entry price + 0.5% buffer for fees
      const beBuffer = 0.5; // 0.5% buffer to cover fees
      this.position.beTriggered = true;
      this.position.beStopPrice = entryPrice * (1 + beBuffer / 100);
      this.savePosition();
      
      console.log(`   Hard stop moved to: $${this.position.beStopPrice.toFixed(8)} (+${beBuffer}%)`);
      console.log(`   You won't lose money from this point!\n`);
    }
    
    // 🔥 FIX: Actually execute scale at +20%
    if (!this.position.scaled && pnl >= CONFIG.scaleTarget) {
      console.log(`\n🎯 SCALE TARGET HIT! +${pnl.toFixed(1)}%`);
      await this.scalePosition();
      return;
    }
    
    // Trailing stop (-10% from peak)
    if (fromPeak <= -CONFIG.trailingStop) {
      console.log(`\n🛑 TRAILING STOP HIT! ${fromPeak.toFixed(1)}% from peak`);
      await this.sellAll();
      return;
    }
    
    // 🔥 MODIFIED: Check break-even stop or hard stop
    const effectiveStopPrice = this.position.beTriggered 
      ? this.position.beStopPrice 
      : entryPrice * (1 - CONFIG.hardStop / 100);
    
    if (currentPrice <= effectiveStopPrice) {
      const stopMessage = this.position.beTriggered 
        ? `BREAK-EVEN STOP HIT! Price $${currentPrice.toFixed(8)} below $${effectiveStopPrice.toFixed(8)}`
        : `HARD STOP HIT! -${Math.abs(pnl).toFixed(1)}%`;
      console.log(`\n🛑 ${stopMessage}`);
      await this.sellAll();
      return;
    }
  }

  async sellAll() {
    if (!this.position) return;
    
    try {
      console.log(`\n🔴 SELLING ALL: ${this.position.token}`);
      
      const balance = await this.getTokenBalance(this.position.mint);
      const sellAmount = Math.floor(balance * Math.pow(10, this.position.decimals));
      
      if (sellAmount <= 0) {
        console.log('   No balance to sell');
        this.position = null;
        this.savePosition();
        return;
      }
      
      console.log(`   Selling ${balance.toFixed(2)} tokens`);
      
      const quote = await this.getQuote(this.position.mint, TOKENS.SOL.mint, sellAmount);
      const solOut = parseFloat(quote.outAmount) / 1e9;
      
      console.log(`   Expected: ~${solOut.toFixed(4)} SOL`);
      
      const swap = await this.buildSwap(quote);
      const signature = await this.executeSwap(swap, `Exit ${this.position.token}`);
      
      this.logTrade('EXIT', { ...this.position, exitPrice: currentPrice, solReceived: solOut, signature });
      
      // 🔥 NEW: Add to blacklist to prevent immediate rebuy
      this.addToBlacklist(this.position.token);
      
      this.position = null;
      this.savePosition(); // 🔥 Clear position file
      
      return signature;
    } catch (e) {
      console.error(`   ❌ Sell failed: ${e.message}`);
    }
  }

  logTrade(action, data) {
    const trade = {
      action,
      timestamp: new Date().toISOString(),
      sydneyTime: this.getSydneyTime(),
      ...data
    };
    
    this.sessionData.trades.push(trade);
    
    const date = new Date().toISOString().split('T')[0];
    fs.writeFileSync(
      `./trading_logs/swing_session_${date}.json`,
      JSON.stringify(this.sessionData, null, 2)
    );
  }

  async scan() {
    console.log('\n🔍 Scanning for entry signals...\n');
    
    const candidates = [];
    
    for (const token of WATCHLIST) {
      const data = await this.getTokenData(token);
      if (!data) continue;
      
      const signal = this.checkEntrySignal(data);
      
      if (signal.passed) {
        candidates.push({ ...data, score: signal.score });
      }
    }
    
    candidates.sort((a, b) => b.score - a.score);
    
    if (candidates.length === 0) {
      console.log('   No signals found\n');
      return;
    }
    
    console.log(`   Found ${candidates.length} candidate(s):\n`);
    candidates.forEach((c, i) => {
      console.log(`   ${i + 1}. ${c.symbol}`);
      console.log(`      Price: $${c.priceUsd.toFixed(8)}`);
      console.log(`      Change: +${c.priceChange6h.toFixed(2)}%`);
      console.log(`      Score: ${c.score}/8\n`);
    });
    
    const best = candidates[0];
    
    if (best.score >= 6) {
      console.log(`\n🎯 STRONG SIGNAL: ${best.symbol} (Score: ${best.score})`);
      
      // Check if we have position already
      if (this.position) {
        console.log(`   Already have position: ${this.position.token}`);
        console.log(`   Skipping new entry\n`);
        return;
      }
      
      // 🔥 NEW: Check blacklist cooldown
      if (this.isBlacklisted(best.symbol)) {
        console.log(`   🚫 ${best.symbol} is blacklisted (recent exit)`);
        console.log(`   Skipping - waiting for cooldown\n`);
        return;
      }
      
      const balance = await this.getSolBalance();
      console.log(`   SOL Balance: ${balance.toFixed(4)}`);
      
      if (balance < CONFIG.maxPositionSol + CONFIG.minCashReserve) {
        console.log(`   ❌ Insufficient balance\n`);
        return;
      }
      
      const token = WATCHLIST.find(t => t.symbol === best.symbol);
      if (token) {
        await this.buyToken(token, CONFIG.maxPositionSol);
      }
    }
  }

  async run() {
    console.log('\n🚀 Swing Trader v2.2 Fixed Starting...\n');
    
    if (!await this.init()) {
      console.log('Init failed');
      return;
    }
    
    this.running = true;
    
    while (this.running) {
      const sydneyTime = this.getSydneyTime();
      const hour = this.getSydneyHour();
      
      console.log(`\n⏰ Sydney Time: ${sydneyTime}`);
      console.log(`   Window: 00:00 - 04:00 (${String(hour).padStart(2,'0')}:XX)`);
      
      if (this.isTradingWindow()) {
        console.log('   Status: 🟢 ACTIVE\n');
        
        if (this.position) {
          await this.monitorPosition();
        } else {
          await this.scan();
        }
      } else {
        console.log('   Status: 🔴 CLOSED\n');
        
        if (this.position) {
          console.log('   Session ending - closing position...');
          await this.sellAll();
        }
      }
      
      await new Promise(r => setTimeout(r, CONFIG.checkIntervalSeconds * 1000));
    }
  }
}

process.on('SIGINT', () => {
  console.log('\n\n👋 Shutting down...');
  process.exit(0);
});

const bot = new SwingTraderBot();
bot.run().catch(console.error);
