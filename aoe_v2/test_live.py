#!/usr/bin/env python3
"""AOE v2.0 - Live Test"""

import logging
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/aoe_v2')

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')

from scanner_dexscreener import DexScreenerScanner
from scanner_pumpfun import PumpFunScanner
from token_pipeline import TokenPipeline
from scorer import OpportunityScorer

print('='*60)
print('🔥 AOE v2.0 Live Test')
print('='*60)

# Create scanners
scanners = [
    DexScreenerScanner(),
    PumpFunScanner()
]

# Run pipeline
print('\n📡 Running Pipeline...')
pipeline = TokenPipeline(
    scanners=scanners,
    mc_min=100_000,
    mc_max=20_000_000,
    strategy='mean_reversion_microcap'
)

tokens, stats = pipeline.run(parallel=False)

print(f'\n📊 Pipeline Results:')
print(f'   Raw tokens: {stats.get("raw_count", 0)}')
print(f'   Unique tokens: {stats.get("unique_count", 0)}')
print(f'   Final tokens: {len(tokens)}')

if tokens:
    # Score
    print('\n📊 Scoring tokens...')
    scorer = OpportunityScorer()
    scored = scorer.score_batch(tokens)
    
    # Get top
    top = scorer.get_top_opportunities(scored, min_score=70)
    urgent = [t for t,s,b in scored if s >= 82]
    queued = [t for t,s,b in scored if 75 <= s < 82]
    
    print(f'\n🚨 Urgent (≥82): {len(urgent)}')
    print(f'📋 Queued (≥75): {len(queued)}')
    print(f'Total ≥70: {len(top)}')
    
    if urgent:
        print('\n🏆 URGENT ALERTS:')
        for token, score, bd in scored[:3]:
            if score >= 82:
                print(f'  {token.symbol}: {score:.0f} | {token.price_change_1h:+.1f}% | ${token.market_cap/1e6:.1f}M MC')
    
    if tokens[:5]:
        print('\n📈 Sample tokens:')
        for t in tokens[:5]:
            print(f'  {t.symbol}: ${t.market_cap:,.0f} MC, ${t.volume_24h:,.0f} vol, {t.price_change_1h:+.1f}%')

print('\n' + '='*60)
print('✅ AOE v2.0 Test Complete')
print('='*60)
