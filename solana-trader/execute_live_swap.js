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

// Known tokens
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

async function executeTrade() {
  console.log('=== REAL TRADE EXECUTION ===\n');
  console.log('⚠️  This will execute an ACTUAL transaction on Solana mainnet\n');
  
  const connection = new Connection(CONFIG.rpcEndpoint, 'confirmed');
  
  // Load keys
  const apiKey = fs.readFileSync(CONFIG.jupiterApiKeyPath, 'utf8').trim();
  const secretKey = fs.readFileSync(CONFIG.walletKeyPath, 'utf8').trim();
  
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
  
  // Step 1: Get Quote
  console.log('\n📊 Getting Jupiter quote...');
  const amount = 100000; // 0.0001 SOL in lamports
  const slippage = 100; // 1%
  
  const quoteUrl = `${CONFIG.jupiterApiUrl}/quote`;
  const params = new URLSearchParams({
    inputMint: TOKENS.SOL.mint,
    outputMint: TOKENS.USDC.mint,
    amount: amount.toString(),
    slippageBps: slippage.toString()
  });
  
  const quoteResponse = await axios.get(`${quoteUrl}?${params.toString()}`, {
    headers: { 'x-api-key': apiKey },
    timeout: 15000
  });
  
  const quoteData = quoteResponse.data;
  const inputAmount = (parseFloat(quoteData.inAmount) / 1e9).toFixed(6);
  const outputAmount = (parseFloat(quoteData.outAmount) / 1e6).toFixed(6);
  const priceImpact = (parseFloat(quoteData.priceImpactPct) || 0).toFixed(4);
  
  console.log(`   Input: ${inputAmount} SOL`);
  console.log(`   Output: ${outputAmount} USDC`);
  console.log(`   Price Impact: ${priceImpact}%`);
  console.log(`   Slippage: ${slippage/100}%`);
  
  // Step 2: Build Swap
  console.log('\n🔨 Building swap transaction...');
  const swapUrl = `${CONFIG.jupiterApiUrl}/swap`;
  const swapBody = {
    quoteResponse: quoteData,
    userPublicKey: walletAddress,
    wrapAndUnwrapSol: true,
    prioritizationFeeLamports: 10000 // 0.00001 SOL
  };
  
  const swapResponse = await axios.post(swapUrl, swapBody, {
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey
    },
    timeout: 15000
  });
  
  const swapData = swapResponse.data;
  console.log(`   Transaction size: ${swapData.swapTransaction.length} bytes`);
  
  // Step 3: Sign and Send
  console.log('\n✍️  Signing transaction...');
  const serializedTx = Buffer.from(swapData.swapTransaction, 'base64');
  const transaction = VersionedTransaction.deserialize(serializedTx);
  transaction.sign([keypair]);
  console.log('   Transaction signed');
  
  console.log('\n📤 Sending transaction...');
  const signature = await connection.sendTransaction(transaction, {
    maxRetries: 3,
    skipPreflight: false,
    preflightCommitment: 'confirmed'
  });
  
  console.log(`\n⏳ Waiting for confirmation...`);
  console.log(`   TX Signature: ${signature}`);
  console.log(`   Explorer: https://solscan.io/tx/${signature}`);
  
  // Confirm
  const confirmation = await connection.confirmTransaction(signature, 'confirmed');
  
  if (confirmation.value.err) {
    throw new Error(`Transaction failed: ${JSON.stringify(confirmation.value.err)}`);
  }
  
  console.log('\n✅ Transaction confirmed!');
  
  // Get execution timestamp
  const now = new Date();
  
  return {
    status: 'SUCCESS',
    txSignature: signature,
    from: inputAmount,
    fromToken: 'SOL',
    to: outputAmount,
    toToken: 'USDC',
    slippage: `${slippage/100}%`,
    actualSlippage: `${priceImpact}%`,
    fee: '0.00001 SOL (priority)',
    solscanLink: `https://solscan.io/tx/${signature}`,
    timestamp: now.toISOString()
  };
}

// Execute
executeTrade()
  .then(result => {
    console.log('\n' + '='.repeat(50));
    console.log('=== REAL TRADE EXECUTED ===');
    console.log('='.repeat(50));
    console.log(`Status: ${result.status}`);
    console.log(`Tx Signature: ${result.txSignature}`);
    console.log(`From: ${result.from} ${result.fromToken}`);
    console.log(`Received: ${result.to} ${result.toToken}`);
    console.log(`Slippage: ${result.slippage}`);
    console.log(`Fee: ${result.fee}`);
    console.log(`Link: ${result.solscanLink}`);
    console.log(`Time: ${result.timestamp}`);
    console.log('='.repeat(50));
    
    // Write result to file
    fs.writeFileSync('/tmp/trade_result.json', JSON.stringify(result, null, 2));
  })
  .catch(err => {
    console.error('\n❌ TRADE FAILED:', err.message);
    if (err.response) {
      console.error('API Error:', err.response.data);
    }
    
    const result = {
      status: 'FAILED',
      reason: err.message,
      stage: 'execution',
      timestamp: new Date().toISOString()
    };
    fs.writeFileSync('/tmp/trade_result.json', JSON.stringify(result, null, 2));
    process.exit(1);
  });
