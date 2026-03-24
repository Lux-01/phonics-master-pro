const axios = require('axios');
const fs = require('fs');

const CONFIG = {
  entryThreshold: 5.0,
  scaleTarget: 20.0,
  trailStop: 10.0,
  checkInterval: 30
};

let state = {
  openPrice: null,
  currentPrice: null,
  peakPrice: null,
  entryPrice: null,
  scaled: false
};

function saveState() {
  fs.writeFileSync('./monitor_state.json', JSON.stringify(state, null, 2));
}

function loadState() {
  try {
    if (fs.existsSync('./monitor_state.json')) {
      state = JSON.parse(fs.readFileSync('./monitor_state.json'));
    }
  } catch (e) {}
}

async function getPrice(tokenMint) {
  try {
    const res = await axios.get(
      `https://api.dexscreener.com/latest/dex/tokens/${tokenMint}`,
      { timeout: 10000 }
    );
    if (res.data?.pairs?.[0]) {
      return parseFloat(res.data.pairs[0].priceUsd);
    }
  } catch (e) {
    console.error('Price error:', e.message);
  }
  return null;
}

function alert(type, msg, data = {}) {
  const time = new Date().toLocaleTimeString();
  const emojis = { ENTRY: '🟢', SCALE: '📊', TRAIL: '🔴', INFO: 'ℹ️' };
  
  console.log(`\n${emojis[type] || 'ℹ️'} [${time}] ${type}`);
  console.log(`   ${msg}`);
  if (data.price) console.log(`   Price: $${data.price}`);
  if (data.pnl) console.log(`   P&L: ${data.pnl}%`);
  
  saveState();
}

async function monitor(tokenMint, symbol) {
  console.log(`\n🔍 Monitoring ${symbol} (${tokenMint})`);
  console.log(`   Interval: ${CONFIG.checkInterval}s`);
  console.log('   Press Ctrl+C to stop\n');
  
  loadState();
  
  const initial = await getPrice(tokenMint);
  if (!initial) {
    console.error('❌ Could not get initial price');
    return;
  }
  
  state.openPrice = initial;
  state.currentPrice = initial;
  state.peakPrice = initial;
  saveState();
  
  alert('INFO', `Session started for ${symbol}`, { price: initial });
  
  let checks = 0;
  const interval = setInterval(async () => {
    checks++;
    const price = await getPrice(tokenMint);
    if (!price) return;
    
    state.currentPrice = price;
    if (price > state.peakPrice) state.peakPrice = price;
    
    const fromOpen = ((price - state.openPrice) / state.openPrice) * 100;
    const fromPeak = ((price - state.peakPrice) / state.peakPrice) * 100;
    
    // Entry alert
    if (!state.entryPrice && fromOpen >= CONFIG.entryThreshold) {
      alert('ENTRY', `${symbol} broke out +${fromOpen.toFixed(2)}%! BUY NOW!`, {
        price: price,
        change: fromOpen,
        rec: 'BUY 0.5 SOL on Axiom.trade'
      });
      state.entryPrice = price;
      saveState();
    }
    
    // Scale alert
    if (state.entryPrice && !state.scaled) {
      const pnl = ((price - state.entryPrice) / state.entryPrice) * 100;
      if (pnl >= CONFIG.scaleTarget) {
        alert('SCALE', `${symbol} hit +20%! SCALE NOW!`, {
          price: price,
          pnl: pnl,
          rec: 'SELL 50% on Axiom.trade'
        });
        state.scaled = true;
        saveState();
      }
    }
    
    // Trail alert
    if (state.scaled && fromPeak <= -CONFIG.trailStop) {
      const pnl = ((price - state.entryPrice) / state.entryPrice) * 100;
      alert('TRAIL', `${symbol} hit trailing stop!`, {
        price: price,
        pnl: pnl,
        peak: state.peakPrice,
        rec: 'SELL ALL on Axiom.trade'
      });
      state.entryPrice = null;
      state.scaled = false;
      saveState();
    }
    
    // Status every 5 checks (2.5 min)
    if (checks % 5 === 0) {
      console.log(`\n⏰ ${new Date().toLocaleTimeString()} - ${symbol}`);
      console.log(`   Price: $${price.toFixed(6)} | From Open: ${fromOpen.toFixed(2)}%`);
      if (state.entryPrice) {
        const pnl = ((price - state.entryPrice) / state.entryPrice) * 100;
        console.log(`   Entry: $${state.entryPrice.toFixed(6)} | P&L: ${pnl.toFixed(2)}%`);
      }
    }
    
    saveState();
  }, CONFIG.checkInterval * 1000);
  
  process.on('SIGINT', () => {
    console.log('\n\n👋 Stopping monitor...');
    clearInterval(interval);
    saveState();
    process.exit(0);
  });
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const params = args.slice(1);
  
  if (cmd === 'monitor' && params.length >= 1) {
    await monitor(params[0], params[1] || 'TOKEN');
  } else {
    console.log('Usage: node price_monitor.js monitor <token_mint> [symbol]');
    console.log('Example: node price_monitor.js monitor DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 BONK');
  }
}

main().catch(console.error);
