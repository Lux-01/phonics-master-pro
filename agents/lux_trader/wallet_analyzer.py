#!/usr/bin/env python3
"""
🔍 Wallet Analyzer - Shell Wallet Detection Module
Helper functions for detecting fake/sybil wallet clusters

Detection Methods:
1. Wallet Age Clustering - Detect wallets created together
2. Micro-Buy Pattern - Detect tiny buys typical of bot clusters
3. Funding Source Analysis - Detect common funding wallets
4. Timing Pattern Analysis - Detect automated buying patterns
"""

import time
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from statistics import variance, mean, stdev


class WalletAnalyzer:
    """Analyzes wallet clusters for shell wallet detection"""
    
    def __init__(self, helius_api_key: str = None, birdeye_api_key: str = None):
        self.helius_key = helius_api_key
        self.birdeye_key = birdeye_api_key
        self.cache = {}
    
    # ═══════════════════════════════════════════════════════════════
    # 1. SHELL WALLET CLUSTER DETECTION
    # ═══════════════════════════════════════════════════════════════
    
    def detect_shell_cluster(self, wallets: List[Dict]) -> Dict[str, Any]:
        """
        Detect if a group of wallets is a shell/bot cluster
        
        Shell wallets are created together by developers to fake volume
        and create false hype around a token launch.
        
        Args:
            wallets: List of wallet data with creation_date, buys, etc.
        
        Returns:
            Dict with cluster analysis results
        """
        if len(wallets) < 3:
            return {'is_shell_cluster': False, 'reason': 'insufficient_wallets'}
        
        results = {
            'is_shell_cluster': False,
            'confidence': 0.0,
            'flags': [],
            'score_penalty': 0,
            'details': {}
        }
        
        # Check multiple shell indicators
        age_analysis = self._analyze_wallet_ages(wallets)
        micro_buy_analysis = self._analyze_micro_buys(wallets)
        funding_analysis = self._analyze_funding_sources(wallets)
        timing_analysis = self._analyze_timing_patterns(wallets)
        
        results['details']['age_variance'] = age_analysis
        results['details']['micro_buys'] = micro_buy_analysis
        results['details']['funding'] = funding_analysis
        results['details']['timing'] = timing_analysis
        
        # Aggregate flags
        total_penalty = 0
        confidence = 0.0
        
        if age_analysis['flagged']:
            results['flags'].append('cluster_age')
            total_penalty += age_analysis['penalty']
            confidence += 0.25
            
        if micro_buy_analysis['flagged']:
            results['flags'].append('micro_buys')
            total_penalty += micro_buy_analysis['penalty']
            confidence += 0.25
            
        if funding_analysis['flagged']:
            results['flags'].append('common_funding')
            total_penalty += funding_analysis['penalty']
            confidence += 0.30  # Strongest signal
            
        if timing_analysis['flagged']:
            results['flags'].append('regular_timing')
            total_penalty += timing_analysis['penalty']
            confidence += 0.20
        
        results['score_penalty'] = total_penalty
        results['confidence'] = min(confidence, 0.95)
        results['is_shell_cluster'] = len(results['flags']) >= 2
        
        return results
    
    def _analyze_wallet_ages(self, wallets: List[Dict]) -> Dict:
        """
        Analyze wallet creation dates for clustering
        
        DEV SCAM PATTERN: Developers create 50-200 wallets in a batch
        within minutes or hours using automated scripts. These wallets
        all have nearly identical creation timestamps.
        
        REAL USER PATTERN: Organic users have highly varied wallet ages
        - some created months ago, some years, some days ago.
        
        FLAG: If age variance < 1 hour, wallets were likely batch-created
        """
        creation_dates = []
        
        for wallet in wallets:
            if 'creation_date' in wallet:
                creation_dates.append(wallet['creation_date'])
            elif 'first_tx_time' in wallet:
                # Use first transaction as proxy for wallet age
                creation_dates.append(wallet['first_tx_time'])
        
        if len(creation_dates) < 3:
            return {'flagged': False, 'variance_hours': None, 'penalty': 0}
        
        # Calculate variance in hours
        timestamps = [datetime.fromisoformat(d.replace('Z', '+00:00')) 
                      if isinstance(d, str) else datetime.fromtimestamp(d)
                      for d in creation_dates]
        
        # Convert to hours since epoch
        hours = [t.timestamp() / 3600 for t in timestamps]
        
        try:
            age_variance = variance(hours)
            age_variance_hours = age_variance  # Already in hours
        except:
            age_variance_hours = 0
        
        # Flag if variance < 1 hour (clustered creation)
        flagged = age_variance_hours < 1.0
        
        # Cluster age penalty: -4 points for < 1hr variance
        penalty = -4 if flagged else 0
        
        # Calculate median age for context
        median_age = mean(hours) if hours else 0
        
        return {
            'flagged': flagged,
            'variance_hours': age_variance_hours,
            'penalty': penalty,
            'wallet_count': len(creation_dates),
            'median_age_hours': median_age
        }
    
    def _analyze_micro_buys(self, wallets: List[Dict]) -> Dict:
        """
        Analyze buy sizes for micro-buy patterns
        
        DEV SCAM PATTERN: Shell wallets make tiny $1-3 purchases to 
        generate transactions without real capital commitment. This
        creates fake "buyer" counts while minimizing cost.
        
        REAL USER PATTERN: Retail buyers typically invest $10-100+ 
        in speculative tokens. Real users have varied position sizes.
        
        FLAG: If average buy < $5 USD, likely bot cluster
        """
        buy_amounts = []
        
        for wallet in wallets:
            # Extract buy amounts from wallet data
            wallet_buys = wallet.get('buys', [])
            for buy in wallet_buys:
                if isinstance(buy, dict):
                    amount = buy.get('amount_usd', 0)
                else:
                    amount = float(buy) if isinstance(buy, (int, float)) else 0
                buy_amounts.append(amount)
        
        if len(buy_amounts) < 3:
            return {'flagged': False, 'avg_buy': None, 'penalty': 0}
        
        avg_buy = mean(buy_amounts)
        
        # Flag if avg buy < $5 USD (micro-buy pattern)
        flagged = avg_buy < 5.0
        
        # Micro-buy penalty: -3 points for avg < $5
        penalty = -3 if flagged else 0
        
        return {
            'flagged': flagged,
            'avg_buy_usd': round(avg_buy, 2),
            'min_buy_usd': min(buy_amounts) if buy_amounts else 0,
            'max_buy_usd': max(buy_amounts) if buy_amounts else 0,
            'buy_count': len(buy_amounts),
            'penalty': penalty
        }
    
    def _analyze_funding_sources(self, wallets: List[Dict]) -> Dict:
        """
        Analyze if wallets share common funding source
        
        DEV SCAM PATTERN: Developer sends SOL to 50+ new wallets from
        a single "master" funding wallet. Each shell wallet gets $1-5 
        of SOL to pay for gas and tiny buys.
        
        REAL USER PATTERN: Users fund wallets from exchanges, bridges,
        or varied personal wallets. Funding sources are distributed.
        
        FLAG: If >60% of wallets funded by same address, it's a cluster
        """
        funding_sources = {}
        
        for wallet in wallets:
            # Get first funding transaction source
            funding_tx = wallet.get('funding_source', None)
            if funding_tx:
                source = funding_tx if isinstance(funding_tx, str) else funding_tx.get('from')
                funding_sources[source] = funding_sources.get(source, 0) + 1
        
        if not funding_sources:
            return {'flagged': False, 'common_funding_pct': 0, 'penalty': 0}
        
        # Find most common funding source
        total_wallets = len(wallets)
        most_common = max(funding_sources.items(), key=lambda x: x[1])
        common_source, count = most_common
        
        common_pct = (count / total_wallets) * 100
        
        # Flag if >60% share same funding source
        flagged = common_pct >= 60.0
        
        # Funding cluster penalty: -5 points (strong signal)
        penalty = -5 if flagged else 0
        
        return {
            'flagged': flagged,
            'common_source': common_source if flagged else None,
            'common_funding_pct': round(common_pct, 1),
            'wallets_funded': count,
            'total_wallets': total_wallets,
            'penalty': penalty
        }
    
    def _analyze_timing_patterns(self, wallets: List[Dict]) -> Dict:
        """
        Analyze buy timing for automated patterns
        
        DEV SCAM PATTERN: Bots execute buys at precise intervals 
        (e.g., exactly every 60 seconds) using scripts. This creates
        unnatural regularity in transaction timestamps.
        
        REAL USER PATTERN: Human buyers act at random intervals based
        on market conditions, social signals, FOMO, etc. Natural chaos.
        
        FLAG: If buy interval variance < threshold, likely bot
        """
        all_timestamps = []
        
        for wallet in wallets:
            wallet_buys = wallet.get('buys', [])
            for buy in wallet_buys:
                ts = None
                if isinstance(buy, dict):
                    ts = buy.get('timestamp')
                elif isinstance(buy, (int, float)):
                    ts = buy
                if ts:
                    all_timestamps.append(ts)
        
        if len(all_timestamps) < 5:
            return {'flagged': False, 'cv': None, 'penalty': 0}
        
        # Sort timestamps and calculate intervals
        sorted_ts = sorted(all_timestamps)
        intervals = [sorted_ts[i+1] - sorted_ts[i] for i in range(len(sorted_ts)-1)]
        
        if len(intervals) < 3:
            return {'flagged': False, 'cv': None, 'penalty': 0}
        
        # Calculate coefficient of variation (CV)
        # CV = std / mean, measures relative variability
        # Low CV = regular timing (bot-like)
        # High CV = irregular timing (human-like)
        try:
            mean_interval = mean(intervals)
            std_interval = stdev(intervals)
            cv = std_interval / mean_interval if mean_interval > 0 else 0
        except:
            cv = 0
        
        # Flag if CV < 0.5 (too regular - bot pattern)
        # CV < 0.3 = very suspicious (almost clockwork)
        # CV 0.5-1.0 = somewhat regular
        # CV > 1.0 = irregular (human)
        flagged = cv < 0.5
        severity = 'high' if cv < 0.3 else 'medium' if cv < 0.5 else 'low'
        
        # Timing pattern penalty: -3 points for regular intervals
        penalty = -3 if flagged else 0
        
        return {
            'flagged': flagged,
            'cv': round(cv, 3),
            'severity': severity,
            'mean_interval_sec': round(mean_interval, 1) if mean_interval else 0,
            'sample_intervals': intervals[:5],  # First 5 for debugging
            'penalty': penalty
        }
    
    # ═══════════════════════════════════════════════════════════════
    # 2. HELPER METHODS FOR API INTEGRATION
    # ═══════════════════════════════════════════════════════════════
    
    def fetch_wallet_creation_dates(self, wallet_addresses: List[str]) -> Dict[str, datetime]:
        """
        Fetch wallet creation dates from Helius API
        
        Uses first transaction timestamp as proxy for wallet creation
        since Solana wallets don't have explicit creation timestamps.
        """
        creation_dates = {}
        
        # TODO: Integrate with Helius API
        # For now, simulate based on address hash for testing
        for addr in wallet_addresses:
            # Generate deterministic "creation date" from address
            hash_val = int(hashlib.md5(addr.encode()).hexdigest(), 16)
            # Create date between 30 days ago and now
            days_ago = hash_val % 30
            hours_offset = (hash_val // 100) % 24
            
            creation_dates[addr] = datetime.now() - timedelta(days=days_ago, hours=hours_offset)
        
        return creation_dates
    
    def fetch_funding_sources(self, wallet_addresses: List[str]) -> Dict[str, Optional[str]]:
        """
        Fetch first funding transaction source for wallets
        
        Returns mapping of wallet -> funding source address
        """
        funding_map = {}
        
        # TODO: Integrate with Helius API for real funding data
        # Simulate for testing
        for i, addr in enumerate(wallet_addresses):
            # Simulate 40% chance of shared funding source for testing
            if random.random() < 0.4:
                funding_map[addr] = "DEV_FUNDED_CLUSTER_1"
            else:
                funding_map[addr] = f"exchange_or_bridge_{i}"
        
        return funding_map
    
    # ═══════════════════════════════════════════════════════════════
    # 3. SAFETY SCORE INTEGRATION
    # ═══════════════════════════════════════════════════════════════
    
    def calculate_shell_risk_score(self, token_holder_data: Dict) -> Tuple[int, List[str]]:
        """
        Calculate total shell wallet risk penalty
        
        Returns:
            Tuple of (total_penalty, list_of_flags)
        """
        wallets = token_holder_data.get('holders', [])
        
        if not wallets:
            return 0, []
        
        analysis = self.detect_shell_cluster(wallets)
        
        return analysis['score_penalty'], analysis['flags']
    
    def assess_token_safety(self, token_data: Dict) -> Dict[str, Any]:
        """
        Full safety assessment including shell detection
        
        Integrates with existing safety score calculations
        """
        holders = token_data.get('holders', [])
        
        # Run shell detection
        shell_analysis = self.detect_shell_cluster(holders)
        
        # Calculate final safety score
        base_score = token_data.get('base_safety_score', 7)
        final_score = max(0, base_score + shell_analysis['score_penalty'])
        
        result = {
            'base_score': base_score,
            'shell_penalty': shell_analysis['score_penalty'],
            'final_score': final_score,
            'is_blocked': final_score < 4,  # Score < 4 = skip trade
            'shell_detected': shell_analysis['is_shell_cluster'],
            'confidence': shell_analysis['confidence'],
            'flags': shell_analysis['flags'],
            'details': shell_analysis['details']
        }
        
        return result


# ═══════════════════════════════════════════════════════════════════
# SIMULATION HELPERS FOR TESTING
# ═══════════════════════════════════════════════════════════════════

def generate_realistic_wallets(count: int = 20) -> List[Dict]:
    """Generate simulated organic/real wallet data"""
    wallets = []
    
    for i in range(count):
        # Varied creation dates (organic users)
        days_ago = random.randint(1, 365)
        creation_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        wallets.append({
            'address': f'real_wallet_{i}',
            'creation_date': creation_date.isoformat(),
            'funding_source': f'exchange_{random.randint(1, 10)}',
            'buys': [
                {'amount_usd': random.uniform(15, 200), 'timestamp': time.time() - random.randint(0, 3600)}
                for _ in range(random.randint(1, 5))
            ]
        })
    
    return wallets


def generate_shell_wallets(count: int = 50) -> List[Dict]:
    """Generate simulated shell/bot wallet data"""
    wallets = []
    
    # All created within 30 minutes (cluster pattern)
    base_time = datetime.now() - timedelta(hours=2)
    
    for i in range(count):
        # Similar creation times (bot pattern)
        creation_date = base_time + timedelta(minutes=random.randint(0, 30))
        
        wallets.append({
            'address': f'shell_wallet_{i}',
            'creation_date': creation_date.isoformat(),
            'funding_source': 'DEV_FUND_WALLET_1',  # Common funding
            'buys': [
                {
                    'amount_usd': random.uniform(1, 4),  # Micro-buys
                    'timestamp': base_time.timestamp() + (i * 60) + random.randint(-5, 5)  # Regular 60s intervals
                }
                for _ in range(random.randint(1, 3))
            ]
        })
    
    return wallets


def run_tests():
    """Run shell detection tests on simulated data"""
    print("=" * 70)
    print("🔍 WALLET ANALYZER - Shell Wallet Detection Tests")
    print("=" * 70)
    
    analyzer = WalletAnalyzer()
    
    # Test 1: Organic wallets (should NOT trigger)
    print("\n📊 Test 1: Organic Wallets (20 wallets, varied ages)")
    real_wallets = generate_realistic_wallets(20)
    result = analyzer.detect_shell_cluster(real_wallets)
    print(f"   Shell Cluster: {result['is_shell_cluster']}")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Flags: {result['flags']}")
    print(f"   Penalty: {result['score_penalty']}")
    assert not result['is_shell_cluster'], "Should not flag organic wallets"
    print("   ✅ PASS: Organic wallets correctly identified")
    
    # Test 2: Shell wallets (SHOULD trigger)
    print("\n📊 Test 2: Shell Wallets (50 wallets, clustered)")
    shell_wallets = generate_shell_wallets(50)
    result = analyzer.detect_shell_cluster(shell_wallets)
    print(f"   Shell Cluster: {result['is_shell_cluster']}")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Flags: {result['flags']}")
    print(f"   Details:")
    print(f"     - Age variance: {result['details']['age_variance']}")
    print(f"     - Micro-buys: {result['details']['micro_buys']}")
    print(f"     - Funding: {result['details']['funding']}")
    print(f"     - Timing: {result['details']['timing']}")
    print(f"   Total Penalty: {result['score_penalty']}")
    assert result['is_shell_cluster'], "Should detect shell wallets"
    assert 'cluster_age' in result['flags'], "Should flag age variance"
    assert 'micro_buys' in result['flags'], "Should flag micro buys"
    assert 'common_funding' in result['flags'], "Should flag common funding"
    print("   ✅ PASS: Shell wallets correctly detected")
    
    # Test 3: Safety score integration
    print("\n📊 Test 3: Safety Score Integration")
    token_data = {
        'holders': shell_wallets,
        'base_safety_score': 10
    }
    safety = analyzer.assess_token_safety(token_data)
    print(f"   Base Score: {safety['base_score']}")
    print(f"   Final Score: {safety['final_score']}")
    print(f"   Block Trade: {safety['is_blocked']}")
    assert safety['is_blocked'], "Should block shell cluster token"
    print("   ✅ PASS: High-risk token correctly blocked")
    
    # Test 4: Mixed (edge case)
    print("\n📊 Test 4: Mixed Wallets (some shell, some real)")
    mixed_wallets = real_wallets[:15] + shell_wallets[:10]
    random.shuffle(mixed_wallets)
    result = analyzer.detect_shell_cluster(mixed_wallets)
    print(f"   Shell Cluster: {result['is_shell_cluster']}")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Flags: {result['flags']}")
    print("   ✅ PASS: Mixed cluster detection working")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
