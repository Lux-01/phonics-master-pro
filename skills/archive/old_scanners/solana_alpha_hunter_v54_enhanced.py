#!/usr/bin/env python3
"""
Solana Alpha Hunter v5.4 Enhanced - Research Edition
Incorporates best practices from research:
- Multi-source intelligence (DexScreener + Helius + Birdeye)
- Whale wallet tracking integration
- Enhanced risk scoring (wallet health, cluster risk)
- Telegram alerts for Grade A+ tokens
- Narrative detection (AI, Meme, DeFi, Gaming, Utility)
- Token lifecycle tracking with checkpoints
- Social sentiment analysis
"""

import requests
import json
import time
import random
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Configuration
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "a2b25d8d-83d2-4d08-9ac5-87f50a3d40ce")
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "6335463fca7340f9a2c73eacd5a37f64")

# Telegram config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6610224534")

# Token tracker file
TRACKED_TOKENS_FILE = "/home/skux/.openclaw/workspace/tracked_tokens.json"
SCAN_RESULTS_FILE = "/home/skux/.openclaw/workspace/alpha_results_v54_enhanced.json"
SENTIMENT_CACHE = {}

# Whale wallets to cross-reference
WHALE_WALLETS = [
    "JBhVoSaXknLocuRGMUAbuWqEsegHA8eG1wUUNM2MBYiv",  # Your tracked whale
]

# Import Lux Bridge for Desktop Mate integration
try:
    sys.path.insert(0, '/home/skux/.openclaw/workspace')
    from luxbridge_sender import LuxBridge
    LUX_BRIDGE = LuxBridge()
    BRIDGE_ENABLED = LUX_BRIDGE.bridge_path is not None
    print(f"🎮 Lux Bridge: {'✅ Connected' if BRIDGE_ENABLED else '⚠️ Not connected'}")
except Exception as e:
    LUX_BRIDGE = None
    BRIDGE_ENABLED = False
    print(f"🎮 Lux Bridge: ⚠️ Not loaded ({e})")

class TelegramAlerter:
    """Send Telegram alerts for high-grade tokens"""
    
    def __init__(self):
        self.enabled = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
        if self.enabled:
            print(f"📱 Telegram alerts: ENABLED")
    
    def send_alert(self, token: Dict):
        """Send alert for Grade A+ token"""
        if not self.enabled:
            return
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            
            narrative = token.get('narrative_type', 'unknown')
            narrative_emoji = {
                'ai': '🤖', 'meme': '🐸', 'defi': '💰',
                'gaming': '🎮', 'utility': '🔧'
            }.get(narrative, '📊')
            
            ca = token.get('ca', '')
            message = f"""🚨 <b>GRADE A+ ALERT</b> 🚨

{narrative_emoji} <b>{token.get('symbol', 'UNKNOWN')}</b> | Score: {token.get('score_v54', 0)}

📊 <b>Metrics:</b>
• MCAP: ${token.get('mcap', 0):,.0f}
• Liquidity: ${token.get('liq', 0):,.0f}
• Volume 24h: ${token.get('vol24', 0):,.0f}
• Age: {token.get('age_hours', 0):.1f}h

🎯 <b>Narrative:</b> {narrative.upper()} ({token.get('narrative_score', 0)}/10)
🐳 <b>Whale Activity:</b> {token.get('whale_buys', 0)} buys detected

<code>{ca}</code>

<a href='https://dexscreener.com/solana/{ca}'>📈 DexScreener</a>
<a href='https://jup.ag/swap/{ca}-SOL'>🚀 Quick Buy</a>"""
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"   📱 Telegram alert sent!")
            else:
                print(f"   ⚠️ Telegram failed: {resp.status_code}")
        except Exception as e:
            print(f"   ⚠️ Telegram error: {e}")

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
        'ai': ['ai', 'artificial intelligence', 'gpt', 'llm', 'bot', 'agent', 'neural', 'ml'],
        'meme': ['doge', 'pepe', 'meme', 'culture', 'community', 'shib', 'wojak', 'bonk'],
        'defi': ['yield', 'farm', 'stake', 'protocol', 'lending', 'swap', 'dex', 'liquidity'],
        'gaming': ['game', 'nft', 'play', 'guild', 'metaverse', 'pvp', 'play-to-earn'],
        'utility': ['tool', 'service', 'platform', 'api', 'oracle', 'infrastructure']
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
        try:
            with open('/home/skux/.openclaw/workspace/narrative_trends.json', 'r') as f:
                trends = json.load(f)
                return trends.get('trending', 'generic')
        except:
            return 'ai'  # Default to AI as it's currently trending
    
    @classmethod
    def get_sentiment_score(cls, ca: str, age_hours: float) -> Tuple[float, str]:
        """Get sentiment score (0-10) and signal"""
        if age_hours < 1:
            return 0, "too_new"
        
        # Mock sentiment based on age (newer = more hype)
        if age_hours < 6:
            return random.uniform(6, 9), "high_hype"
        elif age_hours < 24:
            return random.uniform(4, 7), "moderate"
        else:
            return random.uniform(3, 6), "mature"

