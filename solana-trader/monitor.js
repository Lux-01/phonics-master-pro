const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ANSI colors
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  gray: '\x1b[90m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function color(text, colorName) {
  return `${colors[colorName]}${text}${colors.reset}`;
}

function clearScreen() {
  console.clear();
}

class BotMonitor {
  constructor() {
    this.logFile = './trading_logs/swing_bot_20260222.log';
    this.lastPosition = null;
    this.trades = [];
    this.botStatus = 'Unknown';
    this.lastScan = null;
  }

  checkBotRunning() {
    try {
      const output = execSync('ps aux | grep "swing_bot.js" | grep -v grep', { encoding: 'utf8' });
      const lines = output.trim().split('\n').filter(line => line.includes('node'));
      
      if (lines.length > 0) {
        const pid = lines[0].trim().split(/\s+/)[1];
        const cpu = lines[0].trim().split(/\s+/)[2];
        const mem = lines[0].trim().split(/\s+/)[3];
        this.botStatus = {
          running: true,
          pid: pid,
          cpu: cpu,
          memory: mem,
          uptime: this.calculateUptime(lines[0])
        };
      } else {
        this.botStatus = { running: false, pid: null, cpu: 0, memory: 0 };
      }
    } catch (e) {
      this.botStatus = { running: false, pid: null, cpu: 0, memory: 0 };
    }
  }

  calculateUptime(psLine) {
    try {
      const timeField = psLine.trim().split(/\s+/)[9];
      return timeField || 'Unknown';
    } catch {
      return 'Unknown';
    }
  }

  parseLogFile() {
    try {
      if (!fs.existsSync(this.logFile)) {
        return { trades: [], position: null, lastScan: null };
      }

      const content = fs.readFileSync(this.logFile, 'utf8');
      const lines = content.split('\n');
      
      const trades = [];
      let currentPosition = null;
      let lastScan = null;
      
      for (const line of lines) {
        // Parse BUY signals
        if (line.includes('🟢 BUY SIGNAL:')) {
          const tokenMatch = line.match(/BUY SIGNAL:\s+(\w+)/);
          if (tokenMatch) {
            currentPosition = {
              token: tokenMatch[1],
              action: 'BUY',
              timestamp: new Date().toISOString()
            };
          }
        }
        
        // Parse buy complete
        if (line.includes('✅ Buy') && line.includes('complete')) {
          const tokenMatch = line.match(/Buy\s+(\w+)/);
          const txMatch = line.match(/TX:\s+(https:\/\/[^\s]+)/);
          
          if (tokenMatch && currentPosition) {
            currentPosition.token = tokenMatch[1];
            if (txMatch) currentPosition.txUrl = txMatch[1];
            currentPosition.status = 'OPEN';
          }
        }
        
        // Parse amount info
        if (line.includes('Amount:') && line.includes('SOL')) {
          const amountMatch = line.match(/Amount:\s+([\d.]+)\s+SOL/);
          if (amountMatch && currentPosition) {
            currentPosition.solAmount = parseFloat(amountMatch[1]);
          }
        }
        
        // Parse expected tokens
        if (line.includes('Expected:') && line.includes('~')) {
          const tokensMatch = line.match(/Expected:\s+~([\d.]+)\s+(\w+)/);
          if (tokensMatch && currentPosition) {
            currentPosition.tokensExpected = parseFloat(tokensMatch[1]);
          }
        }
        
        // Parse scanning
        if (line.includes('🔍 Scanning')) {
          lastScan = new Date().toISOString();
        }
        
        // Parse current prices from scans
        if (line.includes('Price:') && line.includes('$')) {
          const priceMatch = line.match(/Price:\s+\$([\d.]+)/);
          const changeMatch = line.match(/Change.*?([+-]?[\d.]+)%/);
          
          // Store for later
          if (priceMatch && currentPosition) {
            currentPosition.lastPrice = priceMatch[1];
          }
        }
      }
      
      // Also try to find position info from the last BUY
      const buyMatches = content.matchAll(/🟢 BUY SIGNAL:\s+(\w+)/g);
      const buyTokens = Array.from(buyMatches);
      
      if (buyTokens.length > 0) {
        const lastToken = buyTokens[buyTokens.length - 1][1];
        
        // Find the buy details
        const buySection = content.substring(content.lastIndexOf('🟢 BUY SIGNAL:'));
        const amountMatch = buySection.match(/Amount:\s+([\d.]+)\s+SOL/);
        const expectedMatch = buySection.match(/Expected:\s+~([\d.]+)/);
        const txMatch = buySection.match(/TX:\s+(https:\/\/solscan\.io\/tx\/[^\s]+)/);
        
        currentPosition = {
          token: lastToken,
          status: 'OPEN',
          solAmount: amountMatch ? parseFloat(amountMatch[1]) : 0.5,
          tokensExpected: expectedMatch ? parseFloat(expectedMatch[1]) : 0,
          txUrl: txMatch ? txMatch[1] : null,
          entryTime: fs.statSync(this.logFile).mtime.toISOString()
        };
      }
      
      return { trades, position: currentPosition, lastScan };
    } catch (e) {
      console.error('Error parsing log:', e.message);
      return { trades: [], position: null, lastScan: null };
    }
  }

