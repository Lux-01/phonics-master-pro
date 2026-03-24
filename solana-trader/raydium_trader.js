// birdeye_trader.js - Birdeye API + Manual Trading Assistant
const { Connection, Keypair, PublicKey } = require('@solana/web3.js');
const axios = require('axios');
const fs = require('fs');
const bs58 = require('bs58');
require('dotenv').config();

// APIs
const BIRDEYE_API = 'https://public-api.birdeye.so';
const BIRDEYE_API_KEY = process.env.BIRDEYE_API_KEY;
const SOL_MINT = 'So11111111111111111111111111111111111111112';

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

class BirdeyeTrader {
  constructor(walletKeypair, connectionUrl = 'https://api.mainnet-beta.solana.com') {
    this.wallet = walletKeypair;
    this.connection = new Connection(connectionUrl, 'confirmed');
    this.priceCache = new Map();
  }
  
  async getBalance() {
    const balance = await this.connection.getBalance(this.wallet.publicKey);
    return balance / 1e9;
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
  
  async getPrice(tokenMint) {
    // Check cache
    if (this.priceCache.has(tokenMint)) {
      const cached = this.priceCache.get(tokenMint);
      if (Date.now() - cached.time < 30000) {
        return cached.price;
      }
    }
    
    try {
      // Try Birdeye API first
      if (BIRDEYE_API_KEY) {
        const response = await axios.get(
          `${BIRDEYE_API}/defi/price?address=${tokenMint}`,
          {
            headers: { 'X-API-KEY': BIRDEYE_API_KEY },
            timeout: 10000
          }
        );
        
        if (response.data?.data?.value) {
          const price = {
            price: response.data.data.value,
            source: 'birdeye'
          };
          this.priceCache.set(tokenMint, { price, time: Date.now() });
          return price;
        }
      }
    } catch (e) {
      console.log('Birdeye failed, trying fallback...');
    }
    
    // Fallback to DexScreener
    try {
      const res = await axios.get(
        `https://api.dexscreener.com/latest/dex/tokens/${tokenMint}`,
        { timeout: 10000 }
      );
      
      if (res.data?.pairs?.[0]) {
        const price = {
          price: parseFloat(res.data.pairs[0].priceUsd),
          source: 'dexscreener'
        };
        this.priceCache.set(tokenMint, { price, time: Date.now() });
        return price;
      }
    } catch (e) {
      console.error('❌ All price APIs failed');
    }
    
    return null;
  }
  
  async buy(tokenMint, solAmount) {
    console.log(`\n🟢 BUY: ${solAmount} SOL → Token`);
    console.log(`   Token: ${tokenMint}`);
    
    const price = await this.getPrice(tokenMint);
    if (!price) {
      console.log('❌ Could not get price');
      return null;
    }
    
    const solPrice = await this.getPrice(SOL_MINT);
    const solUsdValue = solAmount * (solPrice?.price || 85);
    const tokenAmount = solUsdValue / price.price;
    
    console.log(`   Token Price: $${price.price.toFixed(8)} (${price.source})`);
    console.log(`   SOL Price: $${(solPrice?.price || 85).toFixed(2)}`);
    console.log(`   You pay: ${solAmount} SOL (~$${solUsdValue.toFixed(2)})`);
    console.log(`   You receive: ~${tokenAmount.toFixed(2)} tokens`);
    console.log('   ⚠️  Manual execution: Use Axiom.trade or Phantom');
    
    return {
      price: price.price,
      solAmount,
      tokenAmount,
      token: tokenMint
    };
  }
  
  async sell(tokenMint, percentage = 100) {
    console.log(`\n🔴 SELL: ${percentage}% of token`);
    console.log(`   Token: ${tokenMint}`);
    
    const balance = await this.getTokenBalance(tokenMint);
    if (balance <= 0) {
      console.log('❌ No token balance');
      return null;
    }
    
    const price = await this.getPrice(tokenMint);
    const sellAmount = balance * (percentage / 100);
    const solPrice = await this.getPrice(SOL_MINT);
    const solValue = (sellAmount * price.price) / (solPrice?.price || 85);
    
    console.log(`   Balance: ${balance.toFixed(2)} tokens`);
    console.log(`   Selling: ${sellAmount.toFixed(2)} tokens (${percentage}%)`);
    console.log(`   Token price: $${price?.price?.toFixed(8) || 'N/A'}`);
    console.log(`   Estimated SOL: ~${solValue.toFixed(4)} SOL`);
    console.log('   ⚠️  Manual execution: Use Axiom.trade or Phantom');
    
    return { balance, sellAmount, solValue };
  }
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const params = args.slice(1);
  
  if (cmd === 'price' && params[0]) {
    const trader = new RaydiumTrader({ publicKey: { toString: () => 'dummy' } });
    const price = await trader.getPrice(params[0]);
    if (price) {
      console.log(`Price: $${price.price} (${price.source})`);
    } else {
      console.log('❌ Could not fetch price');
    }
  } else if (cmd === 'balance') {
    const config = JSON.parse(fs.readFileSync('./config.json'));
    const wallet = new SecureWallet(config.wallet.keyPath);
    const trader = new RaydiumTrader(wallet.getKeypair());
    const bal = await trader.getBalance();
    console.log(`💰 Wallet Balance: ${bal.toFixed(4)} SOL`);
    console.log(`📍 Public Key: ${wallet.getPublicKey().toString()}`);
  } else if (cmd === 'buy' && params.length >= 2) {
    const config = JSON.parse(fs.readFileSync('./config.json'));
    const wallet = new SecureWallet(config.wallet.keyPath);
    const trader = new RaydiumTrader(wallet.getKeypair());
    await trader.buy(params[0], parseFloat(params[1]));
  } else if (cmd === 'sell' && params.length >= 1) {
    const config = JSON.parse(fs.readFileSync('./config.json'));
    const wallet = new SecureWallet(config.wallet.keyPath);
    const trader = new RaydiumTrader(wallet.getKeypair());
    await trader.sell(params[0], parseInt(params[1]) || 100);
  } else {
    console.log('Raydium Trader - Price & Trading Assistant');
    console.log('');
    console.log('Commands:');
    console.log('  price <mint>                    - Check token price');
    console.log('  balance                          - Check wallet balance');
    console.log('  buy <mint> <amount>             - Simulate buy');
    console.log('  sell <mint> [percentage]         - Simulate sell');
    console.log('');
    console.log('Examples:');
    console.log('  node raydium_trader.js price DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263');
    console.log('  node raydium_trader.js balance');
    console.log('  node raydium_trader.js buy DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 0.001');
  }
}

main().catch(console.error);
