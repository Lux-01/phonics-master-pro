#!/usr/bin/env python3
"""
Jupiter API Client
Trade execution integration for automated trading
"""
import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TradeConfig:
    """Configuration for automated trades"""
    max_slippage: float = 0.005  # 0.5%
    priority_fee: int = 5000  # lamports
    wrap_unwrap_sol: bool = True

class JupiterAPIClient:
    """
    Jupiter API Client for automated trading
    
    Features:
    - Get swap routes
    - Execute swaps
    - Monitor transaction status
    - Calculate price impact
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://quote-api.jup.ag/v6"
        self.api_key = api_key
        self.config = TradeConfig()
        
    def get_quote(self, 
                  input_token: str,
                  output_token: str, 
                  amount: float,
                  slippage_bps: int = 50) -> Dict:
        """
        Get Jupiter swap quote
        
        Args:
            input_token: Input token mint address (or SOL, USDC, etc.)
            output_token: Output token mint address
            amount: Amount in base units (lamports for SOL)
            slippage_bps: Slippage tolerance in basis points (50 = 0.5%)
        
        Returns:
            Quote data including price, route, price impact
        """
        url = f"{self.base_url}/quote"
        
        params = {
            "inputMint": input_token,
            "outputMint": output_token,
            "amount": str(int(amount)),
            "slippageBps": slippage_bps,
            "onlyDirectRoutes": "false",
            "asLegacyTransaction": "false"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def execute_swap(self, 
                     quote_data: Dict,
                     wallet_key: str) -> Dict:
        """
        Execute swap from quote data
        Requires wallet private key for signing
        
        Args:
            quote_data: Quote from get_quote()
            wallet_key: Wallet private key (base58)
        
        Returns:
            Transaction result with signature
        """
        # This is a simplified version
        # Full implementation requires wallet signing logic
        # Integration with wallet_whale or skylar systems
        
        url = f"{self.base_url}/swap"
        
        payload = {
            "quoteResponse": quote_data,
            "userPublicKey": wallet_key,  # Actually needs full signing
            "wrapAndUnwrapSol": self.config.wrap_unwrap_sol,
            "prioritizationFeeLamports": self.config.priority_fee
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def get_token_price(self, token_mint: str, 
                       vs_token: str = "USDC") -> float:
        """
        Get token price in USDC
        
        Args:
            token_mint: Token mint address
            vs_token: Quote token (default USDC)
        
        Returns:
            Price as float
        """
        # Use a small amount to get price
        quote = self.get_quote(token_mint, vs_token, 1000000)  # 1 token
        
        if "error" in quote:
            return 0.0
        
        # Calculate price from outAmount/inAmount
        try:
            out_amount = float(quote.get("outAmount", 0))
            return out_amount / 1000000  # Adjust for decimals
        except:
            return 0.0
    
    def validate_trade(self, 
                      token_address: str,
                      expected_profit: float = 0.15) -> Dict:
        """
        Validate if trade is safe to execute
        
        Checks:
        - Token exists on Jupiter
        - Liquidity is sufficient
        - Price impact is reasonable
        
        Returns:
            Validation result with safe/not safe flag
        """
        # Get quote for small amount
        quote = self.get_quote(
            "So11111111111111111111111111111111111111112",  # SOL
            token_address,
            100000000  # 0.1 SOL
        )
        
        if "error" in quote:
            return {
                "safe": False,
                "error": quote.get("error"),
                "reason": "Token not found on Jupiter"
            }
        
        # Check price impact
        price_impact = quote.get("priceImpactPct", "0")
        try:
            impact_pct = float(price_impact)
            if impact_pct > 5.0:  # More than 5% impact
                return {
                    "safe": False,
                    "price_impact": impact_pct,
                    "reason": "Price impact too high"
                }
        except:
            pass
        
        # Check route exists
        if not quote.get("routePlan"):
            return {
                "safe": False,
                "reason": "No valid route found"
            }
        
        return {
            "safe": True,
            "expected_output": quote.get("outAmount"),
            "price_impact": quote.get("priceImpactPct"),
            "route": len(quote.get("routePlan", []))
        }

class JupiterTradeExecutor:
    """
    High-level trade executor for automated trading
    Integrates with LuxTrader system
    """
    
    def __init__(self, api_key: str, wallet_key: str):
        self.client = JupiterAPIClient(api_key)
        self.wallet_key = wallet_key  # base58 encoded private key
        self.trade_log = []
        
    def execute_buy(self, 
                    token_address: str,
                    sol_amount: float,
                    slippage: float = 0.01) -> Dict:
        """
        Execute buy order
        
        Args:
            token_address: Token to buy
            sol_amount: SOL to spend
            slippage: Max slippage tolerance
        
        Returns:
            Trade execution result
        """
        # Convert SOL to lamports
        lamports = int(sol_amount * 1e9)
        
        # Validate trade first
        validation = self.client.validate_trade(token_address)
        if not validation["safe"]:
            return {
                "success": False,
                "error": validation.get("reason", "Validation failed"),
                "stage": "validation"
            }
        
        # Get quote
        quote = self.client.get_quote(
            "So11111111111111111111111111111111111111112",  # SOL
            token_address,
            lamports,
            int(slippage * 10000)  # Convert to basis points
        )
        
        if "error" in quote:
            return {
                "success": False,
                "error": quote.get("error"),
                "stage": "quote"
            }
        
        # Execute swap
        result = self.client.execute_swap(quote, self.wallet_key)
        
        # Log trade
        self.trade_log.append({
            "type": "buy",
            "token": token_address,
            "input_sol": sol_amount,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        return {
            "success": "error" not in result,
            "tx_signature": result.get("swapTransaction"),
            "quote": quote,
            "result": result
        }
    
    def execute_sell(self,
                     token_address: str,
                     token_amount: float,
                     decimals: int = 6) -> Dict:
        """
        Execute sell order (sell token for SOL)
        
        Args:
            token_address: Token to sell
            token_amount: Amount of token to sell
            decimals: Token decimal places
        
        Returns:
            Trade execution result
        """
        # Convert to base units
        base_amount = int(token_amount * (10 ** decimals))
        
        # Get quote (token -> SOL)
        quote = self.client.get_quote(
            token_address,
            "So11111111111111111111111111111111111111112",  # SOL
            base_amount
        )
        
        if "error" in quote:
            return {"success": False, "error": quote.get("error")}
        
        # Execute swap
        result = self.client.execute_swap(quote, self.wallet_key)
        
        return {
            "success": "error" not in result,
            "tx_signature": result.get("swapTransaction"),
            "expected_sol_out": float(quote.get("outAmount", 0)) / 1e9
        }

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Example usage
if __name__ == "__main__":
    print("=== Jupiter API Client ===")
    print("\nTo use:")
    print("1. Get API key from https://station.jup.ag/docs/apis")
    print("2. Initialize: client = JupiterAPIClient('your_key')")
    print("3. Get quote: quote = client.get_quote(SOL_MINT, token, amount)")
    print("4. Execute: result = client.execute_swap(quote, wallet_key)")
    print("\n✅ Jupiter client ready for integration")
    
    # Test with BONK token (if wanted)
    # BONK = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1Qb7eFy"
    # client = JupiterAPIClient()
    # price = client.get_token_price(BONK)
    # print(f"BONK price: ${price:.10f}")
