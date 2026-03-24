const axios = require('axios');
const fs = require('fs');

// Common Solana token mints with HIGH liquidity
const TOKENS = {
  SOL: { mint: 'So11111111111111111111111111111111111111112', decimals: 9, name: 'Wrapped SOL' },
  USDC: { mint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', decimals: 6, name: 'USDC' },
  BONK: { mint: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', decimals: 5, name: 'BONK' }
};

function loadApiKey() {
  try {
    return fs.readFileSync('./.secrets/jupiter.key', 'utf8').trim();
  } catch (e) {
    console.log('Key read error:', e.message);
    return null;
  }
}

async function testJupiter() {
  const apiKey = loadApiKey();
  console.log('API Key loaded:', apiKey ? `${apiKey.substring(0,8)}...${apiKey.slice(-4)}` : 'NONE');
  
  if (!apiKey) return;
  
  console.log('\n=== Jupiter API Debug ===\n');
  
  // Test pairs with better amounts
  const testPairs = [
    { input: TOKENS.SOL, output: TOKENS.USDC, amount: '1000000000', label: '1 SOL' },        // 1 SOL
    { input: TOKENS.SOL, output: TOKENS.USDC, amount: '10000000000', label: '10 SOL' },     // 10 SOL  
    { input: TOKENS.SOL, output: TOKENS.BONK, amount: '500000000', label: '0.5 SOL' },       // 0.5 SOL
  ];
  
  const endpoints = [
    'https://api.jup.ag/v6/quote',
    'https://api.jup.ag/quote',
    'https://api.jup.ag/swap/v1/quote',
    'https://api.jup.ag/v4/quote'
  ];
  
  for (const endpoint of endpoints) {
    console.log(`\n📍 Testing: ${endpoint}`);
    
    for (const pair of testPairs) {
      const params = {
        inputMint: pair.input.mint,
        outputMint: pair.output.mint,
        amount: pair.amount,
        slippageBps: 50
      };
      
      const headers = { 'x-api-key': apiKey };
      
      try {
        const res = await axios.get(endpoint, { params, headers, timeout: 10000 });
        console.log(`  ${pair.label}: ✅ Status ${res.status}`);
        if (res.status === 200) {
          console.log('\n🎉 WORKING! Sample:', JSON.stringify(res.data).substring(0, 200));
        }
      } catch (e) {
        const msg = e.response?.data?.message || e.response?.status || e.message
        console.log(`  ${pair.label}: ❌ ${msg.substring(0, 50)}`);
      }
    }
  }
  
  console.log('\n=== Done ===');
}

testJupiter().catch(console.error);
