#!/usr/bin/env python3
"""
🛡️ Rug-Radar v3.1 SHELL WALLET DEMO
Demonstrates shell wallet detection with injected shell cluster scenarios
"""

import json
import random
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from wallet_analyzer import WalletAnalyzer, generate_shell_wallets, generate_realistic_wallets
from datetime import datetime, timedelta

random.seed(42)


def create_demo_trades_with_shells():
    """Create demo trades with various shell wallet scenarios"""
    
    trades = []
    
    # Scenario 1: Clean token (A+ grade, no shells)
    trades.append({
        'token': 'BONK_REAL',
        'grade': 'A+',
        'mcap': 45000,
        'age_hours': 8,
        'is_rug': False,
        'entry_reason': 'volume spike',
        'holders': generate_realistic_wallets(35),
        'expected_score': '9+ (clean)',
        'description': 'Real organic holder base'
    })
    
    # Scenario 2: Low-grade with micro-buys
    shell_micro = generate_shell_wallets(40)
    for w in shell_micro:
        w['buys'] = [{'amount_usd': random.uniform(1, 3), 'timestamp': datetime.now().timestamp()}]
    
    real_holders = generate_realistic_wallets(15)
    all_holders = shell_micro + real_holders
    random.shuffle(all_holders)
    
    trades.append({
        'token': 'SUSHI_BOT',
        'grade': 'A',
        'mcap': 25000,
        'age_hours': 3,
        'is_rug': False,
        'entry_reason': 'momentum',
        'holders': all_holders,
        'expected_score': '3-4 (borderline)',
        'description': 'Mixed: 40 shell wallets with micro-buys + 15 real'
    })
    
    # Scenario 3: Full shell cluster (all 4 flags)
    full_shell = generate_shell_wallets(60)
    
    trades.append({
        'token': 'FAKE_CLUSTER',
        'grade': 'A',
        'mcap': 35000,
        'age_hours': 2,
        'is_rug': True,
        'entry_reason': 'volume spike',
        'holders': full_shell,
        'expected_score': 'BLOCKED (<4)',
        'description': 'Full shell cluster: 60 bot wallets'
    })
    
    # Scenario 4: High safety but light shell activity
    light_shell = generate_shell_wallets(15) + generate_realistic_wallets(45)
    
    trades.append({
        'token': 'MIXED_OK',
        'grade': 'A+',
        'mcap': 60000,
        'age_hours': 12,
        'is_rug': False,
        'entry_reason': 'volume spike',
        'holders': light_shell,
        'expected_score': '6-7 (safe)',
        'description': 'Mostly organic with 15 suspicious wallets'
    })
    
    # Scenario 5: Perfect organic token
    trades.append({
        'token': 'BULL_RUNNER',
        'grade': 'A+',
        'mcap': 55000,
        'age_hours': 6,
        'is_rug': False,
        'entry_reason': 'volume spike',
        'holders': generate_realistic_wallets(50),
        'expected_score': '11 (excellent)',
        'description': 'Perfect organic token'
    })
    
    return trades


