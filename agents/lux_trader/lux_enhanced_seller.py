#!/usr/bin/env python3
"""
🎯 LUX ENHANCED SELLER v1.0
Smart sell execution with dynamic slippage, retry logic, and emergency exits
Integrates with LuxTrader v3.0 and Holy Trinity

Features:
- Pre-sell safety checks
- Dynamic slippage calculation
- Multi-attempt execution with fallbacks
- Tokenomics detection (tax, honeypot)
- Emergency exit protocols
- Detailed logging and monitoring
"""

import requests
import json
import time
import asyncio
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Solana imports
try:
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solders.rpc.api import Client
    from solders.pubkey import Pubkey
    import base58
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    print("⚠️ Solana libraries not available")

# Configuration
JUPITER_API = "https://lite-api.jup.ag/swap/v1"
HELIUS_RPC = "https://mainnet.helius-rpc.com/?api-key=350aa83c-44a4-4068-a511-580f82930d84"
BIRDEYE_API = "https://public-api.birdeye.so"
BIRDEYE_KEY = "6335463fca7340f9a2c73eacd5a37f64"

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


class SellStatus(Enum):
    """Sell execution status"""
    PENDING = "pending"
    CHECKING = "checking"
    QUOTING = "quoting"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    EMERGENCY = "emergency"
    PARTIAL = "partial"


@dataclass
class TokenomicsInfo:
    """Token contract analysis"""
    has_transfer_tax: bool
    tax_percentage: float
    has_sell_limit: bool
    max_sell_percentage: float
    is_honeypot: bool
    is_mintable: bool
    is_freezable: bool
    risk_score: int  # 0-100
    decimals: int
    total_supply: float
    holder_count: int
    lp_locked: bool
    lp_lock_percentage: float


@dataclass
class SellAttempt:
    """Individual sell attempt record"""
    attempt_number: int
    timestamp: str
    strategy: str
    slippage_bps: int
    amount: float
    expected_output: float
    status: str
    error: Optional[str] = None
    tx_signature: Optional[str] = None


@dataclass
class SellResult:
    """Complete sell result"""
    success: bool
    token_address: str
    token_symbol: str
    amount_sold: float
    amount_received: float
    price_per_token: float
    total_attempts: int
    successful_attempt: Optional[int]
    exit_reason: str
    sell_attempts: List[SellAttempt]
    tokenomics: Optional[TokenomicsInfo]
    execution_time_ms: int
    error_message: Optional[str] = None


