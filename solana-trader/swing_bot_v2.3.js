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
  blacklistFile: './trading_logs/blacklist.json',
  sessionFile: './trading_logs/session_stats.json',  // 🔥 Track losses
  
  // ⏰ TRADING WINDOW - Set to null to trade 24/7
  tradingWindowStart: null,    // Set to hour (0-23) or null for always active
  tradingWindowEnd: null,      // Set to hour (0-23) or null for always active
  timezone: 'Australia/Sydney',
  enableTimeRestriction: false,  // Set to true to use time window, false for always on
  
  // 📊 ENTRY STRATEGY - Choose one:
  entryMode: 'breakout',  // Options: 'breakout' (buy high) | 'dip' (buy low)
  
  // BREAKOUT MODE (buy momentum)
  breakoutThreshold: 5.0,   // Buy when price UP >= 5%
  
  // DIP MODE (buy dips)
  dipThreshold: -8.0,       // Buy when price DOWN >= 8%
  maxDipFromHigh: -15.0,    // Must be within 15% of 6h high (not too crashed)
  volumeMultiplier: 3.0,
  minMarketCap: 10000000,
  maxMarketCap: 100000000,
  
  maxPositionSol: 0.5,
  reentrySizeSol: 0.25,
  minCashReserve: 0.25,
  
  scaleTarget: 20.0,
  scalePercent: 50,
  trailingStop: 10.0,
  hardStop: 7.0,
  beTrigger: 10.0,           // 🔥 Break-even trigger at +10%
  beBuffer: 0.5,             // 🔥 Break-even buffer at +0.5%
  
  cooldownMinutes: 30,        // Token blacklist cooldown
  maxConsecutiveLosses: 3,    // 🔥 Circuit breaker: max losses
  lossCooldownMinutes: 60,  // 🔥 Circuit breaker: cooldown
  
  checkIntervalSeconds: 30
};

