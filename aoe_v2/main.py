#!/usr/bin/env python3
"""
AOE v2.1 - Main Entry Point (Upgraded)
Orchestrates the complete opportunity detection pipeline.
"""

import json
import os
import sys
import argparse
import logging
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

# Load dotenv from current directory first
try:
    from dotenv import load_dotenv
    # Try current directory first, then home
    env_paths = [
        Path(__file__).parent / ".env",
        Path.home() / ".env",
        Path("/home/skux/.openclaw/workspace/aoe_v2/.env")
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

# Also try manual loading if dotenv isn't available
if not os.getenv('BIRDEYE_API_KEY'):
    env_file = Path("/home/skux/.openclaw/workspace/aoe_v2/.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from scanner_base import Token
from scanner_dexscreener import DexScreenerScanner
from scanner_birdeye import BirdeyeScanner
from scanner_pumpfun import PumpFunScanner
from token_pipeline import TokenPipeline
from scorer import OpportunityScorer
from alerts import AlertManager


# File paths
WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"
STATE_FILE = MEMORY_DIR / "aoe_state.json"
HISTORY_FILE = MEMORY_DIR / "aoe_history.json"  # New: score history
CSV_FILE = Path(__file__).parent / "data" / "scores.csv"  # New: CSV export
CONFIG_FILE = MEMORY_DIR / "aoe_config.json"
QUEUE_FILE = MEMORY_DIR / "aoe_queue.json"
ALERT_LOG = MEMORY_DIR / "aoe_alerts.log"
DATA_DIR = Path(__file__).parent / "data"


def load_config() -> Dict[str, Any]:
    """Load AOE configuration."""
    default_config = {
        "strategy": "mean_reversion_microcap",
        "market_cap": {
            "min": 100000,
            "max": 20000000
        },
        "volume": {
            "min_24h": 1000
        },
        "scoring": {
            "urgent_threshold": 82,
            "queue_threshold": 75
        },
        "filters": {
            "exclude_stablecoins": True,
            "min_liquidity": 5000,
            "max_price_change_24h": 500
        },
        "telegram": {
            "enabled": True,
            "token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID")
        },
        "schedule": {
            "interval_minutes": 30,
            "active_hours": "00:00-08:00"
        }
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            logging.warning(f"Failed to load config: {e}, using defaults")
    
    return default_config


def save_state(state: Dict):
    """Save AOE state."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_state() -> Dict:
    """Load AOE state."""
    default_state = {
        "lastCheck": 0,
        "lastCheckTime": None,
        "totalScanned": 0,
        "totalOpportunities": 0,
        "alertsSent": 0,
        "queueSize": 0
    }
    
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
                for key, value in default_state.items():
                    if key not in state:
                        state[key] = value
                return state
        except:
            pass
    
    return default_state


def save_score_history(scan_results: Dict):
    """Save detailed score history for trend analysis."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except:
            history = []
    
    # Add current scan
    history.append({
        "timestamp": datetime.now().isoformat(),
        **scan_results
    })
    
    # Keep only last 100 scans
    history = history[-100:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def save_csv_export(scored: List[tuple]):
    """Export scores to CSV for manual analysis."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'timestamp', 'token', 'symbol', 'address', 'score', 'potential',
            'probability', 'speed', 'fit', 'alpha', 'risk', 'effort',
            'market_cap', 'volume_24h', 'price_ch_1h', 'price_ch_24h', 'liquidity'
        ])
        
        timestamp = datetime.now().isoformat()
        for token, score, breakdown in scored:
            writer.writerow([
                timestamp,
                token.name if hasattr(token, 'name') else '',
                token.symbol,
                token.address,
                round(score, 2),
                round(breakdown.potential, 1),
                round(breakdown.probability, 1),
                round(breakdown.speed, 1),
                round(breakdown.fit, 1),
                round(breakdown.alpha, 1),
                round(breakdown.risk, 1),
                round(breakdown.effort, 1),
                token.market_cap,
                token.volume_24h,
                getattr(token, 'price_change_1h', 0),
                getattr(token, 'price_change_24h', 0),
                getattr(token, 'liquidity', 0)
            ])


def print_detailed_scores(scored: List[tuple], min_score: int = 50):
    """Print detailed score breakdown in a table format."""
    logger = logging.getLogger("aoe.main")
    
    # Filter and sort by score
    filtered = [(t, s, b) for t, s, b in scored if s >= min_score]
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    if not filtered:
        logger.info("   No tokens scored ≥%d", min_score)
        return
    
    logger.info("\n" + "=" * 100)
    logger.info("📊 DETAILED SCORE BREAKDOWN (≥%d)", min_score)
    logger.info("=" * 100)
    logger.info(f"{'Symbol':<10} {'Score':<6} {'Pot':<5} {'Prob':<5} {'Speed':<5} {'Fit':<5} {'Alpha':<5} {'Risk':<5} {'Status':<10} {'Market Cap'}")
    logger.info("-" * 100)
    
    for token, score, b in filtered:
        status = "🚨 URGENT" if score >= 82 else "📋 QUEUE" if score >= 75 else "📊 MONITOR"
        logger.info(f"{token.symbol:<10} {score:<6.0f} {b.potential:<5.0f} {b.probability:<5.0f} "
                   f"{b.speed:<5.0f} {b.fit:<5.0f} {b.alpha:<5.0f} {b.risk:<5.0f} {status:<10} ${token.market_cap/1000:.0f}K")
        
        # Show extra details for high scorers
        if score >= 75:
            logger.info(f"          └─ ${token.volume_24h/1000:.0f}K vol | "
                       f"1h: {getattr(token, 'price_change_1h', 0):+.1f}% | "
                       f"24h: {getattr(token, 'price_change_24h', 0):+.1f}%")
    
    logger.info("-" * 100)


def compare_with_previous(scored: List[tuple]):
    """Compare with previous scan to show trends."""
    logger = logging.getLogger("aoe.main")
    
    if not HISTORY_FILE.exists():
        return
    
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        
        if not history:
            return
        
        prev_scan = history[-1]
        prev_tokens = {item.get('symbol'): item.get('score') 
                      for item in prev_scan.get('all_scores', [])}
        
        if prev_tokens:
            logger.info("\n📈 SCORE TRENDS (vs previous scan):")
            
            for token, score, _ in scored:
                if token.symbol in prev_tokens:
                    prev_score = prev_tokens[token.symbol]
                    change = score - prev_score
                    if abs(change) > 3:  # Only show significant changes
                        arrow = "↑" if change > 0 else "↓"
                        logger.info(f"   {token.symbol}: {prev_score:.0f} → {score:.0f} ({arrow}{abs(change):.0f})")
    
    except Exception as e:
        logger.debug(f"Could not compare with previous: {e}")


def setup_logging(level=logging.INFO):
    """Configure logging."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def run_scan(config: Dict, dry_run: bool = False) -> Dict[str, Any]:
    """Run complete AOE scan pipeline."""
    logger = logging.getLogger("aoe.main")
    
    logger.info("=" * 70)
    logger.info("🔥 AOE v2.1 - AUTONOMOUS OPPORTUNITY ENGINE")
    logger.info(f"   Strategy: {config['strategy']}")
    logger.info(f"   MC Range: ${config['market_cap']['min']:,} - ${config['market_cap']['max']:,}")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    # Initialize scanners
    logger.info("\n📡 Initializing scanners...")
    scanners = []
    
    scanners.append(DexScreenerScanner())
    logger.info("   ✅ DexScreener scanner")
    
    birdeye_api_key = os.getenv('BIRDEYE_API_KEY')
    if birdeye_api_key:
        scanners.append(BirdeyeScanner(api_key=birdeye_api_key))
        logger.info(f"   ✅ Birdeye scanner (API: {birdeye_api_key[:8]}...)")
    else:
        logger.warning("   ⚠️  Birdeye: No API key found in environment")
        # Debug: show what's in env
        logger.debug(f"   Environment keys: {[k for k in os.environ.keys() if 'api' in k.lower()]}")
    
    scanners.append(PumpFunScanner())
    logger.info("   ✅ PumpFun scanner")
    
    logger.info(f"   Total scanners: {len(scanners)}")
    
    # Initialize pipeline
    pipeline = TokenPipeline(
        scanners=scanners,
        mc_min=config['market_cap']['min'],
        mc_max=config['market_cap']['max'],
        strategy=config['strategy'],
        data_dir=DATA_DIR
    )
    
    # Run pipeline
    logger.info("\n🔄 Running discovery pipeline...")
    try:
        tokens, pipe_stats = pipeline.run(parallel=True)
        logger.info(f"   ✅ Pipeline complete: {len(tokens)} tokens")
    except Exception as e:
        logger.error(f"   ❌ Pipeline failed: {e}")
        return {"success": False, "error": str(e)}
    
    # Score opportunities
    logger.info("\n📊 Scoring opportunities...")
    scorer = OpportunityScorer(strategy=config['strategy'])
    scored = scorer.score_batch(tokens)
    
    logger.info(f"   Scored {len(scored)} tokens")
    
    # NEW: Detailed score breakdown
    print_detailed_scores(scored, min_score=60)
    
    # NEW: Compare with previous
    compare_with_previous(scored)
    
    # Top opportunities
    top = scorer.get_top_opportunities(scored, min_score=75, max_results=20)
    urgent = [t for t, s, b in top if s >= config['scoring']['urgent_threshold']]
    queued = [t for t, s, b in top if config['scoring']['queue_threshold'] <= s < config['scoring']['urgent_threshold']]
    
    logger.info(f"\n   🚨 Urgent (≥{config['scoring']['urgent_threshold']}): {len(urgent)}")
    logger.info(f"   📋 Queued (≥{config['scoring']['queue_threshold']}): {len(queued)}")
    
    # Process alerts
    logger.info("\n🚨 Processing alerts...")
    alerts = AlertManager(
        telegram_token=config['telegram']['token'],
        telegram_chat_id=config['telegram']['chat_id'],
        queue_file=QUEUE_FILE,
        log_file=ALERT_LOG
    )
    
    if dry_run:
        logger.info("   [DRY RUN MODE - No alerts sent]")
    
    alert_stats = alerts.process_batch(top, dry_run=dry_run)
    
    # Update state
    state = load_state()
    state['lastCheck'] = int(start_time.timestamp())
    state['lastCheckTime'] = start_time.isoformat()
    state['totalScanned'] += pipe_stats['raw_count']
    state['totalOpportunities'] += len(top)
    state['alertsSent'] += alert_stats.get('alerted', 0)
    state['queueSize'] = alert_stats.get('queued', 0)
    
    save_state(state)
    
    # NEW: Save score history
    scan_results = {
        "timestamp": start_time.isoformat(),
        "tokens_scanned": pipe_stats['raw_count'],
        "urgent_count": len(urgent),
        "urgent_tokens": [(t.symbol, s) for t, s, b in urgent],
        "queued_count": len(queued),
        "queued_tokens": [(t.symbol, s) for t, s, b in queued],
        "all_scores": [{"symbol": t.symbol, "score": s} for t, s, b in scored]
    }
    save_score_history(scan_results)
    
    # NEW: CSV export
    save_csv_export(scored)
    logger.info(f"\n   📄 CSV export saved: {CSV_FILE}")
    
    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ AOE Scan Complete")
    logger.info("=" * 70)
    logger.info(f"   Duration: {elapsed:.1f}s")
    logger.info(f"   Tokens: {pipe_stats['raw_count']} raw → {pipe_stats['unique_count']} unique → {len(tokens)} final")
    logger.info(f"   Opportunities: {len(top)} (≥{config['scoring']['queue_threshold']})")
    logger.info(f"   🚨 Urgent: {len(urgent)}")
    logger.info(f"   📋 Queued: {len(queued)}")
    logger.info(f"   📊 Alerts sent: {alert_stats.get('alerted', 0)}")
    logger.info(f"   📄 CSV rows: {len(scored)}")
    
    if urgent:
        logger.info("\n   🏆 TOP URGENT OPPORTUNITIES:")
        for token, score, breakdown in urgent[:5]:
            logger.info(f"      {token.symbol}: {score:.0f} | {token.price_change_1h:+.1f}% | ${token.volume_24h/1000:.0f}K vol")
    
    logger.info("=" * 70)
    
    return {
        "success": True,
        "elapsed": elapsed,
        "tokens_scanned": pipe_stats['raw_count'],
        "tokens_unique": pipe_stats['unique_count'],
        "tokens_filtered": len(tokens),
        "opportunities_found": len(top),
        "urgent": len(urgent),
        "queued": len(queued),
        "alerts": alert_stats,
        "state": state
    }


def run_report():
    """Generate status report."""
    logger = logging.getLogger("aoe.main")
    
    state = load_state()
    config = load_config()
    
    logger.info("📊 AOE v2.1 Status Report")
    logger.info("=" * 50)
    
    # Config
    logger.info("\n⚙️  Configuration:")
    logger.info(f"   Strategy: {config['strategy']}")
    logger.info(f"   MC Range: ${config['market_cap']['min']:,} - ${config['market_cap']['max']:,}")
    logger.info(f"   Alert Thresholds: ≥{config['scoring']['urgent_threshold']} urgent, ≥{config['scoring']['queue_threshold']} queue")
    
    # State
    logger.info("\n📈 Statistics:")
    logger.info(f"   Total Scanned: {state.get('totalScanned', 0):,}")
    logger.info(f"   Total Opportunities: {state.get('totalOpportunities', 0)}")
    logger.info(f"   Alerts Sent: {state.get('alertsSent', 0)}")
    logger.info(f"   Queue Size: {state.get('queueSize', 0)}")
    
    last_check = state.get('lastCheck')
    if last_check:
        last_time = datetime.fromtimestamp(last_check)
        logger.info(f"   Last Check: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show history if exists
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
            logger.info(f"\n📚 Score History: {len(history)} scans")
            
            # Show daily summary
            daily_counts = defaultdict(int)
            for entry in history[-30:]:  # Last 30 entries
                day = entry.get('timestamp', '')[:10]
                daily_counts[day] += entry.get('urgent_count', 0)
            
            if daily_counts:
                logger.info("\n   🚨 Urgent opportunities by day (last 7 days):")
                for day, count in sorted(daily_counts.items())[-7:]:
                    logger.info(f"      {day}: {count} urgent")
        except Exception as e:
            logger.debug(f"Could not load history: {e}")
    
    # Queue
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
        opportunities = queue.get('opportunities', [])
        if opportunities:
            logger.info(f"\n📋 Top 5 Queue:")
            for opp in opportunities[:5]:
                logger.info(f"   {opp.get('symbol', '?')}: {opp.get('score', 0):.0f} (status: {opp.get('status', '?')})")
    
    # CSV file info
    if CSV_FILE.exists():
        import os
        size = os.path.getsize(CSV_FILE)
        logger.info(f"\n📄 CSV Export: {CSV_FILE.name} ({size/1024:.1f} KB)")
    
    return state


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AOE v2.1 - Autonomous Opportunity Engine')
    parser.add_argument('--mode', choices=['scan', 'report', 'test'], default='scan',
                      help='Operation mode')
    parser.add_argument('--dry-run', action='store_true',
                      help='Run without sending alerts')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Verbose logging')
    
    args = parser.parse_args()
    
    setup_logging(level=logging.DEBUG if args.verbose else logging.INFO)
    config = load_config()
    
    if args.mode == 'scan':
        results = run_scan(config, dry_run=args.dry_run)
        sys.exit(0 if results.get('success') else 1)
    
    elif args.mode == 'report':
        run_report()
    
    elif args.mode == 'test':
        print("🧪 Running tests...")
        import subprocess
        test_dir = Path(__file__).parent / "tests"
        if test_dir.exists():
            result = subprocess.run(
                ['python', '-m', 'pytest', str(test_dir), '-v'],
                capture_output=False
            )
            sys.exit(result.returncode)
        else:
            print("❌ No tests directory found")
            sys.exit(1)


if __name__ == "__main__":
    main()
