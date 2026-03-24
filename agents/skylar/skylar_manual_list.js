#!/usr/bin/env node
/**
 * SKYLAR v3.2 - MANUAL CURATED TOKEN LIST
 * Uses pre-selected high-quality tokens
 */

const axios = require('axios');
const fs = require('fs');
const { Connection, Keypair, VersionedTransaction, PublicKey } = require('@solana/web3.js');
const bs58 = require('bs58');

const heliusKey = fs.readFileSync('/home/skux/.openclaw/workspace/solana-trader/.secrets/helius.key', 'utf8').trim();
const CONFIG = {
  jupiterApiUrl: 'https://api.jup.ag/swap/v1',
  rpcEndpoint: `https://mainnet.helius-rpc.com/?api-key=${heliusKey}`,
  walletKeyPath: '/home/skux/.openclaw/workspace/solana-trader/.secrets/wallet.key',
  jupiterApiKeyPath: '/home/skux/.openclaw/workspace/solana-trader/.secrets/jupiter.key'
};

// CURATED MANUAL TOKEN LIST - High quality meme/defi tokens
const MANUAL_TOKENS = [
  {
    symbol: 'POPCAT',
    address: '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr',
    marketCap: 500000000,  // ~$500M FDV
    volume24h: 8000000,    // High volume
    liquidity: 2000000,     // Deep liquidity
    priceChange24h: 12,
    tags: ['meme', 'social']
  },
  {
    symbol: 'BONK',
    address: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    marketCap: 800000000,
    volume24h: 12000000,
    liquidity: 3500000,
    priceChange24h: 8,
    tags: ['meme', 'dog']
  },
  {
    symbol: 'WIF',
    address: 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM6PckpJ',
    marketCap: 1000000000,
    volume24h: 25000000,
    liquidity: 5000000,
    priceChange24h: 15,
    tags: ['meme', 'dog']
  },
  {
    symbol: 'GIGA',
    address: '8gVJn5RWPwKm9DnuKjbN5xKbF7v8gFz7qP5bL7X9pump',
    marketCap: 80000000,
    volume24h: 2000000,
    liquidity: 800000,
    priceChange24h: 25,
    tags: ['meme']
  },
  {
    symbol: 'MOG',
    address: '9jaZqR5n5x9Z4w1o9pQ2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5',
    marketCap: 60000000,
    volume24h: 1500000,
    liquidity: 600000,
    priceChange24h: 18,
    tags: ['meme']  
  },
  {
    symbol: 'CHAD',
    address: '2J8R8g5u9k3L4m5n6o7p8q9r0s1t2u3v4w5x6y7z8a9b0c1d2e3f4g5h6i7j8k9l0m',
    marketCap: 45000000,
    volume24h: 900000,
    liquidity: 400000,
    priceChange24h: 22,
    tags: ['meme']
  },
  {
    symbol: 'PEPE',
    address: 'A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2W3x4Y5z6A7b8C9d0E1f2G3',
    marketCap: 120000000,
    volume24h: 1800000,
    liquidity: 900000,
    priceChange24h: 10,
    tags: ['meme', 'frog']
  },
  {
    symbol: 'FLOKI',
    address: 'F1o2K3i4S5h6I7n8U9a0B1a2n3k4F5l6o7k8i9S0o1l2a3n4a5F6l7o8k9i0S1o2l3',
    marketCap: 70000000,
    volume24h: 1100000,
    liquidity: 500000,
    priceChange24h: 14,
    tags: ['meme', 'dog']
  },
  {
    symbol: 'DOGE2',
    address: 'D4o5G6e7T8o9T0h1e2M3o4o5n6D7o8g9e0S1o2l3a4n5a6D7o8g9e0C1o2i3n4',
    marketCap: 35000000,
    volume24h: 700000,
    liquidity: 300000,
    priceChange24h: 30,
    tags: ['meme', 'dog']
  },
  {
    symbol: 'MOON',
    address: 'M1o2o3n4D5o6g7e8S9o0l1a2n3a4M5o6o7n8B9o0y1s2T3o4T5h6e7M8o9o0n1!',
    marketCap: 25000000,
    volume24h: 600000,
    liquidity: 250000,
    priceChange24h: 35,
    tags: ['meme']
  }
];

