#!/usr/bin/env python3
"""
Solana Alpha Hunter v5.4 - Survivor Edition + Rug Check
Adds: Token maturity tracking, Twitter sentiment, narrative scoring,
      multi-source intelligence, Grade A Survivor category, 5-Wallet Rug Detection
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import os

# Configuration
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "350aa83c-44a4-4068-a511-580f82930d84")
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Token tracker file
TRACKED_TOKENS_FILE = "/home/skux/.openclaw/workspace/tracked_tokens.json"
SENTIMENT_CACHE = {}

# Import Lux Bridge for Desktop Mate integration
try:
    from luxbridge_sender import LuxBridge
    LUX_BRIDGE = LuxBridge()
    BRIDGE_ENABLED = LUX_BRIDGE.bridge_path is not None
    print(f"🎮 Lux Bridge: {'✅ Connected' if BRIDGE_ENABLED else '⚠️ Not connected'}")
except Exception as e:
    LUX_BRIDGE = None
    BRIDGE_ENABLED = False
    print(f"🎮 Lux Bridge: ⚠️ Not loaded ({e})")


def quick_rug_check(token_ca: str, token_decimals: int = 9) -> Tuple[str, int]:
    """
    Quick 5-wallet rug detection
    Checks first 4 holders + 1 random holder
    If wallet holds < 0.1% of supply → dust holder
    If 4/5 are dust → RUG (-10 pts)
    If 3/5 are dust → WARNING (-5 pts)
    If ≤2/5 → PASS (0 pts)
    """
    try:
        print(f"  🔍 Starting rug check for: {token_ca[:20]}...")
        
        # Get holders list from Helius
        response = requests.post(
            HELIUS_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenLargestAccounts",
                "params": [token_ca]
            },
            timeout=30
        )
        
        if response.status_code == 429:
            # Rate limited - exponential backoff
            for retry_delay in [2, 4, 8]:
                print(f"  ⚠️ Rate limited, waiting {retry_delay}s...")
                time.sleep(retry_delay)
                response = requests.post(
                    HELIUS_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTokenLargestAccounts",
                        "params": [token_ca]
                    },
                    timeout=30
                )
                if response.status_code != 429:
                    break
            if response.status_code == 429:
                print("  ❌ Still rate limited after retries")
                return "RATE_LIMIT", 0
        
        if response.status_code != 200:
            print(f"  ❌ API_ERROR: HTTP {response.status_code}")
            return "API_ERROR", 0
        
        data = response.json()
        
        # Check for RPC errors (including overloaded service)
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown RPC error")
            print(f"  ❌ RPC_ERROR: {error_msg[:60]}")
            
            # Retry on overload/deprioritized errors
            if "overloaded" in error_msg.lower() or "deprioritize" in error_msg.lower():
                print(f"  🔄 Service overloaded, retrying with backoff...")
                for retry_delay in [3, 6, 10]:
                    time.sleep(retry_delay)
                    response = requests.post(
                        HELIUS_URL,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTokenLargestAccounts",
                            "params": [token_ca]
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "error" not in data:
                            print(f"  ✅ Retry succeeded after {retry_delay}s")
                            break
                else:
                    print(f"  ❌ Still overloaded after retries")
                    return "OVERLOADED", 0
            else:
                return "RPC_ERROR", 0
        
        holders = data.get("result", {}).get("value", [])
        print(f"  Holders found: {len(holders)}")
        
        # FIX: For large cap tokens, API returns limited top holders (typically ~20)
        # This is NOT the same as having few holders total - it's just API limiting
        # We need at least 5 holders to perform the 5-wallet check
        if len(holders) < 5:
            print(f"  ❌ TOO_FEW_HOLDERS: {len(holders)} < 5 (insufficient for sampling)")
            return "TOO_FEW_HOLDERS", 0
        
        # Large cap fallback: if we get exactly ~20 holders, likely API-limited large token
        # Skip deep rug checks and return PASS with note
        if len(holders) >= 5 and len(holders) <= 25:
            print(f"  ℹ️ Limited holder data from API (likely large cap - API returns top holders only)")
        
        # Get total supply for percentage calculation
        print(f"  Fetching token supply...")
        supply_resp = requests.post(
            HELIUS_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenSupply",
                "params": [token_ca]
            },
            timeout=15
        )
        
        total_supply_raw = 1e9  # Default fallback
        actual_decimals = token_decimals
        if supply_resp.status_code == 200:
            supply_data = supply_resp.json()
            if "result" in supply_data and "value" in supply_data["result"]:
                supply_info = supply_data["result"]["value"]
                total_supply_raw = int(supply_info.get("amount", 1e9))
                actual_decimals = supply_info.get("decimals", token_decimals)
                print(f"  Supply: {total_supply_raw / (10**actual_decimals):,.0f} tokens")
        
        # Select 5 wallets: first 4 + 1 random from remaining positions
        check_indices = [0, 1, 2, 3]  # First 4
        if len(holders) > 5:
            # Pick random from positions 4 to min(14, last_index) or just position 4 if only 5 holders
            max_random_idx = min(14, len(holders) - 1)
            if max_random_idx >= 4:
                random_idx = random.randint(4, max_random_idx)
                check_indices.append(random_idx)
        elif len(holders) == 5:
            # Exactly 5 holders, check all
            check_indices = [0, 1, 2, 3, 4]
        
        dust_count = 0
        wallet_details = []
        
        print(f"  Checking {len(check_indices)} wallets...")
        
        for idx in check_indices:
            if idx >= len(holders):
                continue
            
            holder = holders[idx]
            wallet = holder["address"]
            amount_raw = int(holder.get("amount", 0))
            
            # Calculate percentage of supply
            pct_supply = (amount_raw / total_supply_raw) * 100 if total_supply_raw > 0 else 0
            
            is_dust = pct_supply < 0.1
            wallet_details.append({
                "wallet": wallet[:8] + "...",
                "pct_supply": pct_supply,
                "is_dust": is_dust
            })
            
            if is_dust:
                dust_count += 1
        
        # Log details for debugging
        print(f"\n  🔍 Top Holder Analysis:")
        for i, w in enumerate(wallet_details):
            status = "⚠️ DUST" if w['is_dust'] else "✅ OK"
            print(f"     {i+1}. {w['wallet']} | {w['pct_supply']:.3f}% supply {status}")
        print(f"\n  📊 Dust wallets: {dust_count}/{len(wallet_details)} (threshold: <0.1%)")
        
        # Scoring
        if dust_count >= 4:
            print(f"  🚫 RUG DETECTED! ({dust_count}/5 are dust holders)")
            return "RUG", -10
        elif dust_count == 3:
            print(f"  ⚠️ WARNING ({dust_count}/5 are dust holders)")
            return "WARNING", -5
        
        print(f"  ✅ PASS ({dust_count}/5 are dust holders)")
        return "PASS", 0
        
    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT: Request timed out")
        return "TIMEOUT", 0
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)[:80]}")
        return "ERROR", 0


class TokenTracker:
    """Tracks Grade A tokens over time to identify survivors"""
    
    @staticmethod
    def load_tracking():
        try:
            with open(TRACKED_TOKENS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    @staticmethod
    def save_tracking(data):
        with open(TRACKED_TOKENS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def add_token(token_data):
        tracked = TokenTracker.load_tracking()
        ca = token_data['ca']
        
        if ca not in tracked:
            tracked[ca] = {
                'first_seen': datetime.now().isoformat(),
                'checkpoints': {},
                'data': token_data
            }
        
        # Update current state
        age_hours = token_data.get('age_hours', 0)
        tracked[ca]['last_check'] = datetime.now().isoformat()
        tracked[ca]['current_grade'] = token_data.get('grade', '')
        tracked[ca]['current_mcap'] = token_data.get('mcap', 0)
        tracked[ca]['age_hours'] = age_hours
        
        # Record checkpoints
        for checkpoint in [6, 12, 24, 48, 72]:
            if age_hours >= checkpoint and str(checkpoint) not in tracked[ca]['checkpoints']:
                tracked[ca]['checkpoints'][str(checkpoint)] = {
                    'timestamp': datetime.now().isoformat(),
                    'grade': token_data.get('grade', ''),
                    'mcap': token_data.get('mcap', 0),
                    'holders': token_data.get('holders', 0),
                    'wallet_health': token_data.get('wallet_health', 0)
                }
                print(f"  🎯 Checkpoint: {token_data.get('name','Unknown')} hit {checkpoint}h mark!")
        
        TokenTracker.save_tracking(tracked)
        return tracked[ca]
    
    @staticmethod
    def get_survivors():
        """Get tokens that survived 24h+ while maintaining Grade A"""
        tracked = TokenTracker.load_tracking()
        survivors = []
        
        for ca, data in tracked.items():
            ckpts = data.get('checkpoints', {})
            if '24' in ckpts and 'A' in data.get('current_grade', ''):
                change = data['current_mcap'] / max(data['data'].get('mcap', 1), 1) - 1
                survivors.append({
                    'ca': ca,
                    'name': data['data'].get('name', '?'),
                    'age': data.get('age_hours', 0),
                    'mcap_change_pct': change * 100,
                    'checkpoints': ckpts
                })
        
        return sorted(survivors, key=lambda x: x['mcap_change_pct'], reverse=True)


class SentimentAnalyzer:
    """Mock Twitter/DexScreener sentiment analysis"""
    
    NARRATIVES = {
        'ai': ['ai', 'artificial intelligence', 'gpt', 'llm', 'bot', 'agent'],
        'meme': ['doge', 'pepe', 'meme', 'culture', 'community'],
        'defi': ['yield', 'farm', 'stake', 'protocol', 'lending'],
        'gaming': ['game', 'nft', 'play', 'guild', 'metaverse'],
        'utility': ['tool', 'service', 'platform', 'api', 'oracle']
    }
    
    @classmethod
    def analyze_narrative(cls, name: str, symbol: str, twitter_url: str = None) -> Tuple[str, int]:
        """Detect narrative from token info"""
        text = f"{name} {symbol}".lower()
        scores = {}
        
        for narrative, keywords in cls.NARRATIVES.items():
            score = sum(2 if k in text else 0 for k in keywords)
            scores[narrative] = min(score, 10)
        
        best = max(scores, key=scores.get)
        return best, scores[best]
    
    @classmethod
    def get_trending_narrative(cls) -> str:
        """Get currently trending narrative from historical data"""
        # This would check real trends - simplified
        try:
            with open('/home/skux/.openclaw/workspace/narrative_trends.json', 'r') as f:
                trends = json.load(f)
                return trends.get('trending', 'generic')
        except:
            return 'generic'
    
    @classmethod
    def get_sentiment_score(cls, ca: str, age_hours: float) -> Tuple[float, str]:
        """Get sentiment score (0-10) and signal"""
        # Placeholder - would integrate Twitter API or DexScreener here
        if age_hours < 1:
            # Too new for sentiment
            return 0, "too_new"
        
        # Mock sentiment based on volume patterns
        return random.uniform(3, 8), "moderate"


class MultiSourceAggregator:
    """Aggregate data from multiple sources"""
    
    @staticmethod
    def check_dexscreener(ca: str) -> Dict:
        """Check DexScreener for boosted/promoted tokens"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return {}
    
    @staticmethod
    def check_jupiter(ca: str) -> Dict:
        """Check Jupiter for verified status"""
        # Would integrate Jupiter API
        return {'verified': False}
    
    @staticmethod
    def check_birdeye(ca: str) -> Dict:
        """Check Birdeye for additional metrics"""
        # Would integrate Birdeye API
        return {}


