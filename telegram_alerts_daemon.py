#!/usr/bin/env python3
"""
Telegram Alert Daemon for Trading Agent
Reads signals from /tmp/trading_signals.json and sends to Telegram
"""

import json
import time
import os
from datetime import datetime

SIGNALS_FILE = '/tmp/trading_signals.json'
SENT_FILE = '/tmp/trading_signals_sent.json'

def send_telegram_message(message: str, chat_id: str = '6610224534'):
    """Send message via OpenClaw (parent session will handle via message tool)"""
    # Print the message - this will be picked up by the agent session
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*60}")
    print(f"TRADING ALERT [{timestamp}]:")
    print(f"{'='*60}")
    print(message)
    print(f"{'='*60}\n")
    
    # Also write to a pipe for immediate notification
    alert_file = '/tmp/trading_alert_now.txt'
    with open(alert_file, 'w') as f:
        f.write(message)
    
    return True

def check_and_send_signals():
    """Check for new signals and send them"""
    if not os.path.exists(SIGNALS_FILE):
        return
    
    try:
        with open(SIGNALS_FILE, 'r') as f:
            signals = json.load(f)
    except:
        return
    
    if not signals:
        return
    
    # Track which signals we've sent
    sent_ids = []
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, 'r') as f:
                sent_ids = json.load(f)
        except:
            pass
    
    # Send unsent signals
    new_sent = []
    for i, signal in enumerate(signals):
        signal_id = f"{signal['timestamp']}_{i}"
        
        if signal_id not in sent_ids and not signal.get('notified', False):
            if send_telegram_message(signal['message']):
                signal['notified'] = True
                new_sent.append(signal_id)
                print(f"Sent signal {signal_id}")
    
    # Update sent tracking
    if new_sent:
        sent_ids.extend(new_sent)
        with open(SENT_FILE, 'w') as f:
            json.dump(sent_ids, f)
        
        # Update signals file
        with open(SIGNALS_FILE, 'w') as f:
            json.dump(signals, f, indent=2)

def main():
    """Main loop - check every 10 seconds"""
    print("="*60)
    print("Telegram Alert Daemon Started")
    print(f"Watching: {SIGNALS_FILE}")
    print("="*60)
    
    while True:
        check_and_send_signals()
        time.sleep(10)

if __name__ == "__main__":
    main()