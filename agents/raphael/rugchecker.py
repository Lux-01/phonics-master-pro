#!/usr/bin/env python3
"""
RugCheck Module for Raphael
On-chain verification before trading
"""

import requests
import json
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime

@dataclass
class RugCheck:
    safe: bool
    score: int  # 0-100, higher = safer
    risks: List[str]
    warnings: List[str]
    mint_authority: str  # "revoked" or "active"
    freeze_authority: str  # "revoked" or "active"
    lp_burned: bool
    top_holders_pct: float
    verified: bool

class SolanaRugChecker:
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc = rpc_url
        
    def check_token(self, mint_address: str) -> RugCheck:
        """Full rug check on a token before trading"""
        risks = []
        warnings = []
        score = 100
        
        # 1. Check if token exists and get basic info
        token_info = self._get_token_info(mint_address)
        if not token_info:
            return RugCheck(
                safe=False, score=0, 
                risks=["Token not found on-chain"],
                warnings=[],
                mint_authority="unknown",
                freeze_authority="unknown",
                lp_burned=False,
                top_holders_pct=100,
                verified=False
            )
        
        # 2. Check mint authority (MUST be revoked)
        mint_auth = self._check_mint_authority(mint_address)
        if mint_auth == "active":
            risks.append("🔴 CRITICAL: Mint authority still active - dev can print infinite tokens")
            score = 0
        else:
            score += 10
            
        # 3. Check freeze authority (SHOULD be revoked)
        freeze_auth = self._check_freeze_authority(mint_address)
        if freeze_auth == "active":
            warnings.append("⚠️ Freeze authority still active - accounts can be frozen")
            score -= 20
        else:
            score += 10
            
        # 4. Check top holders concentration
        top_holders = self._get_top_holders(mint_address)
        top_pct = sum(h['pct'] for h in top_holders[:5])
        
        if top_pct > 70:
            risks.append(f"🔴 CRITICAL: Top 5 holders control {top_pct:.1f}%")
            score -= 40
        elif top_pct > 50:
            warnings.append(f"⚠️ Top 5 holders control {top_pct:.1f}%")
            score -= 20
        else:
            score += 10
            
        # 5. Check LP burn status
        lp_burned = self._check_lp_burned(mint_address)
        if lp_burned:
            score += 15
        else:
            warnings.append("⚠️ LP tokens not burned - dev can remove liquidity")
            score -= 15
            
        # 6. Check for known scams (blacklist)
        blacklisted = self._check_blacklist(mint_address)
        if blacklisted:
            risks.append("🔴 CRITICAL: Token is blacklisted as known scam")
            score = 0
            
        # 7. Check verification status
        verified = self._check_verification(mint_address)
        if verified:
            score += 5
            
        # Calculate final safety
        safe = score >= 70 and len(risks) == 0
        
        return RugCheck(
            safe=safe,
            score=max(0, score),
            risks=risks,
            warnings=warnings,
            mint_authority=mint_auth,
            freeze_authority=freeze_auth,
            lp_burned=lp_burned,
            top_holders_pct=top_pct,
            verified=verified
        )
    
    def _get_token_info(self, mint: str) -> Optional[Dict]:
        """Get basic token info from RPC"""
        try:
            resp = requests.post(
                self.rpc,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [mint, {"encoding": "jsonParsed"}]
                },
                timeout=5
            )
            data = resp.json()
            if 'result' in data and data['result']['value']:
                return data['result']['value']
            return None
        except:
            return None
    
    def _check_mint_authority(self, mint: str) -> str:
        """Check if mint authority is revoked"""
        try:
            resp = requests.post(
                self.rpc,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [mint, {"encoding": "jsonParsed"}]
                },
                timeout=5
            )
            data = resp.json()
            if 'result' in data and data['result']['value']:
                parsed = data['result']['value'].get('data', {}).get('parsed', {})
                mint_auth = parsed.get('info', {}).get('mintAuthority')
                return "revoked" if not mint_auth else "active"
        except:
            pass
        return "unknown"
    
    def _check_freeze_authority(self, mint: str) -> str:
        """Check if freeze authority is revoked"""
        try:
            resp = requests.post(
                self.rpc,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [mint, {"encoding": "jsonParsed"}]
                },
                timeout=5
            )
            data = resp.json()
            if 'result' in data and data['result']['value']:
                parsed = data['result']['value'].get('data', {}).get('parsed', {})
                freeze_auth = parsed.get('info', {}).get('freezeAuthority')
                return "revoked" if not freeze_auth else "active"
        except:
            pass
        return "unknown"
    
    def _get_top_holders(self, mint: str) -> List[Dict]:
        """Get top token holders"""
        holders = []
        try:
            # Get largest token accounts
            resp = requests.post(
                self.rpc,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenLargestAccounts",
                    "params": [mint]
                },
                timeout=10
            )
            data = resp.json()
            if 'result' in data and 'value' in data['result']:
                accounts = data['result']['value']
                total = sum(a['amount'] for a in accounts)
                for acc in accounts[:5]:
                    holders.append({
                        'address': acc['address'],
                        'amount': acc['amount'],
                        'pct': (acc['amount'] / total * 100) if total > 0 else 0
                    })
        except:
            pass
        return holders
    
    def _check_lp_burned(self, mint: str) -> bool:
        """Check if LP tokens are burned (liquidity locked)"""
        try:
            # Check for liquidity pool accounts
            # This is a simplified check - real implementation would scan Raydium/Orca
            burn_addresses = [
                "11111111111111111111111111111111",  # Null address
                "Burn11111111111111111111111111111111111111",  # Burn address
            ]
            # For now, return unknown as LP checking requires DEX parsing
            return False
        except:
            return False
    
    def _check_blacklist(self, mint: str) -> bool:
        """Check against known scam list"""
        # Known scam tokens (add more as discovered)
        blacklist = set([
            # Add known mint addresses here
        ])
        return mint in blacklist
    
    def _check_verification(self, mint: str) -> bool:
        """Check if token is verified on Jupiter or other aggregators"""
        try:
            resp = requests.get(
                f"https://token.jup.ag/all",
                timeout=5
            )
            if resp.status_code == 200:
                tokens = resp.json()
                for t in tokens:
                    if t.get('address') == mint:
                        return True
        except:
            pass
        return False

