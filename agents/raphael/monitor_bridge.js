#!/usr/bin/env node
/**
 * Raphael's Monitor Bridge
 * Connects sub-agent trades to the live dashboard
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3456;
const STATE_FILE = './state.json';
const LOG_FILE = './trade_log.json';

// Default state
let raphaelState = {
    agent: 'raphael',
    status: 'IDLE',
    balance: 1.0,
    startingBalance: 1.0,
    targetBalance: 50.0,
    tradesToday: 0,
    totalTrades: 0,
    wins: 0,
    losses: 0,
    skips: 0,
    realizedPnl: 0,
    unrealizedPnl: 0,
    position: null,
    positions: [], // Array of all active holdings
    lastUpdate: new Date().toISOString(),
    message: 'Waiting for trades...'
};

let tradeHistory = [];
let logLines = [];

// Load state
function loadState() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            raphaelState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
        }
    } catch (e) {}
    try {
        if (fs.existsSync(LOG_FILE)) {
            tradeHistory = JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
        }
    } catch (e) {}
}

// Save state
function saveState() {
    try {
        fs.writeFileSync(STATE_FILE, JSON.stringify(raphaelState, null, 2));
        fs.writeFileSync(LOG_FILE, JSON.stringify(tradeHistory, null, 2));
    } catch (e) {}
}

// Add log
function addLog(message, type = 'info') {
    logLines.push({ message, type, time: new Date().toISOString() });
    if (logLines.length > 50) logLines.shift();
}

// Calculate progress to 50 SOL
function getProgress() {
    const current = raphaelState.balance;
    const target = raphaelState.targetBalance;
    const percent = ((current - 1) / (target - 1)) * 100;
    return {
        current,
        target,
        percent: Math.max(0, Math.min(100, percent)).toFixed(1)
    };
}

// Calculate unrealized PNL for all positions
function calculateUnrealizedPnl() {
    let totalUnrealized = 0;
    raphaelState.positions.forEach(pos => {
        if (pos.currentPrice && pos.entryPrice) {
            const pnlPercent = ((pos.currentPrice - pos.entryPrice) / pos.entryPrice) * 100;
            const pnlSol = (pos.size * pnlPercent) / 100;
            pos.unrealizedPnlPercent = pnlPercent;
            pos.unrealizedPnlSol = pnlSol;
            totalUnrealized += pnlSol;
        }
    });
    raphaelState.unrealizedPnl = totalUnrealized;
    return totalUnrealized;
}

// HTTP Server
const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Raphael reports a trade
    if (req.url === '/api/report-trade' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const trade = JSON.parse(body);
                
                // Update state
                raphaelState.totalTrades++;
                raphaelState.lastUpdate = new Date().toISOString();
                
                if (trade.type === 'ENTRY') {
                    raphaelState.tradesToday++;
                    
                    // Add to positions array
                    const newPosition = {
                        token: trade.token,
                        entryPrice: trade.entryPrice,
                        currentPrice: trade.entryPrice,
                        size: trade.size,
                        entryTime: trade.timestamp,
                        grade: trade.grade || 'B',
                        stopLoss: trade.stopLoss,
                        target: trade.target,
                        unrealizedPnlPercent: 0,
                        unrealizedPnlSol: 0
                    };
                    
                    raphaelState.positions.push(newPosition);
                    raphaelState.position = newPosition; // Keep single position for backwards compat
                    raphaelState.status = 'IN_POSITION';
                    
                    addLog(`ENTRY: ${trade.token} @ $${trade.entryPrice?.toFixed(6)} (${trade.size?.toFixed(3)} SOL)`, 'success');
                    
                } else if (trade.type === 'EXIT') {
                    // Remove from positions array
                    raphaelState.positions = raphaelState.positions.filter(p => p.token !== trade.token);
                    
                    if (raphaelState.positions.length === 0) {
                        raphaelState.position = null;
                        if (raphaelState.tradesToday >= 5) {
                            raphaelState.status = 'DAILY_LIMIT_REACHED';
                        } else {
                            raphaelState.status = 'IDLE';
                        }
                    } else {
                        raphaelState.position = raphaelState.positions[raphaelState.positions.length - 1];
                    }
                    
                    raphaelState.realizedPnl += trade.pnlSol;
                    raphaelState.balance += trade.pnlSol;
                    
                    if (trade.pnlSol > 0) {
                        raphaelState.wins++;
                        addLog(`EXIT WIN: ${trade.token} +${trade.pnlPercent?.toFixed(2)}% (+${trade.pnlSol?.toFixed(4)} SOL)`, 'success');
                    } else {
                        raphaelState.losses++;
                        addLog(`EXIT LOSS: ${trade.token} ${trade.pnlPercent?.toFixed(2)}% (${trade.pnlSol?.toFixed(4)} SOL)`, 'error');
                    }
                    
                } else if (trade.type === 'SKIP') {
                    raphaelState.skips++;
                    addLog(`SKIP: ${trade.token} - ${trade.reason}`, 'warning');
                }
                
                calculateUnrealizedPnl();
                tradeHistory.push(trade);
                saveState();
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
                
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // Raphael updates position prices (for live PNL tracking)
    if (req.url === '/api/update-prices' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const update = JSON.parse(body);
                
                if (update.prices) {
                    update.prices.forEach(priceUpdate => {
                        const pos = raphaelState.positions.find(p => p.token === priceUpdate.token);
                        if (pos) {
                            pos.currentPrice = priceUpdate.price;
                        }
                    });
                    
                    calculateUnrealizedPnl();
                    raphaelState.lastUpdate = new Date().toISOString();
                    saveState();
                    
                    addLog(`Prices updated - ${update.prices.length} positions`, 'info');
                }
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, positions: raphaelState.positions }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // Raphael reports status update
    if (req.url === '/api/update-status' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const update = JSON.parse(body);
                raphaelState = { ...raphaelState, ...update };
                
                // If positions passed, update our positions array
                if (update.positions) {
                    raphaelState.positions = update.positions;
                    calculateUnrealizedPnl();
                }
                
                raphaelState.lastUpdate = new Date().toISOString();
                saveState();
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // Get status
    if (req.url === '/api/status' && req.method === 'GET') {
        calculateUnrealizedPnl();
        const progress = getProgress();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            ...raphaelState,
            progress,
            trades: tradeHistory.slice(-20).reverse(),
            logs: logLines.slice(-10)
        }));
        return;
    }

    // Serve HTML dashboard
    if (req.url === '/' || req.url === '/index.html') {
        const html = fs.readFileSync(path.join(__dirname, 'dashboard.html'), 'utf8');
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(html);
        return;
    }

    // 404
    res.writeHead(404);
    res.end('Not found');
});

loadState();

server.listen(PORT, () => {
    console.log('\n╔═══════════════════════════════════════════════════╗');
    console.log('║     🦎 RAPHAEL - Monitor Bridge Active         ║');
    console.log('╠═══════════════════════════════════════════════════╣');
    console.log(`║  Status: ${raphaelState.status.padEnd(30)}      ║`);
    console.log(`║  Balance: ${raphaelState.balance.toFixed(4)} SOL → ${raphaelState.targetBalance} SOL  ║`);
    console.log(`║  Positions: ${raphaelState.positions?.length || 0} active              ║`);
    console.log(`║  Progress: ${getProgress().percent}%                      ║`);
    console.log(`║  URL: http://localhost:${PORT}                ║`);
    console.log('╚═══════════════════════════════════════════════════╝\n');
});
