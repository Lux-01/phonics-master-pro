#!/usr/bin/env python3
"""
🔍 TOKENOMICS DETECTOR v1.0
Analyzes Solana token contracts for risks, taxes, and honeypot indicators

Features:
- Transfer tax detection
- Honeypot detection
- Sell limit analysis
- LP lock verification
- Risk scoring
- Real-time monitoring
"""

import requests
import json
import asyncio
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# APIs
BIRDEYE_API = "https://public-api.birdeye.so"
BIRDEYE_KEY = "6335463fca7340f9a2c73eacd5a37f64"
HELIUS_RPC = "https://mainnet.helius-rpc.com/?api-key=350aa83c-44a4-4068-a511-580f82930d84"
DEXSCREENER_API = "https://api.dexscreener.com/latest"


class RiskLevel(Enum):
    """Risk classification"""
    LOW = "low"           # 0-25
    MEDIUM = "medium"     # 26-50
    HIGH = "high"         # 51-75
    CRITICAL = "critical" # 76-100


@dataclass
class TokenSecurity:
    """Token security analysis"""
    address: str
    symbol: str
    name: str
    
    # Contract features
    is_mintable: bool
    is_freezable: bool
    is_honeypot: bool
    is_blacklist: bool
    is_whitelist: bool
    
    # Transfer settings
    has_transfer_tax: bool
    buy_tax: float
    sell_tax: float
    transfer_tax: float
    
    # Limits
    has_max_wallet: bool
    max_wallet_percentage: float
    has_max_transaction: bool
    max_transaction_percentage: float
    
    # LP settings
    lp_mint_address: Optional[str]
    is_lp_burned: bool
    is_lp_locked: bool
    lp_lock_duration_days: int
    lp_lock_percentage: float
    
    # Ownership
    is_ownership_renounced: bool
    owner_address: Optional[str]
    
    # Metadata
    total_supply: float
    decimals: int
    holder_count: int
    
    # Risk
    risk_score: int
    risk_level: RiskLevel
    warnings: List[str]