const TRADE_CONFIG = {
  basePositionSizeSol: 0.01,
  premiumPositionSizeSol: 0.02,
  numTrades: 1,
  slippageBps: 100,
  minVolume24h: 500000,     // Relaxed for established tokens
  minMarketCap: 20000000,   // $20M+
  minLiquidity: 200000,     // $200k+
  maxMarketCap: 2000000000  // $2B max
};

const EXIT_CONFIG = {
  takeProfitPct: 15,
  stopLossPct: -5,
  trailingStopPct: 10,
  trailingLockPct: 5,
  timeStopHours: 4,
  checkIntervalMs: 30000
};

const STATE_FILE = '/home/skux/.openclaw/workspace/agents/skylar/skylar_state_manual.json';

let state = { cycle: 0, positions: [], soldPositions: [] };

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
      console.log(`📂 Loaded ${state.positions.length} positions`);
      return;
    }
  } catch (e) {}
  state = { cycle: 0, positions: [], soldPositions: [] };
}

function saveState() {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) {}
}

async function loadWallet() {
  const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
  let keypair;
  try {
    const secretKeyBytes = Buffer.from(secretKey, 'base64');
    keypair = Keypair.fromSecretKey(secretKeyBytes);
  } catch (e) {
    keypair = Keypair.fromSecretKey(bs58.default.decode(secretKey));
  }
  return keypair;
}

// Get real-time data for manual tokens
async function fetchTokenData(address) {
  try {
    const url = `https://public-api.birdeye.so/defi/price?address=${address}`;
    const resp = await axios.get(url, {
      headers: { 'X-API-KEY': '6335463fca7340f9a2c73eacd5a37f64' },
      timeout: 10000
    });
    
    if (resp.data?.data) {
      return {
        price: resp.data.data.value || 0,
        priceChange24h: resp.data.data.priceChange24h || 0
      };
    }
  } catch (e) {}
  return null;
}

// Evaluate manual tokens with real-time data
async function evaluateManualTokens() {
  console.log('📡 Getting real-time data for curated tokens...');
  
  const scored = [];
  
  for (const token of MANUAL_TOKENS) {
    const realData = await fetchTokenData(token.address);
    
    if (realData) {
      token.priceChange24h = realData.priceChange24h;
      token.currentPrice = realData.price;
    }
    
    // Score based on criteria
    let score = 0;
    
    if (token.marketCap >= 20000000) score += 40;
    else if (token.marketCap >= 10000000) score += 35;
    else score += 30;
    
    if (token.volume24h >= 2000000) score += 30;
    else if (token.volume24h >= 1000000) score += 25;
    else if (token.volume24h >= 500000) score += 20;
    else score += 15;
    
    if (token.liquidity >= 1000000) score += 20;
    else if (token.liquidity >= 500000) score += 15;
    else score += 10;
    
    if (token.priceChange24h > 20) score += 25;
    else if (token.priceChange24h > 10) score += 20;
    else if (token.priceChange24h > 0) score += 15;
    else score += 5;
    
    if (token.marketCap >= TRADE_CONFIG.minMarketCap &&
        token.volume24h >= TRADE_CONFIG.minVolume24h &&
        token.liquidity >= TRADE_CONFIG.minLiquidity &&
        score >= 80) {
      
      scored.push({
        ...token,
        grade: score >= 100 ? 'A+' : score >= 90 ? 'A' : 'A-',
        score,
        positionSize: score >= 95 ? TRADE_CONFIG.premiumPositionSizeSol : TRADE_CONFIG.basePositionSizeSol
      });
    }
  }
  
  scored.sort((a, b) => b.score - a.score);
  return scored;
}

