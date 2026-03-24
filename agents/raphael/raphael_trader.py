#!/usr/bin/env python3
"""
Raphael Auto-Trader v1.0
Real Solana trading with Jupiter API + Wallet integration
"""

import json
import os
import time
import base58
import base64
import requests
from datetime import datetime
from typing import Optional, Dict, Any

# Solana imports
try:
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import VersionedTransaction
    from solders.message import to_bytes_versioned
    from spl.token.instructions import get_associated_token_address
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    print("⚠️ solana-py not installed. Run: pip install solana solders requests spl")

# Configuration
CONFIG = {
    "max_trade_size": 0.01,  # SOL
    "slippage_bps": 100,     # 1%
    "priority_fee": 10000,   # lamports
    "min_balance": 0.05,     # SOL (keep reserve)
}

# Token decimals lookup
TOKEN_DECIMALS = {
    "So11111111111111111111111111111111111111112": 9,  # SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": 6,  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": 6,  # USDT
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": 5,  # BONK
}

class RaphaelTrader:
    def __init__(self):
        self.wallet = None
        self.wallet_address = None
        self.connection = None
        self.balance = 0.0
        self.load_wallet()
        
    def load_wallet(self):
        """Load wallet from key file"""
        try:
            key_path = "/home/skux/.openclaw/workspace/solana-trader/.secrets/wallet.key"
            with open(key_path, 'r') as f:
                private_key = f.read().strip()
            
            # Decode base58 private key (64 bytes = full keypair)
            key_bytes = base58.b58decode(private_key)
            self.wallet = Keypair.from_bytes(key_bytes)
            self.wallet_address = str(self.wallet.pubkey())
            print(f"✅ Wallet loaded: {self.wallet_address[:8]}...{self.wallet_address[-4:]}")
            
            # Init connection
            helius_key = open("/home/skux/.openclaw/workspace/solana-trader/.secrets/helius.key").read().strip()
            self.connection = Client(f"https://mainnet.helius-rpc.com/?api-key={helius_key}")
            
            # Get initial balance
            self.update_balance()
            
        except Exception as e:
            print(f"❌ Wallet load error: {e}")
            import traceback
            traceback.print_exc()
            self.wallet = None
    
    def update_balance(self) -> float:
        """Get wallet SOL balance"""
        if not self.connection:
            return 0.0
        try:
            balance_lamports = self.connection.get_balance(self.wallet.pubkey()).value
            self.balance = balance_lamports / 1e9
            return self.balance
        except Exception as e:
            print(f"❌ Balance check error: {e}")
            return 0.0
    
    def get_quote(self, output_mint: str, amount_sol: float) -> Optional[Dict]:
        """Get Jupiter swap quote"""
        try:
            # Load Jupiter API key
            jupiter_key_path = "/home/skux/.openclaw/workspace/solana-trader/.secrets/jupiter.key"
            jupiter_key = open(jupiter_key_path).read().strip()
            
            url = "https://api.jup.ag/swap/v1/quote"
            headers = {"x-api-key": jupiter_key}
            params = {
                "inputMint": "So11111111111111111111111111111111111111112",
                "outputMint": output_mint,
                "amount": str(int(amount_sol * 1e9)),  # lamports
                "slippageBps": str(CONFIG["slippage_bps"]),
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            
            if resp.status_code != 200:
                print(f"❌ Quote failed: {resp.status_code} - {resp.text[:200]}")
                return None
            
            data = resp.json()
            
            # Parse and display quote
            out_amount = data.get("outAmount", 0)
            in_amount = data.get("inAmount", 0)
            price_impact = data.get("priceImpactPct", "0")
            
            # Convert to readable amounts
            in_decimals = 9  # SOL
            out_decimals = TOKEN_DECIMALS.get(output_mint, 6)
            
            in_readable = float(in_amount) / (10 ** in_decimals)
            out_readable = float(out_amount) / (10 ** out_decimals)
            
            print(f"📊 Quote: {in_readable:.6f} SOL → {out_readable:.6f} tokens")
            print(f"📊 Price impact: {price_impact}%")
            
            return data
                
        except Exception as e:
            print(f"❌ Quote error: {e}")
            return None
    
    def execute_swap(self, quote: Dict) -> Optional[Dict]:
        """Execute Jupiter swap"""
        if not self.wallet:
            print("❌ No wallet loaded")
            return None
        
        try:
            # Get swap transaction
            jupiter_key_path = "/home/skux/.openclaw/workspace/solana-trader/.secrets/jupiter.key"
            jupiter_key = open(jupiter_key_path).read().strip()
            headers = {"x-api-key": jupiter_key}
            
            url = "https://api.jup.ag/swap/v1/swap"
            payload = {
                "quoteResponse": quote,
                "userPublicKey": self.wallet_address,
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": CONFIG["priority_fee"],
                "asLegacyTransaction": False
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code != 200:
                print(f"❌ Swap request failed: {resp.status_code}")
                return None
            
            swap_data = resp.json()
            
            # Parse quote data for display
            quote_data = swap_data.get("quoteResponse", {})
            if quote_data:
                out_amount = quote_data.get("outAmount", 0)
                in_amount = quote_data.get("inAmount", 0)
                price_impact = quote_data.get("priceImpactPct", 0)
                print(f"📊 Quote: {int(in_amount)/1e9:.6f} SOL → {int(out_amount)/1e6:.6f} output")
                print(f"📊 Price impact: {price_impact}%")
            
            # Deserialize the versioned transaction
            tx_bytes = base64.b64decode(swap_data["swapTransaction"])
            tx = VersionedTransaction.from_bytes(tx_bytes)
            
            # The Jupiter API returns a partially signed transaction that needs our signature
            # Create a new signed transaction using the message and our keypair
            # The __init__ takes: message and keypairs
            signed_tx = VersionedTransaction(message=tx.message, keypairs=[self.wallet])
            
            # Send the signed transaction
            opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed")
            result = self.connection.send_transaction(signed_tx, opts=opts)
            
            signature = result.value
            print(f"✅ Transaction sent: {signature}")
            
            # Wait for confirmation
            time.sleep(2)
            self.update_balance()
            
            return {
                "signature": str(signature),
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Swap execution error: {e}")
            return None
    
    def get_token_price(self, token_mint: str) -> Optional[float]:
        """Get current token price in USD via DexScreener"""
        try:
            url = f"https://api.dexscreener.com/token-pairs/v1/solana/{token_mint}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    # Get price from first pair
                    price_usd = data[0].get('priceUsd', 0)
                    if price_usd:
                        return float(price_usd)
            return None
        except Exception as e:
            print(f"⚠️ Price fetch error: {e}")
            return None
    
    def get_token_balance(self, token_mint: str) -> float:
        """Get token balance for a specific mint"""
        try:
            from spl.token.instructions import get_associated_token_address
            from spl.token.constants import TOKEN_PROGRAM_ID
            
            token_pubkey = Pubkey.from_string(token_mint)
            ata = get_associated_token_address(self.wallet.pubkey(), token_pubkey)
            
            resp = self.connection.get_token_account_balance(ata)
            if resp.value:
                return float(resp.value.ui_amount_string)
            return 0.0
        except Exception as e:
            return 0.0
    
    def sell(self, token_mint: str, percentage: float = 100.0) -> Dict:
        """Sell token position (default 100% = full exit)"""
        print(f"\n🦎 RAPHAEL SELL INITIATED")
        print(f"Token: {token_mint}")
        print(f"Percentage: {percentage}%")
        
        # Get token balance
        token_balance = self.get_token_balance(token_mint)
        if token_balance <= 0:
            return {
                "status": "FAILED", 
                "error": "No token balance found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate sell amount
        sell_amount = int(token_balance * (percentage / 100.0))
        print(f"📊 Selling {sell_amount} tokens ({percentage}% of {token_balance})")
        
        try:
            # Load Jupiter API key
            jupiter_key_path = "/home/skux/.openclaw/workspace/solana-trader/.secrets/jupiter.key"
            jupiter_key = open(jupiter_key_path).read().strip()
            headers = {"x-api-key": jupiter_key}
            
            # Get decimals
            decimals = TOKEN_DECIMALS.get(token_mint, 6)
            amount_raw = int(sell_amount * (10 ** decimals))
            
            # Get quote (reverse: token -> SOL)
            url = "https://api.jup.ag/swap/v1/quote"
            params = {
                "inputMint": token_mint,
                "outputMint": "So11111111111111111111111111111111111111112",
                "amount": str(amount_raw),
                "slippageBps": str(CONFIG["slippage_bps"]),
            }
            
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                return {
                    "status": "FAILED",
                    "error": f"Quote failed: {resp.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
            
            quote = resp.json()
            
            # Execute swap
            swap_url = "https://api.jup.ag/swap/v1/swap"
            payload = {
                "quoteResponse": quote,
                "userPublicKey": self.wallet_address,
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": CONFIG["priority_fee"],
            }
            
            resp = requests.post(swap_url, headers=headers, json=payload, timeout=15)
            if resp.status_code != 200:
                return {
                    "status": "FAILED",
                    "error": "Swap request failed",
                    "timestamp": datetime.now().isoformat()
                }
            
            swap_data = resp.json()
            
            # Sign and send transaction
            tx_bytes = base64.b64decode(swap_data["swapTransaction"])
            tx = VersionedTransaction.from_bytes(tx_bytes)
            signed_tx = VersionedTransaction(message=tx.message, keypairs=[self.wallet])
            
            opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed")
            result = self.connection.send_transaction(signed_tx, opts=opts)
            
            signature = result.value
            print(f"✅ Sell transaction sent: {signature}")
            
            time.sleep(2)
            self.update_balance()
            
            return {
                "signature": str(signature),
                "status": "SUCCESS",
                "tokens_sold": sell_amount,
                "percentage": percentage,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Sell error: {e}")
            return {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def trade(self, token_mint: str, amount_sol: float) -> Dict:
        """Execute full trade flow"""
        print(f"\n🦎 RAPHAEL TRADE INITIATED")
        print(f"Token: {token_mint}")
        print(f"Amount: {amount_sol} SOL")
        
        # Check balance
        balance = self.update_balance()
        if balance < amount_sol + CONFIG["min_balance"]:
            return {
                "status": "FAILED",
                "error": f"Insufficient balance: {balance} SOL",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get current price before trade (for entry tracking)
        entry_price = self.get_token_price(token_mint)
        
        # Get quote
        quote = self.get_quote(token_mint, amount_sol)
        if not quote:
            return {
                "status": "FAILED",
                "error": "Failed to get quote",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute
        result = self.execute_swap(quote)
        if result:
            result["amount_sol"] = amount_sol
            result["token_mint"] = token_mint
            result["entry_price_usd"] = entry_price
            
            # Calculate tokens received
            out_amount = quote.get("outAmount", 0)
            out_decimals = TOKEN_DECIMALS.get(token_mint, 6)
            tokens_received = float(out_amount) / (10 ** out_decimals)
            result["tokens_received"] = tokens_received
            
            return result
        else:
            return {
                "status": "FAILED",
                "error": "Swap execution failed",
                "timestamp": datetime.now().isoformat()
            }

if __name__ == "__main__":
    if not SOLANA_AVAILABLE:
        print("❌ Solana packages not installed")
        print("Run: pip install solana solders requests base58")
        exit(1)
    
    trader = RaphaelTrader()
    
    if trader.wallet:
        print(f"\n💰 Wallet Balance: {trader.balance:.6f} SOL")
        print(f"📍 Address: {trader.wallet_address}")
        
        # Test trade to USDC
        if len(sys.argv) > 1 and sys.argv[1] == "trade":
            print("\n🚀 Executing test trade...")
            result = trader.trade(
                token_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                amount_sol=0.0001
            )
            print(f"\n{'='*60}")
            print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to load wallet")
