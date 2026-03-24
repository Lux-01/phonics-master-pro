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

async function executeSmokeTest() {
  console.log('═══════════════════════════════════════════');
  console.log('  RAPHAEL SMOKE TEST - JUPITER SWAPS');
  console.log('═══════════════════════════════════════════\n');

  const connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
  const apiKey = fs.readFileSync(CONFIG.jupiterApiKeyPath, 'utf8').trim();
  const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
  
  // Decode key
  let keypair;
  try {
    const secretKeyBytes = Buffer.from(secretKey, 'base64');
    keypair = Keypair.fromSecretKey(secretKeyBytes);
  } catch (e) {
    const bs58 = require('bs58');
    keypair = Keypair.fromSecretKey(bs58.decode(secretKey));
  }
  
  const walletAddress = keypair.publicKey.toString();
  console.log(`Wallet: ${walletAddress}`);
  
  // Check balance before
  const balanceBefore = await connection.getBalance(keypair.publicKey);
  console.log(`Balance: ${(balanceBefore / 1e9).toFixed(6)} SOL\n`);
  
  const results = {
    buyTx: null,
    sellTx: null,
    usdcReceived: 0,
    usdcSold: 0,
    balanceBefore: balanceBefore / 1e9,
    balanceAfter: 0,
    fees: 0,
    pnl: 0,
    errors: []
  };

  // ===== STEP 1: BUY USDC =====
  console.log('─── STEP 1: BUY USDC (0.0001 SOL) ───');
  try {
    const buyAmount = 100000; // 0.0001 SOL in lamports
    
    // Get quote
    const quoteUrl = `${CONFIG.jupiterApiUrl}/quote?` + new URLSearchParams({
      inputMint: TOKENS.SOL.mint,
      outputMint: TOKENS.USDC.mint,
      amount: buyAmount.toString(),
      slippageBps: '50'
    });
    
    const quoteRes = await axios.get(quoteUrl, { headers: { 'x-api-key': apiKey } });
    const quote = quoteRes.data;
    results.usdcReceived = parseFloat(quote.outAmount) / 1e6;
    console.log(`   Quote: 0.0001 SOL → ${results.usdcReceived.toFixed(6)} USDC`);
    
    // Build swap
    const swapRes = await axios.post(`${CONFIG.jupiterApiUrl}/swap`, {
      quoteResponse: quote,
      userPublicKey: walletAddress,
      wrapAndUnwrapSol: true,
      prioritizationFeeLamports: 50000
    }, { headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey } });
    
    // Execute
    const serializedTx = Buffer.from(swapRes.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([keypair]);
    
    results.buyTx = await connection.sendTransaction(transaction, { maxRetries: 3 });
    console.log(`   TX Sent: ${results.buyTx}`);
    
    await connection.confirmTransaction(results.buyTx, 'confirmed');
    console.log(`   ✅ BUY Confirmed`);
    
  } catch (e) {
    results.errors.push({'BUY ERROR': e.message});
    console.error(`   ❌ BUY Failed:`, e.message);
    return results;
  }

  // Small delay
  await new Promise(r => setTimeout(r, 2000));

  // ===== STEP 2: SELL USDC =====
  console.log('\n─── STEP 2: SELL USDC (full amount) ───');
  try {
    // Get USDC balance first
    const tokenAccounts = await connection.getParsedTokenAccountsByOwner(
      keypair.publicKey, { mint: new PublicKey(TOKENS.USDC.mint) }
    );
    
    let usdcBalance = 0;
    if (tokenAccounts.value.length > 0) {
      usdcBalance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.amount;
    }
    results.usdcSold = parseFloat(usdcBalance) / 1e6;
    console.log(`   USDC Balance: ${results.usdcSold.toFixed(6)} USDC`);
    
    // Get quote
    const quoteUrl = `${CONFIG.jupiterApiUrl}/quote?` + new URLSearchParams({
      inputMint: TOKENS.USDC.mint,
      outputMint: TOKENS.SOL.mint,
      amount: usdcBalance.toString(),
      slippageBps: '50'
    });
    
    const quoteRes = await axios.get(quoteUrl, { headers: { 'x-api-key': apiKey } });
    const quote = quoteRes.data;
    const solExpected = parseFloat(quote.outAmount) / 1e9;
    console.log(`   Quote: ${results.usdcSold.toFixed(6)} USDC → ${solExpected.toFixed(6)} SOL`);
    
    // Build swap
    const swapRes = await axios.post(`${CONFIG.jupiterApiUrl}/swap`, {
      quoteResponse: quote,
      userPublicKey: walletAddress,
      wrapAndUnwrapSol: true,
      prioritizationFeeLamports: 50000
    }, { headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey } });
    
    // Execute
    const serializedTx = Buffer.from(swapRes.data.swapTransaction, 'base64');
    const transaction = VersionedTransaction.deserialize(serializedTx);
    transaction.sign([keypair]);
    
    results.sellTx = await connection.sendTransaction(transaction, { maxRetries: 3 });
    console.log(`   TX Sent: ${results.sellTx}`);
    
    await connection.confirmTransaction(results.sellTx, 'confirmed');
    console.log(`   ✅ SELL Confirmed`);
    
  } catch (e) {
    results.errors.push({'SELL ERROR': e.message});
    console.error(`   ❌ SELL Failed:`, e.message);
  }

  // Small delay
  await new Promise(r => setTimeout(r, 2000));

  // ===== STEP 3: CALCULATE RESULTS =====
  console.log('\n─── STEP 3: VERIFY BALANCE ───');
  const balanceAfter = await connection.getBalance(keypair.publicKey);
  results.balanceAfter = balanceAfter / 1e9;
  console.log(`   Final Balance: ${results.balanceAfter.toFixed(6)} SOL`);
  
  results.fees = results.balanceBefore - results.balanceAfter;
  if (results.fees < 0) results.fees = 0;
  console.log(`   Fees (approx): ${results.fees.toFixed(6)} SOL`);
  
  return results;
}

// Run test
executeSmokeTest().then(results => {
  console.log('\n═══════════════════════════════════════════');
  console.log('  SMOKE TEST RESULTS');
  console.log('═══════════════════════════════════════════\n');
  
  console.log(`BUY Transaction:  ${results.buyTx || 'FAILED'}`);
  console.log(`SELL Transaction: ${results.sellTx || 'FAILED'}`);
  console.log(`\nUSDC Received:    ${results.usdcReceived.toFixed(6)} USDC`);
  console.log(`USDC Sold:        ${results.usdcSold.toFixed(6)} USDC`);
  console.log(`\nBalance Before:   ${results.balanceBefore.toFixed(6)} SOL`);
  console.log(`Balance After:    ${results.balanceAfter.toFixed(6)} SOL`);
  console.log(`Total Fees:       ${results.fees.toFixed(6)} SOL (~$${(results.fees * 78).toFixed(4)} USD)`);
  console.log(`Net PNL:          -${results.fees.toFixed(6)} SOL (fees only)`);
  
  if (results.errors.length > 0) {
    console.log(`\n⚠️ ERRORS ENCOUNTERED:`);
    results.errors.forEach(e => console.log(`   - ${JSON.stringify(e)}`));
  } else {
    console.log(`\n✅ No errors encountered`);
  }
  
  // Save results
  fs.writeFileSync('./smoke_test_results.json', JSON.stringify(results, null, 2));
  console.log('\nResults saved to: smoke_test_results.json');
  
}).catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