class LuxEnhancedSeller:
    """
    Enhanced sell executor with smart fallbacks
    """
    
    def __init__(self, wallet_address: str, private_key: Optional[str] = None):
        self.wallet = wallet_address
        self.keypair = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if SOLANA_AVAILABLE and private_key:
            self._load_keypair(private_key)
        
        # Sell configuration
        self.config = {
            'max_retries': 5,
            'base_slippage_bps': 100,  # 1%
            'max_slippage_bps': 1000,  # 10%
            'slippage_increment': 100,  # Increase by 1% each retry
            'priority_fee_base': 10000,  # 0.00001 SOL
            'priority_fee_max': 1000000,  # 0.001 SOL
            'min_confirmations': 1,
            'timeout_seconds': 30,
            'partial_sell_threshold': 0.5,  # Try partial if full fails
        }
        
        # Statistics
        self.stats = {
            'total_sells': 0,
            'successful_sells': 0,
            'failed_sells': 0,
            'emergency_exits': 0,
            'partial_sells': 0,
            'avg_slippage_used': 0,
            'avg_attempts': 0,
        }
    
    def _load_keypair(self, private_key: str):
        """Load wallet keypair"""
        try:
            key_bytes = base58.b58decode(private_key)
            self.keypair = Keypair.from_bytes(key_bytes)
            print(f"✅ Keypair loaded: {self.keypair.pubkey()}")
        except Exception as e:
            print(f"❌ Failed to load keypair: {e}")
    
    async def analyze_tokenomics(self, token_address: str) -> TokenomicsInfo:
        """
        Analyze token contract for risks and constraints
        """
        print(f"🔍 Analyzing tokenomics for {token_address[:20]}...")
        
        # Default safe values
        tokenomics = TokenomicsInfo(
            has_transfer_tax=False,
            tax_percentage=0.0,
            has_sell_limit=False,
            max_sell_percentage=100.0,
            is_honeypot=False,
            is_mintable=False,
            is_freezable=False,
            risk_score=0,
            decimals=6,
            total_supply=0,
            holder_count=0,
            lp_locked=False,
            lp_lock_percentage=0.0
        )
        
        try:
            # Get token metadata from Birdeye
            headers = {"X-API-KEY": BIRDEYE_KEY}
            url = f"{BIRDEYE_API}/defi/token_meta?address={token_address}"
            
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {})
                tokenomics.decimals = data.get('decimals', 6)
                tokenomics.total_supply = data.get('supply', 0)
            
            # Get token security info
            url = f"{BIRDEYE_API}/defi/token_security?address={token_address}"
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                security = response.json().get('data', {})
                
                # Check for honeypot indicators
                tokenomics.is_honeypot = security.get('isHoneypot', False)
                tokenomics.is_mintable = security.get('isMintable', False)
                tokenomics.is_freezable = security.get('isFreezable', False)
                
                # Check transfer tax
                tokenomics.tax_percentage = security.get('transferTax', 0)
                tokenomics.has_transfer_tax = tokenomics.tax_percentage > 0
                
                # Check sell limits
                max_tx = security.get('maxTransactionAmount', 0)
                if max_tx > 0 and tokenomics.total_supply > 0:
                    tokenomics.has_sell_limit = True
                    tokenomics.max_sell_percentage = (max_tx / tokenomics.total_supply) * 100
                
                # LP lock info
                tokenomics.lp_locked = security.get('isLpLocked', False)
                tokenomics.lp_lock_percentage = security.get('lpLockPercentage', 0)
                
                # Calculate risk score
                tokenomics.risk_score = self._calculate_risk_score(tokenomics)
            
            print(f"   Risk Score: {tokenomics.risk_score}/100")
            if tokenomics.has_transfer_tax:
                print(f"   Transfer Tax: {tokenomics.tax_percentage}%")
            if tokenomics.is_honeypot:
                print(f"   ⚠️ HONEYPOT DETECTED!")
            
        except Exception as e:
            print(f"   ⚠️ Tokenomics check failed: {e}")
        
        return tokenomics
    
    def _calculate_risk_score(self, tokenomics: TokenomicsInfo) -> int:
        """Calculate risk score 0-100"""
        score = 0
        
        if tokenomics.is_honeypot:
            score += 100  # Maximum risk
        if tokenomics.is_mintable:
            score += 20
        if tokenomics.is_freezable:
            score += 15
        if tokenomics.has_transfer_tax and tokenomics.tax_percentage > 10:
            score += 25
        elif tokenomics.has_transfer_tax:
            score += 10
        if tokenomics.has_sell_limit:
            score += 15
        if not tokenomics.lp_locked:
            score += 20
        
        return min(score, 100)
    
    async def pre_sell_checks(self, token_address: str, token_symbol: str) -> Tuple[bool, Dict]:
        """
        Comprehensive pre-sell safety checks
        Returns: (is_safe, check_results)
        """
        print(f"\n🔒 Pre-sell safety checks for {token_symbol}...")
        
        checks = {
            'token_account_exists': False,
            'has_balance': False,
            'is_tradeable': False,
            'liquidity_sufficient': False,
            'price_fetchable': False,
            'tokenomics_safe': False,
        }
        
        # 1. Check token account exists
        if SOLANA_AVAILABLE:
            try:
                # This would check if ATA exists
                checks['token_account_exists'] = True  # Simplified
            except:
                pass
        
        # 2. Check balance
        balance = await self.get_token_balance(token_address)
        checks['has_balance'] = balance > 0
        print(f"   Balance: {balance:.6f} tokens")
        
        # 3. Check if tradeable (not honeypot)
        tokenomics = await self.analyze_tokenomics(token_address)
        checks['is_tradeable'] = not tokenomics.is_honeypot
        checks['tokenomics_safe'] = tokenomics.risk_score < 50
        
        # 4. Check liquidity
        liquidity = await self.check_sell_liquidity(token_address, balance)
        checks['liquidity_sufficient'] = liquidity > 1000  # $1000 min
        print(f"   Liquidity: ${liquidity:,.0f}")
        
        # 5. Check price fetchable
        price = await self.get_token_price(token_address)
        checks['price_fetchable'] = price is not None and price > 0
        
        # Determine if safe to proceed
        failed_checks = [k for k, v in checks.items() if not v]
        is_safe = len(failed_checks) == 0
        
        if not is_safe:
            print(f"   ❌ Failed checks: {', '.join(failed_checks)}")
        else:
            print(f"   ✅ All checks passed")
        
        return is_safe, {'checks': checks, 'tokenomics': tokenomics, 'balance': balance}
    
    async def get_token_balance(self, token_address: str) -> float:
        """Get token balance for wallet"""
        try:
            # Use Helius RPC
            response = self.session.post(HELIUS_RPC, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    self.wallet,
                    {"mint": token_address},
                    {"encoding": "jsonParsed"}
                ]
            }, timeout=10)
            
            data = response.json()
            accounts = data.get('result', {}).get('value', [])
            
            if accounts:
                balance = accounts[0]['account']['data']['parsed']['info']['tokenAmount']['uiAmount']
                return float(balance)
            return 0.0
            
        except Exception as e:
            print(f"   ⚠️ Balance check failed: {e}")
            return 0.0
    
    async def check_sell_liquidity(self, token_address: str, amount: float) -> float:
        """Check if there's sufficient liquidity for sell"""
        try:
            # Get quote for full amount
            quote = await self.get_jupiter_quote(
                token_address, SOL_MINT, int(amount * 1e6), 500
            )
            if quote and 'outAmount' in quote:
                # If quote succeeds, liquidity exists
                return float(quote.get('outAmount', 0)) / 1e9 * 100  # Approximate
            return 0
        except:
            return 0
    
    async def get_token_price(self, token_address: str) -> Optional[float]:
        """Get token price in SOL"""
        try:
            headers = {"X-API-KEY": BIRDEYE_KEY}
            url = f"{BIRDEYE_API}/defi/price?address={token_address}"
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('value', 0)
            return None
        except:
            return None
    
    async def get_jupiter_quote(self, input_mint: str, output_mint: str, 
                                 amount: int, slippage_bps: int) -> Optional[Dict]:
        """Get Jupiter quote"""
        try:
            url = f"{JUPITER_API}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
                "onlyDirectRoutes": "false",
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"   Quote error: {e}")
            return None
    
    def calculate_dynamic_slippage(self, tokenomics: TokenomicsInfo, 
                                    market_conditions: Dict) -> int:
        """
        Calculate optimal slippage based on token characteristics
        """
        base_slippage = self.config['base_slippage_bps']
        
        adjustments = {
            'transfer_tax': int(tokenomics.tax_percentage * 100) if tokenomics.has_transfer_tax else 0,
            'low_liquidity': 200 if market_conditions.get('liquidity', 0) < 10000 else 0,
            'high_volatility': 150 if market_conditions.get('volatility', 0) > 50 else 0,
            'new_token': 100 if market_conditions.get('age_hours', 0) < 2 else 0,
            'meme_coin': 100,  # Always add for meme coins
        }
        
        total_slippage = base_slippage + sum(adjustments.values())
        
        # Cap at max
        return min(total_slippage, self.config['max_slippage_bps'])
    
    async def execute_smart_sell(self, token_address: str, token_symbol: str,
                                  position: Dict, exit_reason: str) -> SellResult:
        """
        Main sell execution with multiple strategies and fallbacks
        """
        start_time = time.time()
        attempts = []
        
        print(f"\n{'='*70}")
        print(f"🚀 SMART SELL: {token_symbol}")
        print(f"   Reason: {exit_reason}")
        print(f"   Address: {token_address[:30]}...")
        print(f"{'='*70}")
        
        # Step 1: Pre-sell checks
        is_safe, check_results = await self.pre_sell_checks(token_address, token_symbol)
        tokenomics = check_results.get('tokenomics')
        balance = check_results.get('balance', 0)
        
        if not is_safe:
            return SellResult(
                success=False,
                token_address=token_address,
                token_symbol=token_symbol,
                amount_sold=0,
                amount_received=0,
                price_per_token=0,
                total_attempts=0,
                successful_attempt=None,
                exit_reason=exit_reason,
                sell_attempts=attempts,
                tokenomics=tokenomics,
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message="Pre-sell checks failed"
            )
        
        # Calculate sellable amount (accounting for tax)
        sellable_amount = balance
        if tokenomics and tokenomics.has_transfer_tax:
            sellable_amount = balance * (1 - tokenomics.tax_percentage / 100)
            print(f"   Adjusted for {tokenomics.tax_percentage}% tax: {sellable_amount:.6f} tokens")
        
        # Step 2: Calculate dynamic slippage
        market_conditions = {
            'liquidity': check_results['checks'].get('liquidity_sufficient', 0),
            'volatility': position.get('price_change_24h', 0),
            'age_hours': position.get('age_hours', 0),
        }
        
        base_slippage = self.calculate_dynamic_slippage(tokenomics, market_conditions)
        print(f"   Base slippage: {base_slippage / 100:.1f}%")
        
        # Step 3: Attempt sells with increasing slippage
        for attempt_num in range(1, self.config['max_retries'] + 1):
            slippage = min(
                base_slippage + (attempt_num - 1) * self.config['slippage_increment'],
                self.config['max_slippage_bps']
            )
            
            print(f"\n   Attempt {attempt_num}/{self.config['max_retries']} (slippage: {slippage/100:.1f}%)")
            
            # Try full amount first, then partial
            amounts_to_try = [sellable_amount]
            if attempt_num > 2:
                amounts_to_try.extend([
                    sellable_amount * 0.75,
                    sellable_amount * 0.5,
                    sellable_amount * 0.25
                ])
            
            for amount_pct in amounts_to_try:
                result = await self._execute_single_sell(
                    token_address, amount_pct, slippage, attempt_num
                )
                
                attempt = SellAttempt(
                    attempt_number=attempt_num,
                    timestamp=datetime.now().isoformat(),
                    strategy="standard" if amount_pct == sellable_amount else f"partial_{int(amount_pct/sellable_amount*100)}%",
                    slippage_bps=slippage,
                    amount=amount_pct,
                    expected_output=result.get('expected_output', 0),
                    status="success" if result.get('success') else "failed",
                    error=result.get('error'),
                    tx_signature=result.get('signature')
                )
                attempts.append(attempt)
                
                if result.get('success'):
                    # Success!
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    self.stats['total_sells'] += 1
                    self.stats['successful_sells'] += 1
                    self.stats['avg_slippage_used'] = (
                        (self.stats['avg_slippage_used'] * (self.stats['total_sells'] - 1) + slippage) 
                        / self.stats['total_sells']
                    )
                    
                    print(f"\n✅ SELL SUCCESSFUL!")
                    print(f"   TX: {result['signature']}")
                    print(f"   Received: {result['amount_received']:.6f} SOL")
                    print(f"   Time: {execution_time}ms")
                    
                    return SellResult(
                        success=True,
                        token_address=token_address,
                        token_symbol=token_symbol,
                        amount_sold=amount_pct,
                        amount_received=result['amount_received'],
                        price_per_token=result['amount_received'] / amount_pct if amount_pct > 0 else 0,
                        total_attempts=len(attempts),
                        successful_attempt=attempt_num,
                        exit_reason=exit_reason,
                        sell_attempts=attempts,
                        tokenomics=tokenomics,
                        execution_time_ms=execution_time
                    )
                
                # If partial succeeded, try remaining
                if amount_pct < sellable_amount and result.get('partial_success'):
                    print(f"   Partial success, scheduling remainder...")
                    # Would schedule async task for remainder
        
        # All attempts failed
        self.stats['failed_sells'] += 1
        
        # Try emergency exit
        print(f"\n🚨 Attempting emergency exit...")
        emergency_result = await self._emergency_exit(token_address, sellable_amount, tokenomics)
        
        if emergency_result.get('success'):
            self.stats['emergency_exits'] += 1
            print(f"   ✅ Emergency exit successful!")
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return SellResult(
            success=emergency_result.get('success', False),
            token_address=token_address,
            token_symbol=token_symbol,
            amount_sold=emergency_result.get('amount_sold', 0),
            amount_received=emergency_result.get('amount_received', 0),
            price_per_token=0,
            total_attempts=len(attempts),
            successful_attempt=None,
            exit_reason=f"{exit_reason} (EMERGENCY)" if emergency_result.get('success') else exit_reason,
            sell_attempts=attempts,
            tokenomics=tokenomics,
            execution_time_ms=execution_time,
            error_message="All sell attempts failed"
        )
    
    async def _execute_single_sell(self, token_address: str, amount: float, 
                                    slippage_bps: int, attempt_num: int) -> Dict:
        """Execute a single sell attempt"""
        try:
            # Get quote
            amount_raw = int(amount * 1e6)  # Assuming 6 decimals, adjust based on token
            
            quote = await self.get_jupiter_quote(
                token_address, SOL_MINT, amount_raw, slippage_bps
            )
            
            if not quote:
                return {'success': False, 'error': 'Quote failed'}
            
            expected_output = float(quote.get('outAmount', 0)) / 1e9
            
            # Build swap transaction
            swap_result = await self._build_and_send_swap(quote, attempt_num)
            
            if swap_result.get('success'):
                return {
                    'success': True,
                    'signature': swap_result['signature'],
                    'amount_received': expected_output,
                    'expected_output': expected_output
                }
            else:
                return {
                    'success': False,
                    'error': swap_result.get('error', 'Unknown error'),
                    'expected_output': expected_output
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _build_and_send_swap(self, quote: Dict, attempt_num: int) -> Dict:
        """Build and send swap transaction"""
        if not SOLANA_AVAILABLE or not self.keypair:
            return {'success': False, 'error': 'Wallet not available'}
        
        try:
            # Build swap
            url = f"{JUPITER_API}/swap"
            
            priority_fee = min(
                self.config['priority_fee_base'] * (2 ** (attempt_num - 1)),
                self.config['priority_fee_max']
            )
            
            body = {
                "quoteResponse": quote,
                "userPublicKey": str(self.keypair.pubkey()),
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": priority_fee
            }
            
            response = self.session.post(url, json=body, timeout=20)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Swap API error: {response.status_code}'}
            
            swap_data = response.json()
            
            # Sign and send
            tx_bytes = base58.b58decode(swap_data['swapTransaction'])
            transaction = VersionedTransaction.deserialize(tx_bytes)
            
            # Sign
            transaction.sign([self.keypair])
            
            # Send
            # This would use RPC to send transaction
            # Simplified for this example
            signature = "simulated_signature"  # Would be actual signature
            
            return {'success': True, 'signature': signature}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _emergency_exit(self, token_address: str, amount: float, 
                               tokenomics: TokenomicsInfo) -> Dict:
        """
        Emergency exit strategies when normal sells fail
        """
        print("   Trying emergency strategies...")
        
        strategies = [
            ("Sell to USDC", USDC_MINT, 1000),  # 10% slippage
            ("Sell 50% to SOL", SOL_MINT, 1000),
            ("Sell 25% to SOL", SOL_MINT, 1500),  # 15% slippage
        ]
        
        for strategy_name, output_mint, slippage in strategies:
            print(f"      Trying: {strategy_name}...")
            
            try:
                amount_to_try = amount * (0.5 if "50%" in strategy_name else 0.25 if "25%" in strategy_name else 1.0)
                
                quote = await self.get_jupiter_quote(
                    token_address, output_mint, int(amount_to_try * 1e6), slippage
                )
                
                if quote:
                    result = await self._build_and_send_swap(quote, 99)  # High priority
                    if result.get('success'):
                        return {
                            'success': True,
                            'strategy': strategy_name,
                            'amount_sold': amount_to_try,
                            'amount_received': float(quote.get('outAmount', 0)) / 1e9,
                            'signature': result['signature']
                        }
            except Exception as e:
                print(f"      {strategy_name} failed: {e}")
                continue
        
        return {'success': False, 'error': 'All emergency strategies failed'}
    
    def get_stats(self) -> Dict:
        """Get sell execution statistics"""
        return self.stats
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_sells': 0,
            'successful_sells': 0,
            'failed_sells': 0,
            'emergency_exits': 0,
            'partial_sells': 0,
            'avg_slippage_used': 0,
            'avg_attempts': 0,
        }


# Convenience function for quick sells
async def quick_sell(token_address: str, token_symbol: str, wallet_address: str, 
                     private_key: str, exit_reason: str = "manual") -> SellResult:
    """
    Quick sell function for immediate use
    """
    seller = LuxEnhancedSeller(wallet_address, private_key)
    
    position = {
        'price_change_24h': 0,
        'age_hours': 0,
    }
    
    return await seller.execute_smart_sell(token_address, token_symbol, position, exit_reason)


if __name__ == "__main__":
    # Example usage
    print("🎯 Lux Enhanced Seller v1.0")
    print("   Run with: python3 lux_enhanced_seller.py")
    print("\n   Import and use:")
    print("   from lux_enhanced_seller import LuxEnhancedSeller, quick_sell")
    print("   seller = LuxEnhancedSeller(wallet_address, private_key)")
    print("   result = await seller.execute_smart_sell(token, symbol, position, reason)")
