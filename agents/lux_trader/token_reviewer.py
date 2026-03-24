#!/usr/bin/env python3
"""
🔍 TOKEN REVIEWER
Generates detailed pre-buy review for every trade
"""

import json
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple

JUPITER_API = "https://quote-api.jup.ag/v6"

class TokenReviewer:
    """Review token before buying"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_token_details(self, token_address: str) -> Dict:
        """Fetch token details from Jupiter"""
        try:
            # Try to get token info from Jupiter token list
            url = f"https://token.jup.ag/all"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                tokens = response.json()
                for token in tokens:
                    if token.get("address") == token_address:
                        return {
                            "symbol": token.get("symbol", "UNKNOWN"),
                            "name": token.get("name", "Unknown"),
                            "decimals": token.get("decimals", 9),
                            "verified": token.get("verified", False),
                            "tags": token.get("tags", [])
                        }
            
            return {
                "symbol": "UNKNOWN",
                "name": "Unknown Token",
                "decimals": 9,
                "verified": False,
                "tags": []
            }
        except Exception as e:
            return {
                "symbol": "UNKNOWN",
                "name": f"Error: {str(e)[:50]}",
                "decimals": 9,
                "verified": False,
                "tags": []
            }
    
    def get_jupiter_quote(self, token_address: str, amount_sol: float) -> Optional[Dict]:
        """Get Jupiter quote for review"""
        try:
            SOL_MINT = "So11111111111111111111111111111111111111112"
            amount_lamports = int(amount_sol * 1e9)
            
            url = f"{JUPITER_API}/quote"
            params = {
                "inputMint": SOL_MINT,
                "outputMint": token_address,
                "amount": str(amount_lamports),
                "slippageBps": 250
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                quote = response.json()
                return {
                    "success": True,
                    "out_amount": quote.get("outAmount"),
                    "price_impact": quote.get("priceImpactPct", "0"),
                    "route": len(quote.get("routePlan", [])),
                    "raw_quote": quote
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_risk_score(self, token_data: Dict, quote_data: Dict) -> Tuple[int, str]:
        """
        Calculate risk score (0-100, lower is better)
        Returns: (score, assessment)
        """
        score = 0
        reasons = []
        
        # Check verification
        if not token_data.get("verified", False):
            score += 30
            reasons.append("Unverified token")
        
        # Check price impact
        try:
            impact = float(quote_data.get("price_impact", "0"))
            if impact > 5:
                score += 40
                reasons.append(f"High price impact: {impact}%")
            elif impact > 2:
                score += 15
                reasons.append(f"Moderate price impact: {impact}%")
        except:
            score += 20
            reasons.append("Unknown price impact")
        
        # Check route complexity
        if quote_data.get("route", 0) > 3:
            score += 10
            reasons.append("Complex route")
        
        # Determine assessment
        if score <= 20:
            assessment = "LOW RISK"
        elif score <= 50:
            assessment = "MEDIUM RISK"
        else:
            assessment = "HIGH RISK"
        
        return score, f"{assessment} ({score}/100)"
    
    def generate_review(self, token: Dict, amount_sol: float) -> str:
        """Generate human-readable review report"""
        
        token_address = token.get("address", "")
        symbol = token.get("symbol", "UNKNOWN")
        grade = token.get("grade", "?")
        score = token.get("score", 0)
        
        # Fetch details
        details = self.fetch_token_details(token_address)
        quote = self.get_jupiter_quote(token_address, amount_sol)
        
        # Calculate risk
        if quote and quote.get("success"):
            risk_score, risk_assessment = self.calculate_risk_score(details, quote)
        else:
            risk_score = 50
            risk_assessment = "UNKNOWN (quote failed)"
        
        # Calculate expected output
        expected_tokens = "???"
        if quote and quote.get("success") and quote.get("out_amount"):
            try:
                out_amount = int(quote["out_amount"])
                decimals = details.get("decimals", 9)
                expected_tokens = f"{out_amount / (10 ** decimals):,.0f}"
            except:
                pass
        
        # Build review
        review_lines = [
            "",
            "=" * 60,
            "🎯 PRE-BUY REVIEW",
            "=" * 60,
            "",
            f"Token: {symbol}",
            f"Address: {token_address}",
            f"Name: {details.get('name', 'Unknown')}",
            "",
            f"📊 Signal Quality:",
            f"   Grade: {grade}",
            f"   Score: {score}/100",
            "",
            f"💰 Trade Details:",
            f"   Input: {amount_sol:.4f} SOL",
            f"   Expected Output: ~{expected_tokens} tokens",
        ]
        
        if quote and quote.get("success"):
            review_lines.extend([
                f"   Price Impact: {quote.get('price_impact', 'N/A')}%",
                f"   Route Hops: {quote.get('route', 'N/A')}",
            ])
        
        review_lines.extend([
            "",
            f"⚠️  Risk Assessment: {risk_assessment}",
        ])
        
        # Add risk factors
        if risk_score > 20:
            review_lines.append("   Risk Factors:")
            if not details.get("verified"):
                review_lines.append("   • Token not verified")
            if quote and float(quote.get("price_impact", "0")) > 2:
                review_lines.append(f"   • High slippage: {quote.get('price_impact')}%")
        else:
            review_lines.append("   ✓ Low risk profile")
            review_lines.append("   ✓ Token verified" if details.get("verified") else "   ⚠ Token not verified")
        
        # Add tags if any
        if details.get("tags"):
            review_lines.extend([
                "",
                f"🏷️  Tags: {', '.join(details['tags'][:3])}",
            ])
        
        review_lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(review_lines)
    
    def approve_trade(self, token: Dict, amount_sol: float) -> Tuple[bool, str]:
        """
        Auto-approve or reject trade based on review
        Returns: (approved, reason)
        """
        token_address = token.get("address", "")
        
        # Get quote for validation
        quote = self.get_jupiter_quote(token_address, amount_sol)
        
        if not quote or not quote.get("success"):
            return False, f"Cannot get quote: {quote.get('error', 'Unknown error')}"
        
        # Check price impact
        try:
            impact = float(quote.get("price_impact", "0"))
            if impact > 5:
                return False, f"Price impact too high: {impact}%"
        except:
            pass
        
        # Get token details
        details = self.fetch_token_details(token_address)
        
        # Calculate risk
        risk_score, _ = self.calculate_risk_score(details, quote)
        
        if risk_score > 70:
            return False, f"Risk score too high: {risk_score}/100"
        
        return True, "Auto-approved"


# Convenience function
def review_token(token: Dict, amount_sol: float) -> str:
    """Generate review for token"""
    reviewer = TokenReviewer()
    return reviewer.generate_review(token, amount_sol)


def approve_token(token: Dict, amount_sol: float) -> Tuple[bool, str]:
    """Auto-approve token"""
    reviewer = TokenReviewer()
    return reviewer.approve_trade(token, amount_sol)


if __name__ == "__main__":
    # Test
    test_token = {
        "symbol": "TEST",
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "grade": "A+",
        "score": 85
    }
    
    print(review_token(test_token, 0.001))
    
    approved, reason = approve_token(test_token, 0.001)
    print(f"\nApproval: {'✅' if approved else '❌'} {reason}")
