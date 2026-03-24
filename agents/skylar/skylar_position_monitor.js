#!/usr/bin/env node
/**
 * SKYLAR AUTO-SELL MONITOR
 * Tracks positions and auto-exits at +15% TP / -7% SL / 4h time stop
 */

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

// Exit config
const EXIT_CONFIG = {
  takeProfitPct: 15,
  stopLossPct: -7,
  timeStopHours: 4,
  checkIntervalMs: 30000, // 30 seconds
  minPositionSeconds: 60  // Don't sell within 1 minute of entry
};

// State
let positions = [];
let soldPositions = [];

// Load wallet
async function loadWallet() {
  const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
  let keypair;
  try {
    const secretKeyBytes = Buffer.from(secretKey, 'base64');
    keypair = Keypair.fromSecretKey(secretKeyBytes);
  } catch (e) {
    const bs58 = require('bs58');
    keypair = Keypair.fromSecretKey(bs58.decode(secretKey));
  }
  return keypair;
}

// Load positions from executed trades
function loadPositions() {
  try {
    const data = JSON.parse(fs.readFileSync('/home/skux/.openclaw/workspace/agents/skylar/skylar_live_executed.json', 'utf8'));
    const positions = data.trades.filter(t => t.status === 'SUCCESS');
    return positions.map(p => ({
      ...p,
      entryTime: new Date(p.timestamp).getTime(),
      sold: false
    }));
  } catch (e) {
    console.error('Failed to load positions:', e.message);
    return [];
  }
}

// Get token balance
async function getTokenBalance(connection, walletAddress, tokenAddress) {
  try {
    const walletPubkey = new PublicKey(walletAddress);
    const tokenPubkey = new PublicKey(tokenAddress);
    
    const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
      walletPubkey,
      { mint: tokenPubkey }
    );
    
    if (tokenAccounts.value.length > 0) {
      const balance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
      return balance;
    }
    return 0;
  } catch (e) {
    return 0;
  }
}

// Get current token price in SOL from Jupiter
async function getTokenPrice(tokenAddress) {
  try {
    const url = `${CONFIG.jupiterApiUrl}/quote`;
    const params = new URLSearchParams({
      inputMint: tokenAddress,
      outputMint: 'So11111111111111111111111111111111111111112', // SOL
      amount: '1000000', // 1 token in micro-units
      slippageBps: '100'
    });
    
    const response = await axios.get(`${url}?${params.toString()}`, {
      timeout: 10000
    });
    
    if (response.data && response.data.outAmount) {
      const solPerToken = parseFloat(response.data.outAmount) / 1e9;
      return solPerToken;
    }
    return null;
  } catch (e) {
    return null;
  }
}

// Execute sell
async function executeSell(connection, keypair, apiKey, position) {
  const walletAddress = keypair.publicKey.toString();
  const tokenAddress = position.tokenAddress;
  const tokenBalance = await getTokenBalance(connection, walletAddress, tokenAddress);
  
  if (tokenBalance <= 0) {
    console.log(`   ⚠️ No balance for ${position.token}`);
    return null;
  }
  
  console.log(`\n🔴 SELLING ${position.token}`);
  console.log(`   Balance: ${tokenBalance.toFixed(6)} tokens`);
  
  // Get Jupiter quote for selling
  const amount = Math.floor(tokenBalance * 1e6); // Assuming 6 decimals
  
  try {
    const quoteUrl = `${CONFIG.jupiterApiUrl}/quote`;
    const params = new URLSearchParams({
      inputMint: tokenAddress,
      outputMint: 'So11111111111111111111111111111111111111112',
      amount: amount.toString(),
      slippageBps: '100'
    });
    
    const quoteResponse = await axios.get(`${quoteUrl}?${params.toString()}`, {
      headers: { 'x-api-key': apiKey },
      timeout: 15000
    });
    
    const quoteData = quoteResponse.data;
    const expectedSol = (parseFloat(quoteData.outAmount) / 1e9).toFixed(6);
    
    console.log(`   Expected SOL: ${expectedSol}`);
    
    // Build swap
    const swapUrl = `${CONFIG.jupiterApiUrl}/swap`;
    const swapBody = {
      quoteResponse: quoteData,
      userPublicKey: walletAddress,
      wrapAndUnwrapSol: false,
      prioritizationFeeLamports: 10000
    };
    
    const swapResponse = await axios.post(swapUrl, swapBody, {
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey
      },
      timeout: 15000
    });
    
    // Sign and send
    const serializedTx = Buffer.from(swapResponse.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([keypair]);
    
    const signature = await connection.sendTransaction(transaction, {
      maxRetries: 3,
      skipPreflight: false
    });
    
    console.log(`   TX: ${signature}`);
    console.log(`   Explorer: https://solscan.io/tx/${signature}`);
    
    // Confirm
    await connection.confirmTransaction(signature, 'confirmed');
    console.log(`   ✅ SOLD!`);
    
    return {
      signature,
      token: position.token,
      tokenAddress,
      amount: tokenBalance,
      receivedSol: parseFloat(expectedSol),
      exitTime: new Date().toISOString()
    };
    
  } catch (e) {
    console.error(`   ❌ Sell failed: ${e.message}`);
    return null;
  }
}