class TokenomicsDetector:
    """
    Advanced token contract analyzer
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-KEY': BIRDEYE_KEY
        })
        self.cache = {}  # Simple cache
    
    async def analyze_token(self, token_address: str) -> Optional[TokenSecurity]:
        """
        Comprehensive token analysis
        """
        print(f"\n🔍 Analyzing token: {token_address[:20]}...")
        
        # Check cache
        if token_address in self.cache:
            print("   Using cached data")
            return self.cache[token_address]
        
        # Initialize with defaults
        security = TokenSecurity(
            address=token_address,
            symbol="UNKNOWN",
            name="Unknown Token",
            is_mintable=False,
            is_freezable=False,
            is_honeypot=False,
            is_blacklist=False,
            is_whitelist=False,
            has_transfer_tax=False,
            buy_tax=0.0,
            sell_tax=0.0,
            transfer_tax=0.0,
            has_max_wallet=False,
            max_wallet_percentage=0.0,
            has_max_transaction=False,
            max_transaction_percentage=0.0,
            lp_mint_address=None,
            is_lp_burned=False,
            is_lp_locked=False,
            lp_lock_duration_days=0,
            lp_lock_percentage=0.0,
            is_ownership_renounced=False,
            owner_address=None,
            total_supply=0,
            decimals=9,
            holder_count=0,
            risk_score=0,
            risk_level=RiskLevel.LOW,
            warnings=[]
        )
        
        try:
            # 1. Get basic metadata
            await self._fetch_metadata(security)
            
            # 2. Check security features
            await self._check_security(security)
            
            # 3. Analyze LP status
            await self._analyze_lp(security)
            
            # 4. Check holder distribution
            await self._check_holders(security)
            
            # 5. Calculate risk score
            self._calculate_risk(security)
            
            # Cache result
            self.cache[token_address] = security
            
            # Print summary
            self._print_summary(security)
            
            return security
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return None
    
    async def _fetch_metadata(self, security: TokenSecurity):
        """Fetch token metadata"""
        try:
            url = f"{BIRDEYE_API}/defi/token_meta?address={security.address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                security.symbol = data.get('symbol', 'UNKNOWN')
                security.name = data.get('name', 'Unknown Token')
                security.decimals = data.get('decimals', 9)
                security.total_supply = float(data.get('supply', 0)) / (10 ** security.decimals)
        except Exception as e:
            print(f"   ⚠️ Metadata fetch failed: {e}")
    
    async def _check_security(self, security: TokenSecurity):
        """Check token security features"""
        try:
            url = f"{BIRDEYE_API}/defi/token_security?address={security.address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                
                # Contract features
                security.is_mintable = data.get('isMintable', False)
                security.is_freezable = data.get('isFreezable', False)
                security.is_honeypot = data.get('isHoneypot', False)
                security.is_blacklist = data.get('isBlackList', False)
                security.is_whitelist = data.get('isWhiteList', False)
                
                # Taxes
                security.buy_tax = data.get('buyTax', 0)
                security.sell_tax = data.get('sellTax', 0)
                security.transfer_tax = data.get('transferTax', 0)
                security.has_transfer_tax = any([
                    security.buy_tax > 0,
                    security.sell_tax > 0,
                    security.transfer_tax > 0
                ])
                
                # Limits
                max_tx = data.get('maxTransactionAmount', 0)
                if max_tx > 0 and security.total_supply > 0:
                    security.has_max_transaction = True
                    security.max_transaction_percentage = (max_tx / security.total_supply) * 100
                
                max_wallet = data.get('maxWalletAmount', 0)
                if max_wallet > 0 and security.total_supply > 0:
                    security.has_max_wallet = True
                    security.max_wallet_percentage = (max_wallet / security.total_supply) * 100
                
                # Ownership
                security.is_ownership_renounced = data.get('isOwnershipRenounced', False)
                security.owner_address = data.get('ownerAddress')
                
        except Exception as e:
            print(f"   ⚠️ Security check failed: {e}")
    
    async def _analyze_lp(self, security: TokenSecurity):
        """Analyze LP token status"""
        try:
            url = f"{BIRDEYE_API}/defi/token_security?address={security.address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                
                security.lp_mint_address = data.get('lpMintAddress')
                security.is_lp_burned = data.get('isLpBurned', False)
                security.is_lp_locked = data.get('isLpLocked', False)
                security.lp_lock_percentage = data.get('lpLockPercentage', 0)
                
                # Estimate lock duration if available
                lock_end = data.get('lpLockEnd')
                if lock_end:
                    try:
                        end_date = datetime.fromtimestamp(lock_end)
                        days = (end_date - datetime.now()).days
                        security.lp_lock_duration_days = max(0, days)
                    except:
                        pass
                        
        except Exception as e:
            print(f"   ⚠️ LP analysis failed: {e}")
    
    async def _check_holders(self, security: TokenSecurity):
        """Check holder distribution"""
        try:
            url = f"{BIRDEYE_API}/defi/tokenholders?address={security.address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                security.holder_count = data.get('total', 0)
        except Exception as e:
            print(f"   ⚠️ Holder check failed: {e}")
    
    def _calculate_risk(self, security: TokenSecurity):
        """Calculate comprehensive risk score"""
        score = 0
        warnings = []
        
        # Critical risks (high weight)
        if security.is_honeypot:
            score += 100
            warnings.append("🚨 HONEYPOT DETECTED - CANNOT SELL")
        
        if security.is_blacklist:
            score += 80
            warnings.append("⚠️ Blacklist function detected")
        
        if security.is_whitelist:
            score += 60
            warnings.append("⚠️ Whitelist required for trading")
        
        # Contract risks
        if security.is_mintable:
            score += 30
            warnings.append("⚠️ Mintable - supply can be inflated")
        
        if security.is_freezable:
            score += 25
            warnings.append("⚠️ Freezable - trading can be halted")
        
        if not security.is_ownership_renounced:
            score += 20
            warnings.append("⚠️ Ownership not renounced")
        
        # Tax risks
        total_tax = security.buy_tax + security.sell_tax + security.transfer_tax
        if total_tax > 20:
            score += 40
            warnings.append(f"🚨 High tax: {total_tax}% total")
        elif total_tax > 10:
            score += 25
            warnings.append(f"⚠️ Moderate tax: {total_tax}% total")
        elif total_tax > 0:
            score += 10
            warnings.append(f"ℹ️ Low tax: {total_tax}% total")
        
        # Limit risks
        if security.has_max_transaction and security.max_transaction_percentage < 5:
            score += 30
            warnings.append(f"🚨 Severe sell limit: {security.max_transaction_percentage:.2f}% max")
        elif security.has_max_transaction:
            score += 15
            warnings.append(f"⚠️ Sell limit: {security.max_transaction_percentage:.2f}% max")
        
        if security.has_max_wallet:
            score += 10
            warnings.append(f"⚠️ Max wallet: {security.max_wallet_percentage:.2f}%")
        
        # LP risks
        if not security.is_lp_locked and not security.is_lp_burned:
            score += 25
            warnings.append("⚠️ LP not locked - rug pull risk")
        elif security.is_lp_locked and security.lp_lock_percentage < 50:
            score += 15
            warnings.append(f"⚠️ Only {security.lp_lock_percentage:.1f}% LP locked")
        
        if security.is_lp_burned:
            score -= 10  # Bonus for burned LP
        
        # Holder concentration risk
        if security.holder_count < 100:
            score += 20
            warnings.append(f"⚠️ Low holder count: {security.holder_count}")
        
        # Cap score
        security.risk_score = min(score, 100)
        security.warnings = warnings
        
        # Set risk level
        if security.risk_score >= 76:
            security.risk_level = RiskLevel.CRITICAL
        elif security.risk_score >= 51:
            security.risk_level = RiskLevel.HIGH
        elif security.risk_score >= 26:
            security.risk_level = RiskLevel.MEDIUM
        else:
            security.risk_level = RiskLevel.LOW
    
    def _print_summary(self, security: TokenSecurity):
        """Print analysis summary"""
        print(f"\n{'='*60}")
        print(f"📊 TOKEN ANALYSIS: {security.symbol}")
        print(f"{'='*60}")
        
        # Risk level with color indicator
        risk_emoji = {
            RiskLevel.LOW: "🟢",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.HIGH: "🟠",
            RiskLevel.CRITICAL: "🔴"
        }
        print(f"\n{risk_emoji[security.risk_level]} Risk Level: {security.risk_level.value.upper()} ({security.risk_score}/100)")
        
        # Contract features
        print(f"\n📜 Contract Features:")
        print(f"   Mintable: {'❌ Yes' if security.is_mintable else '✅ No'}")
        print(f"   Freezable: {'❌ Yes' if security.is_freezable else '✅ No'}")
        print(f"   Ownership Renounced: {'✅ Yes' if security.is_ownership_renounced else '❌ No'}")
        
        # Taxes
        print(f"\n💰 Taxes:")
        print(f"   Buy Tax: {security.buy_tax}%")
        print(f"   Sell Tax: {security.sell_tax}%")
        print(f"   Transfer Tax: {security.transfer_tax}%")
        
        # Limits
        print(f"\n🚫 Limits:")
        if security.has_max_transaction:
            print(f"   Max Transaction: {security.max_transaction_percentage:.2f}%")
        else:
            print(f"   Max Transaction: None")
        
        if security.has_max_wallet:
            print(f"   Max Wallet: {security.max_wallet_percentage:.2f}%")
        else:
            print(f"   Max Wallet: None")
        
        # LP
        print(f"\n💧 Liquidity:")
        print(f"   LP Locked: {'✅ Yes' if security.is_lp_locked else '❌ No'}")
        if security.is_lp_locked:
            print(f"   Lock %: {security.lp_lock_percentage:.1f}%")
            print(f"   Lock Duration: {security.lp_lock_duration_days} days")
        print(f"   LP Burned: {'✅ Yes' if security.is_lp_burned else '❌ No'}")
        
        # Warnings
        if security.warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in security.warnings:
                print(f"   {warning}")
        
        print(f"{'='*60}\n")
    
    async def batch_analyze(self, token_addresses: List[str]) -> List[TokenSecurity]:
        """Analyze multiple tokens"""
        results = []
        for address in token_addresses:
            result = await self.analyze_token(address)
            if result:
                results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        return results
    
    def is_safe_to_trade(self, security: TokenSecurity, max_risk: RiskLevel = RiskLevel.MEDIUM) -> bool:
        """Check if token is safe to trade"""
        risk_order = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3
        }
        return risk_order[security.risk_level] <= risk_order[max_risk]
    
    def get_sell_recommendation(self, security: TokenSecurity) -> Dict:
        """Get sell strategy recommendations"""
        recommendations = {
            'can_sell': not security.is_honeypot,
            'recommended_slippage': 1.0,  # 1%
            'max_sell_percentage': 100.0,
            'warnings': security.warnings,
            'strategy': 'standard'
        }
        
        if security.is_honeypot:
            recommendations['strategy'] = 'cannot_sell'
            return recommendations
        
        # Adjust for taxes
        if security.sell_tax > 0:
            recommendations['recommended_slippage'] += security.sell_tax
        
        # Adjust for limits
        if security.has_max_transaction:
            recommendations['max_sell_percentage'] = security.max_transaction_percentage
            recommendations['strategy'] = 'partial_sells'
        
        # High risk adjustments
        if security.risk_level == RiskLevel.HIGH:
            recommendations['recommended_slippage'] += 2.0
            recommendations['strategy'] = 'aggressive'
        
        return recommendations


# Quick check function
async def quick_check(token_address: str) -> Optional[TokenSecurity]:
    """Quick token check"""
    detector = TokenomicsDetector()
    return await detector.analyze_token(token_address)


if __name__ == "__main__":
    print("🔍 Tokenomics Detector v1.0")
    print("\nUsage:")
    print("   from tokenomics_detector import TokenomicsDetector, quick_check")
    print("   detector = TokenomicsDetector()")
    print("   security = await detector.analyze_token('TOKEN_ADDRESS')")
    print("\n   Or quick check:")
    print("   security = await quick_check('TOKEN_ADDRESS')")
