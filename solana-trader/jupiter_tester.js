const axios = require('axios');
const fs = require('fs');

const CONFIG = {
  solMint: 'So11111111111111111111111111111111111111112',
  usdcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  apiEndpoints: [
    'https://api.jup.ag',
    'https://station.jup.ag'
  ]
};

async function loadApiKey() {
  try {
    return fs.readFileSync('./.secrets/jupiter.key', 'utf8').trim();
  } catch (e) {
    return null;
  }
}

async function testEndpoint(baseUrl, apiKey, label) {
  console.log(`\nTesting ${label} (${baseUrl})`);
  
  const url = `${baseUrl}/v6/quote`;
  const params = {
    inputMint: CONFIG.solMint,
    outputMint: CONFIG.usdcMint,
    amount: 100000000,
    slippageBps: 50
  };
  
  const headers = apiKey ? { 'x-api-key': apiKey } : {};
  
  try {
    const res = await axios.get(url, { params, headers, timeout: 10000 });
    console.log(`Success! Status: ${res.status}`);
    return true;
  } catch (e) {
    console.log(`Failed: ${e.response?.data?.message || e.message}`);
    return false;
  }
}

async function main() {
  console.log('=== Jupiter API Tester ===\n');
  
  const apiKey = await loadApiKey();
  if (!apiKey) {
    console.log('No API key found in .secrets/jupiter.key');
    return;
  }
  
  console.log(`API Key: ${apiKey.substring(0, 8)}...${apiKey.slice(-4)}\n`);
  
  for (const endpoint of CONFIG.apiEndpoints) {
    await testEndpoint(endpoint, apiKey, endpoint.replace('https://', ''));
  }
  
  console.log('\n=== Done ===');
}

main().catch(console.error);
