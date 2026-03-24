#!/usr/bin/env python3
"""
Check Trading Agent Status
Run this to see current status
"""

import json
import os
from datetime import datetime, timezone

SIGNALS_FILE = '/tmp/trading_signals.json'
ALERTS_FILE = '/tmp/trading_alert_now.txt'

def check_sydney_time():
    """Check if we're in trading window"""
    now = datetime.now(timezone.utc)
    sydney_hour = (now.hour + 11) % 24
    hour_minute = f"{sydney_hour}:{now.minute:02d}"
    
    in_window = 0 <= sydney_hour < 4
    
    return {
        'utc_time': now.strftime('%H:%M'),
        'sydney_time': hour_minute,
        'in_trading_window': in_window
    }

def check_signals():
    """Check for trading signals"""
    data = {
        'signal_count': 0,
        'latest_signal': None
    }
    
    # Check immediate alert
    if os.path.exists(ALERTS_FILE):
        data['has_immediate_alert'] = True
        try:
            with open(ALERTS_FILE, 'r') as f:
                data['immediate_message'] = f.read()
        except:
            pass
    
    # Check signals database
    if os.path.exists(SIGNALS_FILE):
        try:
            with open(SIGNALS_FILE, 'r') as f:
                signals = json.load(f)
                data['signal_count'] = len(signals)
                if signals:
                    latest = signals[-1]
                    data['latest_signal'] = {
                        'time': latest.get('timestamp'),
                        'summary': latest.get('message', '')[:200] + '...',
                        'notified': latest.get('notified', False)
                    }
        except:
            pass
    
    return data

def main():
    status = check_sydney_time()
    signals = check_signals()
    
    print("="*60)
    print("TRADING AGENT STATUS")
    print("="*60)
    print(f"\n⏰ TIME:")
    print(f"   UTC Time: {status['utc_time']}")
    print(f"   Sydney Time: {status['sydney_time']}")
    print(f"   Trading Window (12am-4am): {'✅ ACTIVE' if status['in_trading_window'] else '❌ INACTIVE'}")
    
    print(f"\n📊 SIGNALS:")
    print(f"   Total Signals: {signals['signal_count']}")
    
    if signals.get('immediate_message'):
        print(f"\n🔔 IMMEDIATE ALERT:")
        print(f"   {signals['immediate_message'][:500]}")
        # Clear it after reading
        try:
            os.remove(ALERTS_FILE)
        except:
            pass
    elif signals.get('latest_signal'):
        print(f"\n📢 LATEST SIGNAL ({signals['latest_signal']['time']}):")
        print(f"   {signals['latest_signal']['summary']}")
        print(f"   Status: {'✅ Sent' if signals['latest_signal']['notified'] else '⏳ Pending'}")
    
    print("\n" + "="*60)
    print("Files:")
    print(f"  Signals: {SIGNALS_FILE}")
    print(f"  Alerts:  {ALERTS_FILE}")
    print(f"  Logs:    /tmp/trading_agent.log")
    print("="*60)

if __name__ == "__main__":
    main()