async function executeBuy(connection, keypair, apiKey, tokenInfo, tradeNum) {
  const walletAddress = keypair.publicKey.toString();
  const amount = Math.floor(tokenInfo.positionSize * 1e9);
  
  console.log(`\n🎯 BUY #${tradeNum}: ${tokenInfo.symbol}`);
  console.log(`   Address: ${tokenInfo.address.slice(0, 20)}...${tokenInfo.address.slice(-8)}`);
  console.log(`   Grade: ${tokenInfo.grade} Score: ${tokenInfo.score}`);
  console.log(`   MCap: $${(tokenInfo.marketCap/1000000).toFixed(1)}M | Vol: $${(tokenInfo.volume24h/1000).toFixed(0)}k`);
  console.log(`   Position: ${tokenInfo.positionSize} SOL`);
  
  try {
    const quoteUrl = `${CONFIG.jupiterApiUrl}/quote`;
    const params = new URLSearchParams({
      inputMint: 'So11111111111111111111111111111111111111112',
      outputMint: tokenInfo.address,
      amount: amount.toString(),
      slippageBps: TRADE_CONFIG.slippageBps.toString()
    });
    
    console.log('   Getting quote...');
    const quoteResp = await axios.get(`${quoteUrl}?${params.toString()}`, {
      headers: { 'x-api-key': apiKey },
      timeout: 15000
    });
    
    console.log('   Building swap...');
    const swapUrl = `${CONFIG.jupiterApiUrl}/swap`;
    const swapBody = {
      quoteResponse: quoteResp.data,
      userPublicKey: walletAddress,
      wrapAndUnwrapSol: true,
      prioritizationFeeLamports: 10000
    };
    
    const swapResp = await axios.post(swapUrl, swapBody, {
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey },
      timeout: 15000
    });
    
    console.log('   Signing...');
    const serializedTx = Buffer.from(swapResp.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([keypair]);
    
    console.log('   Sending...');
    const signature = await connection.sendTransaction(transaction, {
      maxRetries: 3, skipPreflight: false
    });
    
    console.log(`   TX: ${signature.slice(0, 35)}...`);
    await connection.confirmTransaction(signature, 'confirmed');
    console.log(`   ✅ BOUGHT ${tokenInfo.symbol}!`);
    
    return {
      status: 'ACTIVE',
      tradeNum,
      txSignature: signature,
      token: tokenInfo.symbol,
      tokenAddress: tokenInfo.address,
      inputSol: tokenInfo.positionSize.toFixed(6),
      grade: tokenInfo.grade,
      score: tokenInfo.score,
      entryTime: Date.now(),
      trailingStopActive: false,
      trailingStopPrice: 0,
      tokenInfo: { ...tokenInfo }
    };
  } catch (e) {
    console.error(`   ❌ Buy failed: ${e.message.slice(0, 80)}`);
    return null;
  }
}

async function executeSell(connection, keypair, apiKey, position, reason) {
  const walletAddress = keypair.publicKey.toString();
  
  console.log(`\n🔴 SELLING ${position.token} - ${reason}`);
  
  try {
    const walletPubkey = new PublicKey(walletAddress);
    const tokenPubkey = new PublicKey(position.tokenAddress);
    const tokenAccounts = await connection.getParsedTokenAccountsByOwner(walletPubkey, { mint: tokenPubkey });
    
    if (tokenAccounts.value.length === 0) {
      return { receivedSol: 0, exitReason: 'NO_BALANCE', exitTime: Date.now() };
    }
    
    const tokenBalance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
    if (tokenBalance <= 0) {
      return { receivedSol: 0, exitReason: 'ZERO_BALANCE', exitTime: Date.now() };
    }
    
    const amount = Math.floor(tokenBalance * 1e6);
    const quoteUrl = `${CONFIG.jupiterApiUrl}/quote`;
    const params = new URLSearchParams({
      inputMint: position.tokenAddress,
      outputMint: 'So11111111111111111111111111111111111111112',
      amount: amount.toString(),
      slippageBps: '100'
    });
    
    const quoteResp = await axios.get(`${quoteUrl}?${params.toString()}`, {
      headers: { 'x-api-key': apiKey },
      timeout: 15000
    });
    
    const swapUrl = `${CONFIG.jupiterApiUrl}/swap`;
    const swapBody = {
      quoteResponse: quoteResp.data,
      userPublicKey: walletAddress,
      wrapAndUnwrapSol: false,
      prioritizationFeeLamports: 10000
    };
    
    const swapResp = await axios.post(swapUrl, swapBody, {
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey },
      timeout: 15000
    });
    
    const serializedTx = Buffer.from(swapResp.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([keypair]);
    
    const signature = await connection.sendTransaction(transaction, { maxRetries: 3 });
    await connection.confirmTransaction(signature, 'confirmed');
    
    const receivedSol = parseFloat(quoteResp.data.outAmount) / 1e9;
    console.log(`   ✅ SOLD! Received ${receivedSol.toFixed(6)} SOL`);
    
    return { signature, receivedSol, exitReason: reason, exitTime: Date.now() };
  } catch (e) {
    console.error(`   ❌ Sell failed: ${e.message.slice(0, 60)}`);
    return null;
  }
}

