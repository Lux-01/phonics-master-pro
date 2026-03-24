#!/usr/bin/env python3
"""
Update Trade Outcome
Simple CLI to update outcomes for ALOE learning.

Usage:
  python3 update_outcome.py --signal SIG-20260319-xxx --outcome PROFIT --profit 15
  python3 update_outcome.py --signal SIG-20260319-xxx --outcome RUG --lesson "Too new"
"""

import argparse
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/outcome-tracker')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/pattern-extractor')

from trading_outcome_tracker import update_trade_outcome, get_stats
from rug_pattern_extractor import add_rug


def main():
    parser = argparse.ArgumentParser(description='Update trade outcome for ALOE learning')
    parser.add_argument('--signal', required=True, help='Signal ID (e.g., SIG-20260319-xxx)')
    parser.add_argument('--outcome', required=True, 
                       choices=['PROFIT', 'LOSS', 'RUG', 'PENDING'],
                       help='Trade outcome')
    parser.add_argument('--profit', type=float, default=0, help='Profit percentage')
    parser.add_argument('--lesson', help='Lesson learned (for losses/rugs)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_stats()
        print("📊 OUTCOME STATISTICS")
        print("=" * 50)
        print(f"Total signals: {stats['total_signals']}")
        print(f"Rugs: {stats['rugs']}")
        print(f"Profits: {stats['profits']}")
        print(f"Losses: {stats['losses']}")
        print(f"Pending: {stats['pending']}")
        print()
        print(f"Grade A accuracy: {stats['grade_a_accuracy']}")
        print()
        print("Patterns learned:")
        for name, count in stats['patterns_learned'].items():
            print(f"  • {name}: {count}")
        return
    
    # Update outcome
    print(f"📝 Updating outcome for {args.signal}")
    print(f"   Status: {args.outcome}")
    
    if args.outcome == "RUG":
        print(f"   Recording as RUG pattern...")
        # Will auto-add to patterns
    
    success = update_trade_outcome(
        signal_id=args.signal,
        status=args.outcome,
        profit_pct=args.profit if args.outcome == "PROFIT" else None,
        lesson=args.lesson
    )
    
    if success:
        print(f"✅ Outcome updated successfully!")
        print(f"   ALOE will learn from this outcome")
        
        if args.outcome == "RUG" and args.lesson:
            print(f"   Lesson recorded: {args.lesson}")
        
        # Show updated stats
        stats = get_stats()
        print(f"\n📈 Grade A accuracy: {stats['grade_a_accuracy']}")
    else:
        print(f"❌ Failed to update - signal not found")
        print(f"   Check signal ID with: python3 update_outcome.py --stats")


if __name__ == "__main__":
    main()
