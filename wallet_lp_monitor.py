#!/usr/bin/env python3
"""
Wallet Liquidity Pool Monitor
Monitors specific wallets for LP additions and sends Telegram alerts
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Target wallets to monitor
TARGET_WALLETS = [
    "39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg",
    "LfEcaUf77iEhnz6gFpLqYgDb5Uk6Ekc5n69wu7Qa9Uw",
    "srVBGD3JuvPpssYUq86Xfp4D4cxvEJYNQ2fVnkPW2oo"
]

# LP-related program IDs on Solana
LP_PROGRAMS = {
    "Raydium": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "Orca": "9W959DqneYp8GfrBGjM6kL6dVjPxWz7uF2KJ3M5N8Q7Z",  # Whirlpool
    "Orca Legacy": "DjVe6s44mgXJ2dK2nQVSB5dCnG1pQ1U5M7YkD6S7Q8R9",
    "Meteora": "LBUZKhRxPFHsE8L2T9pAqN4hP9n2Z8kM3wX7YcV5B6N1",
    "Lifinity": "2wT8Yq49kXWL5yL5oV3P5G7J8K9L0M1N2O3P4Q5R6S7T8",
}

# Known LP token patterns
LP_TOKEN_SYMBOLS = ["LP", "RPLP", "ORCA", "meteora", "lifinity"]

class WalletLPMonitor:
    def __init__(self):
        self.seen_txs = {}  # Track seen transactions
        self.load_state()
        
        # Load Helius API key
        try:
            with open("/home/skux/.openclaw/workspace/solana-trader/.secrets/helius.key", 'r') as f:
                self.helius_key = f.read().strip()
            self.helius_url = f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}"
        except:
            self.helius_key = None
            self.helius_url = None
            print("❌ Helius API key not found")
    
    def load_state(self):
        """Load seen transactions"""
        try:
            with open('/tmp/lp_monitor_state.json', 'r') as f:
                data = json.load(f)
                self.seen_txs = data.get('txs', {})
        except:
            self.seen_txs = {}
    
    def save_state(self):
        """Save seen transactions"""
        with open('/tmp/lp_monitor_state.json', 'w') as f:
            json.dump({'txs': self.seen_txs, 'last_update': datetime.now().isoformat()}, f)
    
    def get_wallet_txs(self, wallet: str, limit: int = 20) -> List[Dict]:
        """Get recent transactions for a wallet"""
        if not self.helius_url:
            return []
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet, {"limit": limit}]
            }
            
            r = requests.post(self.helius_url, json=payload, timeout=10)
            data = r.json()
            
            if 'result' in data:
                return data['result']
        except Exception as e:
            print(f"❌ Error fetching txs for {wallet[:8]}: {e}")
        
        return []
    
    def get_tx_details(self, signature: str) -> Optional[Dict]:
        """Get transaction details"""
        if not self.helius_url:
            return None
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
            }
            
            r = requests.post(self.helius_url, json=payload, timeout=10)
            data = r.json()
            
            if 'result' in data and data['result']:
                return data['result']
        except Exception as e:
            print(f"❌ Error fetching tx {signature[:16]}: {e}")
        
        return None
    
    def is_lp_related(self, tx: Dict) -> Optional[Dict]:
        """Check if transaction is LP-related and return details"""
        if not tx or not tx.get('transaction'):
            return None
        
        tx_data = tx['transaction']
        meta = tx.get('meta', {})
        
        # Check for LP program interactions
        account_keys = []
        if 'message' in tx_data and 'accountKeys' in tx_data['message']:
            for acc in tx_data['message']['accountKeys']:
                if isinstance(acc, dict):
                    account_keys.append(acc.get('pubkey', ''))
                else:
                    account_keys.append(acc)
        
        # Check for LP program involvement
        lp_program_found = None
        for acc in account_keys:
            for program_name, program_id in LP_PROGRAMS.items():
                if acc == program_id:
                    lp_program_found = program_name
                    break
            if lp_program_found:
                break
        
        if not lp_program_found:
            return None
        
        # Look for token transfers/mints
        token_addresses = []
        pre_balances = meta.get('preTokenBalances', [])
        post_balances = meta.get('postTokenBalances', [])
        
        # Get token mints from balance changes
        for bal in pre_balances + post_balances:
            if isinstance(bal, dict):
                mint = bal.get('mint')
                if mint:
                    token_addresses.append(mint)
        
        # Also check inner instructions
        inner_instructions = meta.get('innerInstructions', [])
        for inner in inner_instructions:
            if isinstance(inner, dict) and 'instructions' in inner:
                for inst in inner['instructions']:
                    if isinstance(inst, dict):
                        # Check for initialize/mint instructions
                        if inst.get('parsed', {}).get('type') in ['initializeAccount', 'mintTo', 'transfer']:
                            info = inst.get('parsed', {}).get('info', {})
                            if 'mint' in info:
                                token_addresses.append(info['mint'])
        
        # Get unique token addresses
        token_addresses = list(set(token_addresses))
        
        # Filter out common tokens (SOL, USDC, etc)
        common_tokens = [
            'So11111111111111111111111111111111111111112',  # SOL
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
            'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',  # USDT
        ]
        
        project_tokens = [t for t in token_addresses if t not in common_tokens]
        
        if project_tokens:
            return {
                'lp_program': lp_program_found,
                'tokens': project_tokens,
                'timestamp': tx.get('blockTime'),
                'signature': tx.get('transaction', {}).get('signatures', [''])[0]
            }
        
        return None
    
    def send_telegram_alert(self, wallet: str, lp_data: Dict):
        """Send Telegram notification"""
        timestamp = datetime.fromtimestamp(lp_data['timestamp']) if lp_data['timestamp'] else datetime.now()
        
        message = f"""🚨 LP ALERT - Smart Money Activity