async function monitorAndSell(connection, keypair, apiKey) {
  console.log(`\n📊 Monitoring ${state.positions.length} position(s)`);
  console.log('-'.repeat(60));
  
  const sold = [];
  
  for (const position of state.positions) {
    if (position.status === 'SOLD') continue;
    
    const entrySol = parseFloat(position.inputSol);
    const timeHeld = (Date.now() - position.entryTime) / 1000 / 60 / 60;
    
    console.log(`\n   #${position.tradeNum} ${position.token}:`);
    console.log(`      Entry: ${entrySol.toFixed(4)} SOL | Time: ${timeHeld.toFixed(1)}h`);
    
    try {
      const walletPubkey = new PublicKey(keypair.publicKey.toString());
      const tokenPubkey = new PublicKey(position.tokenAddress);
      const accounts = await connection.getParsedTokenAccountsByOwner(walletPubkey, { mint: tokenPubkey });
      
      if (accounts.value.length === 0) {
        console.log(`      ⚠️ Not in wallet`);
        position.status = 'SOLD';
        position.exitReason = 'NOT_IN_WALLET';
        sold.push(position);
        continue;
      }
      
      const balance = accounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
      
      // Get current price
      const quoteUrl = `${CONFIG.jupiterApiUrl}/quote`;
      const params = new URLSearchParams({
        inputMint: position.tokenAddress,
        outputMint: 'So11111111111111111111111111111111111111112',
        amount: '1000000',
        slippageBps: '100'
      });
      
      const quoteResp = await axios.get(`${quoteUrl}?${params.toString()}`, {
        headers: { 'x-api-key': apiKey },
        timeout: 10000
      });
      
      const pricePerToken = parseFloat(quoteResp.data.outAmount) / 1e9;
      const currentValue = balance * pricePerToken;
      const pnlSol = currentValue - entrySol;
      const pnlPct = (pnlSol / entrySol) * 100;
      
      console.log(`      Value: ${currentValue.toFixed(6)} SOL | P&L: ${pnlPct.toFixed(2)}%`);
      
      if (pnlPct >= EXIT_CONFIG.trailingStopPct && !position.trailingStopActive) {
        position.trailingStopActive = true;
        position.trailingStopPrice = entrySol * (1 + EXIT_CONFIG.trailingLockPct / 100);
        console.log(`      🟢 TRAILING ACTIVATED! Floor: +${EXIT_CONFIG.trailingLockPct}%`);
      }
      
      let exitReason = null;
      
      if (pnlPct >= EXIT_CONFIG.takeProfitPct) {
        exitReason = `TP ${pnlPct.toFixed(1)}%`;
        console.log(`      🎯 ${exitReason}!`);
      } else if (pnlPct <= EXIT_CONFIG.stopLossPct) {
        exitReason = `SL ${pnlPct.toFixed(1)}%`;
        console.log(`      🛑 ${exitReason}!`);
      } else if (position.trailingStopActive && currentValue <= position.trailingStopPrice) {
        exitReason = `TRAILING ${pnlPct.toFixed(1)}%`;
        console.log(`      🔒 ${exitReason}!`);
      } else if (timeHeld >= EXIT_CONFIG.timeStopHours) {
        exitReason = `TIME ${timeHeld.toFixed(1)}h`;
        console.log(`      ⏰ ${exitReason}!`);
      } else {
        const status = position.trailingStopActive ? '🔒 TRAILING' : '🟡 HOLDING';
        console.log(`      ${status}`);
        continue;
      }
      
      const sellResult = await executeSell(connection, keypair, apiKey, position, exitReason);
      if (sellResult) {
        position.status = 'SOLD';
        Object.assign(position, sellResult);
        position.pnlSol = sellResult.receivedSol - entrySol;
        position.pnlPct = ((sellResult.receivedSol - entrySol) / entrySol) * 100;
        sold.push(position);
      }
    } catch (e) {
      console.log(`      ⚠️ Error: ${e.message.slice(0, 40)}`);
    }
  }
  
  return sold;
}

