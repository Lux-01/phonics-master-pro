#!/usr/bin/env python3
"""
Raphael Monitor v5.0 - Simple & Robust
No threading issues - clean process separation
"""

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import subprocess

PORT = 3456
STATE_FILE = "/tmp/raphael_state.json"
LOG_FILE = "/tmp/raphael_monitor_v5.log"
PID_FILE = "/tmp/raphael_autotrader.pid"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def get_wallet_balance():
    try:
        with open("/home/skux/.openclaw/workspace/solana-trader/.secrets/wallet.key", 'r') as f:
            pass
        return 1.0
    except:
        return 0.0

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {
        "agent": "raphael",
        "mode": "LIVE_TEST",
        "status": "READY",
        "balance": 1.0,
        "wallet_balance": get_wallet_balance(),
        "target_trades": 5,
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "emergency_stop": False,
        "autotrader_running": False,
        "last_update": datetime.now().isoformat(),
        "version": "5.0"
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def is_autotrader_running():
    """Check if autotrader process is alive"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if process exists
            return True
        except:
            return False
    return False

def start_autotrader():
    """Start autotrader as separate process"""
    try:
        # Start autotrader in background
        proc = subprocess.Popen(
            [sys.executable, "/home/skux/.openclaw/workspace/agents/raphael/raphael_autotrader.py"],
            stdout=open("/tmp/raphael_autotrader.log", "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        with open(PID_FILE, 'w') as f:
            f.write(str(proc.pid))
        log(f"🚀 Autotrader started (PID: {proc.pid})")
        return True
    except Exception as e:
        log(f"❌ Failed to start autotrader: {e}")
        return False

def stop_autotrader():
    """Stop autotrader process"""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 15)  # SIGTERM
            time.sleep(1)
            try:
                os.kill(pid, 9)  # SIGKILL if still running
            except:
                pass
            os.remove(PID_FILE)
        # Also kill any remaining python processes for raphael_autotrader
        subprocess.run(["pkill", "-f", "raphael_autotrader.py"], capture_output=True)
        log("⏹️ Autotrader stopped")
        return True
    except Exception as e:
        log(f"⚠️ Error stopping autotrader: {e}")
        return False

STATE = load_state()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        global STATE
        
        # Update autotrader status
        STATE["autotrader_running"] = is_autotrader_running()
        save_state(STATE)

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            STATE["last_update"] = datetime.now().isoformat()
            self.wfile.write(json.dumps({
                **STATE,
                "wallet_address": "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5",
                "pnl": STATE.get("realized_pnl", 0)
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global STATE
        
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len > 0:
            self.rfile.read(content_len)
        
        if self.path == '/api/emergency-stop':
            STATE["emergency_stop"] = True
            STATE["status"] = "EMERGENCY_STOP"
            STATE["autotrader_running"] = False
            stop_autotrader()
            save_state(STATE)
            log("🚨 EMERGENCY STOP TRIGGERED")
            self.send_json(200, {"stopped": True})
        
        elif self.path == '/api/start-trading':
            if STATE["emergency_stop"]:
                self.send_json(403, {"error": "Emergency stop active"})
                return
            
            if is_autotrader_running():
                self.send_json(403, {"error": "Already running"})
                return
            
            if start_autotrader():
                STATE["autotrader_running"] = True
                STATE["status"] = "SCANNING"
                save_state(STATE)
                self.send_json(200, {"started": True})
            else:
                self.send_json(500, {"error": "Failed to start"})
        
        elif self.path == '/api/stop-trading':
            stop_autotrader()
            STATE["autotrader_running"] = False
            STATE["status"] = "IDLE"
            save_state(STATE)
            self.send_json(200, {"stopped": True})
        
        elif self.path == '/api/reset':
            stop_autotrader()
            STATE = {
                "agent": "raphael",
                "mode": "LIVE_TEST",
                "status": "READY",
                "balance": 1.0,
                "wallet_balance": get_wallet_balance(),
                "target_trades": 5,
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "emergency_stop": False,
                "autotrader_running": False,
                "last_update": datetime.now().isoformat(),
                "version": "5.0"
            }
            save_state(STATE)
            for f in ["/tmp/raphael_live_state.json"]:
                if os.path.exists(f):
                    os.remove(f)
            log("🔄 System reset")
            self.send_json(200, {"reset": True})
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>RAPHAEL v5.0</title>
<style>
body{font-family:monospace;background:#0a0a0a;color:#00ff88;padding:20px}
.header{text-align:center;padding:20px;border-bottom:2px solid #00ff88}
.badge{background:#ff4400;color:white;padding:5px 15px;border-radius:15px;font-weight:bold}
.panel{background:#111;border:1px solid #333;border-radius:10px;padding:20px;margin:15px 0}
.control-btn{background:#00ff88;color:black;border:none;padding:15px 30px;font-size:16px;font-weight:bold;border-radius:5px;cursor:pointer;margin:10px}
.emergency-btn{background:#ff4444;color:white;border:none;padding:15px 30px;font-size:16px;font-weight:bold;border-radius:5px;cursor:pointer;margin:10px}
.alert{background:#1a0000;border:2px solid #ff0000;color:#ff4444;padding:15px;margin:15px 0;text-align:center}
.ready{background:#001a00;border:2px solid #00ff88;color:#00ff88;padding:15px;margin:15px 0;text-align:center}
.scanning{background:#1a1a00;border:2px solid #ffaa00;color:#ffaa00;padding:15px;margin:15px 0;text-align:center}
.stat-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #222}
.stat-label{color:#888}.stat-value{color:#fff;font-weight:bold}
</style></head>
<body>
<div class="header"><h1>🦎 RAPHAEL v5.0</h1><span class="badge">SIMPLE & ROBUST</span></div>

<div id="status-banner" class="ready"><h2 id="main-status">⏳ Loading...</h2></div>

<div class="panel">
<h2>🎮 Controls</h2>
<button class="control-btn" id="btn-start" onclick="start()">▶️ START</button>
<button class="control-btn" id="btn-stop" onclick="stop()">⏹️ STOP</button>
<button class="emergency-btn" onclick="emergency()">🚨 EMERGENCY STOP</button>
<button class="control-btn" onclick="reset()" style="background:#666">🔄 RESET</button>
</div>

<div class="panel">
<h2>📊 Stats</h2>
<div class="stat-row"><span class="stat-label">Status</span><span class="stat-value" id="status">--</span></div>
<div class="stat-row"><span class="stat-label">Autotrader</span><span class="stat-value" id="auto">--</span></div>
<div class="stat-row"><span class="stat-label">Trades</span><span class="stat-value" id="trades">0/5</span></div>
<div class="stat-row"><span class="stat-label">Wallet</span><span class="stat-value" id="wallet">--</span></div>
<div class="stat-row"><span class="stat-label">Emergency</span><span class="stat-value" id="emergency">--</span></div>
</div>

<script>
async function start(){
  document.getElementById('btn-start').disabled=true;
  await fetch('/api/start-trading',{method:'POST'});
  refresh();
}
async function stop(){
  await fetch('/api/stop-trading',{method:'POST'});
  refresh();
}
async function emergency(){
  if(!confirm('🚨 STOP ALL TRADING?'))return;
  await fetch('/api/emergency-stop',{method:'POST'});
  refresh();
}
async function reset(){
  if(!confirm('🔄 Reset everything?'))return;
  await fetch('/api/reset',{method:'POST'});
  refresh();
}
async function refresh(){
  try{
    const r=await fetch('/api/status');
    const d=await r.json();
    
    const banner=document.getElementById('status-banner');
    const mainStatus=document.getElementById('main-status');
    
    banner.className='panel';
    if(d.emergency_stop){
      banner.className='alert';
      mainStatus.innerHTML='🛑 EMERGENCY STOP ACTIVE';
    }else if(d.autotrader_running){
      banner.className='scanning';
      mainStatus.innerHTML='🚀 SCANNING FOR TRADES';
    }else{
      banner.className='ready';
      mainStatus.innerHTML='✅ READY';
    }
    
    document.getElementById('status').textContent=d.status;
    document.getElementById('auto').textContent=d.autotrader_running?'🟢 RUNNING':'❌ OFFLINE';
    document.getElementById('auto').style.color=d.autotrader_running?'#00ff88':'#ff4444';
    document.getElementById('trades').textContent=d.total_trades+'/'+d.target_trades;
    document.getElementById('wallet').textContent=d.wallet_balance.toFixed(4)+' SOL';
    document.getElementById('emergency').textContent=d.emergency_stop?'🔴 TRIGGERED':'❌ Ready';
    document.getElementById('emergency').style.color=d.emergency_stop?'#ff4444':'#00ff88';
    
    document.getElementById('btn-start').disabled=d.emergency_stop||d.autotrader_running;
    document.getElementById('btn-stop').disabled=!d.autotrader_running;
  }catch(e){}
}
refresh();
setInterval(refresh,1000);
</script>
</body></html>"""

if __name__ == '__main__':
    log("="*50)
    log("RAPHAEL MONITOR v5.0 - Starting...")
    log(f"Port: {PORT}")
    log("="*50)
    
    os.system(f"lsof -t -i:{PORT} 2>/dev/null | xargs kill -9 2>/dev/null")
    time.sleep(1)
    
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    log("🟢 Server ready at http://localhost:3456")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("\n🛑 Shutting down...")
        stop_autotrader()
    finally:
        server.shutdown()
