#!/usr/bin/env node
/**
 * The Adaptive Edge - Monitor Server
 * Web interface for controlling the live trading bot
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn, exec } = require('child_process');

const PORT = 3456;
const TRADER_SCRIPT = './adaptive_edge_trader.js';
const STATE_FILE = './trading_logs/adaptive_edge_state.json';

let traderProcess = null;

// Check if trader is running
function isTraderRunning() {
    try {
        const result = require('child_process').execSync(`ps aux | grep "${TRADER_SCRIPT}" | grep -v grep`);
        return result.toString().includes('node');
    } catch (e) {
        return false;
    }
}

// Get current status
function getStatus() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
            return {
                running: state.running,
                dailyStats: state.dailyStats,
                position: state.currentPosition,
                trades: state.tradeHistory || []
            };
        }
    } catch (e) {
        console.error('Error reading status:', e.message);
    }
    return {
        running: false,
        dailyStats: {
            tradesTaken: 0,
            tradesSkipped: 0,
            realizedPnl: 0,
            currentBalance: 0
        },
        position: null,
        trades: []
    };
}

// Start trader
function startTrader() {
    if (traderProcess || isTraderRunning()) {
        return { success: false, message: 'Trader already running' };
    }

    console.log('[Monitor] Starting Adaptive Edge trader...');
    
    traderProcess = spawn('node', [TRADER_SCRIPT, 'start'], {
        detached: true,
        stdio: ['ignore', fs.openSync('./trading_logs/trader.log', 'a'), fs.openSync('./trading_logs/trader.log', 'a')]
    });

    traderProcess.unref();
    
    return { success: true, message: 'Trader started' };
}

// Stop trader
function stopTrader() {
    console.log('[Monitor] Stopping trader...');
    
    try {
        // Try graceful shutdown first
        if (traderProcess) {
            traderProcess.kill('SIGTERM');
        }
        
        // Force kill any remaining processes
        exec(`pkill -f "${TRADER_SCRIPT}"`);
        
        traderProcess = null;
        return { success: true, message: 'Trader stopped' };
    } catch (e) {
        return { success: false, message: e.message };
    }
}

// HTTP Server
const server = http.createServer((req, res) => {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // API: Status
    if (req.url === '/api/bot-status' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ running: isTraderRunning() }));
        return;
    }

    // API: Session Stats
    if (req.url === '/api/session-stats' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(getStatus()));
        return;
    }

    // API: Start
    if (req.url === '/api/start-bot' && req.method === 'POST') {
        const result = startTrader();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
        return;
    }

    // API: Stop
    if (req.url === '/api/stop-bot' && req.method === 'POST') {
        const result = stopTrader();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
        return;
    }

    // Serve HTML
    if (req.url === '/' || req.url === '/index.html') {
        const htmlPath = path.join(__dirname, 'adaptive_edge_monitor.html');
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
    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║              🦞 The Adaptive Edge Monitor              ║');
    console.log('╠═══════════════════════════════════════════════════════════╣');
    console.log(`║  Trading Bot: ${isTraderRunning() ? '🟢 RUNNING' : '🔴 STOPPED'}                              ║`);
    console.log(`║  Monitor:     🟢 RUNNING                                  ║`);
    console.log(`║  URL:         http://localhost:${PORT}                    ║`);
    console.log('╠═══════════════════════════════════════════════════════════╣');
    console.log('║  Trading Rules:                                           ║');
    console.log('║    • Max Risk: 10% of capital                            ║');
    console.log('║    • Trade Size: 0.15-0.25 SOL                           ║');
    console.log('║    • Max Trades: 5 per day                               ║');
    console.log('║    • Daily Loss Limit: -5%                               ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');
    console.log(`Open browser: http://localhost:${PORT}`);
    console.log('\nCommands:');
    console.log('  Start:  Click [START] button on webpage');
    console.log('  Stop:   Click [STOP] button on webpage');
    console.log('\nPress Ctrl+C to stop the monitor\n');
});

process.on('SIGINT', () => {
    console.log('\n👋 Shutting down monitor...');
    server.close();
    process.exit(0);
});