# Standalone execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 rugchecker.py <mint_address>")
        print("\nExample:")
        print("  python3 rugchecker.py EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        sys.exit(1)
    
    mint = sys.argv[1]
    checker = SolanaRugChecker()
    
    print(f"🔍 Checking {mint}...")
    print(f"{'='*60}")
    
    result = checker.check_token(mint)
    
    print(f"\n🛡️  SAFETY SCORE: {result.score}/100")
    print(f"✅ SAFE TO TRADE: {'YES' if result.safe else 'NO'}")
    
    print(f"\n🔐 AUTHORITY STATUS:")
    print(f"   Mint Authority: {result.mint_authority}")
    print(f"   Freeze Authority: {result.freeze_authority}")
    
    print(f"\n👥 HOLDER CONCENTRATION:")
    print(f"   Top 5 Holders: {result.top_holders_pct:.1f}%")
    
    print(f"\n🔥 LP STATUS:")
    print(f"   LP Burned: {result.lp_burned}")
    print(f"   Verified: {result.verified}")
    
    if result.risks:
        print(f"\n🚨 CRITICAL RISKS:")
        for r in result.risks:
            print(f"   • {r}")
    
    if result.warnings:
        print(f"\n⚠️  WARNINGS:")
        for w in result.warnings:
            print(f"   • {w}")
    
    print(f"\n{'='*60}")
    print(f"RECOMMENDATION: {'✅ APPROVED' if result.safe else '❌ REJECTED'}")