def run_shell_demo():
    """Run the shell wallet detection demo"""
    
    print("=" * 80)
    print("🛡️ RUG-RADAR v3.1 SHELL WALLET DETECTION DEMO")
    print("=" * 80)
    print()
    print("This demo shows how v3.1 analyzes holder wallets to detect shell clusters.")
    print()
    
    analyzer = WalletAnalyzer()
    trades = create_demo_trades_with_shells()
    
    print(f"{'Token':<15} {'Grade':<6} {'MCap':<10} {'Base':<6} {'Penalty':<8} {'Final':<6} {'Status':<12} {'Flags'}")
    print("=" * 100)
    
    results = []
    blocked_count = 0
    
    for trade in trades:
        holders = trade['holders']
        
        # Calculate base score
        base_score = 0
        mcap = trade['mcap']
        if 5000 <= mcap <= 80000:
            base_score += 3
        
        age = trade['age_hours']
        if 1 <= age <= 24:
            base_score += 2
        
        if not trade['is_rug']:
            base_score += 3
        
        if trade['grade'] == 'A+':
            base_score += 3
        elif trade['grade'] == 'A':
            base_score += 2
        
        entry = trade['entry_reason'].lower()
        if 'volume' in entry:
            base_score += 2
        
        # Shell analysis
        shell_result = analyzer.detect_shell_cluster(holders)
        final_score = max(0, base_score + shell_result['score_penalty'])
        is_blocked = final_score < 4
        
        if is_blocked:
            blocked_count += 1
            status = "🚫 BLOCKED"
        elif len(shell_result['flags']) > 0:
            status = "⚠️  WARNING"
        else:
            status = "✅ SAFE"
        
        flags_str = ", ".join(shell_result['flags']) if shell_result['flags'] else "None"
        
        print(f"{trade['token']:<15} {trade['grade']:<6} ${mcap/1000:.1f}K{'':<5} "
              f"{base_score:<6} {shell_result['score_penalty']:<8} {final_score:<6} "
              f"{status:<12} {flags_str}")
        
        results.append({
            'token': trade['token'],
            'description': trade['description'],
            'base_score': base_score,
            'penalty': shell_result['score_penalty'],
            'final_score': final_score,
            'blocked': is_blocked,
            'flags': shell_result['flags'],
            'details': shell_result['details']
        })
    
    print("=" * 100)
    print()
    
    # Detailed breakdown
    print("\n📊 DETAILED SHELL ANALYSIS:")
    print("=" * 80)
    
    for r in results:
        print(f"\n🔍 {r['token']}")
        print(f"   Description: {r['description']}")
        print(f"   Base Score: {r['base_score']} → Final Score: {r['final_score']}")
        print(f"   Shell Penalty: {r['penalty']} points")
        print(f"   Status: {'🚫 BLOCKED (safety < 4)' if r['blocked'] else '⚠️  ALLOWED (with caution)' if r['flags'] else '✅ CLEAN'}")
        
        if r['details']:
            print(f"   Detection Details:")
            if r['details'].get('age_variance', {}).get('flagged'):
                av = r['details']['age_variance']
                print(f"     - ⚠️  Age Variance: {av['variance_hours']:.3f} hrs (threshold: 1hr)")
                print(f"       → {av['wallet_count']} wallets with clustered creation")
            if r['details'].get('micro_buys', {}).get('flagged'):
                mb = r['details']['micro_buys']
                print(f"     - ⚠️  Micro-Buys: ${mb['avg_buy_usd']:.2f} avg (threshold: $5)")
                print(f"       → {mb['buy_count']} suspicious small purchases")
            if r['details'].get('funding', {}).get('flagged'):
                fc = r['details']['funding']
                print(f"     - ⚠️  Shared Funding: {fc['common_funding_pct']:.0f}% from same source")
                print(f"       → {fc['wallets_funded']} wallets funded by: {fc['common_source'][:20]}...")
            if r['details'].get('timing', {}).get('flagged'):
                tp = r['details']['timing']
                print(f"     - ⚠️  Regular Timing: CV={tp['cv']:.3f} (threshold: 0.5)")
                print(f"       → Bot-like {tp['mean_interval_sec']:.0f}s interval pattern")
    
    print("\n" + "=" * 80)
    print("🎯 SUMMARY:")
    print("=" * 80)
    print(f"   Total trades analyzed: {len(results)}")
    print(f"   🚫 Blocked (safety < 4): {blocked_count}")
    print(f"   ⚠️  With shell flags: {sum(1 for r in results if r['flags'])}")
    print(f"   ✅ Clean execution: {sum(1 for r in results if not r['flags'])}")
    print()
    
    # Red flag reference
    print("📋 RED FLAG REFERENCE:")
    print("   • cluster_age_flag:     -4 pts (wallets created within 1 hour)")
    print("   • micro_buy_flag:       -3 pts (avg buy <$5 USD)")
    print("   • funding_cluster_flag: -5 pts (>60% same funding source)")
    print("   • timing_pattern_flag:  -3 pts (regular intervals, CV<0.5)")
    print()
    print("   Trade blocked if: Final safety_score < 4")
    print("=" * 80)
    
    # Save demo results
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/shell_detection_demo.json', 'w') as f:
        json.dump({
            'demo_version': 'v3.1',
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total': len(results),
                'blocked': blocked_count,
                'flagged': sum(1 for r in results if r['flags']),
                'clean': sum(1 for r in results if not r['flags'])
            }
        }, f, indent=2)
    
    print("\n💾 Demo results saved to: shell_detection_demo.json")


if __name__ == "__main__":
    run_shell_demo()