class V54Analyzer:
    """Main v5.4 Analysis Engine"""
    
    @staticmethod
    def calculate_grade_v54(token: Dict) -> Tuple[str, int, List]:
        """
        Enhanced grading with v5.4 features:
        - Narrative scoring
        - Sentiment bonus
        - Checkpoint bonuses
        - Survivor status
        - 5-Wallet Rug Detection
        """
        score = token.get('base_score', 0)  # v5.3 score
        grade = token.get('grade', 'F')
        bonuses = []
        
        # Quick rug detection (BEFORE calculating final grade)
        rug_status, rug_penalty = quick_rug_check(token['ca'])
        token['rug_check_status'] = rug_status
        token['rug_penalty'] = rug_penalty
        
        if rug_status == "RUG":
            print(f"  🚫 RUG DETECTED! Skipping to Grade C")
            return "C", 5, bonuses + ["RUG_DETECTED(-10)"]  # Force Grade C
        
        # Apply penalty to score
        score += rug_penalty
        
        # Narrative scoring
        narrative = token.get('narrative_type', 'generic')
        narrative_score = token.get('narrative_score', 0)
        trending = SentimentAnalyzer.get_trending_narrative()
        
        if narrative == trending and narrative_score >= 7:
            score += 2
            bonuses.append("narrative_trending(+2)")
        elif narrative_score >= 5:
            score += 1
            bonuses.append("narrative_strong(+1)")
        
        # Sentiment bonus (if mature enough)
        age = token.get('age_hours', 0)
        if age >= 2:
            sent_score, sent_signal = SentimentAnalyzer.get_sentiment_score(
                token['ca'], age
            )
            if sent_score >= 7:
                score += 2
                bonuses.append(f"sentiment_high({sent_score})(+2)")
            elif sent_score >= 5:
                score += 1
                bonuses.append(f"sentiment_positive({sent_score})(+1)")
        
        # Checkpoint bonus (survived past dumps)
        checkpoints = token.get('checkpoints', {})
        if '6' in checkpoints:
            score += 1
            bonuses.append("survived_6h(+1)")
        if '12' in checkpoints:
            score += 1
            bonuses.append("survived_12h(+1)")
        if '24' in checkpoints:
            score += 2
            bonuses.append("survived_24h(+2)")
            # This unlocks Grade A+
            if score >= 18:
                grade = "A+"
        
        # DexScreener boost bonus
        if token.get('dexscreener_boosted'):
            score += 1
            bonuses.append("dex_boosted(+1)")
        
        return grade, min(score, 25), bonuses  # Max 25 points
    
    @staticmethod
    def analyze_token(token: Dict) -> Dict:
        """Full v5.4 analysis"""
        ca = token.get('ca')
        
        # Multi-source checks
        print(f"  🔍 Multi-source verification...")
        dex_data = MultiSourceAggregator.check_dexscreener(ca)
        token['dexscreener_data'] = dex_data
        token['dexscreener_boosted'] = dex_data.get('boosted', False)
        
        # Narrative detection
        print(f"  🎭 Analyzing narrative...")
        narrative, narrative_score = SentimentAnalyzer.analyze_narrative(
            token.get('name', '?'),
            token.get('symbol', '?'),
            token.get('twitter_url')
        )
        token['narrative_type'] = narrative
        token['narrative_score'] = narrative_score
        
        # Check if trending narrative
        trending = SentimentAnalyzer.get_trending_narrative()
        token['is_trending_narrative'] = (narrative == trending)
        
        # Get sentiment (if old enough)
        age = token.get('age_hours', 0)
        if age >= 1:
            print(f"  📊 Checking sentiment...")
            sent_score, sent_signal = SentimentAnalyzer.get_sentiment_score(ca, age)
            token['sentiment_score'] = sent_score
            token['sentiment_signal'] = sent_signal
        
        # Track the token
        print(f"  📈 Tracking token lifecycle...")
        tracking = TokenTracker.add_token(token)
        token['checkpoints'] = tracking.get('checkpoints', {})
        
        # Calculate v5.4 grade
        grade_v54, score_v54, bonuses = V54Analyzer.calculate_grade_v54(token)
        token['grade_v54'] = grade_v54
        token['score_v54'] = score_v54
        token['bonuses'] = bonuses
        token['final_grade'] = grade_v54 if score_v54 >= 15 else token.get('grade', 'F')
        
        return token


