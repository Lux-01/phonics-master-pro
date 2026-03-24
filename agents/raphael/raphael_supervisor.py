#!/usr/bin/env python3
"""
Raphael Supervisor v2.2 - Keeps trader running with auto-restart
Full 27-rule implementation (BUG FIXED)
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def main():
    log("🦎 Raphael Supervisor v2.2 Starting...")
    log("   Full 27 Rules (BUG FIXED) | Auto-restart on crash")
    log("   Grace period: 60 seconds between restarts")
    
    restart_count = 0
    last_restart = time.time()
    
    while True:
        try:
            # Check if we need rate limiting
            now = time.time()
            if restart_count > 0 and (now - last_restart) < 60:
                wait_time = 60 - (now - last_restart)
                log(f"   Rate limiting: waiting {wait_time:.0f}s before restart...")
                time.sleep(wait_time)
            
            restart_count += 1
            last_restart = time.time()
            
            log(f"🔄 Starting Raphael v2.3 (attempt #{restart_count})...")
            
            # Run Raphael v2.3 with auto-restart on crash
            process = subprocess.Popen(
                [sys.executable, "raphael_autotrader_v2.py"],
                cwd="/home/skux/.openclaw/workspace/agents/raphael",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            log(f"   PID: {process.pid}")
            
            # Monitor output
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line.rstrip())
                sys.stdout.flush()
            
            # Process ended
            returncode = process.wait()
            log(f"⚠️  Raphael exited with code {returncode}")
            
            if returncode == 0:
                log("   Clean exit, will restart in 60 seconds...")
            else:
                log(f"   Crash detected (code {returncode}), restarting...")
                
        except KeyboardInterrupt:
            log("\n🛑 Supervisor stopped by user")
            break
        except Exception as e:
            log(f"   Supervisor error: {e}")
            time.sleep(5)
        
        # Wait before restart
        log("   Waiting 60 seconds before restart...")
        time.sleep(60)

if __name__ == "__main__":
    main()
