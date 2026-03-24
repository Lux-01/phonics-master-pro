#!/usr/bin/env python3
"""
Solana Alpha Hunter v5.3 - Post-Rug Protection Edition
Adds: 6h age minimum, on-chain mint verification, LP depth check, 
backdoor detection, volume anomaly detection, multi-source verification
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Helius API Key
HELIUS_API_KEY = "350aa83c-44a4-4068-a511-580f82930d84"
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Track deployer wallets across scans
DEPLOYER_HISTORY = defaultdict(list)

def get_wallet_data_batch(addresses):
    """Get balance and age for multiple wallets in one batch call"""
    results = {}
    
    # Build batch request for balances
    balance_payloads = [
        {
            "jsonrpc": "2.0",
            "id": i,
            "method": "getAccountInfo",
            "params": [addr, {"encoding": "jsonParsed"}]
        }
        for i, addr in enumerate(addresses)
    ]
    
    # Build batch request for signatures (age check)
    sig_payloads = [
        {
            "jsonrpc": "2.0",
            "id": i + len(addresses),
            "method": "getSignaturesForAddress",
            "params": [addr, {"limit": 1}]
        }
        for i, addr in enumerate(addresses)
    ]
    
    all_payloads = balance_payloads + sig_payloads
    
    try:
        r = requests.post(HELIUS_URL, json=all_payloads, timeout=15)
        if r.status_code == 200:
            responses = r.json()
            
            # Process balance responses (first half)
            for resp in responses[:len(addresses)]:
                idx = resp.get('id', 0)
                if idx < len(addresses):
                    addr = addresses[idx]
                    result = resp.get('result', {})
                    if result and result.get('value'):
                        lamports = result['value'].get('lamports', 0)
                        results[addr] = {'balance': lamports / 1_000_000_000}
                    else:
                        results[addr] = {'balance': 0}
            
            # Process age responses (second half)
            for resp in responses[len(addresses):]:
                idx = resp.get('id', 0) - len(addresses)
                if 0 <= idx < len(addresses):
                    addr = addresses[idx]
                    sigs = resp.get('result', [])
                    if sigs and addr in results:
                        oldest = sigs[-1].get('blockTime')
                        if oldest:
                            results[addr]['first_tx'] = datetime.fromtimestamp(oldest)
                            results[addr]['age_days'] = (datetime.now() - results[addr]['first_tx']).days
                        else:
                            results[addr]['age_days'] = 0
                    elif addr in results:
                        results[addr]['age_days'] = 0
                        
    except Exception as e:
        print(f"  ⚠️ Batch check failed: {e}")
        # Fallback to zeros
        for addr in addresses:
            if addr not in results:
                results[addr] = {'balance': 0, 'age_days': 0}
    
    return results

def get_wallet_balance(address):
    """Get SOL balance for a wallet using Helius (legacy, use batch instead)"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [address, {"encoding": "jsonParsed"}]
        }
        r = requests.post(HELIUS_URL, json=payload, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('result') and data['result'].get('value'):
                lamports = data['result']['value'].get('lamports', 0)
                return lamports / 1_000_000_000
    except:
        pass
    return 0

def check_wallet_health(token_ca, holder_list, sample_size=7):
    """
    FAST VERSION: Check wallet health using batch API calls
    Returns: (health_score, details)
    - Samples top holders + random selection
    - Checks: wallet age (< 7 days = new), balance (< 0.1 SOL = low)
    - If 80% unhealthy → returns (0, details) = F grade
    """
    if not holder_list or len(holder_list) < 3:
        return (50, {"error": "Not enough holders", "sample_size": len(holder_list)})
    
    # Reduced sample size for speed (was 10, now 7)
    sample_size = min(sample_size, len(holder_list))
    
    # Sample strategy: top 3 + rest random
    top_count = min(3, len(holder_list))
    random_count = sample_size - top_count
    
    sampled = holder_list[:top_count]
    if random_count > 0 and len(holder_list) > top_count:
        random_sample = random.sample(holder_list[top_count:], min(random_count, len(holder_list) - top_count))
        sampled.extend(random_sample)
    
    # Extract addresses for batch call
    addresses = []
    for holder in sampled:
        addr = holder.get('address') if isinstance(holder, dict) else holder
        if addr:
            addresses.append(addr)
    
    if not addresses:
        return (50, {"error": "No valid addresses"})
    
    print(f"  🔍 Batch checking {len(addresses)} wallets...")
    
    # Batch fetch all wallet data at once
    start_time = time.time()
    wallet_data = get_wallet_data_batch(addresses)
    elapsed = time.time() - start_time
    
    # Process results
    unhealthy = 0
    details = []
    
    for i, holder in enumerate(sampled):
        address = holder.get('address') if isinstance(holder, dict) else holder
        pct = holder.get('pct', 0) if isinstance(holder, dict) else 0
        
        if not address or address not in wallet_data:
            continue
        
        data = wallet_data[address]
        balance = data.get('balance', 0)
        age_days = data.get('age_days', 0)
        
        is_low_balance = balance < 0.1
        is_new = age_days < 7 if age_days else False
        is_unhealthy = is_low_balance or is_new
        
        if is_unhealthy:
            unhealthy += 1
        
        # Store details for first 2
        if i < 2:
            details.append({
                "address": address[:12] + "...",
                "balance": round(balance, 3),
                "age_days": age_days,
                "pct": round(pct, 2),
                "unhealthy": is_unhealthy
            })
        
        # Early exit if we hit 80% unhealthy
        checked = i + 1
        if checked >= 4 and (unhealthy / checked) >= 0.8:
            print(f"  🚫 Early exit: {unhealthy}/{checked} unhealthy, shell attack detected")
            break
    
    # Calculate health percentage
    if len(sampled) == 0:
        return (50, {"error": "No valid wallets"})
    
    unhealthy_pct = (unhealthy / len(sampled)) * 100
    health_score = 100 - unhealthy_pct
    
    print(f"  📊 Wallet Health: {unhealthy}/{len(sampled)} unhealthy ({unhealthy_pct:.0f}%) [{elapsed:.1f}s]")
    for d in details:
        status = "⚠️" if d['unhealthy'] else "✅"
        print(f"     {status} {d['address']} | {d['balance']} SOL | {d['age_days']}d | {d['pct']}%")
    
    return (health_score, {
        "sampled": len(sampled),
        "unhealthy": unhealthy,
        "unhealthy_pct": unhealthy_pct,
        "details": details
    })

def get_token_age(ca):
    """Get token age in hours"""
    try:
        url = f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pairs = r.json()
            if pairs and len(pairs) > 0:
                pair_created_at = pairs[0].get('pairCreatedAt')
                if pair_created_at:
                    created = datetime.fromtimestamp(pair_created_at / 1000)
                    age_hours = (datetime.now() - created).total_seconds() / 3600
                    return max(0.1, age_hours)
    except:
        pass
    
    # Fallback to Helius
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [ca, {"limit": 100}]
        }
        r = requests.post(HELIUS_URL, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            sigs = data.get('result', [])
            if sigs:
                oldest = sigs[-1].get('blockTime')
                if oldest:
                    created = datetime.fromtimestamp(oldest)
                    age_hours = (datetime.now() - created).total_seconds() / 3600
                    return max(0.1, age_hours)
    except:
        pass
    
    return 0.1

# NEW v5.3: On-chain mint authority verification
def verify_mint_authority_onchain(ca):
    """
    Verify mint authority directly on-chain instead of trusting API
    Returns: (is_revoked, details)
    """
    try:
        # Get mint account info
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [ca, {"encoding": "jsonParsed"}]
        }
        r = requests.post(HELIUS_URL, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            result = data.get('result', {}).get('value', {})
            
            if result and result.get('data'):
                parsed = result['data'].get('parsed', {})
                info = parsed.get('info', {})
                mint_authority = info.get('mintAuthority')
                
                if mint_authority is None:
                    return True, "Mint authority revoked (on-chain)"
                else:
                    return False, f"⚠️ Mint authority ACTIVE: {mint_authority[:20]}..."
            
        return None, "Could not verify on-chain"
    except Exception as e:
        return None, f"On-chain check failed: {e}"

# NEW v5.3: LP pool depth check
def check_lp_pool_depth(ca, dex_data):
    """
    Check actual SOL in LP pool (not just lock %)
    Returns: (sol_in_pool, is_healthy)
    """
    try:
        # Get quote token (SOL) amount from pool
        liquidity = dex_data.get('liquidity', {})
        quote_amount = liquidity.get('quote', 0)  # SOL amount
        
        if quote_amount:
            sol_in_pool = float(quote_amount)
            is_healthy = sol_in_pool >= 20  # Minimum 20 SOL
            return sol_in_pool, is_healthy
        
        # Fallback: calculate from USD liquidity
        usd_liq = liquidity.get('usd', 0)
        if usd_liq:
            # Rough estimate: assume 50% SOL at $150/SOL
            sol_estimate = (usd_liq / 2) / 150
            is_healthy = sol_estimate >= 20
            return sol_estimate, is_healthy
            
    except:
        pass
    
    return 0, False

# NEW v5.3: Backdoor detection
def check_backdoor_contracts(ca):
    """
    Check for suspicious contract patterns
    Returns: (has_backdoor, details)
    """
    suspicious = []
    
    try:
        # Get token account to check for proxy patterns
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [ca, {"encoding": "base64"}]
        }
        r = requests.post(HELIUS_URL, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            result = data.get('result', {}).get('value', {})
            
            if result:
                owner = result.get('owner', '')
                # Check if owned by known suspicious programs
                suspicious_programs = [
                    '11111111111111111111111111111111',  # System program (unusual for tokens)
                ]
                
                if owner in suspicious_programs:
                    suspicious.append(f"Suspicious owner: {owner[:20]}...")
                
                # Check executable flag
                if result.get('executable'):
                    suspicious.append("Executable token account (highly suspicious)")
    except:
        pass
    
    # Cross-reference with RugCheck for freeze authority issues
    try:
        r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", timeout=10)
        if r.status_code == 200:
            rug = r.json()
            token_meta = rug.get('token', {})
            
            # Check freeze authority
            freeze_authority = token_meta.get('freezeAuthority')
            if freeze_authority:
                suspicious.append(f"Freeze authority active: {freeze_authority[:20]}...")
            
            # Check for mintable
            is_mintable = token_meta.get('isMintable', True)
            if is_mintable:
                mint_authority = token_meta.get('mintAuthority')
                if mint_authority:
                    suspicious.append("Token is still mintable")
    except:
        pass
    
    has_backdoor = len(suspicious) > 0
    return has_backdoor, suspicious

# NEW v5.3: Volume anomaly detection
def check_volume_anomaly(mcap, vol24, age_hours):
    """
    Detect suspicious volume patterns (exit liquidity)
    Returns: (is_anomaly, details)
    """
    if mcap <= 0:
        return False, "No MCAP data"
    
    volume_to_mcap_ratio = vol24 / mcap
    
    # Red flags
    if volume_to_mcap_ratio > 10:
        return True, f"🚨 EXTREME: Volume {volume_to_mcap_ratio:.1f}x MCAP (likely exit scam)"
    elif volume_to_mcap_ratio > 5:
        return True, f"⚠️ Volume {volume_to_mcap_ratio:.1f}x MCAP (exit liquidity pattern)"
    elif volume_to_mcap_ratio > 3 and age_hours < 2:
        return True, f"⚠️ Volume {volume_to_mcap_ratio:.1f}x MCAP on new token (< 2h)"
    
    return False, f"Volume {volume_to_mcap_ratio:.1f}x MCAP (normal)"

# NEW v5.3: Multi-source verification
def multi_source_verification(ca):
    """
    Cross-check RugCheck + DexScreener + Helius
    Returns: (is_consistent, discrepancies)
    """
    discrepancies = []
    
    # Source 1: RugCheck
    rug_mint_revoked = None
    try:
        r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", timeout=10)
        if r.status_code == 200:
            rug = r.json()
            rug_mint_revoked = rug.get('token', {}).get('mintAuthority') is None
    except:
        pass
    
    # Source 2: DexScreener
    dex_verified = None
    try:
        url = f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pairs = r.json()
            if pairs:
                dex_verified = True
    except:
        pass
    
    # Source 3: On-chain (Helius)
    onchain_mint_revoked = None
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [ca, {"encoding": "jsonParsed"}]
        }
        r = requests.post(HELIUS_URL, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            result = data.get('result', {}).get('value', {})
            if result and result.get('data'):
                parsed = result['data'].get('parsed', {})
                info = parsed.get('info', {})
                onchain_mint_revoked = info.get('mintAuthority') is None
    except:
        pass
    
    # Check for discrepancies
    if rug_mint_revoked is not None and onchain_mint_revoked is not None:
        if rug_mint_revoked != onchain_mint_revoked:
            discrepancies.append("RugCheck mint status doesn't match on-chain!")
    
    if not dex_verified:
        discrepancies.append("Token not found on DexScreener")
    
    is_consistent = len(discrepancies) == 0
    return is_consistent, discrepancies

def check_migration_pattern(ca, age_hours):
    """
    Check if token shows suspicious migration pattern
    Returns: (is_suspicious, details)
    """
    try:
        url = f"https://api.solana.fm/v1/tokens/{ca}/transfers"
        r = requests.get(url, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            txs = data.get('data', {}).get('transfers', [])
            
            if not txs or len(txs) < 2:
                return False, "No tx data"
            
            sorted_txs = sorted(txs, key=lambda x: x.get('timestamp', 0))
            first_time = sorted_txs[0].get('timestamp', 0)
            
            # Check for early migration activity
            early_txs = sorted_txs[:10]
            migration_keywords = ['raydium', 'orca', 'jupiter']
            
            for tx in early_txs:
                program = str(tx.get('program', '')).lower()
                if any(kw in program for kw in migration_keywords):
                    tx_time = tx.get('timestamp', 0)
                    time_diff = (tx_time - first_time) / 60  # minutes
                    
                    if time_diff < 5:
                        return True, f"🚨 INSTANT MIGRATION: {time_diff:.1f}min"
                    elif time_diff < 15:
                        return True, f"⚠️ Fast migration: {time_diff:.1f}min"
            
            return False, "Normal bonding"
    except:
        pass
    
    return False, "Check failed"

def check_honeypot(ca):
    """Check if token is a honeypot"""
    try:
        url = f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            pairs = r.json()
            if pairs:
                pair = pairs[0]
                buys = pair.get('txns', {}).get('h24', {}).get('buys', 0)
                sells = pair.get('txns', {}).get('h24', {}).get('sells', 0)
                
                if buys > 50 and sells < 5:
                    return {'is_honeypot': True, 'reason': 'High buy/sell ratio imbalance'}
                if buys > 0 and sells == 0:
                    return {'is_honeypot': True, 'reason': 'Zero sells detected'}
        return {'is_honeypot': False, 'reason': 'Normal buy/sell activity'}
    except:
        return {'is_honeypot': None, 'reason': 'Check failed'}

def get_deployer_info(ca):
    """Get contract deployer"""
    try:
        url = f"https://api.solana.fm/v1/tokens/{ca}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get('data', {}).get('mintAuthority') or data.get('data', {}).get('updateAuthority')
    except:
        pass
    return None

def analyze_transactions(ca, hours=6):
    """Analyze recent transaction patterns"""
    try:
        url = f"https://api.solana.fm/v1/tokens/{ca}/transfers"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            txs = data.get('data', {}).get('transfers', [])
            
            sells = [tx for tx in txs if tx.get('direction') == 'out']
            sell_wallets = defaultdict(int)
            for tx in sells:
                wallet = tx.get('from')
                if wallet:
                    sell_wallets[wallet] += 1
            
            coordinated = len([w for w, c in sell_wallets.items() if c > 5])
            total_sells = len(sells)
            
            return {
                'total_sells': total_sells,
                'coordinated_wallets': coordinated,
                'sell_concentration': (coordinated / max(total_sells, 1)) * 100,
                'is_wash_trading': coordinated > 3
            }
    except:
        pass
    return {'total_sells': 0, 'coordinated_wallets': 0, 'sell_concentration': 0, 'is_wash_trading': False}

class DexScanner:
    def get_trending(self):
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return [item for item in data if item.get('chainId') == 'solana']
        except:
            pass
        return []

class RugChecker:
    def check(self, ca):
        try:
            r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{ca}/report", timeout=10)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return {}

class AlphaHunterV53:
    def __init__(self):
        self.dex = DexScanner()
        self.rug = RugChecker()
        self.scan_count = 0
    
    def analyze(self, token):
        ca = token.get('tokenAddress')
        symbol = token.get('symbol', '?')
        name = token.get('name', symbol)
        
        print(f"\n{'='*80}")
        print(f"🎯 SCANNING: {name} (${symbol})")
        print(f"CA: {ca}")
        
        # Get token pairs
        try:
            r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{ca}", timeout=10)
            pairs = r.json() if r.status_code == 200 else []
        except:
            pairs = []
        
        if not pairs:
            print("❌ No Dex Screener data")
            return None
        
        dex = pairs[0]
        mcap = dex.get('marketCap', 0) or 0
        liq = dex.get('liquidity', {}).get('usd', 0) or 0
        vol24 = dex.get('volume', {}).get('h24', 0) or 0
        vol5m = dex.get('volume', {}).get('m5', 0) or 0
        
        # Filter MCAP
        if mcap < 10000 or mcap > 250000:
            print(f"❌ MCAP ${mcap:,.0f} outside range")
            return None
        
        # Age check
        age_hours = get_token_age(ca)
        print(f"  📊 MCAP: ${mcap:,.0f} | Liquidity: ${liq:,.0f} | Vol 24h: ${vol24:,.0f}")
        print(f"  🕐 Token Age: {age_hours:.1f} hours")
        
        # NEW v5.3: Multi-source verification
        print(f"  🔍 Multi-source verification...")
        is_consistent, discrepancies = multi_source_verification(ca)
        if discrepancies:
            print(f"  ⚠️ Data discrepancies detected:")
            for d in discrepancies:
                print(f"     - {d}")
        else:
            print(f"  ✅ Data consistent across sources")
        
        # Migration pattern check
        is_suspicious_migration, migration_msg = check_migration_pattern(ca, age_hours)
        if is_suspicious_migration:
            print(f"  🚨 {migration_msg}")
            print(f"  ❌ AUTO-SKIPPED: Suspicious migration pattern")
            return None
        else:
            print(f"  ✅ Migration Pattern: {migration_msg}")
        
        # NEW v5.3: On-chain mint authority verification
        print(f"  🔐 Verifying mint authority on-chain...")
        onchain_mint_revoked, onchain_mint_msg = verify_mint_authority_onchain(ca)
        if onchain_mint_revoked is False:
            print(f"  🚨 {onchain_mint_msg}")
            print(f"  ❌ AUTO-SKIPPED: Mint authority active (API may be lying)")
            return None
        elif onchain_mint_revoked is True:
            print(f"  ✅ {onchain_mint_msg}")
        else:
            print(f"  ⚠️ {onchain_mint_msg} (falling back to API)")
        
        # NEW v5.3: LP pool depth check
        print(f"  💧 Checking LP pool depth...")
        sol_in_pool, lp_healthy = check_lp_pool_depth(ca, dex)
        if sol_in_pool:
            print(f"  {'✅' if lp_healthy else '⚠️'} LP Pool: {sol_in_pool:.1f} SOL {'(healthy)' if lp_healthy else '(< 20 SOL)'}")
        else:
            print(f"  ⚠️ Could not determine LP depth")
        
        # NEW v5.3: Backdoor detection
        print(f"  🚪 Checking for backdoor contracts...")
        has_backdoor, backdoor_details = check_backdoor_contracts(ca)
        if has_backdoor:
            print(f"  🚨 BACKDOOR DETECTED:")
            for detail in backdoor_details:
                print(f"     - {detail}")
            print(f"  ❌ AUTO-SKIPPED: Potential backdoor")
            return None
        else:
            print(f"  ✅ No backdoor patterns detected")
        
        # NEW v5.3: Volume anomaly detection
        print(f"  📈 Checking volume patterns...")
        is_vol_anomaly, vol_msg = check_volume_anomaly(mcap, vol24, age_hours)
        if is_vol_anomaly:
            print(f"  🚨 {vol_msg}")
        else:
            print(f"  ✅ {vol_msg}")
        
        # Honeypot check
        honeypot = check_honeypot(ca)
        print(f"  🍯 Honeypot Check: {honeypot.get('reason', 'N/A')}")
        
        # RugCheck data
        rug = self.rug.check(ca)
        api_mint_revoked = rug.get('token', {}).get('mintAuthority') is None if rug else False
        markets = rug.get('markets', [{}]) if rug else [{}]
        lp_locked = markets[0].get('lp', {}).get('lpLockedPct', 0) if markets else 0
        holders = rug.get('totalHolders', 0) if rug else 0
        top_holders = rug.get('topHolders', []) if rug else []
        top10_pct = sum(h.get('pct', 0) for h in top_holders[:10])
        net = rug.get('insiderNetworks', []) if rug else []
        cluster_risk = len(net) if isinstance(net, list) else 0
        
        # Use on-chain verification if available
        mint_revoked = onchain_mint_revoked if onchain_mint_revoked is not None else api_mint_revoked
        
        # Deployer check
        deployer = get_deployer_info(ca)
        deployer_risk = False
        if deployer:
            DEPLOYER_HISTORY[deployer].append(ca)
            token_count = len(DEPLOYER_HISTORY[deployer])
            print(f"  👤 Deployer: {deployer[:20]}... | Tokens: {token_count}")
            if token_count > 1:
                deployer_risk = True
                print(f"  ⚠️ DEPLOYER LAUNCHED {token_count} TOKENS!")
        
        # Transaction analysis
        tx_analysis = analyze_transactions(ca)
        print(f"  📊 Tx Analysis: {tx_analysis['total_sells']} sells | {tx_analysis['coordinated_wallets']} coordinated")
        if tx_analysis['is_wash_trading']:
            print(f"  ⚠️ WASH TRADING DETECTED!")
        
        # Wallet Health Check v5.1
        wallet_health_score = 100
        wallet_health_details = {}
        wallet_health_passed = True
        
        skip_wallet_check = (
            honeypot.get('is_honeypot', False) or
            tx_analysis.get('is_wash_trading', False) or
            deployer_risk or
            holders < 50 or
            liq < 5000 or
            is_vol_anomaly
        )
        
        if skip_wallet_check:
            print(f"  ⏭️ Wallet health skipped (token already flagged)")
            wallet_health_score = 0
            wallet_health_passed = False
        elif top_holders:
            wallet_health_score, wallet_health_details = check_wallet_health(ca, top_holders, sample_size=7)
            
            if wallet_health_details.get('unhealthy_pct', 0) >= 80:
                wallet_health_passed = False
                print(f"  🚫 WALLET HEALTH FAIL: {wallet_health_details['unhealthy_pct']:.0f}% unhealthy (shell wallet attack)")
            else:
                print(f"  ✅ Wallet Health: {wallet_health_score:.0f}%")
        else:
            print(f"  ⚠️ No holder data available for wallet health check")
        
        # Socials
        info = dex.get('info', {})
        socials = info.get('socials', [])
        websites = info.get('websites', [])
        has_tw = any(s.get('type') == 'twitter' for s in socials)
        has_tg = any(s.get('type') == 'telegram' for s in socials)
        has_web = len(websites) > 0
        
        # Narrative Analysis v5.2
        narrative_score, narrative_type, narrative_red_flags = analyze_narrative(token)
        print(f"  📖 Narrative: {narrative_type} | Score: {narrative_score}/10")
        if narrative_red_flags:
            print(f"  ⚠️ Narrative Red Flags: {narrative_red_flags}")
        
        # Scoring (v5.3 - 20-point scale, added new checks)
        score = 0
        checks = []
        red_flags = []
        
        # 1. MCAP range
        if 10000 < mcap < 250000:
            score += 1
            checks.append("MCAP range ✅")
        
        # 2. Liquidity amount (USD)
        if liq >= 15000:
            score += 1
            checks.append("Liquidity amount ✅")
        
        # NEW v5.3: 3. LP depth (SOL in pool)
        if lp_healthy and sol_in_pool >= 20:
            score += 1
            checks.append(f"LP depth >= 20 SOL ({sol_in_pool:.1f}) ✅")
        elif sol_in_pool > 0:
            red_flags.append(f"⚠️ LP depth low: {sol_in_pool:.1f} SOL (< 20)")
        
        # 4. LP locked %
        if lp_locked >= 95:
            score += 1
            checks.append("LP locked 95%+ ✅")
        
        # 5. Slippage
        slippage_2k = (2000 / (liq * 2 + 1)) * 100
        if slippage_2k < 20:
            score += 1
            checks.append("Low slippage ✅")
        
        # 6. Volume 5m
        if vol5m >= 5000:
            score += 1
            checks.append("Volume 5m ✅")
        
        # NEW v5.3: 7. Volume anomaly check
        if not is_vol_anomaly:
            score += 1
            checks.append("Volume pattern normal ✅")
        else:
            red_flags.append("🚨 VOLUME ANOMALY (exit liquidity pattern)")
        
        # 8. Volume 24h
        if vol24 >= 20000:
            score += 1
            checks.append("Volume 24h ✅")
        
        # NEW v5.3: 9. Mint verified on-chain
        if onchain_mint_revoked is True:
            score += 1
            checks.append("Mint revoked (on-chain verified) ✅")
        elif onchain_mint_revoked is None:
            # Fallback to API
            if mint_revoked:
                score += 1
                checks.append("Mint revoked (API) ✅")
        
        # 10. Top10 distribution
        if top10_pct < 30:
            score += 1
            checks.append("Top10 <30% ✅")
        
        # 11. Cluster risk
        if cluster_risk <= 3:
            score += 1
            checks.append("Low cluster risk ✅")
        
        # 12. Holders
        if holders > 300:
            score += 1
            checks.append("Holders >300 ✅")
        
        # 13. Website
        if has_web:
            score += 1
            checks.append("Website ✅")
        
        # 14. Twitter
        if has_tw:
            score += 1
            checks.append("Twitter ✅")
        
        # NEW v5.3: 15. Token age (6h minimum for full point)
        if age_hours >= 6:
            score += 1
            checks.append("Age >= 6h ✅")
        elif age_hours >= 0.5:
            score += 0.5
            checks.append("Age > 30m (partial) ⚠️")
            red_flags.append(f"⚠️ TOO NEW ({age_hours:.1f}h < 6h)")
        else:
            red_flags.append(f"🚨 TOO NEW ({age_hours:.1f}h < 30m)")
        
        # 16. Deployer clean
        if not deployer_risk and deployer:
            score += 1
            checks.append("Clean deployer ✅")
        elif deployer_risk:
            red_flags.append("⚠️ REPEAT DEPLOYER")
        
        # 17. Honeypot negative
        if not honeypot.get('is_honeypot'):
            score += 1
            checks.append("Not honeypot ✅")
        else:
            red_flags.append("🚨 HONEYPOT DETECTED")
        
        # NEW v5.3: 18. No backdoor
        if not has_backdoor:
            score += 1
            checks.append("No backdoor ✅")
        else:
            red_flags.append("🚨 BACKDOOR DETECTED")
        
        # 19. Wallet health
        if wallet_health_passed and wallet_health_score >= 50:
            score += 1
            checks.append("Wallet health ✅")
        else:
            red_flags.append(f"🚫 WALLET HEALTH FAIL ({wallet_health_details.get('unhealthy_pct', 0):.0f}% shell wallets)")
        
        # 20. Narrative quality
        if narrative_score >= 5:
            score += 1
            checks.append(f"Strong narrative ({narrative_type}) ✅")
        
        # Security output
        print(f"\n🔒 SECURITY:")
        print(f"  Mint revoked: {'✅ (on-chain)' if onchain_mint_revoked else '❌'} {'(API only)' if onchain_mint_revoked is None else ''}")
        print(f"  LP locked: {lp_locked:.0f}% | Depth: {sol_in_pool:.1f} SOL")
        print(f"  Holders: {holders}")
        print(f"  Top10: {top10_pct:.1f}%")
        print(f"  Cluster risk: {cluster_risk}")
        print(f"  Wallet Health: {wallet_health_score:.0f}%")
        print(f"  Volume/MCAP: {vol24/mcap:.1f}x {'✅' if not is_vol_anomaly else '⚠️'}")
        
        # Grading v5.3 (20-point scale)
        grade = "A+ 🔥" if score >= 17 else "A ✅" if score >= 14 else "B 🟡" if score >= 10 else "C ⚠️" if score >= 7 else "D ❌"
        
        # A+ requirements v5.3
        if score >= 17:
            a_plus_fail = []
            if wallet_health_score < 80:
                a_plus_fail.append(f"wallet_health={wallet_health_score:.0f}%")
            if age_hours < 6:
                a_plus_fail.append(f"age={age_hours:.1f}h (< 6h)")
            if narrative_score < 5:
                a_plus_fail.append(f"narrative={narrative_score}/10")
            if not lp_healthy:
                a_plus_fail.append(f"LP_depth={sol_in_pool:.1f}SOL (< 20)")
            if is_vol_anomaly:
                a_plus_fail.append("volume_anomaly")
            if onchain_mint_revoked is not True:
                a_plus_fail.append("mint_not_onchain_verified")
            if has_backdoor:
                a_plus_fail.append("backdoor_detected")
            
            if a_plus_fail:
                grade = "A ✅"
                print(f"\n📉 A+ downgraded to A (missing: {', '.join(a_plus_fail)})")
        
        # F grade for critical failures
        if not wallet_health_passed or has_backdoor or honeypot.get('is_honeypot'):
            grade = "F 🚫"
            if not wallet_health_passed:
                print(f"\n🚫 GRADE: F (Shell wallet attack detected)")
            elif has_backdoor:
                print(f"\n🚫 GRADE: F (Backdoor contract detected)")
            else:
                print(f"\n🚫 GRADE: F (Honeypot detected)")
        else:
            print(f"\n🎓 SCORE: {score}/20")
            print(f"🎯 GRADE: {grade}")
        
        if red_flags:
            print(f"\n🚨 RED FLAGS:")
            for flag in red_flags:
                print(f"    {flag}")
        
        # Auto-skip conditions
        if honeypot.get('is_honeypot') or tx_analysis['is_wash_trading'] or deployer_risk or not wallet_health_passed or has_backdoor:
            print(f"\n❌ AUTO-SKIPPED: Critical red flags detected")
            return None
        
        return {
            'name': name,
            'symbol': symbol,
            'ca': ca,
            'mcap': mcap,
            'liq': liq,
            'sol_in_pool': sol_in_pool,
            'vol24': vol24,
            'vol5m': vol5m,
            'vol_mcap_ratio': vol24 / mcap if mcap > 0 else 0,
            'age_hours': age_hours,
            'score': score,
            'grade': grade,
            'mint_revoked': mint_revoked,
            'onchain_mint_verified': onchain_mint_revoked,
            'lp_locked': lp_locked,
            'lp_depth_healthy': lp_healthy,
            'holders': holders,
            'top10_pct': top10_pct,
            'cluster_risk': cluster_risk,
            'honeypot': honeypot,
            'tx_analysis': tx_analysis,
            'deployer_risk': deployer_risk,
            'wallet_health': wallet_health_score,
            'wallet_health_details': wallet_health_details,
            'narrative_score': narrative_score,
            'narrative_type': narrative_type,
            'narrative_red_flags': narrative_red_flags,
            'has_backdoor': has_backdoor,
            'backdoor_details': backdoor_details,
            'volume_anomaly': is_vol_anomaly,
            'volume_anomaly_msg': vol_msg,
            'data_consistent': is_consistent,
            'data_discrepancies': discrepancies,
            'red_flags': red_flags,
            'checks': checks
        }

# MEME/HYPE WORDS for narrative detection
HYPE_WORDS = {
    'AI': 2,
    'GPT': 3,
    'CHATGPT': 3,
    'ELON': 2,
    'MUSK': 2,
    'DOGE': 2,
    'PEPE': 2,
    'TRUMP': 2,
    'BIDEN': 2,
    'POLITICAL': 1,
    'ROBOT': 2,
    'BOTS': 2,
    'FUTURE': 1,
    'MOON': 2,
    'MOONING': 2,
    'LAMBO': 2,
    'WEALTH': 1,
    'RICH': 1,
    'MILLION': 1,
    'BILLION': 1,
    'UNSTOPPABLE': 2,
    'REVOLUTION': 1,
    'REVOLUTIONARY': 2,
    'GAMECHANGING': 2,
    'GAME-CHANGING': 2,
    'WORLD': 1,
    'CHANGING': 1,
    'FIRST': 1,
    'ONLY': 1,
    'BEST': 1,
    'ULTIMATE': 2,
    'OFFICIAL': 1,
    'REAL': 1,
    'TRUE': 1,
    'LEGEND': 2,
    'KING': 2,
    'QUEEN': 2,
    'GOD': 3,
    'ALPHA': 2,
    'DEGEN': 2,
    'BASED': 2,
    'CHAD': 2,
    'WOJAK': 2,
    'MEME': 1,
    'MEMES': 1,
    'CULTURE': 1,
    'SOCIAL': 1,
    'TRENDING': 1,
    'VIRAL': 2,
    'COMMUNITY': 1,
    'TOGETHER': 1,
    'STRONG': 1,
    'HODL': 2,
    'HOLD': 1
}

RED_FLAG_WORDS = [
    'SCAM', 'RUG', 'PUMP', 'DUMP', 'FAKE', 'PONZI', 
    'PYRAMID', 'MULTIPLY', '10X', '100X', '1000X', 'GUARANTEED'
]

def analyze_narrative(token):
    """
    Analyze token narrative/story quality
    Returns: (narrative_score, narrative_type, red_flags)
    - Score: 0-10 based on meme potential, legitimacy, clarity
    - Type: AI, Meme, Political, Celebrity, Generic
    - Red flags: obvious scam terms
    """
    name = token.get('name', '').upper()
    symbol = token.get('symbol', '').upper()
    description = token.get('description', '').upper()
    combined = f"{name} {symbol} {description}"
    
    # Check for red flag words
    red_flags = []
    for word in RED_FLAG_WORDS:
        if word in combined:
            red_flags.append(f"Red flag word: {word}")
    
    # Calculate hype score
    hype_score = 0
    narrative_type = "Generic"
    
    # AI-related
    ai_words = ['AI', 'GPT', 'CHATGPT', 'ARTIFICIAL', 'INTELLIGENCE', 'NEURAL', 'BOT']
    if any(w in combined for w in ai_words):
        hype_score += 3
        narrative_type = "AI"
    
    # Political
    political_words = ['TRUMP', 'BIDEN', 'POLITICAL', 'POLITIC', 'ELECTION', 'VOTE']
    if any(w in combined for w in political_words):
        hype_score += 3
        narrative_type = "Political"
    
    # Celebrity
    celeb_words = ['ELON', 'MUSK', 'MUSK', 'BEZOS', 'ZUCK', 'CELEBRITY', 'FAMOUS']
    if any(w in combined for w in celeb_words):
        hype_score += 3
        narrative_type = "Celebrity"
    
    # Classic Memes
    meme_words = ['PEPE', 'DOGE', 'SHIB', 'WOJAK', 'CHAD', 'DEGEN', 'BOOMER']
    if any(w in combined for w in meme_words):
        hype_score += 2
        if narrative_type == "Generic":
            narrative_type = "Meme"
    
    # Generic hype words
    for word, points in HYPE_WORDS.items():
        if word in combined:
            hype_score += points
    
    # Length penalties for overly complex names
    if len(name) > 20:
        hype_score -= 1
    
    # Short symbol bonus (catchy/memorable)
    if len(symbol) <= 4 and symbol.isalpha():
        hype_score += 1
    
    # Scam penalty
    if red_flags:
        hype_score = max(0, hype_score - len(red_flags) * 3)
    
    # Normalize to 0-10
    hype_score = min(10, max(0, hype_score))
    
    return (hype_score, narrative_type, red_flags)

def scan_all():
    hunter = AlphaHunterV53()
    print("="*80)
    print("🚀 SOLANA ALPHA HUNTER v5.3 - Post-Rug Protection Edition")
    print("🛡️ New: On-chain verification | LP depth check | Volume anomaly detection")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\n📊 Fetching trending Solana tokens...")
    
    trending = hunter.dex.get_trending()
    if not trending:
        print("❌ No trending data available")
        return []
    
    print(f"Found {len(trending)} tokens, analyzing first 15...")
    
    results = []
    for token in trending[:15]:
        result = hunter.analyze(token)
        if result:
            results.append(result)
    
    return results

if __name__ == "__main__":
    results = scan_all()
    
    # Summary
    print("\n" + "="*80)
    print("🎯 SUMMARY - v5.3 Post-Rug Protection Scan")
    print("="*80)
    
    alpha_plus = sum(1 for r in results if 'A+' in r['grade'])
    alpha_count = sum(1 for r in results if 'A' in r['grade'] and '+' not in r['grade'])
    f_grades = sum(1 for r in results if 'F' in r['grade'])
    skipped = 15 - len(results)
    
    print(f"✅ Grade A+: {alpha_plus}")
    print(f"✅ Grade A: {alpha_count}")
    print(f"🚫 Grade F (filtered): {f_grades}")
    print(f"❌ Auto-skipped: ~{skipped}")
    
    # Narrative summary
    narratives = {}
    for r in results:
        nt = r.get('narrative_type', 'Unknown')
        narratives[nt] = narratives.get(nt, 0) + 1
    
    print(f"\n📖 Narrative Distribution:")
    for nt, count in sorted(narratives.items(), key=lambda x: x[1], reverse=True):
        print(f"    {nt}: {count}")
    
    # Protection summary
    protections_triggered = {
        'backdoor': sum(1 for r in results if r.get('has_backdoor')),
        'volume_anomaly': sum(1 for r in results if r.get('volume_anomaly')),
        'data_discrepancy': sum(1 for r in results if not r.get('data_consistent')),
        'low_lp_depth': sum(1 for r in results if not r.get('lp_depth_healthy'))
    }
    
    print(f"\n🛡️ Protection Triggers:")
    for protection, count in protections_triggered.items():
        if count > 0:
            print(f"    {protection}: {count}")
    
    # Save
    with open('/home/skux/.openclaw/workspace/alpha_results_v53.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Saved {len(results)} results to alpha_results_v53.json")
    
    # Telegram alerts for A/A+ only
    for r in results:
        if 'A' in r['grade'] and 'F' not in r['grade']:
            print(f"\n🚨 ALERT CANDIDATE:")
            print(f"   {r['grade']} | {r['ca'][:20]}... | {r.get('narrative_type', '?')}")
            print(f"   Wallet: {r['wallet_health']:.0f}% | Age: {r['age_hours']:.1f}h | LP: {r.get('sol_in_pool', 0):.1f} SOL")
            if r.get('volume_anomaly'):
                print(f"   ⚠️ Volume anomaly detected!")
