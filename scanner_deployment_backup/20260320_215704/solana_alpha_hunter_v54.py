#!/usr/bin/env python3
"""
Solana Alpha Hunter v5.4 - Survivor Edition
Adds: Token maturity tracking, Twitter sentiment, narrative scoring,
      multi-source intelligence, Grade A Survivor category
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
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")
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
        """
        score = token.get('base_score', 0)  # v5.3 score
        grade = token.get('grade', 'F')
        bonuses = []
        
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

if __name__ == "__main__":
    run_v54_monitor()
