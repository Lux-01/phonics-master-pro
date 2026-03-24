#!/usr/bin/env python3
"""
Unified Scanner Wrapper
Simple interface to the unified scanner system
"""

import sys
import argparse
from pathlib import Path

# Add unified scanner to path
sys.path.insert(0, str(Path(__file__).parent / "skills" / "unified-scanner"))

from scanner_core import UnifiedScanner, TokenData


def main():
    parser = argparse.ArgumentParser(description="Unified Token Scanner")
    parser.add_argument("--strategy", choices=["quick", "fundamental", "chart", "comprehensive"],
                       default="comprehensive", help="Scanning strategy")
    parser.add_argument("--min-grade", default="B", help="Minimum grade filter")
    parser.add_argument("--min-liquidity", type=float, default=10000,
                       help="Minimum liquidity in USD")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--format", choices=["json", "table"], default="table",
                       help="Output format")
    
    args = parser.parse_args()
    
    print("🔍 Unified Token Scanner")
    print("=" * 60)
    
    # Initialize scanner
    scanner = UnifiedScanner()
    
    # Run scan
    print(f"Running {args.strategy} scan...")
    results = scanner.scan(strategy=args.strategy)
    
    # Filter results
    filtered = [
        t for t in results.tokens
        if t.grade in ['A', 'A+', 'A-', args.min_grade]
        and t.liquidity >= args.min_liquidity
    ]
    
    # Output
    if args.format == "json":
        import json
        output = {
            "tokens": [t.to_dict() for t in filtered],
            "scanner_used": results.scanner_used,
            "execution_time_ms": results.execution_time_ms,
            "timestamp": results.timestamp.isoformat()
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(json.dumps(output, indent=2))
    else:
        # Table format
        print(f"\nFound {len(filtered)} tokens:")
        print("-" * 80)
        print(f"{'Symbol':<10} {'Grade':<8} {'Score':<8} {'Age(h)':<8} {'Liquidity':<15} {'MCap':<15}")
        print("-" * 80)
        
        for token in filtered[:20]:  # Show top 20
            print(f"{token.symbol:<10} {token.grade:<8} {token.score:<8.1f} "
                  f"{token.age_hours:<8.1f} ${token.liquidity:<14,.0f} "
                  f"${token.market_cap:<14,.0f}")
        
        print("-" * 80)
        print(f"Scanner: {results.scanner_used} | Time: {results.execution_time_ms:.0f}ms")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