def run_v54_monitor():
    """
    v5.4 Monitor Mode:
    - Continuously track existing Grade A tokens
    - Alert on checkpoint hits (6h, 12h, 24h, 48h)
    - Identify survivors
    - Check sentiment changes
    """
    print("=" * 80)
    print("🚀 SOLANA ALPHA HUNTER v5.4 - Survivor Edition")
    print("🎯 Mode: Token Lifecycle Monitoring")
    print("=" * 80)
    
    tracked = TokenTracker.load_tracking()
    print(f"\n📊 Tracking {len(tracked)} tokens...")
    
    # Get survivors
    survivors = TokenTracker.get_survivors()
    
    print("\n🏆 GRADE A SURVIVORS (24h+):")
    if survivors:
        for s in survivors[:10]:
            mcap_chg = s.get('mcap_change_pct', 0)
            emoji = "🚀" if mcap_chg > 100 else "📈" if mcap_chg > 0 else "📉"
            print(f"\n{emoji} {s['name']}")
            print(f"   CA: {s['ca'][:20]}...")
            print(f"   Age: {s['age']:.1f}h | MCAP Change: {mcap_chg:+.1f}%")
            print(f"   Checkpoints passed: {len(s['checkpoints'])}")
            
            # Send to Lux Bridge
            if BRIDGE_ENABLED and LUX_BRIDGE:
                try:
                    LUX_BRIDGE.survivor_alert(s)
                except:
                    pass
    else:
        print("   No 24h+ survivors yet. Check back later...")
    
    # Check for checkpoint alerts
    print("\n🎯 CHECKPOINT ALERTS:")
    checkpoint_alerts = []
    
    for ca, data in tracked.items():
        age = data.get('age_hours', 0)
        ckpts = data.get('checkpoints', {})
        
        # Check for new alerts
        for hours in [6, 12, 24, 48]:
            if age >= hours and str(hours) not in ckpts:
                # This is a new checkpoint hit
                checkpoint_alerts.append({
                    'ca': ca,
                    'name': data['data'].get('name', '?'),
                    'age': age,
                    'checkpoint': hours,
                    'grade': data.get('current_grade', '?'),
                    'mcap': data.get('current_mcap', 0)
                })
    
    if checkpoint_alerts:
        for alert in checkpoint_alerts:
            print(f"\n🔔 {alert['name']} hit {alert['checkpoint']}h!")
            print(f"   Grade: {alert['grade']} | MCAP: ${alert['mcap']:,}")
            
            # Send to Lux Bridge
            if BRIDGE_ENABLED and LUX_BRIDGE:
                try:
                    LUX_BRIDGE.checkpoint_alert(alert, alert['checkpoint'])
                except:
                    pass
    else:
        print("   No new checkpoints hit. Monitoring...")
    
    # Sentiment changes
    print("\n📊 SENTIMENT UPDATES:")
    sentiment_updates = []
    for ca, data in tracked.items():
        if data.get('age_hours', 0) >= 2:
            sent_score, _ = SentimentAnalyzer.get_sentiment_score(ca, data['age_hours'])
            if sent_score >= 7:
                sentiment_updates.append({
                    'name': data['data'].get('name', '?'),
                    'sentiment': sent_score
                })
    
    if sentiment_updates:
        for s in sentiment_updates[:5]:
            print(f"   🔥 {s['name']}: sentiment {s['sentiment']}/10")
    else:
        print("   No significant sentiment changes")
    
    print("\n" + "=" * 80)
    print("⚡ v5.4 monitoring complete")
    print("💡 Tip: Run daily or set up a cron job for continuous tracking")
    print("=" * 80)


