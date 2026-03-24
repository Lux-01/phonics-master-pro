const http = require('http');
const fs = require('fs');
const { exec, spawn } = require('child_process');
const path = require('path');

const PORT = 8080;
const BOT_SCRIPT = './swing_bot_v2.3.js';
const POSITION_FILE = './trading_logs/current_position.json';
const SESSION_FILE = './trading_logs/session_stats.json';
const BLACKLIST_FILE = './trading_logs/blacklist.json';

let botProcess = null;

// Check if bot is running
function isBotRunning() {
  try {
    const result = require('child_process').execSync('ps aux | grep "swing_bot_v2.3.js" | grep -v grep');
    return result.toString().includes('node');
  } catch (e) {
    return false;
  }
}

// Start bot
function startBot() {
  if (botProcess) return;
  
  console.log('[Monitor] Starting bot...');
  botProcess = spawn('node', [BOT_SCRIPT], {
    detached: true,
    stdio: ['ignore', 'pipe', 'pipe']
  });
  
  botProcess.stdout.on('data', (data) => {
    console.log('[Bot stdout]:', data.toString());
  });
  
  botProcess.stderr.on('data', (data) => {
    console.error('[Bot stderr]:', data.toString());
  });
  
  botProcess.on('error', (err) => {
    console.error('[Monitor] Failed to start bot:', err);
  });
  
  botProcess.unref();
}

// Stop bot
function stopBot() {
  console.log('[Monitor] Stopping bot...');
  try {
    exec('pkill -f "swing_bot_v2.3.js"');
  } catch (e) {}
  botProcess = null;
}

// Read current position
function getPosition() {
  try {
    if (fs.existsSync(POSITION_FILE)) {
      return JSON.parse(fs.readFileSync(POSITION_FILE, 'utf8'));
    }
  } catch (e) {}
  return null;
}

// Read session stats
function getSessionStats() {
  try {
    if (fs.existsSync(SESSION_FILE)) {
      return JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
    }
  } catch (e) {}
  return {
    consecutiveLosses: 0,
    totalLosses: 0,
    totalWins: 0,
    lossCooldownEnd: null,
    trades: []
  };
}

// Read blacklist
function getBlacklist() {
  try {
    if (fs.existsSync(BLACKLIST_FILE)) {
      const blacklist = JSON.parse(fs.readFileSync(BLACKLIST_FILE, 'utf8'));
      // Calculate remaining time for each
      const now = Date.now();
      const result = {};
      for (const [token, exitTime] of Object.entries(blacklist)) {
        const remaining = Math.max(0, 30 * 60 * 1000 - (now - exitTime));
        if (remaining > 0) {
          result[token] = Math.ceil(remaining / 60000); // minutes remaining
        }
      }
      return result;
    }
  } catch (e) {}
  return {};
}

// Create HTTP server
const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // API endpoints
  if (req.url === '/api/bot-status' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ running: isBotRunning() }));
    return;
  }
  
  if (req.url === '/api/start-bot' && req.method === 'POST') {
    startBot();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, message: 'Bot started' }));
    return;
  }
  
  if (req.url === '/api/stop-bot' && req.method === 'POST') {
    stopBot();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, message: 'Bot stopped' }));
    return;
  }
  
  if (req.url === '/api/position' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(getPosition()));
    return;
  }
  
  // 🔥 NEW: Session stats endpoint
  if (req.url === '/api/session-stats' && req.method === 'GET') {
    const stats = getSessionStats();
    const now = Date.now();
    let cooldownActive = false;
    let cooldownRemaining = 0;
    
    if (stats.lossCooldownEnd) {
      const remaining = stats.lossCooldownEnd - now;
      if (remaining > 0) {
        cooldownActive = true;
        cooldownRemaining = Math.ceil(remaining / 60000);
      }
    }
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      ...stats,
      cooldownActive,
      cooldownRemaining
    }));
    return;
  }
  
  // 🔥 NEW: Blacklist endpoint
  if (req.url === '/api/blacklist' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(getBlacklist()));
    return;
  }
  
  if (req.url === '/api/sell-partial' && req.method === 'POST') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: false, message: 'Manual scale not implemented' }));
    return;
  }
  
  if (req.url === '/api/sell-all' && req.method === 'POST') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: false, message: 'Manual sell not implemented' }));
    return;
  }
  
  // Serve HTML file
  if (req.url === '/' || req.url === '/index.html') {
    const htmlPath = path.join(__dirname, 'monitor_gui.html');
    fs.readFile(htmlPath, (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Error loading monitor');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
    return;
  }
  
  // 404
  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`\n╔═══════════════════════════════════════════════════════╗`);
  console.log(`║     🤖 Swing Trader Monitor Server v2.3              ║`);
  console.log(`╠═══════════════════════════════════════════════════════╣`);
  console.log(`║  Status: ${isBotRunning() ? '🟢 RUNNING' : '🔴 STOPPED'}                          ║`);
  console.log(`║  URL: http://localhost:${PORT}                      ║`);
  console.log(`╚═══════════════════════════════════════════════════════╝\n`);
  console.log(`Open your browser and navigate to: http://localhost:${PORT}`);
  console.log(`\nPress Ctrl+C to stop the server\n`);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down monitor server...');
  server.close();
  process.exit(0);
});