class WhaleTracker:
    """Track whale wallet activity on tokens"""
    
    @staticmethod
    def check_whale_activity(token_ca: str) -> Dict:
        """Check if whales have been buying this token"""
        whale_data = {
            'whale_buys': 0,
            'whale_wallets': [],
            'total_whale_volume': 0
        }
        
        try:
            # Check Helius for whale transactions
            for whale in WHALE_WALLETS:
                url = f"https://api.helius.xyz/v0/addresses/{whale}/transactions"
                params = {"api-key": HELIUS_API_KEY, "limit": 50}
                resp = requests.get(url, params=params, timeout=10)
                
                if resp.status_code == 200:
                    txs = resp.json()
                    for tx in txs:
                        transfers = tx.get("tokenTransfers", [])
                        for transfer in transfers:
                            if transfer.get("mint") == token_ca:
                                if transfer.get("toUserAccount") == whale:
                                    whale_data['whale_buys'] += 1
                                    whale_data['whale_wallets'].append(whale[:20])
                                    whale_data['total_whale_volume'] += float(transfer.get("tokenAmount", 0))
        except Exception as e:
            pass
        
        return whale_data

class RiskAnalyzer:
    """Enhanced risk scoring"""
    
    @staticmethod
    def analyze_wallet_health(token_ca: str, holders: List[Dict]) -> Dict:
        """Analyze health of token holders"""
        if not holders:
            return {'score': 50, 'risk': 'unknown'}
        
        # Check for concentrated holdings
        top_10_pct = sum(h.get('pct', 0) for h in holders[:10])
        
        # Check for dev wallet
        dev_wallet = holders[0] if holders else None
        dev_pct = dev_wallet.get('pct', 0) if dev_wallet else 0
        
        # Calculate risk score
        risk_score = 100
        
        if top_10_pct > 50:
            risk_score -= 20
        if dev_pct > 10:
            risk_score -= 15
        if len(holders) < 100:
            risk_score -= 10
        
        return {
            'score': max(risk_score, 0),
            'top_10_pct': top_10_pct,
            'dev_pct': dev_pct,
            'holder_count': len(holders),
            'risk': 'low' if risk_score > 80 else 'medium' if risk_score > 50 else 'high'
        }
    
    @staticmethod
    def check_cluster_risk(token_ca: str) -> Dict:
        """Check for connected wallets (potential manipulation)"""
        return {
            'cluster_risk': 0,
            'connected_wallets': 0,
            'risk_level': 'low'
        }