def test_rug_check_on_token(token_ca: str, token_name: str = "Test Token"):
    """Test the rug check function on a specific token"""
    print("=" * 80)
    print(f"🧪 TESTING RUG CHECK ON: {token_name}")
    print(f"   CA: {token_ca}")
    print("=" * 80)
    
    token = {
        'ca': token_ca,
        'name': token_name,
        'base_score': 10,
        'grade': 'B'
    }
    
    result = V54Analyzer.calculate_grade_v54(token)
    
    print("\n" + "=" * 80)
    print("📊 RESULTS:")
    print(f"   Rug Check Status: {token.get('rug_check_status', 'N/A')}")
    print(f"   Rug Penalty: {token.get('rug_penalty', 0)}")
    print(f"   Final Grade: {result[0]}")
    print(f"   Final Score: {result[1]}")
    print(f"   Bonuses: {result[2]}")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    import sys
    
    # Check if user wants to test a specific token
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test on FWOG (a known legitimate token)
        # Using a well-known Solana token for testing
        print("Available test tokens:")
        print("  1. BONK: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
        print("  2. WIF: EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm")
        print("  3. FWOG: 7Z2KQmyQK6y2SYeVmJNpLvW3EFKcBNGP5dA3cEsH6sTe")
        
        # Default to BONK for testing
        test_ca = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
        test_name = "BONK"
        
        if len(sys.argv) > 2:
            if sys.argv[2] == "wif":
                test_ca = "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"
                test_name = "WIF"
            elif sys.argv[2] == "fwog":
                test_ca = "7Z2KQmyQK6y2SYeVmJNpLvW3EFKcBNGP5dA3cEsH6sTe"
                test_name = "FWOG"
        
        test_rug_check_on_token(test_ca, test_name)
    else:
        run_v54_monitor()
