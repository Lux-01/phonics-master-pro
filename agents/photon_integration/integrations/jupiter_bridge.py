#!/usr/bin/env python3
"""
Jupiter Bridge - Fallback Execution for Photon Integration

Provides backup trade execution when:
- Photon API is unavailable
- Photon wallet not connected
- Rate limits hit
- Manual override needed

Integrates with existing Jupiter API client
"""
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/apis')

import logging
from typing import Dict, Optional, Callable
from datetime import datetime

# Import existing Jupiter client
from jupiter_client import JupiterAPIClient, JupiterTradeExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JupiterBridge:
    """
    Jupiter Execution Bridge - Fallback to Jupiter DEX aggregator
    
    Features:
    - Swap execution when Photon unavailable
    - Route optimization
    - Slippage protection
    - Transaction status monitoring
    - Manual execution mode
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 wallet_key: Optional[str] = None):
        """
        Initialize Jupiter bridge
        
        Args:
            api_key: Jupiter API key (optional, has free tier)
            wallet_key: Base58 encoded private key for signing
        """
        self.client = JupiterAPIClient(api_key)
        self.wallet_key = wallet_key
        self.executor = None
        
        if wallet_key:
            self.executor = JupiterTradeExecutor(api_key or "", wallet_key)
        
        # Metrics
        self.successful_swaps = 0
        self.failed_swaps = 0
        self.fallback_activations = 0
        
        logger.info("✅ Jupiter Bridge initialized")
        if not wallet_key:
            logger.warning("⚠️ No wallet key provided - manual mode only")
    
    def is_connected(self) -> bool:
        """Check if bridge has wallet for execution"""
        return self.executor is not None
    
    def execute_fallback_sell(self,
                             token_address: str,
                             token_symbol: str,
                             quantity: float,
                             decimals: int = 6,
                             slippage: float = 0.01,
                             reason: str = "photon_fallback") -> Dict:
        """
        Execute sell via Jupiter when Photon fails
        
        Args:
            token_address: Token to sell
            token_symbol: Token symbol (for logging)
            quantity: Amount to sell
            decimals: Token decimal places
            slippage: Max slippage (1% default)
            reason: Why fallback was used
        
        Returns:
            Execution result
        """
        self.fallback_activations += 1
        
        logger.warning(f"🔄 FALLBACK ACTIVATED: Selling {token_symbol} via Jupiter")
        logger.info(f"   Reason: {reason}")
        logger.info(f"   Quantity: {quantity:.4f}")
        
        if not self.executor:
            return {
                "success": False,
                "error": "No wallet connected - manual execution required",
                "fallback": True,
                "token_symbol": token_symbol,
                "suggested_action": "Manual sell via Photon/Jupiter UI"
            }
        
        try:
            # Execute via Jupiter
            result = self.executor.execute_sell(
                token_address=token_address,
                token_amount=quantity,
                decimals=decimals
            )
            
            if result.get("success"):
                self.successful_swaps += 1
                logger.info(f"✅ Jupiter sell executed: {token_symbol}")
                
                return {
                    "success": True,
                    "tx_signature": result.get("tx_signature"),
                    "fallback": True,
                    "via": "jupiter",
                    "token": token_symbol,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                self.failed_swaps += 1
                logger.error(f"❌ Jupiter sell failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error"),
                    "fallback": True,
                    "via": "jupiter",
                    "token": token_symbol
                }
        
        except Exception as e:
            self.failed_swaps += 1
            logger.error(f"❌ Jupiter execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True,
                "via": "jupiter"
            }
    
    def validate_token(self, token_address: str) -> Dict:
        """
        Validate token can be traded on Jupiter
        
        Args:
            token_address: Token mint
        
        Returns:
            Validation result
        """
        validation = self.client.validate_trade(token_address)
        
        if validation.get("safe"):
            logger.info(f"✅ Token validated on Jupiter")
            return {
                "tradable": True,
                "price_impact": validation.get("price_impact", "unknown"),
                "route_length": validation.get("route", 0)
            }
        else:
            logger.warning(f"⚠️ Token validation failed: {validation.get('reason')}")
            return {
                "tradable": False,
                "reason": validation.get("reason", "unknown")
            }
    
    def get_token_price(self, token_address: str) -> float:
        """
        Get token price from Jupiter
        
        Args:
            token_address: Token mint
        
        Returns:
            Price in USDC
        """
        try:
            price = self.client.get_token_price(token_address)
            return price
        except Exception as e:
            logger.error(f"❌ Price fetch failed: {e}")
            return 0.0
    
    def calculate_receive_amount(self,
                                token_address: str,
                                quantity: float,
                                decimals: int = 6) -> Dict:
        """
        Calculate expected SOL received for a sell
        
        Args:
            token_address: Token to sell
            quantity: Amount of token
            decimals: Token decimals
        
        Returns:
            Expected SOL amount
        """
        try:
            base_amount = int(quantity * (10 ** decimals))
            
            quote = self.client.get_quote(
                input_token=token_address,
                output_token="So11111111111111111111111111111111111111112",
                amount=base_amount
            )
            
            if "error" in quote:
                return {
                    "success": False,
                    "error": quote.get("error")
                }
            
            out_lamports = int(quote.get("outAmount", 0))
            sol_amount = out_lamports / 1e9
            
            # Account for fees
            fee_pct = 0.005  # 0.5%
            sol_after_fees = sol_amount * (1 - fee_pct)
            
            return {
                "success": True,
                "expected_sol": sol_amount,
                "after_fees": sol_after_fees,
                "price_impact": quote.get("priceImpactPct", "0"),
                "route": len(quote.get("routePlan", []))
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_health(self) -> Dict:
        """
        Check Jupiter API health
        
        Returns:
            Health status
        """
        try:
            # Try to get SOL price as health check
            price = self.client.get_token_price(
                "So11111111111111111111111111111111111111112"
            )
            
            healthy = price > 0
            
            return {
                "healthy": healthy,
                "sol_price": price,
                "wallet_connected": self.is_connected(),
                "api_key_set": self.client.api_key is not None,
                "status": "operational" if healthy else "degraded"
            }
        
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "status": "offline"
            }
    
    def get_stats(self) -> Dict:
        """Get bridge statistics"""
        return {
            "mode": "auto" if self.is_connected() else "manual",
            "successful_swaps": self.successful_swaps,
            "failed_swaps": self.failed_swaps,
            "fallback_activations": self.fallback_activations,
            "success_rate": self.successful_swaps / (self.successful_swaps + self.failed_swaps) * 100 if (self.successful_swaps + self.failed_swaps) > 0 else 0
        }


class FallbackRouter:
    """
    Smart routing between Photon and Jupiter
    
    Priority:
    1. Photon (fastest, preferred)
    2. Jupiter (fallback if Photon fails)
    3. Manual (if all else fails)
    """
    
    def __init__(self, 
                 photon_client=None,
                 jupiter_bridge: Optional[JupiterBridge] = None):
        self.photon = photon_client
        self.jupiter = jupiter_bridge
        self.manual_queue = []
        
    def execute_sell(self,
                    token_address: str,
                    token_symbol: str,
                    quantity: float,
                    reason: str) -> Dict:
        """
        Route sell execution to available platform
        
        Args:
            token_address: Token mint
            token_symbol: Token symbol
            quantity: Amount to sell
            reason: Sell trigger reason
        
        Returns:
            Execution result from chosen platform
        """
        # Try Photon first
        if self.photon and self.photon.is_connected():
            try:
                result = self.photon.execute_market_sell(
                    token_address=token_address,
                    token_symbol=token_symbol,
                    quantity=quantity
                )
                if result.get("success"):
                    result["via"] = "photon"
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Photon failed: {e}, trying Jupiter...")
        
        # Fallback to Jupiter
        if self.jupiter:
            result = self.jupiter.execute_fallback_sell(
                token_address=token_address,
                token_symbol=token_symbol,
                quantity=quantity,
                reason=f"photon_failed:{reason}"
            )
            if result.get("success"):
                return result
        
        # Manual fallback
        logger.critical(f"🚨 MANUAL SELL REQUIRED: {token_symbol}")
        self.manual_queue.append({
            "token": token_symbol,
            "address": token_address,
            "quantity": quantity,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": False,
            "manual_required": True,
            "token": token_symbol,
            "quantity": quantity,
            "reason": reason,
            "alert": "URGENT: Manual sell required"
        }
    
    def get_manual_queue(self) -> List[Dict]:
        """Get queued manual sells"""
        return self.manual_queue


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🪐 Jupiter Bridge - Fallback Execution")
    print("=" * 60)
    
    # Initialize (without wallet for demo)
    bridge = JupiterBridge()
    
    print("\n📋 Available Features:")
    print("  • execute_fallback_sell() - Emergency sell via Jupiter")
    print("  • validate_token() - Check tradability")
    print("  • calculate_receive_amount() - Preview sell")
    print("  • check_health() - API status")
    
    print("\n⚡ Execution Priority:")
    print("  1. Photon (primary)")
    print("  2. Jupiter (fallback)")
    print("  3. Manual (last resort)")
    
    # Health check
    health = bridge.check_health()
    print(f"\n🔍 Health Check:")
    print(f"   Status: {health.get('status', 'unknown').upper()}")
    print(f"   SOL Price: ${health.get('sol_price', 0):.2f}")
    print(f"   Wallet: {'✅' if health.get('wallet_connected') else '❌'}")
    
    print("\n✅ Jupiter Bridge ready for fallback execution")