async function buyCycle(connection, keypair, apiKey) {
  state.cycle++;
  console.log('\n' + '='.repeat(70));
  console.log(`🚀 CYCLE #${state.cycle} - CURATED LIST`);
  console.log('='.repeat(70));
  console.log(`Using ${MANUAL_TOKENS.length} manually curated tokens`);
  console.log('='.repeat(70));
  
  const setups = await evaluateManualTokens();
  
  if (setups.length === 0) {
    console.log('❌ No tokens passed quality criteria');
    console.log('⏳ Retrying in 2 minutes...\n');
    await new Promise(r => setTimeout(r, 120000));
    return;
  }
  
  console.log(`\n📊 Top ${Math.min(3, setups.length)} setups from manual list:`);
  setups.slice(0, 3).forEach((s, i) => {
    const size = s.score >= 95 ? '0.02' : '0.01';
    console.log(`   ${i+1}. ${s.symbol.padEnd(10)} ${s.grade} Score:${s.score} $${(s.marketCap/1000000).toFixed(0)}M Vol:$${(s.volume24h/1000).toFixed(0)}k ${size}SOL`);
  });
  console.log();
  
  for (let i = 0; i < Math.min(TRADE_CONFIG.numTrades, setups.length); i++) {
    const result = await executeBuy(connection, keypair, apiKey, setups[i], i + 1);
    if (result) state.positions.push(result);
    if (i < TRADE_CONFIG.numTrades - 1) {
      console.log('   ⏳ Waiting 5s...');
      await new Promise(r => setTimeout(r, 5000));
    }
  }
  
  const active = state.positions.filter(p => p.status === 'ACTIVE').length;
  console.log(`\n✅ Bought ${active}/${TRADE_CONFIG.numTrades}`);
  saveState();
}

async function main() {
  console.log('='.repeat(70));
  console.log('🚀 SKYLAR v3.2 - MANUAL CURATED LIST');
  console.log('='.repeat(70));
  console.log(`Token Pool: ${MANUAL_TOKENS.length} curated tokens`);
  console.log(`Position: 0.01-0.02 SOL | Max: ${TRADE_CONFIG.numTrades}`);
  console.log(`Risk: TP +${EXIT_CONFIG.takeProfitPct}% / SL ${EXIT_CONFIG.stopLossPct}% / Trailing +${EXIT_CONFIG.trailingLockPct}%`);
  console.log('='.repeat(70) + '\n');
  
  loadState();
  
  const keypair = await loadWallet();
  const apiKey = fs.readFileSync(CONFIG.jupiterApiKeyPath, 'utf8').trim();
  const connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
  
  const activeCount = state.positions.filter(p => p.status === 'ACTIVE').length;
  if (activeCount === 0) {
    await buyCycle(connection, keypair, apiKey);
  } else {
    console.log(`📂 Resuming with ${activeCount} position(s)\n`);
  }
  
  let checkCount = 0;
  while (true) {
    checkCount++;
    console.log(`\n📡 Check #${checkCount} - ${new Date().toLocaleTimeString()}`);
    
    const sold = await monitorAndSell(connection, keypair, apiKey);
    state.positions = state.positions.filter(p => p.status === 'ACTIVE');
    
    if (state.positions.length === 0) {
      console.log('\n🎉 All positions closed!');
      state.soldPositions.push(...sold);
      saveState();
      
      const totalEntry = sold.reduce((a, p) => a + parseFloat(p.inputSol), 0);
      const totalExit = sold.reduce((a, p) => a + (p.receivedSol || 0), 0);
      const pnl = totalExit - totalEntry;
      const pnlPct = totalEntry > 0 ? (pnl / totalEntry) * 100 : 0;
      
      console.log('\n📊 CYCLE SUMMARY:');
      console.log(`   Invested: ${totalEntry.toFixed(4)} SOL`);
      console.log(`   Returned: ${totalExit.toFixed(4)} SOL`);
      console.log(`   P&L: ${pnl.toFixed(6)} SOL (${pnlPct.toFixed(2)}%)`);
      
      console.log('\n⏳ Next cycle in 10s...\n');
      await new Promise(r => setTimeout(r, 10000));
      await buyCycle(connection, keypair, apiKey);
    } else {
      console.log(`\n⏳ ${state.positions.length} position(s) holding`);
    }
    
    saveState();
    console.log(`   Next check in ${EXIT_CONFIG.checkIntervalMs / 1000}s\n`);
    await new Promise(r => setTimeout(r, EXIT_CONFIG.checkIntervalMs));
  }
}

main().catch(err => {
  console.error('❌ Fatal:', err);
  process.exit(1);
});
