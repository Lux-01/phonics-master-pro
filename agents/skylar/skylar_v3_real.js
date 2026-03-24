#!/usr/bin/env node
/**
 * SKYLAR v3.1 - REAL TOKEN ADDRESSES
 * Uses DexScreener pairs for actual mint addresses
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

const BIRDEYE_KEY = '6335463fca7340f9a2c73eacd5a37f64';

const TRADE_CONFIG = {
  basePositionSizeSol: 0.01,
  premiumPositionSizeSol: 0.02,
  numTrades: 1,
  slippageBps: 100,
  // RELAXED FILTERS (Option 2)
  minVolume24h: 20000,      // Was 50k, now 20k
  minMarketCap: 15000,      // Was 20k, now 15k  
  minLiquidity: 15000,      // Was 30k, now 15k
  maxMarketCap: 200000,
  maxEntryHours: 3,
  minGreenCandles: 3
};

const EXIT_CONFIG = {
  takeProfitPct: 15,
  stopLossPct: -5,
  trailingStopPct: 10,
  trailingLockPct: 5,
  timeStopHours: 4,
  checkIntervalMs: 30000
};

const STATE_FILE = '/home/skux/.openclaw/workspace/agents/skylar/skylar_state_v3.json';

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

// Fetch REAL tokens from DexScreener pairs
async function fetchRealTokens() {
  console.log('📡 Fetching REAL token pairs from DexScreener...');
  
  try {
    // Get trending pairs from Raydium
    const url = 'https://api.dexscreener.com/latest/dex/pairs/solana/raydium';
    const response = await axios.get(url, { timeout: 15000 });
    
    if (response.data && response.data.pairs) {
      const pairs = response.data.pairs
        .filter(p => {
          // Filter for tokens with good metrics
          const volume = parseFloat(p.volume?.h24 || 0);
          const mcap = parseFloat(p.fdv || p.marketCap || 0);
          const liq = parseFloat(p.liquidity?.usd || 0);
          const priceChange = parseFloat(p.priceChange?.h24 || 0);
          
          return volume > 50000 && 
                 mcap > 20000 && 
                 mcap < 200000 && 
                 liq > 30000 &&
                 priceChange > 5;
        })
        .map(p => ({
          symbol: p.baseToken?.symbol || 'UNKNOWN',
          address: p.baseToken?.address,
          marketCap: parseFloat(p.fdv || p.marketCap || 25000),
          volume24h: parseFloat(p.volume?.h24 || 60000),
          priceChange24h: parseFloat(p.priceChange?.h24 || 20),
          liquidity: parseFloat(p.liquidity?.usd || 35000),
          pairAddress: p.pairAddress
        }))
        .filter(t => t.address && t.address.length > 40); // Valid Solana addresses
      
      console.log(`   Found ${pairs.length} valid pairs with real addresses`);
      
      if (pairs.length > 0) return pairs;
    }
  } catch (e) {
    console.log('   DexScreener error:', e.message.slice(0, 50));
  }
  
  // Fallback: Use Birdeye trending
  console.log('   Trying Birdeye trending...');
  try {
    const url = 'https://public-api.birdeye.so/defi/token_trending?sort_by=volume24hUSD&sort_type=desc&offset=0&limit=20';
    const response = await axios.get(url, {
      headers: { 'X-API-KEY': BIRDEYE_KEY },
      timeout: 15000
    });
    
    if (response.data?.data?.items) {
      const tokens = response.data.data.items
        .filter(t => {
          const volume = t.volume24hUSD || 0;
          const mcap = t.marketCap || 0;
          return volume > 50000 && mcap > 20000 && mcap < 200000;
        })
        .map(t => ({
          symbol: t.symbol || 'UNKNOWN',
          address: t.address,
          marketCap: t.marketCap || 25000,
          volume24h: t.volume24hUSD || 60000,
          priceChange24h: (t.priceChange24hPercent || 20) * 100,
          liquidity: t.liquidity || 35000
        }));
      
      console.log(`   Found ${tokens.length} tokens from Birdeye`);
      if (tokens.length > 0) return tokens;
    }
  } catch (e) {
    console.log('   Birdeye error:', e.message.slice(0, 50));
  }
  
  console.log('   ⚠️ No real tokens found - will retry');
  return [];
}

function evaluateToken(token) {
  const mcap = token.marketCap || 0;
  const volume = token.volume24h || 0;
  const liquidity = token.liquidity || 0;
  const priceChange = token.priceChange24h || 0;
  
  if (mcap < TRADE_CONFIG.minMarketCap || mcap > TRADE_CONFIG.maxMarketCap) return null;
  if (volume < TRADE_CONFIG.minVolume24h) return null;
  if (liquidity < TRADE_CONFIG.minLiquidity) return null;
  
  let score = 0;
  if (mcap < 30000) score += 40;
  else if (mcap < 50000) score += 35;
  else score += 30;
  
  if (volume > 150000) score += 30;
  else if (volume > 100000) score += 25;
  else if (volume > 50000) score += 20;
  else score += 15;
  
  if (liquidity > 50000) score += 20;
  else if (liquidity > 30000) score += 15;
  else score += 10;
  
  if (priceChange > 40) score += 25;
  else if (priceChange > 25) score += 20;
  else if (priceChange > 15) score += 15;
  else score += 10;
  
  if (score < 90) return null;
  
  const positionSize = score >= 95 ? TRADE_CONFIG.premiumPositionSizeSol : TRADE_CONFIG.basePositionSizeSol;
  
  return {
    symbol: token.symbol,
    address: token.address,
    mcap, volume, liquidity, priceChange,
    grade: score >= 100 ? 'A+' : score >= 95 ? 'A' : 'A-',
    score,
    positionSize
  };
}

async function executeBuy(connection, keypair, apiKey, tokenInfo, tradeNum) {
  const walletAddress = keypair.publicKey.toString();
  const amount = Math.floor(tokenInfo.positionSize * 1e9);
  
  console.log(`\n🎯 BUY #${tradeNum}/${TRADE_CONFIG.numTrades}: ${tokenInfo.symbol}`);
  console.log(`   Address: ${tokenInfo.address.slice(0, 20)}...${tokenInfo.address.slice(-8)}`);
  console.log(`   Grade: ${tokenInfo.grade} | Score: ${tokenInfo.score}`);
  console.log(`   MCap: $${tokenInfo.mcap.toLocaleString()} | Vol: $${tokenInfo.volume.toLocaleString()}`);
  console.log(`   Position: ${tokenInfo.positionSize} SOL`);
  
  try {
    const quoteUrl = `${CONFIG.jupiterApiUrl}/quote`;
    const params = new URLSearchParams({
      inputMint: 'So11111111111111111111111111111111111111112',
      outputMint: tokenInfo.address,
      amount: amount.toString(),
      slippageBps: TRADE_CONFIG.slippageBps.toString()
    });
    
    console.log('   Getting Jupiter quote...');
    const quoteResp = await axios.get(`${quoteUrl}?${params.toString()}`, {
      headers: { 'x-api-key': apiKey },
      timeout: 15000
    });
    
    console.log('   Building swap transaction...');
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
    
    console.log('   Signing transaction...');
    const serializedTx = Buffer.from(swapResp.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([keypair]);
    
    console.log('   Sending to network...');
    const signature = await connection.sendTransaction(transaction, {
      maxRetries: 3, skipPreflight: false
    });
    
    console.log(`   TX: ${signature}`);
    console.log(`   Waiting for confirmation...`);
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
      trailingStopPrice: 0
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
    const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
      walletPubkey, { mint: tokenPubkey }
    );
    
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
  console.log(`\n📊 Monitoring ${state.positions.length} positions`);
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
      
      // Get price
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
      
      // Trailing stop
      if (pnlPct >= EXIT_CONFIG.trailingStopPct && !position.trailingStopActive) {
        position.trailingStopActive = true;
        position.trailingStopPrice = entrySol * (1 + EXIT_CONFIG.trailingLockPct / 100);
        console.log(`      🟢 TRAILING ACTIVATED! Floor: +${EXIT_CONFIG.trailingLockPct}%`);
      }
      
      // Check exits
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
  console.log(`🚀 CYCLE #${state.cycle} - HIGH QUALITY SETUPS`);
  console.log('='.repeat(70));
  console.log(`Filters: MCap $${TRADE_CONFIG.minMarketCap}+ | Vol $${TRADE_CONFIG.minVolume24h}+`);
  console.log(`Max positions: ${TRADE_CONFIG.numTrades} | Position size: 0.01-0.02 SOL`);
  console.log('='.repeat(70));
  
  const tokens = await fetchRealTokens();
  
  if (tokens.length === 0) {
    console.log('⏳ No tokens found, retrying in 2 minutes...\n');
    await new Promise(r => setTimeout(r, 120000));
    return;
  }
  
  const setups = tokens.map(evaluateToken).filter(s => s !== null);
  setups.sort((a, b) => b.score - a.score);
  
  if (setups.length === 0) {
    console.log('⏳ No setups passed filters, retrying...\n');
    await new Promise(r => setTimeout(r, 60000));
    return;
  }
  
  console.log(`\n📊 Top ${Math.min(5, setups.length)} setups:`);
  setups.slice(0, 5).forEach((s, i) => {
    const size = s.score >= 95 ? '0.02' : '0.01';
    console.log(`   ${i+1}. ${s.symbol.padEnd(10)} ${s.grade} Score:${s.score} $${(s.mcap/1000).toFixed(0)}k Vol:$${(s.volume/1000).toFixed(0)}k ${size}SOL`);
  });
  console.log();
  
  for (let i = 0; i < Math.min(TRADE_CONFIG.numTrades, setups.length); i++) {
    const result = await executeBuy(connection, keypair, apiKey, setups[i], i + 1);
    if (result) state.positions.push(result);
  }
  
  const active = state.positions.filter(p => p.status === 'ACTIVE').length;
  console.log(`\n✅ Bought ${active}/${TRADE_CONFIG.numTrades}`);
  saveState();
}

async function main() {
  console.log('='.repeat(70));
  console.log('🚀 SKYLAR v3.1 - REAL TOKENS');
  console.log('='.repeat(70));
  console.log(`Quality: MCap $${TRADE_CONFIG.minMarketCap}+ | Vol $${TRADE_CONFIG.minVolume24h}+`);
  console.log(`Positions: ${TRADE_CONFIG.numTrades} max (0.01-0.02 SOL)`);
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
    console.log(`📂 Resuming with ${activeCount} positions\n`);
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
      
      // Summary
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
      console.log(`\n⏳ ${state.positions.length} positions holding`);
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