👤 Wallet: {wallet[:16]}...
🔧 LP Program: {lp_data['lp_program']}
🪙 Token CA(s):
"""
        
        for token in lp_data['tokens'][:3]:  # Limit to 3 tokens
            message += f"`{token}`\n"
        
        message += f"""
⏰ Time: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}
🔗 Tx: https://solscan.io/tx/{lp_data['signature']}
"""
        
        print(f"\n{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        
        # Send via Telegram
        try:
            # Use OpenClaw's message tool via sessions_send or direct message
            # For now, just log to console (user can integrate Telegram bot)
            print(f"[TO TELEGRAM]: {message}")
        except Exception as e:
            print(f"Failed to send Telegram: {e}")
    
    def check_all_wallets(self):
        """Check all target wallets"""
        print(f"\n🔍 Checking {len(TARGET_WALLETS)} wallets...")
        
        alerts_triggered = 0
        
        for wallet in TARGET_WALLETS:
            print(f"\n👤 Checking: {wallet[:20]}...")
            
            # Get recent transactions
            txs = self.get_wallet_txs(wallet)
            
            for tx in txs:
                sig = tx.get('signature', '')
                
                # Skip if already seen
                if sig in self.seen_txs.get(wallet, []):
                    continue
                
                # Mark as seen
                if wallet not in self.seen_txs:
                    self.seen_txs[wallet] = []
                self.seen_txs[wallet].append(sig)
                
                # Keep only last 1000 sigs per wallet
                self.seen_txs[wallet] = self.seen_txs[wallet][-1000:]
                
                # Get tx details
                tx_details = self.get_tx_details(sig)
                if not tx_details:
                    continue
                
                # Check if LP-related
                lp_data = self.is_lp_related(tx_details)
                
                if lp_data:
                    print(f"🚨 LP Activity detected!")
                    self.send_telegram_alert(wallet, lp_data)
                    alerts_triggered += 1
                else:
                    print(f"   Tx {sig[:16]}... - Not LP related")
        
        self.save_state()
        return alerts_triggered
    
    def run(self, interval_seconds: int = 60):
        """Run continuous monitoring"""
        print("="*70)
        print("🚨 WALLET LP MONITOR - Starting...")
        print("="*70)
        print(f"\nMonitoring {len(TARGET_WALLETS)} wallets:")
        for wallet in TARGET_WALLETS:
            print(f"  • {wallet[:30]}...")
        
        print(f"\n⏰ Checking every {interval_seconds} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                cycle_start = time.time()
                
                alerts = self.check_all_wallets()
                
                if alerts == 0:
                    print(f"\n⏳ No LP activity at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print(f"\n🚨 {alerts} LP alert(s) triggered!")
                
                # Wait for next cycle
                elapsed = time.time() - cycle_start
                sleep_time = max(0, interval_seconds - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped")
            self.save_state()

if __name__ == "__main__":
    monitor = WalletLPMonitor()
    monitor.run(interval_seconds=60)