  async fetchCurrentPrice(token) {
    try {
      const axios = require('axios');
      const tokenMap = {
        'PUMP1': 'NV2RYH954cTJ3ckFUpvfqaQXU4ARqqDH3562nFSpump',
        'PUMP2': 'AVF9F4C4j8b1Kh4BmNHqybDaHgnZpJ7W7yLvL7hUpump',
        'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
        'WIF': 'EKpQGSJtjGFqKckxLSpxUtMJufH1R9kB2YrJ1ZC86yX',
        'MEW': 'MEW1gQWJ3nUXGzz7kZJkeMo7FLMGLmM6jAp1M5MiZjy'
      };
      
      const mint = tokenMap[token];
      if (!mint) return null;
      
      const res = await axios.get(
        `https://api.dexscreener.com/latest/dex/tokens/${mint}`,
        { timeout: 5000 }
      );
      
      if (res.data?.pairs?.[0]) {
        const pair = res.data.pairs[0];
        return {
          price: parseFloat(pair.priceUsd),
          change24h: parseFloat(pair.priceChange?.h24 || 0),
          change6h: parseFloat(pair.priceChange?.h6 || 0),
          marketCap: parseFloat(pair.marketCap || 0),
          volume24h: parseFloat(pair.volume24h || 0),
          liquidity: parseFloat(pair.liquidity?.usd || 0)
        };
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  async display() {
    clearScreen();
    
    // Check bot status
    this.checkBotRunning();
    
    // Parse log
    const { position, lastScan } = this.parseLogFile();
    
    // Header
    console.log(color('╔════════════════════════════════════════════════════════════════╗', 'cyan'));
    console.log(color('║           🤖 SWING TRADER v2.2 - LIVE MONITOR                  ║', 'bold'));
    console.log(color('╚════════════════════════════════════════════════════════════════╝', 'cyan'));
    console.log();
    
    // Sydney time
    const sydneyTime = new Date().toLocaleString('en-AU', { 
      timeZone: 'Australia/Sydney',
      hour12: false 
    });
    console.log(`📅 Sydney Time: ${color(sydneyTime, 'cyan')}`);
    console.log(`⏰ Trading Window: 00:00 - 04:00 (Session Active)`);
    console.log();
    
    // Bot Status
    console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
    console.log(color('                     BOT STATUS', 'bold'));
    console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
    
    if (this.botStatus.running) {
      console.log(`${color('🟢', 'green')} Status: ${color('RUNNING', 'green')}`);
      console.log(`   PID: ${this.botStatus.pid}`);
      console.log(`   CPU: ${this.botStatus.cpu}%`);
      console.log(`   Memory: ${this.botStatus.memory}%`);
      console.log(`   Uptime: ${this.botStatus.uptime || 'Recently started'}`);
    } else {
      console.log(`${color('🔴', 'red')} Status: ${color('STOPPED', 'red')}`);
      console.log(`   ⚠️  Bot is not running!`);
    }
    console.log();
    
    // Position Status
    console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
    console.log(color('                   POSITION STATUS', 'bold'));
    console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
    
    if (position && position.token) {
      console.log(`${color('💎', 'cyan')} Token: ${color(position.token, 'bold')}`);
      console.log(`   Entry: ${position.solAmount} SOL`);
      console.log(`   Expected Tokens: ~${position.tokensExpected || 'N/A'}`);
      console.log(`   Status: ${color('OPEN', 'green')}`);
      
      if (position.txUrl) {
        console.log(`   TX: ${color(position.txUrl, 'gray')}`);
      }
      
      // Get current price
      const priceData = await this.fetchCurrentPrice(position.token);
      
      if (priceData) {
        console.log();
        console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
        console.log(color('                    P&L CALCULATION', 'bold'));
        console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
        
        // Calculate P&L (estimated entry at $0.02903)
        const entryPrice = 0.02903; // From log
        const currentPrice = priceData.price;
        const pnl = ((currentPrice - entryPrice) / entryPrice) * 100;
        const tokens = position.tokensExpected || 1468;
        const currentValue = tokens * currentPrice;
        const investedUsd = position.solAmount * 85; // Assuming SOL at $85
        
        console.log(`💰 Current Price: $${currentPrice.toFixed(8)}`);
        console.log(`📊 Entry Price: $${entryPrice.toFixed(5)}`);
        console.log(`📈 6h Change: ${priceData.change6h > 0 ? '+' : ''}${priceData.change6h.toFixed(2)}%`);
        console.log(`📈 24h Change: ${priceData.change24h > 0 ? '+' : ''}${priceData.change24h.toFixed(2)}%`);
        console.log();
        
        const pnlColor = pnl >= 0 ? 'green' : 'red';
        const pnlEmoji = pnl >= 0 ? '🟢' : '🔴';
        
        console.log(`${pnlEmoji} P&L: ${color(pnl >= 0 ? '+' : '', pnlColor)}${pnl.toFixed(2)}%`);
        console.log(`   Invested: ~$${investedUsd.toFixed(2)} USD`);
        console.log(`   Current Value: ~$${currentValue.toFixed(2)} USD`);
        console.log(`   Unrealized: ${color((currentValue - investedUsd) >= 0 ? '+' : '', pnlColor)}$${(currentValue - investedUsd).toFixed(2)}`);
        
        console.log();
        console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
        console.log(color('                 🎯 BOT THINKING / TRADE PLAN', 'bold'));
        console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
        
        // Calculate trigger prices
        const scalePrice = entryPrice * 1.20; // +20%
        const hardStopPrice = entryPrice * 0.93; // -7%
        const peakPrice = currentPrice > entryPrice ? currentPrice : entryPrice;
        const trailPrice = peakPrice * 0.90; // -10% from peak
        
        console.log(`🎯 Scale Target (+20%): $${scalePrice.toFixed(8)}`);
        console.log(`   Action: Sell 50% of position`);
        console.log(`   Current progress: ${((currentPrice / scalePrice) * 100).toFixed(1)}%`);
        console.log();
        
        console.log(`📉 Hard Stop (-7%): $${hardStopPrice.toFixed(8)}`);
        console.log(`   Action: Emergency exit - sell all`);
        console.log(`   Distance: ${((currentPrice / hardStopPrice - 1) * 100).toFixed(1)}% away`);
        console.log();
        
        console.log(`🔴 Trailing Stop (-10% from peak): $${trailPrice.toFixed(8)}`);
        console.log(`   Peak so far: $${peakPrice.toFixed(8)}`);
        console.log(`   Action: Exit if price drops below trail`);
        console.log(`   Status: ${currentPrice > trailPrice ? color('ACTIVE - Holding ✓', 'green') : color('TRIGGERED - Exit!', 'red')}`);
        
        console.log();
        console.log(`⏰ Session End (04:00): Auto-close all positions`);
        console.log(`   Status: Monitoring until end of window`);
      } else {
        console.log();
        console.log(`${color('⚠️', 'yellow')} Could not fetch price data (rate limited)`);
        console.log(`   Estimated entry: $0.02903`);
        console.log(`   Check: ${color('solscan.io', 'gray')} for live price`);
      }
    } else {
      console.log(`${color('📭', 'gray')} No open position`);
      console.log(`   Status: ${color('WAITING FOR SIGNAL', 'yellow')}`);
      console.log();
      console.log(`   The bot is scanning for:`);
      console.log(`   • >5% price breakout`);
      console.log(`   • $10M-$100M market cap`);
      console.log(`   • Score 6+/8`);
    }
    
    console.log();
    console.log(color('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'gray'));
    console.log(`   Last log update: ${color(lastScan || fs.statSync(this.logFile).mtime.toLocaleString(), 'gray')}`);
    console.log(`   Refresh every 5 seconds`);
    console.log();
    console.log(color('Commands:', 'bold'));
    console.log(`   q = quit | Ctrl+C = exit`);
    console.log();
  }
  
  async run() {
    console.log('Starting monitor... Press Ctrl+C to exit');
    console.log();
    
    await this.display();
    
    setInterval(async () => {
      await this.display();
    }, 5000);
  }
}

// Run
const monitor = new BotMonitor();

// Handle exit
process.on('SIGINT', () => {
  console.log('\n\n👋 Monitor stopped');
  process.exit(0);
});

monitor.run().catch(console.error);