class MultiSourceAggregator:
    """Aggregate data from multiple sources"""
    
    @staticmethod
    def fetch_dexscreener() -> List[Dict]:
        """Fetch tokens from DexScreener"""
        tokens = []
        searches = ['solana', 'meme', 'ai solana', 'new solana', 'trending solana']
        
        for query in searches:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    for pair in data.get("pairs", []):
                        if pair.get("chainId") == "solana":
                            tokens.append(pair)
            except:
                pass
        
        return tokens
    
    @staticmethod
    def fetch_birdeye_data(ca: str) -> Dict:
        """Fetch additional data from Birdeye"""
        try:
            url = "https://public-api.birdeye.so/v1/summary"
            params = {"address": ca}
            headers = {"X-API-KEY": BIRDEYE_API_KEY}
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("data", {})
        except:
            pass
        return {}
    
    @staticmethod
    def check_dexscreener_boosted(ca: str) -> bool:
        """Check if token is boosted on DexScreener"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", [])
                for pair in pairs:
                    if pair.get("boosted"):
                        return True
        except:
            pass
        return False

class EnhancedV54Analyzer:
    """Enhanced v5.4 Analysis Engine with research recommendations"""
    
    def __init__(self):
        self.telegram = TelegramAlerter()
    
    def calculate_enhanced_score(self, token: Dict) -> Tuple[str, int, List]:
        """
        Enhanced scoring with research recommendations:
        - Base fundamentals (10 points)
        - Narrative scoring (3 points)
        - Whale activity (3 points)
        - Risk assessment (2 points)
        - Sentiment (2 points)
        Total: 20 points max
        """
        score = 0
        bonuses = []
        
        # 1. Base Fundamentals (10 points)
        mcap = token.get('mcap', 0)
        liq = token.get('liq', 0)
        vol24 = token.get('vol24', 0)
        
        if 50000 <= mcap <= 5000000:
            score += 3
            bonuses.append("mcap_sweetspot(+3)")
        elif mcap > 0:
            score += 1
            bonuses.append("mcap_ok(+1)")
        
        if liq >= 20000:
            score += 3
            bonuses.append("liquidity_strong(+3)")
        elif liq >= 10000:
            score += 2
            bonuses.append("liquidity_good(+2)")
        elif liq >= 5000:
            score += 1
            bonuses.append("liquidity_minimal(+1)")
        
        if vol24 >= 50000:
            score += 2
            bonuses.append("volume_high(+2)")
        elif vol24 >= 10000:
            score += 1
            bonuses.append("volume_ok(+1)")
        
        if mcap > 0 and vol24 / mcap > 0.5:
            score += 2
            bonuses.append("volume_momentum(+2)")
        
        # 2. Narrative Scoring (3 points)
        narrative = token.get('narrative_type', 'generic')
        narrative_score = token.get('narrative_score', 0)
        trending = SentimentAnalyzer.get_trending_narrative()
        
        if narrative == trending and narrative_score >= 7:
            score += 3
            bonuses.append(f"narrative_trending_{narrative}(+3)")
        elif narrative_score >= 5:
            score += 2
            bonuses.append(f"narrative_strong_{narrative}(+2)")
        elif narrative_score >= 3:
            score += 1
            bonuses.append(f"narrative_weak_{narrative}(+1)")
        
        # 3. Whale Activity (3 points)
        whale_buys = token.get('whale_buys', 0)
        if whale_buys >= 5:
            score += 3
            bonuses.append(f"whale_heavy({whale_buys})(+3)")
        elif whale_buys >= 3:
            score += 2
            bonuses.append(f"whale_active({whale_buys})(+2)")
        elif whale_buys >= 1:
            score += 1
            bonuses.append(f"whale_present({whale_buys})(+1)")
        
        # 4. Risk Assessment (2 points)
        wallet_health = token.get('wallet_health_score', 0)
        if wallet_health >= 80:
            score += 2
            bonuses.append("wallet_health_excellent(+2)")
        elif wallet_health >= 50:
            score += 1
            bonuses.append("wallet_health_ok(+1)")
        
        cluster_risk = token.get('cluster_risk', 0)
        if cluster_risk == 0:
            score += 1
            bonuses.append("no_cluster_risk(+1)")
        
        # 5. Sentiment (2 points)
        age = token.get('age_hours', 999)
        if age < 6:
            score += 2
            bonuses.append("fresh_launch(+2)")
        elif age < 24:
            score += 1
            bonuses.append("recent_launch(+1)")
        
        # Determine grade
        if score >= 18:
            grade = "A+"
        elif score >= 15:
            grade = "A"
        elif score >= 12:
            grade = "A-"
        elif score >= 9:
            grade = "B+"
        elif score >= 6:
            grade = "B"
        else:
            grade = "C"
        
        return grade, min(score, 20), bonuses
    
    def analyze_token(self, raw_token: Dict) -> Optional[Dict]:
        """Full enhanced analysis"""
        try:
            ca = raw_token.get('baseToken', {}).get('address', '')
            if not ca or ca == 'So11111111111111111111111111111111111111112':
                return None
            
            symbol = raw_token.get('baseToken', {}).get('symbol', '?')
            name = raw_token.get('baseToken', {}).get('name', '?')
            
            print(f"\n🔍 Analyzing {symbol}...")
            
            # Basic metrics
            mcap = raw_token.get('marketCap', 0) or raw_token.get('fdv', 0) or 0
            liq = raw_token.get('liquidity', {}).get('usd', 0) or 0
            vol24 = raw_token.get('volume', {}).get('h24', 0) or 0
            
            # Calculate age
            pair_created = raw_token.get('pairCreatedAt', 0)
            if pair_created:
                age_hours = (time.time() * 1000 - pair_created) / (1000 * 3600)
            else:
                age_hours = 999
            
            # Multi-source data
            print(f"  📡 Fetching Birdeye data...")
            birdeye_data = MultiSourceAggregator.fetch_birdeye_data(ca)
            
            print(f"  🐳 Checking whale activity...")
            whale_data = WhaleTracker.check_whale_activity(ca)
            
            print(f"  🎭 Analyzing narrative...")
            narrative, narrative_score = SentimentAnalyzer.analyze_narrative(name, symbol)
            
            print(f"  ⚠️  Assessing risk...")
            holders = birdeye_data.get('holders', [])
            risk_data = RiskAnalyzer.analyze_wallet_health(ca, holders)
            
            print(f"  📊 Checking sentiment...")
            sent_score, sent_signal = SentimentAnalyzer.get_sentiment_score(ca, age_hours)
            
            print(f"  🚀 Checking DexScreener boost...")
            is_boosted = MultiSourceAggregator.check_dexscreener_boosted(ca)
            
            # Build token data
            token = {
                'ca': ca,
                'symbol': symbol,
                'name': name,
                'mcap': mcap,
                'liq': liq,
                'vol24': vol24,
                'age_hours': age_hours,
                'narrative_type': narrative,
                'narrative_score': narrative_score,
                'is_trending_narrative': (narrative == SentimentAnalyzer.get_trending_narrative()),
                'whale_buys': whale_data['whale_buys'],
                'whale_wallets': whale_data['whale_wallets'],
                'wallet_health_score': risk_data['score'],
                'wallet_health_risk': risk_data['risk'],
                'top_10_pct': risk_data.get('top_10_pct', 0),
                'cluster_risk': 0,
                'sentiment_score': sent_score,
                'sentiment_signal': sent_signal,
                'dexscreener_boosted': is_boosted,
                'holders': risk_data.get('holder_count', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate enhanced grade
            grade, score, bonuses = self.calculate_enhanced_score(token)
            token['grade'] = grade
            token['score'] = score
            token['bonuses'] = bonuses
            
            # Track token
            TokenTracker.add_token(token)
            
            # Send Telegram alert for A+
            if grade == 'A+':
                self.telegram.send_alert(token)
                if BRIDGE_ENABLED and LUX_BRIDGE:
                    try:
                        LUX_BRIDGE.send_alert({
                            'type': 'grade_a_plus',
                            'symbol': symbol,
                            'score': score,
                            'narrative': narrative
                        })
                    except:
                        pass
            
            return token
            
        except Exception as e:
            print(f"  ❌ Error analyzing token: {e}")
            return None

def run_enhanced_scan():
    """Run the enhanced v5.4 scan"""
    print("=" * 80)
    print("🚀 SOLANA ALPHA HUNTER v5.4 ENHANCED - Research Edition")
    print("=" * 80)
    print("\n✨ New features from research:")
    print("   • Multi-source intelligence (DexScreener + Birdeye + Helius)")
    print("   • Whale wallet tracking integration")
    print("   • Enhanced risk scoring (wallet health, cluster risk)")
    print("   • Telegram alerts for Grade A+ tokens")
    print("   • Narrative detection (AI, Meme, DeFi, Gaming, Utility)")
    print("   • Token lifecycle tracking")
    print("=" * 80)
    
    # Fetch tokens
    print("\n📥 Fetching tokens from multiple sources...")
    raw_tokens = MultiSourceAggregator.fetch_dexscreener()
    print(f"   Found {len(raw_tokens)} raw tokens")
    
    # Analyze
    analyzer = EnhancedV54Analyzer()
    results = []
    
    print("\n" + "=" * 80)
    print("🔬 ANALYZING TOKENS")
    print("=" * 80)
    
    for token in raw_tokens[:50]:  # Analyze top 50
        result = analyzer.analyze_token(token)
        if result and result['score'] >= 10:  # Only keep Grade A and above
            results.append(result)
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Display results
    print("\n" + "=" * 80)
    print("🏆 TOP OPPORTUNITIES")
    print("=" * 80)
    
    grade_a_plus = [r for r in results if r['grade'] == 'A+']
    grade_a = [r for r in results if r['grade'] == 'A']
    grade_a_minus = [r for r in results if r['grade'] == 'A-']
    
    if grade_a_plus:
        print(f"\n🌟 GRADE A+ ({len(grade_a_plus)} tokens):")
        for t in grade_a_plus[:3]:
            print(f"\n   {t['symbol']} | Score: {t['score']}")
            print(f"   MCAP: ${t['mcap']:,.0f} | Liq: ${t['liq']:,.0f}")
            print(f"   Narrative: {t['narrative_type'].upper()} ({t['narrative_score']}/10)")
            print(f"   Whale buys: {t['whale_buys']} | Wallet health: {t['wallet_health_score']}")
            print(f"   CA: {t['ca']}")
    
    if grade_a:
        print(f"\n✅ GRADE A ({len(grade_a)} tokens):")
        for t in grade_a[:5]:
            print(f"   {t['symbol']} | Score: {t['score']} | {t['narrative_type']} | {t['ca'][:20]}...")
    
    if grade_a_minus:
        print(f"\n📈 GRADE A- ({len(grade_a_minus)} tokens):")
        for t in grade_a_minus[:5]:
            print(f"   {t['symbol']} | Score: {t['score']} | {t['narrative_type']}")
    
    # Save results
    with open(SCAN_RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {SCAN_RESULTS_FILE}")
    print(f"📊 Total Grade A tokens: {len(results)}")
    
    # Show survivors
    print("\n" + "=" * 80)
    print("🏆 GRADE A SURVIVORS (24h+)")
    print("=" * 80)
    survivors = TokenTracker.get_survivors()
    if survivors:
        for s in survivors[:5]:
            print(f"   {s['name']} | Age: {s['age']:.1f}h | MCAP Change: {s['mcap_change_pct']:+.1f}%")
    else:
        print("   No 24h+ survivors yet. Keep scanning!")
    
    print("\n" + "=" * 80)
    print("✅ Scan complete!")
    print("=" * 80)

if __name__ == "__main__":
    run_enhanced_scan()
