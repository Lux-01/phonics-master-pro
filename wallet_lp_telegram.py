#!/usr/bin/env python3
"""
Wallet LP Monitor - Telegram Integration
Sends Telegram notifications for LP activity
"""

import requests
import time
import json
import sys
from datetime import datetime

# Add path for imports
sys.path.insert(0, '/home/skux/.openclaw/workspace')

# Import the monitor class
from wallet_lp_monitor import WalletLPMonitor, TARGET_WALLETS

class TelegramLPMonitor(WalletLPMonitor):
    def send_telegram_alert(self, wallet: str, lp_data: Dict):
        """Send Telegram notification via OpenClaw message tool"""
        timestamp = datetime.fromtimestamp(lp_data['timestamp']) if lp_data['timestamp'] else datetime.now()
        
        # Get token info from Birdeye
        token_info = {}
        for token in lp_data['tokens'][:2]:
            try:
                url = f"https://public-api.birdeye.so/defi/token_data?address={token}"
                headers = {"X-API-KEY": "6335463fca7340f9a2c73eacd5a37f64"}
                r = requests.get(url, headers=headers, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('success'):
                        token_info[token] = {
                            'symbol': data['data'].get('symbol', 'UNKNOWN'),
                            'mcap': data['data'].get('marketCap', 0),
                            'price': data['data'].get('price', 0)
                        }
            except:
                pass
        
        message = f"""🚨 *LP ALERT* - Smart Money Activity

👤 Wallet: `{wallet[:16]}...`
🔧 Platform: {lp_data['lp_program']}

🪙 *Token Contract Address(es):*
"""
        
        for token in lp_data['tokens'][:2]:
            info = token_info.get(token, {})
            symbol = info.get('symbol', 'UNKNOWN')
            mcap = info.get('mcap', 0)
            
            mcap_str = f" (${mcap/1e6:.2f}M)" if mcap > 0 else ""
            message += f"\n`{token}`{mcap_str}"
        
        message += f"""

⏰ Time: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}
🔗 [View on Solscan](https://solscan.io/tx/{lp_data['signature']})

⚠️ DYOR before trading!
"""
        
        print(f"\n{'='*60}")
        print("SENDING TELEGRAM ALERT:")
        print(message)
        print(f"{'='*60}\n")
        
        # Write to alert file for notification
        alert_file = '/tmp/lp_alert_pending.json'
        with open(alert_file, 'w') as f:
            json.dump({
                'type': 'lp_alert',
                'wallet': wallet,
                'tokens': lp_data['tokens'],
                'program': lp_data['lp_program'],
                'signature': lp_data['signature'],
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        return alert_file, message

def main():
    """Main function - check once and exit"""
    print("🔍 Wallet LP Monitor - Single Check")
    
    monitor = TelegramLPMonitor()
    
    # Load telegram chat ID if available
    try:
        with open('/home/skux/.openclaw/workspace/.telegram_config.json', 'r') as f:
            config = json.load(f)
            chat_id = config.get('chat_id')
            print(f"Telegram chat configured: {chat_id}")
    except:
        chat_id = None
        print("No Telegram config - logging to console only")
    
    print(f"\nMonitoring {len(TARGET_WALLETS)} wallets...")
    for wallet in TARGET_WALLETS:
        print(f"  • {wallet[:25]}...")
    
    print("\n" + "="*70)
    
    alerts = monitor.check_all_wallets()
    
    if alerts == 0:
        print(f"\n✅ No LP activity found")
    else:
        print(f"\n🚨 {alerts} alert(s) triggered!")
        print(f"Check /tmp/lp_alert_pending.json for details")
    
    print("="*70)

if __name__ == "__main__":
    main()
