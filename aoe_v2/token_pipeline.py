"""
AOE v2.0 - Token Pipeline
Orchestrates multiple scanners, deduplicates, enriches, and prepares tokens for scoring.
"""

import json
from typing import List, Dict, Set, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import logging
import time

from scanner_base import Token


class TokenPipeline:
    """
    Orchestrates the complete token flow:
    1. Discovery: Fetch from all sources
    2. Deduplication: Merge by address
    3. Filtering: Apply strategy constraints
    4. Enrichment: Calculate derived metrics
    5. Scoring: Pass to scorer
    """
    
    def __init__(self, 
                 scanners: List[Any],
                 mc_min: float = 100_000,
                 mc_max: float = 20_000_000,
                 strategy: str = "mean_reversion_microcap",
                 data_dir: Optional[Path] = None):
        """
        Initialize the pipeline.
        
        Args:
            scanners: List of scanner instances to use
            mc_min: Minimum market cap filter
            mc_max: Maximum market cap filter
            strategy: Strategy name for filtering
            data_dir: Directory for caching data
        """
        self.scanners = scanners
        self.mc_min = mc_min
        self.mc_max = mc_max
        self.strategy = strategy
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("aoe.pipeline")
        
        # Initialize caches
        self._historical_volume: Dict[str, List[Dict]] = {}
        self._token_cache_file = self.data_dir / "token_cache.json"
        self._load_cache()
    
    def run(self, parallel: bool = True) -> Tuple[List[Token], Dict[str, Any]]:
        """
        Run the complete pipeline.
        
        Args:
            parallel: Whether to fetch sources in parallel
            
        Returns:
            Tuple of (enriched tokens, pipeline stats)
        """
        start_time = time.time()
        stats = {
            'timestamp': datetime.now().isoformat(),
            'sources': [],
            'raw_count': 0,
            'unique_count': 0,
            'filtered_count': 0,
            'final_count': 0,
            'duration': 0
        }
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 Starting AOE Token Pipeline v2.0")
        self.logger.info(f"   Strategy: {self.strategy}")
        self.logger.info(f"   MC Range: ${self.mc_min:,.0f} - ${self.mc_max:,.0f}")
        self.logger.info("=" * 60)
        
        # Stage 1: Discovery
        self.logger.info("\n📡 Stage 1: Discovery")
        raw_tokens = self._discovery(parallel)
        stats['raw_count'] = len(raw_tokens)
        stats['sources'] = self._count_by_source(raw_tokens)
        
        # Stage 2: Deduplication
        self.logger.info("\n🔍 Stage 2: Deduplication")
        unique_tokens = self._deduplicate(raw_tokens)
        stats['unique_count'] = len(unique_tokens)
        
        # Stage 3: Filtering
        self.logger.info("\n🔰 Stage 3: Filtering")
        filtered_tokens = self._filter(unique_tokens)
        stats['filtered_count'] = len(filtered_tokens)
        
        # Stage 4: Enrichment
        self.logger.info("\n✨ Stage 4: Enrichment")
        enriched_tokens = self._enrich(filtered_tokens)
        
        # Stage 5: Persist
        self._save_cache(enriched_tokens)
        
        elapsed = time.time() - start_time
        stats['duration'] = elapsed
        stats['final_count'] = len(enriched_tokens)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("✅ Pipeline Complete")
        self.logger.info(f"   Duration: {elapsed:.1f}s")
        self.logger.info(f"   Tokens: {stats['raw_count']} raw → {stats['unique_count']} unique → {len(enriched_tokens)} final")
        self.logger.info("=" * 60)
        
        return enriched_tokens, stats
    
    def _discovery(self, parallel: bool = True) -> List[Token]:
        """
        Fetch tokens from all scanners.
        
        Args:
            parallel: Run scanners in parallel
            
        Returns:
            Combined raw token list
        """
        all_tokens = []
        
        if parallel and len(self.scanners) > 1:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(s.fetch_with_retry): s for s in self.scanners}
                
                for future in as_completed(futures):
                    scanner = futures[future]
                    try:
                        tokens = future.result(timeout=30)
                        all_tokens.extend(tokens)
                        self.logger.info(f"   ✅ {scanner.name}: {len(tokens)} tokens")
                    except Exception as e:
                        self.logger.error(f"   ❌ {scanner.name}: {e}")
        else:
            # Sequential execution
            for scanner in self.scanners:
                try:
                    tokens = scanner.fetch_with_retry()
                    all_tokens.extend(tokens)
                    self.logger.info(f"   ✅ {scanner.name}: {len(tokens)} tokens")
                except Exception as e:
                    self.logger.error(f"   ❌ {scanner.name}: {e}")
        
        return all_tokens
    
    def _count_by_source(self, tokens: List[Token]) -> Dict[str, int]:
        """Count tokens found by each source."""
        counts = defaultdict(int)
        for token in tokens:
            for source in token.sources:
                counts[source] += 1
        return dict(counts)
    
    def _deduplicate(self, tokens: List[Token]) -> List[Token]:
        """
        Deduplicate tokens by address, merging data from all sources.
        
        Args:
            tokens: Raw token list with possible duplicates
            
        Returns:
            Unique token list with merged data
        """
        # Group by address
        by_address: Dict[str, List[Token]] = defaultdict(list)
        for token in tokens:
            by_address[token.address].append(token)
        
        # Merge duplicates
        merged = []
        for address, token_list in by_address.items():
            if len(token_list) == 1:
                merged.append(token_list[0])
            else:
                merged_token = self._merge_tokens(token_list)
                merged.append(merged_token)
        
        self.logger.info(f"   Merged {len(merged)}/{len(tokens)} unique by address")
        return merged
    
    def _merge_tokens(self, tokens: List[Token]) -> Token:
        """
        Merge multiple tokens into one, keeping best data.
        
        Args:
            tokens: List of tokens for same address
            
        Returns:
            Merged token
        """
        # Use first as base
        base = tokens[0]
        
        # Collect all sources
        all_sources = set()
        for t in tokens:
            all_sources.update(t.sources)
        
        # Find token with most complete data
        best_token = max(tokens, key=lambda t: sum([
            t.volume_24h > 0,
            t.liquidity > 0,
            t.txns_24h > 0,
            t.price_change_1h != 0
        ]))
        
        # Merge fields carefully
        merged = Token(
            address=base.address,
            symbol=base.symbol or best_token.symbol,
            name=base.name or best_token.name,
            chain_id=base.chain_id,
            price=base.price or best_token.price,
            market_cap=base.market_cap or best_token.market_cap,
            fdv=max(t.fdv for t in tokens),
            liquidity=max((t.liquidity for t in tokens), default=0),
            volume_24h=max((t.volume_24h for t in tokens), default=0),
            volume_1h=max((t.volume_1h for t in tokens), default=0),
            volume_5m=max((t.volume_5m for t in tokens), default=0),
            price_change_1h=best_token.price_change_1h or base.price_change_1h,
            price_change_24h=best_token.price_change_24h or base.price_change_24h,
            price_change_5m=best_token.price_change_5m or base.price_change_5m,
            txns_24h=max((t.txns_24h for t in tokens), default=0),
            buys_24h=max((t.buys_24h for t in tokens), default=0),
            sells_24h=max((t.sells_24h for t in tokens), default=0),
            holders=max((t.holders for t in tokens), default=0),
            creation_time=min(
                (t.creation_time for t in tokens if t.creation_time),
                default=None
            ),
            sources=list(all_sources),
            source='merged'
        )
        
        return merged
    
    def _filter(self, tokens: List[Token]) -> List[Token]:
        """
        Apply strategy filters.
        
        Args:
            tokens: Unique token list
            
        Returns:
            Tokens matching strategy criteria
        """
        filtered = []
        
        for token in tokens:
            # Market cap filter
            if not (self.mc_min <= token.market_cap <= self.mc_max):
                continue
            
            # Exclude stablecoins
            if token.symbol in ['USDC', 'USDT', 'SOL', 'WSOL']:
                continue
            
            # Exclude very low volume (dead tokens)
            if token.volume_24h < 100:
                continue
            
            # Exclude suspicious
            if self._is_suspicious(token):
                self.logger.debug(f"   Filtered suspicious: {token.symbol}")
                continue
            
            filtered.append(token)
        
        self.logger.info(f"   Filtered: {len(filtered)}/{len(tokens)} match strategy")
        
        # Log filter breakdown
        by_range = defaultdict(int)
        for t in filtered:
            if t.market_cap < 1_000_000:
                by_range['microcap'] += 1
            elif t.market_cap < 5_000_000:
                by_range['small'] += 1
            elif t.market_cap < 20_000_000:
                by_range['medium'] += 1
        
        self.logger.info(f"   Breakdown: {dict(by_range)}")
        
        return filtered
    
    def _is_suspicious(self, token: Token) -> bool:
        """Check if token looks suspicious/rug."""
        # No transactions
        if token.txns_24h == 0 and token.volume_24h > 0:
            return True
        
        # Impossible price changes
        if abs(token.price_change_24h) > 10000:  # >10000%
            return True
        
        # Zero liquidity with volume (wash trading)
        if token.liquidity == 0 and token.volume_24h > 100000:
            return True
        
        return False
    
    def _enrich(self, tokens: List[Token]) -> List[Token]:
        """
        Enrich tokens with calculated metrics.
        
        Args:
            tokens: Filtered tokens
            
        Returns:
            Enriched tokens
        """
        enriched = []
        
        for token in tokens:
            # Calculate volume spike (5m vs 24h average)
            if token.volume_24h > 0:
                hourly_avg = token.volume_24h / 24
                if token.volume_1h > 0:
                    token.volume_5m = token.volume_1h * 0.2  # Estimate
                if token.volume_5m > 0 and hourly_avg > 0:
                    vol_spike = token.volume_5m / (hourly_avg / 12)  # vs 5min avg
                    # Add to token dict for scoring
                    token.__dict__['vol_spike_5m'] = vol_spike
            
            # Calculate age in hours if known
            if token.creation_time:
                age_hours = (datetime.now() - token.creation_time).total_seconds() / 3600
                token.__dict__['age_hours'] = age_hours
            
            # Calculate reversion potential
            if -20 < token.price_change_1h < -5:
                # Good dip range for mean reversion
                token.__dict__['dip_quality'] = min(100, abs(token.price_change_1h) * 5)
            else:
                token.__dict__['dip_quality'] = 0
            
            # Narrative detection
            token.__dict__['narratives'] = self._detect_narratives(token)
            
            enriched.append(token)
        
        self.logger.info(f"   Enriched: {len(enriched)} tokens with metrics")
        return enriched
    
    def _detect_narratives(self, token: Token) -> List[str]:
        """Detect narrative keywords in token metadata."""
        text = f"{token.name} {token.symbol}".lower()
        narratives = []
        
        narrative_keywords = {
            'ai': ['ai', 'artificial', 'intelligence', 'gpt', 'neural', 'agent', 'bot', 'model'],
            'meme': ['meme', 'doge', 'pepe', 'wojak', 'chad', 'based', 'mog'],
            'gaming': ['game', 'gaming', 'play', 'metaverse', 'virtual'],
            'defi': ['dao', 'yield', 'stake', 'farm', 'vault', 'defi'],
            'utility': ['swap', 'bridge', 'protocol', 'network', 'platform']
        }
        
        for narrative, keywords in narrative_keywords.items():
            if any(kw in text for kw in keywords):
                narratives.append(narrative)
        
        return narratives
    
    def _load_cache(self):
        """Load historical volume cache."""
        cache_file = self.data_dir / "historical_volume.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    self._historical_volume = json.load(f)
            except:
                pass
    
    def _save_cache(self, tokens: List[Token]):
        """Save token cache with timestamp."""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'count': len(tokens),
            'tokens': [
                {
                    'address': t.address,
                    'symbol': t.symbol,
                    'volume_24h': t.volume_24h,
                    'market_cap': t.market_cap
                }
                for t in tokens[:100]  # Keep top 100
            ]
        }
        
        try:
            with open(self._token_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")
    
    def get_token_history(self, address: str) -> List[Dict]:
        """Get historical data for a token."""
        return self._historical_volume.get(address, [])
    
    def compare_to_historical(self, token: Token) -> Dict[str, float]:
        """Compare token to its historical average."""
        history = self.get_token_history(token.address)
        
        if not history or len(history) < 3:
            return {'vol_spike': 1.0, 'change_vs_avg': 0}
        
        avg_volume = sum(h.get('volume', 0) for h in history) / len(history)
        vol_spike = token.volume_24h / avg_volume if avg_volume > 0 else 1.0
        
        return {
            'vol_spike': vol_spike,
            'change_vs_avg': (token.market_cap / history[-1].get('mc', token.market_cap)) - 1
        }


if __name__ == "__main__":
    # Test the pipeline
    import logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    from scanner_dexscreener import DexScreenerScanner
    from scanner_birdeye import BirdeyeScanner
    from scanner_pumpfun import PumpFunScanner
    
    print("🧪 Testing Token Pipeline v2.0...")
    print("=" * 60)
    
    # Create scanners
    scanners = [
        DexScreenerScanner(),
        BirdeyeScanner(),
        PumpFunScanner()
    ]
    
    # Create pipeline
    pipeline = TokenPipeline(
        scanners=scanners,
        mc_min=100_000,
        mc_max=20_000_000,
        strategy="mean_reversion_microcap"
    )
    
    # Run pipeline
    tokens, stats = pipeline.run(parallel=False)  # Sequential for testing
    
    print("\n" + "=" * 60)
    print("📊 Pipeline Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Found {len(tokens)} opportunities")
    
    if tokens:
        print("\nTop 10 by volume:")
        top = sorted(tokens, key=lambda t: t.volume_24h, reverse=True)[:10]
        for t in top:
            print(f"  {t.symbol}: ${t.market_cap:,.0f} MC, ${t.volume_24h:,.0f} vol, {t.txns_24h} txns")
        
        print(f"\nWith volume spikes:")
        spiky = [t for t in tokens if t.__dict__.get('vol_spike_5m', 0) > 3]
        print(f"   {len(spiky)} tokens with 3x+ volume spike")
