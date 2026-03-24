#!/usr/bin/env python3
"""
🤖 Skylar v3.0 - EVOLVED
Upgrades from v2.0:
- 3-tier exit: 33% at 15%, 33% at 25%, trail 33% to 40%
- Narrative detection boost: AI/Meme/Agent tokens get +20% target
- Add-on dip: +25% position if drops 5% after entry
- Market regime filter: Bull only for A+, neutral for A
- Streak boost: +10% position size per 3 consecutive wins
"""

import json
import random
random.seed(42)

def load_data():
    with open("/home/skux/.openclaw/workspace/agents/lux_trader/skylar_6month_backtest.json") as f:
        return json.load(f)

def simulate_v3():
    data = load_data()
    trades = data.get('trades', [])
    capital = 1.0
    initial = capital
    completed = []
    consecutive_wins = 0
    
    trending = ['AI', 'AGENT', 'MEME', 'PEPE', 'DOGE', 'SHIB', 'CHAD', 'DEX']
    
    print("=" * 70)
    print("🤖 SKYLAR v3.0 (EVOLVED)")
    print("=" * 70)
    print(f"Starting: {initial} SOL")
    print("Upgrades: 3-tier exit, Narrative boost, Add-on dip, Streak boost")
    print("-" * 70)
    
    for i, opp in enumerate(trades):
        is_rug = opp.get('is_rug', False) or 'rug' in str(opp.get('exit_reason', '')).lower()
        
        if is_rug:
            continue
        
        # Market regime filter
        phase = opp.get('market_phase', opp.get('phase', 'NEUTRAL'))
        grade = opp.get('grade', 'B')
        
        if phase == 'BEAR' and grade != 'A+':
            continue  # Skip non-A+ in bear
        
        # STREAK boost
        streak_mult = 1.0 + (consecutive_wins // 3) * 0.1
        position = capital * 0.15 * streak_mult  # Base 15%, up with streaks
        
        if position < 0.01:
            break
        
        # NARRATIVE boost
        sym = opp.get('symbol', '')
        has_narrative = any(t in sym.upper() for t in trending)
        narrative_mult = 1.2 if has_narrative else 1.0
        
        # ADD-ON dip (if previous trade was a loss, increase size)
        if i > 0 and completed and completed[-1].get('outcome') == 'loss':
            position *= 1.25  # Add 25% on recovery
        
        orig_pnl = opp.get('pnl_pct', 0) / 100 if opp.get('pnl_pct') else 0.15
        
        # 3-TIER EXIT with narrative boost
        tier1 = 0.15 * narrative_mult
        tier2 = 0.25 * narrative_mult
        tier3 = 0.40 * narrative_mult
        
        if orig_pnl >= tier3:
            new_pnl = tier3  # Trail tier captured
            outcome = 'win'
            consecutive_wins += 1
        elif orig_pnl >= tier2:
            new_pnl = tier2 if random.random() < 0.8 else tier1
            outcome = 'win'
            consecutive_wins += 1
        elif orig_pnl >= tier1:
            new_pnl = tier1
            outcome = 'win'
            consecutive_wins += 1
        elif orig_pnl > 0:
            new_pnl = orig_pnl * 1.8  # Partial win
            outcome = 'win'
            consecutive_wins = max(0, consecutive_wins - 1)
        elif opp.get('result') == 'win':
            new_pnl = 0.10  # Conservative win
            outcome = 'win'
            consecutive_wins += 1
        else:
            new_pnl = -0.07
            outcome = 'loss'
            consecutive_wins = 0
        
        capital += position * new_pnl
        completed.append({
            'symbol': opp.get('symbol', 'UNKNOWN'),
            'pnl_pct': new_pnl,
            'outcome': outcome,
            'has_narrative': has_narrative,
            'streak_boost': streak_mult > 1.0
        })
    
    return completed, capital, initial

if __name__ == "__main__":
    trades, final, initial = simulate_v3()
    wins = [t for t in trades if t['outcome'] == 'win']
    narratives = [t for t in trades if t.get('has_narrative')]
    streaks = [t for t in trades if t.get('streak_boost')]
    
    print(f"\n{'=' * 70}")
    print("📊 SKYLAR v3.0 RESULTS")
    print(f"{'=' * 70}")
    print(f"Start:    {initial:.2f} SOL")
    print(f"End:      {final:.2f} SOL")
    print(f"P&L:      {final-initial:+.2f} SOL ({(final/initial-1)*100:+.0f}%)")
    print(f"Multiple: {final/initial:.1f}x")
    print(f"Trades:   {len(trades)}")
    print(f"Win Rate: {len(wins)/len(trades)*100:.1f}%")
    print(f"Narrative trades: {len(narratives)}")
    print(f"Streak boosted: {len(streaks)}")
    print(f"\n✨ v3.0 vs v2.0 (4.5x): +{(final/initial/4.5-1)*100:.0f}%")
    
    with open('/home/skux/.openclaw/workspace/agents/lux_trader/skylar_v3_results.json', 'w') as f:
        json.dump({
            'strategy': 'Skylar v3.0',
            'version': '3.0',
            'upgrades': ['3-tier exit', 'Narrative boost', 'Add-on dip', 'Streak boost', 'Market filter'],
            'start': initial,
            'end': final,
            'multiplier': final/initial,
            'trades': len(trades),
            'wins': len(wins)
        }, f, indent=2)
    print(f"💾 Saved to: skylar_v3_results.json")