const WATCHLIST = [
  { symbol: 'BONK', mint: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', decimals: 5 },
  { symbol: 'WIF', mint: 'EKpQGSJtjGFqKckxLSpxUtMJufH1R9kB2YrJ1ZC86yX', decimals: 6 },
  { symbol: 'MEW', mint: 'MEW1gQWJ3nUXGzz7kZJkeMo7FLMGLmM6jAp1M5MiZjy', decimals: 6 },
  { symbol: 'POPCAT', mint: '7GCihgBD8b79BRfY51y1xE6P7xZ1uNHHePgnTx4QWFLF', decimals: 6 },
  { symbol: 'PENGU', mint: '2zMMhcVQEXDPDLM5zwdkAmS1F3rpSJ5zxWuzRZyjqFN', decimals: 6 }
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
    this.blacklist = {};
    this.sessionStats = {      // 🔥 Track session performance
      consecutiveLosses: 0,
      totalLosses: 0,
      totalWins: 0,
      lossCooldownEnd: null,
      trades: []
    };
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
    
    this.loadPosition();
    this.loadBlacklist();
    this.loadSessionStats();  // 🔥 Load stats
    
    if (this.position) {
      console.log(`📂 Loaded position: ${this.position.token}`);
      console.log(`   Entry: $${this.position.entryPrice.toFixed(8)}`);
      console.log(`   Tokens: ${this.position.tokensRemaining?.toFixed(2) || this.position.tokensReceived.toFixed(2)}\n`);
    }
    
    this.showSessionStats();  // 🔥 Show stats
    
    return true;
  }

  savePosition() {
    if (this.position) {
      fs.writeFileSync(CONFIG.positionFile, JSON.stringify(this.position, null, 2));
    } else {
      try { fs.unlinkSync(CONFIG.positionFile); } catch(e) {}
    }
  }

  loadPosition() {
    try {
      if (fs.existsSync(CONFIG.positionFile)) {
        const data = fs.readFileSync(CONFIG.positionFile, 'utf8');
        this.position = JSON.parse(data);
        console.log(`📂 Loaded position: ${this.position.token}`);
      }
    } catch (e) {
      this.position = null;
    }
  }

  saveBlacklist() {
    fs.writeFileSync(CONFIG.blacklistFile, JSON.stringify(this.blacklist, null, 2));
  }

  loadBlacklist() {
    try {
      if (fs.existsSync(CONFIG.blacklistFile)) {
        const data = fs.readFileSync(CONFIG.blacklistFile, 'utf8');
        this.blacklist = JSON.parse(data);
      }
    } catch (e) {
      this.blacklist = {};
    }
  }

  isBlacklisted(tokenSymbol) {
    const exitTime = this.blacklist[tokenSymbol];
    if (!exitTime) return false;
    
    const now = Date.now();
    const cooldownMs = CONFIG.cooldownMinutes * 60 * 1000;
    const timeSinceExit = now - exitTime;
    
    if (timeSinceExit < cooldownMs) {
      const remainingMin = Math.ceil((cooldownMs - timeSinceExit) / 60000);
      console.log(`   ⏳ ${tokenSymbol} blacklisted - ${remainingMin} min remaining`);
      return true;
    }
    
    delete this.blacklist[tokenSymbol];
    this.saveBlacklist();
    return false;
  }

  addToBlacklist(tokenSymbol) {
    this.blacklist[tokenSymbol] = Date.now();
    this.saveBlacklist();
    console.log(`   🚫 ${tokenSymbol} blacklisted (${CONFIG.cooldownMinutes} min cooldown)`);
  }

  // 🔥 NEW: Session stats
  saveSessionStats() {
    fs.writeFileSync(CONFIG.sessionFile, JSON.stringify(this.sessionStats, null, 2));
  }

  loadSessionStats() {
    try {
      if (fs.existsSync(CONFIG.sessionFile)) {
        const data = fs.readFileSync(CONFIG.sessionFile, 'utf8');
        this.sessionStats = JSON.parse(data);
      }
    } catch (e) {
      this.sessionStats = {
        consecutiveLosses: 0,
        totalLosses: 0,
        totalWins: 0,
        lossCooldownEnd: null,
        trades: []
      };
    }
  }

  // 🔥 NEW: Show session stats
  showSessionStats() {
    console.log(`\n📊 SESSION STATS:`);
    console.log(`   Wins: ${this.sessionStats.totalWins} | Losses: ${this.sessionStats.totalLosses}`);
    console.log(`   Consecutive Losses: ${this.sessionStats.consecutiveLosses}`);
    
    if (this.sessionStats.lossCooldownEnd) {
      const remaining = this.sessionStats.lossCooldownEnd - Date.now();
      if (remaining > 0) {
        const mins = Math.ceil(remaining / 60000);
        console.log(`   🛑 COOLDOWN: ${mins} min remaining`);
      } else {
        this.sessionStats.lossCooldownEnd = null;
        this.sessionStats.consecutiveLosses = 0;
        this.saveSessionStats();
        console.log(`   ✅ Cooldown expired - resuming trading`);
      }
    }
    console.log();
  }

  // 🔥 NEW: Check circuit breaker
  isCircuitBreakerActive() {
    if (!this.sessionStats.lossCooldownEnd) return false;
    
    const remaining = this.sessionStats.lossCooldownEnd - Date.now();
    if (remaining > 0) {
      const mins = Math.ceil(remaining / 60000);
      console.log(`\n🛑 CIRCUIT BREAKER ACTIVE`);
      console.log(`   ${CONFIG.maxConsecutiveLosses} consecutive losses`);
      console.log(`   Trading paused for ${mins} more minutes`);
      console.log(`   Protecting capital from bad market conditions\n`);
      return true;
    }
    
    // Cooldown expired
    console.log(`\n✅ Circuit breaker expired - resetting`);
    this.sessionStats.lossCooldownEnd = null;
    this.sessionStats.consecutiveLosses = 0;
    this.saveSessionStats();
    return false;
  }

  // 🔥 NEW: Record trade result
  recordTradeResult(pnl) {
    const isWin = pnl > 0;
    
    this.sessionStats.trades.push({
      timestamp: Date.now(),
      pnl: pnl,
      win: isWin
    });
    
    if (isWin) {
      this.sessionStats.totalWins++;
      this.sessionStats.consecutiveLosses = 0;  // Reset on win
      console.log(`\n✅ WIN recorded (+${pnl.toFixed(2)}%) - loss counter reset`);
    } else {
      this.sessionStats.totalLosses++;
      this.sessionStats.consecutiveLosses++;
      console.log(`\n❌ LOSS recorded (${pnl.toFixed(2)}%) - loss #${this.sessionStats.consecutiveLosses}`);
      
      // Check circuit breaker
      if (this.sessionStats.consecutiveLosses >= CONFIG.maxConsecutiveLosses) {
        const cooldownMs = CONFIG.lossCooldownMinutes * 60 * 1000;
        this.sessionStats.lossCooldownEnd = Date.now() + cooldownMs;
        console.log(`\n🛑 CIRCUIT BREAKER TRIGGERED!`);
        console.log(`   ${CONFIG.maxConsecutiveLosses} consecutive losses`);
        console.log(`   Trading paused for ${CONFIG.lossCooldownMinutes} minutes`);
        console.log(`   ⏰ Resumes at: ${new Date(this.sessionStats.lossCooldownEnd).toLocaleTimeString()}`);
      }
    }
    
    this.saveSessionStats();
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
    // ⏰ If time restriction is disabled, always return true (trade 24/7)
    if (!CONFIG.enableTimeRestriction || CONFIG.tradingWindowStart === null || CONFIG.tradingWindowEnd === null) {
      return true;
    }
    
    const hour = this.getSydneyHour();
    return hour >= CONFIG.tradingWindowStart && hour < CONFIG.tradingWindowEnd;
  }

  async getSolBalance() {
    const balance = await this.connection.getBalance(this.keypair.publicKey);
    return balance / 1e9;
  }

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

  async getTokenPriceUsd(mint) {
    try {
      const res = await axios.get(
        `https://api.dexscreener.com/latest/dex/tokens/${mint}`,
        { timeout: 10000 }
      );
      
      if (!res.data?.pairs?.[0]) return 0;
      
      return parseFloat(res.data.pairs[0].priceUsd || 0);
    } catch (e) {
      return 0;
    }
  }

  checkEntrySignal(data) {
    if (!data) return { passed: false };
    
    // 📊 Choose entry strategy based on entryMode
    if (CONFIG.entryMode === 'dip') {
      return this.checkDipEntry(data);
    }
    
    // Default: Breakout entry (original)
    return this.checkBreakoutEntry(data);
  }
  
  checkBreakoutEntry(data) {
    // 🚀 BREAKOUT MODE: Buy when price is pumping
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
        details: checks,
        mode: 'breakout'
      };
    }
    
    return { passed: false, details: checks, mode: 'breakout' };
  }
  
  checkDipEntry(data) {
    // 📉 DIP MODE: Buy when price has dropped (mean reversion)
    const checks = {
      marketCap: data.marketCap >= CONFIG.minMarketCap && data.marketCap <= CONFIG.maxMarketCap,
      priceChange: data.priceChange6h <= CONFIG.dipThreshold,  // Price down X%
      notCrashed: data.priceChange6h >= CONFIG.maxDipFromHigh,  // But not completely dead
      hasLiquidity: data.liquidity > 100000,
      volumeOk: data.volume6h > (data.volume24h / 4 * 0.5)  // Some volume (not abandoned)
    };
    
    const passed = Object.values(checks).every(v => v);
    
    if (passed) {
      return {
        passed: true,
        score: this.calculateDipScore(data),
        details: checks,
        mode: 'dip'
      };
    }
    
    return { passed: false, details: checks, mode: 'dip' };
  }

  calculateScore(data) {
    if (CONFIG.entryMode === 'dip') {
      return this.calculateDipScore(data);
    }
    return this.calculateBreakoutScore(data);
  }
  
  calculateBreakoutScore(data) {
    // 🚀 BREAKOUT: Higher score = stronger momentum
    let score = 0;
    if (data.marketCap >= 20000000 && data.marketCap <= 50000000) score += 3;
    else if (data.marketCap >= 10000000 && data.marketCap <= 100000000) score += 2;
    if (data.priceChange6h >= 10) score += 3;
    else if (data.priceChange6h >= 5) score += 2;
    if (data.volume6h > data.volume24h / 4 * 1.5) score += 2;
    return score;
  }
  
  calculateDipScore(data) {
    // 📉 DIP BUYING: Higher score = better dip opportunity
    let score = 0;
    
    // Market cap (same as breakout)
    if (data.marketCap >= 20000000 && data.marketCap <= 50000000) score += 3;
    else if (data.marketCap >= 10000000 && data.marketCap <= 100000000) score += 2;
    
    // Dip depth (deeper dip = higher score, but not too deep)
    const dipPct = Math.abs(data.priceChange6h);
    if (dipPct >= 15 && dipPct <= 20) score += 4;        // Sweet spot: -15% to -20%
    else if (dipPct >= 10 && dipPct < 15) score += 3;    // Good dip: -10% to -15%
    else if (dipPct >= 8 && dipPct < 10) score += 2;     // Okay dip: -8% to -10%
    
    // Volume during dip (liquidation volume = opportunity)
    if (data.volume6h > data.volume24h / 4 * 2.0) score += 2;  // High volume on dip
    else if (data.volume6h > data.volume24h / 4 * 1.0) score += 1;
    
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
      
      // Calculate actual price paid: SOL per token
      const solPaid = solAmount;
      const tokensReceived = outAmount;
      const entryPriceUsd = await this.getTokenPriceUsd(token.mint);
      
      this.position = {
        token: token.symbol,
        mint: token.mint,
        decimals: token.decimals,
        entryPrice: entryPriceUsd,
        solInvested: solAmount,
        tokensReceived: outAmount,
        tokensRemaining: outAmount,
        entryTime: Date.now(),
        peakPrice: entryPriceUsd,
        scaled: false,
        beTriggered: false,
        beStopPrice: 0,
        signature
      };
      
      this.savePosition();
      this.logTrade('ENTRY', this.position);
      
      return signature;
    } catch (e) {
      console.error(`   ❌ Buy failed: ${e.message}`);
      return null;
    }
  }

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
      
      this.position.tokensRemaining -= (sellAmount / Math.pow(10, this.position.decimals));
      this.position.scaled = true;
      this.position.scaleSignature = signature;
      this.position.scaleTime = Date.now();
      
      this.savePosition();
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
      this.savePosition();
    }
    
    const fromPeak = ((currentPrice - this.position.peakPrice) / this.position.peakPrice) * 100;
    
    console.log(`\n📊 Position Monitor: ${this.position.token}`);
    console.log(`   Current: $${currentPrice.toFixed(8)}`);
    console.log(`   Entry: $${entryPrice.toFixed(8)}`);
    console.log(`   Peak: $${this.position.peakPrice.toFixed(8)}`);
    console.log(`   P&L: ${pnl.toFixed(2)}%`);
    console.log(`   From Peak: ${fromPeak.toFixed(2)}%`);
    console.log(`   Scaled: ${this.position.scaled ? '✅ YES' : '⏳ NO'}`);
    console.log(`   BE Stop: ${this.position.beTriggered ? '🛡️ ACTIVE' : '⏳ WAITING'}`);
    console.log(`   Remaining: ${this.position.tokensRemaining?.toFixed(2) || 'N/A'} tokens`);
    
    // 🔥 Break-even trigger at +10%
    if (!this.position.beTriggered && !this.position.scaled && pnl >= CONFIG.beTrigger) {
      console.log(`\n🛡️ BREAK-EVEN TRIGGERED at +${pnl.toFixed(1)}%!`);
      
      this.position.beTriggered = true;
      this.position.beStopPrice = entryPrice * (1 + CONFIG.beBuffer / 100);
      this.savePosition();
      
      console.log(`   Hard stop moved to: $${this.position.beStopPrice.toFixed(8)} (+${CONFIG.beBuffer}%)`);
      console.log(`   Won't lose money from this point!`);
    }
    
    // Scale at +20%
    if (!this.position.scaled && pnl >= CONFIG.scaleTarget) {
      console.log(`\n🎯 SCALE TARGET HIT! +${pnl.toFixed(1)}%`);
      await this.scalePosition();
      return;
    }
    
    // Trailing stop (-10% from peak)
    if (fromPeak <= -CONFIG.trailingStop) {
      console.log(`\n🛑 TRAILING STOP HIT! ${fromPeak.toFixed(1)}% from peak`);
      const pnlAtExit = pnl;
      await this.sellAll();
      this.recordTradeResult(pnlAtExit);  // 🔥 Record result
      return;
    }
    
    // Hard stop or break-even stop
    const stopPrice = this.position.beTriggered 
      ? this.position.beStopPrice 
      : entryPrice * (1 - CONFIG.hardStop / 100);
    
    if (currentPrice <= stopPrice) {
      const stopType = this.position.beTriggered ? 'BREAK-EVEN' : 'HARD';
      console.log(`\n🛑 ${stopType} STOP HIT!`);
      const pnlAtExit = ((stopPrice - entryPrice) / entryPrice) * 100;
      await this.sellAll();
      this.recordTradeResult(pnlAtExit);  // 🔥 Record result
      return;
    }
  }

  async sellAll() {
    if (!this.position) return;
    
    const tokenSymbol = this.position.token;
    
    try {
      console.log(`\n🔴 SELLING ALL: ${tokenSymbol}`);
      
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
      const signature = await this.executeSwap(swap, `Exit ${tokenSymbol}`);
      
      const exitPrice = parseFloat(quote.outAmount) / parseFloat(quote.inAmount) * Math.pow(10, 9 - this.position.decimals);
      const pnl = ((exitPrice - this.position.entryPrice) / this.position.entryPrice) * 100;
      
      this.logTrade('EXIT', { ...this.position, exitPrice, solReceived: solOut, pnl, signature });
      
      this.addToBlacklist(tokenSymbol);  // Blacklist after exit
      
      this.position = null;
      this.savePosition();
      
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
    // 🔥 Check circuit breaker first
    if (this.isCircuitBreakerActive()) {
      return;
    }
    
    const mode = CONFIG.entryMode === 'dip' ? '📉 DIP BUYING' : '🚀 BREAKOUT';
    console.log(`\n🔍 Scanning for ${mode} signals...\n`);
    
    const candidates = [];
    
    for (const token of WATCHLIST) {
      // Skip blacklisted tokens
      if (this.isBlacklisted(token.symbol)) continue;
      
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
      const changeEmoji = c.priceChange6h >= 0 ? '🟢' : '🔴';
      console.log(`   ${i + 1}. ${c.symbol}`);
      console.log(`      Price: $${c.priceUsd.toFixed(8)}`);
      console.log(`      Change: ${changeEmoji} ${c.priceChange6h.toFixed(2)}%`);
      console.log(`      Score: ${c.score}/8\n`);
    });
    
    const best = candidates[0];
    
    if (best.score >= 6) {
      console.log(`\n🎯 STRONG SIGNAL: ${best.symbol} (Score: ${best.score})`);
      
      if (this.position) {
        console.log(`   Already have position: ${this.position.token}`);
        console.log(`   Skipping new entry\n`);
        return;
      }
      
      // Check blacklist
      if (this.isBlacklisted(best.symbol)) {
        console.log(`   🚫 ${best.symbol} blacklisted (recent exit)`);
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
    console.log('\n🚀 Swing Trader v2.3 Starting...');
    console.log('   Features: Break-even | Blacklist | Circuit Breaker');
    
    if (CONFIG.entryMode === 'dip') {
      console.log('   Entry Mode: 📉 DIP BUYING (buy low, sell high)');
      console.log(`   Trigger: Price down >= ${Math.abs(CONFIG.dipThreshold)}% from 6h ago`);
      console.log(`   Max Dip: ${Math.abs(CONFIG.maxDipFromHigh)}% (avoiding dead coins)\n`);
    } else {
      console.log('   Entry Mode: 🚀 BREAKOUT (buy high, sell higher)');
      console.log(`   Trigger: Price up >= ${CONFIG.breakoutThreshold}% from 6h ago`);
    }

    if (CONFIG.enableTimeRestriction) {
      console.log(`   Time Window: ${String(CONFIG.tradingWindowStart).padStart(2,'0')}:00 - ${String(CONFIG.tradingWindowEnd).padStart(2,'0')}:00 Sydney`);
    } else {
      console.log('   Time Window: 🟢 24/7 Trading (no restrictions)');
    }
    console.log();

    await this.init();
    
    this.running = true;
    
    while (this.running) {
      const sydneyTime = this.getSydneyTime();
      const hour = this.getSydneyHour();
      
      console.log(`\n⏰ Sydney Time: ${sydneyTime}`);
      
      if (CONFIG.enableTimeRestriction) {
        console.log(`   Window: ${String(CONFIG.tradingWindowStart).padStart(2,'0')}:00 - ${String(CONFIG.tradingWindowEnd).padStart(2,'0')}:00 (${String(hour).padStart(2,'0')}:XX)`);
      } else {
        console.log(`   Mode: 🟢 24/7 Trading (no time restrictions)`);
      }
      
      if (this.isTradingWindow()) {
        console.log('   Status: 🟢 ACTIVE\n');
        
        if (this.position) {
          await this.monitorPosition();
        } else {
          await this.scan();
        }
      } else {
        console.log('   Status: 🔴 CLOSED (outside trading window)\n');
        
        if (this.position) {
          console.log('   Session ending - closing position...');
          const data = await this.getTokenData({ symbol: this.position.token, mint: this.position.mint });
          const pnl = data ? ((data.priceUsd - this.position.entryPrice) / this.position.entryPrice) * 100 : 0;
          await this.sellAll();
          this.recordTradeResult(pnl);
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