// Main monitor loop
async function monitorPositions() {
  console.log('='.repeat(70));
  console.log('🎯 SKYLAR AUTO-SELL MONITOR');
  console.log('='.repeat(70));
  console.log(`Take Profit: +${EXIT_CONFIG.takeProfitPct}%`);
  console.log(`Stop Loss: ${EXIT_CONFIG.stopLossPct}%`);
  console.log(`Time Stop: ${EXIT_CONFIG.timeStopHours} hours`);
  console.log(`Check Interval: ${EXIT_CONFIG.checkIntervalMs / 1000}s`);
  console.log('='.repeat(70) + '\n');
  
  // Load positions
  positions = loadPositions();
  
  if (positions.length === 0) {
    console.log('❌ No positions found to monitor');
    process.exit(1);
  }
  
  console.log(`📊 Monitoring ${positions.length} positions:\n`);
  positions.forEach(p => {
    console.log(`   #${p.tradeNum}: ${p.token} (Entry: ${p.inputSol} SOL)`);
  });
  console.log();
  
  // Setup connections
  const keypair = await loadWallet();
  const apiKey = fs.readFileSync(CONFIG.jupiterApiKeyPath, 'utf8').trim();
  const connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
  
  let checkCount = 0;
  
  while (true) {
    checkCount++;
    const now = Date.now();
    
    console.log(`\n📡 Check #${checkCount} - ${new Date().toLocaleTimeString()}`);
    console.log('-'.repeat(70));
    
    for (const position of positions) {
      if (position.sold) continue;
      
      const entryTime = position.entryTime;
      const entrySol = parseFloat(position.inputSol);
      const timeHeld = (now - entryTime) / 1000 / 60 / 60; // hours
      const minutesHeld = (now - entryTime) / 1000 / 60;
      
      // Skip if too recent (avoid immediate re-sell)
      if (minutesHeld < EXIT_CONFIG.minPositionSeconds / 60) {
        console.log(`   #${position.tradeNum} ${position.token}: ⏳ Just entered (${Math.floor(minutesHeld)}m ago)`);
        continue;
      }
      
      // Get current price
      const tokenPrice = await getTokenPrice(position.tokenAddress);
      
      if (!tokenPrice) {
        console.log(`   #${position.tradeNum} ${position.token}: ⚠️ Price unavailable`);
        continue;
      }
      
      // Calculate P&L
      const tokenBalance = await getTokenBalance(connection, keypair.publicKey.toString(), position.tokenAddress);
      const currentValue = tokenBalance * tokenPrice;
      const pnlSol = currentValue - entrySol;
      const pnlPct = (pnlSol / entrySol) * 100;
      
      console.log(`   #${position.tradeNum} ${position.token}:`);
      console.log(`      Entry: ${entrySol.toFixed(4)} SOL | Current: ${currentValue.toFixed(4)} SOL`);
      console.log(`      P&L: ${pnlSol.toFixed(6)} SOL (${pnlPct.toFixed(2)}%) | Time: ${timeHeld.toFixed(1)}h`);
      
      // Check exit signals
      let exitReason = null;
      
      if (pnlPct >= EXIT_CONFIG.takeProfitPct) {
        exitReason = `TAKE PROFIT (${pnlPct.toFixed(1)}%)`;
        console.log(`      🟢 EXIT SIGNAL: ${exitReason}`);
      } else if (pnlPct <= EXIT_CONFIG.stopLossPct) {
        exitReason = `STOP LOSS (${pnlPct.toFixed(1)}%)`;
        console.log(`      🔴 EXIT SIGNAL: ${exitReason}`);
      } else if (timeHeld >= EXIT_CONFIG.timeStopHours) {
        exitReason = `TIME STOP (${timeHeld.toFixed(1)}h)`;
        console.log(`      ⏰ EXIT SIGNAL: ${exitReason}`);
      } else {
        const toTp = EXIT_CONFIG.takeProfitPct - pnlPct;
        const toSl = pnlPct - EXIT_CONFIG.stopLossPct;
        console.log(`      🟡 HOLDING | +${toTp.toFixed(1)}% to TP | -${toSl.toFixed(1)}% to SL`);
      }
      
      // Execute exit if triggered
      if (exitReason) {
        console.log(`\n   💥 EXECUTING SELL FOR ${exitReason}...`);
        const sellResult = await executeSell(connection, keypair, apiKey, position);
        
        if (sellResult) {
          position.sold = true;
          soldPositions.push({
            ...sellResult,
            originalEntry: position.inputSol,
            pnlSol: sellResult.receivedSol - entrySol,
            pnlPct: ((sellResult.receivedSol - entrySol) / entrySol) * 100,
            exitReason
          });
          
          // Save state
          fs.writeFileSync(
            '/home/skux/.openclaw/workspace/agents/skylar/skylar_sold_positions.json',
            JSON.stringify(soldPositions, null, 2)
          );
          
          console.log(`   ✅ Position closed!`);
        }
      }
    }
    
    // Check if all closed
    const remaining = positions.filter(p => !p.sold);
    if (remaining.length === 0) {
      console.log('\n' + '='.repeat(70));
      console.log('🎉 ALL POSITIONS CLOSED!');
      console.log('='.repeat(70));
      break;
    }
    
    console.log(`\n⏳ ${remaining.length} positions remaining...`);
    console.log(`   Next check in ${EXIT_CONFIG.checkIntervalMs / 1000} seconds`);
    
    await new Promise(r => setTimeout(r, EXIT_CONFIG.checkIntervalMs));
  }
  
  // Final report
  console.log('\n' + '='.repeat(70));
  console.log('📊 FINAL REPORT');
  console.log('='.repeat(70));
  
  let totalEntry = 0;
  let totalExit = 0;
  
  soldPositions.forEach(p => {
    totalEntry += parseFloat(p.originalEntry);
    totalExit += p.receivedSol;
    console.log(`\n   #${p.token}`);
    console.log(`      Entry: ${p.originalEntry} SOL | Exit: ${p.receivedSol.toFixed(6)} SOL`);
    console.log(`      P&L: ${p.pnlSol:+.6f} SOL (${p.pnlPct:+.2f}%)`);
    console.log(`      Reason: ${p.exitReason}`);
  });
  
  const totalPnl = totalExit - totalEntry;
  const totalPnlPct = (totalPnl / totalEntry) * 100;
  
  console.log('\n' + '='.repeat(70));
  console.log(`   Total Entry: ${totalEntry.toFixed(4)} SOL`);
  console.log(`   Total Exit: ${totalExit.toFixed(4)} SOL`);
  console.log(`   Total P&L: ${totalPnl:+.6f} SOL (${totalPnlPct:+.2f}%)`);
  console.log('='.repeat(70));
}

// Run
monitorPositions().catch(err => {
  console.error('❌ Monitor crashed:', err);
  process.exit(1);
});