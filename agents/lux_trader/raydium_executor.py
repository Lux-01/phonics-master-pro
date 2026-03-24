#!/usr/bin/env python3
"""
🚀 RAYDIUM DIRECT SELL EXECUTOR
Sells directly on Raydium AMM (bypassing Jupiter)
"""

import requests
import json
import base64
from typing import Dict, Optional, Tuple
from datetime import datetime

try:
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solders.pubkey import Pubkey
    import base58
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

from secure_key_manager import SecureKeyManager

# Raydium program IDs
RAYDIUM_AMM_PROGRAM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
RAYDIUM_AUTHORITY = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
SOL_MINT = "So11111111111111111111111111111111111111112"

SOLANA_RPC = "https://mainnet.helius-rpc.com/?api-key=350aa83c-44a4-4068-a511-580f82930d84"


class RaydiumExecutor:
    """Execute swaps directly on Raydium AMM"""
    
    def __init__(self, wallet_address: str):
        self.wallet = wallet_address
        self.key_manager = SecureKeyManager()
        self.keypair: Optional[Keypair] = None
        
        if SOLANA_AVAILABLE:
            self._load_keypair()
    
    def _load_keypair(self) -> bool:
        """Load keypair from secure storage"""
        private_key = self.key_manager.get_key()
        if not private_key:
            return False
        
        try:
            key_bytes = base58.b58decode(private_key)
            self.keypair = Keypair.from_bytes(key_bytes)
            return True
        except Exception as e:
            print(f"❌ Error loading keypair: {e}")
            return False
    
    def find_raydium_pool(self, token_mint: str) -> Optional[Dict]:
        """Find Raydium pool for token/SOL pair"""
        try:
            # Query Raydium API for pools
            url = "https://api.raydium.io/v2/main/pools"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                pools = data.get('data', [])
                
                for pool in pools:
                    # Check if this pool has our token and SOL
                    coin_mint = pool.get('coinMint', '')
                    pc_mint = pool.get('pcMint', '')
                    
                    if (coin_mint == token_mint and pc_mint == SOL_MINT) or \
                       (pc_mint == token_mint and coin_mint == SOL_MINT):
                        return {
                            "id": pool.get('id'),
                            "amm_id": pool.get('ammId'),
                            "lp_mint": pool.get('lpMint'),
                            "coin_mint": coin_mint,
                            "pc_mint": pc_mint,
                            "coin_amount": pool.get('coinAmount', 0),
                            "pc_amount": pool.get('pcAmount', 0),
                            "lp_amount": pool.get('lpAmount', 0)
                        }
                
                return None
            else:
                print(f"   Raydium API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   Error finding pool: {e}")
            return None
    
    def calculate_swap_amounts(self, pool: Dict, token_amount: float, 
                               token_decimals: int = 9) -> Tuple[float, float]:
        """
        Calculate expected SOL output using constant product formula
        x * y = k
        """
        try:
            # Get reserves
            coin_amount = float(pool.get('coin_amount', 0))
            pc_amount = float(pool.get('pc_amount', 0))
            
            if coin_amount == 0 or pc_amount == 0:
                return 0, 0
            
            # Determine which is token and which is SOL
            coin_mint = pool.get('coin_mint', '')
            
            if coin_mint == SOL_MINT:
                # coin = SOL, pc = token
                sol_reserve = coin_amount / 1e9
                token_reserve = pc_amount / (10 ** token_decimals)
            else:
                # coin = token, pc = SOL
                token_reserve = coin_amount / (10 ** token_decimals)
                sol_reserve = pc_amount / 1e9
            
            # Constant product
            k = sol_reserve * token_reserve
            
            # New token reserve after swap
            new_token_reserve = token_reserve + token_amount
            
            # New SOL reserve (must maintain k)
            new_sol_reserve = k / new_token_reserve
            
            # SOL output (minus fees - 0.25%)
            sol_out = sol_reserve - new_sol_reserve
            sol_out_after_fees = sol_out * 0.9975  # 0.25% fee
            
            # Price impact
            price_impact = (token_amount / token_reserve) * 100
            
            return sol_out_after_fees, price_impact
            
        except Exception as e:
            print(f"   Calculation error: {e}")
            return 0, 0
    
    def execute_sell_raydium(self, token_address: str, amount_tokens: float,
                              token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
        """
        Execute sell directly on Raydium
        
        NOTE: This finds the pool and calculates expected output.
        Full transaction building requires:
        1. Creating swap instruction for Raydium AMM
        2. Handling ATA creation
        3. Proper instruction ordering
        """
        print(f"\n🚀 RAYDIUM DIRECT SELL")
        print(f"   Token: {token_symbol}")
        print(f"   Amount: {amount_tokens:.6f} tokens")
        
        if not SOLANA_AVAILABLE or not self.keypair:
            return {
                "status": "failed",
                "error": "Solana libraries not available"
            }
        
        # Find Raydium pool
        print("   Finding Raydium pool...")
        pool = self.find_raydium_pool(token_address)
        
        if not pool:
            print("   ❌ No Raydium pool found")
            return {
                "status": "failed",
                "error": "No Raydium pool for this token"
            }
        
        print(f"   ✅ Pool found: {pool['amm_id'][:20]}...")
        print(f"      Token reserve: {pool['coin_amount']}")
        print(f"      SOL reserve: {pool['pc_amount']}")
        
        # Calculate expected output
        print("   Calculating swap...")
        expected_sol, price_impact = self.calculate_swap_amounts(pool, amount_tokens, token_decimals)
        
        print(f"   ✅ Expected: ~{expected_sol:.6f} SOL")
        print(f"      Price impact: {price_impact:.2f}%")
        
        if price_impact > 5:
            print(f"   ⚠️ High price impact ({price_impact:.1f}%) - may fail")
        
        # NOTE: Building the actual Raydium swap transaction requires:
        # - Raydium AMM instruction layout
        # - Associated token account handling
        # - Proper account metas
        
        # For now, provide manual fallback with pool info
        print("   ⚠️ Raydium direct requires additional implementation")
        print("   🔗 Use Jupiter (which routes through Raydium)")
        
        return {
            "status": "manual_required",
            "message": "Raydium direct requires additional implementation",
            "manual_url": f"https://raydium.io/swap/?inputCurrency={token_address}&outputCurrency=SOL",
            "pool_id": pool['amm_id'],
            "expected_sol": expected_sol,
            "price_impact": price_impact
        }


def execute_sell_raydium(wallet: str, token_address: str, amount_tokens: float,
                         token_symbol: str = "UNKNOWN", token_decimals: int = 9) -> Dict:
    """Execute sell on Raydium"""
    executor = RaydiumExecutor(wallet)
    return executor.execute_sell_raydium(token_address, amount_tokens, token_symbol, token_decimals)


if __name__ == "__main__":
    wallet = "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
    token = "6TyK5BiBRJPdU4o1naDaNb54kR9nF4wk7nwu6iUFpump"
    
    result = execute_sell_raydium(wallet, token, 6366.49, "PUMP")
    print(f"\nResult: {json.dumps(result, indent=2)}")
